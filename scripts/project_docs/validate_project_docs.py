#!/usr/bin/env python3
"""Structural validator for the product documentation system.

Standard-library only. Exits nonzero when any structural check fails. Soft
observations print as WARN and do not fail the run.

Checks (see docs/project/DOCS_INDEX.md for the system layout):
  1. PROJECT_TRACKER.md exists, within size limits, required sections present
  2. Task IDs unique; detail blocks reference table tasks
  3. HIST / VER event IDs unique and well-formed
  4. done tasks reference a verification ID
  5. blocked tasks name an unblock condition; paused tasks a resume point
  6. Workstream rollups do not contradict child task statuses
  7. Internal relative links in control files resolve
  8. Canonical documents named in the source-of-truth map exist
  9. Exactly one current row per metric in the executive snapshot
 10. Head-snapshot SHAs in REPO_HISTORY.md are well-formed and exist locally
 11. No obvious unredacted credential patterns in control files
 12. Archive paths named in MIGRATION_MAP.md exist

Usage: python3 scripts/project_docs/validate_project_docs.py [--root PATH]
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

TRACKER = "PROJECT_TRACKER.md"
HISTORY = "docs/project/REPO_HISTORY.md"
VERLOG = "docs/project/VERIFICATION_LOG.md"
INDEX = "docs/project/DOCS_INDEX.md"
PROPOSALS = "docs/project/PROPOSALS.md"
MIGMAP = "docs/project/MIGRATION_MAP.md"
HANDOFF = "HANDOFF.md"
CONTROL_FILES = [TRACKER, HISTORY, VERLOG, INDEX, PROPOSALS, MIGMAP, HANDOFF]

MAX_TRACKER_LINES = 350
MAX_TRACKER_BYTES = 45 * 1024

REQUIRED_SECTIONS = [
    "0. How to use this tracker",
    "1. Current executive snapshot",
    "2. Source-of-truth map",
    "3. Workstream index",
    "4. Active task table",
    "5. Active task details",
    "6. Blockers, risks",
    "7. Current verification snapshot",
    "8. Environment and release state",
    "9. Recently completed",
    "10. Proposed scope",
    "11. Next recommended actions",
    "12. Ledger and archive links",
]

TASK_ID_RE = re.compile(r"^([A-Z][A-Z0-9]+-\d{3})\b")
VER_ID_RE = re.compile(r"VER-\d{8}-\d{3}")
HIST_ID_RE = re.compile(r"HIST-\d{8}-\d{3}")
SHA_RE = re.compile(r"`([0-9a-f]{40})`")
LINK_RE = re.compile(r"\]\(([^)#\s]+)(?:#[^)]*)?\)")
SECRET_RES = [
    re.compile(r"ghp_[A-Za-z0-9]{30,}"),
    re.compile(r"github_pat_[A-Za-z0-9_]{30,}"),
    re.compile(r"sk-[A-Za-z0-9]{20,}"),
    re.compile(r"AKIA[0-9A-Z]{16}"),
    re.compile(r"BEGIN [A-Z ]*PRIVATE KEY"),
    re.compile(r"xox[baprs]-[A-Za-z0-9-]{10,}"),
]

failures: list[str] = []
warnings: list[str] = []


def fail(msg: str) -> None:
    failures.append(msg)


def warn(msg: str) -> None:
    warnings.append(msg)


def read(root: Path, rel: str) -> str | None:
    p = root / rel
    if not p.is_file():
        fail(f"missing required file: {rel}")
        return None
    return p.read_text(encoding="utf-8")


def table_rows(text: str) -> list[list[str]]:
    rows = []
    for line in text.splitlines():
        line = line.strip()
        if line.startswith("|") and line.endswith("|") and "---" not in line:
            cells = [c.strip() for c in line.strip("|").split("|")]
            rows.append(cells)
    return rows


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=None)
    args = ap.parse_args()
    root = Path(args.root).resolve() if args.root else Path(
        subprocess.run(["git", "rev-parse", "--show-toplevel"],
                       capture_output=True, text=True, check=True).stdout.strip())

    tracker = read(root, TRACKER)
    history = read(root, HISTORY)
    verlog = read(root, VERLOG)
    index = read(root, INDEX)
    migmap = read(root, MIGMAP)
    read(root, PROPOSALS)
    read(root, HANDOFF)

    # 1. Tracker size and sections
    if tracker is not None:
        lines = tracker.splitlines()
        if len(lines) > MAX_TRACKER_LINES:
            fail(f"tracker has {len(lines)} lines (limit {MAX_TRACKER_LINES})")
        size = len(tracker.encode())
        if size > MAX_TRACKER_BYTES:
            fail(f"tracker is {size} bytes (limit {MAX_TRACKER_BYTES})")
        for section in REQUIRED_SECTIONS:
            if not re.search(rf"^##\s+{re.escape(section)}", tracker, re.M):
                fail(f"tracker missing required section: {section}")

        # 2/4/5/6. Task table checks
        task_rows = [r for r in table_rows(tracker) if r and TASK_ID_RE.match(r[0])]
        ids = [TASK_ID_RE.match(r[0]).group(1) for r in task_rows]  # type: ignore[union-attr]
        for dup in {i for i in ids if ids.count(i) > 1}:
            fail(f"duplicate task ID in tracker table: {dup}")
        detail_ids = re.findall(r"^###\s+([A-Z][A-Z0-9]+-\d{3})\s+—", tracker, re.M)
        for did in detail_ids:
            if did not in ids:
                fail(f"detail block for {did} has no task-table row")
        status_of = {}
        for r in task_rows:
            tid = TASK_ID_RE.match(r[0]).group(1)  # type: ignore[union-attr]
            joined = " | ".join(r)
            status = next((s for s in
                           ["needs-reconciliation", "in-progress", "verified-stale",
                            "proposed", "todo", "ready", "paused", "blocked",
                            "done", "superseded", "cancelled"] if s in r), None)
            status_of[tid] = status
            if status == "done" and not VER_ID_RE.search(joined):
                fail(f"done task {tid} has no verification ID reference")
            if status == "blocked" and "unblock" not in joined.lower():
                fail(f"blocked task {tid} names no unblock condition")
            if status == "paused" and "resume" not in joined.lower():
                fail(f"paused task {tid} has no resume point")
            if status == "superseded" and "→" not in joined and "replac" not in joined.lower():
                fail(f"superseded task {tid} points to no replacement")

        # Workstream rollup consistency: the derived status is the leading
        # token of the status cell (before any em-dash explanation). A WS
        # marked done must have all mapped children done.
        ws_rows = [r for r in table_rows(tracker) if r and re.match(r"^WS-[A-Z]+$", r[0])]
        for r in ws_rows:
            joined = " ".join(r)
            children = re.findall(r"\b([A-Z][A-Z0-9]+-\d{3})\b", joined)
            child_statuses = [status_of.get(c) for c in children if c in status_of]
            derived = re.split(r"[\s—-]", r[2].strip(), maxsplit=1)[0].lower()
            if derived == "done" and child_statuses and \
               any(s != "done" for s in child_statuses):
                fail(f"workstream {r[0]} marked done with unfinished children")

        # 9. Executive snapshot: unique metric labels
        snap = tracker.split("## 1. Current executive snapshot")[1].split("## 2.")[0]
        labels = [r[0] for r in table_rows(snap) if r and not r[0].startswith("Metric")]
        for dup in {l for l in labels if labels.count(l) > 1}:
            fail(f"executive snapshot repeats metric row: {dup}")

    # 3. Event ID uniqueness and format. Only ledger-row definitions
    # (`| HIST-…` / `| VER-…` at row start) count as definitions; inline
    # cross-references are allowed to repeat. Malformed = contains a digit but
    # does not match the canonical pattern (skips format placeholders).
    if history is not None:
        hids = re.findall(r"^\|\s*(HIST-\d{8}-\d{3})\s*\|", history, re.M)
        for dup in {i for i in hids if hids.count(i) > 1}:
            fail(f"duplicate history event ID: {dup}")
        for bad in re.findall(r"HIST-[\w-]+", history):
            if any(c.isdigit() for c in bad) and not HIST_ID_RE.fullmatch(bad):
                fail(f"malformed history event ID: {bad}")
    if verlog is not None:
        vids = re.findall(r"^\|\s*(VER-\d{8}-\d{3})\s*\|", verlog, re.M)
        for dup in {i for i in vids if vids.count(i) > 1}:
            fail(f"duplicate verification ID: {dup}")
        for bad in re.findall(r"VER-[\w-]+", verlog):
            if any(c.isdigit() for c in bad) and not VER_ID_RE.fullmatch(bad):
                fail(f"malformed verification ID: {bad}")

    # 7. Relative links resolve (control files)
    for rel in CONTROL_FILES:
        text = read(root, rel)
        if text is None:
            continue
        base = (root / rel).parent
        for target in LINK_RE.findall(text):
            if "://" in target or target.startswith("mailto:"):
                continue
            t = target.split("#", 1)[0]
            if not t:
                continue
            if not (base / t).exists():
                fail(f"broken relative link in {rel}: {target}")

    # 8. Source-of-truth map paths exist
    if tracker is not None and "## 2. Source-of-truth map" in tracker:
        sotm = tracker.split("## 2. Source-of-truth map")[1].split("## 3.")[0]
        for path in re.findall(r"`([^`]+/[^`]+?\.(?:md|json))`", sotm):
            if not (root / path).exists():
                fail(f"source-of-truth map names missing doc: {path}")

    # 10. Head-snapshot SHAs well-formed and present locally
    if history is not None and "## 2. Current head snapshot" in history:
        snap = history.split("## 2. Current head snapshot")[1].split("## 3.")[0]
        for sha in SHA_RE.findall(snap):
            out = subprocess.run(["git", "-C", str(root), "cat-file", "-t", sha],
                                 capture_output=True, text=True)
            if out.returncode != 0:
                fail(f"head-snapshot SHA not found locally: {sha}")

    # 11. Secret patterns in control files
    for rel in CONTROL_FILES:
        text = read(root, rel)
        if text is None:
            continue
        for rx in SECRET_RES:
            if rx.search(text):
                fail(f"possible unredacted credential in {rel}: pattern {rx.pattern[:24]}")

    # 12. Migration-map archive paths exist
    if migmap is not None:
        for m in re.findall(r"`(archive/pre-consolidation/[^`]+?)`", migmap):
            if not (root / "docs/project" / m).exists():
                fail(f"migration map names missing archive path: {m}")

    for w in warnings:
        print(f"WARN  {w}")
    for f in failures:
        print(f"FAIL  {f}")
    if failures:
        print(f"\n{len(failures)} structural failure(s)")
        return 1
    print("project docs validation: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
