import cv2
import serial

with open('label_to_value.txt') as lbl:
    lst = lbl.readlines()
    label_to_value = {}
    for i in lst:
        i = i.replace('\n', '').split(': ')
        label_to_value[i[0]] = i[1]
port = serial.Serial('COM7', baudrate=9600, timeout=.1)
current_label = None
frame_counter = 0
dim = (600, 400)
folder_name = 'videos/'
current_video = folder_name + 'basis_00.mp4'
ex = False
while port:
    current_line = (
            port.readline().decode(encoding='latin-1').replace('\r\n', '')
    )
    if current_line not in label_to_value.values():
        current_video = folder_name + 'basis_00.mp4'
    else:
        current_video = folder_name + 'smth.mp4'
    cap = cv2.VideoCapture(current_video)
    while True:
        ret, frame = cap.read()
        frame_counter += 1
        if frame_counter == cap.get(cv2.CAP_PROP_FRAME_COUNT):
            cap.release()
            break
        try:
            frame = cv2.resize(frame, dim, interpolation=cv2.INTER_AREA)
            cv2.imshow('frame', frame)
            cv2.resizeWindow('frame', 600, 400)
            cv2.moveWindow('frame', 40, 30)
        except cv2.error:
            cap.release()
            break
        if cv2.waitKey(1) & 0xFF == ord('q') or cv2.getWindowProperty('frame', cv2.WND_PROP_VISIBLE) < 1:
            port.close()
            ex = True
            break
    if ex:
        break
cap.release()
cv2.destroyAllWindows()
