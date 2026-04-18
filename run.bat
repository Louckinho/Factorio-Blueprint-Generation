@echo off
pushd %~dp0
powershell -ExecutionPolicy Bypass -File run_dev.ps1
popd
pause
