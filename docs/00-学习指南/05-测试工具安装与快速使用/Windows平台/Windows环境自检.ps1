$ErrorActionPreference = "Continue"

Write-Host "=== Windows 测试环境自检（不安装、不改配置） ===" -ForegroundColor Cyan
Write-Host "时间: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"

$system = Get-ComputerInfo |
    Select-Object WindowsProductName, WindowsVersion, OsBuildNumber, OsArchitecture
$system | Format-List

$checks = @(
    @{ Name = "Git"; Command = "git"; Arguments = @("--version"); Required = $true },
    @{ Name = "Python 管理器"; Command = "py"; Arguments = @("list"); Required = $false },
    @{ Name = "Python"; Command = "python"; Arguments = @("--version"); Required = $true },
    @{ Name = "Conda"; Command = "conda"; Arguments = @("--version"); Required = $false },
    @{ Name = "Node.js"; Command = "node"; Arguments = @("-v"); Required = $false },
    @{ Name = "npm"; Command = "npm.cmd"; Arguments = @("-v"); Required = $false },
    @{ Name = "Java"; Command = "java"; Arguments = @("-version"); Required = $false },
    @{ Name = "Java 编译器"; Command = "javac"; Arguments = @("-version"); Required = $false },
    @{ Name = "MySQL"; Command = "mysql"; Arguments = @("--version"); Required = $false },
    @{ Name = "Docker"; Command = "docker"; Arguments = @("--version"); Required = $false },
    @{ Name = "ADB"; Command = "adb"; Arguments = @("version"); Required = $false },
    @{ Name = "Appium"; Command = "appium"; Arguments = @("--version"); Required = $false },
    @{ Name = "k6"; Command = "k6"; Arguments = @("version"); Required = $false },
    @{ Name = "VS Code"; Command = "code"; Arguments = @("--version"); Required = $false }
)

$missingRequired = 0

foreach ($check in $checks) {
    $resolved = Get-Command $check.Command -ErrorAction SilentlyContinue
    if (-not $resolved) {
        $level = if ($check.Required) { "必需项缺失" } else { "可选项未安装" }
        $color = if ($check.Required) { "Red" } else { "DarkYellow" }
        Write-Host "[$level] $($check.Name): $($check.Command)" -ForegroundColor $color
        if ($check.Required) {
            $missingRequired += 1
        }
        continue
    }

    Write-Host "[已找到] $($check.Name): $($resolved.Source)" -ForegroundColor Green
    try {
        $argumentList = @($check.Arguments)
        $output = & $check.Command @argumentList 2>&1 |
            Select-Object -First 5
        $output | ForEach-Object { Write-Host "  $_" }
    }
    catch {
        Write-Host "  版本命令执行失败: $($_.Exception.Message)" -ForegroundColor Yellow
    }
}

$pythonCommand = Get-Command python -ErrorAction SilentlyContinue
if ($pythonCommand) {
    try {
        $pythonVersionText = & python -c "import platform; print(platform.python_version())"
        $pythonVersion = [version]$pythonVersionText.Trim()
        if ($pythonVersion -lt [version]"3.12") {
            Write-Host "[版本基线不通过] 本仓库要求 Python >= 3.12，当前为 $pythonVersion" -ForegroundColor Red
            $missingRequired += 1
        }
        else {
            Write-Host "[版本基线通过] Python >= 3.12" -ForegroundColor Green
        }
    }
    catch {
        Write-Host "[版本检查失败] 无法解析 Python 版本: $($_.Exception.Message)" -ForegroundColor Red
        $missingRequired += 1
    }
}

Write-Host "`n=== 关键环境变量 ===" -ForegroundColor Cyan
foreach ($name in @("JAVA_HOME", "ANDROID_HOME", "APPIUM_HOME")) {
    $value = [Environment]::GetEnvironmentVariable($name, "Process")
    if ($value) {
        $exists = Test-Path $value
        Write-Host "$name=$value (路径存在: $exists)"
    }
    else {
        Write-Host "$name=<未设置>"
    }
}

if (Get-Command adb -ErrorAction SilentlyContinue) {
    Write-Host "`n=== Android 设备 ===" -ForegroundColor Cyan
    adb devices -l 2>&1 | ForEach-Object { Write-Host $_ }
}

Write-Host "`n=== 常用端口监听状态 ===" -ForegroundColor Cyan
foreach ($port in @(3001, 3306, 4723, 5037, 8080, 8866, 8888)) {
    $listeners = Get-NetTCPConnection -State Listen -LocalPort $port -ErrorAction SilentlyContinue
    if ($listeners) {
        foreach ($listener in $listeners) {
            Write-Host "端口 $port 正在监听，PID=$($listener.OwningProcess)" -ForegroundColor Yellow
        }
    }
    else {
        Write-Host "端口 $port 未监听"
    }
}

Write-Host "`n说明：Conda、Node、Java、MySQL、Docker、ADB、Appium、k6 和 VS Code 均为按需项。" -ForegroundColor Cyan
Write-Host "隐私提示：输出可能包含用户名路径、设备标识和进程信息，公开分享前请脱敏。" -ForegroundColor Yellow
if ($missingRequired -gt 0) {
    Write-Host "基础必需项有 $missingRequired 项缺失或不符合版本基线，请先阅读本目录教程。" -ForegroundColor Red
    exit 1
}

Write-Host "基础必需项检查通过。请继续完成对应工具的最小实践。" -ForegroundColor Green
