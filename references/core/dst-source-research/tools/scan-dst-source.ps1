[CmdletBinding()]
param(
    [string]$Root,
    [ValidateSet('Summary', 'Files', 'Symbol')]
    [string]$Mode = 'Summary',
    [string]$Pattern,
    [string]$Glob = '*.lua'
)

if ([string]::IsNullOrWhiteSpace($Root)) {
    $Root = $env:DST_SCRIPTS_DIR
}
if ([string]::IsNullOrWhiteSpace($Root)) {
    $Root = 'D:\mods\scripts'
}
$resolvedRoot = (Resolve-Path -LiteralPath $Root -ErrorAction Stop).Path
if (-not (Test-Path -LiteralPath (Join-Path $resolvedRoot 'main.lua') -PathType Leaf)) {
    $resolvedRoot = Join-Path $resolvedRoot 'scripts'
}
foreach ($requiredFile in @('main.lua', 'modutil.lua', 'entityscript.lua')) {
    if (-not (Test-Path -LiteralPath (Join-Path $resolvedRoot $requiredFile) -PathType Leaf)) {
        throw ('Missing ' + $requiredFile + ' in DST scripts directory: ' + $resolvedRoot)
    }
}
Write-Verbose ('Read-only source snapshot: ' + $resolvedRoot + '; version must be verified separately.')

switch ($Mode) {
    'Summary' {
        Get-ChildItem -LiteralPath $resolvedRoot -Directory |
            ForEach-Object {
                [pscustomobject]@{
                    Module = $_.Name
                    LuaFiles = (Get-ChildItem -LiteralPath $_.FullName -Recurse -File -Filter '*.lua').Count
                }
            } |
            Sort-Object LuaFiles -Descending

        [pscustomobject]@{
            Module = '(root)'
            LuaFiles = (Get-ChildItem -LiteralPath $resolvedRoot -File -Filter '*.lua').Count
        }
    }

    'Files' {
        $files = @(
            Get-ChildItem -LiteralPath $resolvedRoot -Recurse -File -Filter $Glob |
                Sort-Object FullName |
                Select-Object -ExpandProperty FullName
        )
        if ($files.Count -eq 0) {
            Write-Host 'No files matched.'
        }
        else {
            $files
        }
    }

    'Symbol' {
        if ([string]::IsNullOrWhiteSpace($Pattern)) {
            throw '-Pattern is required when -Mode Symbol is used.'
        }

        $rg = Get-Command rg -ErrorAction SilentlyContinue
        if ($null -ne $rg) {
            & $rg.Source -n --glob $Glob -- $Pattern $resolvedRoot
            if ($LASTEXITCODE -eq 1) {
                Write-Host 'No symbol matches.'
            }
            elseif ($LASTEXITCODE -gt 1) {
                throw ('rg failed with exit code ' + $LASTEXITCODE)
            }
        }
        else {
            $matches = @(
                Get-ChildItem -LiteralPath $resolvedRoot -Recurse -File -Filter $Glob |
                    Select-String -Pattern $Pattern -CaseSensitive |
                    ForEach-Object {
                        '{0}:{1}:{2}' -f $_.Path, $_.LineNumber, $_.Line.Trim()
                    }
            )
            if ($matches.Count -eq 0) {
                Write-Host 'No symbol matches.'
            }
            else {
                $matches
            }
        }
    }
}
