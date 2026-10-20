#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

# Colors for terminal output formatting
GREEN="\033[0;32m"
RED="\033[0;31m"
YELLOW="\033[1;33m"
NC="\033[0m" # No Color

print_banner() {
    echo -e "${GREEN}"
    echo "    _    _ _      __        ___ ______ ___   ____            _    _               "
    echo "   / \  (_) |    \ \      / (_)  ____|_ _| / ___|_ __ __ _ | | _| | _____ _ __   "
    echo "  / _ \ | | |____ \ \ /\ / /| | |_     | | | |   | '__/ _\` || |/ / |/ / _ \ '__|  "
    echo " / ___ \| | |____| \ V  V / | |  _|    | | | |___| | | (_| ||   <|   <  __/ |     "
    echo "/_/   \_\_|_|       \_/\_/  |_|_|     |___| \____|_|  \__,_||_|\_\_|\_\___|_|     "
    echo -e "${NC}"
    echo -e "${YELLOW}Air_wifi_craker Installer${NC}\n"
}

# Check for root / superuser privileges
check_root() {
    if [ "$EUID" -ne 0 ]; then
        echo -e "${RED}[-] Please run this script with root/sudo privileges (sudo ./install.sh).${NC}"
        exit 1
    fi
}

# Detect system and install core system dependencies
install_dependencies() {
    echo -e "${YELLOW}[*] Updating package lists...${NC}"
    
    if command -v apt &> /dev/null; then
        apt update && apt upgrade -y
        echo -e "${YELLOW}[*] Installing system dependencies (aircrack-ng, python3, python3-pip, iw, wireless-tools)...${NC}"
        apt install -y aircrack-ng python3 python3-pip iw wireless-tools net-tools
    elif command -v pkg &> /dev/null; then
        # Termux environment support
        pkg update -y && pkg upgrade -y
        pkg install -y aircrack-ng python python-pip wireless-tools
    else
        echo -e "${RED}[-] Unsupported package manager. Please install aircrack-ng and python3 manually.${NC}"
        exit 1
    fi
}

# Install Python package dependencies if requirements.txt is present
install_python_deps() {
    if [ -f "requirements.txt" ]; then
        echo -e "${YELLOW}[*] Installing Python dependencies from requirements.txt...${NC}"
        pip3 install -r requirements.txt
    else
        echo -e "${YELLOW}[*] No requirements.txt found. Skipping pip dependencies.${NC}"
    fi
}

# Setup executable permissions and global command symlink
setup_permissions() {
    echo -e "${YELLOW}[*] Setting up executable permissions...${NC}"
    
    # Locate the main python script file dynamically
    MAIN_SCRIPT=""
    if [ -f "air_wifi_craker.py" ]; then
        MAIN_SCRIPT="air_wifi_craker.py"
    elif [ -f "main.py" ]; then
        MAIN_SCRIPT="main.py"
    fi

    if [ -n "$MAIN_SCRIPT" ]; then
        chmod +x "$MAIN_SCRIPT"
        # Create a convenient global symlink
        ln -sf "$(pwd)/$MAIN_SCRIPT" /usr/local/bin/air_wifi_craker
        echo -e "${GREEN}[+] Successfully created global command symlink: air_wifi_craker${NC}"
    else
        echo -e "${YELLOW}[!] Main Python entrypoint script not found in current directory. Please ensure your script file is named properly.${NC}"
    fi
}

main() {
    print_banner
    check_root
    install_dependencies
    install_python_deps
    setup_permissions
    echo -e "\n${GREEN}[+] Installation completed successfully!${NC}"
    echo -e "${YELLOW}You can now run the tool from anywhere using: sudo air_wifi_craker${NC}"
}

main "$@"
