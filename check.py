import requests
import base64
import re
import time
import socket

SUBSCRIPTIONS = [
    "https://raw.githubusercontent.com/Hidashimora/free-vpn-anti-rkn/main/configs/1.1.txt",
]

OUTPUT_FILE = "working.txt"
MAX_PER_COUNTRY = 5
TIMEOUT = 3

# Ключевые слова для стран
COUNTRY_KEYWORDS = {
    "🇩🇪 Германия": ["de", "germany", "🇩🇪", "DE", "германия"],
    "🇺🇸 США": ["us", "usa", "🇺🇸", "US", "сша", "америка"],
    "🇷🇺 Россия": ["ru", "russia", "🇷🇺", "RU", "россия", "рф"],
}

def fetch_links(url):
    try:
        r = requests.get(url, timeout=30)
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

def detect_country(link):
    link_lower = link.lower()
    for country, keywords in COUNTRY_KEYWORDS.items():
        for kw in keywords:
            if kw.lower() in link_lower:
                return country
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
        return True, ping
    except:
        return False, 9999

def main():
    all_links = []
    for sub_url in SUBSCRIPTIONS:
        links = fetch_links(sub_url)
        all_links.extend(links)
    
    unique_links = list(dict.fromkeys(all_links))
    print(f"Всего уникальных ссылок: {len(unique_links)}")
    
    # Сортируем по странам
    by_country = {c: [] for c in COUNTRY_KEYWORDS}
    
    for link in unique_links:
        host, port = extract_host_port(link)
        if not host or not port:
            continue
        
        ok, ping = check_tcp(host, port)
        if not ok:
            continue
        
        country = detect_country(link)
        if country:
            by_country[country].append((ping, link))
            print(f"✅ {country} | {host}:{port} | {ping}ms")
    
    # Сохраняем результат
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(f"# Авто-проверка | Обновлено: {time.ctime()}\n\n")
        
        total = 0
        for country in ["🇩🇪 Германия", "🇺🇸 США", "🇷🇺 Россия"]:
            servers = by_country[country]
            servers.sort(key=lambda x: x[0])
            best = servers[:MAX_PER_COUNTRY]
            total += len(best)
            f.write(f"# ========== {country} ({len(best)} шт) ==========\n")
            for ping, link in best:
                f.write(f"{link}\n")
            f.write("\n")
        
        f.write(f"# Всего: {total} серверов\n")
    
    print(f"\n✅ Германия: {len(by_country['🇩🇪 Германия'])}")
    print(f"✅ США: {len(by_country['🇺🇸 США'])}")
    print(f"✅ Россия: {len(by_country['🇷🇺 Россия'])}")
    print(f"Готово! Сохранено в {OUTPUT_FILE}")

if __name__ == '__main__':
    main()
