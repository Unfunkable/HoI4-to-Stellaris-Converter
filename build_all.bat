@echo off
call build_windows.bat
wsl bash build_linux.sh
echo All builds completed!