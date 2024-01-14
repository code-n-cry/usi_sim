import os
import serial
import subprocess
import tkinter
import time
from tkinter.simpledialog import askinteger
from PIL import Image, ImageTk

label_to_value = {}  # переменная для хранение пар номер-значение
tkinter_labels = (
    []
)  # массив для хранения надписей, чтобы их было удобнее менять


'''def loop_video(event):
    tkinter.videoplayer.play()
'''


def on_closing():
    '''
    Сохраняет пары номер-значение в файл при закрытии окна
    '''
    if label_to_value:
        with open('label_to_value.txt', 'w') as cfg:
            for num in label_to_value:
                cfg.write(f'{num}: {label_to_value[num]}\n')
    window.destroy()


def bind():
    '''
    При нажатии кнопки "Добавить метку" добавляет в переменную label_to_value
    пару номер-значение
    '''
    global port, lbl
    with_warning = False  # переменная-флаг, чтобы заменить метку
    if not port.is_open:
        port.open()
    while True:
        current_line = (
            port.readline().decode(encoding='latin-1').replace('\r\n', '')
        )  # считываем строку из порта и приводим в человеческий вид
        if (
            current_line not in ['0', '']
            and current_line not in label_to_value.values()
        ):  # если такой ещё не было, то добавляем номер-значение в labels_to_value
            label_to_value[len(label_to_value.keys()) + 1] = current_line
            port.read_all()
            break
        elif (
            current_line in label_to_value.values()
        ):  # если была, активируем флаг
            with_warning = True
            port.read_all()
            break
    if with_warning:
        num = askinteger(  # спрашиваем о замене значения метки
            'Заменить метку',
            ''.join(
                [
                    'Такое значение уже было. Если хотите присвоить его другой метке,',
                    'напишите её номер: ',
                ]
            ),
        )
        if num:  # если решили менять, а не случайно туда же
            label_to_value[num] = current_line  # присваиваем новое значение
            tkinter_labels[num - 1].configure(  # меняем надпись на экране
                text=''.join(
                    [
                        f'Метка {num},',
                        f'значение: {current_line}',
                    ]
                )
            )
            for (
                ind
            ) in (
                label_to_value
            ):  # удаляем старую метку с таким же значением из списка
                if label_to_value[ind] == current_line and ind != num:
                    tkinter_labels[ind - 1].configure(
                        text=''
                    )  # делаем пустой надпись с таким же значением
                    del label_to_value[ind]
                    break
        with_warning = False
    else:
        label = tkinter.Label(  # если номер новый, показываем на экране информацию о новой паре
            window,
            text=''.join(
                [
                    f'Метка {len(label_to_value.keys())},',
                    f'значение: {label_to_value[len(label_to_value.keys())]}',
                ]
            ),
        )
        label.pack(side='top')
        tkinter_labels.append(label)
        lbl.configure(  # обновляем надпись-подсказку
            text=f'Прислоните датчик к метке {len(label_to_value.keys()) + 1}',
        )
    port.close()


def start():
    '''
    При нажатии кнопки "Запустить симулятор" открывает другое окно, которое
    имитирует процесс УЗИ
    '''
    global port
    port.close()
    if label_to_value:
        with open('label_to_value.txt', 'w') as cfg:
            for num in label_to_value:
                cfg.write(f'{num}: {label_to_value[num]}\n')
    subprocess.Popen('python simulator.py', shell=True)


lbl_text = f'Прислоните датчик к метке {len(label_to_value.keys()) + 1}'
window = tkinter.Tk()  # создание окна
window.title('Привязка меток')
window.geometry('800x600')
port = serial.Serial(
    'COM7', baudrate=9600
)  # объявление порта, номер другой может быть, пока что лучше смотреть через arduino IDE
bind_btn = tkinter.Button(
    window, text='Добавить метку', command=bind
)  # создаём кнопку
start_sim_btn = tkinter.Button(
    window, text='Запустить симулятор', command=start
)
bind_btn.place(relx=0, rely=0.6)
start_sim_btn.place(relx=0, rely=0.7)
if os.path.isfile('label_to_value.txt'): # если уже существует непустой файл с метками, 
    with open('label_to_value.txt') as lbl:
        lst = lbl.readlines()
        label_to_value = {}
        for i in lst:
            i = i.replace('\n', '').split(': ')
            label_to_value[int(i[0])] = i[1]
    if label_to_value:
        for i in label_to_value:
            label = tkinter.Label(  # если номер новый, показываем на экране информацию о новой паре
                window,
                text=''.join(
                    [
                        f'Метка {i},',
                        f'значение: {label_to_value[len(label_to_value.keys())]}',
                    ]
                ),
            )
            label.pack(side='top')
            tkinter_labels.append(label)
        lbl_text = 'Некоторые метки уже привязаны!'
lbl = tkinter.Label(  # надпись-подсказка
    window, text=lbl_text
)
lbl.place(relx=0.5, rely=0.5)
frame = tkinter.Frame(window)  # помещаем схему размещения меток(картинку)
frame.place(relx=0, rely=0)
canvas = tkinter.Canvas(window, height=350, width=150)
image = Image.open('tors.png')
photo = ImageTk.PhotoImage(image)
image = canvas.create_image(0, 0, anchor='nw', image=photo)
canvas.place(relx=0, rely=0)
window.protocol(
    'WM_DELETE_WINDOW', on_closing
)  # привязываем функцию для закрытия
window.mainloop()
