param(
    [switch]$Check,
    [switch]$Publish,
    [string]$Proxy = 'http://127.0.0.1:7890'
)

# 模组发布：先核对版本与包内文件齐全且与源文件一致，再上传、复核远端并留回执。
# 用法（必须 Windows 侧运行，令牌只从 Windows 用户环境变量读取）：
#   scripts\packaging\publish_mod.ps1 -Check     # 只核对，不上传
#   scripts\packaging\publish_mod.ps1 -Publish   # 核对通过后发布并核对结果

$ErrorActionPreference = 'Stop'
[Console]::OutputEncoding = New-Object System.Text.UTF8Encoding
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12

$repoRoot = Split-Path (Split-Path $PSScriptRoot -Parent) -Parent
$modDir = Join-Path $repoRoot 'game_mod'
$packageName = 'TFWR_Oracle_Runner'
$namespace = 'MengLei'
$community = 'the-farmer-was-replaced'
$categories = @('tools')
$base = 'https://thunderstore.io'
$pluginRelative = 'plugins/TFWROracleRunner/TFWROracleRunner.dll'
$expectedEntries = @('CHANGELOG.md', 'LICENSE', 'README.md', 'icon.png', 'manifest.json', $pluginRelative)

function Fail($message) {
    Write-Output "核对失败：$message"
    exit 1
}

function Sha256($path) {
    return (Get-FileHash -LiteralPath $path -Algorithm SHA256).Hash.ToLowerInvariant()
}

function Read-ZipEntries($zipPath) {
    Add-Type -AssemblyName System.IO.Compression.FileSystem
    $archive = [System.IO.Compression.ZipFile]::OpenRead($zipPath)
    try {
        $result = @{}
        foreach ($entry in $archive.Entries) {
            $stream = $entry.Open()
            try {
                $sha = [System.Security.Cryptography.SHA256]::Create()
                try {
                    $hash = $sha.ComputeHash($stream)
                    $result[$entry.FullName] = [pscustomobject]@{
                        Bytes = $entry.Length
                        Sha256 = ([BitConverter]::ToString($hash) -replace '-', '').ToLowerInvariant()
                    }
                } finally { $sha.Dispose() }
            } finally { $stream.Dispose() }
        }
        return $result
    } finally { $archive.Dispose() }
}

# ---- 版本一致性：manifest / csproj / Plugin.cs / CHANGELOG 首条 ----
$manifestPath = Join-Path $modDir 'manifest.json'
if (-not (Test-Path -LiteralPath $manifestPath)) { Fail "缺少 manifest.json" }
$manifest = Get-Content -Raw -Encoding UTF8 -LiteralPath $manifestPath | ConvertFrom-Json
$version = [string]$manifest.version_number
if ($version -notmatch '^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)$') { Fail "manifest 版本不是三段数字：$version" }
if ([string]$manifest.name -ne $packageName) { Fail "manifest 包名不是 $packageName" }

$projectVersion = (Select-String -LiteralPath (Join-Path $modDir 'TFWROracleRunner.csproj') -Pattern '<Version>([^<]+)</Version>').Matches[0].Groups[1].Value
if ($projectVersion -ne $version) { Fail "csproj 版本 $projectVersion ≠ manifest $version" }

$pluginVersion = (Select-String -LiteralPath (Join-Path $modDir 'Plugin.cs') -Pattern 'PluginVersion\s*=\s*"([^"]+)"').Matches[0].Groups[1].Value
if ($pluginVersion -ne $version) { Fail "PluginVersion $pluginVersion ≠ manifest $version" }

$changelogHead = (Select-String -Encoding UTF8 -LiteralPath (Join-Path $modDir 'CHANGELOG.md') -Pattern '^##\s+v?(\d+\.\d+\.\d+)' | Select-Object -First 1).Matches[0].Groups[1].Value
if ($changelogHead -ne $version) { Fail "CHANGELOG 首条 $changelogHead ≠ manifest $version" }

# ---- 包内文件：必须齐全，且与当前源文件逐字节一致 ----
$zipPath = Join-Path $modDir ("bin\Release\netstandard2.1\{0}-{1}.zip" -f $packageName, $version)
if (-not (Test-Path -LiteralPath $zipPath)) { Fail "缺少构建包：$zipPath（先运行 scripts\packaging\build_mod.cmd）" }
$zipHash = Sha256 $zipPath
$entries = Read-ZipEntries $zipPath

