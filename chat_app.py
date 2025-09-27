import tkinter as tk
from tkinter import scrolledtext
import threading
import queue
import time

from player_controller import PlayerCtrl
from messages_controller import MessagesCtrl
from static import str_time_to_ms


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

        # Кнопка отправки сообщения
        self.send_button = tk.Button(self.input_frame, text="Отправить", command=self.send_message_handler)
        self.send_button.pack(side=tk.RIGHT)

        # Запускаем поток для отправки сообщений
        self.send_thread = None

        # Запускаем поток для опроса сервера
        self.poll_thread = threading.Thread(target=self.poll_messages_worker, daemon=True)
        self.poll_thread.start()

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
            self.msg_ctrl.send_message(message)
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

            # Пауза между опросами
            time.sleep(1)  # Уменьшил интервал опроса для более быстрого обновления

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
            formatted_msg = f"[{msg.get('time', '??:??')}] {msg.get('nickname', 'Unknown')}: {msg.get('text', '')}\n"
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
            msg_user = msg.get('user')
            msg_time = msg.get('time')
            msg_time_ms = str_time_to_ms(msg_time)
            cur_time_ms = str_time_to_ms(time.strftime("%H:%M:%S"))
            if not msg_text or msg_text[0] != "-" or abs(cur_time_ms-msg_time_ms) > 60000:
                continue

            if msg_user == self.msg_ctrl.user_id:
                if msg_text[:5] == '-nick' or msg_text[:2] == '-n':
                    new_nick = msg_text.split(' ')[1]
                    self.msg_ctrl.nickname = new_nick
                if msg_text[:5] == '-load' or msg_text[:2] == '-l':
                    new_video_path = msg_text.replace(' ', '*', 1).split('*')[1]
                    self.player_ctrl.close_player()
                    self.player_ctrl = PlayerCtrl()
                    self.player_ctrl.set_new_video(new_video_path)
            if msg_text[:5] == '-play' or msg_text[:2] == '-p':
                cmd_time = msg_text.split(' ')[1]
                self.player_ctrl.set_time(cmd_time)
                self.player_ctrl.play()
            elif msg_text[:5] == '-stop' or msg_text[:2] == '-s':
                cmd_time = msg_text.split(' ')[1]
                self.player_ctrl.set_time(cmd_time)
                self.player_ctrl.pause()
            elif msg_text[:5] == '-time' or msg_text[:2] == '-t':
                cmd_time = msg_text.split(' ')[1]
                self.player_ctrl.set_time(cmd_time)


    def on_closing(self):
        """Вызывается при закрытии приложения"""
        self.polling_active = False
        self.master.destroy()


# Запуск приложения
if __name__ == "__main__":
    root = tk.Tk()
    app = ChatApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()