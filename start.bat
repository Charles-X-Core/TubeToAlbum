@echo off
echo ===================================
echo   TubeToAlbum - Iniciando...
echo ===================================
echo.

echo [1/2] Iniciando Backend Python...
start "TubeToAlbum Backend" cmd /k "cd /d %~dp0backend && pip install -r requirements.txt -q && python server.py"

echo [2/2] Esperando Backend (3 segundos)...
timeout /t 3 /nobreak >nul

echo [3/3] Iniciando Electron...
cd /d %~dp0electron
if not exist node_modules (
    echo Instalando dependencias...
    call npm install
)
call npm start
