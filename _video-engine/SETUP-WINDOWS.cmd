@echo off
cd /d "%~dp0"
if not exist package.json (echo Run this file from the project folder with package.json & pause & exit /b 1)
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\setup.ps1
pause
