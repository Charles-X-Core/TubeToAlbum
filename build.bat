@echo off
echo ===================================
echo   TubeToAlbum - Build Installer
echo ===================================
echo.

echo [1/4] Verificando Python...
python --version
if %errorlevel% neq 0 (
    echo ERROR: Python no encontrado
    pause
    exit /b 1
)

echo [2/4] Instalando dependencias Python...
pip install pyinstaller -q
pip install -r requirements.txt -q
pip install -r backend/requirements.txt -q

echo [3/4] Instalando dependencias Electron...
cd electron
call npm install
if %errorlevel% neq 0 (
    echo ERROR: npm install failed
    pause
    exit /b 1
)

echo [4/4] Construyendo instalador...
call npm run build
if %errorlevel% neq 0 (
    echo ERROR: Build failed
    pause
    exit /b 1
)

cd ..
echo.
echo ===================================
echo   Build completado!
echo   Installer en: electron/dist/
echo ===================================
pause
