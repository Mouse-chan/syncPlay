from datetime import datetime
import customtkinter as ctk
import requests
import threading
import time
import json

SERVER_URL = "https://nezumi403.pythonanywhere.com"


def a_origin_els(a, b):
    """Оптимизированная версия функции поиска новых элементов"""
    # Используем множества для быстрого сравнения
    set_b = set(b)
    return [item for item in a if item not in set_b]


class MessengerApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.MESSAGES = []
        # Настройка окна и темы
        self.title("Чатик")
        self.geometry("350x550")
        ctk.set_appearance_mode("dark")

        # Переменные для хранения состояния
        self.last_check_time = datetime.now()
        self.is_running = True
        self.last_message_count = 0  # Счетчик сообщений для оптимизации
        self.session = requests.Session()  # Переиспользуемая сессия

        # Создание элементов интерфейса
        self.create_widgets()

        # Запуск фонового потока для проверки сообщений
        self.start_message_checker_thread()

    def create_widgets(self):
        self.text_display = ctk.CTkTextbox(self, state="disabled")
        self.text_display.pack(fill="both", expand=True, padx=10, pady=(10, 5))

        # Фрейм для поля ввода и кнопки
        self.input_frame = ctk.CTkFrame(self)
        self.input_frame.pack(fill="x", padx=10, pady=5)

        # Поле для ввода сообщения
        self.entry_input = ctk.CTkEntry(self.input_frame, placeholder_text="Тыкай кнопочки...")
        self.entry_input.pack(side="left", fill="x", expand=True, padx=(0, 5))
        self.entry_input.bind("<Return>", self.send_message_handler)

        # Кнопка отправки
        self.button_send = ctk.CTkButton(self.input_frame, text="➤",
                                         width=60, command=self.send_message_handler)
        self.button_send.pack(side="right")

    def send_message_handler(self, event=None):
        """Обработчик нажатия кнопки 'Отправить' или клавиши Enter."""
        message = self.entry_input.get().strip()
        if message:
            msg_with_time = f'[{time.strftime("%H:%M:%S")}]  {message}'
            # Запускаем отправку в отдельном потоке чтобы не блокировать GUI
            threading.Thread(target=self.send_message, args=(msg_with_time,), daemon=True).start()
            self.entry_input.delete(0, "end")
            # Сразу показываем свое сообщение в чате
            self.after(0, self.add_message_to_display, f"{msg_with_time} (отправляется...)")
        return None

    def send_message(self, message):
        """Отправка сообщения в отдельном потоке"""
        try:
            response = self.session.post(f"{SERVER_URL}/send",
                                         json={'msg': message},
                                         timeout=3)  # Уменьшаем таймаут
            return True
        except Exception as e:
            # Обновляем статус сообщения в GUI
            self.after(0, self.update_message_status, message, "❌ Ошибка отправки")
            return False

    def update_message_status(self, original_message, status):
        """Обновляет статус отправленного сообщения"""
        self.text_display.configure(state="normal")
        # Находим и заменяем сообщение со статусом отправки
        content = self.text_display.get("1.0", "end")
        if "(отправляется...)" in content:
            lines = content.split("\n")
            for i, line in enumerate(lines):
                if "(отправляется...)" in line:
                    lines[i] = line.replace("(отправляется...)", status)
                    break
            self.text_display.delete("1.0", "end")
            self.text_display.insert("1.0", "\n".join(lines))
        self.text_display.see("end")
        self.text_display.configure(state="disabled")

    def add_message_to_display(self, message):
        """Добавляет сообщение в текстовую область."""
        self.text_display.configure(state="normal")
        self.text_display.insert("end", message + "\n")
        self.text_display.see("end")
        self.text_display.configure(state="disabled")

    def check_for_new_messages(self):
        """Оптимизированная проверка новых сообщений"""
        try:
            # Проверяем только если изменилось количество сообщений
            response = self.session.get(f"{SERVER_URL}/receive", timeout=3)
            data = response.json()

            if not data.get('msg'):
                return None

            current_messages = data['msg']

            # Быстрая проверка по количеству сообщений
            if len(current_messages) == len(self.MESSAGES):
                return None

            new_mess = a_origin_els(current_messages, self.MESSAGES)
            if new_mess:
                self.MESSAGES = current_messages
                return new_mess
        except Exception as e:
            print(f"Ошибка при проверке сообщений: {e}")
        return None

    def start_message_checker_thread(self):
        """Оптимизированный поток проверки сообщений"""

        def message_checker_loop():
            last_check = time.time()
            error_count = 0

            while self.is_running:
                try:
                    current_time = time.time()
                    # Проверяем не чаще чем раз в секунду (можно регулировать)
                    if current_time - last_check >= 1.0:
                        new_messages = self.check_for_new_messages()
                        if new_messages:
                            for ms in new_messages:
                                self.after(0, self.add_message_to_display, f"{ms}")
                        last_check = current_time
                        error_count = 0  # Сбрасываем счетчик ошибок при успехе

                    time.sleep(0.1)  # Короткая пауза для снижения нагрузки

                except Exception as e:
                    error_count += 1
                    print(f"Ошибка в потоке проверки: {e}")
                    # Увеличиваем паузу при множественных ошибках
                    time.sleep(min(error_count * 2, 10))

        thread = threading.Thread(target=message_checker_loop, daemon=True)
        thread.start()

    def on_closing(self):
        """Обработчик закрытия окна."""
        self.is_running = False
        self.session.close()  # Закрываем сессию
        self.destroy()


def main():
    app = MessengerApp()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()


if __name__ == '__main__':
    main()