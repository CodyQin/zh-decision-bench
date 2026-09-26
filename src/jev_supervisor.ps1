# Jev grinder supervisor: run grinder synchronously, restart after 30s if not done.
# ASCII-only: PowerShell 5.1 mis-parses BOM-less UTF-8 scripts.
Set-Location "C:\Users\Cody Qin\Projects\zh-decision-bench"
$log = "results\raw\supervisor.log"
function Log($msg) {
    "$(Get-Date -Format 'MM-dd HH:mm:ss')  $msg" | Add-Content -Path $log -Encoding UTF8
}
Log "supervisor started"
$round = 0
while ($true) {
    $done = Select-String -Path "results\raw\jev_e1.log" -Pattern "Finish|complete" -Quiet -ErrorAction SilentlyContinue
    $lines = (Get-Content "results\raw\jev_e1.jsonl" -ErrorAction SilentlyContinue | Measure-Object -Line).Lines
    if ($done -or $lines -ge 285) { Log "DONE detected (lines=$lines), supervisor exit"; break }
    $round += 1
    Log ("round {0}: start grinder (lines={1})" -f $round, $lines)
    & ".\.venv\Scripts\python.exe" "src\run_eval.py" --model jev --data data/massive_items.jsonl data/synthetic_items.jsonl --out jev_e1 --resume *>> "results\raw\jev_e1.log"
    Log ("round {0}: grinder exited (code {1}), retry in 30s" -f $round, $LASTEXITCODE)
    Start-Sleep -Seconds 30
}
