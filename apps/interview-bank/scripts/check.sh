#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
BANK_DIR="$(cd -- "${SCRIPT_DIR}/.." && pwd)"
BACKEND_DIR="${BANK_DIR}/backend"
FRONTEND_DIR="${BANK_DIR}/frontend"
PYTHON_BIN="${BACKEND_DIR}/.venv/bin/python"
PYTEST_BIN="${BACKEND_DIR}/.venv/bin/pytest"

if [[ ! -x "${PYTHON_BIN}" || ! -x "${PYTEST_BIN}" ]]; then
  echo "后端环境尚未安装，请先运行 ${SCRIPT_DIR}/setup.sh" >&2
  exit 1
fi

echo "检查生成数据与源文档一致..."
"${PYTHON_BIN}" "${SCRIPT_DIR}/build_personal_latest.py" --check
"${PYTHON_BIN}" "${SCRIPT_DIR}/build_bank.py" --check
"${PYTHON_BIN}" "${SCRIPT_DIR}/build_offline.py" --check

echo "运行逐题内容质量门禁..."
"${PYTHON_BIN}" "${SCRIPT_DIR}/audit_question_quality.py" --check-report

echo "运行 FastAPI 测试与隐私扫描..."
"${PYTEST_BIN}" "${BACKEND_DIR}/tests"

if [[ -f "${FRONTEND_DIR}/package.json" && -d "${FRONTEND_DIR}/node_modules" ]]; then
  echo "运行 Vue 前端测试、类型检查与构建..."
  npm --prefix "${FRONTEND_DIR}" run test --if-present
  npm --prefix "${FRONTEND_DIR}" run typecheck --if-present
  npm --prefix "${FRONTEND_DIR}" run build
else
  echo "前端依赖尚未安装，已跳过前端检查。"
fi

echo "全部检查通过。"
