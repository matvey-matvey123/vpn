#!/usr/bin/env python3
"""VPN Config Checker with GUI - checks locally, pushes to GitHub"""

import socket
import json
import os
import sys
import random
import subprocess
import threading
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

# Settings
INPUT_FILE = 'working2.txt'
OUTPUT_FILE = 'test.txt'
STATS_FILE = 'test_stats.json'

MAX_WORKING = 40
MAX_CHECK = 2000
MAX_WORKERS = 100
TIMEOUT = 3

# GitHub
GITHUB_USER = "matvey-matvey123"
GITHUB_REPO = "vpn"
GITHUB_BRANCH = "main"

class VPNCheckerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("VPN Config Checker - matvey-matvey123/vpn")
        self.root.geometry("700x600")
        self.root.resizable(True, True)
        
        self.running = False
        self.working_configs = []
        
        self.setup_ui()
    
    def setup_ui(self):
        # Title
        title = tk.Label(self.root, text="🔍 VPN CONFIG CHECKER", 
                        font=("Arial", 16, "bold"))
        title.pack(pady=10)
        
        # GitHub info
        github_label = tk.Label(self.root, 
                               text=f"📁 GitHub: {GITHUB_USER}/{GITHUB_REPO}",
                               font=("Arial", 10))
        github_label.pack()
        
        # Frame for buttons
        btn_frame = tk.Frame(self.root)
        btn_frame.pack(pady=10)
        
        self.check_btn = tk.Button(btn_frame, text="▶️ Проверить конфиги", 
                                   command=self.start_check,
                                   bg="#4CAF50", fg="white",
                                   font=("Arial", 12), padx=20, pady=5)
        self.check_btn.pack(side=tk.LEFT, padx=5)
        
        self.push_btn = tk.Button(btn_frame, text="📤 Отправить на GitHub",
                                  command=self.push_to_github,
                                  bg="#2196F3", fg="white",
                                  font=("Arial", 12), padx=20, pady=5,
                                  state=tk.DISABLED)
        self.push_btn.pack(side=tk.LEFT, padx=5)
        
        self.stop_btn = tk.Button(btn_frame, text="⏹ Стоп",
                                  command=self.stop_check,
                                  bg="#f44336", fg="white",
                                  font=("Arial", 12), padx=20, pady=5,
                                  state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT, padx=5)
        
        # Progress
        self.progress_frame = tk.Frame(self.root)
        self.progress_frame.pack(pady=10, fill=tk.X, padx=20)
        
        self.progress_bar = ttk.Progressbar(self.progress_frame, length=400, mode='determinate')
        self.progress_bar.pack(side=tk.LEFT, padx=5)
        
        self.progress_label = tk.Label(self.progress_frame, text="0/0", font=("Arial", 10))
        self.progress_label.pack(side=tk.LEFT, padx=5)
        
        # Stats
        self.stats_frame = tk.Frame(self.root)
        self.stats_frame.pack(pady=5)
        
        self.total_label = tk.Label(self.stats_frame, text="Всего: 0", font=("Arial", 10))
        self.total_label.pack(side=tk.LEFT, padx=10)
        
        self.working_label = tk.Label(self.stats_frame, text="Рабочих: 0", 
                                      font=("Arial", 10, "bold"), fg="green")
        self.working_label.pack(side=tk.LEFT, padx=10)
        
        self.time_label = tk.Label(self.stats_frame, text="Время: 0с", font=("Arial", 10))
        self.time_label.pack(side=tk.LEFT, padx=10)
        
        # Log
        log_label = tk.Label(self.root, text="📋 Лог:", font=("Arial", 10, "bold"))
        log_label.pack(anchor=tk.W, padx=20)
        
        self.log_text = scrolledtext.ScrolledText(self.root, height=15, 
                                                   font=("Consolas", 9))
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Status
        self.status_label = tk.Label(self.root, text="Готов к работе", 
                                     font=("Arial", 10), fg="gray")
        self.status_label.pack(pady=5)
    
    def log(self, message):
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.root.update()
    
    def check_tcp(self, config):
        try:
            if '@' not in config:
                return False, config
            after = config.split('@')[1]
            for sep in ['?', '#', '/', '&']:
                if sep in after:
                    after = after.split(sep)[0]
            if ':' not in after:
                return False, config
            host, port = after.rsplit(':', 1)
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(TIMEOUT)
            result = sock.connect_ex((host.strip(), int(port.strip())))
            sock.close()
            return result == 0, config
        except:
            return False, config
    
    def start_check(self):
        if self.running:
            return
        
        self.running = True
        self.check_btn.config(state=tk.DISABLED)
        self.push_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        self.working_configs = []
        self.log_text.delete(1.0, tk.END)
        
        thread = threading.Thread(target=self.run_check)
        thread.start()
    
    def run_check(self):
        start_time = datetime.now()
        self.log("="*50)
        self.log(f"🔍 Начинаю проверку конфигов...")
        self.log(f"⏰ {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        self.log("="*50)
        
        if not os.path.exists(INPUT_FILE):
            self.log(f"❌ Файл {INPUT_FILE} не найден!")
            self.status_label.config(text="Ошибка: файл не найден")
            self.running = False
            self.check_btn.config(state=tk.NORMAL)
            self.stop_btn.config(state=tk.DISABLED)
            return
        
        with open(INPUT_FILE, 'r', encoding='utf-8', errors='ignore') as f:
            configs = [l.strip() for l in f if l.strip() and '@' in l]
        
        total = len(configs)
        self.log(f"📋 Загружено конфигов: {total:,}")
        self.total_label.config(text=f"Всего: {total:,}")
        
        random.shuffle(configs)
        to_check = configs[:MAX_CHECK]
        
        self.progress_bar['maximum'] = len(to_check)
        
        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            futures = {executor.submit(self.check_tcp, c): c for c in to_check}
            
            checked = 0
            for future in as_completed(futures):
                if not self.running:
                    for f in futures:
                        f.cancel()
                    break
                
                checked += 1
                try:
                    ok, cfg = future.result(timeout=TIMEOUT+2)
                    if ok:
                        self.working_configs.append(cfg)
                        host = cfg.split('@')[1].split(':')[0].split('?')[0].split('#')[0]
                        self.log(f"✅ #{len(self.working_configs):2d} {host}")
                    
                    self.progress_bar['value'] = checked
                    self.progress_label.config(text=f"{checked}/{len(to_check)}")
                    self.working_label.config(text=f"Рабочих: {len(self.working_configs)}")
                    
                    elapsed = (datetime.now() - start_time).total_seconds()
                    self.time_label.config(text=f"Время: {elapsed:.0f}с")
                    
                    if len(self.working_configs) >= MAX_WORKING:
                        self.log(f"\n🎯 Найдено {MAX_WORKING} рабочих конфигов!")
                        for f in futures:
                            f.cancel()
                        break
                        
                except:
                    pass
        
        # Save
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            for w in self.working_configs:
                f.write(w + '\n')
        
        with open(STATS_FILE, 'w', encoding='utf-8') as f:
            json.dump({
                'timestamp': datetime.now().isoformat(),
                'working': len(self.working_configs),
                'total': total
            }, f, indent=2)
        
        duration = (datetime.now() - start_time).total_seconds()
        
        self.log(f"\n{'='*50}")
        self.log(f"✅ Проверка завершена!")
        self.log(f"⏱️ Время: {duration:.1f}с")
        self.log(f"📊 Рабочих: {len(self.working_configs)} из {len(to_check)}")
        self.log(f"📁 Сохранено в: {OUTPUT_FILE}")
        self.log(f"{'='*50}")
        
        self.running = False
        self.check_btn.config(state=tk.NORMAL)
        self.push_btn.config(state=tk.NORMAL if self.working_configs else tk.DISABLED)
        self.stop_btn.config(state=tk.DISABLED)
        self.status_label.config(text=f"Готово! Найдено {len(self.working_configs)} рабочих конфигов")
    
    def stop_check(self):
        self.running = False
        self.log("\n⏹ Остановлено пользователем")
        self.status_label.config(text="Остановлено")
    
    def push_to_github(self):
        if not self.working_configs:
            messagebox.showwarning("Нет данных", "Нет рабочих конфигов для отправки!")
            return
        
        self.status_label.config(text="Отправка на GitHub...")
        
        def push():
            try:
                self.log("\n📤 Отправка на GitHub...")
                
                # Pull latest
                subprocess.run(['git', 'pull', 'origin', GITHUB_BRANCH], 
                             check=True, capture_output=True, cwd=os.path.dirname(__file__))
                
                # Add files
                subprocess.run(['git', 'add', OUTPUT_FILE, STATS_FILE], 
                             check=True, capture_output=True, cwd=os.path.dirname(__file__))
                
                # Check changes
                result = subprocess.run(['git', 'diff', '--staged', '--quiet'], 
                                      capture_output=True, cwd=os.path.dirname(__file__))
                
                if result.returncode == 0:
                    self.log("📁 Нет изменений для отправки")
                    self.status_label.config(text="Нет изменений")
                    return
                
                # Commit
                count = len(self.working_configs)
                subprocess.run([
                    'git', 'commit', '-m', 
                    f'✅ {count} working configs [{datetime.now().strftime("%H:%M")}]'
                ], check=True, capture_output=True, cwd=os.path.dirname(__file__))
                
                # Push
                subprocess.run(['git', 'push', 'origin', GITHUB_BRANCH], 
                             check=True, capture_output=True, cwd=os.path.dirname(__file__))
                
                self.log(f"✅ Успешно отправлено {count} конфигов на GitHub!")
                self.log(f"🔗 https://github.com/{GITHUB_USER}/{GITHUB_REPO}")
                self.status_label.config(text=f"Отправлено! {count} конфигов на GitHub")
                
                messagebox.showinfo("Успех", 
                    f"✅ {count} рабочих конфигов отправлены на GitHub!")
                
            except Exception as e:
                self.log(f"❌ Ошибка отправки: {e}")
                self.status_label.config(text="Ошибка отправки")
                messagebox.showerror("Ошибка", 
                    f"Не удалось отправить на GitHub:\n{e}\n\nУбедись что ты в папке с репозиторием и залогинен в git!")
        
        thread = threading.Thread(target=push)
        thread.start()

if __name__ == '__main__':
    root = tk.Tk()
    app = VPNCheckerGUI(root)
    root.mainloop()