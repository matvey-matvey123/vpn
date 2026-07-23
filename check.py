import requests
import base64
import re
import time
import socket
import ipaddress

SUBSCRIPTIONS = [
    "https://raw.githubusercontent.com/Hidashimora/free-vpn-anti-rkn/main/configs/1.1.txt",
    "https://raw.githubusercontent.com/mahdibland/ShadowsocksAggregator/master/sub/sub_merge.txt",
]

MAX_PER_COUNTRY = 5
MAX_OTHER = 10
TIMEOUT = 2

OUTPUT_FILES = [
    "working.txt",
    "1019410.txt",
    "1033910.txt",
    "1026810.txt",
    "1080810.txt",
    "1063010.txt",
    "1042310.txt",
    "1061910.txt",
    "1077610.txt",
    "1054310.txt",
    "1016910.txt",
]

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
        links = []
        for line in text.split('\n'):
            line = line.strip()
            if line and not line.startswith('#') and ('://' in line):
                links.append(line)
        return links
    except:
        return []

def extract_host_port(link):
    match = re.search(r'@([^:?\s]+):(\d+)', link)
    if match:
        return match.group(1), int(match.group(2))
    return None, None

def detect_country_by_ip(ip_str):
    try:
        ip = ipaddress.ip_address(ip_str)
        for country, ranges in COUNTRY_RANGES.items():
            for cidr in ranges:
                if ip in ipaddress.ip_network(cidr):
                    return country
    except:
        pass
    return None

def check_tcp(host, port):
    try:
        ip = socket.gethostbyname(host)
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(TIMEOUT)
        start = time.time()
        s.connect((ip, port))
        ping = round((time.time() - start) * 1000)
        s.close()
        return True, ping, ip
    except:
        return False, 9999, None

def check_subscription(sub_url, max_check=500):
    links = fetch_links(sub_url)
    unique_links = list(dict.fromkeys(links))[:max_check]
    
    by_country = {c: [] for c in COUNTRY_RANGES}
    other = []
    
    for link in unique_links:
        host, port = extract_host_port(link)
        if not host or not port:
            continue
        ok, ping, ip = check_tcp(host, port)
        if not ok or not ip:
            continue
        country = detect_country_by_ip(ip)
        if country:
            by_country[country].append((ping, link))
        else:
            other.append((ping, link))
    
    for c in COUNTRY_RANGES:
        by_country[c].sort(key=lambda x: x[0])
    other.sort(key=lambda x: x[0])
    
    return by_country, other

def main():
    by_country_hida, other_hida = check_subscription(SUBSCRIPTIONS[0], max_check=300)
    by_country_mahdi, other_mahdi = check_subscription(SUBSCRIPTIONS[1], max_check=200)
    
    all_by_country = {c: [] for c in COUNTRY_RANGES}
    for c in COUNTRY_RANGES:
        all_by_country[c] = by_country_hida[c] + by_country_mahdi[c]
        all_by_country[c].sort(key=lambda x: x[0])
    
    all_other = other_hida + other_mahdi
    all_other.sort(key=lambda x: x[0])
    best_other = all_other[:MAX_OTHER]
    
    lines = []
    for country in ["🇩🇪 Германия", "🇺🇸 США", "🇷🇺 Россия", "🇳🇱 Нидерланды"]:
        servers = all_by_country[country][:MAX_PER_COUNTRY]
        for ping, link in servers:
            lines.append(link)
    for ping, link in best_other:
        lines.append(link)
    
    content = '\n'.join(lines)
    
    for fname in OUTPUT_FILES:
        with open(fname, 'w', encoding='utf-8') as f:
            f.write(content)

if __name__ == '__main__':
    main()
