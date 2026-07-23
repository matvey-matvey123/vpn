import requests
import base64
import re
import time
import socket

# Список подписок
SUBSCRIPTIONS = [
    "https://raw.githubusercontent.com/Hidashimora/free-vpn-anti-rkn/main/configs/1.1.txt",
    # Добавь другие подписки сюда
]

OUTPUT_FILE = "working.txt"
MAX_SERVERS = 5
TIMEOUT = 5  # секунд на проверку

def fetch_links(url):
    """Скачивает подписку и возвращает список ссылок"""
    try:
        r = requests.get(url, timeout=30)
        if r.status_code != 200:
            return []
        
        # Пробуем декодировать base64
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

def extract_ip_port(link):
    """Извлекает IP и порт из ссылки"""
    # VLESS/VMess: ...@IP:PORT?... или ...@DOMAIN:PORT?...
    match = re.search(r'@([^:]+):(\d+)', link)
    if match:
        host = match.group(1)
        port = int(match.group(2))
        return host, port
    
    # SS: IP:PORT после @
    match = re.search(r'@(.+):(\d+)', link)
    if match:
        host = match.group(1)
        port = int(match.group(2))
        return host, port
    
    return None, None

def check_tcp(host, port):
    """Проверяет TCP соединение"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(TIMEOUT)
        start = time.time()
        s.connect((host, port))
        ping = round((time.time() - start) * 1000)  # мс
        s.close()
        return True, ping
    except:
        return False, 9999

def main():
    all_links = []
    
    for sub_url in SUBSCRIPTIONS:
        links = fetch_links(sub_url)
        all_links.extend(links)
        print(f"Загружено {len(links)} ссылок из {sub_url}")
    
    # Убираем дубликаты
    unique_links = list(dict.fromkeys(all_links))
    print(f"Всего уникальных ссылок: {len(unique_links)}")
    
    # Проверяем серверы
    results = []
    for link in unique_links:
        host, port = extract_ip_port(link)
        if not host or not port:
            continue
        
        # Разрешаем DNS если домен
        try:
            ip = socket.gethostbyname(host)
        except:
            continue
        
        ok, ping = check_tcp(ip, port)
        if ok:
            results.append((ping, link))
            print(f"✅ {host}:{port} - {ping}ms")
        else:
            print(f"❌ {host}:{port}")
    
    # Сортируем по пингу и берём лучшие
    results.sort(key=lambda x: x[0])
    best = results[:MAX_SERVERS]
    
    # Сохраняем
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write("# Автоматически отобраны лучшие 5 серверов\n")
        f.write(f"# Обновлено: {time.ctime()}\n\n")
        for ping, link in best:
            f.write(f"{link}\n")
    
    print(f"\nСохранено {len(best)} лучших серверов в {OUTPUT_FILE}")

if __name__ == '__main__':
    main()
