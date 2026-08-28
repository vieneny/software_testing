#!/bin/zsh

setopt NO_UNSET

print -P "%F{cyan}=== macOS 测试环境自检（不安装、不改配置） ===%f"
print "时间: $(date '+%Y-%m-%d %H:%M:%S')"
sw_vers
print "uname -m: $(uname -m)"
print "arch: $(arch)"

typeset -a names
typeset -a command_names
typeset -a arguments
typeset -a required

names=(
  "Git"
  "Python"
  "Conda"
  "Node.js"
  "npm"
  "Java"
  "Java 编译器"
  "MySQL"
  "Docker"
  "ADB"
  "Appium"
  "k6"
  "VS Code"
  "Xcode"
)

command_names=(
  "git"
  "python3"
  "conda"
  "node"
  "npm"
  "java"
  "javac"
  "mysql"
  "docker"
  "adb"
  "appium"
  "k6"
  "code"
  "xcodebuild"
)

arguments=(
  "--version"
  "--version"
  "--version"
  "-v"
  "-v"
  "-version"
  "-version"
  "--version"
  "--version"
  "version"
  "--version"
  "version"
  "--version"
  "-version"
)

required=(
  "yes"
  "yes"
  "no"
  "no"
  "no"
  "no"
  "no"
  "no"
  "no"
  "no"
  "no"
  "no"
  "no"
  "no"
)

integer missing_required=0
integer index=1

while (( index <= ${#command_names} )); do
  command_name="${command_names[$index]}"
  if (( $+commands[$command_name] )); then
    command_path="$(command -v "$command_name")"
    print -P "%F{green}[已找到]%f ${names[$index]}: $command_path"
    "$command_name" "${=arguments[$index]}" 2>&1 | head -n 5 | sed 's/^/  /'
  else
    local_appium_path="$HOME/workspace/appium-server/node_modules/.bin/appium"
    if [[ "$command_name" == "appium" && -x "$local_appium_path" ]]; then
      print -P "%F{green}[已找到]%f Appium 项目本地命令: $local_appium_path"
      "$local_appium_path" --version 2>&1 | head -n 5 | sed 's/^/  /'
      (( index += 1 ))
      continue
    fi
    if [[ "${required[$index]}" == "yes" ]]; then
      print -P "%F{red}[必需项缺失]%f ${names[$index]}: $command_name"
      (( missing_required += 1 ))
    else
      print -P "%F{yellow}[可选项未安装]%f ${names[$index]}: $command_name"
    fi
  fi
  (( index += 1 ))
done

if (( $+commands[python3] )); then
  if python3 -c 'import sys; raise SystemExit(0 if sys.version_info >= (3, 12) else 1)'; then
    print -P "%F{green}[版本基线通过]%f Python >= 3.12"
  else
    print -P "%F{red}[版本基线不通过]%f 本仓库要求 Python >= 3.12"
    (( missing_required += 1 ))
  fi
fi

print -P "\n%F{cyan}=== 架构与包管理 ===%f"
if (( $+commands[brew] )); then
  print "Homebrew: $(brew --prefix)"
  print "brew arch: $(file "$(command -v brew)")"
else
  print "Homebrew: <未安装>"
fi

if (( $+commands[python3] )); then
  python3 -c 'import platform, sys; print(f"Python executable: {sys.executable}"); print(f"Python arch: {platform.machine()}")'
fi

if (( $+commands[node] )); then
  print "Node executable: $(node -p 'process.execPath')"
  print "Node arch: $(node -p 'process.arch')"
fi

print -P "\n%F{cyan}=== 关键环境变量 ===%f"
for variable_name in JAVA_HOME ANDROID_HOME APPIUM_HOME; do
  variable_value="${(P)variable_name-}"
  if [[ -n "$variable_value" ]]; then
    if [[ -e "$variable_value" ]]; then
      print "$variable_name=$variable_value (路径存在)"
    else
      print "$variable_name=$variable_value (路径不存在)"
    fi
  else
    print "$variable_name=<未设置>"
  fi
done

if (( $+commands[adb] )); then
  print -P "\n%F{cyan}=== Android 设备 ===%f"
  adb devices -l 2>&1
fi

if (( $+commands[xcrun] )); then
  print -P "\n%F{cyan}=== 已启动 iOS Simulator ===%f"
  xcrun simctl list devices booted 2>&1 | head -n 20
fi

print -P "\n%F{cyan}=== 常用端口监听状态 ===%f"
for port in 3001 3306 4723 5037 8080 8866 8888; do
  listener="$(lsof -nP -iTCP:"$port" -sTCP:LISTEN 2>/dev/null | tail -n +2 | head -n 1)"
  if [[ -n "$listener" ]]; then
    print -P "%F{yellow}端口 $port 正在监听:%f $listener"
  else
    print "端口 $port 未监听"
  fi
done

print
print "说明：Conda、Node、Java、MySQL、Docker、ADB、Appium、k6、VS Code 和 Xcode 均按需安装。"
print -P "%F{yellow}隐私提示：输出可能包含用户名路径、设备标识和进程信息，公开分享前请脱敏。%f"
if (( missing_required > 0 )); then
  print -P "%F{red}基础必需项有 $missing_required 项缺失或不符合版本基线，请先阅读本目录教程。%f"
  exit 1
fi

print -P "%F{green}基础必需项检查通过。请继续完成对应工具的最小实践。%f"
