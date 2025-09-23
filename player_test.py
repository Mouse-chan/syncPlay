# path_v = "C:\\Users\\belak\\Videos\\Мои видео\\Аниме\\Агент времени\\Link Click 1\\02.mkv"
# C:\Users\belak\Videos\Мои видео\Аниме\Агент времени\Link Click 1\02.mkv

import vlc
import time
import keyboard
import win32gui
import win32process
import os


def is_window_active():
    try:
        # Получаем ID процесса активного окна
        window = win32gui.GetForegroundWindow()
        _, active_pid = win32process.GetWindowThreadProcessId(window)
        # Получаем ID текущего процесса
        current_pid = os.getpid()
        return active_pid == current_pid
    except:
        return False

def main():
    path_v = 'C:\\Users\\belak\\Videos\\Мои видео\\Аниме\\Агент времени\\Link Click 1\\02.mkv'

    #player: vlc.MediaPlayer = vlc.MediaPlayer(path_v)
    instance = vlc.Instance()
    player = instance.media_player_new()

    media = instance.media_new(path_v)
    player.set_media(media)

    player.set_video_title_display(10, 1000)
    player.play()
    time.sleep(1)
    player.set_time(0)
    player.pause()

    while True:
        # Проверяем, активно ли наше окно
        if not is_window_active():
            time.sleep(0.1)
            continue
            
        #time.sleep(1)
        if keyboard.is_pressed('esc'):
            break
        elif keyboard.is_pressed('left'):
            player.set_time(max(0, player.get_time()-1000))
            time.sleep(0.2)
        elif keyboard.is_pressed('right'):
            player.set_time(min(player.get_length()-1, player.get_time() + 1000))
            time.sleep(0.2)
        elif keyboard.is_pressed('shift+left'):
            player.set_time(max(0, player.get_time()-10000))
            time.sleep(0.2)
        elif keyboard.is_pressed('shift+right'):
            player.set_time(min(player.get_length()-1, player.get_time() + 10000))
            time.sleep(0.2)
        elif keyboard.is_pressed('space'):
            if str(player.get_state()) == 'State.Playing':
                player.pause()
            else:
                print(player.get_state())
                player.play()
            time.sleep(0.2)
        elif keyboard.is_pressed('='):
            d = player.audio_get_track_description()
            audios = []
            for i in range(len(d)):
                audios.append(d[i][0])
            cur = audios.index(player.audio_get_track())
            if cur == len(audios)-1:
                player.audio_set_track(audios[1])
            else:
                player.audio_set_track(audios[cur+1])
            time.sleep(0.2)
        elif keyboard.is_pressed('-'):
            d = player.video_get_spu_description()
            subs = []
            for i in range(len(d)):
                subs.append(d[i][0])
            cur = subs.index(player.video_get_spu())
            if cur == len(subs)-1:
                player.video_set_spu(subs[0])
            else:
                player.video_set_spu(subs[cur+1])
            time.sleep(0.2)

if __name__ == '__main__':
    main()