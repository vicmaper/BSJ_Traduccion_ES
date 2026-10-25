@echo off
chcp 65001 >nul
cd /d "%~dp0"
set PY=python
where python >nul 2>nul || set PY=py
%PY% --version >nul 2>nul || (echo No encontre Python. Usa BSJ_Kit.exe o instala Python 3 desde python.org ^(marca "Add Python to PATH"^). & pause & exit /b)
rem Opcional: arrastra tu CSV sobre este .bat para revisarlo antes.
%PY% herramientas\bsj_kit.py generar %*
echo.
pause
