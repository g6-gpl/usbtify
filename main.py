import tkinter as tk
from tkinter import scrolledtext
import sys
import datetime
import win32api
import win32con
import win32file

# Начальный пароль для доступа к настройкам
PASSWORD = "1234"  # Замените на ваш пароль

def exit_app():
    root.destroy()
    sys.exit()

def check_password(action,passwords=[]):
    global password_window
    # Проверка введенного пароля
    if entry_password.get() == PASSWORD:
        # Если пароль верный, выполняем действие
        password_window.destroy()
        if action == "exit":
            exit_app()
        elif action == "change_password":
            change_password()
        elif action == "open_settings":
            open_settings()
        elif action == "check_password":
            if passwords[0]!=passwords[1]:
                return True
            else: 
                return False
        

        entry_password.delete(0, tk.END)  # Очищаем поле ввода
        label_error.config(text="")  # Очищаем сообщение об ошибке
    else:
        # Если пароль неверный, показываем сообщение об ошибке
        label_error.config(text="Неверный пароль", fg="red")

password_window_open = False
def ask_password(action):
    # Создаем окно для ввода пароля
    global entry_password, label_error,password_window, password_window_open

    # print(password_window)
    password_window = tk.Toplevel(root)
    password_window.title("Введите пароль")
    password_window.geometry("300x125")


    label_password = tk.Label(password_window, text="Введите пароль:")
    label_password.pack(pady=5)

    entry_password = tk.Entry(password_window, show="*")
    entry_password.pack(pady=5)

    label_error = tk.Label(password_window, text="", fg="red")
    label_error.pack(pady=5)

    # Передаем действие в check_password
    button_confirm = tk.Button(password_window, text="Подтвердить", command=lambda: check_password(action))
    button_confirm.pack(pady=5)
    
    

def change_password():
    # Функция для изменения пароля
    change_password_window = tk.Toplevel(root)
    change_password_window.title("Изменить пароль")
    change_password_window.geometry("300x300")

    label_old_password = tk.Label(change_password_window, text="Старый пароль:")
    label_old_password.pack(pady=5)

    entry_old_password = tk.Entry(change_password_window, show="*")
    entry_old_password.pack(pady=5)

    label_new_password = tk.Label(change_password_window, text="Новый пароль:")
    label_new_password.pack(pady=5)

    entry_new_password = tk.Entry(change_password_window, show="*")
    entry_new_password.pack(pady=5)

    label_confirm_password = tk.Label(change_password_window, text="Подтвердите новый пароль:")
    label_confirm_password.pack(pady=5)

    entry_confirm_password = tk.Entry(change_password_window, show="*")
    entry_confirm_password.pack(pady=5)

    label_password_error = tk.Label(change_password_window, text="", fg="red")
    label_password_error.pack(pady=5)

    def confirm_change_password():
        old_password = entry_old_password.get()
        new_password = entry_new_password.get()
        confirm_password = entry_confirm_password.get()

        if check_password('check_password',[old_password,new_password]):
            label_password_error.config(text="Старый пароль неверный", fg="red")
        elif new_password != confirm_password:
            label_password_error.config(text="Новые пароли не совпадают", fg="red")
        else:
            PASSWORD = new_password
            label_password_error.config(text="Пароль успешно изменен", fg="green")
            # Очищаем поля ввода
            entry_old_password.delete(0, tk.END)
            entry_new_password.delete(0, tk.END)
            entry_confirm_password.delete(0, tk.END)

    button_confirm_change = tk.Button(change_password_window, text="Подтвердить", command=confirm_change_password)
    button_confirm_change.pack(pady=5)

def open_settings():
    settings_frame.pack(side="left", anchor="nw", padx=10, pady=10)

def log_message(message):
    log_area.insert(tk.END,f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {message}\n")
    log_area.see(tk.END)
    
def get_connetcted_drives():
    drives = [i for i in win32api.GetLogicalDriveStrings().split("\\\x00") if i]
    rdrives = [d for d in drives if win32file.GetDriveType(d) == win32con.DRIVE_REMOVABLE]
    return rdrives

def update_drives_list():
    drives = get_connetcted_drives()
    drives_listbox.delete(0,tk.END)
    for drive in drives:
        drives_listbox.insert(tk.END,drives)

    log_message("Список носителей обновлен")
    root.after(2000,update_drives_list)
    
# Создание основного окна
root = tk.Tk()
root.attributes("-fullscreen", True)  # Полноэкранный режим
root.option_add("*tearOff", False)

# Фрейм для настроек
settings_frame = tk.Frame(root)
settings_frame.pack_forget()  # Скрываем фрейм настроек по умолчанию

main_menu = tk.Menu()

settings_menu = tk.Menu()
settings_menu.add_command(label="Exit", command=lambda: ask_password("exit"))
settings_menu.add_command(label="Change password", command=lambda: ask_password("change_password"))
settings_menu.add_command(label="Open settings", command=lambda: ask_password("open_settings"))
main_menu.add_cascade(label="Settings", menu=settings_menu)

main_menu.add_cascade(label="Statistic")

root.config(menu=main_menu)

log_frame = tk.Frame(root)
log_frame.pack(pady=10,side='bottom')

log_area = scrolledtext.ScrolledText(log_frame,wrap=tk.WORD)
log_area.pack(pady=10,fill=tk.BOTH,expand=True)

drives_listbox = tk.Listbox(root,width=60,height=10)
drives_listbox.pack(pady=10)

# Запуск основного цикла обработки событий
log_message("Hello")

update_drives_list()
root.mainloop()