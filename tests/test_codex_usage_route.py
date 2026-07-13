import pytest

import codex_usage
import main

pytestmark = pytest.mark.asyncio


async def test_codex_usage_route_returns_normalized_data(client, monkeypatch):
    async def fake_fetch(bin_path):
        return {"available": True, "planType": "plus", "primary": {"remainingPercent": 83}}

    monkeypatch.setattr(codex_usage, "fetch_codex_usage", fake_fetch)
    main._codex_usage_cache = {"data": None, "expires": 0.0}

    response = await client.get("/api/usage/codex")

    assert response.status == 200
    assert (await response.json())["primary"]["remainingPercent"] == 83


async def test_codex_usage_route_maps_client_error_to_502(client, monkeypatch):
    async def fake_fetch(bin_path):
        raise codex_usage.CodexUsageError("not logged in")

    monkeypatch.setattr(codex_usage, "fetch_codex_usage", fake_fetch)
    main._codex_usage_cache = {"data": None, "expires": 0.0}

    response = await client.get("/api/usage/codex")

    assert response.status == 502
    assert "not logged in" in (await response.json())["error"]
