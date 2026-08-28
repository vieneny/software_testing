#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
BANK_DIR="$(cd -- "${SCRIPT_DIR}/.." && pwd)"
BACKEND_DIR="${BANK_DIR}/backend"
FRONTEND_DIR="${BANK_DIR}/frontend"
PYTHON_BIN="${BACKEND_DIR}/.venv/bin/python"
UVICORN_BIN="${BACKEND_DIR}/.venv/bin/uvicorn"
HOST="${INTERVIEW_BANK_HOST:-127.0.0.1}"
PORT="${INTERVIEW_BANK_PORT:-8000}"
SNAPSHOT_MANIFEST="${BANK_DIR}/data/source-snapshots/manifest.json"

if [[ ! -x "${PYTHON_BIN}" || ! -x "${UVICORN_BIN}" ]]; then
  echo "后端环境尚未安装，请先运行 ${SCRIPT_DIR}/setup.sh" >&2
  exit 1
fi
if [[ ! -f "${FRONTEND_DIR}/package.json" || ! -d "${FRONTEND_DIR}/node_modules" ]]; then
  echo "前端环境尚未安装，请先运行 ${SCRIPT_DIR}/setup.sh" >&2
  exit 1
fi
if [[ ! -f "${SNAPSHOT_MANIFEST}" ]]; then
  echo "提示：尚未生成公开来源的本地快照。来源入口不会跳转外站，但暂时无法阅读正文。" >&2
  echo "需要离线资料时，先运行：${PYTHON_BIN} ${SCRIPT_DIR}/fetch_sources.py" >&2
fi

echo "重建并校验题库数据..."
"${PYTHON_BIN}" "${SCRIPT_DIR}/build_bank.py"

echo "构建 Vue 静态站..."
npm --prefix "${FRONTEND_DIR}" run build

echo "启动地址：http://${HOST}:${PORT}"
exec "${UVICORN_BIN}" app.main:app \
  --app-dir "${BACKEND_DIR}" \
  --host "${HOST}" \
  --port "${PORT}"
