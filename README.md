# Phantom

**Phantom** is an advanced ARP spoofing tool designed for educational and ethical penetration testing purposes. It enables **Man-In-The-Middle (MITM)** attacks on local area networks by manipulating ARP tables.

> ⚠️ **Legal Disclaimer**  
> Usage of Phantom for attacking targets without prior mutual consent is **illegal**. It is the end user's responsibility to comply with all applicable local, state, and federal laws. The developer assumes no liability and is **not responsible** for any misuse or damage caused by this program.

---

##  Features

- **Cross-Environment Support**: Runs in Jupyter Notebook (interactive) and Linux terminal (command-line).
- **IP Forwarding Management**: Automatically enables/disables IP forwarding on Linux for seamless MITM.
- **Configurable Packet Rate**: Adjust the frequency of ARP packets for stealth or performance.
- **Robust Logging**: Logs all actions to timestamped files for auditing and debugging.
- **Progress Visualization**: Displays a progress bar (via `tqdm`) for real-time packet-sending feedback.
- **Color-Coded Output**: Uses `colorama` for visually appealing console output.
- **Error Handling**: Validates IPs, handles network errors, and restores ARP tables on exit.
- **Network Interface Selection**: Supports multiple interfaces (e.g., `eth0`, `wlan0`).

---

##  Supported Platforms

| Platform | Support Level | Notes |
|----------|----------------|-------|
| **Linux** | ✅ Full | Requires root privileges |
| **macOS** | ✅ Partial | Requires modification for IP forwarding |
| **Windows** | ⚠️ Limited | ARP spoofing may be unreliable |

---

##  Prerequisites

- Python 3.x
- Install required libraries:
  ```bash
  pip install scapy colorama tqdm
- **Linux:** Root privileges (sudo) for packet manipulation and IP forwarding.
- **macOS:** Root privileges and modified IP forwarding commands.
- **Windows:** Npcap (npcap.com) and administrative privileges; less reliable for ARP spoofing.

## Installation

1. Clone the repository
```bash
git clone https://github.com/BadBoy0170/PhantomARP.git
cd PhantomARP
```
2. Install dependencies:
```bash
pip install -r requirements.txt
```
3. (Windows only) Install Npcap from npcap.com.

## Usage

**Linux Terminal**
Run the script with command-line arguments:
```bash
sudo python3 phantom_arp.py -t <target_ip> -g <gateway_ip> -i <interface> -r <packet_rate>
```

Example:
```bash
sudo python3 phantom_arp.py -t 192.168.1.100 -g 192.168.1.1 -i eth0 -r 2.0
```

## Output

- The script displays a colorful banner and legal disclaimer.
- It enables IP forwarding (Linux) and sends spoofed ARP packets.
- A progress bar shows the number of packets sent.
- Logs are saved to phantom_arp_<timestamp>.log.
- On exit (Ctrl+C), ARP tables are restored, and IP forwarding is disabled.

## Modifications for macOS and Windows

**macOS**
- Update the IP forwarding functions in phantom_arp.py:
```bash
def enable_ip_forwarding():
    if platform.system() == "Darwin":
        subprocess.run(["sysctl", "-w", "net.inet.ip.forwarding=1"], check=True)
        # ... (other platform logic)
```

- Run with the correct interface (e.g., en0):
```bash
sudo python3 phantom_arp.py -t 192.168.1.100 -g 192.168.1.1 -i en0 -r 2.0
```

**Windows**
- Install Npcap and update IP forwarding:
```bash
def enable_ip_forwarding():
    if platform.system() == "Windows":
        subprocess.run(["netsh", "interface", "ipv4", "set", "interface", "forwarding=enabled"], check=True)
        # ... (other platform logic)
```

- List interfaces using scapy:

```bash
from scapy.arch.windows import get_windows_if_list
```
Note: ARP spoofing on Windows is less reliable due to networking stack limitations.

Example Log Output
```bash
2025-06-26 22:11:00,123 - INFO - Script started - Legal disclaimer displayed
2025-06-26 22:11:02,456 - INFO - IP forwarding enabled
2025-06-26 22:11:03,789 - INFO - Sent spoof packet to 192.168.1.100 pretending to be 192.168.1.1
2025-06-26 22:11:05,012 - INFO - Session completed. Total packets sent: 10
```
License

This project is licensed under the MIT License - see the LICENSE file for details.

Warning: Use PhantomARP responsibly and only in environments where you have explicit permission. Unauthorized use is illegal and unethical.