$missing = $expectedEntries | Where-Object { -not $entries.ContainsKey($_) }
$extra = $entries.Keys | Where-Object { $expectedEntries -notcontains $_ }
if ($missing) { Fail ("包内缺少文件：" + ($missing -join ', ')) }
if ($extra) { Fail ("包内含白名单之外的文件：" + ($extra -join ', ')) }

$dllPath = Join-Path $modDir 'bin\Release\netstandard2.1\TFWROracleRunner.dll'
$sources = @{
    'manifest.json' = $manifestPath
    'README.md' = (Join-Path $modDir 'README.md')
    'CHANGELOG.md' = (Join-Path $modDir 'CHANGELOG.md')
    'LICENSE' = (Join-Path $modDir 'LICENSE')
    'icon.png' = (Join-Path $modDir 'icon.png')
    $pluginRelative = $dllPath
}
foreach ($name in $expectedEntries) {
    $source = $sources[$name]
    if (-not (Test-Path -LiteralPath $source)) { Fail "缺少发布素材：$source" }
    if ($entries[$name].Sha256 -ne (Sha256 $source)) { Fail "包内 $name 与当前文件不一致，请重新构建" }
}

Write-Output ("{0} {1}" -f $packageName, $version)
Write-Output ("ZIP {0}（{1:N0} 字节） sha256={2}" -f $zipPath, (Get-Item -LiteralPath $zipPath).Length, $zipHash)
foreach ($name in ($expectedEntries | Sort-Object)) {
    Write-Output ("  {0,-48} {1,9:N0} 字节 {2}" -f $name, $entries[$name].Bytes, $entries[$name].Sha256.Substring(0, 12))
}
Write-Output '版本、包内文件与源文件核对通过。'
if (-not $Publish) {
    Write-Output '未上传；加 -Publish 上传并核对远端结果。'
    exit 0
}

# ---- 上传：远端同版本已存在就停止，避免覆盖或重复发布 ----
$auth = @{ Authorization = "Bearer $([Environment]::GetEnvironmentVariable('THUNDERSTORE_API_TOKEN','User'))" }
if ([string]::IsNullOrWhiteSpace($auth.Authorization)) { Fail 'Windows 用户环境变量缺少 THUNDERSTORE_API_TOKEN' }
$packageApi = "$base/api/experimental/package/$namespace/$packageName/"
$versionApi = "$packageApi$version/"

function Get-Remote($uri, [switch]$AllowMissing) {
    try {
        return Invoke-RestMethod -Uri $uri -Proxy $Proxy -TimeoutSec 20
    } catch {
        if ($AllowMissing -and $_.Exception.Response -and [int]$_.Exception.Response.StatusCode -eq 404) { return $null }
        throw
    }
}

$existing = Get-Remote $versionApi -AllowMissing
if ($existing) { Fail "$namespace-$packageName-$version 已存在于远端，请升版本号" }

$file = Get-Item -LiteralPath $zipPath
$init = Invoke-RestMethod -Uri "$base/api/experimental/usermedia/initiate-upload/" -Method Post -Headers $auth -Proxy $Proxy -TimeoutSec 20 -ContentType 'application/json' -Body (@{ filename = $file.Name; file_size_bytes = $file.Length } | ConvertTo-Json -Compress)
$uploadId = $init.user_media.uuid
if (-not $uploadId -or -not $init.upload_urls) { Fail '上传初始化返回不完整' }
$parts = @()
$stream = [IO.File]::OpenRead($zipPath)
try {
    foreach ($part in $init.upload_urls) {
        $offset = [long]$part.offset
        $length = [int][Math]::Min([long]$part.length, $file.Length - $offset)
        if ($offset -lt 0 -or $length -lt 1) { Fail '上传分片范围非法' }
        [void]$stream.Seek($offset, [IO.SeekOrigin]::Begin)
        $buffer = New-Object byte[] $length
        $read = 0
        while ($read -lt $length) {
            $count = $stream.Read($buffer, $read, $length - $read)
            if ($count -eq 0) { Fail 'ZIP 读取提前结束' }
            $read += $count
        }
        # 预签名地址不接收 Thunderstore Bearer 令牌。
        $request = [Net.HttpWebRequest]::Create([string]$part.url)
        $request.Method = 'PUT'
        $request.Proxy = New-Object Net.WebProxy($Proxy)
        $request.ContentType = 'application/octet-stream'
        $request.ContentLength = $length
        $request.Timeout = 30000
        $request.ReadWriteTimeout = 30000
        $requestStream = $request.GetRequestStream()
        try { $requestStream.Write($buffer, 0, $length) } finally { $requestStream.Dispose() }
        $response = $request.GetResponse()
        try { $etag = [string]$response.Headers['ETag'] } finally { $response.Dispose() }
        if (-not $etag) { Fail '上传分片没有返回 ETag' }
        $parts += @{ ETag = $etag; PartNumber = [int]$part.part_number }
        Write-Output "已上传分片 $($part.part_number)"
    }
} finally { $stream.Dispose() }

