#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
BANK_DIR="$(cd -- "${SCRIPT_DIR}/.." && pwd)"
BACKEND_DIR="${BANK_DIR}/backend"
FRONTEND_DIR="${BANK_DIR}/frontend"

echo "安装 FastAPI 后端与测试依赖..."
if command -v uv >/dev/null 2>&1; then
  uv sync --project "${BACKEND_DIR}" --extra dev
else
  if command -v python3 >/dev/null 2>&1; then
    PYTHON_COMMAND="$(command -v python3)"
  elif command -v python >/dev/null 2>&1; then
    PYTHON_COMMAND="$(command -v python)"
  else
    echo "未找到 Python。请先安装 Python 3.11 或更高版本。" >&2
    exit 1
  fi
  if ! "${PYTHON_COMMAND}" -c 'import sys; raise SystemExit(0 if sys.version_info >= (3, 11) else 1)'; then
    echo "当前 Python 版本低于 3.11，请升级后重试。" >&2
    exit 1
  fi
  "${PYTHON_COMMAND}" -m venv "${BACKEND_DIR}/.venv"
  "${BACKEND_DIR}/.venv/bin/python" -m pip install --upgrade pip
  "${BACKEND_DIR}/.venv/bin/python" -m pip install -e "${BACKEND_DIR}[dev]"
fi

if [[ ! -f "${FRONTEND_DIR}/package.json" ]]; then
  echo "未找到 frontend/package.json，无法安装前端依赖。" >&2
  exit 1
fi
if ! command -v npm >/dev/null 2>&1; then
  echo "未找到 npm。请先安装当前 LTS 版 Node.js。" >&2
  exit 1
fi

echo "安装 Vue 前端依赖..."
if [[ -f "${FRONTEND_DIR}/package-lock.json" ]]; then
  npm --prefix "${FRONTEND_DIR}" ci
else
  npm --prefix "${FRONTEND_DIR}" install
fi

echo "环境准备完成。"
