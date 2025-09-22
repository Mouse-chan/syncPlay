from datetime import datetime

import customtkinter as ctk
import requests
import threading
import time


SERVER_URL = "https://nezumi403.pythonanywhere.com"

def a_origin_els(a, b):
    res = []
    for i in range(len(a)):
        if a[i] not in b:
            res.append(a[i])
    return res

class MessengerApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.MESSAGES = []
        # Настройка окна и темы
        self.title("Чатик")
        self.geometry("350x550")
        ctk.set_appearance_mode("dark")  # Возможные варианты: "dark", "light", "system"

        # Переменные для хранения состояния
        self.last_check_time = datetime.now()
        self.is_running = True

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
        self.entry_input.bind("<Return>", self.send_message_handler)  # Отправка по Enter

        # Кнопка отправки
        self.button_send = ctk.CTkButton(self.input_frame, text="➤",
            width=60, command=self.send_message_handler)
        self.button_send.pack(side="right")

    def send_message_handler(self, event=None):
        """Обработчик нажатия кнопки 'Отправить' или клавиши Enter."""
        message = self.entry_input.get().strip()
        if message:
            msg_with_time = '[' + str(time.strftime("%H:%M:%S")) + ']  ' + message
            # self.add_message_to_display(msg_with_time)
            self.entry_input.delete(0, "end")
            self.send_message(msg_with_time)
            #self.send_message(msg_with_time)
            return msg_with_time
        return None

    def send_message(self, message):
        try:
            response = requests.post(f"{SERVER_URL}/send",
                                     json={'msg': message},
                                     timeout=5)
            return True
        except Exception as e:
            return False

    def add_message_to_display(self, message):
        """Добавляет сообщение в текстовую область."""
        self.text_display.configure(state="normal")  # Включаем редактирование
        self.text_display.insert("end", message + "\n")  # Добавляем текст
        self.text_display.see("end")  # Прокручиваем к последнему сообщению
        self.text_display.configure(state="disabled")  # Снова отключаем редактирование

    def check_for_new_messages(self):
        """Проверяет наличие новых сообщений."""
        #print("🔄 Проверяю новые сообщения...")
        response = requests.get(f"{SERVER_URL}/receive", timeout=5)
        # print(f"✅ Получен ответ. Статус: {response.status_code}")
        data = response.json()

        if data['msg'] != self.MESSAGES and data['msg']:
            new_mess = a_origin_els(data['msg'], self.MESSAGES)
            """for ms in new_mess:
                print(f"📨: {ms}\n")"""
            self.MESSAGES = data['msg']
            return new_mess
        return None

    def update_messages(self):
        """Функция обновления, которая проверяет новые сообщения."""
        if not self.is_running:
            return

        try:
            # Проверяем наличие новых сообщений
            new_messages = self.check_for_new_messages()

            if new_messages:
                # Добавляем новое сообщение в интерфейс (потокобезопасно)
                for ms in new_messages:
                    self.after(0, self.add_message_to_display, f"{ms}")

        except Exception as e:
            print(f"Ошибка при проверке сообщений: {e}")

        # Планируем следующую проверку через 1 секунду
        if self.is_running:
            self.after(2000, self.update_messages)

    def start_message_checker(self):
        """Запускает проверку сообщений в основном потоке GUI."""
        # Запускаем первую проверку через 1 секунду
        self.after(2000, self.update_messages)

    def start_message_checker_thread(self):
        """Альтернативный вариант: запуск в отдельном потоке."""

        def message_checker_loop():
            while self.is_running:
                try:
                    new_messages = self.check_for_new_messages()
                    if new_messages:
                        for ms in new_messages:
                            self.after(0, self.add_message_to_display, f"Система: {ms}")
                except Exception as e:
                    print(f"Ошибка в потоке проверки: {e}")
                time.sleep(1)  # Проверка каждые 2 секунды

        thread = threading.Thread(target=message_checker_loop, daemon=True)
        thread.start()

    def on_closing(self):
        """Обработчик закрытия окна."""
        self.is_running = False
        self.destroy()

"""def send_message(message):
    try:
        print(f"🔄 Пытаюсь отправить: '{message}'")
        response = requests.post(f"{SERVER_URL}/send",
                                 json={'msg': message},
                                 timeout=5)
        print(f"✅ Отправлено! Статус: {response.status_code}")
        return True
    except requests.exceptions.Timeout:
        print("❌ Таймаут при отправке")
    except requests.exceptions.ConnectionError:
        print("❌ Ошибка соединения при отправке")
    except Exception as e:
        print(f"❌ Ошибка отправки: {e}")
    return False"""


"""def test_connection():
    Тест соединения с сервером
    try:
        print("🧪 Тестирую соединение с сервером...")
        response = requests.get(f"{SERVER_URL}/receive", timeout=10)
        print(f"✅ Сервер отвечает! Статус: {response.status_code}")
        print(f"📋 Ответ сервера: {response.text}")
        return True
    except Exception as e:
        print(f"❌ Не могу подключиться к серверу: {e}")
        print("Проверьте:")
        print("1. Правильный ли URL?")
        print("2. Активен ли веб-сайт на PythonAnywhere?")
        print("3. Есть ли интернет соединение?")
        return False"""

def main():
    """# Запуск теста соединения
    if not test_connection():
        print("Прерываю работу...")
        exit()

    print("\n💬 Чат запущен! Вводите сообщения:")"""

    app = MessengerApp()
    app.mainloop()

    """while True:
        message = input("Ваше сообщение (или 'exit' для выхода): ")
        if message == 'exit':
            break

        if send_message(message):
            print("✓ Сообщение отправлено на сервер")

        # Даем время серверу обработать
        time.sleep(1)

        received = receive_message()
        if received:
            print(f"👤 Получено: {received}")

        time.sleep(1)"""

if __name__ == '__main__':
    main()
