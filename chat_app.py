import tkinter as tk
from tkinter import scrolledtext
import threading
import queue
import time
from collections import deque

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
        self.last_message_time = 0  # Временная метка последнего сообщения
        self.message_batch = deque()  # Буфер для батчинга сообщений

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
        last_poll_time = 0
        poll_interval = 0.3  # Уменьшенный интервал опроса

        while self.polling_active:
            current_time = time.time()

            # Регулируем частоту опросов в зависимости от нагрузки
            if current_time - last_poll_time >= poll_interval:
                try:
                    new_messages = self.msg_ctrl.receive_message()
                    if new_messages:
                        current_time = time.time()
                        # Добавляем временную метку и пакетируем сообщения
                        for msg in new_messages:
                            msg['_timestamp'] = current_time
                        self.message_queue.put(new_messages)
                        last_poll_time = current_time
                except Exception as e:
                    print(f"Ошибка при опросе сервера: {e}")
                    # Увеличиваем интервал при ошибках
                    poll_interval = min(2.0, poll_interval * 1.5)
                else:
                    # Постепенно уменьшаем интервал при успешных опросах
                    poll_interval = max(0.1, poll_interval * 0.9)

            # Небольшая пауза для снижения нагрузки на CPU
            time.sleep(0.01)

    def process_message_queue(self):
        """Периодически проверяет очередь и обновляет UI в главном потоке"""
        try:
            # Обрабатываем сообщения пачками
            processed_count = 0
            max_messages_per_frame = 10  # Максимальное количество сообщений за один кадр

            while processed_count < max_messages_per_frame:
                # Обновляем состояние плеера
                event = self.update_player()
                if event:
                    self.event_manage(event)

                # Получаем сообщения
                try:
                    messages = self.message_queue.get_nowait()
                    if messages:
                        # Добавляем сообщения в буфер
                        self.message_batch.extend(messages)
                        processed_count += len(messages)
                except queue.Empty:
                    break

            # Обрабатываем накопленные сообщения
            if self.message_batch:
                # Сортируем по времени, если это важно
                self.message_batch = list(self.message_batch)
                self.message_batch.sort(key=lambda x: x.get('_timestamp', 0))
                self.update_chat_display(self.message_batch)
                self.check_chat_commands(self.message_batch)
                self.message_batch = deque()

        except Exception as e:
            print(f"Ошибка при обработке очереди: {e}")
        finally:
            # Планируем следующую проверку с динамическим интервалом
            next_check = 50 if self.message_queue.qsize() > 0 else 100
            self.master.after(next_check, self.process_message_queue)

    def event_manage(self, event):
        if not event:
            return
        self.send_message_handler(message=event)

    def update_chat_display(self, messages):
        """Обновляет окно чата новыми сообщениями с оптимизацией производительности"""
        if not messages:
            return

        self.chat_history.config(state='normal')

        try:
            # Отключаем обновление виджета во время вставки
            self.chat_history.configure(autoseparators=False)
            self.chat_history.configure(state='normal')

            # Собираем все сообщения в один буфер
            buffer = []
            for msg in messages:
                time_str = msg.get('time', '??:??')
                nickname = msg.get('nickname', 'Unknown')
                text = msg.get('text', '')
                buffer.append(f"[{time_str}] {nickname}: {text}\n")

            # Вставляем все сообщения за один вызов
            if buffer:
                self.chat_history.insert(tk.END, ''.join(buffer))
                self.chat_history.see(tk.END)

        except Exception as e:
            print(f"Ошибка при обновлении чата: {e}")

        finally:
            # Восстанавливаем настройки
            self.chat_history.configure(autoseparators=True)
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

            #if True:
            if msg_user == self.msg_ctrl.user_id:
                if msg_text[:5] == '-nick' or msg_text[:2] == '-n':
                    new_nick = msg_text.split(' ')[1]
                    self.msg_ctrl.nickname = new_nick
                if msg_text[:5] == '-load' or msg_text[:2] == '-l':
                    new_video_path = msg_text.replace(' ', '*', 1).split('*')[1]
                    self.player_ctrl.close_player()
                    self.player_ctrl = PlayerCtrl()
                    self.player_ctrl.set_new_video(new_video_path)
            #else:
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