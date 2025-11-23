
import tkinter as tk
from tkinter import ttk
import threading
import time
import keyboard
import pyautogui


# Глобальные переменные
running = False
thread = None

# Значения по умолчанию
default_open_time = 3
default_prepare_time = 1
default_battle_time = 24
default_iterations = 1000
default_start_key = 'F5'
default_stop_key = 'F6'

# Функции управления
def start_automation():
    global running, thread
    if not running:
        try:
            open_time = float(open_time_var.get())
            prepare_time = float(prepare_time_var.get())
            battle_time = float(battle_time_var.get())
            iterations = int(iterations_var.get())
        except ValueError:
            status_label.config(text="Ошибка: Проверьте ввод")
            return

        running = True
        thread = threading.Thread(target=automation_loop, args=(open_time, prepare_time, battle_time, iterations), daemon=True)
        thread.start()
        update_button_state()
        status_label.config(text="Статус: В работе")

def stop_automation():
    global running
    if running:
        running = False
        if thread.is_alive():
            thread.join()
        update_button_state()
        status_label.config(text="Статус: Остановлено")
while True:
    def automation_loop(open_time, prepare_time, battle_time, iterations):
        time.sleep(open_time)
        for i in range(1, iterations + 1):
            if not running:
                break
            time.sleep(prepare_time)
            keyboard.press("f")
            time.sleep(battle_time)
            keyboard.release("f")

        keyboard.press('tab')
        for i in range(1, iterations + 1):
            if not running:
                break
                keyboard.press('tab')
                time.sleep(0.2)
                pyautogui.moveTo(147, 226)

                pyautogui.mouseDown()
                time.sleep(0.2)
                pyautogui.mouseUp()
                pyautogui.mouseDown()
                time.sleep(0.2)
                pyautogui.mouseUp()
        keyboard.release('tab')







    def update_button_state():
        if running:
            start_btn.config(state='disabled')
            stop_btn.config(state='normal')
        else:
            start_btn.config(state='normal')
            stop_btn.config(state='disabled')


    # Обработка биндов
    def bind_start(event=None):
        global start_hotkey
        start_hotkey = start_key_entry.get()
        keyboard.add_hotkey(start_hotkey, start_automation)
        status_label.config(text=f"Забинджен старт: {start_hotkey}")


    def bind_stop(event=None):
        global stop_hotkey
        stop_hotkey = stop_key_entry.get()
        keyboard.add_hotkey(stop_hotkey, stop_automation)
        status_label.config(text=f"Забинджен стоп: {stop_hotkey}")


    # Создаем главное окно
    root = tk.Tk()
    root.title("Автоматизация игры")
    root.geometry("600x700")
    root.configure(bg="#34495e")

    # Заголовок
    ttk.Label(root, text="Настройки автоматизации", font=("Helvetica", 20, "bold"), foreground="#ecf0f1",
              background="#34495e").pack(pady=15)

    # Стиль
    style = ttk.Style()
    style.theme_use('clam')
    style.configure('TLabel', font=('Helvetica', 12), background="#34495e", foreground="#ecf0f1")
    style.configure('TButton', font=('Helvetica', 12), padding=8)
    style.configure('TEntry', font=('Helvetica', 12))

    # Ввод параметров
    params_frame = ttk.Frame(root)
    params_frame.pack(pady=10, padx=20, fill='x')

    # Время открытия
    ttk.Label(params_frame, text="Время открытия игры (сек):").grid(row=0, column=0, sticky='w', pady=5)
    open_time_var = tk.StringVar(value=str(default_open_time))
    ttk.Entry(params_frame, textvariable=open_time_var).grid(row=0, column=1, pady=5, padx=10)

    # Время подготовки
    ttk.Label(params_frame, text="Время подготовки (сек):").grid(row=1, column=0, sticky='w', pady=5)
    prepare_time_var = tk.StringVar(value=str(default_prepare_time))
    ttk.Entry(params_frame, textvariable=prepare_time_var).grid(row=1, column=1, pady=5, padx=10)

    # Время бега
    ttk.Label(params_frame, text="Время бега (сек):").grid(row=2, column=0, sticky='w', pady=5)
    battle_time_var = tk.StringVar(value=str(default_battle_time))
    ttk.Entry(params_frame, textvariable=battle_time_var).grid(row=2, column=1, pady=5, padx=10)

    # Количество итераций
    ttk.Label(params_frame, text="Количество итераций:").grid(row=3, column=0, sticky='w', pady=5)
    iterations_var = tk.StringVar(value=str(default_iterations))
    ttk.Entry(params_frame, textvariable=iterations_var).grid(row=3, column=1, pady=5, padx=10)

    # Бинды для старт и стоп
    binds_frame = ttk.Frame(root)
    binds_frame.pack(pady=15)

    ttk.Label(binds_frame, text="Клавиша старт:").grid(row=0, column=0, padx=5, sticky='w')
    start_key_entry = ttk.Entry(binds_frame, width=10)
    start_key_entry.insert(0, default_start_key)

    ttk.Label(binds_frame, text="Клавиша стоп:").grid(row=1, column=0, padx=5, sticky='w')
    stop_key_entry = ttk.Entry(binds_frame, width=10)
    stop_key_entry.insert(0, default_stop_key)

    # Кнопки для биндинга
    binds_button_frame = ttk.Frame(root)
    binds_button_frame.pack(pady=10)

    ttk.Button(binds_button_frame, text="Задать старт", command=bind_start).grid(row=0, column=0, padx=10)
    ttk.Button(binds_button_frame, text="Задать стоп", command=bind_stop).grid(row=0, column=1, padx=10)

    # Кнопки управления
    buttons_frame = ttk.Frame(root)
    buttons_frame.pack(pady=20)

    start_btn = ttk.Button(buttons_frame, text="Запустить", command=start_automation)
    start_btn.grid(row=0, column=0, padx=10)

    stop_btn = ttk.Button(buttons_frame, text="Остановить", command=stop_automation, state='disabled')
    stop_btn.grid(row=0, column=1, padx=10)

    # Статус
    status_label = ttk.Label(root, text="Статус: Остановлено", font=("Helvetica", 14), foreground="#bdc3c7",
                             background="#34495e")
    status_label.pack(pady=10)


    # Обновление статуса и биндингов
    def periodic_update():
        update_button_state()
        root.after(500, periodic_update)


    periodic_update()

    # Запуск биндингов
    bind_start()
    bind_stop()

    root.mainloop()


    from table import *

    find_and_select_item(threshold=0.8, max_attempts=10)