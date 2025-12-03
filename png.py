import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, scrolledtext
from datetime import datetime, timedelta
import json
import random
import re
import threading
import time
from queue import Queue
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from collections import deque


class UserGameTracker:
    def __init__(self, root):
        self.root = root
        self.root.title("Neon Casino - Внутренний трекер игровой активности")
        self.root.geometry("1600x900")
        self.root.configure(bg='#0a0a16')

        # Внутренние структуры данных вместо SQLite
        self.users = []  # Список пользователей
        self.game_logs = []  # Список игровых сессий
        self.active_bets = []  # Активные ставки в реальном времени
        self.live_events = deque(maxlen=50)  # Журнал живых событий

        # Очередь для обновления UI из фонового потока
        self.ui_queue = Queue()

        # Флаги симуляции
        self.simulation_active = False
        self.simulation_thread = None

        self.games_list = [  # Список доступных игр
            "KITCHEN: HEAT IT UP!",
            "THUNDER ON THE TRACK",
            "Кости Судьбы",
            "ROCKET: TO THE MOON!",
            "Красное или Черное",
            "MINEFIELD: THE LOGICAL RUSH",
            "Гробница Фараона: Свиток Удачи",
            "Теннис",
            "Бинарные опционы",
            "Хомяк Кликер"
        ]

        # Статистика симуляции
        self.simulation_stats = {
            'total_bets': 0,
            'active_players': 0,
            'total_wagered': 0,
            'peak_concurrent': 0,
            'events_per_minute': 0
        }

        # Коэффициенты для разных игр (вероятность выигрыша, множитель)
        self.game_odds = {
            "KITCHEN: HEAT IT UP!": {"win_prob": 0.45, "multiplier_range": (1.5, 10.0)},
            "THUNDER ON THE TRACK": {"win_prob": 0.35, "multiplier_range": (2.0, 20.0)},
            "Кости Судьбы": {"win_prob": 0.5, "multiplier_range": (1.2, 5.0)},
            "ROCKET: TO THE MOON!": {"win_prob": 0.25, "multiplier_range": (3.0, 50.0)},
            "Красное или Черное": {"win_prob": 0.49, "multiplier_range": (1.95, 1.95)},
            "MINEFIELD: THE LOGICAL RUSH": {"win_prob": 0.6, "multiplier_range": (1.1, 3.0)},
            "Гробница Фараона: Свиток Удачи": {"win_prob": 0.4, "multiplier_range": (1.5, 15.0)},
            "Теннис": {"win_prob": 0.48, "multiplier_range": (1.8, 2.5)},
            "Бинарные опционы": {"win_prob": 0.55, "multiplier_range": (1.8, 2.0)},
            "Хомяк Кликер": {"win_prob": 0.7, "multiplier_range": (1.05, 2.0)}
        }

        # Загрузка данных из localStorage-подобного формата
        self.load_website_data()

        # Стили
        self.setup_styles()

        # Интерфейс
        self.setup_ui()

        # Загрузка данных в интерфейс
        self.load_users_table()
        self.update_overall_stats()

        # Запуск обработки очереди UI
        self.process_ui_queue()

    def extract_data_from_html(self):
        """
        Эмуляция извлечения данных из HTML/JavaScript кода сайта
        В реальной ситуации эти данные были бы получены из localStorage браузера
        """
        # Эмуляция структуры данных из веб-сайта
        website_users_data = [
            {"username": "Алексей_К", "balance": 15400, "vip_status": "gold", "registration_date": "2023-01-15"},
            {"username": "Марина_С", "balance": 28900, "vip_status": "platinum", "registration_date": "2023-03-22"},
            {"username": "Дмитрий_И", "balance": 8700, "vip_status": "silver", "registration_date": "2023-02-10"},
            {"username": "Сергей_П", "balance": 4300, "vip_status": "bronze", "registration_date": "2023-04-05"},
            {"username": "Ольга_В", "balance": 2100, "vip_status": "none", "registration_date": "2023-05-18"},
            {"username": "Иван_М", "balance": 12600, "vip_status": "gold", "registration_date": "2023-06-30"},
            {"username": "Анна_К", "balance": 1800, "vip_status": "none", "registration_date": "2023-07-12"},
            {"username": "Андрей_Н", "balance": 5900, "vip_status": "silver", "registration_date": "2023-08-25"}
        ]

        # Эмуляция игровой активности из JavaScript кода
        website_game_activity = [
            {"username": "Алексей_К", "game": "THUNDER ON THE TRACK", "bet": 1500, "win": 3200,
             "timestamp": "2024-01-15 14:30:00"},
            {"username": "Марина_С", "game": "Кости Судьбы", "bet": 800, "win": 0, "timestamp": "2024-01-15 14:25:00"},
            {"username": "Дмитрий_И", "game": "ROCKET: TO THE MOON!", "bet": 2000, "win": 4500,
             "timestamp": "2024-01-15 14:20:00"},
            {"username": "Сергей_П", "game": "Бинарные опционы", "bet": 500, "win": 950,
             "timestamp": "2024-01-15 14:15:00"},
            {"username": "Ольга_В", "game": "Красное или Черное", "bet": 300, "win": 600,
             "timestamp": "2024-01-15 14:10:00"},
            {"username": "Иван_М", "game": "MINEFIELD: THE LOGICAL RUSH", "bet": 1200, "win": 0,
             "timestamp": "2024-01-15 14:05:00"},
            {"username": "Анна_К", "game": "Гробница Фараона", "bet": 400, "win": 850,
             "timestamp": "2024-01-15 14:00:00"},
            {"username": "Андрей_Н", "game": "Теннис", "bet": 700, "win": 1400, "timestamp": "2024-01-15 13:55:00"},
            {"username": "Алексей_К", "game": "Хомяк Кликер", "bet": 1000, "win": 2100,
             "timestamp": "2024-01-15 13:50:00"},
            {"username": "Марина_С", "game": "KITCHEN: HEAT IT UP!", "bet": 600, "win": 0,
             "timestamp": "2024-01-15 13:45:00"}
        ]

        return website_users_data, website_game_activity

    def load_website_data(self):
        """Загрузка данных из веб-сайта Neon Casino"""
        try:
            # Эмуляция получения данных с сайта
            website_users, website_activity = self.extract_data_from_html()

            # Преобразование пользователей
            self.users = []
            for i, user_data in enumerate(website_users, 1):
                user = {
                    'id': i,
                    'username': user_data['username'],
                    'registration_date': user_data['registration_date'],
                    'vip_status': user_data['vip_status'],
                    'balance': user_data['balance'],
                    'active': False,  # Флаг активности пользователя
                    'current_game': None,  # Текущая игра пользователя
                    'last_action': None  # Время последнего действия
                }
                self.users.append(user)

            # Преобразование игровой активности
            self.game_logs = []
            session_id = 1

            # Создаем словарь для быстрого поиска ID пользователя по имени
            username_to_id = {user['username']: user['id'] for user in self.users}

            for activity in website_activity:
                user_id = username_to_id.get(activity['username'])
                if user_id:
                    session = {
                        'id': session_id,
                        'user_id': user_id,
                        'game_name': activity['game'],
                        'start_time': activity['timestamp'],
                        'duration': random.randint(60, 7200),
                        'bet_amount': activity['bet'],
                        'win_amount': activity['win'],
                        'profit': activity['win'] - activity['bet'],
                        'status': 'completed'
                    }
                    self.game_logs.append(session)
                    session_id += 1

            # Дополняем историю случайными сессиями для полноты данных
            self.generate_additional_sessions()

            print(f"Загружено {len(self.users)} пользователей и {len(self.game_logs)} игровых сессий с веб-сайта")

        except Exception as e:
            print(f"Ошибка загрузки данных с веб-сайта: {e}")
            # Если не удалось загрузить данные с сайта, генерируем тестовые данные
            self.generate_sample_data()

    def generate_additional_sessions(self):
        """Генерация дополнительных игровых сессий для полноты данных"""
        session_id = len(self.game_logs) + 1

        for user in self.users:
            # Добавляем случайное количество дополнительных сессий (3-10 на пользователя)
            num_additional_sessions = random.randint(3, 10)

            for _ in range(num_additional_sessions):
                game_name = random.choice(self.games_list)
                start_time = self.random_date()
                duration = random.randint(60, 7200)
                bet_amount = random.randint(100, 5000)

                # Используем коэффициенты игры для определения результата
                odds = self.game_odds.get(game_name, {"win_prob": 0.5, "multiplier_range": (1.5, 5.0)})
                is_win = random.random() < odds["win_prob"]
                multiplier = random.uniform(*odds["multiplier_range"])
                win_amount = round(bet_amount * multiplier) if is_win else 0

                session = {
                    "id": session_id,
                    "user_id": user["id"],
                    "game_name": game_name,
                    "start_time": start_time,
                    "duration": duration,
                    "bet_amount": bet_amount,
                    "win_amount": win_amount,
                    "profit": win_amount - bet_amount,
                    "status": "completed"
                }

                self.game_logs.append(session)
                session_id += 1

    def generate_sample_data(self):
        """Генерация тестовых данных для демонстрации (резервный метод)"""
        sample_users = [
            {"id": 1, "username": "Алексей_К", "registration_date": "2023-01-15", "vip_status": "gold",
             "balance": 15400, "active": False, "current_game": None, "last_action": None},
            {"id": 2, "username": "Марина_С", "registration_date": "2023-03-22", "vip_status": "platinum",
             "balance": 28900, "active": False, "current_game": None, "last_action": None},
            {"id": 3, "username": "Дмитрий_И", "registration_date": "2023-02-10", "vip_status": "silver",
             "balance": 8700, "active": False, "current_game": None, "last_action": None},
            {"id": 4, "username": "Сергей_П", "registration_date": "2023-04-05", "vip_status": "bronze",
             "balance": 4300, "active": False, "current_game": None, "last_action": None},
            {"id": 5, "username": "Ольга_В", "registration_date": "2023-05-18", "vip_status": "none", "balance": 2100,
             "active": False, "current_game": None, "last_action": None},
            {"id": 6, "username": "Иван_М", "registration_date": "2023-06-30", "vip_status": "gold", "balance": 12600,
             "active": False, "current_game": None, "last_action": None},
            {"id": 7, "username": "Анна_К", "registration_date": "2023-07-12", "vip_status": "none", "balance": 1800,
             "active": False, "current_game": None, "last_action": None},
            {"id": 8, "username": "Андрей_Н", "registration_date": "2023-08-25", "vip_status": "silver",
             "balance": 5900, "active": False, "current_game": None, "last_action": None}
        ]

        self.users = sample_users

        # Генерация игровых сессий
        game_sessions = []
        session_id = 1

        for user in sample_users:
            user_id = user["id"]
            num_sessions = random.randint(5, 20)

            for _ in range(num_sessions):
                game_name = random.choice(self.games_list)
                start_time = self.random_date()
                duration = random.randint(60, 7200)
                bet_amount = random.randint(100, 5000)

                odds = self.game_odds.get(game_name, {"win_prob": 0.5, "multiplier_range": (1.5, 5.0)})
                is_win = random.random() < odds["win_prob"]
                multiplier = random.uniform(*odds["multiplier_range"])
                win_amount = round(bet_amount * multiplier) if is_win else 0

                session = {
                    "id": session_id,
                    "user_id": user_id,
                    "game_name": game_name,
                    "start_time": start_time,
                    "duration": duration,
                    "bet_amount": bet_amount,
                    "win_amount": win_amount,
                    "profit": win_amount - bet_amount,
                    "status": "completed"
                }

                game_sessions.append(session)
                session_id += 1

        self.game_logs = game_sessions

    def random_date(self):
        """Генерация случайной даты за последние 30 дней"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        random_date = start_date + timedelta(
            seconds=random.randint(0, int((end_date - start_date).total_seconds()))
        )
        return random_date.strftime("%Y-%m-%d %H:%M:%S")

    def setup_styles(self):
        self.style = ttk.Style()
        self.style.theme_use('clam')

        # Цветовая схема Neon Casino (как на сайте)
        self.colors = {
            'bg': '#0a0a16',
            'card_bg': '#141428',
            'accent_pink': '#ff00ff',
            'accent_blue': '#00ffff',
            'accent_green': '#39ff14',
            'accent_purple': '#bf00ff',
            'accent_orange': '#ff6600',
            'accent_yellow': '#ffff00',
            'text_primary': '#ffffff',
            'text_secondary': '#cccccc',
            'success': '#00ff88',
            'warning': '#ffaa00',
            'danger': '#ff4444'
        }

    def setup_ui(self):
        # Заголовок
        header_frame = tk.Frame(self.root, bg=self.colors['bg'])
        header_frame.pack(fill='x', padx=20, pady=10)

        title_label = tk.Label(
            header_frame,
            text="🎮 Внутренняя система отслеживания игр Neon Casino",
            font=('Arial', 20, 'bold'),
            fg=self.colors['accent_pink'],
            bg=self.colors['bg']
        )
        title_label.pack()

        subtitle_label = tk.Label(
            header_frame,
            text="Данные загружены с веб-сайта Neon Casino | Симуляция активных ставок ВКЛЮЧЕНА",
            font=('Arial', 12),
            fg=self.colors['accent_green'],
            bg=self.colors['bg']
        )
        subtitle_label.pack()

        # Основной контейнер
        main_container = tk.Frame(self.root, bg=self.colors['bg'])
        main_container.pack(fill='both', expand=True, padx=20, pady=10)

        # Левая панель - пользователи и управление
        left_frame = tk.Frame(main_container, bg=self.colors['card_bg'], relief='ridge', bd=2)
        left_frame.pack(side='left', fill='y', padx=(0, 10))

        self.setup_left_panel(left_frame)

        # Правая панель - детали и статистика
        right_frame = tk.Frame(main_container, bg=self.colors['bg'])
        right_frame.pack(side='right', fill='both', expand=True)

        # Вкладки
        notebook = ttk.Notebook(right_frame)
        notebook.pack(fill='both', expand=True)

        # Вкладка игровой активности
        activity_frame = tk.Frame(notebook, bg=self.colors['bg'])
        notebook.add(activity_frame, text='🎯 Детальная статистика')

        self.setup_activity_tab(activity_frame)

        # Вкладка живой симуляции
        live_frame = tk.Frame(notebook, bg=self.colors['bg'])
        notebook.add(live_frame, text='⚡ Живые ставки')

        self.setup_live_tab(live_frame)

        # Вкладка общей статистики
        overall_frame = tk.Frame(notebook, bg=self.colors['bg'])
        notebook.add(overall_frame, text='📈 Общая статистика')

        self.setup_overall_stats_tab(overall_frame)

        # Вкладка анализа игр
        analysis_frame = tk.Frame(notebook, bg=self.colors['bg'])
        notebook.add(analysis_frame, text='📊 Аналитика по играм')

        self.setup_analysis_tab(analysis_frame)

        # Вкладка - интеграция с сайтом
        website_frame = tk.Frame(notebook, bg=self.colors['bg'])
        notebook.add(website_frame, text='🌐 Данные с сайта')

        self.setup_website_tab(website_frame)

    def setup_live_tab(self, parent):
        """Вкладка с живыми ставками и симуляцией"""
        # Контейнер для живой симуляции
        live_container = tk.Frame(parent, bg=self.colors['bg'])
        live_container.pack(fill='both', expand=True, padx=10, pady=10)

        # Панель управления симуляцией
        control_frame = tk.Frame(live_container, bg=self.colors['card_bg'], relief='ridge', bd=2)
        control_frame.pack(fill='x', pady=(0, 10))

        # Заголовок
        control_label = tk.Label(
            control_frame,
            text="⚡ ПУЛЬТ УПРАВЛЕНИЯ СИМУЛЯЦИЕЙ",
            font=('Arial', 14, 'bold'),
            fg=self.colors['accent_yellow'],
            bg=self.colors['card_bg'],
            pady=10
        )
        control_label.pack()

        # Кнопки управления
        btn_frame = tk.Frame(control_frame, bg=self.colors['card_bg'])
        btn_frame.pack(pady=10)

        self.start_sim_btn = tk.Button(
            btn_frame,
            text="▶ ЗАПУСК СИМУЛЯЦИИ",
            command=self.start_simulation,
            bg=self.colors['success'],
            fg='white',
            font=('Arial', 12, 'bold'),
            padx=20,
            pady=10
        )
        self.start_sim_btn.pack(side='left', padx=5)

        self.stop_sim_btn = tk.Button(
            btn_frame,
            text="⏹ ОСТАНОВИТЬ СИМУЛЯЦИЮ",
            command=self.stop_simulation,
            bg=self.colors['danger'],
            fg='white',
            font=('Arial', 12, 'bold'),
            padx=20,
            pady=10,
            state='disabled'
        )
        self.stop_sim_btn.pack(side='left', padx=5)

        self.boost_sim_btn = tk.Button(
            btn_frame,
            text="⚡ ТУРБО РЕЖИМ (x3)",
            command=self.toggle_turbo_mode,
            bg=self.colors['accent_orange'],
            fg='white',
            font=('Arial', 12, 'bold'),
            padx=20,
            pady=10
        )
        self.boost_sim_btn.pack(side='left', padx=5)

        # Настройки симуляции
        settings_frame = tk.Frame(control_frame, bg=self.colors['card_bg'])
        settings_frame.pack(pady=10)

        tk.Label(
            settings_frame,
            text="Скорость симуляции:",
            font=('Arial', 10),
            fg=self.colors['text_primary'],
            bg=self.colors['card_bg']
        ).pack(side='left', padx=5)

        self.speed_var = tk.StringVar(value="Нормальная")
        speed_combo = ttk.Combobox(
            settings_frame,
            textvariable=self.speed_var,
            values=["Очень медленная", "Медленная", "Нормальная", "Быстрая", "Очень быстрая"],
            state='readonly',
            width=15
        )
        speed_combo.pack(side='left', padx=5)

        tk.Label(
            settings_frame,
            text="Активных игроков:",
            font=('Arial', 10),
            fg=self.colors['text_primary'],
            bg=self.colors['card_bg']
        ).pack(side='left', padx=(20, 5))

        self.active_players_var = tk.StringVar(value="0")
        active_label = tk.Label(
            settings_frame,
            textvariable=self.active_players_var,
            font=('Arial', 10, 'bold'),
            fg=self.colors['accent_green'],
            bg=self.colors['card_bg']
        )
        active_label.pack(side='left')

        # Статистика симуляции
        stats_frame = tk.Frame(control_frame, bg=self.colors['card_bg'])
        stats_frame.pack(fill='x', padx=20, pady=10)

        self.sim_stats_vars = {
            'total_bets': tk.StringVar(value="0"),
            'total_wagered': tk.StringVar(value="0 ₽"),
            'current_bets': tk.StringVar(value="0"),
            'events_minute': tk.StringVar(value="0"),
            'peak_concurrent': tk.StringVar(value="0")
        }

        stats_labels = [
            ("Всего ставок", self.sim_stats_vars['total_bets']),
            ("Общая сумма ставок", self.sim_stats_vars['total_wagered']),
            ("Активных ставок сейчас", self.sim_stats_vars['current_bets']),
            ("Событий/минуту", self.sim_stats_vars['events_minute']),
            ("Пик игроков", self.sim_stats_vars['peak_concurrent'])
        ]

        for i, (title, var) in enumerate(stats_labels):
            frame = tk.Frame(stats_frame, bg=self.colors['card_bg'])
            frame.grid(row=i // 3, column=i % 3, padx=10, pady=5, sticky='w')

            tk.Label(
                frame,
                text=title + ":",
                font=('Arial', 9),
                fg=self.colors['text_secondary'],
                bg=self.colors['card_bg']
            ).pack(anchor='w')

            tk.Label(
                frame,
                textvariable=var,
                font=('Arial', 11, 'bold'),
                fg=self.colors['accent_blue'],
                bg=self.colors['card_bg']
            ).pack(anchor='w')

        # Разделитель
        separator = tk.Frame(live_container, height=2, bg=self.colors['accent_purple'])
        separator.pack(fill='x', pady=10)

        # Панель активных ставок
        active_bets_frame = tk.Frame(live_container, bg=self.colors['bg'])
        active_bets_frame.pack(fill='both', expand=True)

        # Левая колонка - активные ставки
        bets_left = tk.Frame(active_bets_frame, bg=self.colors['bg'])
        bets_left.pack(side='left', fill='both', expand=True, padx=(0, 10))

        bets_label = tk.Label(
            bets_left,
            text="🎲 АКТИВНЫЕ СТАВКИ В РЕАЛЬНОМ ВРЕМЕНИ",
            font=('Arial', 14, 'bold'),
            fg=self.colors['accent_pink'],
            bg=self.colors['bg'],
            pady=10
        )
        bets_label.pack(anchor='w')

        # Таблица активных ставок
        self.active_bets_tree = ttk.Treeview(
            bets_left,
            columns=('Игрок', 'Игра', 'Ставка', 'Время', 'Статус'),
            show='headings',
            height=15
        )

        self.active_bets_tree.heading('Игрок', text='Игрок')
        self.active_bets_tree.heading('Игра', text='Игра')
        self.active_bets_tree.heading('Ставка', text='Ставка')
        self.active_bets_tree.heading('Время', text='Время')
        self.active_bets_tree.heading('Статус', text='Статус')

        self.active_bets_tree.column('Игрок', width=120)
        self.active_bets_tree.column('Игра', width=180)
        self.active_bets_tree.column('Ставка', width=100, anchor='center')
        self.active_bets_tree.column('Время', width=80, anchor='center')
        self.active_bets_tree.column('Статус', width=100, anchor='center')

        scrollbar_bets = ttk.Scrollbar(bets_left, orient='vertical', command=self.active_bets_tree.yview)
        self.active_bets_tree.configure(yscrollcommand=scrollbar_bets.set)

        self.active_bets_tree.pack(side='left', fill='both', expand=True)
        scrollbar_bets.pack(side='right', fill='y')

        # Правая колонка - лог событий
        bets_right = tk.Frame(active_bets_frame, bg=self.colors['bg'])
        bets_right.pack(side='right', fill='both', expand=True)

        log_label = tk.Label(
            bets_right,
            text="📝 ЖУРНАЛ СОБЫТИЙ",
            font=('Arial', 14, 'bold'),
            fg=self.colors['accent_green'],
            bg=self.colors['bg'],
            pady=10
        )
        log_label.pack(anchor='w')

        # Лог событий
        self.event_log = scrolledtext.ScrolledText(
            bets_right,
            bg='#1a1a2e',
            fg=self.colors['text_primary'],
            font=('Consolas', 9),
            wrap='word',
            height=15
        )
        self.event_log.pack(fill='both', expand=True)
        self.event_log.config(state='disabled')

        # Кнопка очистки лога
        btn_clear_log = tk.Button(
            bets_right,
            text="Очистить журнал",
            command=self.clear_event_log,
            bg=self.colors['accent_blue'],
            fg='white',
            font=('Arial', 9),
            padx=10,
            pady=5
        )
        btn_clear_log.pack(pady=5)

    def setup_website_tab(self, parent):
        """Вкладка с информацией о интеграции с веб-сайтом"""
        # Заголовок
        header_frame = tk.Frame(parent, bg=self.colors['card_bg'], relief='ridge', bd=2)
        header_frame.pack(fill='x', padx=10, pady=10)

        header_label = tk.Label(
            header_frame,
            text="🌐 Интеграция с веб-сайтом Neon Casino",
            font=('Arial', 16, 'bold'),
            fg=self.colors['accent_blue'],
            bg=self.colors['card_bg'],
            pady=10
        )
        header_label.pack()

        # Информация о данных
        info_frame = tk.Frame(parent, bg=self.colors['bg'])
        info_frame.pack(fill='both', expand=True, padx=10, pady=10)

        info_text = tk.Text(
            info_frame,
            bg=self.colors['card_bg'],
            fg=self.colors['text_primary'],
            font=('Arial', 11),
            wrap='word',
            padx=15,
            pady=15
        )

        info_text.insert('end', "⚡ СИСТЕМА СИМУЛЯЦИИ АКТИВНЫХ СТАВОК\n\n")
        info_text.insert('end', "• Реалистичная симуляция игровой активности\n")
        info_text.insert('end', "• Динамические коэффициенты для каждой игры\n")
        info_text.insert('end', "• Живое обновление балансов пользователей\n")
        info_text.insert('end', "• Визуализация ставок в реальном времени\n")
        info_text.insert('end', "• Статистика и аналитика активности\n\n")

        info_text.insert('end', "🎮 ВОЗМОЖНОСТИ СИМУЛЯЦИИ:\n\n")
        info_text.insert('end', "• Запуск/остановка симуляции\n")
        info_text.insert('end', "• Регулировка скорости\n")
        info_text.insert('end', "• Турбо режим (ускоренная симуляция)\n")
        info_text.insert('end', "• Отслеживание активных игроков\n")
        info_text.insert('end', "• Журнал событий в реальном времени\n\n")

        info_text.insert('end', "📊 ДАННЫЕ С ВЕБ-САЙТА:\n\n")
        info_text.insert('end', "• Пользователи и их балансы\n")
        info_text.insert('end', "• История игровой активности\n")
        info_text.insert('end', "• VIP статусы игроков\n")
        info_text.insert('end', "• Статистика по играм\n")

        info_text.config(state='disabled')

        scrollbar = ttk.Scrollbar(info_frame, orient='vertical', command=info_text.yview)
        info_text.configure(yscrollcommand=scrollbar.set)

        info_text.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')

    def setup_left_panel(self, parent):
        # Заголовок пользователей
        users_header = tk.Label(
            parent,
            text="👥 АКТИВНЫЕ ПОЛЬЗОВАТЕЛИ",
            font=('Arial', 16, 'bold'),
            fg=self.colors['accent_blue'],
            bg=self.colors['card_bg'],
            pady=15
        )
        users_header.pack(fill='x')

        # Поиск пользователей
        search_frame = tk.Frame(parent, bg=self.colors['card_bg'])
        search_frame.pack(fill='x', padx=15, pady=10)

        self.search_var = tk.StringVar()
        search_entry = tk.Entry(
            search_frame,
            textvariable=self.search_var,
            font=('Arial', 12),
            bg='#2a2a4a',
            fg=self.colors['text_primary'],
            insertbackground='white'
        )
        search_entry.pack(fill='x')
        search_entry.insert(0, "Поиск пользователя...")
        search_entry.bind('<KeyRelease>', self.search_users)
        search_entry.bind('<FocusIn>', lambda e: search_entry.delete(0,
                                                                     'end') if search_entry.get() == "Поиск пользователя..." else None)

        # Статистика пользователей
        stats_frame = tk.Frame(parent, bg=self.colors['card_bg'])
        stats_frame.pack(fill='x', padx=15, pady=10)

        self.total_users_var = tk.StringVar(value=f"Всего: {len(self.users)} | Активных: 0")
        total_label = tk.Label(
            stats_frame,
            textvariable=self.total_users_var,
            font=('Arial', 12, 'bold'),
            fg=self.colors['accent_green'],
            bg=self.colors['card_bg']
        )
        total_label.pack()

        # Список пользователей
        users_tree_frame = tk.Frame(parent, bg=self.colors['card_bg'])
        users_tree_frame.pack(fill='both', expand=True, padx=15, pady=10)

        self.users_tree = ttk.Treeview(
            users_tree_frame,
            columns=('ID', 'Имя', 'Статус', 'VIP', 'Баланс', 'Игр'),
            show='headings',
            height=15
        )

        self.users_tree.heading('ID', text='ID')
        self.users_tree.heading('Имя', text='Имя пользователя')
        self.users_tree.heading('Статус', text='Статус')
        self.users_tree.heading('VIP', text='VIP статус')
        self.users_tree.heading('Баланс', text='Баланс')
        self.users_tree.heading('Игр', text='Всего игр')

        self.users_tree.column('ID', width=50, anchor='center')
        self.users_tree.column('Имя', width=120)
        self.users_tree.column('Статус', width=80, anchor='center')
        self.users_tree.column('VIP', width=80, anchor='center')
        self.users_tree.column('Баланс', width=80, anchor='center')
        self.users_tree.column('Игр', width=60, anchor='center')

        scrollbar_users = ttk.Scrollbar(users_tree_frame, orient='vertical', command=self.users_tree.yview)
        self.users_tree.configure(yscrollcommand=scrollbar_users.set)

        self.users_tree.pack(side='left', fill='both', expand=True)
        scrollbar_users.pack(side='right', fill='y')

        self.users_tree.bind('<<TreeviewSelect>>', self.on_user_select)

        # Панель быстрых действий
        quick_actions_frame = tk.Frame(parent, bg=self.colors['card_bg'])
        quick_actions_frame.pack(fill='x', padx=15, pady=15)

        btn_refresh = tk.Button(
            quick_actions_frame,
            text="🔄 Обновить с сайта",
            command=self.refresh_website_data,
            bg=self.colors['accent_blue'],
            fg='white',
            font=('Arial', 10, 'bold'),
            padx=10,
            pady=5
        )
        btn_refresh.pack(fill='x', pady=2)

        btn_add_user = tk.Button(
            quick_actions_frame,
            text="➕ Новый пользователь",
            command=self.add_user_dialog,
            bg=self.colors['accent_pink'],
            fg='white',
            font=('Arial', 10, 'bold'),
            padx=10,
            pady=5
        )
        btn_add_user.pack(fill='x', pady=2)

        btn_add_session = tk.Button(
            quick_actions_frame,
            text="🎮 Добавить сессию",
            command=self.add_game_session_dialog,
            bg=self.colors['accent_green'],
            fg='white',
            font=('Arial', 10, 'bold'),
            padx=10,
            pady=5
        )
        btn_add_session.pack(fill='x', pady=2)

        btn_force_bet = tk.Button(
            quick_actions_frame,
            text="⚡ Принудительная ставка",
            command=self.force_bet,
            bg=self.colors['accent_orange'],
            fg='white',
            font=('Arial', 10, 'bold'),
            padx=10,
            pady=5
        )
        btn_force_bet.pack(fill='x', pady=2)

    def process_ui_queue(self):
        """Обработка очереди обновления UI из фонового потока"""
        try:
            while not self.ui_queue.empty():
                callback, args = self.ui_queue.get_nowait()
                if callback:
                    callback(*args)
        except:
            pass
        finally:
            self.root.after(100, self.process_ui_queue)

    def log_event(self, message, event_type="info"):
        """Добавление события в лог"""
        colors = {
            "info": self.colors['accent_blue'],
            "success": self.colors['success'],
            "warning": self.colors['warning'],
            "danger": self.colors['danger'],
            "bet": self.colors['accent_pink'],
            "win": self.colors['accent_green']
        }

        timestamp = datetime.now().strftime("%H:%M:%S")
        colored_message = f"[{timestamp}] {message}"

        self.live_events.append((colored_message, colors.get(event_type, self.colors['text_primary'])))

        # Обновляем UI через очередь
        self.ui_queue.put((self._update_event_log, ()))

    def _update_event_log(self):
        """Обновление лога событий в UI"""
        self.event_log.config(state='normal')
        self.event_log.delete(1.0, tk.END)

        for message, color in self.live_events:
            self.event_log.insert(tk.END, message + "\n", color)

        self.event_log.config(state='disabled')
        self.event_log.see(tk.END)

    def clear_event_log(self):
        """Очистка лога событий"""
        self.live_events.clear()
        self._update_event_log()

    def start_simulation(self):
        """Запуск симуляции активных ставок"""
        if not self.simulation_active:
            self.simulation_active = True
            self.simulation_stats = {
                'total_bets': 0,
                'active_players': 0,
                'total_wagered': 0,
                'peak_concurrent': 0,
                'events_per_minute': 0,
                'start_time': datetime.now(),
                'last_events_count': 0
            }

            self.start_sim_btn.config(state='disabled')
            self.stop_sim_btn.config(state='normal')

            self.log_event("=== СИМУЛЯЦИЯ ЗАПУЩЕНА ===", "success")

            # Запускаем симуляцию в отдельном потоке
            self.simulation_thread = threading.Thread(target=self.simulation_loop, daemon=True)
            self.simulation_thread.start()

    def stop_simulation(self):
        """Остановка симуляции"""
        if self.simulation_active:
            self.simulation_active = False
            self.start_sim_btn.config(state='normal')
            self.stop_sim_btn.config(state='disabled')

            self.log_event("=== СИМУЛЯЦИЯ ОСТАНОВЛЕНА ===", "warning")

            # Деактивируем всех пользователей
            for user in self.users:
                user['active'] = False
                user['current_game'] = None

            self.active_bets.clear()
            self.update_active_bets_display()
            self.update_users_table()

    def toggle_turbo_mode(self):
        """Переключение турбо режима"""
        if self.boost_sim_btn.cget('bg') == self.colors['accent_orange']:
            self.boost_sim_btn.config(
                bg=self.colors['accent_yellow'],
                text="⚡ ТУРБО РЕЖИМ ВКЛ (x3)"
            )
            self.log_event("Турбо режим ВКЛЮЧЕН (x3 скорость)", "warning")
        else:
            self.boost_sim_btn.config(
                bg=self.colors['accent_orange'],
                text="⚡ ТУРБО РЕЖИМ (x3)"
            )
            self.log_event("Турбо режим ВЫКЛЮЧЕН", "info")

    def simulation_loop(self):
        """Основной цикл симуляции"""
        event_count = 0
        last_minute_check = time.time()

        while self.simulation_active:
            try:
                # Определяем скорость симуляции
                speed_multiplier = 1
                if self.boost_sim_btn.cget('bg') == self.colors['accent_yellow']:
                    speed_multiplier = 3

                speed_settings = {
                    "Очень медленная": 5.0,
                    "Медленная": 2.5,
                    "Нормальная": 1.0,
                    "Быстрая": 0.5,
                    "Очень быстрая": 0.25
                }

                base_delay = speed_settings.get(self.speed_var.get(), 1.0)
                delay = base_delay / speed_multiplier

                time.sleep(delay)

                # Генерируем случайное событие
                event_type = random.choice(['new_bet', 'bet_result', 'user_login', 'user_logout'])

                if event_type == 'new_bet' and self.users:
                    self.generate_live_bet()
                    event_count += 1

                elif event_type == 'bet_result' and self.active_bets:
                    self.resolve_active_bet()
                    event_count += 1

                elif event_type == 'user_login':
                    self.simulate_user_login()
                    event_count += 1

                elif event_type == 'user_logout':
                    self.simulate_user_logout()
                    event_count += 1

                # Обновляем статистику каждую минуту
                current_time = time.time()
                if current_time - last_minute_check > 60:
                    self.simulation_stats['events_per_minute'] = event_count
                    event_count = 0
                    last_minute_check = current_time

                    # Обновляем статистику в UI
                    self.ui_queue.put((self.update_simulation_stats, ()))

                # Периодическое обновление UI
                if random.random() < 0.3:  # 30% шанс обновления UI
                    self.ui_queue.put((self.update_active_bets_display, ()))
                    self.ui_queue.put((self.update_users_table, ()))

            except Exception as e:
                print(f"Ошибка в симуляции: {e}")
                time.sleep(1)

    def generate_live_bet(self):
        """Генерация новой живой ставки"""
        # Выбираем случайного пользователя
        user = random.choice(self.users)

        # Проверяем, что у пользователя достаточно баланса
        if user['balance'] < 100:
            return

        # Выбираем игру
        game = random.choice(self.games_list)
        odds = self.game_odds.get(game, {"win_prob": 0.5, "multiplier_range": (1.5, 5.0)})

        # Определяем сумму ставки (от 1% до 10% от баланса)
        max_bet = min(user['balance'] * 0.1, 5000)
        min_bet = max(100, user['balance'] * 0.01)
        bet_amount = random.randint(int(min_bet), int(max_bet))

        # Создаем активную ставку
        bet_id = len(self.active_bets) + 1
        active_bet = {
            'id': bet_id,
            'user_id': user['id'],
            'username': user['username'],
            'game': game,
            'bet_amount': bet_amount,
            'start_time': datetime.now(),
            'status': 'active',
            'odds': odds,
            'potential_win': 0,
            'duration': random.randint(5, 30)  # Длительность ставки в секундах
        }

        # Рассчитываем потенциальный выигрыш
        win_prob = odds['win_prob']
        multiplier_range = odds['multiplier_range']
        potential_multiplier = random.uniform(*multiplier_range)
        active_bet['potential_win'] = round(bet_amount * potential_multiplier)

        # Добавляем ставку в список активных
        self.active_bets.append(active_bet)

        # Обновляем пользователя
        user['active'] = True
        user['current_game'] = game
        user['last_action'] = datetime.now()

        # Обновляем статистику
        self.simulation_stats['total_bets'] += 1
        self.simulation_stats['total_wagered'] += bet_amount

        # Логируем событие
        self.log_event(
            f"{user['username']} сделал ставку {bet_amount}₽ на {game} (Потенциальный выигрыш: {active_bet['potential_win']}₽)",
            "bet")

        # Обновляем UI
        self.ui_queue.put((self.update_simulation_stats, ()))

    def resolve_active_bet(self):
        """Завершение активной ставки"""
        if not self.active_bets:
            return

        # Выбираем случайную ставку для завершения
        bet = random.choice(self.active_bets)

        # Находим пользователя
        user = next((u for u in self.users if u['id'] == bet['user_id']), None)
        if not user:
            return

        # Определяем результат ставки
        win_prob = bet['odds']['win_prob']
        is_win = random.random() < win_prob

        if is_win:
            # Выигрыш
            win_amount = bet['potential_win']
            user['balance'] += win_amount
            bet['result'] = 'win'
            bet['win_amount'] = win_amount

            # Логируем выигрыш
            self.log_event(f"🎉 {user['username']} ВЫИГРАЛ {win_amount}₽ в {bet['game']}!", "win")

            # Добавляем в историю
            new_session = {
                'id': len(self.game_logs) + 1,
                'user_id': user['id'],
                'game_name': bet['game'],
                'start_time': bet['start_time'].strftime("%Y-%m-%d %H:%M:%S"),
                'duration': bet['duration'],
                'bet_amount': bet['bet_amount'],
                'win_amount': win_amount,
                'profit': win_amount - bet['bet_amount'],
                'status': 'completed'
            }
            self.game_logs.append(new_session)

        else:
            # Проигрыш
            user['balance'] -= bet['bet_amount']
            bet['result'] = 'lose'
            bet['win_amount'] = 0

            # Логируем проигрыш
            self.log_event(f"💥 {user['username']} проиграл {bet['bet_amount']}₽ в {bet['game']}", "danger")

            # Добавляем в историю
            new_session = {
                'id': len(self.game_logs) + 1,
                'user_id': user['id'],
                'game_name': bet['game'],
                'start_time': bet['start_time'].strftime("%Y-%m-%d %H:%M:%S"),
                'duration': bet['duration'],
                'bet_amount': bet['bet_amount'],
                'win_amount': 0,
                'profit': -bet['bet_amount'],
                'status': 'completed'
            }
            self.game_logs.append(new_session)

        # Удаляем ставку из активных
        self.active_bets.remove(bet)

        # Обновляем пользователя
        user['current_game'] = None
        if not any(b['user_id'] == user['id'] for b in self.active_bets):
            user['active'] = False

        # Обновляем UI
        self.ui_queue.put((self.update_active_bets_display, ()))
        self.ui_queue.put((self.update_users_table, ()))

        # Если пользователь выбран, обновляем его статистику
        selection = self.users_tree.selection()
        if selection:
            selected_user_id = int(self.users_tree.item(selection[0], 'values')[0])
            if selected_user_id == user['id']:
                self.ui_queue.put((self.show_user_details, (user['id'],)))

    def simulate_user_login(self):
        """Симуляция входа пользователя"""
        # Выбираем случайного неактивного пользователя
        inactive_users = [u for u in self.users if not u['active']]
        if not inactive_users:
            return

        user = random.choice(inactive_users)
        user['active'] = True
        user['last_action'] = datetime.now()

        self.log_event(f"👤 {user['username']} вошел в систему", "info")

        # Обновляем статистику активных пользователей
        active_count = len([u for u in self.users if u['active']])
        self.simulation_stats['active_players'] = active_count
        if active_count > self.simulation_stats['peak_concurrent']:
            self.simulation_stats['peak_concurrent'] = active_count

        self.ui_queue.put((self.update_simulation_stats, ()))
        self.ui_queue.put((self.update_users_table, ()))

    def simulate_user_logout(self):
        """Симуляция выхода пользователя"""
        # Выбираем случайного активного пользователя без активных ставок
        active_users = [u for u in self.users if u['active']]
        if not active_users:
            return

        user = random.choice(active_users)

        # Проверяем, есть ли у пользователя активные ставки
        if any(b['user_id'] == user['id'] for b in self.active_bets):
            return

        user['active'] = False
        user['current_game'] = None

        self.log_event(f"👤 {user['username']} вышел из системы", "info")

        # Обновляем статистику
        self.simulation_stats['active_players'] = len([u for u in self.users if u['active']])

        self.ui_queue.put((self.update_simulation_stats, ()))
        self.ui_queue.put((self.update_users_table, ()))

    def update_simulation_stats(self):
        """Обновление статистики симуляции"""
        active_count = len([u for u in self.users if u['active']])

        self.sim_stats_vars['total_bets'].set(str(self.simulation_stats['total_bets']))
        self.sim_stats_vars['total_wagered'].set(f"{self.simulation_stats['total_wagered']:,} ₽")
        self.sim_stats_vars['current_bets'].set(str(len(self.active_bets)))
        self.sim_stats_vars['events_minute'].set(str(self.simulation_stats['events_per_minute']))
        self.sim_stats_vars['peak_concurrent'].set(str(self.simulation_stats['peak_concurrent']))

        self.active_players_var.set(str(active_count))
        self.total_users_var.set(f"Всего: {len(self.users)} | Активных: {active_count}")

    def update_active_bets_display(self):
        """Обновление отображения активных ставок"""
        for item in self.active_bets_tree.get_children():
            self.active_bets_tree.delete(item)

        for bet in self.active_bets:
            duration = (datetime.now() - bet['start_time']).seconds
            self.active_bets_tree.insert('', 'end', values=(
                bet['username'],
                bet['game'],
                f"{bet['bet_amount']}₽",
                f"{duration}с",
                "Активна"
            ), tags=('active',))

    def update_users_table(self):
        """Обновление таблицы пользователей"""
        for item in self.users_tree.get_children():
            self.users_tree.delete(item)

        for user in self.users:
            user_sessions = [s for s in self.game_logs if s['user_id'] == user['id']]
            total_games = len(user_sessions)

            vip_display = {
                'none': '❌',
                'bronze': '🥉',
                'silver': '🥈',
                'gold': '🥇',
                'platinum': '💎'
            }.get(user.get('vip_status', 'none'), '❌')

            status_display = '🟢' if user['active'] else '⚫'
            if user['current_game']:
                status_display = '🎮'

            self.users_tree.insert('', 'end', values=(
                user['id'],
                user['username'],
                status_display,
                vip_display,
                f"{user['balance']} ₽",
                total_games
            ))

    def force_bet(self):
        """Принудительное создание ставки"""
        if not self.users:
            messagebox.showwarning("Ошибка", "Нет пользователей!")
            return

        # Диалог выбора пользователя
        dialog = tk.Toplevel(self.root)
        dialog.title("Создать ставку")
        dialog.geometry("400x300")
        dialog.configure(bg=self.colors['bg'])
        dialog.transient(self.root)
        dialog.grab_set()

        tk.Label(dialog, text="Выберите пользователя:", bg=self.colors['bg'], fg='white').pack(pady=5)
        user_var = tk.StringVar()
        user_combo = ttk.Combobox(dialog, textvariable=user_var, state='readonly')
        user_combo['values'] = [user['username'] for user in self.users]
        user_combo.pack(pady=5)

        tk.Label(dialog, text="Выберите игру:", bg=self.colors['bg'], fg='white').pack(pady=5)
        game_var = tk.StringVar()
        game_combo = ttk.Combobox(dialog, textvariable=game_var, state='readonly')
        game_combo['values'] = self.games_list
        game_combo.pack(pady=5)

        tk.Label(dialog, text="Сумма ставки:", bg=self.colors['bg'], fg='white').pack(pady=5)
        bet_var = tk.StringVar()
        bet_entry = tk.Entry(dialog, textvariable=bet_var)
        bet_entry.pack(pady=5)

        def create_forced_bet():
            try:
                username = user_var.get()
                game = game_var.get()
                bet_amount = int(bet_var.get())

                user = next((u for u in self.users if u['username'] == username), None)
                if not user:
                    messagebox.showerror("Ошибка", "Пользователь не найден!")
                    return

                if user['balance'] < bet_amount:
                    messagebox.showerror("Ошибка", "Недостаточно средств!")
                    return

                # Создаем ставку
                odds = self.game_odds.get(game, {"win_prob": 0.5, "multiplier_range": (1.5, 5.0)})

                bet_id = len(self.active_bets) + 1
                active_bet = {
                    'id': bet_id,
                    'user_id': user['id'],
                    'username': user['username'],
                    'game': game,
                    'bet_amount': bet_amount,
                    'start_time': datetime.now(),
                    'status': 'active',
                    'odds': odds,
                    'potential_win': 0,
                    'duration': random.randint(5, 30)
                }

                # Рассчитываем потенциальный выигрыш
                multiplier = random.uniform(*odds['multiplier_range'])
                active_bet['potential_win'] = round(bet_amount * multiplier)

                self.active_bets.append(active_bet)
                user['active'] = True
                user['current_game'] = game
                user['last_action'] = datetime.now()

                self.simulation_stats['total_bets'] += 1
                self.simulation_stats['total_wagered'] += bet_amount

                self.log_event(f"[РУЧНОЙ РЕЖИМ] {user['username']} сделал ставку {bet_amount}₽ на {game}", "bet")

                self.update_active_bets_display()
                self.update_users_table()
                self.update_simulation_stats()

                dialog.destroy()
                messagebox.showinfo("Успех", "Ставка создана!")

            except ValueError:
                messagebox.showerror("Ошибка", "Введите корректную сумму!")

        tk.Button(dialog, text="Создать ставку", command=create_forced_bet,
                  bg=self.colors['accent_pink'], fg='white').pack(pady=20)

    # Остальные методы остаются аналогичными, но с небольшими изменениями для поддержки симуляции
    def refresh_website_data(self):
        """Обновление данных с веб-сайта"""
        try:
            # Останавливаем симуляцию если она активна
            if self.simulation_active:
                self.stop_simulation()

            old_user_count = len(self.users)
            old_session_count = len(self.game_logs)

            self.load_website_data()

            new_user_count = len(self.users)
            new_session_count = len(self.game_logs)

            self.load_users_table()
            self.update_overall_stats()
            self.update_simulation_stats()

            messagebox.showinfo(
                "Обновление данных",
                f"Данные успешно обновлены!\n"
                f"Пользователей: {old_user_count} → {new_user_count}\n"
                f"Сессий: {old_session_count} → {new_session_count}"
            )

        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при обновлении данных: {str(e)}")

    def load_users_table(self):
        """Загрузка пользователей в таблицу (обертка для совместимости)"""
        self.update_users_table()

    def search_users(self, event=None):
        """Поиск пользователей"""
        search_term = self.search_var.get().lower()

        for item in self.users_tree.get_children():
            self.users_tree.delete(item)

        for user in self.users:
            if search_term in user['username'].lower():
                user_sessions = [s for s in self.game_logs if s['user_id'] == user['id']]
                total_games = len(user_sessions)

                vip_display = {
                    'none': '❌',
                    'bronze': '🥉',
                    'silver': '🥈',
                    'gold': '🥇',
                    'platinum': '💎'
                }.get(user.get('vip_status', 'none'), '❌')

                status_display = '🟢' if user['active'] else '⚫'
                if user['current_game']:
                    status_display = '🎮'

                self.users_tree.insert('', 'end', values=(
                    user['id'],
                    user['username'],
                    status_display,
                    vip_display,
                    f"{user['balance']} ₽",
                    total_games
                ))

    def on_user_select(self, event):
        """Обработчик выбора пользователя"""
        selection = self.users_tree.selection()
        if selection:
            item = selection[0]
            user_data = self.users_tree.item(item, 'values')
            user_id = int(user_data[0])
            self.show_user_details(user_id)

    def show_user_details(self, user_id):
        """Показать детальную информацию о пользователе"""
        user = next((u for u in self.users if u['id'] == user_id), None)
        if not user:
            return

        user_sessions = [s for s in self.game_logs if s['user_id'] == user_id]

        # Обновляем заголовок
        vip_status = user.get('vip_status', 'none').capitalize()
        status_text = "🟢 В сети" if user['active'] else "⚫ Не в сети"
        if user['current_game']:
            status_text = f"🎮 Играет в {user['current_game']}"

        self.stats_label.config(
            text=f"📊 Статистика пользователя: {user['username']} (VIP: {vip_status}) | {status_text}"
        )

        # Рассчитываем статистику
        total_games = len(user_sessions)
        total_bets = sum(session['bet_amount'] for session in user_sessions)
        total_wins = sum(session['win_amount'] for session in user_sessions)
        total_profit = total_wins - total_bets
        avg_bet = total_bets / total_games if total_games > 0 else 0
        win_sessions = len([s for s in user_sessions if s['win_amount'] > s['bet_amount']])
        win_rate = (win_sessions / total_games * 100) if total_games > 0 else 0

        # Обновляем карточки статистики
        self.user_stats_vars['total_games'].set(str(total_games))
        self.user_stats_vars['total_bets'].set(f"{total_bets:,.0f} ₽")
        self.user_stats_vars['total_wins'].set(f"{total_wins:,.0f} ₽")
        self.user_stats_vars['total_profit'].set(f"{total_profit:+,.0f} ₽")
        self.user_stats_vars['avg_bet'].set(f"{avg_bet:,.0f} ₽")
        self.user_stats_vars['win_rate'].set(f"{win_rate:.1f}%")

        # Загружаем историю игр
        for item in self.games_tree.get_children():
            self.games_tree.delete(item)

        for session in sorted(user_sessions, key=lambda x: x['start_time'], reverse=True)[:50]:  # Ограничиваем показ
            duration_str = f"{session['duration'] // 60} мин"
            profit = session['win_amount'] - session['bet_amount']
            profit_color_tag = "profit_positive" if profit >= 0 else "profit_negative"

            self.games_tree.insert('', 'end', values=(
                session['id'],
                session['game_name'],
                session['start_time'],
                duration_str,
                f"{session['bet_amount']} ₽",
                f"{session['win_amount']} ₽",
                f"{profit:+,.0f} ₽"
            ), tags=(profit_color_tag,))

        # Настраиваем цвета для прибыли/убытка
        self.games_tree.tag_configure('profit_positive', foreground=self.colors['success'])
        self.games_tree.tag_configure('profit_negative', foreground=self.colors['danger'])

    def setup_activity_tab(self, parent):
        # Статистика выбранного пользователя
        stats_frame = tk.Frame(parent, bg=self.colors['card_bg'], relief='ridge', bd=2)
        stats_frame.pack(fill='x', padx=10, pady=10)

        self.stats_label = tk.Label(
            stats_frame,
            text="Выберите пользователя для просмотра детальной статистики",
            font=('Arial', 14, 'bold'),
            fg=self.colors['accent_green'],
            bg=self.colors['card_bg'],
            pady=10
        )
        self.stats_label.pack()

        # Детальная статистика в виде карточек
        stats_cards_frame = tk.Frame(stats_frame, bg=self.colors['card_bg'])
        stats_cards_frame.pack(fill='x', padx=20, pady=10)

        # Создаем карточки статистики
        self.user_stats_vars = {
            'total_games': tk.StringVar(value="0"),
            'total_bets': tk.StringVar(value="0 ₽"),
            'total_wins': tk.StringVar(value="0 ₽"),
            'total_profit': tk.StringVar(value="0 ₽"),
            'avg_bet': tk.StringVar(value="0 ₽"),
            'win_rate': tk.StringVar(value="0%")
        }

        stats_data = [
            ("🎮 Всего игр", self.user_stats_vars['total_games']),
            ("💰 Общие ставки", self.user_stats_vars['total_bets']),
            ("🏆 Общие выигрыши", self.user_stats_vars['total_wins']),
            ("💸 Общая прибыль", self.user_stats_vars['total_profit']),
            ("📊 Средняя ставка", self.user_stats_vars['avg_bet']),
            ("📈 Процент выигрышей", self.user_stats_vars['win_rate'])
        ]

        for i, (title, var) in enumerate(stats_data):
            row = i // 3
            col = i % 3
            card = self.create_stat_card(stats_cards_frame, title, var, row, col)

        # История игр пользователя
        games_frame = tk.Frame(parent, bg=self.colors['bg'])
        games_frame.pack(fill='both', expand=True, padx=10, pady=10)

        games_header = tk.Label(
            games_frame,
            text="📋 История игровых сессий (последние 50)",
            font=('Arial', 16, 'bold'),
            fg=self.colors['accent_blue'],
            bg=self.colors['bg']
        )
        games_header.pack(anchor='w')

        self.games_tree = ttk.Treeview(
            games_frame,
            columns=('ID', 'Игра', 'Дата', 'Длительность', 'Ставка', 'Выигрыш', 'Прибыль'),
            show='headings',
            height=12
        )

        self.games_tree.heading('ID', text='ID')
        self.games_tree.heading('Игра', text='Игра')
        self.games_tree.heading('Дата', text='Дата и время')
        self.games_tree.heading('Длительность', text='Длительность')
        self.games_tree.heading('Ставка', text='Ставка')
        self.games_tree.heading('Выигрыш', text='Выигрыш')
        self.games_tree.heading('Прибыль', text='Прибыль')

        self.games_tree.column('ID', width=50, anchor='center')
        self.games_tree.column('Игра', width=150)
        self.games_tree.column('Дата', width=150)
        self.games_tree.column('Длительность', width=100, anchor='center')
        self.games_tree.column('Ставка', width=100, anchor='center')
        self.games_tree.column('Выигрыш', width=100, anchor='center')
        self.games_tree.column('Прибыль', width=100, anchor='center')

        scrollbar_games = ttk.Scrollbar(games_frame, orient='vertical', command=self.games_tree.yview)
        self.games_tree.configure(yscrollcommand=scrollbar_games.set)

        self.games_tree.pack(side='left', fill='both', expand=True)
        scrollbar_games.pack(side='right', fill='y')

    def setup_overall_stats_tab(self, parent):
        # Общая статистика казино
        stats_container = tk.Frame(parent, bg=self.colors['bg'])
        stats_container.pack(fill='both', expand=True, padx=20, pady=20)

        # Карточки общей статистики
        overall_stats_frame = tk.Frame(stats_container, bg=self.colors['bg'])
        overall_stats_frame.pack(fill='x', pady=10)

        self.overall_stats_vars = {
            'total_users': tk.StringVar(value="0"),
            'total_sessions': tk.StringVar(value="0"),
            'total_bets': tk.StringVar(value="0 ₽"),
            'total_wins': tk.StringVar(value="0 ₽"),
            'total_profit': tk.StringVar(value="0 ₽"),
            'avg_session': tk.StringVar(value="0 мин")
        }

        overall_stats_data = [
            ("👥 Всего пользователей", self.overall_stats_vars['total_users']),
            ("🎮 Всего игровых сессий", self.overall_stats_vars['total_sessions']),
            ("💰 Общие ставки", self.overall_stats_vars['total_bets']),
            ("🏆 Общие выигрыши", self.overall_stats_vars['total_wins']),
            ("💸 Прибыль казино", self.overall_stats_vars['total_profit']),
            ("⏱ Средняя сессия", self.overall_stats_vars['avg_session'])
        ]

        for i, (title, var) in enumerate(overall_stats_data):
            row = i // 3
            col = i % 3
            self.create_stat_card(overall_stats_frame, title, var, row, col)

        # Топ пользователей по прибыли
        top_users_frame = tk.Frame(stats_container, bg=self.colors['card_bg'], relief='ridge', bd=2)
        top_users_frame.pack(fill='both', expand=True, pady=10)

        top_users_label = tk.Label(
            top_users_frame,
            text="🏆 Топ пользователей по прибыли",
            font=('Arial', 16, 'bold'),
            fg=self.colors['accent_pink'],
            bg=self.colors['card_bg'],
            pady=10
        )
        top_users_label.pack()

        self.top_users_tree = ttk.Treeview(
            top_users_frame,
            columns=('Место', 'Имя пользователя', 'VIP статус', 'Общая прибыль', 'Количество игр'),
            show='headings',
            height=8
        )

        self.top_users_tree.heading('Место', text='Место')
        self.top_users_tree.heading('Имя пользователя', text='Имя пользователя')
        self.top_users_tree.heading('VIP статус', text='VIP статус')
        self.top_users_tree.heading('Общая прибыль', text='Общая прибыль')
        self.top_users_tree.heading('Количество игр', text='Количество игр')

        self.top_users_tree.column('Место', width=60, anchor='center')
        self.top_users_tree.column('Имя пользователя', width=150)
        self.top_users_tree.column('VIP статус', width=100, anchor='center')
        self.top_users_tree.column('Общая прибыль', width=120, anchor='center')
        self.top_users_tree.column('Количество игр', width=120, anchor='center')

        scrollbar_top = ttk.Scrollbar(top_users_frame, orient='vertical', command=self.top_users_tree.yview)
        self.top_users_tree.configure(yscrollcommand=scrollbar_top.set)

        self.top_users_tree.pack(side='left', fill='both', expand=True, padx=10, pady=10)
        scrollbar_top.pack(side='right', fill='y', pady=10)

    def setup_analysis_tab(self, parent):
        # Аналитика по играм
        analysis_container = tk.Frame(parent, bg=self.colors['bg'])
        analysis_container.pack(fill='both', expand=True, padx=20, pady=20)

        # Статистика по играм
        games_stats_frame = tk.Frame(analysis_container, bg=self.colors['card_bg'], relief='ridge', bd=2)
        games_stats_frame.pack(fill='both', expand=True, pady=10)

        games_stats_label = tk.Label(
            games_stats_frame,
            text="📊 Статистика по играм",
            font=('Arial', 16, 'bold'),
            fg=self.colors['accent_blue'],
            bg=self.colors['card_bg'],
            pady=10
        )
        games_stats_label.pack()

        self.games_stats_tree = ttk.Treeview(
            games_stats_frame,
            columns=('Игра', 'Количество сессий', 'Общие ставки', 'Общие выигрыши', 'Прибыль казино', 'Средняя ставка'),
            show='headings',
            height=10
        )

        self.games_stats_tree.heading('Игра', text='Игра')
        self.games_stats_tree.heading('Количество сессий', text='Количество сессий')
        self.games_stats_tree.heading('Общие ставки', text='Общие ставки')
        self.games_stats_tree.heading('Общие выигрыши', text='Общие выигрыши')
        self.games_stats_tree.heading('Прибыль казино', text='Прибыль казино')
        self.games_stats_tree.heading('Средняя ставка', text='Средняя ставка')

        self.games_stats_tree.column('Игра', width=200)
        self.games_stats_tree.column('Количество сессий', width=120, anchor='center')
        self.games_stats_tree.column('Общие ставки', width=120, anchor='center')
        self.games_stats_tree.column('Общие выигрыши', width=120, anchor='center')
        self.games_stats_tree.column('Прибыль казино', width=120, anchor='center')
        self.games_stats_tree.column('Средняя ставка', width=120, anchor='center')

        scrollbar_games_stats = ttk.Scrollbar(games_stats_frame, orient='vertical', command=self.games_stats_tree.yview)
        self.games_stats_tree.configure(yscrollcommand=scrollbar_games_stats.set)

        self.games_stats_tree.pack(side='left', fill='both', expand=True, padx=10, pady=10)
        scrollbar_games_stats.pack(side='right', fill='y', pady=10)

    def create_stat_card(self, parent, title, variable, row, column):
        card = tk.Frame(parent, bg=self.colors['card_bg'], relief='ridge', bd=1)
        card.grid(row=row, column=column, padx=10, pady=10, sticky='nsew')

        title_label = tk.Label(
            card,
            text=title,
            font=('Arial', 11, 'bold'),
            fg=self.colors['text_secondary'],
            bg=self.colors['card_bg'],
            wraplength=150
        )
        title_label.pack(pady=(10, 5))

        value_label = tk.Label(
            card,
            textvariable=variable,
            font=('Arial', 14, 'bold'),
            fg=self.colors['accent_green'],
            bg=self.colors['card_bg']
        )
        value_label.pack(pady=(5, 10))

        parent.columnconfigure(column, weight=1)
        parent.rowconfigure(row, weight=1)

        return card

    def add_user_dialog(self):
        """Диалог добавления нового пользователя"""
        username = simpledialog.askstring("Новый пользователь", "Введите имя пользователя:")
        if username:
            # Проверяем, существует ли уже пользователь
            if any(user['username'] == username for user in self.users):
                messagebox.showerror("Ошибка", "Пользователь с таким именем уже существует!")
                return

            new_user = {
                'id': max(user['id'] for user in self.users) + 1 if self.users else 1,
                'username': username,
                'registration_date': datetime.now().strftime("%Y-%m-%d"),
                'vip_status': 'none',
                'balance': 1000,
                'active': False,
                'current_game': None,
                'last_action': None
            }

            self.users.append(new_user)
            self.update_users_table()
            self.update_overall_stats()
            messagebox.showinfo("Успех", f"Пользователь {username} успешно добавлен!")

    def add_game_session_dialog(self):
        """Диалог добавления игровой сессии"""
        if not self.users:
            messagebox.showwarning("Внимание", "Сначала добавьте пользователей!")
            return

        # Создаем диалоговое окно
        dialog = tk.Toplevel(self.root)
        dialog.title("Добавить игровую сессию")
        dialog.geometry("400x300")
        dialog.configure(bg=self.colors['bg'])
        dialog.transient(self.root)
        dialog.grab_set()

        # Выбор пользователя
        tk.Label(dialog, text="Выберите пользователя:", bg=self.colors['bg'], fg='white').pack(pady=5)
        user_var = tk.StringVar()
        user_combo = ttk.Combobox(dialog, textvariable=user_var, state='readonly')
        user_combo['values'] = [user['username'] for user in self.users]
        user_combo.pack(pady=5)

        # Выбор игры
        tk.Label(dialog, text="Выберите игру:", bg=self.colors['bg'], fg='white').pack(pady=5)
        game_var = tk.StringVar()
        game_combo = ttk.Combobox(dialog, textvariable=game_var, state='readonly')
        game_combo['values'] = self.games_list
        game_combo.pack(pady=5)

        # Сумма ставки
        tk.Label(dialog, text="Сумма ставки:", bg=self.colors['bg'], fg='white').pack(pady=5)
        bet_var = tk.StringVar()
        bet_entry = tk.Entry(dialog, textvariable=bet_var)
        bet_entry.pack(pady=5)

        # Сумма выигрыша
        tk.Label(dialog, text="Сумма выигрыша (0 если проигрыш):", bg=self.colors['bg'], fg='white').pack(pady=5)
        win_var = tk.StringVar()
        win_entry = tk.Entry(dialog, textvariable=win_var)
        win_entry.pack(pady=5)

        def add_session():
            try:
                user_name = user_var.get()
                game_name = game_var.get()
                bet_amount = float(bet_var.get())
                win_amount = float(win_var.get() or 0)

                if not user_name or not game_name:
                    messagebox.showerror("Ошибка", "Заполните все поля!")
                    return

                user = next((u for u in self.users if u['username'] == user_name), None)
                if not user:
                    messagebox.showerror("Ошибка", "Пользователь не найден!")
                    return

                new_session = {
                    'id': max(session['id'] for session in self.game_logs) + 1 if self.game_logs else 1,
                    'user_id': user['id'],
                    'game_name': game_name,
                    'start_time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    'duration': random.randint(60, 1800),  # 1-30 минут
                    'bet_amount': bet_amount,
                    'win_amount': win_amount,
                    'profit': win_amount - bet_amount,
                    'status': 'completed'
                }

                self.game_logs.append(new_session)

                # Обновляем баланс пользователя
                user['balance'] += (win_amount - bet_amount)

                dialog.destroy()
                self.update_users_table()
                self.update_overall_stats()

                # Если выбран этот пользователь, обновляем его статистику
                selection = self.users_tree.selection()
                if selection:
                    current_user_id = int(self.users_tree.item(selection[0], 'values')[0])
                    if current_user_id == user['id']:
                        self.show_user_details(user['id'])

                messagebox.showinfo("Успех", "Игровая сессия добавлена!")

            except ValueError:
                messagebox.showerror("Ошибка", "Введите корректные числовые значения!")

        tk.Button(dialog, text="Добавить", command=add_session, bg=self.colors['accent_green'], fg='black').pack(
            pady=20)

    def simulate_activity(self):
        """Симуляция случайной игровой активности (старая версия)"""
        if not self.users:
            messagebox.showwarning("Внимание", "Нет пользователей для симуляции!")
            return

        num_sessions = simpledialog.askinteger(
            "Симуляция активности",
            "Сколько игровых сессий сгенерировать?",
            initialvalue=10,
            minvalue=1,
            maxvalue=100
        )

        if num_sessions:
            for _ in range(num_sessions):
                user = random.choice(self.users)
                game_name = random.choice(self.games_list)
                odds = self.game_odds.get(game_name, {"win_prob": 0.5, "multiplier_range": (1.5, 5.0)})
                bet_amount = random.randint(100, 5000)
                is_win = random.random() < odds["win_prob"]
                multiplier = random.uniform(*odds["multiplier_range"])
                win_amount = round(bet_amount * multiplier) if is_win else 0

                new_session = {
                    'id': max(session['id'] for session in self.game_logs) + 1 if self.game_logs else 1,
                    'user_id': user['id'],
                    'game_name': game_name,
                    'start_time': self.random_date(),
                    'duration': random.randint(60, 7200),
                    'bet_amount': bet_amount,
                    'win_amount': win_amount,
                    'profit': win_amount - bet_amount,
                    'status': 'completed'
                }

                self.game_logs.append(new_session)
                # Обновляем баланс пользователя
                user['balance'] += (win_amount - bet_amount)

            self.update_users_table()
            self.update_overall_stats()
            messagebox.showinfo("Успех", f"Сгенерировано {num_sessions} игровых сессий!")

    def update_overall_stats(self):
        """Обновление общей статистики"""
        # Общая статистика
        total_users = len(self.users)
        total_sessions = len(self.game_logs)
        total_bets = sum(session['bet_amount'] for session in self.game_logs)
        total_wins = sum(session['win_amount'] for session in self.game_logs)
        total_profit = total_bets - total_wins  # Прибыль казино
        avg_session_duration = sum(
            session['duration'] for session in self.game_logs) / total_sessions if total_sessions > 0 else 0

        self.overall_stats_vars['total_users'].set(str(total_users))
        self.overall_stats_vars['total_sessions'].set(str(total_sessions))
        self.overall_stats_vars['total_bets'].set(f"{total_bets:,.0f} ₽")
        self.overall_stats_vars['total_wins'].set(f"{total_wins:,.0f} ₽")
        self.overall_stats_vars['total_profit'].set(f"{total_profit:,.0f} ₽")
        self.overall_stats_vars['avg_session'].set(f"{avg_session_duration // 60} мин")

        # Топ пользователей
        self.update_top_users()

        # Статистика по играм
        self.update_games_stats()

    def update_top_users(self):
        """Обновление топа пользователей"""
        for item in self.top_users_tree.get_children():
            self.top_users_tree.delete(item)

        user_profits = []
        for user in self.users:
            user_sessions = [s for s in self.game_logs if s['user_id'] == user['id']]
            total_profit = sum(session['win_amount'] - session['bet_amount'] for session in user_sessions)
            user_profits.append((user, total_profit, len(user_sessions)))

        # Сортируем по прибыли (по убыванию)
        user_profits.sort(key=lambda x: x[1], reverse=True)

        for i, (user, profit, games_count) in enumerate(user_profits[:10], 1):
            vip_display = {
                'none': '❌',
                'bronze': '🥉',
                'silver': '🥈',
                'gold': '🥇',
                'platinum': '💎'
            }.get(user.get('vip_status', 'none'), '❌')

            self.top_users_tree.insert('', 'end', values=(
                f"{i}",
                user['username'],
                vip_display,
                f"{profit:+,.0f} ₽",
                games_count
            ))

    def update_games_stats(self):
        """Обновление статистики по играм"""
        for item in self.games_stats_tree.get_children():
            self.games_stats_tree.delete(item)

        game_stats = {}
        for session in self.game_logs:
            game_name = session['game_name']
            if game_name not in game_stats:
                game_stats[game_name] = {
                    'sessions': 0,
                    'total_bets': 0,
                    'total_wins': 0
                }

            game_stats[game_name]['sessions'] += 1
            game_stats[game_name]['total_bets'] += session['bet_amount']
            game_stats[game_name]['total_wins'] += session['win_amount']

        for game_name, stats in game_stats.items():
            sessions = stats['sessions']
            total_bets = stats['total_bets']
            total_wins = stats['total_wins']
            casino_profit = total_bets - total_wins
            avg_bet = total_bets / sessions if sessions > 0 else 0

            self.games_stats_tree.insert('', 'end', values=(
                game_name,
                sessions,
                f"{total_bets:,.0f} ₽",
                f"{total_wins:,.0f} ₽",
                f"{casino_profit:,.0f} ₽",
                f"{avg_bet:,.0f} ₽"
            ))

    def export_statistics(self):
        """Экспорт статистики в JSON файл"""
        try:
            data = {
                'export_time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'users': self.users,
                'game_sessions': self.game_logs,
                'active_bets': self.active_bets,
                'simulation_stats': self.simulation_stats,
                'statistics': {
                    'total_users': len(self.users),
                    'total_sessions': len(self.game_logs),
                    'total_bets': sum(session['bet_amount'] for session in self.game_logs),
                    'total_wins': sum(session['win_amount'] for session in self.game_logs),
                    'casino_profit': sum(session['bet_amount'] - session['win_amount'] for session in self.game_logs)
                }
            }

            filename = f"casino_stats_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

            messagebox.showinfo("Успех", f"Статистика экспортирована в файл: {filename}")

        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при экспорте: {str(e)}")


def main():
    root = tk.Tk()
    app = UserGameTracker(root)
    root.mainloop()


if __name__ == "__main__":
    main()