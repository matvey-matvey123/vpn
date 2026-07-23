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

OUTPUT_FILE = "working.txt"
MAX_PER_COUNTRY_HIDA = 5
MAX_OTHER = 10
TIMEOUT = 3

COUNTRY_RANGES = {
    "🇩🇪 Германия": [
        "2.56.0.0/13", "5.9.0.0/16", "31.13.64.0/18", "37.120.0.0/14",
        "45.8.0.0/14", "46.4.0.0/14", "49.12.0.0/16", "78.46.0.0/15",
        "88.198.0.0/15", "116.202.0.0/15", "136.243.0.0/16", "138.201.0.0/16",
        "144.76.0.0/16", "148.251.0.0/16", "159.69.0.0/16", "167.233.0.0/16",
        "168.119.0.0/16", "176.9.0.0/16", "178.63.0.0/16", "188.40.0.0/16",
    ],
    "🇺🇸 США": [
        "3.0.0.0/9", "15.0.0.0/8", "23.0.0.0/8", "34.0.0.0/8",
        "35.0.0.0/8", "44.0.0.0/8", "47.0.0.0/8", "50.0.0.0/8",
        "52.0.0.0/8", "54.0.0.0/8", "64.0.0.0/8", "66.0.0.0/8",
        "104.0.0.0/8", "107.0.0.0/8", "142.0.0.0/8", "155.0.0.0/8",
        "162.0.0.0/8", "172.0.0.0/8", "173.0.0.0/8", "199.0.0.0/8",
    ],
    "🇷🇺 Россия": [
        "5.3.0.0/16", "5.8.0.0/13", "5.16.0.0/14", "31.13.0.0/16",
        "37.1.0.0/16", "37.9.0.0/16", "46.0.0.0/16", "46.8.0.0/13",
        "62.16.0.0/14", "77.34.0.0/15", "78.24.0.0/15", "79.104.0.0/15",
        "80.64.0.0/13", "82.112.0.0/12", "85.192.0.0/10", "87.224.0.0/11",
        "89.16.0.0/13", "91.122.0.0/15", "92.36.0.0/14", "94.19.0.0/16",
        "95.24.0.0/13", "109.60.0.0/14", "128.68.0.0/16", "176.48.0.0/12",
        "178.34.0.0/16", "185.3.0.0/16", "188.16.0.0/12",
    ],
    "🇳🇱 Нидерланды": [
        "5.2.64.0/19", "5.10.0.0/15", "5.34.192.0/18", "5.79.64.0/18",
        "31.3.64.0/18", "31.7.0.0/16", "31.21.0.0/16", "31.148.0.0/15",
        "37.34.0.0/16", "37.97.0.0/16", "37.139.0.0/16", "37.148.0.0/14",
        "45.64.0.0/14", "46.44.0.0/14", "46.144.0.0/14", "62.45.0.0/16",
        "62.212.128.0/18", "77.60.0.0/14", "77.248.0.0/16", "80.56.0.0/13",
        "81.204.0.0/14", "82.92.0.0/14", "82.168.0.0/14", "83.80.0.0/13",
        "84.24.0.0/15", "84.80.0.0/14", "85.144.0.0/14", "86.80.0.0/13",
        "87.208.0.0/13", "88.159.0.0/16", "89.20.0.0/16", "91.148.0.0/16",
        "136.144.0.0/16", "141.101.0.0/16", "141.138.0.0/15",
        "145.0.0.0/15", "145.49.0.0/16", "145.100.0.0/15",
        "146.50.0.0/16", "188.204.0.0/16", "212.127.0.0/16",
    ],
}

def fetch_links(url):
    try:
        r = requests.get(url, timeout=60)
        if r.status_code != 200:
            return []
        try:
            text = base64.b64decode(r.text).decode('utf-8')
        except:
            text = r.text
        links = []
        for line in text.split('\n'):
            line = line.strip()
            if line and not line.startswith('#'):
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

def main():
    # Источник 1: Hidashimora (по странам)
    links_hida = fetch_links(SUBSCRIPTIONS[0])
    unique_hida = list(dict.fromkeys(links_hida))
    
    # Источник 2: Mahdibland (любые 10)
    links_mahdi = fetch_links(SUBSCRIPTIONS[1])
    unique_mahdi = list(dict.fromkeys(links_mahdi))
    
    print(f"Hidashimora: {len(unique_hida)} ссылок")
    print(f"Mahdibland: {len(unique_mahdi)} ссылок")
    
    by_country = {c: [] for c in COUNTRY_RANGES}
    other_servers = []
    
    # Проверяем Hidashimora
    for link in unique_hida:
        host, port = extract_host_port(link)
        if not host or not port:
            continue
        ok, ping, ip = check_tcp(host, port)
        if not ok or not ip:
            continue
        country = detect_country_by_ip(ip)
        if country:
            by_country[country].append((ping, link))
    
    # Проверяем Mahdibland (берём любые рабочие)
    for link in unique_mahdi:
        host, port = extract_host_port(link)
        if not host or not port:
            continue
        ok, ping, ip = check_tcp(host, port)
        if ok:
            other_servers.append((ping, link))
    
    other_servers.sort(key=lambda x: x[0])
    best_other = other_servers[:MAX_OTHER]
    
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(f"# 🤖 Авто-проверка | {time.ctime()}\n\n")
        
        f.write(f"# ========== 🇩🇪 Германия ==========\n")
        by_country["🇩🇪 Германия"].sort(key=lambda x: x[0])
        for ping, link in by_country["🇩🇪 Германия"][:MAX_PER_COUNTRY_HIDA]:
            f.write(f"{link}\n")
        f.write("\n")
        
        f.write(f"# ========== 🇺🇸 США ==========\n")
        by_country["🇺🇸 США"].sort(key=lambda x: x[0])
        for ping, link in by_country["🇺🇸 США"][:MAX_PER_COUNTRY_HIDA]:
            f.write(f"{link}\n")
        f.write("\n")
        
        f.write(f"# ========== 🇷🇺 Россия ==========\n")
        by_country["🇷🇺 Россия"].sort(key=lambda x: x[0])
        for ping, link in by_country["🇷🇺 Россия"][:MAX_PER_COUNTRY_HIDA]:
            f.write(f"{link}\n")
        f.write("\n")
        
        f.write(f"# ========== 🇳🇱 Нидерланды ==========\n")
        by_country["🇳🇱 Нидерланды"].sort(key=lambda x: x[0])
        for ping, link in by_country["🇳🇱 Нидерланды"][:MAX_PER_COUNTRY_HIDA]:
            f.write(f"{link}\n")
        f.write("\n")
        
        f.write(f"# ========== 🌍 Другие (Mahdibland) ==========\n")
        for ping, link in best_other:
            f.write(f"{link}\n")
        f.write("\n")
        
        total = sum(len(by_country[c][:MAX_PER_COUNTRY_HIDA]) for c in COUNTRY_RANGES) + len(best_other)
        f.write(f"# Всего: {total} серверов\n")
    
    for c in COUNTRY_RANGES:
        print(f"{c}: {len(by_country[c])}")
    print(f"Другие: {len(best_other)}")

if __name__ == '__main__':
    main()
