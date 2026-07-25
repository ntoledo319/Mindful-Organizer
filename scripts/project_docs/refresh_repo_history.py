#!/usr/bin/env python3
"""Regenerate the machine commit index and print current head rows.

Standard-library only, read-only against the repository (except an optional
explicit --fetch), deterministic output. Never rewrites Git state, never
fabricates release or deployment events: it indexes commits and refs only.
Curated history events belong to docs/project/REPO_HISTORY.md, maintained by
evidence-backed reconciliation.

Usage:
    python3 scripts/project_docs/refresh_repo_history.py [--repo PATH ...] [--fetch]

Output:
    docs/project/history/commit-index.tsv  (overwritten deterministically)
    stdout: Markdown rows for the "Current head snapshot" table in
    docs/project/REPO_HISTORY.md, plus a summary line.
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

INDEX_REL = Path("docs/project/history/commit-index.tsv")

CRED_RE = re.compile(r"(https?://)[^/@\s]+(?::[^/@\s]*)?@")


def redact(url: str) -> str:
    return CRED_RE.sub(r"\1***@", url.strip())


def git(repo: Path, *args: str) -> str:
    out = subprocess.run(
        ["git", "-C", str(repo), *args],
        capture_output=True, text=True, check=True,
    )
    return out.stdout


def clean_field(text: str) -> str:
    return re.sub(r"[\t\n\r]+", " ", text).strip()


def collect_refs(repo: Path) -> list[tuple[str, str, str]]:
    """Return (refname, sha, object_type) for heads, remotes, and tags."""
    rows: list[tuple[str, str, str]] = []
    out = git(repo, "for-each-ref",
              "--format=%(refname)%09%(objectname)%09%(objecttype)",
              "refs/heads", "refs/remotes", "refs/tags")
    for line in out.splitlines():
        if not line.strip():
            continue
        name, sha, otype = line.split("\t")
        if name.endswith("/HEAD"):
            continue
        # Annotated tags: record the commit they peel to for readability.
        if otype == "tag":
            sha = git(repo, "rev-list", "-n", "1", name).strip()
        rows.append((name, sha, otype))
    return sorted(rows)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", action="append", default=[],
                        help="Repository path (repeatable). Default: repo containing CWD.")
    parser.add_argument("--fetch", action="store_true",
                        help="Run 'git fetch --all --prune' first (network; off by default).")
    args = parser.parse_args()

    repos = [Path(p).resolve() for p in args.repo] if args.repo else [
        Path(git(Path.cwd(), "rev-parse", "--show-toplevel").strip()).resolve()
    ]

    all_rows: list[str] = []
    head_lines: list[str] = []
    for idx, repo in enumerate(repos, start=1):
        repo_id = f"REPO-{idx:02d}"
        if args.fetch:
            git(repo, "fetch", "--all", "--prune")
        remotes = git(repo, "remote", "-v")
        remote_urls = sorted({redact(line.split()[1]) for line in remotes.splitlines() if line.strip()})
        refs = collect_refs(repo)
        seen: set[str] = set()
        log = git(repo, "log", "--all",
                  "--format=%H%x09%P%x09%aI%x09%cI%x09%an%x09%s%x09%D")
        for line in log.splitlines():
            sha, parents, adate, cdate, author, subject, deco = (line.split("\t") + [""] * 7)[:7]
            if sha in seen:
                continue
            seen.add(sha)
            merge = "merge" if len(parents.split()) > 1 else ""
            all_rows.append("\t".join([
                repo_id, sha, clean_field(parents), adate, cdate,
                clean_field(author), clean_field(subject), clean_field(deco), merge,
            ]))
        for name, sha, otype in refs:
            scope = "remote" if name.startswith("refs/remotes/") else "local"
            label = name.replace("refs/remotes/", "", 1).replace("refs/heads/", "", 1).replace("refs/tags/", "tag ", 1)
            head_lines.append(f"| {label} | `{sha}` | {scope} {otype} | |")
        head_lines.append(f"| ({repo_id} remotes: {', '.join(remote_urls) or 'none'}) | | | |")

    # Deterministic order: repo, commit date, sha.
    all_rows.sort(key=lambda r: (r.split("\t")[0], r.split("\t")[3], r.split("\t")[1]))
    index_path = repos[0] / INDEX_REL
    index_path.parent.mkdir(parents=True, exist_ok=True)
    header = "repo\tsha\tparents\tauthor_date\tcommit_date\tauthor\tsubject\tdecorations\tmerge"
    index_path.write_text("\n".join([header, *all_rows]) + "\n", encoding="utf-8")

    print(f"# {index_path.relative_to(repos[0])}: {len(all_rows)} commits indexed across {len(repos)} repo(s)")
    print("# Head snapshot rows for docs/project/REPO_HISTORY.md section 2:")
    print("\n".join(head_lines))
    return 0


if __name__ == "__main__":
    sys.exit(main())
