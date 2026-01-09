@echo off
REM Script de acceso rápido para iniciar el servidor en modo producción
echo Iniciando servidor en modo PRODUCCION con supervisión automática...
echo.
powershell -ExecutionPolicy Bypass -File "%~dp0run_server.ps1" -Production
pause
