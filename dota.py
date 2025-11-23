import requests
import numpy as np
import tkinter as tk
from tkinter import ttk, messagebox
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

API_KEY = 'YOUR_ALPHA_VANTAGE_API_KEY'  # Замените на ваш API ключ

def get_historical_rates(currency, days=30):
    url = 'https://www.alphavantage.co/query'
    params = {
        'function': 'FX_DAILY',
        'from_symbol': currency,
        'to_symbol': 'USD',  # Анализируем курс к USD
        'apikey': API_KEY,
        'outputsize': 'full'  # Получить полный набор данных
    }
    response = requests.get(url, params=params)
    data = response.json()
    if 'Time Series FX (Daily)' not in data:
        raise ValueError('Ошибка получения данных: ' + data.get('Error Message', 'Нет данных'))
    time_series = data['Time Series FX (Daily)']
    dates = sorted(time_series.keys(), reverse=True)[:days]
    rates = []
    for date in dates:
        rate = float(time_series[date]['4. close'])
        rates.append((date, rate))
    rates.reverse()
    return rates

def analyze_trends(rates):
    if len(rates) < 2:
        return 'Недостаточно данных'
    x = np.arange(len(rates))
    y = np.array([rate for _, rate in rates])
    slope, _ = np.polyfit(x, y, 1)
    if slope > 0:
        return 'Валюта растет'
    elif slope < 0:
        return 'Валюта падает'
    else:
        return 'Валюта остается без изменений'

class CurrencyAnalyzerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Анализ курса валют")
        self.root.configure(bg='#f0f4f8')
        self.create_widgets()

    def create_widgets(self):
        style = ttk.Style()
        style.configure('TLabel', background='#f0f4f8', font=('Arial', 12))
        style.configure('TButton', font=('Arial', 12, 'bold'))

        # Ввод валюты
        ttk.Label(self.root, text="Введите валюту (например, EUR):").grid(row=0, column=0, padx=15, pady=10, sticky='w')
        self.currency_entry = ttk.Entry(self.root, width=15)
        self.currency_entry.grid(row=0, column=1, padx=15, pady=10)

        # Кнопка анализа
        self.analyze_button = ttk.Button(self.root, text="Анализировать", command=self.perform_analysis)
        self.analyze_button.grid(row=1, column=0, columnspan=2, pady=10)

        # Результат анализа
        self.result_label = ttk.Label(self.root, text="", font=('Arial', 14, 'bold'))
        self.result_label.grid(row=2, column=0, columnspan=2, pady=8)

        # График
        self.figure = Figure(figsize=(7, 4), dpi=100)
        self.ax = self.figure.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.figure, master=self.root)
        self.canvas.get_tk_widget().grid(row=3, column=0, columnspan=2, pady=10)

    def perform_analysis(self):
        currency = self.currency_entry.get().strip().upper()
        if not currency:
            messagebox.showwarning("Ввод пустой", "Пожалуйста, введите валюту.")
            return
        try:
            rates = get_historical_rates(currency)
            trend = analyze_trends(rates)
            self.result_label.config(text=f"Общий тренд: {trend}")
            self.plot_rates(rates, currency)
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    def plot_rates(self, rates, currency):
        self.ax.clear()
        dates = [d for d, _ in rates]
        values = [r for _, r in rates]
        self.ax.plot(dates, values, marker='o', color='#007acc')
        self.ax.set_title(f'{currency}/USD — Курсы за последние 30 дней', fontsize=14)
        self.ax.set_xlabel('Дата', fontsize=12)
        self.ax.set_ylabel('Курс', fontsize=12)
        self.ax.tick_params(axis='x', rotation=45)
        self.ax.grid(True, linestyle='--', alpha=0.5)
        self.figure.tight_layout()
        self.canvas.draw()

if __name__ == "__main__":
    root = tk.Tk()
    app = CurrencyAnalyzerApp(root)
    root.mainloop()