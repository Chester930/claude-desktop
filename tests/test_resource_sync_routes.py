import pytest

from routes import resource_sync as routes

pytestmark = pytest.mark.asyncio


class FakeService:
    def status(self):
        return {"agents": {"missing_in_codex": ["planner"]}, "skills": {}}

    def sync(self, dry_run=False):
        return {"agents": {"created": ["planner"]}, "skills": {}, "was_dry": dry_run}


async def test_resource_sync_status(client, monkeypatch):
    monkeypatch.setattr(routes, "_service", lambda: FakeService())
    response = await client.get("/api/resource-sync")
    assert response.status == 200
    body = await response.json()
    assert body["agents"]["missing_in_codex"] == ["planner"]


async def test_resource_sync_dry_run(client, monkeypatch):
    monkeypatch.setattr(routes, "_service", lambda: FakeService())
    response = await client.post("/api/resource-sync", json={"dry_run": True})
    assert response.status == 200
    body = await response.json()
    assert body["dry_run"] is True
    assert body["was_dry"] is True


async def test_resource_sync_rejects_non_boolean_dry_run(client, monkeypatch):
    monkeypatch.setattr(routes, "_service", lambda: FakeService())
    response = await client.post("/api/resource-sync", json={"dry_run": "yes"})
    assert response.status == 400
