import vlc
import time
import keyboard
import win32gui
import win32process
import os
import sys
from typing import Optional


def is_window_active_cached():
    """Кешированная проверка активного окна"""
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
        self._instance: vlc.Instance = vlc.Instance('--no-xlib --quiet --sub-source=marq')
        self._player: vlc.MediaPlayer = self._instance.media_player_new()

        # Переменные для оптимизации
        self._last_key_time = 0
        self._key_cooldown = 0.2  # Задержка между обработкой клавиш
        self._last_window_check = 0
        self._window_check_interval = 0.1  # Проверять окно раз в 100мс
        self._cached_window_active = False
        self._last_update_time = 0
        self._update_interval = 0.033  # ~30 FPS

        if self.video_path:
            self.set_new_video(self.video_path)

    def set_new_video(self, video_path):
        media = self._instance.media_new(video_path)
        self._player.set_media(media)

        self._player.video_set_marquee_int(0, 1)
        self._player.video_set_marquee_int(2, 0xFFFFFF)
        self._player.video_set_marquee_int(3, 100)
        self._player.video_set_marquee_int(4, 9)
        self._player.video_set_marquee_int(6, 24)
        self._player.video_set_marquee_int(7, 0)

        self._player.play()
        self._player.audio_set_mute(False)

    def play(self):
        self._player.play()

    def pause(self):
        self._player.pause()

    def _should_handle_input(self) -> bool:
        """Проверяет, можно ли обрабатывать ввод"""
        current_time = time.time()

        # Кешируем проверку окна (не чаще чем раз в interval)
        if current_time - self._last_window_check >= self._window_check_interval:
            self._cached_window_active = is_window_active_cached()
            self._last_window_check = current_time

        if not self._cached_window_active:
            return False

        # Защита от слишком частого нажатия клавиш
        if current_time - self._last_key_time < self._key_cooldown:
            return False

        return True

    def _handle_keyboard_input(self):
        """Обработка клавиатуры без блокирующих sleep"""
        if not self._should_handle_input():
            return

        current_time = time.time()

        try:
            if keyboard.is_pressed('esc'):
                self._player.stop()
                self._last_key_time = current_time
                sys.exit(0)


            elif keyboard.is_pressed('shift+left'):
                self._player.set_time(max(0, self._player.get_time() - 500))

            elif keyboard.is_pressed('shift+right'):
                self._player.set_time(min(self._player.get_length() - 1,
                                          self._player.get_time() + 500))

            elif keyboard.is_pressed('left'):
                self._player.set_time(max(0, self._player.get_time() - 10000))
                self._last_key_time = current_time

            elif keyboard.is_pressed('right'):
                self._player.set_time(min(self._player.get_length() - 1,
                                          self._player.get_time() + 10000))
                self._last_key_time = current_time

            elif keyboard.is_pressed('space'):
                if str(self._player.get_state()) == 'State.Playing':
                    self._player.pause()
                    self._last_key_time = current_time
                else:
                    self._player.play()
                    self._last_key_time = current_time

            elif keyboard.is_pressed('='):
                self._switch_audio_track()
                self._last_key_time = current_time

            elif keyboard.is_pressed('-'):
                self._switch_subtitle_track()
                self._last_key_time = current_time

            elif keyboard.is_pressed('t'):
                self._player.video_set_marquee_string(1, "Test")
                self._last_key_time = current_time


        except Exception as e:
            print(f"Keyboard error: {e}")

    def _switch_audio_track(self):
        """Переключение аудиодорожки"""
        d = self._player.audio_get_track_description()
        if not d:
            return

        audios = [item[0] for item in d]
        cur = audios.index(self._player.audio_get_track())
        self._player.audio_set_track(audios[1] if cur == len(audios) - 1 else audios[cur + 1])

    def _switch_subtitle_track(self):
        """Переключение субтитров"""
        d = self._player.video_get_spu_description()
        if not d:
            return

        subs = [item[0] for item in d]
        cur = subs.index(self._player.video_get_spu())
        self._player.video_set_spu(subs[0] if cur == len(subs) - 1 else subs[cur + 1])

    def update(self):
        """Основной метод обновления с ограничением FPS"""
        current_time = time.time()

        # Ограничение FPS
        if current_time - self._last_update_time < self._update_interval:
            return

        self._last_update_time = current_time

        # Обработка ввода
        self._handle_keyboard_input()

        # Обновление времени на экране (не чаще чем FPS)
        current_time_str = time.strftime('%H:%M:%S', time.gmtime(self._player.get_time() / 1000))
        self._player.video_set_marquee_string(1, current_time_str)