#!/bin/bash

# Cores
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo ""
echo -e "${GREEN}    ═══════════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}     CORE NEXUS v3.2.1 - AUTO BUILD SCRIPT (LINUX / MACOS)${NC}"
echo -e "${GREEN}    ═══════════════════════════════════════════════════════════════════${NC}"
echo ""

echo -e "${GREEN}[SYSTEM]${NC} Validating Python environment..."
if ! command -v python3 &> /dev/null
then
    echo -e "\n${RED}[ERROR]${NC} Python3 is not installed or not in PATH."
    echo "Please install Python 3.x first."
    exit 1
fi
echo -e "${GREEN}[OK]${NC} Python3 is available"
echo ""

echo -e "${GREEN}[SYSTEM]${NC} Checking pyinstaller..."
python3 -m PyInstaller --version >/dev/null 2>&1
if [ $? -ne 0 ]; then
    echo -e "${YELLOW}[WARNING]${NC} pyinstaller is not installed."
    echo "Installing pyinstaller..."
    python3 -m pip install pyinstaller
fi

echo -e "${GREEN}[SYSTEM]${NC} Checking required packages..."
python3 -m pip install --upgrade selenium pywebview undetected-chromedriver requests pystray pillow >/dev/null 2>&1
if [ $? -ne 0 ]; then
    echo -e "${YELLOW}[WARNING]${NC} Could not install all dependencies."
    echo "Please run: pip install selenium pywebview undetected-chromedriver requests pystray pillow"
fi

echo -e "${GREEN}[SYSTEM]${NC} Cleaning up previous build files..."
rm -rf build dist
rm -f *.spec
echo ""

echo -e "${GREEN}[INFO]${NC} Starting build process..."
echo "This may take a few minutes depending on your system."
echo ""

# Nota: no Linux/Mac usa-se : em vez de ; no add-data
python3 -m PyInstaller --noconfirm --onefile --windowed --name="Core Nexus v3.2.1" --icon="rewards.ico" --add-data "rewards.ico:." --add-data "locales.json:." AppGUI.py

if [ $? -ne 0 ]; then
    echo ""
    echo -e "${RED}[ERROR]${NC} Build failed!"
    echo "Please check the error messages above."
    exit 1
fi

echo ""
echo -e "${GREEN}    ═══════════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}    BUILD COMPLETE!${NC}"
echo -e "${GREEN}    ═══════════════════════════════════════════════════════════════════${NC}"
echo ""

if [ -f "dist/Core Nexus v3.2.1" ] || [ -d "dist/Core Nexus v3.2.1.app" ]; then
    echo -e "${GREEN}[SUCCESS]${NC} The application executable is located at:"
    echo "dist/Core Nexus v3.2.1"
    echo ""
fi
