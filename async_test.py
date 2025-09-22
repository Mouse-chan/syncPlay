# client.py
import asyncio

import aioconsole
import requests
import time
import json

SERVER_URL = "https://nezumi403.pythonanywhere.com"

def a_origin_els(a, b):
    res = []
    for i in range(len(a)):
        if a[i] not in b:
            res.append(a[i])
    return res

async def send_message():
    while True:
        message = await aioconsole.ainput("Введите сообщение: ")
        if message.lower() == 'exit':
            break
        try:
            await aioconsole.aprint(f"🔄 Пытаюсь отправить: '{message}'")
            response = requests.post(f"{SERVER_URL}/send",
                                     json={'msg': '[' + str(time.strftime("%H:%M:%S")) + ']  ' + message},
                                     timeout=5)
            await aioconsole.aprint(f"✅ Отправлено! Статус: {response.status_code}")
            await aioconsole.aprint("✓ Сообщение отправлено на сервер")
        except requests.exceptions.Timeout:
            await aioconsole.aprint("❌ Таймаут при отправке")
        except requests.exceptions.ConnectionError:
            await aioconsole.aprint("❌ Ошибка соединения при отправке")
        except Exception as e:
            await aioconsole.aprint(f"❌ Ошибка отправки: {e}")


async def receive_message():
    MESSAGES = []
    while True:
        time.sleep(3)
        try:
            await aioconsole.aprint("\n🔄 Проверяю новые сообщения...\n")
            response = requests.get(f"{SERVER_URL}/receive", timeout=5)
            #await aioconsole.aprint(f"✅ Получен ответ. Статус: {response.status_code}")
            data = response.json()


            if data['msg'] != MESSAGES and data['msg']:
                new_mess = a_origin_els(data['msg'], MESSAGES)
                #await aioconsole.aprint(f"📨 Новое сообщение: {new_mess}")
                for ms in new_mess:
                    await aioconsole.aprint(f"📨: {ms}\n")
                MESSAGES = data['msg']
            #return data.get('msg')
            """received = data.get('msg')
            if received:
                await aioconsole.aprint(f"👤 Получено: {received}")"""
        except requests.exceptions.Timeout:
            await aioconsole.aprint("❌ Таймаут при получении")
        except requests.exceptions.ConnectionError:
            await aioconsole.aprint("❌ Ошибка соединения при получении")
        except Exception as e:
            await aioconsole.aprint(f"❌ Ошибка получения: {e}")


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

async def main():
    # Запуск теста соединения
    if not test_connection():
        print("Прерываю работу...")
        exit()

    print("\n💬 Чат запущен! Вводите сообщения:")
    await asyncio.gather(
        receive_message(),
        send_message(),
    )

if __name__ == '__main__':
    asyncio.run(main())