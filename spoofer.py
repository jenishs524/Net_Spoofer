#!/usr/bin/env python3
"""
Ultimate Network Spoofer v4.0
Guaranteed MAC & IP change.
"""

import subprocess, random, time, argparse, sys, signal, re, os, logging
from typing import Optional, Tuple

PRIVATE_RANGES = [("10.0.0.0", 8), ("172.16.0.0", 12), ("192.168.0.0", 16)]
LOG_FILE = "/var/log/spoofer.log"

original_mac = original_ip = interface = None
running = True
nm_managed = False  # store if we disabled NetworkManager

logging.basicConfig(level=logging.INFO,
                    format="[%(asctime)s] %(levelname)s: %(message)s",
                    handlers=[logging.FileHandler(LOG_FILE), logging.StreamHandler()])
logger = logging.getLogger("Spoofer")

def run_cmd(cmd, check=False):
    try:
        return subprocess.run(cmd, capture_output=True, text=True, check=check)
    except subprocess.CalledProcessError as e:
        logger.error(f"Command failed: {' '.join(cmd)} -> {e.stderr.strip()}")
        return e

def get_interface_info(iface):
    out = run_cmd(["ip", "a", "show", iface]).stdout
    mac = re.search(r"link/ether ([0-9a-f:]{17})", out)
    ip = re.search(r"inet (\d+\.\d+\.\d+\.\d+/\d+)", out)
    return (mac.group(1) if mac else None, ip.group(1) if ip else None)

def random_mac():
    mac = [0x02, random.randint(0,255), random.randint(0,255),
           random.randint(0,255), random.randint(0,255), random.randint(0,255)]
    mac[0] |= 0x02
    return ":".join(f"{b:02x}" for b in mac)

def random_ip():
    base, prefix = random.choice(PRIVATE_RANGES)
    parts = list(map(int, base.split('.')))
    host_bits = 32 - prefix
    max_hosts = (1 << host_bits) - 2
    if max_hosts < 1: prefix, host_bits = 24, 8; max_hosts = 254
    host = random.randint(1, max_hosts)
    ip_parts = parts.copy()
    for i in range(3, -1, -1):
        if host_bits > 0:
            bits = min(8, host_bits)
            ip_parts[i] = (ip_parts[i] & ~((1<<bits)-1)) | (host & ((1<<bits)-1))
            host >>= bits; host_bits -= bits
    return ".".join(str(p) for p in ip_parts), prefix

def change_mac(iface, new_mac):
    try:
        run_cmd(["ip", "link", "set", iface, "down"])
        run_cmd(["ip", "link", "set", iface, "address", new_mac])
        run_cmd(["ip", "link", "set", iface, "up"])
        return True
    except: return False

def change_ip(iface, new_ip, prefix):
    try:
        run_cmd(["ip", "link", "set", iface, "down"])
        run_cmd(["ip", "addr", "flush", "dev", iface])
        run_cmd(["ip", "addr", "add", f"{new_ip}/{prefix}", "dev", iface])
        run_cmd(["ip", "link", "set", iface, "up"])
        return True
    except: return False

def disable_dhcp_permanently(iface):
    global nm_managed
    # 1. Kill all known DHCP clients
    for client in ["dhclient", "dhcpcd", "pump", "udhcpc"]:
        run_cmd(["pkill", "-f", f"{client}.*{iface}"])
    # 2. Disable NetworkManager for this interface (set to unmanaged)
    try:
        # Check if NetworkManager is running
        if run_cmd(["systemctl", "is-active", "NetworkManager"]).returncode == 0:
            # Create a config file to mark the interface as unmanaged
            conf = f"/etc/NetworkManager/conf.d/99-unmanaged-{iface}.conf"
            with open(conf, "w") as f:
                f.write(f"[keyfile]\nunmanaged-devices=interface-name:{iface}\n")
            run_cmd(["systemctl", "restart", "NetworkManager"])
            nm_managed = True
            logger.info(f"NetworkManager disabled for {iface}")
    except Exception as e:
        logger.warning(f"Could not disable NetworkManager: {e}")

def restore_networkmanager(iface):
    if nm_managed:
        try:
            conf = f"/etc/NetworkManager/conf.d/99-unmanaged-{iface}.conf"
            if os.path.exists(conf):
                os.remove(conf)
                run_cmd(["systemctl", "restart", "NetworkManager"])
                logger.info("NetworkManager re-enabled")
        except Exception as e:
            logger.warning(f"Failed to restore NetworkManager: {e}")

def restore_original(iface, mac, ip):
    logger.info("Restoring original settings...")
    if mac: change_mac(iface, mac)
    if ip:
        run_cmd(["ip", "link", "set", iface, "down"])
        run_cmd(["ip", "addr", "flush", "dev", iface])
        run_cmd(["ip", "addr", "add", ip, "dev", iface])
        run_cmd(["ip", "link", "set", iface, "up"])
        logger.info(f"Restored IP to {ip}")
    restore_networkmanager(iface)

def signal_handler(sig, frame):
    global running
    logger.info("Interrupt received. Restoring...")
    running = False
    restore_original(interface, original_mac, original_ip)
    sys.exit(0)

def main():
    global interface, original_mac, original_ip
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--interface", required=True)
    parser.add_argument("--interval", type=float, default=2.0)
    args = parser.parse_args()
    if os.geteuid() != 0:
        logger.error("Must be root")
        sys.exit(1)
    interface = args.interface
    original_mac, original_ip = get_interface_info(interface)
    if not original_mac:
        logger.error(f"Interface {interface} not found")
        sys.exit(1)
    logger.info(f"Original MAC: {original_mac}")
    logger.info(f"Original IP : {original_ip}")
    disable_dhcp_permanently(interface)
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    round_num = 0
    while running:
        new_mac = random_mac()
        new_ip, prefix = random_ip()
        ip_str = f"{new_ip}/{prefix}"
        logger.info(f"Round {round_num+1}: new MAC={new_mac}, new IP={ip_str}")
        if change_mac(interface, new_mac): logger.info("MAC changed")
        else: logger.error("MAC failed")
        if change_ip(interface, new_ip, prefix): logger.info("IP changed")
        else: logger.error("IP failed")
        round_num += 1
        time.sleep(args.interval)
    restore_original(interface, original_mac, original_ip)

if __name__ == "__main__":
    main()