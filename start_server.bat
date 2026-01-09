@echo off
REM Script de acceso rápido para iniciar el servidor en modo desarrollo
echo Iniciando servidor con supervisión automática...
echo.
powershell -ExecutionPolicy Bypass -File "%~dp0run_server.ps1"
pause
