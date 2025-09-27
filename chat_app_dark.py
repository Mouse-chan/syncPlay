import tkinter as tk
from tkinter import scrolledtext, ttk
import threading
import queue
import time

from messages_controller import MessagesCtrl


class SimpleChatApp:
    def __init__(self, master):
        self.master = master
        master.title("Чатик")
        master.geometry("400x500")

        # Настройка темной темы
        self.setup_dark_theme()

        self.msg_ctrl = MessagesCtrl()
        self.message_queue = queue.Queue()
        self.polling_active = True

        if not self.msg_ctrl.check_connection():
            print("Внимание: проблемы с соединением")

        # Создаем виджеты с темной темой
        self.chat_history = scrolledtext.ScrolledText(
            master,
            state='disabled',
            wrap=tk.WORD,
            bg=self.colors['bg'],
            fg=self.colors['text'],
            insertbackground=self.colors['text'],  # Цвет курсора
            selectbackground=self.colors['select_bg'],
            selectforeground=self.colors['text']
        )
        self.chat_history.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        self.input_frame = tk.Frame(master, bg=self.colors['bg'])
        self.input_frame.pack(padx=10, pady=10, fill=tk.X)

        # Поле для ввода сообщения с темной темой
        self.entry = tk.Entry(
            self.input_frame,
            bg=self.colors['entry_bg'],
            fg=self.colors['text'],
            insertbackground=self.colors['text'],
            selectbackground=self.colors['select_bg'],
            selectforeground=self.colors['text']
        )
        self.entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.entry.bind("<Return>", self.send_message_handler)

        # Кнопка отправки с темной темой
        self.send_button = tk.Button(
            self.input_frame,
            text="Отправить",
            command=self.send_message_handler,
            bg=self.colors['button_bg'],
            fg=self.colors['text'],
            activebackground=self.colors['button_active'],
            activeforeground=self.colors['text'],
            relief='flat'
        )
        self.send_button.pack(side=tk.RIGHT)

        # Запускаем поток для опроса сервера
        self.poll_thread = threading.Thread(target=self.poll_messages_worker, daemon=True)
        self.poll_thread.start()

        # Запускаем периодическую проверку очереди сообщений
        self.process_message_queue()

    def setup_dark_theme(self):
        """Настройка цветов темной темы"""
        self.colors = {
            'bg': '#2b2b2b',  # Темный фон
            'text': '#ffffff',  # Белый текст
            'entry_bg': '#3c3c3c',  # Темный фон поля ввода
            'button_bg': '#404040',  # Темный фон кнопки
            'button_active': '#505050',  # Активный цвет кнопки
            'select_bg': '#555555',  # Цвет выделения
        }

        # Устанавливаем цвет фона главного окна
        self.master.configure(bg=self.colors['bg'])

    def send_message_handler(self, event=None):
        """Обрабатывает отправку сообщения в отдельном потоке"""
        message = self.entry.get().strip()
        if message:
            self.entry.delete(0, tk.END)
            threading.Thread(target=self.send_message_worker, args=(message,), daemon=True).start()

    def send_message_worker(self, message):
        """Рабочая функция для отправки сообщения в отдельном потоке"""
        try:
            self.msg_ctrl.send_message(message)
        except Exception as e:
            print(f"Ошибка отправки: {e}")

    def poll_messages_worker(self):
        """Рабочая функция для опроса сервера в отдельном потоке"""
        while self.polling_active:
            try:
                new_messages = self.msg_ctrl.receive_message()
                if new_messages:
                    self.message_queue.put(new_messages)
            except Exception as e:
                print(f"Ошибка при опросе сервера: {e}")
            time.sleep(1)

    def process_message_queue(self):
        """Периодически проверяет очередь и обновляет UI в главном потоке"""
        try:
            while True:
                messages = self.message_queue.get_nowait()
                self.update_chat_display(messages)
        except queue.Empty:
            pass
        self.master.after(100, self.process_message_queue)

    def update_chat_display(self, messages):
        """Обновляет окно чата новыми сообщениями"""
        self.chat_history.config(state='normal')
        self.chat_history.configure(autoseparators=False)

        for msg in messages:
            # Форматируем сообщение с цветовым кодированием
            nickname = msg.get('nickname', 'Unknown')
            time_str = msg.get('time', '??:??')
            text = msg.get('text', '')

            # Добавляем сообщение
            formatted_msg = f"[{time_str}] {nickname}: {text}\n"
            self.chat_history.insert(tk.END, formatted_msg)

        self.chat_history.configure(autoseparators=True)
        self.chat_history.see(tk.END)
        self.chat_history.config(state='disabled')

    def on_closing(self):
        """Вызывается при закрытии приложения"""
        self.polling_active = False
        self.master.destroy()


# Запуск приложения
if __name__ == "__main__":
    root = tk.Tk()
    app = SimpleChatApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)

    style = ttk.Style()
    style.theme_use('clam')
    style.configure("Vertical.TScrollbar",
                    background='#404040',
                    darkcolor='#404040',
                    lightcolor='#404040',
                    troughcolor='#2b2b2b',
                    bordercolor='#2b2b2b',
                    arrowcolor='#ffffff')

    root.mainloop()

""" # Дополнительно: добавляем поддержку темной темы для скроллбара
style = tk.ttk.Style()
style.theme_use('clam')
style.configure("Vertical.TScrollbar",
                background='#404040',
                darkcolor='#404040',
                lightcolor='#404040',
                troughcolor='#2b2b2b',
                bordercolor='#2b2b2b',
                arrowcolor='#ffffff')"""

# root.mainloop()