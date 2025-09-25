# player_controller

import vlc
import time
import keyboard
import win32gui
import win32process
import os


def is_window_active():
    try:
        window = win32gui.GetForegroundWindow()
        _, active_pid = win32process.GetWindowThreadProcessId(window)
        current_pid = os.getpid()
        return active_pid == current_pid
    except:
        return False

class PlayerCtrl:
    def __init__(self, video_path=None):
        self.video_path = video_path
        self._instance: vlc.Instance = vlc.Instance("--sub-source=marq")
        self._player: vlc.MediaPlayer = self._instance.media_player_new()

        if self.video_path:
            self.set_new_video(self.video_path)

    def set_new_video(self, video_path):
        media = self._instance.media_new(video_path, "sub-filter=marq")
        self._player.set_media(media)
        # self._player.set_video_title_display(10, 1000)
        self._player.play()

        time.sleep(0.1)

        self._player.video_set_marquee_int(1, 1)
        self._player.video_set_marquee_int(6, 8)
        self._player.video_set_marquee_int(5, 24)  # Размер шрифта (в пикселях)
        self._player.video_set_marquee_int(2, 0xFFFFFF)  # Цвет текста (белый)
        self._player.video_set_marquee_int(3, 255)  # Непрозрачность текста (0-255)
        self._player.video_set_marquee_int(7, 0)

    def play(self):
        self._player.play()

    def pause(self):
        self._player.pause()

    def update(self):
        self.event_handler()
        if self._player.is_playing():
            current_time = time.strftime('%H:%M:%S', time.gmtime(self._player.get_time() / 1000))
            self._player.video_set_marquee_string(0, 'Test')
            print(current_time)

    def event_handler(self):
        # Обработчик событий в основном цикле
        if not is_window_active():
            return

        if keyboard.is_pressed('esc'):
            self._player.stop()
            time.sleep(0.2)
        elif keyboard.is_pressed('left'):
            self._player.set_time(max(0, self._player.get_time()-10000))
            time.sleep(0.2)
        elif keyboard.is_pressed('right'):
            self._player.set_time(min(self._player.get_length()-1, self._player.get_time() + 10000))
            time.sleep(0.2)
        elif keyboard.is_pressed('shift+right'):
            self._player.set_time(min(self._player.get_length()-1, self._player.get_time() + 1000))
            time.sleep(0.2)
        elif keyboard.is_pressed('space'):
            if str(self._player.get_state()) == 'State.Playing':
                self._player.pause()
            else:
                print(self._player.get_state())
                self._player.play()
            time.sleep(0.2)

        elif keyboard.is_pressed('='):
            d = self._player.audio_get_track_description()
            audios = []
            for i in range(len(d)):
                audios.append(d[i][0])
            cur = audios.index(self._player.audio_get_track())
            if cur == len(audios)-1:
                self._player.audio_set_track(audios[1])
            else:
                self._player.audio_set_track(audios[cur+1])
            time.sleep(0.2)

        elif keyboard.is_pressed('-'):
            d = self._player.video_get_spu_description()
            subs = []
            for i in range(len(d)):
                subs.append(d[i][0])
            cur = subs.index(self._player.video_get_spu())
            if cur == len(subs)-1:
                self._player.video_set_spu(subs[0])
            else:
                self._player.video_set_spu(subs[cur+1])
            time.sleep(0.2)