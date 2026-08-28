#!/usr/bin/env bash

set -euo pipefail

LAB_ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
INSTALL_DEPS="${INSTALL_DEPS:-0}"

section() {
  printf '\n[%s]\n' "$1"
}

require_command() {
  if ! command -v "$1" >/dev/null 2>&1; then
    printf '缺少命令：%s。请先按工具安装知识库完成安装。\n' "$1" >&2
    exit 1
  fi
}

prepare_python_dependencies() {
  if [[ "$INSTALL_DEPS" == "1" ]]; then
    (
      cd "$LAB_ROOT/社区问答系统/backend"
      uv sync --dev --locked
    )
    (
      cd "$LAB_ROOT/人工智能中间件"
      uv sync --extra test --locked
    )
  fi
}

prepare_frontend_dependencies() {
  local project_dir="$1"
  if [[ "$INSTALL_DEPS" == "1" ]]; then
    (
      cd "$project_dir"
      npm ci
    )
  elif [[ ! -d "$project_dir/node_modules" ]]; then
    printf '缺少 %s/node_modules。\n' "$project_dir" >&2
    printf '首次运行请使用：INSTALL_DEPS=1 bash ./一键质量检查.sh\n' >&2
    exit 1
  fi
}

select_java_home() {
  local java_bin=""
  local java_major=""
  local brew_java_home="/opt/homebrew/opt/openjdk/libexec/openjdk.jdk/Contents/Home"

  if [[ -n "${JAVA_HOME:-}" && -x "$JAVA_HOME/bin/java" ]]; then
    java_bin="$JAVA_HOME/bin/java"
  elif command -v java >/dev/null 2>&1; then
    java_bin="$(command -v java)"
  fi

  if [[ -n "$java_bin" ]]; then
    java_major="$(
      "$java_bin" -XshowSettings:properties -version 2>&1 |
        awk -F= '/java.specification.version/ {gsub(/[[:space:]]/, "", $2); print $2; exit}'
    )"
  fi

  if [[ ! "$java_major" =~ ^[0-9]+$ || "$java_major" -lt 21 ]]; then
    if [[ -x "$brew_java_home/bin/java" ]]; then
      export JAVA_HOME="$brew_java_home"
      java_major="$(
        "$JAVA_HOME/bin/java" -XshowSettings:properties -version 2>&1 |
          awk -F= '/java.specification.version/ {gsub(/[[:space:]]/, "", $2); print $2; exit}'
      )"
    else
      printf 'Java 项目需要 JDK 21 或更高版本，当前版本为：%s。\n' "${java_major:-未安装}" >&2
      exit 1
    fi
  fi

  printf '使用 JDK %s（JAVA_HOME=%s）\n' "$java_major" "${JAVA_HOME:-系统默认}"
}

require_command uv
require_command npm
require_command mvn

section "准备依赖"
if [[ "$INSTALL_DEPS" == "1" ]]; then
  printf '将依据锁文件安装 Python 与前端依赖。\n'
else
  printf '复用现有依赖；首次运行可设置 INSTALL_DEPS=1。\n'
fi
prepare_python_dependencies
prepare_frontend_dependencies "$LAB_ROOT/社区问答系统/frontend"
prepare_frontend_dependencies "$LAB_ROOT/企业智能客服系统/frontend"

section "Python 社区问答后端"
(
  cd "$LAB_ROOT/社区问答系统/backend"
  uv run --frozen ruff check app tests
  uv run --frozen pytest
)

section "Python 人工智能中间件"
(
  cd "$LAB_ROOT/人工智能中间件"
  uv run --frozen ruff check src tests
  uv run --frozen pytest
)

section "React 社区前端"
(
  cd "$LAB_ROOT/社区问答系统/frontend"
  npm run typecheck
  npm run build
)

section "Vue 客服前端"
(
  cd "$LAB_ROOT/企业智能客服系统/frontend"
  npm run typecheck
  npm run test
  npm run build
)

section "Spring Boot 客服后端"
select_java_home
(
  cd "$LAB_ROOT/企业智能客服系统/backend"
  mvn test
)

section "Docker Compose 配置"
if docker compose version >/dev/null 2>&1; then
  docker compose -f "$LAB_ROOT/社区问答系统/docker-compose.yml" config --quiet
  docker compose -f "$LAB_ROOT/企业智能客服系统/docker-compose.yml" config --quiet
elif command -v docker-compose >/dev/null 2>&1; then
  docker-compose -f "$LAB_ROOT/社区问答系统/docker-compose.yml" config --quiet
  docker-compose -f "$LAB_ROOT/企业智能客服系统/docker-compose.yml" config --quiet
else
  printf '未安装 Docker Compose，跳过编排文件运行时解析；其余检查已完成。\n'
fi

section "完成"
printf '两个项目及统一人工智能中间件的本地质量检查全部通过。\n'
