import tkinter as tk
from tkinter import ttk, messagebox

# Ваша функция анализа
def анализировать_матч(данные_команды1, данные_команды2):
    def оценка_силы(данные):
        победы = данные['победы']
        проигрыши = данные['проигрыши']
        голы_забитые = данные['голы_забитые']
        голы_пропущенные = данные['голы_пропущенные']
        последние_игры = данные['последние_игры']
        победность = победы / (победы + проигрыши) if (победы + проигрыши) > 0 else 0
        голевая_разница = голы_забитые - голы_пропущенные
        силу = (победность * 50) + (голевая_разница * 2) + (последние_игры * 5)
        return силу

    сила_команды1 = оценка_силы(данные_команды1)
    сила_команды2 = оценка_силы(данные_команды2)

    if сила_команды1 > сила_команды2:
        прогноз = 'Первая команда скорее выиграет'
    elif сила_команды2 > сила_команды1:
        прогноз = 'Вторая команда скорее выиграет'
    else:
        прогноз = 'Вероятна ничья или равенство сил'
    return прогноз

# Создаем главное окно
root = tk.Tk()
root.title("Анализ матчей")
root.geometry("800x700")
root.configure(bg='#1e1e2f')

# Заголовок
title = tk.Label(root, text="Прогноз матча", font=("Helvetica Neue", 28, "bold"), fg="#00ffff", bg='#1e1e2f')
title.pack(pady=20)

# Фреймы для команд
frame1 = tk.LabelFrame(root, text="Данные первой команды", font=("Helvetica Neue", 14, "bold"), fg="#ffffff", bg='#2c2c3f', padx=10, pady=10)
frame1.pack(fill='x', padx=20, pady=10)

frame2 = tk.LabelFrame(root, text="Данные второй команды", font=("Helvetica Neue", 14, "bold"), fg="#ffffff", bg='#2c2c3f', padx=10, pady=10)
frame2.pack(fill='x', padx=20, pady=10)

fields1 = {}
fields2 = {}
labels = ['Победы', 'Поражения', 'Голы забитые', 'Голы пропущенные', 'Последние игры']

# Создаем поля для первой команды
for i, lbl in enumerate(labels):
    tk.Label(frame1, text=lbl, font=("Helvetica Neue", 12), fg="#ffffff", bg='#2c2c3f').grid(row=i, column=0, sticky='w', padx=10, pady=5)
    entry = tk.Entry(frame1, font=("Helvetica Neue", 12))
    entry.grid(row=i, column=1, padx=10, pady=5)
    fields1[lbl] = entry

# Создаем поля для второй команды
for i, lbl in enumerate(labels):
    tk.Label(frame2, text=lbl, font=("Helvetica Neue", 12), fg="#ffffff", bg='#2c2c3f').grid(row=i, column=0, sticky='w', padx=10, pady=5)
    entry = tk.Entry(frame2, font=("Helvetica Neue", 12))
    entry.grid(row=i, column=1, padx=10, pady=5)
    fields2[lbl] = entry

# Функция для анализа и вывода результата
def анализировать():
    try:
        данные1 = {
            'победы': int(fields1['Победы'].get()),
            'проигрыши': int(fields1['Поражения'].get()),
            'голы_забитые': int(fields1['Голы забитые'].get()),
            'голы_пропущенные': int(fields1['Голы пропущенные'].get()),
            'последние_игры': int(fields1['Последние игры'].get())
        }
        данные2 = {
            'победы': int(fields2['Победы'].get()),
            'проигрыши': int(fields2['Поражения'].get()),
            'голы_забитые': int(fields2['Голы забитые'].get()),
            'голы_пропущенные': int(fields2['Голы пропущенные'].get()),
            'последние_игры': int(fields2['Последние игры'].get())
        }
    except ValueError:
        messagebox.showerror("Ошибка", "Пожалуйста, введите все числовые значения.")
        return

    прогноз = анализировать_матч(данные1, данные2)
    результат_label.config(text=прогноз)

# Кнопка анализа
анализ_button = tk.Button(root, text="Произвести анализ", font=("Helvetica Neue", 14, "bold"), bg="#4CAF50", fg="#ffffff", padx=20, pady=10, command=анализировать)
анализ_button.pack(pady=20)

# Метка для результата
результат_label = tk.Label(root, text="", font=("Helvetica Neue", 16, "bold"), fg="#ffd700", bg='#1e1e2f')
результат_label.pack(pady=10)

# Фрейм для итоговой оценки победителя
winner_frame = tk.Frame(root, bg='#1e1e2f')
winner_frame.pack(pady=10)

# Текстовая метка для победителя
winner_label = tk.Label(winner_frame, text="", font=("Helvetica Neue", 18, "bold"), fg="#ff6347", bg='#1e1e2f')
winner_label.pack(pady=10)

# Функция сравнения параметров и определения победителя
def определить_победителя():
    try:
        data1 = {
            'победы': int(fields1['Победы'].get()),
            'проигрыши': int(fields1['Поражения'].get()),
            'голы_забитые': int(fields1['Голы забитые'].get()),
            'голы_пропущенные': int(fields1['Голы пропущенные'].get()),
            'последние_игры': int(fields1['Последние игры'].get())
        }
        data2 = {
            'победы': int(fields2['Победы'].get()),
            'проигрыши': int(fields2['Поражения'].get()),
            'голы_забитые': int(fields2['Голы забитые'].get()),
            'голы_пропущенные': int(fields2['Голы пропущенные'].get()),
            'последние_игры': int(fields2['Последние игры'].get())
        }
    except ValueError:
        messagebox.showerror("Ошибка", "Пожалуйста, введите все числовые значения.")
        return

    # Простая логика для определения победителя
    strength1 = (data1['победы'] - data1['проигрыши']) + (data1['голы_забитые'] - data1['голы_пропущенные']) + data1['последние_игры']
    strength2 = (data2['победы'] - data2['проигрыши']) + (data2['голы_забитые'] - data2['голы_пропущенные']) + data2['последние_игры']

    if strength1 > strength2:
        winner_text = "Побеждает: Первая команда!"
    elif strength2 > strength1:
        winner_text = "Побеждает: Вторая команда!"
    else:
        winner_text = "Ничья!"

    winner_label.config(text=winner_text)

# Кнопка для определения победителя
winner_button = tk.Button(root, text="Определить победителя", font=("Helvetica Neue", 14, "bold"), bg="#2196F3", fg="#ffffff", padx=20, pady=10, command=определить_победителя)
winner_button.pack(pady=20)

# Запускаем интерфейс
root.mainloop()