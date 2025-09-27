# syncPlay
Синхронизация видео по интернету


# Гайд по скачиванию

### Клонирование:
`git clone https://github.com/Mouse-chan/mapMAI.git`
### Виртуальное окружение:
`python -m venv venv`
### Активация виртуального окружения:
#### Unix: `source venv/bin/activate`
#### Windows: `.\venv\Scripts\activate`
### Установка зависимостей
`pip install -r requirements.txt`

# Если видео не включается, возможно программа не видит плеер
## Добавьте путь к VLC в системные пути:
`import os
os.add_dll_directory(r'C:\Program Files\VideoLAN\VLC') # пример`

# Команды:
* `-nick {nick} (-n {nick})` - смена ника
* `-play {hh:mm:ss} (-p {hh:mm:ss})` - воспроизведение + синхронизация времени
* `-stop {hh:mm:ss} (-s {hh:mm:ss})` - стоп + синхронизация времени
* `-time {hh:mm:ss} (-t {hh:mm:ss})` - перемотка
* `-load {video_path} (-l {video_path})` - загрузка видео
