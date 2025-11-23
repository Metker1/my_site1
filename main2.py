import tkinter as tk
from tkinter import ttk, messagebox

def рассчитать():
    try:
        k1 = float(entry_k1.get())
        k2 = float(entry_k2.get())
        S = float(entry_S.get())

        if k1 <= 1 or k2 <= 1:
            messagebox.showerror("Ошибка", "Коэффициенты должны быть больше 1.")
            return
        if S <= 0:
            messagebox.showerror("Ошибка", "Общая сумма должна быть положительной.")
            return

        denominator = (1 / k1) + (1 / k2)
        ставка_1 = S * (1 / k1) / denominator
        ставка_2 = S * (1 / k2) / denominator

        прибыль_1 = ставка_1 * k1 - S
        прибыль_2 = ставка_2 * k2 - S

        label_result.config(text=(
            f"Ставка на исход 1: {ставка_1:.2f} руб.\n"
            f"Ставка на исход 2: {ставка_2:.2f} руб.\n"
            f"Прибыль при выигрыше 1: {прибыль_1:.2f} руб.\n"
            f"Прибыль при выигрыше 2: {прибыль_2:.2f} руб."
        ))
    except ValueError:
        messagebox.showerror("Ошибка", "Введите корректные числа.")

# Создаем главное окно
root = tk.Tk()
root.title("Беспроигрышная стратегия ставок")
root.geometry("650x700")
root.configure(bg="#f0f4f8")

# Заголовок
ttk.Label(root, text="Беспроигрышная стратегия ставок на спорт", font=("Helvetica", 20, "bold"), background="#f0f4f8").pack(pady=20)

# Стиль
style = ttk.Style()
style.configure("TLabel", font=("Helvetica", 14))
style.configure("TEntry", font=("Helvetica", 14))
style.configure("TButton", font=("Helvetica", 14, "bold"))

# Ввод данных
frame = ttk.Frame(root)
frame.pack(pady=10)

ttk.Label(frame, text="Коэффициент на исход 1:").grid(row=0, column=0, padx=10, pady=10, sticky='e')
entry_k1 = ttk.Entry(frame, width=15)
entry_k1.grid(row=0, column=1, padx=10, pady=10)

ttk.Label(frame, text="Коэффициент на исход 2:").grid(row=1, column=0, padx=10, pady=10, sticky='e')
entry_k2 = ttk.Entry(frame, width=15)
entry_k2.grid(row=1, column=1, padx=10, pady=10)

ttk.Label(frame, text="Общая сумма ставки (руб):").grid(row=2, column=0, padx=10, pady=10, sticky='e')
entry_S = ttk.Entry(frame, width=15)
entry_S.grid(row=2, column=1, padx=10, pady=10)

# Кнопка
btn = ttk.Button(root, text="Рассчитать ставки", command=рассчитать)
btn.pack(pady=20)

# Результат
label_result = ttk.Label(root, text="", font=("Helvetica", 14), background="#f0f4f8")
label_result.pack(pady=10)

# Запуск
root.mainloop()