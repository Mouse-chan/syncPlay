import time

from messages_controller import MessagesCtrl


def main():
    msg_ctrl = MessagesCtrl()

    if not msg_ctrl.check_connection():
        exit()

    while True:
        time.sleep(0.1)

        m = input(": ")
        msg_ctrl.send_message(m)

        time.sleep(0.1)

        msgs = msg_ctrl.receive_message()

        for i in range(len(msgs)):
            print(f'[{msgs[i]['time']}] {msgs[i]['nickname']}: {msgs[i]['text']}\n')


if __name__ == '__main__':
    main()