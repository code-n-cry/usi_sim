import serial
import tkinter
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
    При нажатии кнопки добавляет в переменную label_to_value
    пару номер-значение
    '''
    global lbl
    with_warning = False  # переменная-флаг, чтобы заменить метку
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


window = tkinter.Tk()  # создание окна
window.title('Привязка меток')
window.geometry('800x600')
port = serial.Serial(
    'COM7', 9600
)  # объявление порта, номер другой может быть, пока что лучше смотреть через arduino IDE
bind_btn = tkinter.Button(
    window, text='Добавить метку', command=bind
)  # создаём кнопку
bind_btn.place(relx=0, rely=0.6)
lbl = tkinter.Label(  # надпись-подсказка
    window, text=f'Прислоните датчик к метке {len(label_to_value.keys()) + 1}'
)
lbl.place(relx=0.5, rely=0.5)
frame = tkinter.Frame(window)  # помещаем схему размещения меток(картинку)
frame.place(relx=0, rely=0)
canvas = tkinter.Canvas(window, height=350, width=150)
image = Image.open('tors.png')
photo = ImageTk.PhotoImage(image)
image = canvas.create_image(0, 0, anchor='nw',image=photo)
canvas.place(relx=0, rely=0)
window.protocol(
    'WM_DELETE_WINDOW', on_closing
)  # привязываем функцию для закрытия
window.mainloop()
