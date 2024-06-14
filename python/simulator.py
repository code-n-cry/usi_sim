import cv2
import serial
from subprocess import Popen
from pathlib import Path
import vlc
from requests import get
import time

BASE_DIR = str(Path(__file__).resolve().parent.parent)
with open(BASE_DIR + "/python/label_to_value.txt") as lbl:  # получаем информацию о метках
    lst = lbl.readlines()
    label_to_value = {}
    for i in lst:
        i = i.replace("\n", "").split(": ")
        label_to_value[i[0]] = i[1]
port = serial.Serial("/dev/ttyUSB0", baudrate=9600, timeout=0.2)
current_label = None
frame_counter = 0
dim = (600, 400)
media_player = vlc.MediaPlayer()
folder_name = BASE_DIR + "/python/videos/"
current_video = folder_name + "basis_00.mp4"
is_playing = False
while True:
    #current_videos = get('http://127.0.0.1:8000/current-values').json()['Сердце']
    #print(current_videos)
    try:
        current_line = (
            port.readline().decode(encoding="latin-1").replace("\r\n", "")
        )  # читаем строчку из порта
    except:
        current_line = (
            port.readline().decode(encoding="latin-1").replace("\r\n", "")
        )  # читаем строчку из порта
    '''if (
        current_line not in label_to_value.values()
    ):  # пока что костыль, если строчка пустая или 0, показываем базовое видео, иначе - другое
        current_video = folder_name + "basis_00.mp4"
    else:
        current_video = folder_name + "smth.mp4"
    if not is_playing:
        Popen(f"vlc -I dummy --no-video-deco --no-embedded-video --width=500 --height=500 --loop {current_video}".split())
        is_playing = True
    time.sleep(5)
    current_video = folder_name + "smth.mp4"
    is_playing = False'''