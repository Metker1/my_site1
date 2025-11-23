from pynput import keyboard, mouse
import pyautogui

# Создаем объекты для управления мышью
mouse_controller = mouse.Controller()

# Определяем, какая клавиша будет запускать клик
TRIGGER_KEY = keyboard.Key.f2

def on_press(key):
    if key == TRIGGER_KEY:
        # Выполняем клик мышью (левая кнопка)
        pyautogui.mouseDown()
        print("Клик выполнен!")

# Запускаем слушатель клавиатуры
with keyboard.Listener(on_press=on_press) as listener:
    print("Нажмите F2 для выполнения клика мыши. Для выхода нажмите Esc.")
    listener.join()