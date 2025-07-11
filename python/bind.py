import os
#import serial
import subprocess
import tkinter
import tkinter.messagebox
from tkinter.simpledialog import askinteger
from PIL import Image, ImageTk

label_to_value = {}  # переменная для хранения пар номер-значение
labels_frame = None  # фрейм для отображения меток
lbl = None  # Добавляем глобальную переменную для подсказки


def label_dict_to_file():
    """Сохраняет пары номер-значение в файл"""
    if label_to_value:
        with open("label_to_value.txt", "w") as cfg:
            for num in sorted(label_to_value.keys()):
                cfg.write(f"{num}: {label_to_value[num]}\n")


def rebuild_labels():
    """Перестраивает отображение меток в главном окне"""
    global lbl  # Делаем lbl доступной в функции

    # Очищаем фрейм с метками
    for widget in labels_frame.winfo_children():
        widget.destroy()

    # Добавляем метки в отсортированном порядке
    for num in sorted(label_to_value.keys()):
        label = tkinter.Label(
            labels_frame,
            text=f"Метка {num}, значение: {label_to_value[num]}",
            anchor="w",
            width=40
        )
        label.pack(side="top", fill=tkinter.X, padx=5, pady=2)

    # Обновляем подсказку, только если lbl уже создан
    if lbl:
        next_num = max(label_to_value.keys()) + 1 if label_to_value else 1
        lbl.configure(text=f"Прислоните датчик к метке {next_num}")


