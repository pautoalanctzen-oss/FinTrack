# Script de supervisión del servidor
# Este script reinicia automáticamente el servidor si se cae

param(
    [switch]$Production = $false
)

$ErrorActionPreference = "Continue"
$maxRestarts = 10
$restartCount = 0
$restartWindow = 300  # 5 minutos en segundos
$lastRestartTime = Get-Date

Write-Host "==================================" -ForegroundColor Cyan
Write-Host "  Sistema de Supervisión del Servidor" -ForegroundColor Cyan
Write-Host "==================================" -ForegroundColor Cyan
Write-Host ""

# Determinar el modo
$mode = if ($Production) { "Producción" } else { "Desarrollo" }
Write-Host "Modo: $mode" -ForegroundColor Yellow
Write-Host ""

# Cambiar al directorio correcto
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptPath

while ($true) {
    try {
        # Reiniciar contador si ha pasado suficiente tiempo
        $timeSinceLastRestart = (Get-Date) - $lastRestartTime
        if ($timeSinceLastRestart.TotalSeconds -gt $restartWindow) {
            $restartCount = 0
            Write-Host "Reiniciando contador de reinicios (ventana de tiempo expirada)" -ForegroundColor Green
        }

        # Verificar si se ha excedido el límite de reinicios
        if ($restartCount -ge $maxRestarts) {
            Write-Host "" -ForegroundColor Red
            Write-Host "ERROR CRÍTICO: El servidor se ha reiniciado $maxRestarts veces en $restartWindow segundos." -ForegroundColor Red
            Write-Host "Por favor, revise los logs y corrija los errores antes de reiniciar." -ForegroundColor Red
            Write-Host "Log file: backend.log" -ForegroundColor Yellow
            exit 1
        }

        $restartCount++
        $lastRestartTime = Get-Date
        $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
        
        Write-Host "[$timestamp] Iniciando servidor (intento $restartCount)..." -ForegroundColor Green
        
        # Buscar el ejecutable de Python (venv o sistema)
        $pythonExe = "python"
        $venvPython = Join-Path $scriptPath ".venv\Scripts\python.exe"
        
        if (Test-Path $venvPython) {
            $pythonExe = $venvPython
            Write-Host "Usando Python del entorno virtual: $pythonExe" -ForegroundColor Cyan
        } else {
            Write-Host "Usando Python del sistema" -ForegroundColor Cyan
        }
        
        # Ejecutar el servidor
        if ($Production) {
            # Modo producción
            & $pythonExe -m uvicorn backend.app:app --host 0.0.0.0 --port 8000
        } else {
            # Modo desarrollo con hot-reload
            & $pythonExe -m uvicorn backend.app:app --host 127.0.0.1 --port 8000 --reload
        }
        
        $exitCode = $LASTEXITCODE
        $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
        
        Write-Host "" -ForegroundColor Yellow
        Write-Host "[$timestamp] El servidor se detuvo (código de salida: $exitCode)" -ForegroundColor Yellow
        
        # Si fue una salida limpia (Ctrl+C), no reiniciar
        if ($exitCode -eq 0) {
            Write-Host "Salida limpia detectada. No se reiniciará el servidor." -ForegroundColor Green
            break
        }
        
        Write-Host "Esperando 3 segundos antes de reiniciar..." -ForegroundColor Cyan
        Start-Sleep -Seconds 3
        
    } catch {
        $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
        Write-Host "[$timestamp] Error: $_" -ForegroundColor Red
        Write-Host "Esperando 5 segundos antes de reiniciar..." -ForegroundColor Cyan
        Start-Sleep -Seconds 5
    }
}

Write-Host ""
Write-Host "Script de supervisión finalizado." -ForegroundColor Green
