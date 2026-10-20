# Air_wifi_craker

**Air_wifi_craker** is a WiFi security testing tool that detects nearby
wireless networks, displays them in a clean banner UI, and attempts to
crack the selected network's WPA/WPA2 password using a dictionary attack
powered by the `aircrack-ng` suite.

> For authorized penetration testing and security education only.
> Only test networks you own or have explicit written permission to test.

## Features
- Automatic wireless interface detection
- Network scanning via `nmcli` (SSID, channel, signal, encryption)
- Banner UI with numbered network list and `senpai@Air_wifi_craker` prompt
- Handshake capture with `airodump-ng` (monitor mode)
- Dictionary attack with `aircrack-ng`
- On success prints: `Password: <key>`

## Requirements
- Linux (Kali, Parrot, Ubuntu, etc.)
- Python 3.6+
- Root privileges
- A WiFi adapter that supports **monitor mode**
- Tools: `aircrack-ng`, `iw`, `nmcli`

## Installation (Kali,Debian,Ubuntu)
# 1. Clone the repository
git clone https://github.com/bagdigourav3/Air_wifi_craker.git
cd Air_wifi_craker

# 2. Install required tools
sudo apt update
sudo apt install aircrack-ng network-manager wireless-tools wordlists

# 3. (Optional) Unzip the default wordlist
sudo gunzip /usr/share/wordlists/rockyou.txt.gz

# 4. Run the tool
chmod +x install.sh
install.sh

