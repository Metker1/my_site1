import telebot
from telebot import types

API_TOKEN = '8421270114:AAGWIyRCWX_ncdlhVs_B45HpNLwKyjcAyoQ'

bot = telebot.TeleBot(API_TOKEN)

# Списки для хранения пользователей по полу
waiting_users = {'male': [], 'female': []}
active_chats = {}  # user_id: partner_id
user_gender = {}  # user_id: 'male' или 'female'


@bot.message_handler(commands=['start'])
def handle_start(message):
    markup = types.InlineKeyboardMarkup(row_width=2)
    btn_male = types.InlineKeyboardButton('Мужчина', callback_data='gender_male')
    btn_female = types.InlineKeyboardButton('Женщина', callback_data='gender_female')
    markup.add(btn_male, btn_female)
    bot.send_message(
        message.chat.id,
        'Пожалуйста, выберите ваш пол:',
        reply_markup=markup
    )


@bot.callback_query_handler(func=lambda call: call.data.startswith('gender_'))
def handle_gender_selection(call):
    user_id = call.message.chat.id
    gender = call.data.split('_')[1]
    user_gender[user_id] = gender

    # Добавляем пользователя в очередь по его полу
    waiting_users[gender].append(user_id)
    # Удаляем клавиатуру
    bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id)
    bot.send_message(user_id, 'Вы добавлены в очередь. Ожидайте поиска собеседника...')
    find_partner(user_id)


def find_partner(user_id):
    user_gender_value = user_gender.get(user_id)
    opposite_gender = 'female' if user_gender_value == 'male' else 'male'

    # Проверяем, есть ли кто-то в очереди противоположного пола
    if waiting_users[opposite_gender]:
        partner_id = waiting_users[opposite_gender].pop(0)
        # Создаем чат
        active_chats[user_id] = partner_id
        active_chats[partner_id] = user_id
        # Оповещаем обоих
        start_chat_with_users(user_id, partner_id)
        start_chat_with_users(partner_id, user_id)
    else:
        # Пока никто не найден, пользователь ждет
        pass


def start_chat_with_users(user_id, partner_id):
    markup = types.InlineKeyboardMarkup(row_width=2)
    btn_leave = types.InlineKeyboardButton('Выйти из чата', callback_data='leave')
    btn_new = types.InlineKeyboardButton('Найти нового собеседника', callback_data='new')
    markup.add(btn_leave, btn_new)
    bot.send_message(
        user_id,
        'Вы подключены к собеседнику. Можете общаться или воспользоваться кнопками ниже.',
        reply_markup=markup
    )


@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    user_id = call.message.chat.id
    data = call.data

    if data == 'leave':
        leave_chat(user_id)
    elif data == 'new':
        start_new_chat(user_id)
    bot.answer_callback_query(call.id)


def leave_chat(user_id):
    if user_id in active_chats:
        partner_id = active_chats.pop(user_id)
        active_chats.pop(partner_id, None)
        bot.send_message(partner_id, 'Ваш собеседник вышел из чата.')
        bot.send_message(user_id, 'Вы покинули чат.')
        # Возвращаем их в очередь
        add_to_waiting_list(user_id)
        add_to_waiting_list(partner_id)


def start_new_chat(user_id):
    # Удаляем текущего партнера из активных чатов
    if user_id in active_chats:
        partner_id = active_chats.pop(user_id)
        active_chats.pop(partner_id, None)
        bot.send_message(partner_id, 'Ваш собеседник попросил начать новый чат.')
        # Возвращаем их в очередь
        add_to_waiting_list(user_id)
        add_to_waiting_list(partner_id)
        # Пытаемся найти нового партнера
        find_partner(user_id)
        find_partner(partner_id)


def add_to_waiting_list(user_id):
    gender = user_gender.get(user_id)
    if gender:
        waiting_users[gender].append(user_id)


@bot.message_handler(func=lambda message: True)
def relay_message(message):
    user_id = message.chat.id
    if user_id in active_chats:
        partner_id = active_chats[user_id]
        bot.send_message(partner_id, message.text)


if __name__ == '__main__':
    bot.polling()