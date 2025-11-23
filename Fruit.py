import cv2
import numpy as np
import pyautogui
import time
import threading
import tkinter as tk
from tkinter import ttk
import keyboard

# Глобальные переменные
running = False
thread = None

# Загружаем шаблон
template = cv2.imread('99.jpg               ', cv2.IMREAD_UNCHANGED)
w, h = template.shape[1], template.shape[0]

def script_loop():
    global running
    while running:
        # Скриншот всего экрана
        screenshot = pyautogui.screenshot()
        screenshot_rgb = np.array(screenshot)
        # Конвертация в BGR для OpenCV
        screenshot_bgr = cv2.cvtColor(screenshot_rgb, cv2.COLOR_RGB2BGR)

        # Поиск шаблона
        result = cv2.matchTemplate(screenshot_bgr, template, cv2.TM_CCOEFF_NORMED)
        threshold = 0.8
        loc = np.where(result >= threshold)
        keyboard.press('tab')
        time.sleep(0.01)

        if len(loc[0]) > 0:
            pt = (loc[1][0], loc[0][0])
            center_x = pt[0] + w // 2
            center_y = pt[1] + h // 2

            pyautogui.mouseDown(center_x, center_y)
            pyautogui.moveTo(2071, 1041, duration=1)
            print(f"Клик по координатам: {center_x}, {center_y}")
            time.sleep(1)
            pyautogui.mouseUp()

            time.sleep(1)
            keyboard.press('esc')
            time.sleep(0.03)
            keyboard.release('esc')
            time.sleep(1)
            keyboard.release('tab')

            pyautogui.mouseDown()
            time.sleep(19)
            pyautogui.mouseUp()
        else:
            time.sleep(0.5)

def start_script():
    global running, thread
    if not running:
        running = True
        thread = threading.Thread(target=script_loop)
        thread.start()
        update_status("Запущено", "green")

def stop_script():
    global running
    running = False
    if thread is not None:
        thread.join()
    update_status("Остановлено", "red")

def toggle_script(event=None):
    if running:
        stop_script()
    else:
        start_script()

def update_status(text, color):
    status_label.config(text=f"Статус: {text}", foreground=color)

# Создаем красивое окно
root = tk.Tk()
root.title("Автоматизация поиска")
root.geometry("400x250")
root.configure(bg="#2c3e50")
root.resizable(False, False)

# Заголовок
title_label = tk.Label(root, text="Автоматический поиск и клик", font=("Helvetica", 16, "bold"), bg="#2c3e50", fg="#ecf0f1")
title_label.pack(pady=15)

# Статус
status_label = tk.Label(root, text="Статус: Остановлено", font=("Helvetica", 14), bg="#2c3e50", fg="red")
status_label.pack(pady=10)

# Кнопки управления
button_frame = tk.Frame(root, bg="#2c3e50")
button_frame.pack(pady=10)

start_button = tk.Button(button_frame, text="Старт", command=start_script, font=("Helvetica", 12), bg="#27ae60", fg="white", width=10, relief="raised")
start_button.grid(row=0, column=0, padx=10)

stop_button = tk.Button(button_frame, text="Стоп", command=stop_script, font=("Helvetica", 12), bg="#c0392b", fg="white", width=10, relief="raised")
stop_button.grid(row=0, column=1, padx=10)

# Инструкции
instr_label = tk.Label(root, text="Нажмите 'S' для запуска\n'N' для остановки", font=("Helvetica", 10), bg="#2c3e50", fg="#bdc3c7")
instr_label.pack(pady=10)

# Бинды клавиш
root.bind('<Key-s>', lambda e: start_script())
root.bind('<Key-n>', lambda e: stop_script())

root.mainloop()