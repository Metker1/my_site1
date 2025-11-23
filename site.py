import time
import telebot
from telebot import types
import os
from dotenv import load_dotenv
import json
import psycopg2
from datetime import date

# --- Конфигурация ---
load_dotenv()
TELEGRAM_TOKEN = '8421270114:AAGWIyRCWX_ncdlhVs_B45HpNLwKyjcAyoQ'
bot = telebot.TeleBot(TELEGRAM_TOKEN)

# Настройки базы данных
DB_HOST = os.getenv("DB_HOST", "127.0.0.1")
DB_NAME = os.getenv("DB_NAME", "bot_tg")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASS = os.getenv("DB_PASS", "Mashinist132")
DB_PORT = os.getenv("DB_PORT", "5432")

USER_DATA_FILE = "user_data.json"

# --- Работа с данными пользователя ---
def load_user_data():
    try:
        with open(USER_DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_user_data(data):
    with open(USER_DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

user_data = load_user_data()

def connect_to_db():
    try:
        return psycopg2.connect(host=DB_HOST, database=DB_NAME, user=DB_USER, password=DB_PASS, port=DB_PORT)
    except Exception as e:
        print(f"Ошибка подключения к базе данных: {e}")
        return None

def create_tables():
    conn = connect_to_db()
    if conn:
        try:
            cur = conn.cursor()
            cur.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id BIGINT PRIMARY KEY,
                    nickname VARCHAR(255),
                    info TEXT,
                    telegram_link VARCHAR(255)
                );
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS user_views (
                    user_id BIGINT,
                    viewed_user_id BIGINT,
                    view_date DATE,
                    PRIMARY KEY (user_id, viewed_user_id)
                );
            """)
            conn.commit()
            cur.close()
            conn.close()
            print("✅ Таблицы успешно созданы или уже существуют.")
        except Exception as e:
            print(f"❌ Ошибка при создании таблиц: {e}")

# Создаем таблицы при запуске
create_tables()

# --- Стейты регистрации ---
STATE_START = 0
STATE_NICKNAME = 1
STATE_INFO = 2
STATE_TELEGRAM_LINK = 3

# --- Стейты редактирования ---
STATE_EDIT_CHOICE = 10
STATE_EDIT_NICKNAME = 11
STATE_EDIT_INFO = 12
STATE_EDIT_TELEGRAM = 13

user_states = {}
edit_states = {}  # Для обработки редактирования профиля

# --- Обработка команды /start ---
@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    conn = connect_to_db()
    if conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE user_id = %s", (user_id,))
        existing_user = cur.fetchone()
        cur.close()
        conn.close()

        if existing_user:
            bot.send_message(message.chat.id, f"🎉 Привет, {existing_user[1]}! Рад снова видеть.",
                             reply_markup=main_menu())
            time.sleep(1)
            bot.send_message(message.chat.id, "Что ты хочешь сделать? 🤔", reply_markup=main_menu())
        else:
            bot.send_message(
                message.chat.id,
                "👋 Привет! Кажется, ты здесь впервые. Давай зарегистрируемся.\n"
                "Как тебя зовут (псевдоним)?"
            )
            user_states[user_id] = STATE_NICKNAME
    else:
        bot.send_message(message.chat.id, "❗️ Ошибка подключения к базе данных. Попробуйте позже.")

# --- Команда /profile ---
@bot.message_handler(commands=['profile'])
def profile_command(message):
    user_id = message.from_user.id
    conn = connect_to_db()
    if conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE user_id = %s", (user_id,))
        user_record = cur.fetchone()
        cur.close()
        conn.close()
        if user_record:
            profile_text = (
                f"✨ <b>Псевдоним:</b> {user_record[1]}\n"
                f"📝 <b>О себе:</b> {user_record[2]}\n"
                f"🔗 <b>Telegram:</b> {user_record[3]}"
            )
            bot.send_message(message.chat.id, profile_text, parse_mode="HTML")
        else:
            bot.send_message(message.chat.id, "Вы еще не зарегистрированы. Используйте /start для регистрации.")
    else:
        bot.send_message(message.chat.id, "❗️ Ошибка подключения к базе данных.")

# --- Главное меню ---
def main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add("🔍 Посмотреть анкеты", "ℹ️ Мой профиль", "✏️ Редактировать профиль", "🚪 Выйти")
    return markup

# --- Обработка кнопки "Мой профиль" ---
@bot.message_handler(func=lambda m: m.text == "ℹ️ Мой профиль")
def handle_both_tests(message):
    user_id = message.from_user.id
    conn = connect_to_db()
    if conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE user_id = %s", (user_id,))
        user_record = cur.fetchone()
        cur.close()
        conn.close()
        if user_record:
            profile_text = (
                f"✨ <b>Псевдоним:</b> {user_record[1]}\n"
                f"📝 <b>О себе:</b> {user_record[2]}\n"
                f"🔗 <b>Telegram:</b> {user_record[3]}"
            )
            bot.send_message(message.chat.id, profile_text, parse_mode="HTML")
        else:
            bot.send_message(message.chat.id, "Вы еще не зарегистрированы. Используйте /start для регистрации.")
    else:
        bot.send_message(message.chat.id, "❗️ Ошибка подключения к базе данных.")

# --- Обработка команды "Выйти" ---
@bot.message_handler(func=lambda m: m.text == "🚪 Выйти")
def handle_both_tests(message):
    bot.send_message(message.chat.id, f"❗️ Я тебя понял, ждем тебя позже 🤔 ")

# --- Обработка команды "✏️ Редактировать профиль" ---
@bot.message_handler(func=lambda m: m.text == "✏️ Редактировать профиль")
def edit_profile_start(message):
    user_id = message.from_user.id
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("Изменить псевдоним", "Изменить описание", "Изменить Telegram ссылку", "Отменить")
    bot.send_message(message.chat.id, "Что бы вы хотели изменить?", reply_markup=markup)
    edit_states[user_id] = {'step': 'choice'}

# --- Обработка выбора редактирования ---
@bot.message_handler(
    func=lambda m: m.chat.type == 'private' and m.from_user.id in edit_states and edit_states[m.from_user.id]['step'] == 'choice')
def handle_edit_choice(message):
    user_id = message.from_user.id
    choice = message.text
    if choice == "Изменить псевдоним":
        bot.send_message(message.chat.id, "Введите новый псевдоним:")
        edit_states[user_id]['step'] = 'nickname'
    elif choice == "Изменить описание":
        bot.send_message(message.chat.id, "Введите новое описание (о себе):")
        edit_states[user_id]['step'] = 'info'
    elif choice == "Изменить Telegram ссылку":
        bot.send_message(message.chat.id, "Введите новую ссылку на Telegram:")
        edit_states[user_id]['step'] = 'telegram'
    elif choice == "Отменить":
        bot.send_message(message.chat.id, "Редактирование отменено.", reply_markup=main_menu())
        edit_states.pop(user_id)
    else:
        bot.send_message(message.chat.id, "Пожалуйста, выберите один из вариантов.")

# --- Обработка ввода новых данных ---
@bot.message_handler(
    func=lambda m: m.chat.type == 'private' and m.from_user.id in edit_states and edit_states[m.from_user.id]['step'] in ['nickname', 'info', 'telegram'])
def handle_edit_input(message):
    user_id = message.from_user.id
    step = edit_states[user_id]['step']
    new_value = message.text.strip()
    # Получить текущие данные пользователя
    conn = connect_to_db()
    if conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE user_id = %s", (user_id,))
        user_record = cur.fetchone()
        if user_record:
            nickname, info, telegram_link = user_record[1], user_record[2], user_record[3]
            if step == 'nickname':
                nickname = new_value
            elif step == 'info':
                info = new_value
            elif step == 'telegram':
                telegram_link = new_value
            # Обновить запись
            try:
                cur.execute("""
                    UPDATE users SET nickname=%s, info=%s, telegram_link=%s WHERE user_id=%s
                """, (nickname, info, telegram_link, user_id))
                conn.commit()
                bot.send_message(message.chat.id, "✅ Профиль успешно обновлен.", reply_markup=main_menu())
            except Exception as e:
                bot.send_message(message.chat.id, "❗️ Ошибка при обновлении профиля.")
        else:
            bot.send_message(message.chat.id, "Пользователь не найден.")
        cur.close()
        conn.close()
    else:
        bot.send_message(message.chat.id, "❗️ Ошибка подключения к базе данных.")
    # Удаляем состояние редактирования
    edit_states.pop(user_id)

# --- Обработка регистрации ---
@bot.message_handler(func=lambda m: user_states.get(m.from_user.id) == STATE_NICKNAME)
def process_nickname(message):
    user_id = message.from_user.id
    nickname = message.text.strip()
    user_states[user_id] = STATE_INFO
    user_states[user_id + 100000] = nickname
    bot.send_message(message.chat.id, f"Отлично, {nickname}! Расскажи немного о себе (пара предложений).")

@bot.message_handler(func=lambda m: user_states.get(m.from_user.id) == STATE_INFO)
def process_info(message):
    user_id = message.from_user.id
    info = message.text.strip()
    user_states[user_id] = STATE_TELEGRAM_LINK
    user_states[user_id + 200000] = info
    bot.send_message(message.chat.id,
                     "👍 Замечательно! Теперь, пожалуйста, пришли свою ссылку на Telegram (например, @username).")

@bot.message_handler(func=lambda m: user_states.get(m.from_user.id) == STATE_TELEGRAM_LINK)
def process_telegram_link(message):
    user_id = message.from_user.id
    telegram_link = message.text.strip()
    nickname = user_states.pop(user_id + 100000, None)
    info = user_states.pop(user_id + 200000, None)
    conn = connect_to_db()
    if conn:
        try:
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO users (user_id, nickname, info, telegram_link)
                VALUES (%s, %s, %s, %s);
            """, (user_id, nickname, info, telegram_link))
            conn.commit()
            cur.close()
            conn.close()
            bot.send_message(message.chat.id, "✅ Регистрация завершена! Теперь вы можете просматривать анкеты.")
        except Exception as e:
            print(f"❌ Ошибка при сохранении пользователя: {e}")
            bot.send_message(message.chat.id, "❗️ Произошла ошибка при сохранении данных.")
    else:
        bot.send_message(message.chat.id, "❗️ Ошибка подключения к базе данных.")
    user_states[user_id] = STATE_START
    bot.send_message(message.chat.id, "📝 Главное меню:", reply_markup=main_menu())

