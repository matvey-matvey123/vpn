import urllib.request
import base64
import shutil

SUBSCRIPTIONS = [
    "https://raw.githubusercontent.com/mahdibland/ShadowsocksAggregator/master/sub/sub_merge.txt",
    "https://raw.githubusercontent.com/barry-far/V2ray-Config/main/All_Configs_Sub.txt",
    "https://raw.githubusercontent.com/yebekhe/TelegramV2rayCollector/main/sub/normal/mix",
    "https://raw.githubusercontent.com/rtwo2/FastNodes/main/sub/everything.txt",
    "https://raw.githubusercontent.com/ninjastrikers/Nexus-nodes/main/configs/all.txt",
    "https://raw.githubusercontent.com/Au1rxx/free-vpn-subscriptions/main/output/v2ray-base64.txt",
    "https://raw.githubusercontent.com/Pawdroid/Free-servers/main/sub",
    "https://raw.githubusercontent.com/peasoft/NoMoreWalls/master/list.txt",
    "https://raw.githubusercontent.com/ebrasha/free-v2ray-public-list/main/all_extracted_configs.txt",
    "https://raw.githubusercontent.com/arshsisodiya/helios-server/main/proxies.txt",
    "https://raw.githubusercontent.com/soroushmirzaei/telegram-vpn-collector/main/subs/split/v2ray/v2ray_base64.txt",
    "https://raw.githubusercontent.com/Surfboardv2ray/v2ray-worker-sub/main/providers.txt",
    "https://raw.githubusercontent.com/hans-thomas/v2ray-subscription/refs/heads/master/servers.txt",
    "https://raw.githubusercontent.com/a2470982985/getNode/main/v2ray.txt",
    "https://raw.githubusercontent.com/amirhosseinchoghaei/iran-ipline/main/v2ray.txt",
    "https://raw.githubusercontent.com/sevcator/5ubscrpt10n/main/protocols/vl.txt",
    "https://raw.githubusercontent.com/sevcator/5ubscrpt10n/main/protocols/tr.txt",
    "https://raw.githubusercontent.com/sevcator/5ubscrpt10n/main/protocols/ss.txt",
    "https://raw.githubusercontent.com/Hidashimora/free-vpn-anti-rkn/main/configs/1.1.txt",
    "https://raw.githubusercontent.com/Hidashimora/free-vpn-anti-rkn/main/configs/2.1.txt",
    "https://raw.githubusercontent.com/Hidashimora/free-vpn-anti-rkn/main/configs/3.1.txt",
    "https://raw.githubusercontent.com/Hidashimora/free-vpn-anti-rkn/main/configs/4.1.txt",
    "https://raw.githubusercontent.com/Hidashimora/free-vpn-anti-rkn/main/configs/5.1.txt",
    "https://raw.githubusercontent.com/V2RAYCONFIGSPOOL/V2RAY_SUB/main/v2ray_configs_no1.txt",
    "https://raw.githubusercontent.com/V2RAYCONFIGSPOOL/V2RAY_SUB/main/v2ray_configs_no8.txt",
    "https://raw.githubusercontent.com/V2RAYCONFIGSPOOL/V2RAY_SUB/main/v2ray_configs_no10.txt",
    "https://raw.githubusercontent.com/ssavnayt/AWCFG-CONFIG-LIST/main/CONFIGS-AUTO-TEST",
    "https://raw.githubusercontent.com/ssavnayt/AWCFG-CONFIG-LIST/main/Configs-AUTO-ALT2.txt",
    "https://raw.githubusercontent.com/ssavnayt/AWCFG-CONFIG-LIST/main/Configs-all-country.txt",
    "https://raw.githubusercontent.com/morteza-v2/free-v2ray-irancell-config/main/Sub1.txt",
    "https://raw.githubusercontent.com/miladtahanian/V2RayCFGDumper/main/sub.txt",
    "https://raw.githubusercontent.com/pornnewbee/free-vless-VPN/main/vless.txt",
]

OUTPUT_FILE = "working.txt"
MAX_SERVERS = 400

COPY_FILES = [
    "1019410.txt", "1033910.txt", "1026810.txt", "1080810.txt", "1063010.txt",
    "1042310.txt", "1061910.txt", "1077610.txt", "1054310.txt", "1016910.txt",
]

def fetch_links(url):
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=30) as r:
            text = r.read().decode('utf-8', errors='ignore')
        try:
            text = base64.b64decode(text).decode('utf-8', errors='ignore')
        except:
            pass
        return [l.strip() for l in text.split('\n') if l.strip() and not l.startswith('#') and '://' in l]
    except:
        return []

all_links = []
for sub in SUBSCRIPTIONS:
    links = fetch_links(sub)
    all_links.extend(links)

unique_links = list(dict.fromkeys(all_links))[:MAX_SERVERS]
content = '\n'.join(unique_links)

with open(OUTPUT_FILE, 'w') as f:
    f.write(content)

for fn in COPY_FILES:
    shutil.copy(OUTPUT_FILE, fn)
