import customtkinter as ctk

class MessengerApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Настройка окна и темы
        self.title("Чатик")
        self.geometry("350x550")
        ctk.set_appearance_mode("dark")  # Возможные варианты: "dark", "light", "system"

        # Создание элементов интерфейса
        self.create_widgets()

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
            # 1. Добавляем сообщение в область чата
            self.add_message_to_display(f"Я: {message}")
            # 2. Очищаем поле ввода
            self.entry_input.delete(0, "end")
            # 3. Здесь должна быть твоя логика отправки сообщения в сеть
            # send_message(message)
            return message

    def add_message_to_display(self, message):
        """Добавляет сообщение в текстовую область."""
        self.text_display.configure(state="normal")  # Включаем редактирование
        self.text_display.insert("end", message + "\n")  # Добавляем текст
        self.text_display.see("end")  # Прокручиваем к последнему сообщению
        self.text_display.configure(state="disabled")  # Снова отключаем редактирование


if __name__ == "__main__":
    app = MessengerApp()
    app.mainloop()