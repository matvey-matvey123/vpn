import requests
import base64
import re
import time
import socket

SUBSCRIPTIONS = [
    "https://raw.githubusercontent.com/Hidashimora/free-vpn-anti-rkn/main/configs/1.txt",
    "https://raw.githubusercontent.com/Hidashimora/free-vpn-anti-rkn/main/configs/5.txt",
    "https://raw.githubusercontent.com/Hidashimora/free-vpn-anti-rkn/main/configs/10.1.txt",
    "https://raw.githubusercontent.com/Hidashimora/free-vpn-anti-rkn/main/configs/15.txt",
    "https://raw.githubusercontent.com/Hidashimora/free-vpn-anti-rkn/main/configs/20.txt",
    "https://raw.githubusercontent.com/Hidashimora/free-vpn-anti-rkn/main/configs/25.txt",
    "https://raw.githubusercontent.com/Hidashimora/free-vpn-anti-rkn/main/configs/30.txt",
    "https://raw.githubusercontent.com/Hidashimora/free-vpn-anti-rkn/main/configs/34.txt",
    "https://raw.githubusercontent.com/Hidashimora/free-vpn-anti-rkn/main/configs/2.1.txt",
    "https://raw.githubusercontent.com/Hidashimora/free-vpn-anti-rkn/main/configs/8.txt",
]

OUTPUT_FILE = "working.txt"
MAX_SERVERS = 20
MAX_PING = 300
TIMEOUT = 3

DYNAMIC_KEYWORDS = [
    "dynamic", "dyn", "ddns", "no-ip", "duckdns", "hopto", "zapto",
    "sytes", "servehttp", "serveftp", "myftp", "myddns", "changeip",
    "dnsdynamic", "dynamicdns", "dynip", "dynamic-ip",
]

def is_dynamic(link):
    link_lower = link.lower()
    for kw in DYNAMIC_KEYWORDS:
        if kw in link_lower:
            return True
    host = re.search(r'@([^:?\s]+):', link)
    if host:
        h = host.group(1)
        if not re.match(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$', h):
            parts = h.split('.')
            if len(parts) > 3:
                return True
    return False

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

def check_tcp(host, port):
    try:
        ip = socket.gethostbyname(host)
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(TIMEOUT)
        t = time.time()
        s.connect((ip, port))
        p = round((time.time() - t) * 1000)
        s.close()
        return True, p
    except:
        return False, 9999

def main():
    all_links = []
    for sub in SUBSCRIPTIONS:
        links = fetch_links(sub)
        all_links.extend(links)
    
    unique_links = list(dict.fromkeys(all_links))
    static_links = [l for l in unique_links if not is_dynamic(l)]
    
    results = []
    for l in static_links:
        h, p = extract_host_port(l)
        if not h:
            continue
        ok, ping = check_tcp(h, p)
        if ok and ping <= MAX_PING:
            results.append((ping, l))
    
    results.sort()
    best = results[:MAX_SERVERS]
    
    lines = [l for _, l in best]
    with open(OUTPUT_FILE, 'w') as f:
        f.write('\n'.join(lines))

if __name__ == '__main__':
    main()
