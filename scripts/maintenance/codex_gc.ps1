param(
    [switch]$Apply,
    [switch]$KeepTmp,
    [double]$TrashDays = 7,
    [double]$MinAgeHours = 2,
    [double]$MaxReportMB = 5,
    [string[]]$KeepDirs = @(
        'drafts', 'tests\simulator-seed-parallel', 'tests\tick-optimizer-cactus-20261113',
        'tests\mush-surface', 'deployments', 'thunderstore', 'sources'
    ),
    [int]$Limit = 15
)

# .codex 回收：临时产物、运行回执、中断下载和超期回收站。
# 必须在 Windows 侧运行（9p 挂载下 WSL 遍历 .codex 要几分钟，NTFS 原生枚举约 3 秒）。
# 默认只报告；-Apply 才删除，并在 .codex\trash\<时间戳>\removed-files.json 留下清单。

$ErrorActionPreference = 'Stop'
[Console]::OutputEncoding = New-Object System.Text.UTF8Encoding
$repoRoot = Split-Path (Split-Path $PSScriptRoot -Parent) -Parent
$codexRoot = Join-Path $repoRoot '.codex'
if (-not (Test-Path -LiteralPath $codexRoot)) { throw ".codex 不存在：$codexRoot" }

$tmpRoot = Join-Path $codexRoot 'tmp'
$trashRoot = Join-Path $codexRoot 'trash'
$keepPrefixes = $KeepDirs | ForEach-Object { (Join-Path $codexRoot $_) + '\' }
$now = Get-Date
$ageLimit = $now.AddHours(-$MinAgeHours)
$trashLimit = $now.AddDays(-$TrashDays)
$reportBytes = $MaxReportMB * 1MB

function Add-Target($list, $item, $category) {
    [void]$list.Add([pscustomobject]@{ Path = $item.FullName; Category = $category; Bytes = $item.Length })
}

$targets = New-Object System.Collections.ArrayList
$kept = 0

$expiredTrash = @()
if (Test-Path -LiteralPath $trashRoot) {
    foreach ($entry in Get-ChildItem -LiteralPath $trashRoot -Directory -Force) {
        if ($entry.Name -match '^\d{8}(-\d{6})?$' -and $entry.LastWriteTime -lt $trashLimit) {
            $expiredTrash += $entry
        } else { $kept++ }
    }
}

$files = Get-ChildItem -LiteralPath $codexRoot -Recurse -File -Force |
    Where-Object { $_.FullName -notlike "$trashRoot\*" -and $_.FullName -notlike "$tmpRoot\*" }

foreach ($file in $files) {
    $skipped = $false
    foreach ($prefix in $keepPrefixes) {
        if ($file.FullName.StartsWith($prefix, [StringComparison]::OrdinalIgnoreCase)) { $skipped = $true; break }
    }
    if ($skipped) { $kept++; continue }
    $isInterrupted = $file.Extension -in @('.part', '.tmp', '.crdownload')
    if ($isInterrupted) { Add-Target $targets $file '中断产物'; continue }
    if ($file.LastWriteTime -ge $ageLimit) { $kept++; continue }
    if ($file.DirectoryName -eq $codexRoot -and $file.Extension -in @('.log', '.pid')) {
        Add-Target $targets $file '散落日志'
    } elseif ($file.Extension -eq '.jsonl' -or $file.Name -eq 'report.json' -or $file.Name -like '*-full.json') {
        Add-Target $targets $file '运行回执'
    } elseif ($file.Extension -eq '.json' -and $file.Length -ge $reportBytes) {
        Add-Target $targets $file '大份 JSON'
    } else { $kept++ }
}

$tmpBytes = 0
if ((Test-Path -LiteralPath $tmpRoot) -and -not $PSBoundParameters.ContainsKey('KeepTmp')) {
    $tmpFiles = Get-ChildItem -LiteralPath $tmpRoot -Recurse -File -Force
    $tmpBytes = ($tmpFiles | Measure-Object Length -Sum).Sum
    Add-Target $targets ([pscustomobject]@{ FullName = $tmpRoot; Length = [long]$tmpBytes }) '临时目录'
}

$trashBytes = 0
foreach ($entry in $expiredTrash) {
    $size = (Get-ChildItem -LiteralPath $entry.FullName -Recurse -File -Force | Measure-Object Length -Sum).Sum
    if (-not $size) { $size = 0 }
    $trashBytes += $size
    Add-Target $targets ([pscustomobject]@{ FullName = $entry.FullName; Length = [long]$size }) '回收站超期'
}

# 规则外顶层条目：.codex 只允许固定七个目录和本 README，其余一律可删。
$allowedTop = @('README.md', 'drafts', 'tests', 'tmp', 'trash', 'deployments', 'thunderstore', 'sources')
foreach ($entry in Get-ChildItem -LiteralPath $codexRoot -Force) {
    if ($allowedTop -contains $entry.Name) { continue }
    $size = $null
    if ($entry.PSIsContainer) {
        $size = (Get-ChildItem -LiteralPath $entry.FullName -Recurse -File -Force -ErrorAction SilentlyContinue |
            Measure-Object Length -Sum).Sum
    } else { $size = $entry.Length }
    if (-not $size) { $size = 0 }
    Add-Target $targets ([pscustomobject]@{ FullName = $entry.FullName; Length = [long]$size }) '规则外顶层'
}

$totalBytes = ($targets | Measure-Object Bytes -Sum).Sum
if (-not $totalBytes) { $totalBytes = 0 }
Write-Output ("仓库 {0}（apply={1}）" -f $codexRoot, $Apply.IsPresent)
# 本次研究单独允许：Josh 28:03 视频整段及逐帧分析不计入 .codex 容量，也不参与回收。
$sourceRoot = Join-Path $codexRoot 'sources'
$exemptRoot = Join-Path $sourceRoot 'videos\youtube-hdBSvuOim74'
$sourceBytes = ($files | Where-Object {
    $_.FullName.StartsWith("$sourceRoot\", [StringComparison]::OrdinalIgnoreCase) -and
    -not $_.FullName.StartsWith("$exemptRoot\", [StringComparison]::OrdinalIgnoreCase) } | Measure-Object Length -Sum).Sum
$currentBytes = (Get-ChildItem -LiteralPath $codexRoot -Recurse -File -Force |
    Where-Object { -not $_.FullName.StartsWith("$exemptRoot\", [StringComparison]::OrdinalIgnoreCase) } |
    Measure-Object Length -Sum).Sum
Write-Output ("当前 .codex {0:N1} MiB，其中来源证据 {1:N1} MiB（已排除 youtube-hdBSvuOim74）" -f ($currentBytes / 1MB), ($sourceBytes / 1MB))
if ($sourceBytes -gt 250MB) { Write-Warning '来源证据超过 250 MiB；请精简重复帧和可重建产物后再保存新素材。' }
if ($currentBytes -gt 512MB) { Write-Warning '.codex 超过 512 MiB；请先回收临时产物，再检查来源证据、部署备份和发布回执。' }
Write-Output ("待清理 {0} 项，共 {1:N1} MB；保留跳过 {2} 个文件" -f $targets.Count, ($totalBytes / 1MB), $kept)
foreach ($group in $targets | Group-Object Category | Sort-Object Name) {
    $sum = ($group.Group | Measure-Object Bytes -Sum).Sum
    Write-Output ("  {0}: {1} 项，{2:N1} MB" -f $group.Name, $group.Count, ($sum / 1MB))
}
foreach ($item in $targets | Sort-Object Bytes -Descending | Select-Object -First $Limit) {
    Write-Output ("{0,10:N1} MB  [{1}] {2}" -f ($item.Bytes / 1MB), $item.Category, $item.Path.Substring($codexRoot.Length + 1))
}

if (-not $Apply) {
    Write-Output '只报告未删除；加 -Apply 执行。'
    exit 0
}

$stamp = $now.ToString('yyyyMMdd-HHmmss')
$manifestDir = Join-Path $trashRoot $stamp
New-Item -ItemType Directory -Path $manifestDir -Force | Out-Null
$removed = 0
$failed = 0
foreach ($item in $targets) {
    try {
        if (Test-Path -LiteralPath $item.Path -PathType Container) {
            Remove-Item -LiteralPath $item.Path -Recurse -Force
        } else {
            Remove-Item -LiteralPath $item.Path -Force
        }
        $removed += $item.Bytes
    } catch {
        Write-Output ("删除失败 {0}：{1}" -f $item.Path, $_.Exception.Message)
        $failed++
    }
}
$records = $targets | ForEach-Object {
    [pscustomobject]@{ path = $_.Path.Substring($codexRoot.Length + 1); category = $_.Category; bytes = $_.Bytes }
}
$records | ConvertTo-Json -Depth 3 | Set-Content -Encoding UTF8 (Join-Path $manifestDir 'removed-files.json')
$after = (Get-ChildItem -LiteralPath $codexRoot -Recurse -File -Force | Measure-Object Length -Sum).Sum
Write-Output ("已释放 {0:N1} MB，失败 {1} 项；清单 trash\{2}\removed-files.json；当前 .codex {3:N1} MB" -f ($removed / 1MB), $failed, $stamp, ($after / 1MB))
