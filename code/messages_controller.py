# messages_controller.py

import hashlib
import os
import requests
from datetime import datetime


def a_origin_els(a, b):
    """Функция поиска новых элементов"""
    return [item for item in a if item not in b]

class MessagesCtrl:
    SERVER_URL = "https://nezumi403.pythonanywhere.com"
    MESSAGES = []

    def __init__(self):  # TODO: delite if not use
        self.user_id = str(int(hashlib.sha256(os.getlogin().encode()).hexdigest(), 16))[:5]
        self.nickname = 'user' + self.user_id
        self.password = 'none'

    def check_connection(self):
        try:
            print("🧪 Тестирую соединение с сервером...")
            response = requests.get(f"{self.SERVER_URL}/receive", timeout=10)
            print(f"✅ Сервер отвечает! Статус: {response.status_code}")
            return True
        except Exception as e:
            print(f"❌ Не могу подключиться к серверу: {e}")
            return False

    def send_message(self, message):
        try:
            time = datetime.now()
            new_msg = {
                'user': self.user_id,
                'nickname': self.nickname,
                'time': str(time.strftime("%H:%M:%S:%f")[:-3]),
                'text': message
            }
            response = requests.post(f"{self.SERVER_URL}/send",
                                     json={'msg': new_msg},
                                     timeout=5)
            return response.status_code
        except Exception as e:
            print(f"❌ Ошибка отправки: {e}")
            return e


    def receive_message(self):
        try:
            response = requests.get(f"{self.SERVER_URL}/receive", timeout=5)
            data = response.json()

            if data['msg'] != self.MESSAGES and data['msg']:
                new_mess = a_origin_els(data['msg'], self.MESSAGES)
                self.MESSAGES = data['msg']
                return new_mess
            return None
        except Exception as e:
            print(f"❌ Ошибка получения: {e}")
