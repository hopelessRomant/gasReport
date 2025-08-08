@echo off
REM Get the directory of this .bat file (Windows path)
set SCRIPT_DIR=%~dp0

REM Call WSL directly with the converted path and execute run.sh
wsl bash -c "cd \"$(wslpath '%SCRIPT_DIR%')\" && ./run.sh"

pause
