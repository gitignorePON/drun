import tkinter as tk
from tkinter import ttk, messagebox
import json
import threading
import time
import os

# -------------------------------
# Настройки стиля — темно-фиолетовый неон
# -------------------------------
BG_DARK = "#0d0618"        # Почти черный с фиолетовым отливом
BG_PANEL = "#160b2a"       # Левая панель — темнее фиолет
BG_CHAT = "#0f0820"        # Правая панель
ACCENT = "#b16ce1"         # Неоново-фиолетовый (#b16ce1)
ACCENT_HOVER = "#cc8cff"
ACCENT_ACTIVE = "#d9a1ff"
TEXT_COLOR = "#f0f0f0"
TEXT_SECONDARY = "#aaaaff"
BORDER_COLOR = "#8a5ad9"

# -------------------------------
# Хранилище чатов
# -------------------------------
CHAT_FILE = "chats.json"

def load_chats():
    if os.path.exists(CHAT_FILE):
        try:
            with open(CHAT_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            pass
    return {
        "Избранные": [],
        "Qwen": [
            {"role": "system", "text": "Привет! Я Qwen — ваш виртуальный помощник в Drun. Спрашивайте!"}
        ]
    }

def save_chats(chats):
    with open(CHAT_FILE, "w", encoding="utf-8") as f:
        json.dump(chats, f, ensure_ascii=False, indent=2)

# -------------------------------
# Основное окно
# -------------------------------
class DrunMessenger:
    def __init__(self, root):
        self.root = root
        self.root.title("Drun — Мессенджер Будущего")
        self.root.geometry("900x600")
        self.root.configure(bg=BG_DARK)

        # Иконка (опционально, если есть файл)
        # self.root.iconbitmap("drun_icon.ico")

        # Загрузка чатов
        self.chats = load_chats()
        self.current_chat = "Избранные"

        self.setup_ui()

    def setup_ui(self):
        # Главной контейнер: 2 колонки
        self.pane = tk.PanedWindow(self.root, orient=tk.HORIZONTAL, bg=BG_DARK, sashwidth=4)
        self.pane.pack(fill=tk.BOTH, expand=True)

        # ----- Левая панель: список чатов (25%) -----
        self.chat_list_frame = tk.Frame(self.pane, bg=BG_PANEL, width=225)
        self.pane.add(self.chat_list_frame)

        tk.Label(self.chat_list_frame, text="ЧАТЫ", bg=BG_PANEL, fg=ACCENT,
                 font=("Segoe UI", 12, "bold")).pack(pady=(10, 5))

        self.chat_buttons = {}
        for name in ["Избранные", "Qwen"]:
            btn = tk.Label(
                self.chat_list_frame,
                text=name,
                bg=BG_PANEL,
                fg=TEXT_COLOR,
                font=("Segoe UI", 11),
                padx=15,
                pady=8,
                cursor="hand2",
                relief="flat"
            )
            btn.pack(fill=tk.X, padx=10, pady=2)
            btn.bind("<Button-1>", lambda e, n=name: self.select_chat(n))
            btn.bind("<Enter>", lambda e, b=btn: b.config(bg=BG_CHAT, fg=ACCENT_HOVER))
            btn.bind("<Leave>", lambda e, b=btn, n=name: b.config(
                bg=BG_PANEL if self.current_chat != n else ACCENT_ACTIVE,
                fg=TEXT_COLOR if self.current_chat != n else ACCENT_HOVER
            ))
            self.chat_buttons[name] = btn

        self.update_chat_button_style()

        # ----- Правая панель: чат (75%) -----
        self.chat_frame = tk.Frame(self.pane, bg=BG_CHAT)
        self.pane.add(self.chat_frame)

        # Заголовок чата
        self.chat_title = tk.Label(
            self.chat_frame, text=self.current_chat.upper(),
            bg=BG_CHAT, fg=ACCENT, font=("Segoe UI", 14, "bold")
        )
        self.chat_title.pack(pady=10)

        # Область сообщений — Text + Scrollbar
        text_frame = tk.Frame(self.chat_frame, bg=BG_CHAT)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 10))

        self.msg_text = tk.Text(
            text_frame,
            bg=BG_DARK,
            fg=TEXT_COLOR,
            font=("Segoe UI", 11),
            wrap=tk.WORD,
            relief="flat",
            padx=12,
            pady=12,
            insertbackground=ACCENT,
            selectbackground=ACCENT,
            selectforeground=BG_DARK,
            state=tk.DISABLED,
            highlightthickness=2,
            highlightbackground=BORDER_COLOR
        )
        self.msg_scroll = ttk.Scrollbar(text_frame, command=self.msg_text.yview)
        self.msg_text.configure(yscrollcommand=self.msg_scroll.set)

        self.msg_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.msg_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        # Поле ввода и кнопка отправки
        input_frame = tk.Frame(self.chat_frame, bg=BG_CHAT)
        input_frame.pack(fill=tk.X, padx=15, pady=(0, 15))

        self.input_entry = tk.Entry(
            input_frame,
            bg=BG_DARK,
            fg=TEXT_COLOR,
            font=("Segoe UI", 11),
            insertbackground=ACCENT,
            relief="flat",
            highlightthickness=2,
            highlightbackground=BORDER_COLOR,
            highlightcolor=ACCENT
        )
        self.input_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=6)

        send_btn = tk.Button(
            input_frame,
            text="➤",
            bg=ACCENT,
            fg=BG_DARK,
            font=("Segoe UI", 12, "bold"),
            relief="flat",
            cursor="hand2",
            command=self.send_message
        )
        send_btn.pack(side=tk.RIGHT, padx=(8, 0), ipadx=12, ipady=6)

        # Привязка Enter
        self.input_entry.bind("<Return>", lambda e: self.send_message())
        self.input_entry.bind("<Shift-Return>", lambda e: self.input_entry.insert(tk.END, "\n"))

        # Загрузка начального чата
        self.load_chat_history()

    def update_chat_button_style(self):
        for name, btn in self.chat_buttons.items():
            if name == self.current_chat:
                btn.config(bg=ACCENT_ACTIVE, fg=ACCENT_HOVER)
            else:
                btn.config(bg=BG_PANEL, fg=TEXT_COLOR)

    def select_chat(self, chat_name):
        self.current_chat = chat_name
        self.update_chat_button_style()
        self.chat_title.config(text=chat_name.upper())
        self.load_chat_history()

    def load_chat_history(self):
        self.msg_text.config(state=tk.NORMAL)
        self.msg_text.delete("1.0", tk.END)

        messages = self.chats[self.current_chat]
        for msg in messages:
            role = msg["role"]
            text = msg["text"]
            if role == "user":
                self._insert_message("Вы", text, align="right", color=ACCENT)
            elif role == "system":
                self._insert_message("Drun", text, align="left", color="#8888ff", italic=True)
            elif role == "ai":
                self._insert_message("Qwen", text, align="left", color="#d197ff")

        self.msg_text.config(state=tk.DISABLED)
        self.msg_text.yview(tk.END)

    def _insert_message(self, sender, text, align="left", color="#ffffff", italic=False):
        tag_name = f"{sender}_{len(self.msg_text.get('1.0', tk.END))}"
        self.msg_text.tag_configure(
            tag_name,
            lmargin1=20 if align == "left" else 100,
            lmargin2=20 if align == "left" else 100,
            rmargin=100 if align == "left" else 20,
            justify=tk.LEFT if align == "left" else tk.RIGHT,
            foreground=color,
            font=("Segoe UI", 10, "italic" if italic else "normal")
        )
        header = f"{sender}:\n" if sender else ""
        self.msg_text.insert(tk.END, f"{header}{text}\n\n", tag_name)

    def send_message(self):
        msg = self.input_entry.get().strip()
        if not msg:
            return

        # Добавить сообщение от пользователя
        self.chats[self.current_chat].append({"role": "user", "text": msg})
        self.input_entry.delete(0, tk.END)

        self.load_chat_history()  # Обновить интерфейс

        # Сохранить сразу
        save_chats(self.chats)

        # Если чат с Qwen — имитируем ответ через поток
        if self.current_chat == "Qwen":
            threading.Thread(target=self._simulate_qwen_response, args=(msg,), daemon=True).start()

    def _simulate_qwen_response(self, user_msg):
        time.sleep(0.8)  # Эмуляция задержки

        # Простая логика ответа (можно расширить)
        lower_msg = user_msg.lower()
        if any(kw in lower_msg for kw in ["привет", "здравствуй", "хай", "hello"]):
            reply = "Привет! Рад снова с вами в Drun 🌌"
        elif any(kw in lower_msg for kw in ["как дела", "как ты", "how are you"]):
            reply = "Отлично! Особенно когда общаюсь с таким интересным пользователем 😉"
        elif any(kw in lower_msg for kw in ["спасибо", "благодарю", "thx", "thanks"]):
            reply = "Всегда пожалуйста! Заходите чаще — в Drun всегда есть что обсудить ✨"
        elif "drun" in lower_msg:
            reply = "Drun — не просто мессенджер. Это портал в будущее связи. Ловит даже в Обосратии 📡"
        else:
            reply = "Интересный вопрос! В Drun мы ценим любознательность. Продолжайте в том же духе 🔮"

        # Добавить в чат
        self.chats["Qwen"].append({"role": "ai", "text": reply})
        save_chats(self.chats)

        # Обновить UI в основном потоке
        self.root.after(0, self.load_chat_history)


# -------------------------------
# Запуск
# -------------------------------
if __name__ == "__main__":
    root = tk.Tk()
    app = DrunMessenger(root)
    root.mainloop()