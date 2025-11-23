import time
import threading
import keyboard
import pyautogui
import cv2
import numpy as np

time.sleep(3)
# Функция поиска и наведения на предмет
def find_and_focus_item(template_path, threshold=0.8):
    template = cv2.imread(template_path, cv2.IMREAD_UNCHANGED)
    if template is None:
        print("Не удалось загрузить изображение шаблона.")
        return
    w, h = template.shape[1], template.shape[0]
    screenshot = pyautogui.screenshot()
    screenshot_rgb = np.array(screenshot)
    screenshot_bgr = cv2.cvtColor(screenshot_rgb, cv2.COLOR_RGB2BGR)
    result = cv2.matchTemplate(screenshot_bgr, template, cv2.TM_CCOEFF_NORMED)
    loc = np.where(result >= threshold)
    if len(loc[0]) > 0:
        pt = (loc[1][0], loc[0][0])
        center_x = int(pt[0] + w / 2)
        center_y = int(pt[1] + h / 2)
        # Наводим курсор и кликаем на предмет
        pyautogui.moveTo(center_x, center_y, duration=0.2)
        pyautogui.click()
        print(f"Предмет найден и кликнут по координатам: {center_x}, {center_y}")
    else:
        print("Предмет не найден.")


def main():
    # 1. Зажимает F 31 секунд и отпускает, повторяет 2 раза
    for _ in range(2):
        keyboard.press('f')
        time.sleep(24)
        keyboard.release('f')
        time.sleep(0.1)  # небольшая задержка между повторениями

    keyboard.press('tab')
    time.sleep(0.01)
    keyboard.release('tab')

    for _ in range(2):
        pyautogui.moveTo(147, 226)
        pyautogui.mouseDown()
        time.sleep(0.2)
        pyautogui.mouseUp()
        pyautogui.mouseDown()
        time.sleep(0.2)
        pyautogui.mouseUp()
    time.sleep(1)
    keyboard.press('tab')
    time.sleep(0.2)
    keyboard.release('tab')




    time.sleep(1)
    # 2. Нажимает D 1 секунду и отпускает
    keyboard.press('d')
    time.sleep(1)
    keyboard.release('d')

    # 3. Нажимает Tab 0.01 секунду


    for _ in range(2):
        keyboard.press('tab')
        time.sleep(0.01)
        keyboard.release('tab')
        template_path = '678.jpg'  # замените на путь к вашему изображению
        find_and_focus_item(template_path)
        pyautogui.mouseDown()
        time.sleep(0.2)
        pyautogui.mouseUp()
        pyautogui.mouseDown()
        time.sleep(0.2)
        pyautogui.mouseUp()
        keyboard.press('tab')
        time.sleep(0.01)
        keyboard.release('tab')
        time.sleep(1)
        pyautogui.mouseDown()
        time.sleep(18)
        pyautogui.mouseUp()

    keyboard.press('tab')
    time.sleep(0.01)
    keyboard.release('tab')

    for _ in range(2):
        pyautogui.moveTo(147, 226)
        pyautogui.mouseDown()
        time.sleep(0.2)
        pyautogui.mouseUp()
        pyautogui.mouseDown()
        time.sleep(0.2)
        pyautogui.mouseUp()

    keyboard.press('tab')
    time.sleep(0.1)
    keyboard.release('tab')

    keyboard.press('s')
    time.sleep(2)
    keyboard.release('s')
    keyboard.press('a')
    time.sleep(0.5)
    keyboard.release('a')
    keyboard.release('s')
    keyboard.press('w')
    time.sleep(0.5)
    keyboard.release('w')


    for _ in range(2):
        keyboard.press('tab')
        time.sleep(0.01)
        keyboard.release('tab')
        template_path = '677.jpg'  # замените на путь к вашему изображению
        find_and_focus_item(template_path)
        pyautogui.mouseDown()
        time.sleep(0.2)
        pyautogui.mouseUp()
        pyautogui.mouseDown()
        time.sleep(0.2)
        pyautogui.mouseUp()
        keyboard.press('tab')
        time.sleep(0.01)
        keyboard.release('tab')
        time.sleep(1)
        pyautogui.mouseDown()
        time.sleep(18)
        pyautogui.mouseUp()

    keyboard.press('tab')
    time.sleep(0.01)
    keyboard.release('tab')

    for _ in range(2):
        pyautogui.moveTo(147, 226)
        pyautogui.mouseDown()
        time.sleep(0.2)
        pyautogui.mouseUp()
        pyautogui.mouseDown()
        time.sleep(0.2)
        pyautogui.mouseUp()

    keyboard.press('tab')
    time.sleep(0.1)
    keyboard.release('tab')





# Запускаем все в отдельном потоке, чтобы не блокировать основной
thread = threading.Thread(target=main)
thread.start()