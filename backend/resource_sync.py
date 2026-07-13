"""Safe Agent/Skill deployment from Agent Desktop's Claude home to Codex.

Agent Desktop and Claude Code already share the same ``~/.claude`` files.  Codex
uses different native locations and, for agents, a different file format.  This
module therefore treats the configured Claude home as the canonical source and
materialises Codex-compatible copies without overwriting user-owned targets.
"""

from __future__ import annotations

import hashlib
import json
import shutil
import tomllib
from pathlib import Path

import yaml


MANAGED_MARKER = "# Managed by Agent Desktop resource sync."
SKILL_MARKER = ".agent-desktop-sync.json"


def _frontmatter_and_body(path: Path) -> tuple[dict, str]:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return {}, text.strip()
    lines = text.splitlines()
    try:
        end = lines.index("---", 1)
    except ValueError:
        return {}, text.strip()
    try:
        metadata = yaml.safe_load("\n".join(lines[1:end])) or {}
    except yaml.YAMLError:
        metadata = {}
    if not isinstance(metadata, dict):
        metadata = {}
    return metadata, "\n".join(lines[end + 1 :]).strip()


def _agent_toml(source: Path) -> str:
    metadata, body = _frontmatter_and_body(source)
    name = str(metadata.get("name") or source.stem)
    description = str(metadata.get("description") or "")
    digest = hashlib.sha256(source.read_bytes()).hexdigest()
    # JSON strings are valid TOML basic strings and safely handle arbitrary
    # Markdown backslashes/quotes without hand-written TOML escaping.
    return (
        f"{MANAGED_MARKER}\n"
        f"# source-sha256: {digest}\n"
        f"name = {json.dumps(name, ensure_ascii=False)}\n"
        f"description = {json.dumps(description, ensure_ascii=False)}\n"
        f"developer_instructions = {json.dumps(body, ensure_ascii=False)}\n"
    )


def _agent_equivalent(source: Path, target: Path) -> bool:
    metadata, body = _frontmatter_and_body(source)
    expected = {
        "name": str(metadata.get("name") or source.stem),
        "description": str(metadata.get("description") or ""),
        "developer_instructions": body,
    }
    try:
        actual = tomllib.loads(target.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, tomllib.TOMLDecodeError):
        return False
    return all(actual.get(key) == value for key, value in expected.items())


def _skill_payload(source: Path) -> dict[str, bytes]:
    if source.is_file():
        return {"SKILL.md": source.read_bytes()}

    payload: dict[str, bytes] = {}
    for path in sorted(source.rglob("*")):
        if path.is_file() and path.name != SKILL_MARKER:
            payload[path.relative_to(source).as_posix()] = path.read_bytes()
    if "SKILL.md" not in payload and "README.md" in payload:
        payload["SKILL.md"] = payload.pop("README.md")
    return payload


def _payload_hash(payload: dict[str, bytes]) -> str:
    digest = hashlib.sha256()
    for name, content in sorted(payload.items()):
        digest.update(name.encode("utf-8"))
        digest.update(b"\0")
        digest.update(content)
        digest.update(b"\0")
    return digest.hexdigest()


def _skill_entry_hash(source: Path) -> str:
    """Fast identity used by status/dry-run; assets are read only when syncing."""
    if source.is_file():
        content = source.read_bytes()
    else:
        entry = source / "SKILL.md"
        if not entry.is_file():
            entry = source / "README.md"
        content = entry.read_bytes()
    return hashlib.sha256(content).hexdigest()


def _write_skill_payload(target: Path, payload: dict[str, bytes]) -> None:
    target.mkdir(parents=True, exist_ok=True)
    for relative, content in payload.items():
        path = target / Path(relative)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)
    marker = {
        "managed_by": "agent-desktop",
        "entry_sha256": hashlib.sha256(payload.get("SKILL.md", b"")).hexdigest(),
    }
    (target / SKILL_MARKER).write_text(
        json.dumps(marker, ensure_ascii=False, indent=2), encoding="utf-8"
    )


