# Test Audit — 2026-07-14

## Repair outcome (continued session)

The previously recorded repair work was completed later on 2026-07-14.

| Check | Repaired result |
| --- | ---: |
| `python -m pytest -q` | 322/322 passed in 18.73s; command exits normally |
| Angular/Vitest unit tests | 2/2 passed; HTTP initialization is mocked |
| `npx playwright test` | 18 passed, 10 skipped in 26.9s; command exits normally |
| Angular production build | Passed; initial bundle 1.78 MB |
| TypeScript `--noEmit` | Passed |

Changes made:

- Replaced the stale Angular starter-template assertion with application-shell assertions and supplied valid mocked responses for initialization requests.
- Disabled onboarding consistently in UI journeys and updated stale settings, export, and right-panel selectors to match the current UI.
- Added two-second backend probes so backend-dependent E2E tests skip promptly when port 8765 is not provisioned, instead of hanging the suite.
- Removed redundant module-level `pytest.mark.asyncio` declarations. The repository already uses `asyncio_mode = auto`; removing the marks prevents synchronous tests from being incorrectly marked.

Residual non-blocking observations:

- Five Windows Proactor transport cleanup warnings can still appear during the Python suite, but all 322 tests pass and the process exits normally.
- When Playwright runs without the backend, Angular's development proxy logs expected `ECONNREFUSED` messages. Backend tests are reported as skipped, while all browser-only journeys pass.

The sections below preserve the original pre-repair audit for comparison.

## Executive summary

The repository is not fully green when using its documented/default test commands.

- All 322 Python assertions pass when the large backend integration module is split into isolated groups.
- All 15 Codex-specific tests pass.
- Angular production build and TypeScript type checking pass.
- Angular unit tests fail because the root component performs unmocked HTTP requests and one assertion still targets the starter template.
- The current Playwright team-run progress journey passes, but the older E2E suite contains stale selectors and assumptions.
- `python -m pytest` and `python -m pytest tests/test_backend.py` hang when the entire integration module runs in one process.

## Environment

- Date: 2026-07-14
- OS: Windows
- Python: 3.13.5
- pytest: 9.0.2
- Angular: 22
- Vitest: 4.1.9 (resolved runtime version)
- Playwright: 1.61.1
- Browser project: Chromium

## Results

### Backend and Codex

| Scope | Result | Notes |
| --- | ---: | --- |
| Codex-specific tests | 15/15 passed | Usage, route mapping, CLI binary override, API key command |
| Tests excluding `tests/test_backend.py` | 227/227 passed | One process, 6.64 seconds |
| `tests/test_backend.py`, split by class groups | 95/95 passed | All assertions pass in isolated processes |
| Total Python assertions covered | 322/322 passed | Requires isolation of the large integration module |
| `python -m pytest` | Timed out | No final summary after 125 seconds |
| `python -m pytest tests/test_backend.py` | Timed out | No final summary after 95 seconds |

Recurring warnings:

- Synchronous tests inherit `pytest.mark.asyncio`.
- Windows Proactor transports/pipes are not always closed before garbage collection.
- `requests` reports an unsupported urllib3/chardet/charset-normalizer combination.

### Frontend unit and static checks

| Check | Result | Notes |
| --- | ---: | --- |
| `npm run build` | Passed | Initial bundle 1.78 MB; below the 2 MB warning budget |
| `npx tsc -p tsconfig.app.json --noEmit` | Passed | No type errors |
| Angular/Vitest unit suite | Failed | 2 tests discovered |

Unit-test failures:

1. The component creation assertion passes, but the suite exits with an error because component initialization issues unmocked `/api/*` requests.
2. The title test looks for an `h1` containing `Hello, frontend`; the current application no longer renders the starter template.
3. The title test run produced 12 unhandled HTTP errors, including `/api/usage`, `/api/usage/codex`, `/api/stats`, `/api/agents`, `/api/skills`, and `/api/mcp-local-config`.

### Playwright E2E

| Scope | Result | Notes |
| --- | ---: | --- |
| Complete suite | Timed out | No summary after 185 seconds |
| Team-run SSE progress journey | 1/1 passed | Real Chromium with mocked HR/run/SSE endpoints |
| Basic flow group | 5/8 passed | Settings selector/onboarding and backend availability issues |
| Agent/Teams/Memory/HR visibility group | 3/4 passed | Memory tab is no longer present |
| Export/global-search group | 1/2 passed | Export selector is no longer present; Ctrl+K passes |

Observed stale assumptions in `frontend/e2e/app.spec.ts`:

- Most tests do not disable the onboarding overlay.
- Tests look for `Claude Code 使用者`, while the current empty state shows `無代理人`.
- Tests expect a Memory tab that is not present in the current right panel.
- Tests expect `.export-format-select`, which is not present in the current top bar.
- Playwright starts only the Angular server; direct requests to port 8765 can time out when the backend is absent.

## Recommended repair order

1. Mock Angular HTTP dependencies and replace the stale starter-template assertion.
2. Update E2E selectors and globally disable onboarding for UI journeys.
3. Make backend-dependent Playwright tests explicitly detect or provision the backend.
4. Identify shared mutable state/background processes in `tests/test_backend.py` so the documented one-shot pytest command exits.
5. Remove incorrect asyncio marks and close Windows transports cleanly.

## Reproduction commands

```powershell
python -m pytest
python -m pytest --ignore=tests/test_backend.py -q --tb=short
python -m pytest tests/test_backend.py -q --tb=short

Set-Location frontend
npm test -- --watch=false
npm run build
npx tsc -p tsconfig.app.json --noEmit
npx playwright test
npx playwright test e2e/team-run-progress.spec.ts --reporter=line
```

## Repository state

The audit itself was performed before any repair changes. The working tree was clean at the end of the audit.
