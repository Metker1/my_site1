import time
import keyboard

# список для сохранения команд: (клавиша, задержка после нажатия)
commands = []

def начать_запись():
    global commands
    commands = []
    print("Начинаем запись. Нажмите ESC для завершения.")
    last_time = time.time()

    while True:
        if keyboard.is_pressed('esc'):
            print("Запись завершена.")
            break
        event = keyboard.read_event(suppress=False)
        if event.event_type == keyboard.KEY_DOWN:
            current_time = time.time()
            delay = current_time - last_time
            commands.append((event.name, delay))
            last_time = current_time
            print(f"Записано: {event.name} с задержкой {delay:.2f} сек")
        time.sleep(0.01)

def повторить():
    print("Воспроизведение через 3 секунды...")
    time.sleep(3)
    for key, delay in commands:
        time.sleep(delay)
        keyboard.press_and_release(key)
        print(f"Отпущена клавиша: {key}")
    print("Воспроизведение завершено.")

if __name__ == "__main__":
    input("Подготовьтесь в игре, затем нажмите Enter для начала записи.")
    начать_запись()
    input("Нажмите Enter для воспроизведения через 3 секунды.")
    повторить()