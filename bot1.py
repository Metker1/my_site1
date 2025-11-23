import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
import datetime
import json
import threading
import time
import logging

# Настройки бота
BOT_TOKEN = '8421270114:AAGWIyRCWX_ncdlhVs_B45HpNLwKyjcAyoQ'
ADMIN_IDS = [5710697156]  # Замените на ID администраторов

# Инициализация бота
bot = telebot.TeleBot(BOT_TOKEN)


# Встроенное хранилище данных в памяти бота
class TelegramBotStorage:
    def __init__(self):
        self.tickets = {}
        self.users = {}
        self.ticket_counter = 1
        self.user_counter = 1
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
        except FileNotFoundError:
            self.tickets = {}
            self.users = {}
            self.ticket_counter = 1
            self.user_counter = 1

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
        except Exception as e:
            print(f"Ошибка сохранения данных: {e}")

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
            return True
        return False

    def add_ticket(self, user_id, message):
        """Добавление заявки"""
        ticket_id = self.ticket_counter
        self.tickets[str(ticket_id)] = {
            'user_id': str(user_id),
            'username': self.users.get(str(user_id), {}).get('username'),
            'first_name': self.users.get(str(user_id), {}).get('first_name'),
            'message': message,
            'status': 'open',
            'created_at': datetime.datetime.now().isoformat(),
            'admin_id': None,
            'admin_username': None,
            'responses': []
        }
        self.ticket_counter += 1
        self.save_data()
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


# Инициализация хранилища
storage = TelegramBotStorage()

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


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
    keyboard.add(KeyboardButton('📖 Инструкция'))  # Заменяем "Главное меню" на "Инструкция"
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


# Обработчик команды /start
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


# Обработчик кнопки "Задать вопрос"
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


# Обработчик кнопки "Мои заявки"
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


# Обработчик кнопки "О казино"
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


# Обработчик кнопки "Контакты"
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


# Админские функции
@bot.message_handler(func=lambda message: message.text == '📊 Статистика' and message.from_user.id in ADMIN_IDS)
def admin_stats(message):
    open_tickets = len(storage.get_open_tickets())
    in_progress_tickets = len(storage.get_in_progress_tickets())
    closed_tickets = len(storage.get_closed_tickets())
    today_tickets = len(storage.get_today_tickets())
    total_users = len(storage.users)

    stats_text = f"""
📊 Статистика поддержки

📨 Заявки:
🆕 Открытые: {open_tickets}
🟡 В работе: {in_progress_tickets}
✅ Закрытые: {closed_tickets}
📈 Сегодня: {today_tickets}

👥 Пользователи:
Всего: {total_users}

💾 Память бота:
Заявок: {len(storage.tickets)}
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


# Функция - вывод всех пользователей
@bot.message_handler(func=lambda message: message.text == '👥 Все пользователи' and message.from_user.id in ADMIN_IDS)
def all_users(message):
    users = storage.get_all_users()

    if not users:
        bot.send_message(message.chat.id, "📭 Нет зарегистрированных пользователей.")
        return

    response = f"👥 Все зарегистрированные пользователи ({len(users)}):\n\n"

    for user_id, user_data in list(users.items())[:50]:  # Ограничиваем вывод первыми 50 пользователями
        reg_date = datetime.datetime.fromisoformat(user_data['registered_at']).strftime('%d.%m.%Y %H:%M')
        response += (
            f"🆔 ID: {user_data['id']}\n"
            f"👤 Имя: {user_data.get('first_name', 'Не указано')}\n"
            f"📛 Фамилия: {user_data.get('last_name', 'Не указана')}\n"
            f"📧 Username: @{user_data.get('username', 'Не указан')}\n"
            f"⏰ Регистрация: {reg_date}\n"
            f"────────────────────\n"
        )

    if len(users) > 50:
        response += f"\n... и еще {len(users) - 50} пользователей"

    bot.send_message(message.chat.id, response)


# Новая функция - инструкция для админов
@bot.message_handler(func=lambda message: message.text == '📖 Инструкция' and message.from_user.id in ADMIN_IDS)
def admin_instructions(message):
    instructions = """
📖 ИНСТРУКЦИЯ ДЛЯ АДМИНИСТРАТОРА

🛠️ ФУНКЦИОНАЛ АДМИН-ПАНЕЛИ:

1. 📊 СТАТИСТИКА
   - Показывает общую статистику по заявкам
   - Отображает количество пользователей
   - Показывает заявки за сегодня

2. 📋 АКТИВНЫЕ ЗАЯВКИ
   - Список открытых заявок (статус: open)
   - Список заявок в работе (статус: in_progress)

3. 👥 ВСЕ ПОЛЬЗОВАТЕЛИ
   - Полный список зарегистрированных пользователей
   - Информация о дате регистрации
   - Ограничение: первые 50 пользователей

💬 РАБОТА С ЗАЯВКАМИ:

1. ОТВЕТ НА ЗАЯВКУ:
   Формат: #<номер_заявки> <ваш_ответ>
   Пример: #12 Здравствуйте! Ваша проблема решена.

2. ИЗМЕНЕНИЕ СТАТУСА ЗАЯВКИ:
   - Взять в работу: "В работу #<номер>"
   - Закрыть заявку: "Закрыть #<номер>"

3. ПРОСМОТР ИНФОРМАЦИИ О ЗАЯВКЕ:
   Отправьте только номер заявки с решеткой: #<номер>

🔔 УВЕДОМЛЕНИЯ:

- Автоматические уведомления о новых пользователях
- Уведомления о новых заявках
- Все уведомления приходят всем администраторам

📊 СТАТУСЫ ЗАЯВОК:

- 🆕 OPEN - новая заявка, ожидает ответа
- 🟡 IN_PROGRESS - заявка в работе
- ✅ CLOSED - заявка закрыта

💾 СИСТЕМА:

- Автосохранение данных каждые 5 минут
- Данные хранятся в файле bot_data.json
- Логирование всех действий

⚠️ ВАЖНО:

- Для ответа на заявку не нужно использовать меню
- Просто отправьте сообщение в нужном формате
- Все администраторы видят все заявки
- Изменения статуса сразу сохраняются

Для возврата в меню используйте кнопки ниже.
    """

    bot.send_message(message.chat.id, instructions, reply_markup=admin_menu())


# Обработка ответов админов на заявки
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