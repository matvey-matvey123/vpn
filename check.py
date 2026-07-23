import requests
import base64
import re
import time
import socket
import ipaddress
import os

SUBSCRIPTIONS = [
    "https://raw.githubusercontent.com/Hidashimora/free-vpn-anti-rkn/main/configs/1.1.txt",
    "https://raw.githubusercontent.com/mahdibland/ShadowsocksAggregator/master/sub/sub_merge.txt",
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
        links = []
        for line in text.split('\n'):
            line = line.strip()
            if line and not line.startswith('#') and ('://' in line):
                links.append(line)
        return links
    except Exception as e:
        print(f"Ошибка загрузки {url}: {e}")
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
    """Проверяет одну подписку и возвращает серверы по странам + другие"""
    links = fetch_links(sub_url)
    unique_links = list(dict.fromkeys(links))[:max_check]  # Ограничиваем для скорости
    print(f"Проверяю {len(unique_links)} ссылок из {sub_url}")
    
    by_country = {c: [] for c in COUNTRY_RANGES}
    other = []
    
    for i, link in enumerate(unique_links):
        if i % 100 == 0:
            print(f"  Прогресс: {i}/{len(unique_links)}")
        
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
    print("=" * 50)
    print(f"Запуск: {time.ctime()}")
    
    # Проверяем Hidashimora
    print("\n>>> Hidashimora (по странам)")
    by_country_hida, other_hida = check_subscription(SUBSCRIPTIONS[0], max_check=300)
    
    # Проверяем Mahdibland
    print("\n>>> Mahdibland (любые 10)")
    _, other_mahdi = check_subscription(SUBSCRIPTIONS[1], max_check=200)
    
    # Объединяем другие серверы
    all_other = other_hida + other_mahdi
    all_other.sort(key=lambda x: x[0])
    best_other = all_other[:MAX_OTHER]
    
    # Сохраняем результат
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(f"# 🤖 Авто-проверка | {time.ctime()}\n\n")
        
        for country in ["🇩🇪 Германия", "🇺🇸 США", "🇷🇺 Россия", "🇳🇱 Нидерланды"]:
            servers = by_country_hida[country][:MAX_PER_COUNTRY]
            f.write(f"# ========== {country} ({len(servers)} шт) ==========\n")
            for ping, link in servers:
                f.write(f"{link}\n")
            f.write("\n")
        
        f.write(f"# ========== 🌍 Другие рабочие ({len(best_other)} шт) ==========\n")
        for ping, link in best_other:
            f.write(f"{link}\n")
        f.write("\n")
        
        total = sum(len(by_country_hida[c][:MAX_PER_COUNTRY]) for c in COUNTRY_RANGES) + len(best_other)
        f.write(f"# Всего: {total} серверов\n")
    
    print("\nГотово!")
    for c in COUNTRY_RANGES:
        print(f"  {c}: {len(by_country_hida[c][:MAX_PER_COUNTRY])}")
    print(f"  Другие: {len(best_other)}")

if __name__ == '__main__':
    main()
