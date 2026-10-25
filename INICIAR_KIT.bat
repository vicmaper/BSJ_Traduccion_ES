@echo off
cd /d "%~dp0"
if exist "%~dp0BSJ_Kit.exe" (start "" "%~dp0BSJ_Kit.exe" & exit /b)
chcp 65001 >nul
set PY=python
where python >nul 2>nul || set PY=py
%PY% --version >nul 2>nul || (echo No encontre Python. Usa BSJ_Kit.exe o instala Python 3 desde python.org ^(marca "Add Python to PATH"^). & pause & exit /b)
%PY% herramientas\bsj_gui.py
