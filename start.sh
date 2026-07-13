#!/usr/bin/env bash
# Agent Desktop — macOS / Linux launcher
# Usage: ./start.sh [--dev|--docker]
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# ── 找 Python ────────────────────────────────────────────────────────────────
PYTHON=""
for cmd in python3 python; do
  if command -v "$cmd" &>/dev/null; then
    PYTHON="$cmd"
    break
  fi
done

if [[ -z "$PYTHON" ]]; then
  echo "❌  Python not found. Please install Python 3.8+ and re-run."
  exit 1
fi

PYVER=$("$PYTHON" -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
echo "✔  Python $PYVER ($PYTHON)"

# ── 安裝 Python 依賴（若尚未安裝）───────────────────────────────────────────
if ! "$PYTHON" -c "import aiohttp, aiohttp_cors" &>/dev/null 2>&1; then
  echo "📦  Installing Python dependencies..."
  "$PYTHON" -m pip install -r "$SCRIPT_DIR/backend/requirements.txt" --quiet
fi

# ── 檢查是否已導入 Agency Agents ───────────────────────────────────────────
FLAG_FILE="$HOME/.claude/agency_imported.flag"
if [[ ! -f "$FLAG_FILE" ]]; then
  echo "======================================================================"
  echo " Do you want to import 140+ specialized agents and department teams"
  echo " from msitarzewski/agency-agents?"
  echo "======================================================================"
  read -p "Import now? (y/n): " IMPORT_CHOICE
  if [[ "$IMPORT_CHOICE" =~ ^[Yy]$ ]]; then
    echo "[Import] Importing agency agents (this may take a minute)..."
    "$PYTHON" "$SCRIPT_DIR/backend/agency_agents_importer.py"
  fi
  echo ""
fi

# ── Docker 模式 ──────────────────────────────────────────────────────────────
if [[ "${1:-}" == "--docker" ]]; then
  echo "🐳  Starting backend + dev-frontend via Docker Compose [dev profile]..."
  cd "$SCRIPT_DIR"
  docker compose --profile dev up -d
  echo ""
  echo "   Backend:  http://localhost:8765"
  echo "   Frontend: http://localhost:4200 (Dev HMR)"
  echo ""
  npx electron . --docker
  exit 0
fi

# ── 開發模式 vs 正式模式 ─────────────────────────────────────────────────────
# 本機後端一律交給 Electron 的 startBackend()（electron/main.js）自動啟動，
# 這裡不再重複 spawn `python main.py`——兩邊各自啟動一次會搶同一個 8765
# 埠，其中一個必然綁定失敗，留下沒用的孤兒行程（跟 start.bat 同一類問題，
# 一起修正）。
if [[ "${1:-}" == "--dev" ]]; then
  echo "🔧  Dev mode: starting Angular HMR server..."
  cd "$SCRIPT_DIR/frontend"
  npm run start &
  FRONTEND_PID=$!
  trap "kill $FRONTEND_PID 2>/dev/null || true" EXIT

  echo ""
  echo "   Backend:  http://localhost:8765  (由 Electron 自動啟動)"
  echo "   Frontend: http://localhost:4200  (HMR)"
  echo ""
  echo "   Waiting 12 s for Angular to compile..."
  sleep 12

  cd "$SCRIPT_DIR"
  npx electron . --dev
else
  echo ""
  echo "   Backend: http://localhost:8765  (由 Electron 自動啟動)"
  echo ""
  echo "   Launching Electron..."
  cd "$SCRIPT_DIR"
  npx electron .
fi
