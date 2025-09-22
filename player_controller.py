# path_v = "C:\\Users\\belak\\Videos\\Мои видео\\Аниме\\Агент времени\\Link Click 1\\02.mkv"
# C:\Users\belak\Videos\Мои видео\Аниме\Агент времени\Link Click 1\02.mkv

import vlc
import time
import keyboard


def main():
    path_v = input('Открыть файл: ')

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
        #time.sleep(1)
        if keyboard.is_pressed('ctrl+esc'):
            break
        elif keyboard.is_pressed('ctrl+left'):
            player.set_time(max(0, player.get_time()-1000))
            time.sleep(0.2)
        elif keyboard.is_pressed('ctrl+right'):
            player.set_time(min(player.get_length()-1, player.get_time() + 1000))
            time.sleep(0.2)
        elif keyboard.is_pressed('ctrl+shift+left'):
            player.set_time(max(0, player.get_time()-10000))
            time.sleep(0.2)
        elif keyboard.is_pressed('ctrl+shift+right'):
            player.set_time(min(player.get_length()-1, player.get_time() + 10000))
            time.sleep(0.2)
        elif keyboard.is_pressed('ctrl+space'):
            if str(player.get_state()) == 'State.Playing':
                player.pause()
            else:
                print(player.get_state())
                player.play()
            time.sleep(0.2)
        elif keyboard.is_pressed('ctrl+='):
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
        elif keyboard.is_pressed('ctrl+-'):
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