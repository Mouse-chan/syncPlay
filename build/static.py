import time

TEST_PATH = "C:\\Users\\belak\\Videos\\Мои видео\\Аниме\\Агент времени\\Link Click 1\\02.mkv"

def str_time_to_ms(str_time):
    h, m, s = map(float, str_time.split(':'))
    time_ms = int((h * 3600 + m * 60 + s) * 1000)
    return time_ms

def ms_to_str_time(time_ms):
    return time.strftime('%H:%M:%S', time.gmtime(time_ms / 1000))
