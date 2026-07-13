from pathlib import Path

from resource_sync import ResourceSyncService


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def test_status_classifies_missing_and_conflicting_resources(tmp_path):
    claude = tmp_path / ".claude"
    codex = tmp_path / ".codex"
    shared = tmp_path / ".agents" / "skills"

    _write(
        claude / "agents" / "planner.md",
        "---\nname: planner\ndescription: Plans work\n---\n\nPlan carefully.\n",
    )
    _write(codex / "agents" / "reviewer.toml", 'name = "reviewer"\n')
    _write(claude / "skills" / "tdd" / "SKILL.md", "# TDD\n")
    _write(shared / "tdd" / "SKILL.md", "# Different TDD\n")

    status = ResourceSyncService(claude, codex, shared).status()

    assert status["agents"]["missing_in_codex"] == ["planner"]
    assert status["agents"]["codex_only"] == ["reviewer"]
    assert status["skills"]["conflicts"] == ["tdd"]


def test_sync_creates_codex_agent_and_skill_without_overwriting_conflicts(tmp_path):
    claude = tmp_path / ".claude"
    codex = tmp_path / ".codex"
    shared = tmp_path / ".agents" / "skills"

    _write(
        claude / "agents" / "planner.md",
        "---\nname: planner\ndescription: Plans work\nmodel: opus\n---\n\nPlan carefully.\n",
    )
    _write(claude / "skills" / "tdd.md", "---\nname: tdd\n---\n\nTest first.\n")
    _write(shared / "keep" / "SKILL.md", "user-owned\n")
    _write(claude / "skills" / "keep" / "SKILL.md", "claude-owned\n")

    result = ResourceSyncService(claude, codex, shared).sync()

    agent = (codex / "agents" / "planner.toml").read_text(encoding="utf-8")
    skill = (shared / "tdd" / "SKILL.md").read_text(encoding="utf-8")
    assert 'name = "planner"' in agent
    assert 'description = "Plans work"' in agent
    assert 'developer_instructions = "' in agent
    assert "Plan carefully." in agent
    assert skill.endswith("Test first.\n")
    assert (shared / "keep" / "SKILL.md").read_text(encoding="utf-8") == "user-owned\n"
    assert result["agents"]["created"] == ["planner"]
    assert result["skills"]["created"] == ["tdd"]
    assert result["skills"]["conflicts"] == ["keep"]


def test_sync_updates_only_managed_codex_agent(tmp_path):
    claude = tmp_path / ".claude"
    codex = tmp_path / ".codex"
    shared = tmp_path / ".agents" / "skills"
    source = claude / "agents" / "planner.md"
    target = codex / "agents" / "planner.toml"

    _write(source, "---\nname: planner\ndescription: v1\n---\n\nFirst body.\n")
    service = ResourceSyncService(claude, codex, shared)
    service.sync()
    _write(source, "---\nname: planner\ndescription: v2\n---\n\nSecond body.\n")

    result = service.sync()

    assert 'description = "v2"' in target.read_text(encoding="utf-8")
    assert "Second body." in target.read_text(encoding="utf-8")
    assert result["agents"]["updated"] == ["planner"]


def test_dry_run_makes_no_files(tmp_path):
    claude = tmp_path / ".claude"
    codex = tmp_path / ".codex"
    shared = tmp_path / ".agents" / "skills"
    _write(claude / "agents" / "planner.md", "---\nname: planner\n---\n\nBody\n")

    result = ResourceSyncService(claude, codex, shared).sync(dry_run=True)

    assert result["agents"]["created"] == ["planner"]
    assert not (codex / "agents" / "planner.toml").exists()


def test_invalid_codex_skill_path_is_a_conflict_in_status_and_sync(tmp_path):
    claude = tmp_path / ".claude"
    codex = tmp_path / ".codex"
    shared = tmp_path / ".agents" / "skills"
    _write(claude / "skills" / "broken.md", "skill body\n")
    _write(shared / "broken", "not a skill directory\n")

    service = ResourceSyncService(claude, codex, shared)

    assert service.status()["skills"]["conflicts"] == ["broken"]
    assert service.sync(dry_run=True)["skills"]["conflicts"] == ["broken"]


def test_equivalent_unmanaged_codex_agent_is_already_synced(tmp_path):
    claude = tmp_path / ".claude"
    codex = tmp_path / ".codex"
    shared = tmp_path / ".agents" / "skills"
    _write(claude / "agents" / "planner.md", "---\nname: planner\ndescription: Plans\n---\n\nBody\n")
    _write(
        codex / "agents" / "planner.toml",
        'name = "planner"\ndescription = "Plans"\ndeveloper_instructions = "Body"\n',
    )

    service = ResourceSyncService(claude, codex, shared)

    assert service.status()["agents"]["synced"] == ["planner"]
    assert service.sync(dry_run=True)["agents"]["conflicts"] == []
