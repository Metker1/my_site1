import tkinter as tk
from tkinter import ttk
import threading
import time
import keyboard
import pyautogui

# Глобальные переменные
running = False
thread = None
click_thread = None
auto_click_active = False

# Настройки
default_battle_time = 24
default_iterations = 1000
default_start_key = 'F5'
default_stop_key = 'F6'
trigger_click_key = 'F2'

# Создаем интерфейс
root = tk.Tk()
root.title("🎮 Многофункциональный автоматизатор")
root.geometry("700x750")
root.configure(bg="#34495e")

style = ttk.Style()
style.theme_use('clam')
style.configure('TLabel', font=('Helvetica', 12), background="#34495e", foreground="#ecf0f1")
style.configure('TButton', font=('Helvetica', 12), padding=8, background="#2980b9", foreground="#fff")
style.configure('TEntry', font=('Helvetica', 12))
style.map('TButton', background=[('active', '#3498db')])

# Заголовок
ttk.Label(root, text="Настройки автоматизации", font=("Helvetica", 20, "bold"),
          foreground="#ecf0f1", background="#34495e").pack(pady=15)

# Параметры
params_frame = ttk.Frame(root)
params_frame.pack(pady=10, padx=20, fill='x')

# Время бега
ttk.Label(params_frame, text="Время бега (сек):").grid(row=0, column=0, sticky='w', pady=5)
battle_time_var = tk.StringVar(value=str(default_battle_time))
ttk.Entry(params_frame, textvariable=battle_time_var).grid(row=0, column=1, pady=5, padx=10)

# Количество итераций
ttk.Label(params_frame, text="Количество итераций:").grid(row=1, column=0, sticky='w', pady=5)
iterations_var = tk.StringVar(value=str(default_iterations))
ttk.Entry(params_frame, textvariable=iterations_var).grid(row=1, column=1, pady=5, padx=10)

# Бинды старт/стоп
binds_frame = ttk.Frame(root)
binds_frame.pack(pady=15)

ttk.Label(binds_frame, text="Клавиша старт:").grid(row=0, column=0, padx=5, sticky='w')
start_key_entry = ttk.Entry(binds_frame, width=12)
start_key_entry.insert(0, default_start_key)

ttk.Label(binds_frame, text="Клавиша стоп:").grid(row=1, column=0, padx=5, sticky='w')
stop_key_entry = ttk.Entry(binds_frame, width=12)
stop_key_entry.insert(0, default_stop_key)

ttk.Button(binds_frame, text="Задать старт", command=lambda: keyboard.add_hotkey(start_key_entry.get(), start_automation)).grid(row=0, column=1, padx=10)
ttk.Button(binds_frame, text="Задать стоп", command=lambda: keyboard.add_hotkey(stop_key_entry.get(), stop_automation)).grid(row=1, column=1, padx=10)

# Управление
buttons_frame = ttk.Frame(root)
buttons_frame.pack(pady=20)

start_btn = ttk.Button(buttons_frame, text="Запустить", command=lambda: start_automation())
start_btn.grid(row=0, column=0, padx=10)

stop_btn = ttk.Button(buttons_frame, text="Остановить", command=lambda: stop_automation(), state='disabled')
stop_btn.grid(row=0, column=1, padx=10)

# Статус
status_label = ttk.Label(root, text="Статус: Остановлено", font=("Helvetica", 14),
                         foreground="#bdc3c7", background="#34495e")
status_label.pack(pady=10)

# Объявление функций
def update_button_state():
    if running:
        start_btn.config(state='disabled')
        stop_btn.config(state='normal')
    else:
        start_btn.config(state='normal')
        stop_btn.config(state='disabled')

def start_automation():
    global running, thread
    if not running:
        try:
            battle_time = float(battle_time_var.get())
            iterations = int(iterations_var.get())
        except ValueError:
            status_label.config(text="Ошибка: Проверьте ввод")
            return
        running = True
        thread = threading.Thread(target=automation_loop, args=(battle_time, iterations), daemon=True)
        thread.start()
        update_button_state()
        status_label.config(text="Статус: В работе")

def stop_automation():
    global running
    if running:
        running = False
        if thread and thread.is_alive():
            thread.join()
        update_button_state()
        status_label.config(text="Статус: Остановлено")

def automation_loop(battle_time, iterations):
    for i in range(1, iterations + 1):
        if not running:
            break
        time.sleep(1)  # небольшая задержка перед каждым запуском
        # зажимание клавиши 'f', ожидание, отпускание
        keyboard.press('f')
        time.sleep(battle_time)
        keyboard.release('f')
        keyboard.press_and_release('tab')

# Обработка горячих клавиш
def bind_start():
    hotkey = start_key_entry.get()
    keyboard.add_hotkey(hotkey, start_automation)

def bind_stop():
    hotkey = stop_key_entry.get()
    keyboard.add_hotkey(hotkey, stop_automation)

# Инициализация биндингов
bind_start()
bind_stop()

# Проверка на нажатие F2 для клика мышью
def mouse_click_on_press():
    def on_press(key):
        if key == keyboard.Key.f2:
            # Выполняем клик мышью
            pyautogui.click()
            print("Клик мышью выполнен!")

    with keyboard.Listener(on_press=on_press) as listener:
        listener.join()

# Запуск слушателя клика
click_thread = threading.Thread(target=mouse_click_on_press, daemon=True)
click_thread.start()

# Обновление интерфейса
def periodic_update():
    update_button_state()
    root.after(500, periodic_update)

periodic_update()

# Запуск интерфейса
root.mainloop()