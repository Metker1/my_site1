import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
import datetime
import json
import threading
import time
import logging
import re
import psycopg2
from psycopg2 import sql

# Настройки бота
BOT_TOKEN = '8421270114:AAGWIyRCWX_ncdlhVs_B45HpNLwKyjcAyoQ'
ADMIN_IDS = [5710697156]

# Настройки PostgreSQL
DB_CONFIG = {
    'host': '127.0.0.1',
    'database': 'neon_casino_db',
    'user': 'postgres',
    'password': 'Mashinist132',
    'port': 5432
}

# Инициализация бота
bot = telebot.TeleBot(BOT_TOKEN)

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class PostgreSQLStorage:
    def __init__(self, db_config):
        self.db_config = db_config
        self.init_database()

    def get_connection(self):
        """Создание соединения с базой данных"""
        try:
            conn = psycopg2.connect(**self.db_config)
            logger.info("Успешное подключение к PostgreSQL")
            return conn
        except Exception as e:
            logger.error(f"Ошибка подключения к PostgreSQL: {e}")
            return None

    def init_database(self):
        """Инициализация таблиц в базе данных"""
        try:
            conn = self.get_connection()
            if conn is None:
                logger.error("Не удалось подключиться к PostgreSQL для инициализации")
                return

            cursor = conn.cursor()

            # Таблица пользователей бота
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS telegram_users (
                    id SERIAL PRIMARY KEY,
                    user_id BIGINT UNIQUE NOT NULL,
                    username VARCHAR(255),
                    first_name VARCHAR(255),
                    last_name VARCHAR(255),
                    registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            # Таблица заявок
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS tickets (
                    id SERIAL PRIMARY KEY,
                    ticket_id INTEGER NOT NULL,
                    user_id BIGINT NOT NULL,
                    username VARCHAR(255),
                    first_name VARCHAR(255),
                    message TEXT,
                    status VARCHAR(50) DEFAULT 'open',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    admin_id BIGINT,
                    admin_username VARCHAR(255),
                    FOREIGN KEY (user_id) REFERENCES telegram_users(user_id)
                )
            ''')

            # Таблица ответов на заявки
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS ticket_responses (
                    id SERIAL PRIMARY KEY,
                    ticket_id INTEGER NOT NULL,
                    response_text TEXT,
                    is_admin BOOLEAN DEFAULT FALSE,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (ticket_id) REFERENCES tickets(id)
                )
            ''')

            # Таблица распарсенных пользователей с сайта
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS parsed_users (
                    id SERIAL PRIMARY KEY,
                    username VARCHAR(255) NOT NULL,
                    balance DECIMAL(15,2) DEFAULT 0,
                    vip_status VARCHAR(100),
                    registration_date VARCHAR(255),
                    parsed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    admin_id BIGINT,
                    source VARCHAR(50) DEFAULT 'website'
                )
            ''')

            # Добавляем UNIQUE ограничение если его нет
            try:
                cursor.execute('''
                    ALTER TABLE parsed_users 
                    ADD CONSTRAINT parsed_users_username_unique UNIQUE (username)
                ''')
                logger.info("UNIQUE ограничение добавлено на поле username")
            except psycopg2.Error as e:
                if "уже существует" in str(e) or "already exists" in str(e):
                    logger.info("UNIQUE ограничение уже существует")
                else:
                    raise e

            conn.commit()
            cursor.close()
            conn.close()
            logger.info("База данных инициализирована успешно")

        except Exception as e:
            logger.error(f"Ошибка инициализации базы данных: {e}")

    def add_telegram_user(self, user_data):
        """Добавление пользователя Telegram в базу данных"""
        try:
            conn = self.get_connection()
            if conn is None:
                return None

            cursor = conn.cursor()

            cursor.execute('''
                INSERT INTO telegram_users (user_id, username, first_name, last_name, registered_at)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (user_id) DO NOTHING
                RETURNING id
            ''', (
                user_data['id'],
                user_data.get('username'),
                user_data.get('first_name'),
                user_data.get('last_name'),
                datetime.datetime.now()
            ))

            result = cursor.fetchone()
            conn.commit()
            cursor.close()
            conn.close()

            if result:
                logger.info(f"Пользователь {user_data['id']} добавлен в PostgreSQL")
            return result[0] if result else None

        except Exception as e:
            logger.error(f"Ошибка добавления пользователя в PostgreSQL: {e}")
            return None

    def add_ticket(self, user_id, message, username, first_name):
        """Добавление заявки в базу данных"""
        try:
            conn = self.get_connection()
            if conn is None:
                return None

            cursor = conn.cursor()

            # Получаем последний ticket_id
            cursor.execute('SELECT COALESCE(MAX(ticket_id), 0) FROM tickets')
            last_ticket_id = cursor.fetchone()[0]
            new_ticket_id = last_ticket_id + 1

            cursor.execute('''
                INSERT INTO tickets (ticket_id, user_id, username, first_name, message, created_at)
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING id
            ''', (new_ticket_id, user_id, username, first_name, message, datetime.datetime.now()))

            result = cursor.fetchone()
            conn.commit()
            cursor.close()
            conn.close()

            if result:
                logger.info(f"Заявка #{new_ticket_id} добавлена в PostgreSQL")
            return new_ticket_id if result else None

        except Exception as e:
            logger.error(f"Ошибка добавления заявки в PostgreSQL: {e}")
            return None

    def add_parsed_users(self, users, admin_id):
        """Добавление распарсенных пользователей в базу данных"""
        try:
            logger.info(f"Попытка добавить {len(users)} пользователей в PostgreSQL")

            conn = self.get_connection()
            if conn is None:
                logger.error("Нет подключения к PostgreSQL")
                return 0

            cursor = conn.cursor()

            added_count = 0
            for user in users:
                logger.info(f"Добавление пользователя: {user['username']}, баланс: {user['balance']}")

                try:
                    # Сначала пробуем обновить существующую запись
                    cursor.execute('''
                        UPDATE parsed_users 
                        SET balance = %s, vip_status = %s, registration_date = %s, 
                            admin_id = %s, parsed_at = %s
                        WHERE username = %s
                    ''', (
                        user['balance'],
                        user['vip_status'],
                        user['registration_date'],
                        admin_id,
                        datetime.datetime.now(),
                        user['username']
                    ))

                    # Если не было обновлено ни одной строки, значит пользователя нет, вставляем нового
                    if cursor.rowcount == 0:
                        cursor.execute('''
                            INSERT INTO parsed_users (username, balance, vip_status, registration_date, admin_id, parsed_at)
                            VALUES (%s, %s, %s, %s, %s, %s)
                        ''', (
                            user['username'],
                            user['balance'],
                            user['vip_status'],
                            user['registration_date'],
                            admin_id,
                            datetime.datetime.now()
                        ))

                    added_count += 1
                    logger.info(f"Успешно добавлен/обновлен пользователь: {user['username']}")

                except Exception as user_error:
                    logger.error(f"Ошибка при добавлении пользователя {user['username']}: {user_error}")
                    # Продолжаем со следующим пользователем
                    continue

            conn.commit()
            cursor.close()
            conn.close()

            logger.info(f"Успешно добавлено {added_count} пользователей в PostgreSQL")
            return added_count

        except Exception as e:
            logger.error(f"Ошибка добавления распарсенных пользователей в PostgreSQL: {e}")
            return 0

    def get_parsed_users_stats(self):
        """Получение статистики по распарсенным пользователям"""
        try:
            conn = self.get_connection()
            if conn is None:
                return None

            cursor = conn.cursor()

            cursor.execute('''
                SELECT 
                    COUNT(*) as total_users,
                    COALESCE(SUM(balance), 0) as total_balance,
                    COUNT(CASE WHEN vip_status != 'Нет' AND vip_status IS NOT NULL THEN 1 END) as vip_users,
                    MAX(parsed_at) as last_parse
                FROM parsed_users
            ''')

            result = cursor.fetchone()
            cursor.close()
            conn.close()

            stats = {
                'total_users': result[0],
                'total_balance': float(result[1]) if result[1] else 0,
                'vip_users': result[2],
                'last_parse': result[3]
            }

            logger.info(f"Получена статистика: {stats}")
            return stats

        except Exception as e:
            logger.error(f"Ошибка получения статистики из PostgreSQL: {e}")
            return None

    def get_telegram_users_count(self):
        """Получение количества пользователей бота"""
        try:
            conn = self.get_connection()
            if conn is None:
                return 0

            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM telegram_users')
            count = cursor.fetchone()[0]
            cursor.close()
            conn.close()
            return count

        except Exception as e:
            logger.error(f"Ошибка получения количества пользователей: {e}")
            return 0

    def get_all_telegram_users(self):
        """Получение всех пользователей бота"""
        try:
            conn = self.get_connection()
            if conn is None:
                return []

            cursor = conn.cursor()
            cursor.execute('''
                SELECT user_id, username, first_name, last_name, registered_at 
                FROM telegram_users 
                ORDER BY registered_at DESC
            ''')

            users = []
            for row in cursor.fetchall():
                users.append({
                    'user_id': row[0],
                    'username': row[1],
                    'first_name': row[2],
                    'last_name': row[3],
                    'registered_at': row[4]
                })

            cursor.close()
            conn.close()
            return users

        except Exception as e:
            logger.error(f"Ошибка получения пользователей: {e}")
            return []

    def get_ticket_stats(self):
        """Получение статистики по заявкам"""
        try:
            conn = self.get_connection()
            if conn is None:
                return {}

            cursor = conn.cursor()

            cursor.execute('''
                SELECT 
                    status,
                    COUNT(*) as count
                FROM tickets 
                GROUP BY status
            ''')

            stats = {}
            for row in cursor.fetchall():
                stats[row[0]] = row[1]

            # Заявки за сегодня
            cursor.execute('''
                SELECT COUNT(*) 
                FROM tickets 
                WHERE DATE(created_at) = CURRENT_DATE
            ''')
            today_count = cursor.fetchone()[0]
            stats['today'] = today_count

            cursor.close()
            conn.close()
            return stats

        except Exception as e:
            logger.error(f"Ошибка получения статистики заявок: {e}")
            return {}

    def get_parsed_users_count(self):
        """Получение количества распарсенных пользователей"""
        try:
            conn = self.get_connection()
            if conn is None:
                return 0

            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM parsed_users')
            count = cursor.fetchone()[0]
            cursor.close()
            conn.close()
            return count

        except Exception as e:
            logger.error(f"Ошибка получения количества распарсенных пользователей: {e}")
            return 0

    def get_recent_parsed_users(self, limit=10):
        """Получение последних распарсенных пользователей"""
        try:
            conn = self.get_connection()
            if conn is None:
                return []

            cursor = conn.cursor()
            cursor.execute('''
                SELECT username, balance, vip_status, registration_date, parsed_at 
                FROM parsed_users 
                ORDER BY parsed_at DESC 
                LIMIT %s
            ''', (limit,))

            users = []
            for row in cursor.fetchall():
                users.append({
                    'username': row[0],
                    'balance': row[1],
                    'vip_status': row[2],
                    'registration_date': row[3],
                    'parsed_at': row[4]
                })

            cursor.close()
            conn.close()
            return users

        except Exception as e:
            logger.error(f"Ошибка получения распарсенных пользователей: {e}")
            return []


class TelegramBotStorage:
    def __init__(self, postgres_storage):
        self.tickets = {}
        self.users = {}
        self.ticket_counter = 1
        self.user_counter = 1
        self.postgres = postgres_storage
        self.load_data()

    def load_data(self):
        """Загрузка данных из файла"""
        try:
            with open('bot_data.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.tickets = data.get('tickets', {})
                self.users = data.get('users', {})
                self.ticket_counter = data.get('ticket_counter', 1)
                self.user_counter = data.get('user_counter', 1)
            logger.info("Данные загружены из файла")
        except FileNotFoundError:
            self.tickets = {}
            self.users = {}
            self.ticket_counter = 1
            self.user_counter = 1
            logger.info("Файл данных не найден, создана новая база")
        except Exception as e:
            logger.error(f"Ошибка загрузки данных: {e}")

    def save_data(self):
        """Сохранение данных в файл"""
        data = {
            'tickets': self.tickets,
            'users': self.users,
            'ticket_counter': self.ticket_counter,
            'user_counter': self.user_counter
        }
        try:
            with open('bot_data.json', 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            logger.info("Данные сохранены в файл")
        except Exception as e:
            logger.error(f"Ошибка сохранения данных: {e}")

    def add_user(self, user_data):
        """Добавление пользователя"""
        user_id = str(user_data['id'])
        if user_id not in self.users:
            self.users[user_id] = {
                'username': user_data.get('username'),
                'first_name': user_data.get('first_name'),
                'last_name': user_data.get('last_name'),
                'registered_at': datetime.datetime.now().isoformat(),
                'id': self.user_counter
            }
            self.user_counter += 1
            self.save_data()

            # Дублируем в PostgreSQL
            self.postgres.add_telegram_user(user_data)
            logger.info(f"Новый пользователь добавлен: {user_id}")
            return True
        return False

    def add_ticket(self, user_id, message):
        """Добавление заявки"""
        ticket_id = self.ticket_counter
        user_info = self.users.get(str(user_id), {})

        self.tickets[str(ticket_id)] = {
            'user_id': str(user_id),
            'username': user_info.get('username'),
            'first_name': user_info.get('first_name'),
            'message': message,
            'status': 'open',
            'created_at': datetime.datetime.now().isoformat(),
            'admin_id': None,
            'admin_username': None,
            'responses': []
        }
        self.ticket_counter += 1
        self.save_data()

        # Дублируем в PostgreSQL
        postgres_ticket_id = self.postgres.add_ticket(
            user_id,
            message,
            user_info.get('username'),
            user_info.get('first_name')
        )

        logger.info(f"Создана заявка #{ticket_id} для пользователя {user_id}")
        return ticket_id

    def get_user_tickets(self, user_id):
        """Получение заявок пользователя"""
        user_tickets = []
        for ticket_id, ticket in self.tickets.items():
            if ticket['user_id'] == str(user_id):
                user_tickets.append((int(ticket_id), ticket))
        return sorted(user_tickets, key=lambda x: x[1]['created_at'], reverse=True)

    def get_ticket(self, ticket_id):
        """Получение заявки по ID"""
        return self.tickets.get(str(ticket_id))

    def update_ticket_status(self, ticket_id, status, admin_id=None, admin_username=None):
        """Обновление статуса заявки"""
        ticket = self.tickets.get(str(ticket_id))
        if ticket:
            ticket['status'] = status
            if admin_id:
                ticket['admin_id'] = admin_id
                ticket['admin_username'] = admin_username
            self.save_data()
            logger.info(f"Статус заявки #{ticket_id} изменен на {status}")
            return True
        return False

    def add_response(self, ticket_id, response_text, is_admin=False):
        """Добавление ответа к заявке"""
        ticket = self.tickets.get(str(ticket_id))
        if ticket:
            if 'responses' not in ticket:
                ticket['responses'] = []
            ticket['responses'].append({
                'text': response_text,
                'is_admin': is_admin,
                'timestamp': datetime.datetime.now().isoformat()
            })
            self.save_data()
            logger.info(f"Добавлен ответ к заявке #{ticket_id}")
            return True
        return False

    def get_open_tickets(self):
        """Получение открытых заявок"""
        return [ticket for ticket in self.tickets.values() if ticket['status'] == 'open']

    def get_in_progress_tickets(self):
        """Получение заявок в работе"""
        return [ticket for ticket in self.tickets.values() if ticket['status'] == 'in_progress']

    def get_closed_tickets(self):
        """Получение закрытых заявок"""
        return [ticket for ticket in self.tickets.values() if ticket['status'] == 'closed']

    def get_today_tickets(self):
        """Получение заявок за сегодня"""
        today = datetime.datetime.now().date()
        today_tickets = []
        for ticket in self.tickets.values():
            ticket_date = datetime.datetime.fromisoformat(ticket['created_at']).date()
            if ticket_date == today:
                today_tickets.append(ticket)
        return today_tickets

    def get_all_users(self):
        """Получение всех пользователей"""
        return self.users


# Инициализация хранилищ
postgres_storage = PostgreSQLStorage(DB_CONFIG)
storage = TelegramBotStorage(postgres_storage)


# Клавиатура главного меню
def main_menu():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(KeyboardButton('❓ Задать вопрос'))
    keyboard.add(KeyboardButton('📋 Мои заявки'))
    keyboard.add(KeyboardButton('ℹ️ О казино'))
    keyboard.add(KeyboardButton('📞 Контакты'))
    return keyboard


# Клавиатура админа
def admin_menu():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(KeyboardButton('📊 Статистика'))
    keyboard.add(KeyboardButton('📋 Активные заявки'))
    keyboard.add(KeyboardButton('👥 Все пользователи'))
    keyboard.add(KeyboardButton('📥 Парсинг данных'))
    keyboard.add(KeyboardButton('📖 Инструкция'))
    keyboard.add(KeyboardButton('🔍 Проверить данные'))
    return keyboard


def notify_admins_about_new_user(user_data):
    """Уведомление администраторов о новом пользователе"""
    user_info = (
        f"👤 Зарегистрирован новый пользователь:\n"
        f"🆔 ID: {user_data['id']}\n"
        f"👤 Имя: {user_data.get('first_name', 'Не указано')}\n"
        f"📛 Фамилия: {user_data.get('last_name', 'Не указана')}\n"
        f"📧 Username: @{user_data.get('username', 'Не указан')}\n"
        f"⏰ Время: {datetime.datetime.now().strftime('%H:%M %d.%m.%Y')}"
    )

    for admin_id in ADMIN_IDS:
        try:
            bot.send_message(admin_id, user_info)
            logger.info(f"Уведомление о новом пользователе отправлено админу {admin_id}")
        except Exception as e:
            logger.error(f"Ошибка отправки уведомления админу {admin_id}: {e}")


# ФУНКЦИИ ДЛЯ ПАРСИНГА ДАННЫХ
def parse_local_storage_data(message):
    """Парсинг данных из localStorage сайта"""
    try:
        logger.info(f"Начало парсинга данных от пользователя {message.from_user.id}")

        # Пытаемся распарсить JSON из сообщения
        data = json.loads(message.text)
        logger.info("JSON успешно распарсен")

        # Ищем пользователей рекурсивно во всех полях
        parsed_users = deep_search_users(data)
        logger.info(f"Найдено {len(parsed_users)} пользователей при парсинге")

        if not parsed_users:
            bot.send_message(message.chat.id, "❌ Не удалось извлечь данные пользователей.")
            return

        # Показываем сколько найдено
        bot.send_message(message.chat.id, f"🔍 Найдено пользователей: {len(parsed_users)}")

        # Создаем отчет
        report = create_users_report(parsed_users)
        bot.send_message(message.chat.id, report, parse_mode='HTML')

        # Сохраняем данные в PostgreSQL
        saved_count = postgres_storage.add_parsed_users(parsed_users, message.from_user.id)

        if saved_count > 0:
            bot.send_message(message.chat.id, f"✅ Данные сохранены в PostgreSQL ({saved_count} пользователей)")
        else:
            bot.send_message(message.chat.id, "❌ Не удалось сохранить данные в PostgreSQL")

    except json.JSONDecodeError as e:
        logger.error(f"Ошибка JSON: {e}")
        # Если это не JSON, пытаемся извлечь данные другими способами
        extract_from_text(message)
    except Exception as e:
        logger.error(f"Ошибка при обработке данных: {e}")
        bot.send_message(message.chat.id, f"❌ Ошибка при обработке данных: {str(e)}")


def deep_search_users(data, path=""):
    """Рекурсивный поиск пользователей в данных"""
    parsed_users = []

    if isinstance(data, dict):
        # Проверяем текущий объект на наличие полей пользователя
        if is_user_object(data):
            user = parse_user_object(data)
            if user:
                parsed_users.append(user)

        # Рекурсивно проверяем все значения
        for key, value in data.items():
            new_path = f"{path}.{key}" if path else key
            parsed_users.extend(deep_search_users(value, new_path))

    elif isinstance(data, list):
        # Проверяем каждый элемент списка
        for i, item in enumerate(data):
            new_path = f"{path}[{i}]"
            parsed_users.extend(deep_search_users(item, new_path))

    elif isinstance(data, str):
        # Пытаемся распарсить строку как JSON
        if looks_like_json(data):
            try:
                parsed_data = json.loads(data)
                parsed_users.extend(deep_search_users(parsed_data, path))
            except:
                pass

    return parsed_users


def is_user_object(obj):
    """Проверяет, является ли объект пользователем"""
    if not isinstance(obj, dict):
        return False

    # Проверяем наличие ключевых полей пользователя
    has_username = 'username' in obj
    has_balance = 'balance' in obj

    return has_username or has_balance


def parse_user_object(user):
    """Парсинг объекта пользователя"""
    try:
        username = user.get('username')
        if not username:
            logger.warning("Пользователь без username пропущен")
            return None

        # Преобразуем баланс в число
        balance = user.get('balance', 0)
        if isinstance(balance, str):
            try:
                # Убираем лишние символы и преобразуем
                balance = float(balance.replace('₽', '').replace(',', '').replace(' ', '').strip())
            except ValueError:
                balance = 0
                logger.warning(f"Не удалось преобразовать баланс: {user.get('balance')}")

        user_data = {
            'username': username,
            'balance': balance,
            'vip_status': user.get('vipStatus') or user.get('vip_status', 'Нет'),
            'registration_date': user.get('registrationDate', 'Неизвестно')
        }

        logger.info(f"Парсинг пользователя: {user_data}")
        return user_data

    except Exception as e:
        logger.error(f"Ошибка парсинга пользователя {user}: {e}")
        return None


def looks_like_json(text):
    """Проверяет, похожа ли строка на JSON"""
    text = text.strip()
    return (text.startswith('{') and text.endswith('}')) or (text.startswith('[') and text.endswith(']'))


def create_users_report(users):
    """Создание отчета по пользователям"""
    if not users:
        return "❌ Нет данных о пользователях для отчета"

    total_users = len(users)
    total_balance = sum(user['balance'] for user in users)
    vip_users = len([user for user in users if user['vip_status'] != 'Нет' and user['vip_status'] is not None])

    report = f"""
📊 <b>ОТЧЕТ О ПОЛЬЗОВАТЕЛЯХ С САЙТА</b>

👥 <b>Всего пользователей:</b> {total_users}
💰 <b>Общий баланс:</b> {total_balance:,.2f} ₽
👑 <b>VIP пользователей:</b> {vip_users}

<b>ТОП-10 ПО БАЛАНСУ:</b>
"""

    # Добавляем топ-10 пользователей по балансу
    top_users = sorted(users, key=lambda x: x['balance'], reverse=True)[:10]

    for i, user in enumerate(top_users, 1):
        vip_badge = "👑" if user['vip_status'] != 'Нет' and user['vip_status'] is not None else "👤"
        report += f"\n{i}. {vip_badge} <b>{user['username']}</b>"
        report += f"\n   💰 Баланс: {user['balance']:,.2f} ₽"
        if user['vip_status'] != 'Нет' and user['vip_status'] is not None:
            report += f"\n   🏆 VIP: {user['vip_status']}"
        if user['registration_date'] != 'Неизвестно':
            try:
                reg_date = datetime.datetime.fromisoformat(user['registration_date'].replace('Z', '+00:00'))
                report += f"\n   📅 Регистрация: {reg_date.strftime('%d.%m.%Y')}"
            except:
                report += f"\n   📅 Регистрация: {user['registration_date']}"
        report += "\n   ─────────────────"

    if total_users > 10:
        report += f"\n\n... и еще {total_users - 10} пользователей"

    report += f"\n\n⏰ Отчет создан: {datetime.datetime.now().strftime('%d.%m.%Y %H:%M')}"

    return report


def extract_from_text(message):
    """Извлечение данных из текстового формата"""
    text = message.text
    logger.info("Извлечение данных из текста")

    # Пытаемся найти данные в различных форматах
    patterns = [
        r'"users"\s*:\s*"([^"]+)"',  # "users": "[...]"
        r"'users'\s*:\s*'([^']+)'",  # 'users': '[...]'
        r'"users"\s*:\s*(\[[^]]+\])',  # "users": [...]
        r"'users'\s*:\s*(\[[^]]+\])",  # 'users': [...]
        r'users\s*=\s*"([^"]+)"',  # users = "[...]"
        r'users\s*=\s*\'([^\']+)\''  # users = '[...]'
    ]

    for pattern in patterns:
        match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
        if match:
            users_text = match.group(1)
            try:
                # Пробуем распарсить извлеченный текст
                users_data = json.loads(users_text)
                parsed_users = deep_search_users(users_data)
                if parsed_users:
                    report = create_users_report(parsed_users)
                    bot.send_message(message.chat.id, report, parse_mode='HTML')

                    # Сохраняем в PostgreSQL
                    saved_count = postgres_storage.add_parsed_users(parsed_users, message.from_user.id)
                    if saved_count > 0:
                        bot.send_message(message.chat.id,
                                         f"✅ Данные сохранены в PostgreSQL ({saved_count} пользователей)")
                    return
            except Exception as e:
                logger.error(f"Ошибка парсинга из текста: {e}")
                continue

    # Если не нашли структурированные данные, пробуем найти отдельные пользователи
    parsed_users = []

    # Ищем JSON-объекты пользователей в тексте
    user_objects = re.findall(r'\{[^{}]*username[^{}]*balance[^{}]*\}', text)
    for user_obj in user_objects:
        try:
            # Добавляем кавычки к ключам для валидного JSON
            json_str = re.sub(r'(\w+):', r'"\1":', user_obj)
            user_data = json.loads(json_str)
            user = parse_user_object(user_data)
            if user:
                parsed_users.append(user)
        except Exception as e:
            logger.error(f"Ошибка парсинга объекта пользователя: {e}")
            continue

    if parsed_users:
        report = create_users_report(parsed_users)
        bot.send_message(message.chat.id, report, parse_mode='HTML')

        # Сохраняем в PostgreSQL
        saved_count = postgres_storage.add_parsed_users(parsed_users, message.from_user.id)
        if saved_count > 0:
            bot.send_message(message.chat.id, f"✅ Данные сохранены в PostgreSQL ({saved_count} пользователей)")
    else:
        bot.send_message(message.chat.id,
                         "❌ Не удалось распознать данные.\n\n"
                         "<b>Как получить данные:</b>\n"
                         "1. Откройте сайт в браузере\n"
                         "2. Нажмите F12 → Console\n"
                         "3. Введите: <code>JSON.stringify(localStorage)</code>\n"
                         "4. Скопируйте и отправьте результат\n\n"
                         "<b>Пример правильных данных:</b>\n"
                         "<code>{\"users\": \"[{\\\"username\\\": \\\"test\\\", \\\"balance\\\": 1000}]\"}</code>",
                         parse_mode='HTML')


def get_parsed_stats(message):
    """Статистика по всем распарсенным данным"""
    try:
        # Получаем статистику из PostgreSQL
        stats = postgres_storage.get_parsed_users_stats()

        if not stats:
            bot.send_message(message.chat.id, "📭 Нет сохраненных данных парсинга.")
            return

        last_parse_time = stats['last_parse'].strftime('%d.%m.%Y %H:%M') if stats['last_parse'] else 'Неизвестно'

        stats_text = f"""
📈 <b>СТАТИСТИКА ПАРСИНГОВ ИЗ POSTGRESQL</b>

👥 <b>Всего пользователей в базе:</b> {stats['total_users']}
💰 <b>Суммарный баланс:</b> {stats['total_balance']:,.2f} ₽
👑 <b>VIP пользователей:</b> {stats['vip_users']}

<b>ПОСЛЕДНИЙ ПАРСИНГ:</b>
⏰ <b>Дата:</b> {last_parse_time}

<b>КОМАНДЫ:</b>
/parse_history - История парсингов
/clear_parsed - Очистить данные
"""
        bot.send_message(message.chat.id, stats_text, parse_mode='HTML')

    except Exception as e:
        logger.error(f"Ошибка получения статистики: {e}")
        bot.send_message(message.chat.id, f"❌ Ошибка получения статистики: {str(e)}")


# ОСНОВНЫЕ ОБРАБОТЧИКИ КОМАНД
@bot.message_handler(commands=['start'])
def start_command(message):
    user_id = message.from_user.id
    user_data = {
        'id': user_id,
        'username': message.from_user.username,
        'first_name': message.from_user.first_name,
        'last_name': message.from_user.last_name
    }

    # Добавляем пользователя и проверяем, новый ли он
    is_new_user = storage.add_user(user_data)

    # Если пользователь новый - уведомляем админов
    if is_new_user:
        notify_admins_about_new_user(user_data)

    welcome_text = """
🎰 Добро пожаловать в службу поддержки Neon Casino! 🎰

Я ваш виртуальный помощник. Чем могу помочь?

Доступные команды:
❓ Задать вопрос - Создать заявку в поддержку
📋 Мои заявки - Посмотреть статус ваших обращений
ℹ️ О казино - Узнать больше о нашем казино
📞 Контакты - Связаться с нами

Для срочной помощи напишите: @username_менеджера
    """

    if user_id in ADMIN_IDS:
        bot.send_message(message.chat.id, welcome_text, reply_markup=admin_menu())
    else:
        bot.send_message(message.chat.id, welcome_text, reply_markup=main_menu())


@bot.message_handler(commands=['parse'])
def parse_command(message):
    """Обработчик команды парсинга"""
    if message.from_user.id not in ADMIN_IDS:
        bot.send_message(message.chat.id, "❌ Эта команда только для администраторов.")
        return

    help_text = """
📥 <b>ПАРСИНГ ДАННЫХ С САЙТА</b>

<b>Как получить данные:</b>
1. Откройте сайт в браузере
2. Нажмите F12 → Вкладка Console
3. Введите команду:
   <code>JSON.stringify(localStorage)</code>
4. Скопируйте ВЕСЬ полученный текст
5. Отправьте его этим сообщением

<b>Альтернативный способ:</b>
1. В консоли браузера:
   <code>copy(JSON.stringify(localStorage))</code>
2. Затем вставьте сюда (Ctrl+V)

<b>Поддерживаемые данные:</b>
• Информация о пользователях
• Балансы
• VIP статусы
• Даты регистрации

Отправьте данные сейчас:
"""
    msg = bot.send_message(message.chat.id, help_text, parse_mode='HTML')
    bot.register_next_step_handler(msg, parse_local_storage_data)


@bot.message_handler(commands=['parse_stats'])
def parse_stats_command(message):
    """Статистика парсингов"""
    if message.from_user.id not in ADMIN_IDS:
        bot.send_message(message.chat.id, "❌ Эта команда только для администраторов.")
        return
    get_parsed_stats(message)


@bot.message_handler(commands=['parse_history'])
def parse_history_command(message):
    """История парсингов"""
    if message.from_user.id not in ADMIN_IDS:
        bot.send_message(message.chat.id, "❌ Эта команда только для администраторов.")
        return

    try:
        recent_users = postgres_storage.get_recent_parsed_users(10)

        if not recent_users:
            bot.send_message(message.chat.id, "📭 Нет данных о последних парсингах.")
            return

        response = "📋 <b>ПОСЛЕДНИЕ РАСПАРСЕННЫЕ ПОЛЬЗОВАТЕЛИ:</b>\n\n"

        for i, user in enumerate(recent_users, 1):
            vip_badge = "👑" if user['vip_status'] != 'Нет' and user['vip_status'] is not None else "👤"
            response += f"{i}. {vip_badge} <b>{user['username']}</b>\n"
            response += f"   💰 Баланс: {user['balance']:,.2f} ₽\n"
            if user['vip_status'] != 'Нет' and user['vip_status'] is not None:
                response += f"   🏆 VIP: {user['vip_status']}\n"
            response += f"   ⏰ Дата: {user['parsed_at'].strftime('%d.%m.%Y %H:%M')}\n"
            response += "   ─────────────────\n"

        bot.send_message(message.chat.id, response, parse_mode='HTML')

    except Exception as e:
        logger.error(f"Ошибка получения истории парсингов: {e}")
        bot.send_message(message.chat.id, f"❌ Ошибка получения истории: {str(e)}")


@bot.message_handler(commands=['clear_parsed'])
def clear_parsed_command(message):
    """Очистка данных парсинга"""
    if message.from_user.id not in ADMIN_IDS:
        bot.send_message(message.chat.id, "❌ Эта команда только для администраторов.")
        return

    try:
        conn = postgres_storage.get_connection()
        if conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM parsed_users')
            deleted_count = cursor.rowcount
            conn.commit()
            cursor.close()
            conn.close()

            logger.info(f"Очищено {deleted_count} записей из parsed_users")
            bot.send_message(message.chat.id,
                             f"✅ Данные парсинга очищены из PostgreSQL. Удалено записей: {deleted_count}")
        else:
            bot.send_message(message.chat.id, "❌ Нет подключения к PostgreSQL")
    except Exception as e:
        logger.error(f"Ошибка очистки данных: {e}")
        bot.send_message(message.chat.id, f"❌ Ошибка очистки данных: {str(e)}")


@bot.message_handler(commands=['check_data'])
def check_data_command(message):
    """Проверка данных в таблице parsed_users"""
    if message.from_user.id not in ADMIN_IDS:
        bot.send_message(message.chat.id, "❌ Эта команда только для администраторов.")
        return

    try:
        count = postgres_storage.get_parsed_users_count()
        recent_users = postgres_storage.get_recent_parsed_users(5)

        response = f"📊 <b>ПРОВЕРКА ДАННЫХ В POSTGRESQL</b>\n\n"
        response += f"👥 <b>Всего пользователей в базе:</b> {count}\n\n"

        if recent_users:
            response += "<b>Последние 5 записей:</b>\n"
            for user in recent_users:
                response += f"👤 {user['username']} | 💰 {user['balance']:,.2f} ₽ | 👑 {user['vip_status']} | ⏰ {user['parsed_at'].strftime('%d.%m.%Y %H:%M')}\n"
        else:
            response += "📭 Нет записей в таблице parsed_users\n"

        bot.send_message(message.chat.id, response, parse_mode='HTML')

    except Exception as e:
        logger.error(f"Ошибка проверки данных: {e}")
        bot.send_message(message.chat.id, f"❌ Ошибка проверки данных: {str(e)}")


# ОБРАБОТЧИКИ КНОПОК
@bot.message_handler(func=lambda message: message.text == '❓ Задать вопрос')
def ask_question(message):
    msg = bot.send_message(message.chat.id,
                           "📝 Опишите ваш вопрос или проблему подробно:\n\n"
                           "Пример: Не могу вывести средства с баланса")
    bot.register_next_step_handler(msg, process_question)


def process_question(message):
    user_id = message.from_user.id
    question = message.text

    ticket_id = storage.add_ticket(user_id, question)

    user_info = storage.users.get(str(user_id), {})
    for admin_id in ADMIN_IDS:
        try:
            bot.send_message(
                admin_id,
                f"🆕 Новая заявка #{ticket_id}\n\n"
                f"👤 Пользователь: {user_info.get('first_name', 'Unknown')} (@{user_info.get('username', 'NoUsername')})\n"
                f"📝 Вопрос: {question}\n\n"
                f"💬 Для ответа просто напишите сообщение начинающееся с #{ticket_id}"
            )
        except Exception as e:
            logger.error(f"Ошибка отправки уведомления админу {admin_id}: {e}")

    bot.send_message(
        message.chat.id,
        f"✅ Ваш вопрос принят!\n\n"
        f"🆔 Номер заявки: #{ticket_id}\n"
        f"⏰ Время: {datetime.datetime.now().strftime('%H:%M %d.%m.%Y')}\n\n"
        f"Мы ответим вам в ближайшее время!",
        reply_markup=main_menu()
    )


@bot.message_handler(func=lambda message: message.text == '📋 Мои заявки')
def my_tickets(message):
    user_id = message.from_user.id
    tickets = storage.get_user_tickets(user_id)

    if not tickets:
        bot.send_message(message.chat.id, "📭 У вас пока нет активных заявок.")
        return

    response = "📋 Ваши последние заявки:\n\n"
    for ticket_id, ticket in tickets[:10]:
        status_emoji = "✅" if ticket['status'] == 'closed' else "🟡" if ticket['status'] == 'in_progress' else "🆕"
        response += f"{status_emoji} Заявка #{ticket_id}\n"
        response += f"📝 Тема: {ticket['message'][:50]}...\n"
        response += f"📊 Статус: {ticket['status']}\n"
        response += f"⏰ Создана: {datetime.datetime.fromisoformat(ticket['created_at']).strftime('%H:%M %d.%m.%Y')}\n\n"

    bot.send_message(message.chat.id, response)


@bot.message_handler(func=lambda message: message.text == 'ℹ️ О казино')
def about_casino(message):
    about_text = """
🎰 Neon Casino - премиум онлайн-казино 🎰

Наши преимущества:
✨ Более 1000 лицензионных игр
⚡ Мгновенные выплаты
🎁 Щедрые бонусы новичкам
🔒 Максимальная безопасность
👑 VIP программа

Игровые категории:
• 🎯 Игровые автоматы
• ♠️ Настольные игры
• 🎲 Live-казино
• ⚽ Ставки на спорт
• 📈 Бинарные опционы

Лицензия: Curacao eGaming № 8048/JAZ
    """
    bot.send_message(message.chat.id, about_text)


@bot.message_handler(func=lambda message: message.text == '📞 Контакты')
def contacts(message):
    contacts_text = """
📞 Контакты Neon Casino

Техническая поддержка:
👨‍💻 @neon_support_bot (этот бот)
📧 support@neon-casino.ru
⏰ 24/7

Отдел безопасности:
🔒 security@neon-casino.ru

Партнерская программа:
🤝 partners@neon-casino.ru

Официальный сайт:
🌐 https://neon-casino.ru

Мы в социальных сетях:
📱 Telegram: @neon_casino_news
    """
    bot.send_message(message.chat.id, contacts_text)


# АДМИНСКИЕ ФУНКЦИИ
@bot.message_handler(func=lambda message: message.text == '📊 Статистика' and message.from_user.id in ADMIN_IDS)
def admin_stats(message):
    # Получаем статистику из PostgreSQL
    ticket_stats = postgres_storage.get_ticket_stats()
    telegram_users_count = postgres_storage.get_telegram_users_count()
    parsed_stats = postgres_storage.get_parsed_users_stats()

    open_tickets = ticket_stats.get('open', 0)
    in_progress_tickets = ticket_stats.get('in_progress', 0)
    closed_tickets = ticket_stats.get('closed', 0)
    today_tickets = ticket_stats.get('today', 0)

    stats_text = f"""
📊 Статистика поддержки (PostgreSQL)

📨 Заявки:
🆕 Открытые: {open_tickets}
🟡 В работе: {in_progress_tickets}
✅ Закрытые: {closed_tickets}
📈 Сегодня: {today_tickets}

👥 Пользователи бота:
Всего: {telegram_users_count}
"""

    if parsed_stats:
        last_parse_time = parsed_stats['last_parse'].strftime('%d.%m.%Y %H:%M') if parsed_stats[
            'last_parse'] else 'Неизвестно'
        stats_text += f"""
📊 Парсинг пользователей:
👥 Всего: {parsed_stats['total_users']}
💰 Баланс: {parsed_stats['total_balance']:,.2f} ₽
👑 VIP: {parsed_stats['vip_users']}
⏰ Последний парсинг: {last_parse_time}
"""

    bot.send_message(message.chat.id, stats_text)


@bot.message_handler(func=lambda message: message.text == '📋 Активные заявки' and message.from_user.id in ADMIN_IDS)
def active_tickets(message):
    open_tickets = storage.get_open_tickets()
    in_progress_tickets = storage.get_in_progress_tickets()

    if not open_tickets and not in_progress_tickets:
        bot.send_message(message.chat.id, "🎉 Нет активных заявок! Все вопросы решены.")
        return

    response = "📋 Активные заявки:\n\n"

    if open_tickets:
        response += "🆕 Открытые заявки:\n"
        for ticket_id, ticket_data in storage.tickets.items():
            if ticket_data['status'] == 'open':
                response += f"#{ticket_id} - {ticket_data['message'][:30]}...\n"

    if in_progress_tickets:
        response += "\n🟡 Заявки в работе:\n"
        for ticket_id, ticket_data in storage.tickets.items():
            if ticket_data['status'] == 'in_progress':
                response += f"#{ticket_id} - {ticket_data['message'][:30]}...\n"

    bot.send_message(message.chat.id, response)


@bot.message_handler(func=lambda message: message.text == '👥 Все пользователи' and message.from_user.id in ADMIN_IDS)
def all_users(message):
    users = postgres_storage.get_all_telegram_users()

    if not users:
        bot.send_message(message.chat.id, "📭 Нет зарегистрированных пользователей.")
        return

    response = f"👥 Все зарегистрированные пользователи ({len(users)}):\n\n"

    for user in users[:20]:  # Ограничиваем вывод первыми 20 пользователями
        reg_date = user['registered_at'].strftime('%d.%m.%Y %H:%M')
        response += (
            f"🆔 ID: {user['user_id']}\n"
            f"👤 Имя: {user.get('first_name', 'Не указано')}\n"
            f"📛 Фамилия: {user.get('last_name', 'Не указана')}\n"
            f"📧 Username: @{user.get('username', 'Не указан')}\n"
            f"⏰ Регистрация: {reg_date}\n"
            f"────────────────────\n"
        )

    if len(users) > 20:
        response += f"\n... и еще {len(users) - 20} пользователей"

    bot.send_message(message.chat.id, response)


@bot.message_handler(func=lambda message: message.text == '📥 Парсинг данных' and message.from_user.id in ADMIN_IDS)
def parse_data_button(message):
    parse_command(message)


@bot.message_handler(func=lambda message: message.text == '🔍 Проверить данные' and message.from_user.id in ADMIN_IDS)
def check_data_button(message):
    check_data_command(message)


@bot.message_handler(func=lambda message: message.text == '📖 Инструкция' and message.from_user.id in ADMIN_IDS)
def admin_instructions(message):
    instructions = """
📖 ИНСТРУКЦИЯ ДЛЯ АДМИНИСТРАТОРА

🛠️ ФУНКЦИОНАЛ АДМИН-ПАНЕЛИ:

1. 📊 СТАТИСТИКА
   - Показывает общую статистику по заявкам
   - Отображает количество пользователей
   - Показывает статистику парсингов

2. 📋 АКТИВНЫЕ ЗАЯВКИ
   - Список открытых заявок (статус: open)
   - Список заявок в работе (статус: in_progress)

3. 👥 ВСЕ ПОЛЬЗОВАТЕЛИ
   - Полный список зарегистрированных пользователей
   - Информация о дате регистрации

4. 📥 ПАРСИНГ ДАННЫХ
   - Парсинг пользователей с сайта казино
   - Анализ балансов и VIP статусов
   - Создание отчетов

5. 🔍 ПРОВЕРИТЬ ДАННЫЕ
   - Проверка данных в таблице parsed_users
   - Показывает последние записи

💬 РАБОТА С ЗАЯВКАМИ:

1. ОТВЕТ НА ЗАЯВКУ:
   Формат: #<номер_заявки> <ваш_ответ>
   Пример: #12 Здравствуйте! Ваша проблема решена.

2. ИЗМЕНЕНИЕ СТАТУСА ЗАЯВКИ:
   - Взять в работу: "В работу #<номер>"
   - Закрыть заявку: "Закрыть #<номер>"

3. ПРОСМОТР ИНФОРМАЦИИ О ЗАЯВКЕ:
   Отправьте только номер заявки с решеткой: #<номер>

📥 РАБОТА С ПАРСИНГОМ:

1. АВТОМАТИЧЕСКИЙ ПАРСИНГ:
   - Отправьте данные localStorage
   - Бот автоматически определит и распарсит

2. КОМАНДЫ ПАРСИНГА:
   /parse - Начать парсинг
   /parse_stats - Статистика парсингов
   /parse_history - История парсингов
   /check_data - Проверить данные в БД
   /clear_parsed - Очистить данные

🔔 УВЕДОМЛЕНИЯ:

- Автоматические уведомления о новых пользователях
- Уведомления о новых заявках
- Все уведомления приходят всем администраторам

📊 СТАТУСЫ ЗАЯВОК:

- 🆕 OPEN - новая заявка, ожидает ответа
- 🟡 IN_PROGRESS - заявка в работе
- ✅ CLOSED - заявка закрыта

💾 СИСТЕМА:

- Данные сохраняются в PostgreSQL
- Логирование всех действий

⚠️ ВАЖНО:

- Для ответа на заявку не нужно использовать меню
- Просто отправьте сообщение в нужном формате
- Все администраторы видят все заявки
- Изменения статуса сразу сохраняются

Для возврата в меню используйте кнопки ниже.
    """

    bot.send_message(message.chat.id, instructions, reply_markup=admin_menu())


# ОБРАБОТКА ОТВЕТОВ АДМИНОВ НА ЗАЯВКИ
@bot.message_handler(
    func=lambda message: message.from_user.id in ADMIN_IDS and message.text and message.text.startswith('#'))
def admin_ticket_response(message):
    try:
        parts = message.text.split(' ', 1)
        ticket_id_str = parts[0][1:]
        response_text = parts[1] if len(parts) > 1 else ""

        if not ticket_id_str.isdigit():
            return

        ticket_id = int(ticket_id_str)
        ticket = storage.get_ticket(ticket_id)

        if not ticket:
            bot.send_message(message.chat.id, f"❌ Заявка #{ticket_id} не найдена")
            return

        if not response_text:
            ticket_info = f"""
📋 Заявка #{ticket_id}

👤 Пользователь: {ticket['first_name']} (@{ticket['username']})
📝 Вопрос: {ticket['message']}
📊 Статус: {ticket['status']}
⏰ Создана: {datetime.datetime.fromisoformat(ticket['created_at']).strftime('%H:%M %d.%m.%Y')}

💬 Для ответа напишите: #{ticket_id} ваш ответ
            """
            bot.send_message(message.chat.id, ticket_info)
            return

        try:
            user_id = int(ticket['user_id'])

            bot.send_message(
                user_id,
                f"📨 Ответ от поддержки Neon Casino\n\n"
                f"{response_text}\n\n"
                f"🆔 Заявка: #{ticket_id}"
            )

            storage.update_ticket_status(ticket_id, 'in_progress', message.from_user.id, message.from_user.username)
            storage.add_response(ticket_id, response_text, is_admin=True)

            bot.send_message(message.chat.id, f"✅ Ответ отправлен пользователю по заявке #{ticket_id}")

        except Exception as e:
            bot.send_message(message.chat.id, f"❌ Не удалось отправить ответ: {str(e)}")

    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Ошибка обработки команды: {str(e)}")


# Обработка текстовых сообщений для закрытия заявок
@bot.message_handler(func=lambda message: message.from_user.id in ADMIN_IDS and 'Закрыть #' in message.text)
def close_ticket(message):
    try:
        ticket_id = int(message.text.split('#')[1])
        ticket = storage.get_ticket(ticket_id)

        if ticket:
            storage.update_ticket_status(ticket_id, 'closed', message.from_user.id, message.from_user.username)
            bot.send_message(message.chat.id, f"✅ Заявка #{ticket_id} закрыта")
        else:
            bot.send_message(message.chat.id, f"❌ Заявка #{ticket_id} не найдена")
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Ошибка: {str(e)}")


# Обработка текстовых сообщений для взятия заявки в работу
@bot.message_handler(func=lambda message: message.from_user.id in ADMIN_IDS and 'В работу #' in message.text)
def take_ticket_to_work(message):
    try:
        ticket_id = int(message.text.split('#')[1])
        ticket = storage.get_ticket(ticket_id)

        if ticket:
            storage.update_ticket_status(ticket_id, 'in_progress', message.from_user.id, message.from_user.username)
            bot.send_message(message.chat.id, f"🟡 Заявка #{ticket_id} взята в работу")
        else:
            bot.send_message(message.chat.id, f"❌ Заявка #{ticket_id} не найдена")
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Ошибка: {str(e)}")


# Функция автосохранения данных
def auto_save():
    while True:
        time.sleep(300)
        storage.save_data()
        logger.info("Данные автоматически сохранены")


# Запуск автосохранения в отдельном потоке
auto_save_thread = threading.Thread(target=auto_save, daemon=True)
auto_save_thread.start()

# Запуск бота
if __name__ == '__main__':
    logger.info("Бот поддержки Neon Casino запущен...")
    print("Бот запущен! Для остановки нажмите Ctrl+C")

    try:
        bot.polling(none_stop=True, skip_pending=True)
    except KeyboardInterrupt:
        print("\nБот остановлен.")
    except Exception as e:
        logger.error(f"Ошибка запуска бота: {e}")
    finally:
        storage.save_data()
        print("Данные сохранены.")