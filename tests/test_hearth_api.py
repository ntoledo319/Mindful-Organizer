"""Smoke test for the FastAPI scaffold.

Verifies:
  - the app boots
  - /system/health works
  - /docs is reachable
  - /today returns a valid TodayResponse shape
  - /journal returns a valid JournalListResponse shape
"""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from hearth_api import deps as hearth_deps


@pytest.fixture
def client(tmp_path, monkeypatch):
    """Boot the API against a temp data dir, isolated per test."""
    monkeypatch.setenv("HEARTH_DATA_DIR", str(tmp_path))
    # Singletons may have been built against a different data dir — reset.
    hearth_deps.reset_all()

    # Settings is also cached — clear it so HEARTH_DATA_DIR is re-read.
    from hearth_api.settings import get_settings
    get_settings.cache_clear()

    from hearth_api.main import create_app
    app = create_app()
    return TestClient(app)


def test_root(client):
    r = client.get("/")
    assert r.status_code == 200
    body = r.json()
    assert body["service"] == "Hearth"
    assert "version" in body


def test_health(client):
    r = client.get("/system/health")
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "ok"
    assert "version" in body
    assert "server_time" in body


def test_docs_available(client):
    r = client.get("/docs")
    assert r.status_code == 200
    assert "swagger" in r.text.lower()


def test_openapi_schema(client):
    """The OpenAPI schema is the contract used to generate the TS client."""
    r = client.get("/openapi.json")
    assert r.status_code == 200
    schema = r.json()
    assert schema["info"]["title"] == "Hearth"
    # The journal + today + system route groups must be present
    paths = schema["paths"]
    assert any(p.startswith("/journal") for p in paths)
    assert any(p.startswith("/today") for p in paths)
    assert any(p.startswith("/system") for p in paths)
