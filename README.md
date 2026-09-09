# 🛡️ Net Spoofer

**MAC & IP Randomizer – Local Network Anonymity Tool**

![Python](https://img.shields.io/badge/Python-3.x-green?logo=python)
![License](https://img.shields.io/badge/License-MIT-lightgrey)

---

## 📖 Table of Contents
- [Overview](#overview)
- [Features](#features)
- [How It Works](#how-it-works)
- [Requirements](#requirements)
- [Installation](#installation)
- [Usage](#usage)
- [Workflow](#workflow)
- [Troubleshooting](#troubleshooting)
- [Security Considerations](#security-considerations)
- [File Structure](#file-structure)
- [Contributing](#contributing)
- [License](#license)
- [Disclaimer](#disclaimer)

---


## 📌 Overview

**Net Spoofer** is a lightweight Python script that automatically changes your **MAC address** and **local IP address** at regular intervals. By rotating these identifiers, it makes you harder to track on a local network (Wi‑Fi or Ethernet). The script works on Linux systems, disables DHCP to prevent automatic IP renewal, and restores original settings when you stop it.

This is a standalone tool for **privacy testing** on networks you own or have explicit permission to use.

---

## ✨ Features

- ✅ **Real MAC address randomisation** – changes your hardware identifier on the LAN.
- ✅ **Real local IP randomisation** – assigns a random private IP from the ranges: `10.0.0.0/8`, `172.16.0.0/12`, or `192.168.0.0/16`.
- ✅ **Automatic DHCP suppression** – kills `dhclient`, `dhcpcd`, and (if present) disables NetworkManager for the interface to prevent IP renewal.
- ✅ **Graceful restoration** – on exit (Ctrl+C), restores original MAC and original IP, then re‑enables NetworkManager.
- ✅ **Comprehensive logging** – logs all actions to `/var/log/spoofer.log` and the terminal.
- ✅ **Fully automated** – runs in a loop with a configurable interval.

---

## ⚙️ How It Works

1. **Initialisation** – saves the original MAC and IP of the specified interface.
2. **DHCP disable** – kills all DHCP clients and marks the interface as unmanaged (if using NetworkManager).
3. **Random generation** – creates a locally‑administered MAC (second bit of first byte set to `1`) and a random IP from one of the private ranges.
4. **Apply changes** – flushes old IP, assigns new IP, updates MAC.
5. **Wait** – sleeps for the configured interval.
6. **Loop** – repeats steps 3–5.
7. **On interrupt (Ctrl+C)** – restores original MAC and IP, re‑enables NetworkManager, and exits cleanly.

---

## 📦 Requirements

- **Operating System**: Linux (Debian‑based, e.g., Kali, Ubuntu, or any with `ip` and `iproute2`).
- **Root privileges** – the script must run with `sudo`.
- **Python 3.6+** – with standard library modules (`subprocess`, `random`, `time`, `argparse`, `signal`, `re`, `os`, `logging`).
- **NetworkManager** – optional (the script will attempt to disable it; if not present, it will still work).

---

## 🔧 Installation

### 1. Download the Script

Save the script as `net_spoofer.py` in your preferred directory, e.g., `~/tools/net_spoofer/`.

Make it executable:
```bash
chmod +x net_spoofer.py
```

### 2. (Optional) Install `iproute2` if not already present
Most Linux distributions already include `ip`; if not:
```bash
sudo apt install iproute2 -y
```

---

## 🚀 Usage

Run the script with root privileges:

```bash
sudo ./net_spoofer.py -i wlan0 --interval 10
```

**Arguments:**

| Option | Description | Default |
|--------|-------------|---------|
| `-i, --interface` | Network interface (e.g., `wlan0`, `eth0`) | **Required** |
| `--interval` | Time in seconds between each rotation | `2` |

**Example:**
```bash
sudo ./net_spoofer.py -i eth0 --interval 15
```

While running, you can monitor changes in another terminal:
```bash
watch -n 1 ip a show wlan0
```

To stop the script, press `Ctrl+C` – it will automatically restore your original MAC and IP.

---

## 🔄 Workflow

```
Start Script
    │
    ▼
Save original MAC & IP
    │
    ▼
Disable DHCP (kill dhclient, dhcpcd, mark unmanaged)
    │
    ▼
Loop forever:
    │
    ├─► Generate random MAC
    ├─► Generate random IP from private ranges
    ├─► Apply MAC and IP changes
    ├─► Log changes
    ├─► Wait for interval
    └─► Repeat
    │
    ▼
Ctrl+C → Restore original MAC/IP, re‑enable NetworkManager
    │
    ▼
Exit
```

---

## 🧪 Troubleshooting

### Wi‑Fi disappears after running the script
If the script crashes or you kill it abruptly, NetworkManager may still think the interface is unmanaged. Fix it with:
```bash
sudo rm -f /etc/NetworkManager/conf.d/99-unmanaged-*.conf
sudo service NetworkManager restart
sudo nmcli device set wlan0 managed yes
sudo nmcli radio wifi on
sudo ip link set wlan0 up
```
*(Replace `wlan0` with your interface.)*

### `systemctl: command not found`
If your system doesn’t have `systemctl`, use `service` instead:
```bash
sudo service NetworkManager restart
```
Or fix your PATH:
```bash
export PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
```

### Internet stops working after IP change
The script assigns a random IP from private ranges, which may not be in the same subnet as your gateway. This can break routing. To keep internet working, modify the script to generate an IP within your current subnet (this is not included in the base version). You can also manually reconnect to your network after stopping the script.

---

## 🛡️ Security Considerations

- This tool **only changes local identifiers** (MAC and local IP). It does **not** hide your traffic from your ISP or change your public IP.
- It is useful for evading local network tracking or bypassing MAC filtering, but it is **not** a full anonymity solution.
- For complete privacy, combine this with a **VPN** and **Tor**.
- **Always test on networks you own or have permission to test.** Unauthorised spoofing may be illegal.

---

## 📁 File Structure

```
net_spoofer.py             # Main script
/var/log/spoofer.log       # Log file (created automatically)
```

---

## 🤝 Contributing

Contributions are welcome! If you find a bug or want to add features:
- Fork the repository
- Create a new branch
- Make your changes
- Submit a pull request with a clear description

---

## 📄 License

This project is licensed under the **MIT License** – see the [LICENSE](LICENSE) file for details.

---

## ⚠️ Disclaimer

**This tool is intended for educational and authorised testing purposes only.**  
Unauthorised use on networks without explicit permission is illegal and unethical. The authors assume no liability for any misuse or damage caused by this software. Use at your own risk.

---

**Stay safe, stay private!** 🔒
