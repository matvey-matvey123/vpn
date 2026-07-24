import requests
import base64
import re
import time
import socket
import ipaddress

SUBSCRIPTIONS = [
    "https://raw.githubusercontent.com/Hidashimora/free-vpn-anti-rkn/main/configs/1.txt",
    "https://raw.githubusercontent.com/Hidashimora/free-vpn-anti-rkn/main/configs/5.txt",
    "https://raw.githubusercontent.com/Hidashimora/free-vpn-anti-rkn/main/configs/10.1.txt",
    "https://raw.githubusercontent.com/Hidashimora/free-vpn-anti-rkn/main/configs/15.txt",
    "https://raw.githubusercontent.com/Hidashimora/free-vpn-anti-rkn/main/configs/20.txt",
    "https://raw.githubusercontent.com/Hidashimora/free-vpn-anti-rkn/main/configs/25.txt",
    "https://raw.githubusercontent.com/Hidashimora/free-vpn-anti-rkn/main/configs/30.txt",
    "https://raw.githubusercontent.com/Hidashimora/free-vpn-anti-rkn/main/configs/34.txt",
    "https://raw.githubusercontent.com/Hidashimora/free-vpn-anti-rkn/main/configs/1.13.txt",
    "https://raw.githubusercontent.com/Hidashimora/free-vpn-anti-rkn/main/configs/2.1.txt",
    "https://raw.githubusercontent.com/Hidashimora/free-vpn-anti-rkn/main/configs/5.1.txt",
    "https://raw.githubusercontent.com/Hidashimora/free-vpn-anti-rkn/main/configs/8.txt",
    "https://raw.githubusercontent.com/Hidashimora/free-vpn-anti-rkn/main/configs/11.txt",
    "https://raw.githubusercontent.com/Hidashimora/free-vpn-anti-rkn/main/configs/16.1.txt",
    "https://raw.githubusercontent.com/Hidashimora/free-vpn-anti-rkn/main/configs/20.1.txt",
    "https://raw.githubusercontent.com/Hidashimora/free-vpn-anti-rkn/main/configs/24.txt",
    "https://raw.githubusercontent.com/Hidashimora/free-vpn-anti-rkn/main/configs/28.txt",
    "https://raw.githubusercontent.com/Hidashimora/free-vpn-anti-rkn/main/configs/33.txt",
    "https://raw.githubusercontent.com/mahdibland/ShadowsocksAggregator/master/sub/sub_merge.txt",
    "https://raw.githubusercontent.com/Au1rxx/free-vpn-subscriptions/main/output/v2ray-base64.txt",
]

OUTPUT_FILE = "working.txt"
MAX_PER_COUNTRY = 5
MAX_OTHER = 10
TIMEOUT = 2

COUNTRY_RANGES = {
    "🇩🇪 Германия": ["5.9.0.0/16", "46.4.0.0/14", "78.46.0.0/15", "88.198.0.0/15", "116.202.0.0/15", "136.243.0.0/16", "144.76.0.0/16", "148.251.0.0/16", "159.69.0.0/16", "167.233.0.0/16", "168.119.0.0/16", "176.9.0.0/16", "188.40.0.0/16"],
    "🇺🇸 США": ["3.0.0.0/9", "15.0.0.0/8", "23.0.0.0/8", "34.0.0.0/8", "35.0.0.0/8", "44.0.0.0/8", "47.0.0.0/8", "52.0.0.0/8", "54.0.0.0/8", "64.0.0.0/8", "66.0.0.0/8", "104.0.0.0/8", "107.0.0.0/8", "142.0.0.0/8", "155.0.0.0/8", "162.0.0.0/8", "172.0.0.0/8", "199.0.0.0/8"],
    "🇷🇺 Россия": ["5.3.0.0/16", "5.8.0.0/13", "31.13.0.0/16", "37.1.0.0/16", "37.9.0.0/16", "46.0.0.0/16", "62.16.0.0/14", "77.34.0.0/15", "78.24.0.0/15", "79.104.0.0/15", "82.112.0.0/12", "85.192.0.0/10", "87.224.0.0/11", "91.122.0.0/15", "94.19.0.0/16", "95.24.0.0/13", "176.48.0.0/12", "178.34.0.0/16", "185.3.0.0/16", "188.16.0.0/12"],
    "🇳🇱 Нидерланды": ["5.79.64.0/18", "31.7.0.0/16", "37.34.0.0/16", "37.97.0.0/16", "45.64.0.0/14", "46.144.0.0/14", "62.45.0.0/16", "77.60.0.0/14", "80.56.0.0/13", "82.92.0.0/14", "82.168.0.0/14", "83.80.0.0/13", "84.80.0.0/14", "87.208.0.0/13", "88.159.0.0/16", "136.144.0.0/16", "141.101.0.0/16", "188.204.0.0/16"],
}

def fetch_links(url):
    try:
        r = requests.get(url, timeout=120)
        if r.status_code != 200:
            return []
        try:
            text = base64.b64decode(r.text).decode('utf-8', errors='ignore')
        except:
            text = r.text
        return [l.strip() for l in text.split('\n') if l.strip() and not l.startswith('#') and '://' in l]
    except:
        return []

def extract_host_port(link):
    m = re.search(r'@([^:?\s]+):(\d+)', link)
    return (m.group(1), int(m.group(2))) if m else (None, None)

def detect_country(ip_str):
    try:
        ip = ipaddress.ip_address(ip_str)
        for c, r in COUNTRY_RANGES.items():
            for cidr in r:
                if ip in ipaddress.ip_network(cidr):
                    return c
    except:
        pass
    return None

def check_tcp(host, port):
    try:
        ip = socket.gethostbyname(host)
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(TIMEOUT)
        t = time.time()
        s.connect((ip, port))
        p = round((time.time() - t) * 1000)
        s.close()
        return True, p, ip
    except:
        return False, 9999, None

def check_sub(url, mx=200):
    links = list(dict.fromkeys(fetch_links(url)))[:mx]
    bc = {c: [] for c in COUNTRY_RANGES}
    ot = []
    for l in links:
        h, p = extract_host_port(l)
        if not h:
            continue
        ok, ping, ip = check_tcp(h, p)
        if not ok:
            continue
        c = detect_country(ip)
        if c:
            bc[c].append((ping, l))
        else:
            ot.append((ping, l))
    for c in COUNTRY_RANGES:
        bc[c].sort()
    ot.sort()
    return bc, ot

def main():
    all_bc = {c: [] for c in COUNTRY_RANGES}
    all_ot = []
    for sub in SUBSCRIPTIONS:
        bc, ot = check_sub(sub, 200)
        for c in COUNTRY_RANGES:
            all_bc[c].extend(bc[c])
        all_ot.extend(ot)
    for c in COUNTRY_RANGES:
        all_bc[c].sort()
    bo = sorted(all_ot)[:MAX_OTHER]
    lines = []
    for c in ["🇩🇪 Германия", "🇺🇸 США", "🇷🇺 Россия", "🇳🇱 Нидерланды"]:
        for _, l in all_bc[c][:MAX_PER_COUNTRY]:
            lines.append(l)
    for _, l in bo:
        lines.append(l)
    content = '\n'.join(lines)
    with open(OUTPUT_FILE, 'w') as f:
        f.write(content)

if __name__ == '__main__':
    main()
