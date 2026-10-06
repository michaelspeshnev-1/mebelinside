# Автозапуск наблюдателя при входе в Windows (Планировщик заданий). Убрать: -Remove
param([switch]$Remove)
$root = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$name = 'MebelInsideVideoEngine'
if($Remove){ Unregister-ScheduledTask -TaskName $name -Confirm:$false; Write-Host "Автозапуск убран"; exit }
$node = (Get-Command node).Source
$a = New-ScheduledTaskAction -Execute $node -Argument "src\watch.js" -WorkingDirectory $root
$t = New-ScheduledTaskTrigger -AtLogOn
$s = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -RestartCount 3 -RestartInterval (New-TimeSpan -Minutes 1)
Register-ScheduledTask -TaskName $name -Action $a -Trigger $t -Settings $s -Force | Out-Null
Start-ScheduledTask -TaskName $name
Write-Host "Готово: наблюдатель запускается при входе и уже работает. Логи: $root\logs"