# --- Просмотр анкет с пролистыванием по кругу (с учетом уже просмотренных) ---
view_profiles_state = {}

@bot.message_handler(func=lambda m: m.text == "🔍 Посмотреть анкеты")
def view_profiles(message):
    user_id = message.from_user.id
    conn = connect_to_db()
    if not conn:
        bot.send_message(message.chat.id, "❗️ Ошибка подключения к базе данных.")
        return

    cur = conn.cursor()
    # Получить всех пользователей, кроме текущего
    cur.execute("SELECT * FROM users WHERE user_id != %s", (user_id,))
    all_users = [row for row in cur.fetchall()]

    # Получить просмотренных сегодня
    cur.execute("SELECT viewed_user_id FROM user_views WHERE user_id = %s AND view_date = %s", (user_id, date.today()))
    viewed_today_ids = {row[0] for row in cur.fetchall()}

    # Исключить уже просмотренных (сегодня)
    remaining_users = [user for user in all_users if user[0] not in viewed_today_ids]

    # Если все просмотрены, покажем всех (по кругу)
    if not remaining_users:
        # Получить всех, кроме текущего (повторно)
        cur.execute("SELECT * FROM users WHERE user_id != %s", (user_id,))
        remaining_users = [row for row in cur.fetchall()]

        # Проверка, если и после этого все просмотрены (нет новых), сообщить
        viewed_ids = {row[0] for row in remaining_users}
        # Проверка, есть ли вообще еще не просмотренные
        if len(viewed_ids) >= len(remaining_users):
            # Все просмотрены
            conn.close()
            bot.send_message(message.chat.id, "🔚 Анкеты закончились. Больше новых сегодня нет.")
            return

    # Инициализация или обновление состояния для кругового просмотра
    if user_id not in view_profiles_state:
        view_profiles_state[user_id] = {
            'users': remaining_users,
            'index': 0
        }
    else:
        # Обновляем список, если он отличается
        view_profiles_state[user_id]['users'] = remaining_users
        # индекс остается, чтобы продолжить
        if view_profiles_state[user_id]['index'] >= len(remaining_users):
            view_profiles_state[user_id]['index'] = 0

    show_next_profile(message)

