path_v = "C:\\Users\\belak\\Videos\\Мои видео\\Аниме\\Агент времени\\Link Click 1\\02.mkv"

import vlc
import time

player = vlc.MediaPlayer(path_v)

player.set_video_title_display(10, 1000)
player.play()
while True:
    time.sleep(1)
# Даем видео проиграться 5 секунд
time.sleep(30)

# Ставим на паузу
media_player.pause()
print("Видео на паузе")

# Ждем 3 секунды, пока видео paused
#time.sleep(3)

# Перематываем на 20-ю секунду (10000 мс)
media_player.set_time(20000)

# Возобновляем воспроизведение с новой позиции
media_player.play()
print("Возобновляем воспроизведение с 20-й секунды")

# Даем видео проиграться еще 10 секунд before exiting
#time.sleep(10)

# Останавливаем воспроизведение
#media_player.stop()