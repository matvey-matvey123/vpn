from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    if 'message' in data:
        chat_id = data['message']['chat']['id']
        text = data['message'].get('text', '').lower()
        
        if text in ['обнови', 'update', '/update']:
            send(chat_id, '🔄 Запускаю...')
            r = requests.post(
                'https://api.github.com/repos/matvey-matvey123/vpn/actions/workflows/check-servers.yml/dispatches',
                headers={
                    'Authorization': 'token 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',
                    'Accept': 'application/vnd.github+json'
                },
                json={'ref': 'main'}
            )
            send(chat_id, '✅ Запущено!' if r.status_code == 204 else '⚠️ Уже запущен')
        
        elif text in ['проверь', 'статус', '/status']:
            r = requests.get('https://raw.githubusercontent.com/matvey-matvey123/vpn/main/working.txt')
            if r.ok:
                n = len([l for l in r.text.split('\n') if '://' in l])
                send(chat_id, f'📡 Серверов: {n}')
        
        else:
            send(chat_id, '👋 обнови / проверь')
    
    return jsonify({'status': 'ok'})

def send(chat_id, text):
    requests.post(
        f'https://api.telegram.org/bot8907038357:AAGSgNYn96USmTiLLL9EwwgpC4pmJshv_ek/sendMessage',
        json={'chat_id': chat_id, 'text': text}
    )

if __name__ == '__main__':
    app.run()