def show_next_profile(message):
    user_id = message.from_user.id
    state = view_profiles_state.get(user_id)
    if not state or not state['users']:
        bot.send_message(message.chat.id, "🚫 Нет доступных анкет для просмотра.")
        view_profiles_state.pop(user_id, None)
        return

    users_list = state['users']
    index = state['index']

    if not users_list:
        bot.send_message(message.chat.id, "🚫 Нет доступных анкет для просмотра.")
        view_profiles_state.pop(user_id, None)
        return

    # Выбираем текущий профиль
    user_profile = users_list[index]
    profile_id = user_profile[0]
    nickname = user_profile[1]
    info = user_profile[2]
    telegram_link = user_profile[3]

    profile_text = (
        f"✨ <b>Псевдоним:</b> {nickname}\n"
        f"📝 <b>О себе:</b> {info}\n"
        f"🔗 <b>Telegram:</b> {telegram_link}"
    )

    # Записываем просмотр
    conn = connect_to_db()
    if conn:
        try:
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO user_views (user_id, viewed_user_id, view_date) VALUES (%s, %s, %s) ON CONFLICT DO NOTHING",
                (user_id, profile_id, date.today())
            )
            conn.commit()
            cur.close()
            conn.close()
        except Exception as e:
            print(f"Ошибка при сохранении просмотра: {e}")

    # Создаем inline-кнопку "Следующий"
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("✅", callback_data="next_profile"))

    bot.send_message(message.chat.id, profile_text, parse_mode="HTML", reply_markup=markup)

    # Обновляем индекс для кругового просмотра
    state['index'] = (state['index'] + 1) % len(users_list)



# --- Запуск бота ---
bot.polling(none_stop=True)