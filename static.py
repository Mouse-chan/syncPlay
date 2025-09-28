import time
from cryptography.fernet import Fernet, InvalidToken
import base64
import hashlib

TEST_PATH = "C:\\Users\\belak\\Videos\\Мои видео\\Аниме\\Агент времени\\Link Click 1\\02.mkv"

def str_time_to_ms(str_time):
    h, m, s = map(float, str_time.split(':'))
    time_ms = int((h * 3600 + m * 60 + s) * 1000)
    return time_ms

def ms_to_str_time(time_ms):
    return time.strftime('%H:%M:%S', time.gmtime(time_ms / 1000))



def generate_key_from_password(password):
    """Генерация ключа из пароля"""
    key = base64.urlsafe_b64encode(hashlib.sha256(password.encode()).digest())
    return key

def encrypt_message(message, password):
    """Шифрование сообщения"""
    key = generate_key_from_password(password)
    fernet = Fernet(key)
    encrypted = fernet.encrypt(message.encode())
    return encrypted.decode()

def decrypt_message(encrypted_message, password):
    """Дешифрование сообщения с проверкой пароля"""
    try:
        key = generate_key_from_password(password)
        fernet = Fernet(key)
        decrypted = fernet.decrypt(encrypted_message.encode())
        return decrypted.decode()
    except InvalidToken:
        return None


def is_admin_user_id(user_id):
    return user_id in ['79032', '12617']
