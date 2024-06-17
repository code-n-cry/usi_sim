import serial
from subprocess import Popen
from pathlib import Path
import vlc
from requests import get
import time

BASE_DIR = str(Path(__file__).resolve().parent.parent)
with open(
    BASE_DIR + "/python/label_to_value.txt"
) as lbl:  # получаем информацию о метках
    lst = lbl.readlines()
    label_to_value = {}
    for i in lst:
        i = i.replace("\n", "").split(": ")
        label_to_value[i[1]] = i[0]
port = serial.Serial("/dev/ttyUSB0", baudrate=9600, timeout=0.1)
current_label = None
current_video = None
frame_counter = 0
dim = (600, 400)
media_player = vlc.MediaPlayer()
folder_name = BASE_DIR + "/python/videos/"
label_to_video = {}
pid = 0
for i in range(1, 8):
    if i in [1, 2, 5, 7]:
        label_to_video[str(i)] = folder_name + f'{i}_LN.mp4'
    else:
        label_to_video[str(i)] = folder_name + f'{i}_CN.mp4'
while True:
    current_videos = get(
        'http://127.0.0.1:8000/current-values'
    ).json()  # с сервера получаем информацию о патологиях
    for i in current_videos:
        label_to_video[i] = (
            folder_name + f'{i}_' + current_videos[i].split(', ')[1] + '.mp4'
        )  # привязываем видео к меткам
    current_line = (
        port.readline().decode(encoding="latin-1").replace('\r\n', '')
    )
    if (
        current_line
        and current_line != '0'
        and label_to_video[label_to_value[current_line]] != current_video
    ):
        if pid:
            Popen(["kill", '-9', str(pid)])
        current_video = label_to_video[label_to_value[current_line]]
        args = [
            'vlc',
            '-I',
            'dummy',
            current_video,
            '--no-embedded-video',
            '--loop',
        ]
        process = Popen(args)
        pid = process.pid
