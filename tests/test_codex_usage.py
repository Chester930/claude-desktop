import asyncio

import pytest

import codex_usage


def test_normalize_codex_usage_exposes_remaining_without_credit_ids():
    rate_limits = {
        "rateLimits": {
            "planType": "plus",
            "primary": {"usedPercent": 17, "windowDurationMins": 10080, "resetsAt": 1784523939},
            "secondary": None,
            "credits": {"hasCredits": False, "unlimited": False, "balance": "0"},
        },
        "rateLimitResetCredits": {
            "availableCount": 3,
            "credits": [{"id": "secret-opaque-id", "status": "available"}],
        },
    }
    token_usage = {
        "summary": {"lifetimeTokens": 1234, "currentStreakDays": 7},
        "dailyUsageBuckets": [{"startDate": "2026-07-12", "tokens": 99}],
    }

    result = codex_usage.normalize_codex_usage(rate_limits, token_usage)

    assert result["available"] is True
    assert result["planType"] == "plus"
    assert result["primary"]["usedPercent"] == 17
    assert result["primary"]["remainingPercent"] == 83
    assert result["resetCreditsAvailable"] == 3
    assert result["tokenUsage"]["lifetimeTokens"] == 1234
    assert "secret-opaque-id" not in str(result)


def test_normalize_clamps_invalid_percentages():
    result = codex_usage.normalize_codex_usage(
        {"rateLimits": {"primary": {"usedPercent": 140}}},
        {"summary": {}},
    )
    assert result["primary"]["usedPercent"] == 100
    assert result["primary"]["remainingPercent"] == 0


class _FakeStdin:
    def __init__(self):
        self.messages = []

    def write(self, data):
        self.messages.append(data.decode("utf-8").strip())

    async def drain(self):
        return None

    def close(self):
        return None

    async def wait_closed(self):
        return None


class _FakeStdout:
    def __init__(self, lines):
        self.lines = [line.encode("utf-8") + b"\n" for line in lines]

    async def readline(self):
        await asyncio.sleep(0)
        return self.lines.pop(0) if self.lines else b""


class _FakeProcess:
    def __init__(self, lines):
        self.stdin = _FakeStdin()
        self.stdout = _FakeStdout(lines)
        self.stderr = _FakeStdout([])
        self.returncode = None

    def terminate(self):
        self.returncode = 0

    def kill(self):
        self.returncode = -9

    async def wait(self):
        self.returncode = 0 if self.returncode is None else self.returncode
        return self.returncode

    async def communicate(self):
        await self.wait()
        return b"", b""


@pytest.mark.asyncio
async def test_fetch_codex_usage_performs_handshake_and_reads_both_responses(monkeypatch):
    proc = _FakeProcess([
        '{"id":1,"result":{"userAgent":"test"}}',
        '{"method":"account/rateLimits/updated","params":{}}',
        '{"id":2,"result":{"rateLimits":{"planType":"pro","primary":{"usedPercent":20}}}}',
        '{"id":3,"result":{"summary":{"lifetimeTokens":55}}}',
    ])

    async def fake_spawn(*args, **kwargs):
        return proc

    monkeypatch.setattr(codex_usage.asyncio, "create_subprocess_exec", fake_spawn)

    result = await codex_usage.fetch_codex_usage("codex", timeout=1)

    assert result["primary"]["remainingPercent"] == 80
    sent = "\n".join(proc.stdin.messages)
    assert '"method":"initialize"' in sent
    assert '"method":"initialized"' in sent
    assert '"method":"account/rateLimits/read"' in sent
    assert '"method":"account/usage/read"' in sent


@pytest.mark.asyncio
async def test_fetch_codex_usage_reports_early_exit(monkeypatch):
    proc = _FakeProcess([])

    async def fake_spawn(*args, **kwargs):
        return proc

    monkeypatch.setattr(codex_usage.asyncio, "create_subprocess_exec", fake_spawn)

    with pytest.raises(codex_usage.CodexUsageError, match="closed"):
        await codex_usage.fetch_codex_usage("codex", timeout=1)
