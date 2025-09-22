# client.py
import requests
import time
import json

SERVER_URL = "https://nezumi403.pythonanywhere.com"


def send_message(message):
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
    return False


def receive_message():
    try:
        print("🔄 Проверяю новые сообщения...")
        response = requests.get(f"{SERVER_URL}/receive", timeout=5)
        print(f"✅ Получен ответ. Статус: {response.status_code}")
        data = response.json()
        if data.get('msg'):
            print(f"📨 Новое сообщение: {data['msg']}")
        else:
            print("📭 Сообщений нет")
        return data.get('msg')
    except requests.exceptions.Timeout:
        print("❌ Таймаут при получении")
    except requests.exceptions.ConnectionError:
        print("❌ Ошибка соединения при получении")
    except Exception as e:
        print(f"❌ Ошибка получения: {e}")
    return None


def test_connection():
    """Тест соединения с сервером"""
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
        return False

def main():
    # Запуск теста соединения
    if not test_connection():
        print("Прерываю работу...")
        exit()

    print("\n💬 Чат запущен! Вводите сообщения:")
    while True:
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

        time.sleep(1)

if __name__ == '__main__':
    main()