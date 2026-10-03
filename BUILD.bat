@echo off
chcp 65001 >nul
color 0a
echo.
echo    ═══════════════════════════════════════════════════════════════════
echo     CORE NEXUS v3.2.1 - AUTO BUILD SCRIPT
echo    ═══════════════════════════════════════════════════════════════════

echo.
echo    [SYSTEM] Validating Python environment...
python --version >nul 2>&1
if errorlevel 1 (
    echo.
    echo    [ERROR] Python is not installed or not in PATH.
    echo    Please install Python 3.x first.
    echo.
    pause
    exit /b
)

echo    [OK] Python is available
echo.

echo    [SYSTEM] Checking pyinstaller...
python -m PyInstaller --version >nul 2>&1
if errorlevel 1 (
    echo    [WARNING] pyinstaller is not installed.
    echo    Installing pyinstaller...
    python -m pip install pyinstaller
)

echo    [SYSTEM] Checking required packages...
pip install selenium pywebview undetected-chromedriver requests pystray pillow >nul 2>&1
if errorlevel 1 (
    echo    [WARNING] Could not install all dependencies.
    echo    Please run: pip install selenium pywebview undetected-chromedriver requests pystray pillow
)

echo    [SYSTEM] Cleaning up previous build files...
rmdir /s /q build dist >nul 2>&1
del *.spec >nul 2>&1
echo.

echo    [INFO] Starting build process...
echo    This may take a few minutes depending on your system.
echo.

python -m PyInstaller --noconfirm --onefile --windowed --name="Core Nexus v3.2.1" --icon="rewards.ico" --add-data "rewards.ico;." --add-data "locales.json;." --version-file="version.txt" AppGUI.py

if errorlevel 1 (
    echo.
    echo    [ERROR] Build failed!
    echo    Please check the error messages above.
)

echo.
echo    ═══════════════════════════════════════════════════════════════════
echo    BUILD COMPLETE!
echo    ═══════════════════════════════════════════════════════════════════
echo.

if exist "dist\Core Nexus v3.2.1.exe" (
    echo    [SUCCESS] The application executable is located at:
    echo    dist\Core Nexus v3.2.1.exe
    echo.
)

pause
