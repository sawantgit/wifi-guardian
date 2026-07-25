# pyrefly: ignore [missing-import]
from scapy.all import ARP, Ether, srp
import socket
import subprocess
import re
import time
import threading

# Caching structures
_cache_lock = threading.Lock()
_cached_devices = None
_last_scan_time = 0.0
CACHE_TIMEOUT = 15.0  # seconds

def get_last_scan_time():
    """Returns the timestamp of the last successful scan."""
    return _last_scan_time

def get_local_ip():
    """Retrieves the local active IP address by opening a dummy connection."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except Exception:
        return None

def get_local_ip_range():
    """Automatically detects your local network IP subnet range."""
    local_ip = get_local_ip()
    if local_ip:
        # Convert an IP like '192.168.1.45' into a broad subnet range '192.168.1.0/24'
        ip_parts = local_ip.split('.')
        ip_parts[3] = '0/24'
        return '.'.join(ip_parts)
    return "192.168.1.0/24"

def scan_network_fallback(target_ip_range):
    """Fallback scanner for Windows when WinPcap/Npcap is missing or not administrator."""
    # Extract subnet prefix (e.g. '10.79.33.0/24' -> '10.79.33.')
    subnet_prefix = target_ip_range.split('/')[0]
    if subnet_prefix.endswith('.0'):
        subnet_prefix = subnet_prefix[:-1]
    else:
        ip_parts = target_ip_range.split('.')
        if len(ip_parts) >= 3:
            subnet_prefix = '.'.join(ip_parts[:3]) + '.'
        else:
            subnet_prefix = '192.168.1.'
            
    local_ip = get_local_ip()
    
    # Sweep IPs in a single-threaded loop (highly efficient for UDP on local stack)
    ips = [f"{subnet_prefix}{i}" for i in range(1, 255) if f"{subnet_prefix}{i}" != local_ip]
    
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        for ip in ips:
            try:
                # Discard port (9) is standard for dummy packets
                sock.sendto(b"", (ip, 9))
            except Exception:
                pass
        sock.close()
    except Exception:
        pass
        
    # Give a short duration for the OS to receive the ARP replies and update cache
    time.sleep(0.3)
    
    devices = []
    try:
        # Run arp -a to read the system ARP cache
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        output = subprocess.check_output(
            ["arp", "-a"], 
            startupinfo=startupinfo
        ).decode("utf-8", errors="ignore")
        
        # Match IPs under the local subnet and parse their MAC addresses
        pattern = re.compile(
            r"^\s*(" + re.escape(subnet_prefix) + r"\d+)\s+([0-9a-fA-F\-]{17})\s+(\w+)", 
            re.MULTILINE
        )
        
        for match in pattern.finditer(output):
            ip, mac, entry_type = match.groups()
            mac_normalized = mac.replace('-', ':').lower()
            # Avoid showing broadcast / multicast entries
            if mac_normalized != "ff:ff:ff:ff:ff:ff" and not mac_normalized.startswith("01:00:5e"):
                devices.append({
                    "ip": ip,
                    "mac": mac_normalized
                })
    except Exception as e:
        print(f"Fallback ARP cache parsing failed: {e}")
        
    return devices

def scan_network(force_refresh=False):
    """Scans the local network and returns a list of active devices, with caching support."""
    global _cached_devices, _last_scan_time
    
    current_time = time.time()
    with _cache_lock:
        if not force_refresh and _cached_devices is not None and (current_time - _last_scan_time) < CACHE_TIMEOUT:
            return _cached_devices

    target_ip_range = get_local_ip_range()
    
    try:
        # Craft an ARP Request Packet targeted at the whole subnet range
        arp = ARP(pdst=target_ip_range)
        ether = Ether(dst="ff:ff:ff:ff:ff:ff") # Broadcast address configuration
        packet = ether / arp

        # Send packets onto the airwaves and wait max 3 seconds for answers
        answered_list = srp(packet, timeout=3, verbose=False)[0]
        
        devices = []
        for element in answered_list:
            device_info = {
                "ip": element[1].psrc,
                "mac": element[1].hwsrc.lower()
            }
            devices.append(device_info)
    except Exception as e:
        # If scapy fails (e.g. no WinPcap/Npcap), run fallback ARP-cache scan
        devices = scan_network_fallback(target_ip_range)

    with _cache_lock:
        _cached_devices = devices
        _last_scan_time = time.time()

    return devices