class ResourceSyncService:
    """Inspect and deploy Claude-home Agents/Skills to Codex native paths."""

    def __init__(self, claude_home: Path, codex_home: Path, codex_skills: Path):
        self.claude_home = Path(claude_home)
        self.codex_home = Path(codex_home)
        self.codex_skills = Path(codex_skills)

    @property
    def claude_agents(self) -> Path:
        return self.claude_home / "agents"

    @property
    def claude_skills(self) -> Path:
        return self.claude_home / "skills"

    def _agent_sources(self) -> dict[str, Path]:
        if not self.claude_agents.exists():
            return {}
        return {p.stem: p for p in self.claude_agents.glob("*.md") if p.is_file()}

    def _agent_targets(self) -> dict[str, Path]:
        root = self.codex_home / "agents"
        if not root.exists():
            return {}
        return {p.stem: p for p in root.glob("*.toml") if p.is_file()}

    def _skill_sources(self) -> dict[str, Path]:
        if not self.claude_skills.exists():
            return {}
        result: dict[str, Path] = {}
        for entry in self.claude_skills.iterdir():
            if entry.is_file() and entry.suffix.lower() == ".md":
                result[entry.stem] = entry
            elif entry.is_dir() and (
                (entry / "SKILL.md").is_file() or (entry / "README.md").is_file()
            ):
                result[entry.name] = entry
        return result

    def _skill_targets(self) -> dict[str, Path]:
        if not self.codex_skills.exists():
            return {}
        return {p.name: p for p in self.codex_skills.iterdir()}

    @staticmethod
    def _is_managed_agent(path: Path) -> bool:
        try:
            return path.read_text(encoding="utf-8").startswith(MANAGED_MARKER)
        except OSError:
            return False

    @staticmethod
    def _is_managed_skill(path: Path) -> bool:
        return (path / SKILL_MARKER).is_file()

    def status(self) -> dict:
        agent_sources = self._agent_sources()
        agent_targets = self._agent_targets()
        skill_sources = self._skill_sources()
        skill_targets = self._skill_targets()

        agents = {
            "synced": [], "missing_in_codex": [], "outdated": [],
            "conflicts": [], "codex_only": sorted(set(agent_targets) - set(agent_sources)),
        }
        for name, source in sorted(agent_sources.items()):
            target = agent_targets.get(name)
            if target is None:
                agents["missing_in_codex"].append(name)
            elif target.is_symlink():
                agents["conflicts"].append(name)
            elif target.read_text(encoding="utf-8") == _agent_toml(source) or _agent_equivalent(source, target):
                agents["synced"].append(name)
            elif self._is_managed_agent(target):
                agents["outdated"].append(name)
            else:
                agents["conflicts"].append(name)

        skills = {
            "synced": [], "missing_in_codex": [], "outdated": [],
            "conflicts": [], "codex_only": sorted(set(skill_targets) - set(skill_sources)),
        }
        for name, source in sorted(skill_sources.items()):
            target = skill_targets.get(name)
            source_hash = _skill_entry_hash(source)
            if target is None:
                skills["missing_in_codex"].append(name)
                continue
            if target.is_symlink() or not target.is_dir() or not (target / "SKILL.md").is_file():
                bucket = "outdated" if self._is_managed_skill(target) else "conflicts"
                skills[bucket].append(name)
                continue
            target_hash = _skill_entry_hash(target)
            if source_hash == target_hash:
                skills["synced"].append(name)
            elif self._is_managed_skill(target):
                skills["outdated"].append(name)
            else:
                skills["conflicts"].append(name)

        return {"agents": agents, "skills": skills}

    def sync(self, dry_run: bool = False) -> dict:
        result = {
            "agents": {"created": [], "updated": [], "conflicts": []},
            "skills": {"created": [], "updated": [], "conflicts": []},
        }
        agent_targets = self._agent_targets()
        for name, source in sorted(self._agent_sources().items()):
            target = agent_targets.get(name) or (self.codex_home / "agents" / f"{name}.toml")
            expected = _agent_toml(source)
            if target.is_symlink():
                result["agents"]["conflicts"].append(name)
                continue
            if target.exists() and (
                target.read_text(encoding="utf-8") == expected or _agent_equivalent(source, target)
            ):
                continue
            if target.exists() and not self._is_managed_agent(target):
                result["agents"]["conflicts"].append(name)
                continue
            action = "updated" if target.exists() else "created"
            result["agents"][action].append(name)
            if not dry_run:
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text(expected, encoding="utf-8")

        skill_targets = self._skill_targets()
        for name, source in sorted(self._skill_sources().items()):
            target = skill_targets.get(name) or (self.codex_skills / name)
            source_hash = _skill_entry_hash(source)
            target_valid = not target.is_symlink() and target.is_dir() and (target / "SKILL.md").is_file()
            if target.exists() and target_valid and _skill_entry_hash(target) == source_hash:
                continue
            if target.exists() and not self._is_managed_skill(target):
                result["skills"]["conflicts"].append(name)
                continue
            action = "updated" if target.exists() else "created"
            result["skills"][action].append(name)
            if not dry_run:
                payload = _skill_payload(source)
                if target.exists():
                    shutil.rmtree(target)
                _write_skill_payload(target, payload)
        return result