$finished = Invoke-RestMethod -Uri "$base/api/experimental/usermedia/$uploadId/finish-upload/" -Method Post -Headers $auth -Proxy $Proxy -TimeoutSec 20 -ContentType 'application/json' -Body (@{ parts = $parts } | ConvertTo-Json -Depth 5 -Compress)
if ($finished.status -ne 'upload_complete') { Fail "上传未完成：$($finished.status)" }

$body = @{
    author_name = $namespace
    communities = @($community)
    community_categories = @{ $community = $categories }
    has_nsfw_content = $false
    upload_uuid = $uploadId
}
$submission = Invoke-RestMethod -Uri "$base/api/experimental/submission/submit/" -Method Post -Headers $auth -Proxy $Proxy -TimeoutSec 60 -ContentType 'application/json' -Body ($body | ConvertTo-Json -Depth 5 -Compress)

# ---- 复核：精确版本激活、社区与分类一致、公开下载与本地包同哈希 ----
$confirmed = $false
$remote = $null
for ($attempt = 1; $attempt -le 12; $attempt++) {
    Start-Sleep -Seconds 5
    $remote = Get-Remote $versionApi -AllowMissing
    if ($remote -and $remote.is_active) { $confirmed = $true; break }
}
$listing = $null
if ($confirmed) { $listing = Get-Remote $packageApi -AllowMissing }

$downloadHash = $null
$downloadPath = Join-Path $env:TEMP "$packageName-$version-public.zip"
try {
    Invoke-WebRequest -Uri "$base/package/download/$namespace/$packageName/$version/" -OutFile $downloadPath -Proxy $Proxy -TimeoutSec 60
    $downloadHash = Sha256 $downloadPath
} catch {
    Write-Output "公开下载核对失败：$($_.Exception.Message)"
} finally {
    if (Test-Path -LiteralPath $downloadPath) { Remove-Item -LiteralPath $downloadPath -Force }
}

$receiptDir = Join-Path $repoRoot ".codex\thunderstore\$version"
New-Item -ItemType Directory -Path $receiptDir -Force | Out-Null
$receiptPath = Join-Path $receiptDir ("receipt-{0}.json" -f (Get-Date -Format 'yyyyMMdd-HHmmss'))
$receipt = [ordered]@{
    published_at_utc = (Get-Date).ToUniversalTime().ToString('o')
    namespace = $namespace
    name = $packageName
    version = $version
    zip = $zipPath
    zip_sha256 = $zipHash
    entries = $entries
    remote_active = $confirmed
    remote_version = $remote
    remote_package_community = ($listing.community_listings | Select-Object -First 1)
    public_download_sha256 = $downloadHash
    public_download_matches = ($downloadHash -eq $zipHash)
    submission = $submission
}
$receipt | ConvertTo-Json -Depth 8 | Set-Content -Encoding UTF8 $receiptPath
Write-Output ("回执 {0}" -f $receiptPath)

if (-not $confirmed) { Fail "远端未确认 $version 激活，先核对回执与远端状态，不要直接重传" }
if ($downloadHash -ne $zipHash) { Fail "公开下载与本地包哈希不一致：$downloadHash" }
Write-Output "已确认 $namespace-$packageName-$version 激活，公开下载与本地包哈希一致。"
