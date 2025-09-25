# main.py

import time

from messages_controller import MessagesCtrl
from player_controller import PlayerCtrl


def main():
    msg_ctrl = MessagesCtrl()
    test_message(msg_ctrl)

    play_ctrl = PlayerCtrl()
    player_test(play_ctrl)


def test_message(msg_ctrl):
    if not msg_ctrl.check_connection():
        exit()

    while True:
        try:
            time.sleep(0.1)

            m = input(": ")
            msg_ctrl.send_message(m)

            time.sleep(0.1)

            msgs = msg_ctrl.receive_message()

            for i in range(len(msgs)):
                print(f'[{msgs[i]['time']}] {msgs[i]['nickname']}: {msgs[i]['text']}\n')
        except Exception as e:
            print(f"❌ Ошибка в тесте сообщений: {e}")

def player_test(play_ctrl):
    play_ctrl.set_new_video("C:\\Users\\belak\\Videos\\Мои видео\\Аниме\\Агент времени\\Link Click 1\\02.mkv")
    while True:
        play_ctrl.update()

if __name__ == '__main__':
    main()
