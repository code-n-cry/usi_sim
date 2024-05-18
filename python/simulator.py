import cv2
import serial

from pathlib import Path

from requests import get

BASE_DIR = str(Path(__file__).resolve().parent.parent)
with open(
    BASE_DIR + "/python/label_to_value.txt"
) as lbl:  # получаем информацию о метках
    lst = lbl.readlines()
    label_to_value = {}
    for i in lst:
        i = i.replace("\n", "").split(": ")
        label_to_value[i[0]] = i[1]
port = serial.Serial("/dev/ttyUSB0", baudrate=9600, timeout=0.1)
current_label = None
frame_counter = 0
dim = (600, 400)
folder_name = BASE_DIR + "/videos/"
current_video = folder_name + "basis_00.mp4"
ex = False
while True:
    current_videos = get('http://127.0.0.1:8000/current-values').json()[
        'Сердце'
    ]
    print(current_videos)
    current_line = (
        port.readline().decode(encoding="latin-1").replace("\r\n", "")
    )  # читаем строчку из порта
    if (
        current_line not in label_to_value.values()
    ):  # пока что костыль, если строчка пустая или 0, показываем базовое видео, иначе - другое
        current_video = folder_name + "basis_00.mp4"
    else:
        current_video = folder_name + "smth.mp4"
    cap = cv2.VideoCapture(current_video)  # запускаем показ видео
    while True:
        ret, frame = cap.read()
        frame_counter += 1
        if frame_counter == cap.get(
            cv2.CAP_PROP_FRAME_COUNT
        ):  # если видео закончилось, выходим из цикла, чтобы проверить, нет ли активной метки
            cap.release()
            break
        try:
            frame = cv2.resize(
                frame, dim, interpolation=cv2.INTER_AREA
            )  # иногда opencv падает с ошибкой, костыль небольшой
            cv2.imshow("frame", frame)
            cv2.resizeWindow("frame", 600, 400)
            cv2.moveWindow("frame", 40, 30)
        except cv2.error:
            cap.release()
            break
        if (
            cv2.getWindowProperty("frame", cv2.WND_PROP_VISIBLE) < 1
        ):  # закрываем окно по желанию пользователя и выходим из цикла
            port.close()
            ex = True
            break
    if ex:
        break
cap.release()  # останавливаем плеер, чтобы ничего не сломать
cv2.destroyAllWindows()
