import tkinter as tk
from tkinter import scrolledtext, filedialog
import threading
import queue
import time

from player_controller import PlayerCtrl
from messages_controller import MessagesCtrl
from static import str_time_to_ms, is_admin_user_id
from static import decrypt_message
from static import encrypt_message


class ChatApp:
    def __init__(self, master):
        self.master = master
        master.title("Чатик")
        master.geometry("400x500")

        self.msg_ctrl = MessagesCtrl()
        self.message_queue = queue.Queue()  # Очередь для новых сообщений

        self.player_ctrl = PlayerCtrl()

        # Флаг для управления потоком опроса
        self.polling_active = True

        # Проверяем соединение с сервером при запуске
        if not self.msg_ctrl.check_connection():
            print("Внимание: проблемы с соединением")

        # Создаем виджет для отображения истории сообщений
        self.chat_history: scrolledtext.ScrolledText = scrolledtext.ScrolledText(master, state='disabled', wrap=tk.WORD)
        self.chat_history.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        # Создаем фрейм для размещения поля ввода и кнопки отправки
        self.input_frame = tk.Frame(master)
        self.input_frame.pack(padx=10, pady=10, fill=tk.X)

        # Поле для ввода сообщения
        self.entry = tk.Entry(self.input_frame)
        self.entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.entry.bind("<Return>", self.send_message_handler)

        # Кнопка загрузки видео
        self.load_video_btn = tk.Button(
            self.input_frame,
            text="Загрузить",
            command=self.load_video
        )
        self.load_video_btn.pack(side=tk.RIGHT, padx=5)

        # Кнопка отправки сообщения
        self.send_button = tk.Button(self.input_frame, text="Отправить", command=self.send_message_handler)
        self.send_button.pack(side=tk.RIGHT, padx=5)

        # Запускаем поток для отправки сообщений
        self.send_thread = None

        # Запускаем поток для опроса сервера
        self.poll_thread = threading.Thread(target=self.poll_messages_worker, daemon=True)
        self.poll_thread.start()

        # Запускаем периодическую проверку очереди сообщений
        #self.process_message_queue()

        self.send_message_handler(message='*Пoдключился*')
        time.sleep(0.02)
        self.send_message_handler(message='-pass ' + self.msg_ctrl.user_id)
        time.sleep(0.02)
        # Запускаем периодическую проверку очереди сообщений
        self.process_message_queue()

    def send_message_handler(self, event=None, message=None):
        """Обрабатывает отправку сообщения в отдельном потоке"""
        if not message:
            message = self.entry.get().strip()
        if message:
            # Очищаем поле ввода сразу (не дожидаясь отправки)
            self.entry.delete(0, tk.END)

            # Отправляем в отдельном потоке, чтобы не блокировать интерфейс
            self.send_thread = threading.Thread(target=self.send_message_worker, args=(message,), daemon=True)
            self.send_thread.start()

    def send_message_worker(self, message):
        """Рабочая функция для отправки сообщения в отдельном потоке"""
        try:
            encrypt = encrypt_message(message, self.msg_ctrl.password)
            self.msg_ctrl.send_message(encrypt)
        except Exception as e:
            print(f"Ошибка отправки: {e}")

    def poll_messages_worker(self):
        """Рабочая функция для опроса сервера в отдельном потоке"""
        while self.polling_active:
            try:
                new_messages = self.msg_ctrl.receive_message()
                if new_messages:
                    # Помещаем сообщения в очередь вместо прямого обновления UI
                    self.message_queue.put(new_messages)
            except Exception as e:
                print(f"Ошибка при опросе сервера: {e}")

            time.sleep(1)

    def process_message_queue(self):
        """Периодически проверяет очередь и обновляет UI в главном потоке"""
        try:
            # Обрабатываем все сообщения в очереди
            while True:
                event = self.update_player()
                self.event_manage(event)

                messages = self.message_queue.get_nowait()
                self.update_chat_display(messages)
                self.check_chat_commands(messages)
        except queue.Empty:
            pass

        # Планируем следующую проверку через 100 мс
        self.master.after(100, self.process_message_queue)

    def event_manage(self, event):
        if not event:
            return
        self.send_message_handler(message=event)

    def update_chat_display(self, messages):
        """Обновляет окно чата новыми сообщениями"""
        self.chat_history.config(state='normal')

        # Более эффективное обновление - отключаем автообновление во время вставки
        self.chat_history.configure(autoseparators=False)

        for msg in messages:
            text_msg = msg.get('text', '')
            decrypt = decrypt_message(text_msg, self.msg_ctrl.password)
            if decrypt is not None and ('-pass' not in decrypt or is_admin_user_id(self.msg_ctrl.user_id)):
                if is_admin_user_id(self.msg_ctrl.user_id):
                    formatted_msg = f"[{msg.get('time', '??:??:??')}] {msg.get('nickname', 'Unknown')}({msg.get('user')}): {decrypt}\n"
                else:
                    formatted_msg = f"[{msg.get('time', '??:??:??')}] {msg.get('nickname', 'Unknown')}: {decrypt}\n"
                self.chat_history.insert(tk.END, formatted_msg)

        # Включаем обратно автообновление
        self.chat_history.configure(autoseparators=True)
        self.chat_history.see(tk.END)
        self.chat_history.config(state='disabled')

    def update_player(self):
        return self.player_ctrl.update()

    def check_chat_commands(self, messages):
        # TODO: обработчик команд, с учётом задержки

        for msg in messages:
            msg_text: str = msg.get('text', None)
            msg_text: str = decrypt_message(msg_text, self.msg_ctrl.password)
            msg_user = msg.get('user')
            msg_time = msg.get('time')
            msg_time_ms = str_time_to_ms(msg_time)
            cur_time_ms = str_time_to_ms(time.strftime("%H:%M:%S"))
            if not msg_text or msg_text[0] != "-" or abs(cur_time_ms - msg_time_ms) > 30000:
                continue

            if msg_user == self.msg_ctrl.user_id:
                if msg_text[:5] == '-nick' or msg_text[:3] == '-n ':
                    new_nick = msg_text.split(' ')[1]
                    self.msg_ctrl.nickname = new_nick
                elif msg_text[:5] == '-load' or msg_text[:3] == '-l ':
                    new_video_path = msg_text.replace(' ', '*', 1).split('*')[1]
                    self.player_ctrl.close_player()
                    self.player_ctrl = PlayerCtrl()
                    self.player_ctrl.set_new_video(new_video_path)
                elif msg_text[:5] == '-pass':
                    new_pass = msg_text.split(' ')[1]
                    if new_pass != self.msg_ctrl.password and abs(cur_time_ms - msg_time_ms) < 10000:
                        self.msg_ctrl.password = new_pass
                        self.chat_history.config(state='normal')
                        self.chat_history.delete(1.0, tk.END)
                        self.chat_history.config(state='disabled')
                        self.msg_ctrl.MESSAGES = []
                        if new_pass == 'none':
                            self.send_message_handler(message=f'*Пoдключился*')
                        else:
                            self.send_message_handler(message=f'*Пoдключился в {new_pass}*')

                elif msg_text == '-exit' or msg_text == '-e':
                    self.on_closing()
            if msg_text[:5] == '-play' or msg_text[:3] == '-p ':
                cmd_time = msg_text.split(' ')[1]
                self.player_ctrl.set_time(cmd_time)
                self.player_ctrl.play()
            elif msg_text[:5] == '-stop' or msg_text[:3] == '-s ':
                cmd_time = msg_text.split(' ')[1]
                self.player_ctrl.set_time(cmd_time)
                self.player_ctrl.pause()
            elif msg_text[:5] == '-time' or msg_text[:3] == '-t ':
                cmd_time = msg_text.split(' ')[1]
                self.player_ctrl.set_time(cmd_time)
            elif msg_text[:5] == '-kick':
                kick_user = msg_text.split(' ')[1]
                if is_admin_user_id(msg_user) and kick_user == self.msg_ctrl.user_id:
                    self.on_closing()

    def load_video(self):
        """Открывает диалог выбора видеофайла и загружает выбранное видео"""
        # Открываем диалог выбора файла
        file_path = filedialog.askopenfilename(
            title="Выберите видеофайл",
            filetypes=(
                ("Видеофайлы", "*.mp4 *.avi *.mkv *.mov *.flv"),
                ("Все файлы", "*.*")
            )
        )

        if file_path:
            self.send_message_handler(message=f"-load {file_path}")
            self.send_message_handler('-stop 00:00:00')

    def on_closing(self):
        """Вызывается при закрытии приложения"""
        try:
            self.polling_active = False

            try:
                encrypt = encrypt_message(f'*Oтключился*', self.msg_ctrl.password)
                self.msg_ctrl.send_message(encrypt)
                print("Сообщение об отключении отправлено")
            except Exception as e:
                print(f"Не удалось отправить сообщение об отключении: {e}")

            if hasattr(self, 'player_ctrl'):
                self.player_ctrl.close_player()
            self.master.destroy()

        except Exception as e:
            print(f"Ошибка при закрытии: {e}")
            self.master.destroy()


# Запуск приложения
if __name__ == "__main__":
    root = tk.Tk()
    app = ChatApp(root)
    root.protocol("WM_DELETE_WINDOW", lambda: app.on_closing())
    root.mainloop()