def on_closing():
    """Сохраняет пары номер-значение в файл при закрытии окна"""
    label_dict_to_file()
    window.destroy()
    try:
        subprocess.Popen(["killall", "uvicorn", "ngrok"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except:
        pass
    try:
        subprocess.Popen(["fuser", "-k", "8000/tcp"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except:
        pass


def bind():
    """Добавляет новую метку или заменяет существующую"""
    global lbl

    # try:
    #     port = serial.Serial("/dev/ttyUSB0", baudrate=9600)
    # except serial.SerialException:
    #     tkinter.messagebox.showerror("Ошибка", "Не удалось открыть порт /dev/ttyUSB0")
    #     return
    #
    # if not port.is_open:
    #     try:
    #         port.open()
    #     except:
    #         tkinter.messagebox.showerror("Ошибка", "Не удалось открыть порт /dev/ttyUSB0")
    #         return
    #
    # port.read_all()  # Очищаем буфер
    current_line = ""
    # try:
    #     while True:
    #         data = port.readline().decode(encoding="latin-1", errors="ignore").replace("\r\n", "")
    #         if data and data != "0":
    #             current_line = data
    #             break
    # except:
    #     tkinter.messagebox.showerror("Ошибка", "Ошибка при чтении данных с порта")
    #     port.close()
    #     return
    #
    # port.close()
    #
    # if not current_line:
    #     tkinter.messagebox.showerror("Ошибка", "Не удалось считать данные с датчика")
    #     return

    # Проверяем, есть ли такое значение уже в словаре
    existing_num = None
    for num, value in label_to_value.items():
        if value == current_line:
            existing_num = num
            break

    if existing_num is not None:
        response = tkinter.messagebox.askyesno(
            "Метка уже существует",
            f"Значение '{current_line}' уже привязано к метке {existing_num}.\n"
            "Хотите присвоить его другой метке?"
        )
        if response:
            num = askinteger(
                "Выбор метки",
                "Введите номер метки для перепривязки:"
            )
            if num:
                # Удаляем старую метку с таким же значением
                for k, v in list(label_to_value.items()):
                    if v == current_line:
                        del label_to_value[k]

                # Привязываем к новой метке
                label_to_value[num] = current_line
                label_dict_to_file()
                rebuild_labels()
    else:
        # Определяем новый номер метки
        new_num = max(label_to_value.keys()) + 1 if label_to_value else 1
        label_to_value[new_num] = current_line
        label_dict_to_file()
        rebuild_labels()


def server():
    """Запускает сервер для инструктора"""
    try:
        args = ["python3", "-m", "uvicorn", "server:app", "--port", "8000", "--host", "0.0.0.0"]
        subprocess.Popen(args)
        tkinter.messagebox.showinfo("Сервер запущен", "Сервер успешно запущен на порту 8000")
    except Exception as e:
        tkinter.messagebox.showerror("Ошибка", f"Не удалось запустить сервер: {str(e)}")


def start():
    """Запускает симулятор УЗИ"""
    label_dict_to_file()
    try:
        subprocess.Popen(["python3", "simulator.py"])
    except Exception as e:
        tkinter.messagebox.showerror("Ошибка", f"Не удалось запустить симулятор: {str(e)}")


def edit_labels():
    """Открывает окно редактирования меток"""
    edit_window = tkinter.Toplevel(window)
    edit_window.title("Редактирование меток")
    edit_window.geometry("500x350")  # Увеличили окно для новых кнопок
    edit_window.transient(window)
    edit_window.grab_set()

    # Фрейм для списка меток
    list_frame = tkinter.Frame(edit_window)
    list_frame.pack(fill=tkinter.BOTH, expand=True, padx=10, pady=10)

    scrollbar = tkinter.Scrollbar(list_frame)
    scrollbar.pack(side=tkinter.RIGHT, fill=tkinter.Y)

    listbox = tkinter.Listbox(
        list_frame,
        yscrollcommand=scrollbar.set,
        selectmode=tkinter.SINGLE,
        font=("Arial", 12)
    )
    listbox.pack(side=tkinter.LEFT, fill=tkinter.BOTH, expand=True)
    scrollbar.config(command=listbox.yview)

    # Заполняем список метками
    for num in sorted(label_to_value.keys()):
        listbox.insert(tkinter.END, f"Метка {num}: {label_to_value[num]}")

    # Фрейм для кнопок
    btn_frame = tkinter.Frame(edit_window)
    btn_frame.pack(fill=tkinter.X, padx=10, pady=10)

    def delete_selected():
        """Удаляет выбранную метку"""
        selection = listbox.curselection()
        if not selection:
            tkinter.messagebox.showwarning("Ошибка", "Выберите метку для удаления")
            return

        index = selection[0]
        item = listbox.get(index)
        try:
            num = int(item.split()[1][:-1])  # Извлекаем номер метки
        except (IndexError, ValueError):
            tkinter.messagebox.showerror("Ошибка", "Неверный формат метки")
            return

        if num in label_to_value:
            del label_to_value[num]
            listbox.delete(index)
            label_dict_to_file()
            rebuild_labels()
            tkinter.messagebox.showinfo("Успех", f"Метка {num} удалена")

    def rebind_selected():
        """Перепривязывает выбранную метку"""
        selection = listbox.curselection()
        if not selection:
            tkinter.messagebox.showwarning("Ошибка", "Выберите метку для перепривязки")
            return

        index = selection[0]
        item = listbox.get(index)
        try:
            old_num = int(item.split()[1][:-1])  # Извлекаем старый номер метки
        except (IndexError, ValueError):
            tkinter.messagebox.showerror("Ошибка", "Неверный формат метки")
            return

        # Считываем новое значение с датчика
        # try:
        #     port = serial.Serial("/dev/ttyUSB0", baudrate=9600)
        #     if not port.is_open:
        #         port.open()
        #
        #     port.read_all()  # Очищаем буфер
        #     new_value = ""
        #     while True:
        #         try:
        #             data = port.readline().decode(encoding="latin-1", errors="ignore").replace("\r\n", "")
        #             if data and data != "0":
        #                 new_value = data
        #                 break
        #         except:
        #             continue
        #
        #     port.close()
        #
        #     if not new_value:
        #         tkinter.messagebox.showerror("Ошибка", "Не удалось считать данные с датчика")
        #         return
        #
        #     # Удаляем старую метку с таким же значением (если есть)
        #     for k, v in list(label_to_value.items()):
        #         if v == new_value and k != old_num:
        #             del label_to_value[k]
        #
        #     # Обновляем значение
        #     label_to_value[old_num] = new_value
        #     label_dict_to_file()
        #     rebuild_labels()
        #
        #     # Обновляем список в окне редактирования
        #     listbox.delete(index)
        #     listbox.insert(index, f"Метка {old_num}: {new_value}")
        #     listbox.select_set(index)
        #
        #     tkinter.messagebox.showinfo("Успех", f"Метка {old_num} перепривязана")
        #
        # except serial.SerialException:
        #     tkinter.messagebox.showerror("Ошибка", "Не удалось открыть порт /dev/ttyUSB0")

    def change_number():
        """Изменяет номер существующей метки"""
        selection = listbox.curselection()
        if not selection:
            tkinter.messagebox.showwarning("Ошибка", "Выберите метку для изменения номера")
            return

        index = selection[0]
        item = listbox.get(index)
        try:
            old_num = int(item.split()[1][:-1])  # Извлекаем старый номер метки
        except (IndexError, ValueError):
            tkinter.messagebox.showerror("Ошибка", "Неверный формат метки")
            return

        # Запрашиваем новый номер
        new_num = askinteger(
            "Изменение номера метки",
            f"Текущий номер метки: {old_num}\nВведите новый номер:",
            minvalue=1
        )

        if not new_num:
            return  # Пользователь отменил

        if new_num == old_num:
            tkinter.messagebox.showinfo("Информация", "Новый номер совпадает с текущим")
            return

        # Проверяем, существует ли уже метка с таким номером
        if new_num in label_to_value:
            response = tkinter.messagebox.askyesno(
                "Подтверждение",
                f"Метка {new_num} уже существует. Заменить её?"
            )
            if not response:
                return

        # Сохраняем значение метки
        value = label_to_value[old_num]

        # Удаляем старую запись
        del label_to_value[old_num]

        # Если новый номер уже существует, удаляем его
        if new_num in label_to_value:
            del label_to_value[new_num]

        # Создаем новую запись с новым номером
        label_to_value[new_num] = value

        # Сохраняем изменения
        label_dict_to_file()
        rebuild_labels()

        # Обновляем список в окне редактирования
        listbox.delete(0, tkinter.END)
        for num in sorted(label_to_value.keys()):
            listbox.insert(tkinter.END, f"Метка {num}: {label_to_value[num]}")

        # Находим и выделяем измененную метку
        for i in range(listbox.size()):
            if f"Метка {new_num}:" in listbox.get(i):
                listbox.select_set(i)
                listbox.see(i)
                break

        tkinter.messagebox.showinfo("Успех", f"Номер метки изменен с {old_num} на {new_num}")

    # Кнопки управления
    btn_frame1 = tkinter.Frame(btn_frame)
    btn_frame1.pack(fill=tkinter.X, pady=5)

    btn_frame2 = tkinter.Frame(btn_frame)
    btn_frame2.pack(fill=tkinter.X, pady=5)

    delete_btn = tkinter.Button(
        btn_frame1,
        text="Удалить",
        command=delete_selected,
        width=15
    )
    delete_btn.pack(side=tkinter.LEFT, padx=5)

    rebind_btn = tkinter.Button(
        btn_frame1,
        text="Перепривязать",
        command=rebind_selected,
        width=15
    )
    rebind_btn.pack(side=tkinter.LEFT, padx=5)

    change_num_btn = tkinter.Button(
        btn_frame1,
        text="Изменить номер",
        command=change_number,
        width=15
    )
    change_num_btn.pack(side=tkinter.LEFT, padx=5)

    close_btn = tkinter.Button(
        btn_frame2,
        text="Закрыть",
        command=edit_window.destroy,
        width=15
    )
    close_btn.pack(side=tkinter.RIGHT, padx=5)


# Создание главного окна
window = tkinter.Tk()
window.title("Привязка меток")
window.geometry("800x600")

# Загрузка существующих меток
if os.path.isfile("label_to_value.txt"):
    try:
        with open("label_to_value.txt", "r") as lbl_file:
            for line in lbl_file:
                line = line.strip()
                if line:
                    parts = line.split(": ", 1)
                    if len(parts) == 2:
                        try:
                            num = int(parts[0])
                            label_to_value[num] = parts[1]
                        except ValueError:
                            continue
    except Exception as e:
        tkinter.messagebox.showwarning("Ошибка", f"Ошибка при чтении файла меток: {str(e)}")

# Виджеты интерфейса
# Фрейм для изображения
img_frame = tkinter.Frame(window)
img_frame.place(relx=0, rely=0, relwidth=0.2, relheight=0.5)

# Изображение схемы размещения меток
try:
    canvas = tkinter.Canvas(img_frame, height=350, width=150)
    image = Image.open("tors.png")
    photo = ImageTk.PhotoImage(image)
    canvas.create_image(0, 0, anchor="nw", image=photo)
    canvas.image = photo  # Сохраняем ссылку на изображение
    canvas.pack(fill=tkinter.BOTH, expand=True)
except Exception as e:
    error_label = tkinter.Label(img_frame, text="Ошибка загрузки изображения", fg="red")
    error_label.pack(fill=tkinter.BOTH, expand=True)
    print(f"Ошибка загрузки изображения: {str(e)}")

# Фрейм для списка меток
labels_frame = tkinter.Frame(window)
labels_frame.place(relx=0.2, rely=0, relwidth=0.6, relheight=0.5)

# Подсказка (создаем здесь, чтобы она была доступна в rebuild_labels)
lbl = tkinter.Label(window, text="Прислоните датчик к метке 1", font=("Arial", 12))
lbl.place(relx=0.5, rely=0.55, anchor="center")

# Теперь можно безопасно вызывать rebuild_labels
rebuild_labels()

# Фрейм для кнопок
btn_frame = tkinter.Frame(window)
btn_frame.place(relx=0.3, rely=0.6, relwidth=0.4, relheight=0.3)

bind_btn = tkinter.Button(
    btn_frame,
    text="Добавить метку",
    command=bind,
    width=20,
    height=1
)
bind_btn.pack(side=tkinter.TOP, pady=5)

edit_btn = tkinter.Button(
    btn_frame,
    text="Редактировать метки",
    command=edit_labels,
    width=20,
    height=1
)
edit_btn.pack(side=tkinter.TOP, pady=5)

start_sim_btn = tkinter.Button(
    btn_frame,
    text="Запустить симулятор",
    command=start,
    width=20,
    height=1
)
start_sim_btn.pack(side=tkinter.TOP, pady=5)

start_server_btn = tkinter.Button(
    btn_frame,
    text="Запустить сервер",
    command=server,
    width=20,
    height=1
)
start_server_btn.pack(side=tkinter.TOP, pady=5)

# Авторская подпись
author_label = tkinter.Label(
    window,
    text="Создатели: Щукины Владислав Владимирович и Егор Владиславович, Сафонов Алексей",
    font=("Arial", 9)
)
author_label.place(relx=0.5, rely=0.95, anchor="center")

# Обработка закрытия окна
window.protocol("WM_DELETE_WINDOW", on_closing)

# Запуск главного цикла
window.mainloop()