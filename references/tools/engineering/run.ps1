param(
    [Parameter(Mandatory = $true, Position = 0)]
    [ValidateSet('check_api_fast', 'check_api_ast', 'zip_read', 'check_skill', 'test_skill', 'test_api',
        'check_api', 'dst_zip_tool', 'dst_modtest', 'test_tools', 'knowledge', 'test_knowledge',
        'test_knowledge_service')]
    [string]$Tool,
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$ToolArguments
)

$skillRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '../../..')).Path
$workspaceRoot = (Resolve-Path -LiteralPath (Join-Path $skillRoot '../../..')).Path
$projectPython = Join-Path $workspaceRoot '.codex/venvs/dst-skill/Scripts/python.exe'
if (-not (Test-Path -LiteralPath $projectPython -PathType Leaf)) {
    $pythonCommand = Get-Command python -ErrorAction Stop
    $projectPython = $pythonCommand.Source
}
$scripts = @{
    check_api_fast = '../general/check_api.py'
    check_api_ast = 'scripts/check_api.py'
    zip_read = 'scripts/dst_zip_tool.py'
    check_skill = '../general/check_skill.py'
    test_skill = '../../testing/test_skill_maintenance.py'
    test_api = '../../testing/test_check_api.py'
    check_api = 'scripts/check_api.py'
    dst_zip_tool = 'scripts/dst_zip_tool.py'
    dst_modtest = 'scripts/dst_modtest.py'
    test_tools = 'tests/test_tools.py'
    knowledge = '../knowledge/dst_kb_cli.py'
    test_knowledge = '../knowledge/tests/test_skill_knowledge.py'
    test_knowledge_service = '../knowledge/tests/test_service.py'
}
$relativeScript = $scripts[$Tool]
$targetScript = Join-Path $PSScriptRoot $relativeScript
[Console]::Error.WriteLine("Python: {0}`nTool: {1}", $projectPython, $targetScript)
$previousUtf8 = [Environment]::GetEnvironmentVariable('PYTHONUTF8', 'Process')
$previousNoBytecode = [Environment]::GetEnvironmentVariable('PYTHONDONTWRITEBYTECODE', 'Process')
try {
    # -X/-B 只影响当前解释器；环境变量同时覆盖测试工具创建的 Python 子进程。
    $env:PYTHONUTF8 = '1'
    $env:PYTHONDONTWRITEBYTECODE = '1'
    & $projectPython -X utf8 -B $targetScript @ToolArguments
    $toolExitCode = $LASTEXITCODE
}
finally {
    [Environment]::SetEnvironmentVariable('PYTHONUTF8', $previousUtf8, 'Process')
    [Environment]::SetEnvironmentVariable('PYTHONDONTWRITEBYTECODE', $previousNoBytecode, 'Process')
}
exit $toolExitCode
