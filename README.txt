# Чтобы запустить:
pip install requests flask python-vlc keyboard
pip install pywin32

# Если видео не включается, возможно программа не видит плеер
# Добавь путь к VLC в системные пути:
import os
os.add_dll_directory(r'C:\Program Files\VideoLAN\VLC') # пример

# Команды:
-nick {nick} (-n {nick})
-play (-p)
-stop (-s)
-time {hh:mm:ss} (-t {hh:mm:ss})
-load {video_path} (-l {video_path})

-conf {команда} (-c {команда})  # подтверждение выполнения команды
