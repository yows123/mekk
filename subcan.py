import requests
import shutil
import os

BLACKLIST_PREFIX = [
    'cpanel.', 'mail.', 'webmail.', 'www.', 'webdisk.',
    'autodiscover.', 'whm.', 'cpcontacts.', 'cpcalendars.'
]

ASCII_BANNER = r"""
░██████╗██╗░░░██╗██████╗░██████╗░░█████╗░░██████╗░█████╗░░█████╗░███╗░░██╗
██╔════╝██║░░░██║██╔══██╗██╔══██╗██╔══██╗██╔════╝██╔══██╗██╔══██╗████╗░██║
╚█████╗░██║░░░██║██████╦╝██║░░██║██║░░██║╚█████╗░██║░░╚═╝███████║██╔██╗██║
░╚═══██╗██║░░░██║██╔══██╗██║░░██║██║░░██║░╚═══██╗██║░░██╗██╔══██║██║╚████║
██████╔╝╚██████╔╝██████╦╝██████╔╝╚█████╔╝██████╔╝╚█████╔╝██║░░██║██║░╚███║
╚═════╝░░╚═════╝░╚═════╝░╚═════╝░░╚════╝░╚═════╝░░╚════╝░╚═╝░░╚═╝╚═╝░░╚══╝
"""

def print_centered_banner():
    terminal_width = shutil.get_terminal_size().columns
    os.system('cls' if os.name == 'nt' else 'clear')
    for line in ASCII_BANNER.strip().split('\n'):
        print(line.center(terminal_width))
    print("\n")

def is_blacklisted(hostname):
    return any(hostname.startswith(prefix) for prefix in BLACKLIST_PREFIX)

def get_unique_hostnames(domain):
    url = f"https://otx.alienvault.com/api/v1/indicators/domain/{domain}/passive_dns"
    hostnames = set()

    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        for record in data.get("passive_dns", []):
            hostname = record.get("hostname")
            if hostname:
                hostname = hostname.lower()
                if not is_blacklisted(hostname):
                    hostnames.add(hostname)

    except requests.RequestException as e:
        print(f"[!] Gagal fetch {domain} -> {e}")

    return hostnames

def main():
    print_centered_banner()
    input_file = input("[+] Input list file (e.g. domains.txt): ").strip()
    output_file = input("[+] Output file (e.g. hasil.txt): ").strip()

    all_hostnames = set()

    try:
        with open(input_file, 'r') as f:
            domains = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print(f"[-] File tidak ditemukan: {input_file}")
        return

    print(f"\n[+] Total domain yang akan diproses: {len(domains)}\n")

    for i, domain in enumerate(domains, 1):
        print(f"[{i:02d}/{len(domains)}] Fetching: {domain}")
        hostnames = get_unique_hostnames(domain)
        all_hostnames.update(hostnames)

    try:
        with open(output_file, 'w') as out:
            for hostname in sorted(all_hostnames):
                out.write(hostname + "\n")
        print(f"\n[+] Selesai! {len(all_hostnames)} subdomain unik disimpan di: {output_file}")
    except Exception as e:
        print(f"[-] Gagal menulis file output: {e}")

if __name__ == "__main__":
    main()
