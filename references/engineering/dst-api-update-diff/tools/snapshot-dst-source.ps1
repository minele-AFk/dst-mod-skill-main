[CmdletBinding()]
param(
    [string]$Root = 'D:\steam\steamapps\common\Don''t Starve Together\data\scripts',
    [string]$OutputPath = '.\dst-source-snapshot.json'
)

function Get-CaptureValues {
    param(
        [string]$Text,
        [string]$Pattern
    )

    @(
        [regex]::Matches($Text, $Pattern) |
            ForEach-Object { $_.Groups[1].Value } |
            Where-Object { -not [string]::IsNullOrWhiteSpace($_) } |
            Sort-Object -Unique
    )
}

function Get-FunctionNames {
    param(
        [string]$Text
    )

    @(
        Get-CaptureValues $Text '(?m)^\s*(?:local\s+)?function\s+([A-Za-z_][A-Za-z0-9_:.]*)'
        Get-CaptureValues $Text '(?m)^\s*(?:local\s+)?([A-Za-z_][A-Za-z0-9_:.]*)\s*=\s*function\s*\('
    ) |
        Where-Object { -not [string]::IsNullOrWhiteSpace($_) } |
        Sort-Object -Unique
}

$resolvedRoot = (Resolve-Path -LiteralPath $Root -ErrorAction Stop).Path
if (-not (Test-Path -LiteralPath (Join-Path $resolvedRoot 'main.lua') -PathType Leaf)) {
    throw ('The root does not look like a DST data/scripts directory: ' + $resolvedRoot)
}

$fullOutput = [System.IO.Path]::GetFullPath($OutputPath)
if ([System.IO.Path]::GetExtension($fullOutput) -ine '.json') {
    throw ('Output path must use a .json extension: ' + $fullOutput)
}
$rootPrefix = $resolvedRoot.TrimEnd([System.IO.Path]::DirectorySeparatorChar) +
    [System.IO.Path]::DirectorySeparatorChar
if ($fullOutput.StartsWith($rootPrefix, [System.StringComparison]::OrdinalIgnoreCase)) {
    throw 'Output path must be outside the read-only DST source root.'
}

$records = @(
    Get-ChildItem -LiteralPath $resolvedRoot -Recurse -File -Filter '*.lua' |
        Sort-Object FullName |
        ForEach-Object {
            $content = [System.IO.File]::ReadAllText($_.FullName)
            $relative = $_.FullName.Substring($resolvedRoot.Length).TrimStart('\').Replace('\', '/')

            [ordered]@{
                path = $relative
                sha256 = (Get-FileHash -LiteralPath $_.FullName -Algorithm SHA256).Hash.ToLowerInvariant()
                functions = @(Get-FunctionNames $content)
                requires = @(Get-CaptureValues $content 'require\s*\(?\s*[''\x22]([^''\x22]+)[''\x22]')
                prefabs = @(Get-CaptureValues $content 'Prefab\s*\(\s*[''\x22]([^''\x22]+)[''\x22]')
                components = @(Get-CaptureValues $content 'AddComponent\s*\(\s*[''\x22]([^''\x22]+)[''\x22]')
                brains = @(Get-CaptureValues $content 'SetBrain\s*\(\s*([A-Za-z_][A-Za-z0-9_.:]*)')
                stategraphs = @(Get-CaptureValues $content 'SetStateGraph\s*\(\s*[''\x22]([^''\x22]+)[''\x22]')
            }
        }
)

$snapshot = [ordered]@{
    schema_version = 1
    generated_utc = [DateTime]::UtcNow.ToString('o')
    source_root = $resolvedRoot
    file_count = $records.Count
    files = $records
}

$parent = Split-Path -Parent $fullOutput
if (-not (Test-Path -LiteralPath $parent -PathType Container)) {
    New-Item -ItemType Directory -Path $parent -Force | Out-Null
}

$json = $snapshot | ConvertTo-Json -Depth 8
$encoding = New-Object System.Text.UTF8Encoding($false)
[System.IO.File]::WriteAllText($fullOutput, $json, $encoding)

[pscustomobject]@{
    OutputPath = $fullOutput
    FileCount = $records.Count
}