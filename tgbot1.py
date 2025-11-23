import telebot
from telebot import types
import datetime
import random
import threading
import time
import math

# ===== КОНФИГУРАЦИЯ =====
BOT_TOKEN = '8421270114:AAGWIyRCWX_ncdlhVs_B45HpNLwKyjcAyoQ'  # ЗАМЕНИТЕ НА ВАШ ТОКЕН
ADMIN_ID = 123456789  # ЗАМЕНИТЕ НА ВАШ ID

bot = telebot.TeleBot(BOT_TOKEN)

# ===== ХРАНИЛИЩЕ ДАННЫХ =====
users_data = {}
user_sessions = {}
live_bets = []
recent_wins = []
sports_events = []
tournaments_list = []


# ===== ИНИЦИАЛИЗАЦИЯ ДАННЫХ =====
def initialize_data():
    global sports_events, tournaments_list

    # Инициализация спортивных событий
    sports_events = [
        {
            'id': 1, 'sport': '⚽ Футбол', 'teams': 'ЦСКА - Спартак',
            'odds': {'1': 2.1, 'X': 3.2, '2': 2.8}, 'time': '19:00'
        },
        {
            'id': 2, 'sport': '⚽ Футбол', 'teams': 'Зенит - Динамо',
            'odds': {'1': 1.8, 'X': 3.4, '2': 4.2}, 'time': '20:30'
        },
        {
            'id': 3, 'sport': '🏀 Баскетбол', 'teams': 'Лейкерс - Селтикс',
            'odds': {'1': 1.9, '2': 1.8}, 'time': '22:00'
        },
        {
            'id': 4, 'sport': '🎾 Теннис', 'teams': 'Надаль - Джокович',
            'odds': {'1': 2.3, '2': 1.6}, 'time': '18:45'
        }
    ]

    # Инициализация турниров
    tournaments_list = [
        {
            'id': 1, 'name': 'Neon Poker Championship', 'prize': 1000000,
            'fee': 5000, 'players': '128/256', 'date': '15-17.12.2023'
        },
        {
            'id': 2, 'name': 'Слот-турнир "Золотой джекпот"', 'prize': 500000,
            'fee': 0, 'players': '不限', 'date': '10-17.12.2023'
        }
    ]


# ===== МЕНЕДЖЕР ПОЛЬЗОВАТЕЛЕЙ =====
class UserManager:
    @staticmethod
    def get_user(user_id):
        return users_data.get(user_id)

    @staticmethod
    def create_user(user_id, username):
        if user_id not in users_data:
            users_data[user_id] = {
                'user_id': user_id,
                'username': username,
                'balance': 1000,
                'registration_date': datetime.datetime.now().isoformat(),
                'last_bonus_date': None,
                'total_bets': 0,
                'total_wins': 0,
                'vip_level': 'standard',
                'total_deposited': 0,
                'total_withdrawn': 0,
                'max_win': 0
            }
        return users_data[user_id]

    @staticmethod
    def update_balance(user_id, amount):
        if user_id in users_data:
            users_data[user_id]['balance'] += amount
            if amount > 0:
                users_data[user_id]['total_deposited'] += amount
            else:
                users_data[user_id]['total_withdrawn'] += abs(amount)
            return users_data[user_id]['balance']
        return None

    @staticmethod
    def update_bonus_date(user_id):
        if user_id in users_data:
            users_data[user_id]['last_bonus_date'] = datetime.datetime.now().date().isoformat()

    @staticmethod
    def update_stats(user_id, is_win=False):
        if user_id in users_data:
            users_data[user_id]['total_bets'] += 1
            if is_win:
                users_data[user_id]['total_wins'] += 1

    @staticmethod
    def update_vip_level(user_id):
        if user_id in users_data:
            user = users_data[user_id]
            total_deposited = user['total_deposited']

            if total_deposited >= 1000000:
                user['vip_level'] = 'platinum'
            elif total_deposited >= 200000:
                user['vip_level'] = 'gold'
            elif total_deposited >= 50000:
                user['vip_level'] = 'silver'
            elif total_deposited >= 10000:
                user['vip_level'] = 'bronze'
            else:
                user['vip_level'] = 'standard'


# ===== СИМУЛЯЦИЯ ОНЛАЙН ИГРОКОВ =====
online_players = 1247


def update_online_players():
    global online_players
    while True:
        online_players += random.randint(-10, 10)
        online_players = max(1000, online_players)
        time.sleep(30)


def generate_live_activity():
    global live_bets, recent_wins
    first_names = ['Алексей', 'Мария', 'Дмитрий', 'Анна', 'Сергей', 'Ольга']
    last_names = ['Иванов', 'Петрова', 'Сидоров', 'Кузнецова', 'Смирнов']
    games = ['Слоты', 'Рулетка', 'Блэкджек', 'Покер', 'Кости']

    if random.random() < 0.3:
        bet = {
            'user': f"{random.choice(first_names)} {random.choice(last_names)[0]}.",
            'game': random.choice(games),
            'amount': random.randint(100, 10000),
            'is_win': random.random() > 0.6,
            'time': datetime.datetime.now().strftime('%H:%M')
        }
        live_bets.insert(0, bet)

        if bet['is_win']:
            win_amount = int(bet['amount'] * random.uniform(1.5, 5.0))
            win_info = {
                'user': bet['user'],
                'game': bet['game'],
                'amount': win_amount,
                'time': bet['time']
            }
            recent_wins.insert(0, win_info)

        if len(live_bets) > 10:
            live_bets.pop()
        if len(recent_wins) > 10:
            recent_wins.pop()

    threading.Timer(random.randint(5, 15), generate_live_activity).start()


# ===== ИГРОВЫЕ ФУНКЦИИ =====
class GameEngine:
    @staticmethod
    def play_slots(bet_amount, slot_type='fruit'):
        symbols = ['🍒', '🍋', '🍊', '🍇', '💎', '7️⃣']
        result = [random.choice(symbols) for _ in range(3)]

        # Определяем выигрыш
        if result[0] == result[1] == result[2]:
            if result[0] == '7️⃣':
                multiplier = 50  # Джекпот
            elif result[0] == '💎':
                multiplier = 10
            else:
                multiplier = 5
        elif result[0] == result[1] or result[1] == result[2]:
            multiplier = 2
        else:
            multiplier = 0

        win_amount = bet_amount * multiplier
        return result, win_amount, multiplier > 0

    @staticmethod
    def play_roulette(bet_type, bet_amount, number=None):
        winning_number = random.randint(0, 36)
        is_red = winning_number in [1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36]

        if bet_type == 'number' and number == winning_number:
            multiplier = 35
        elif bet_type == 'red' and is_red and winning_number != 0:
            multiplier = 2
        elif bet_type == 'black' and not is_red and winning_number != 0:
            multiplier = 2
        elif bet_type == 'even' and winning_number % 2 == 0 and winning_number != 0:
            multiplier = 2
        elif bet_type == 'odd' and winning_number % 2 == 1 and winning_number != 0:
            multiplier = 2
        elif bet_type == '1-12' and 1 <= winning_number <= 12:
            multiplier = 3
        elif bet_type == '13-24' and 13 <= winning_number <= 24:
            multiplier = 3
        elif bet_type == '25-36' and 25 <= winning_number <= 36:
            multiplier = 3
        else:
            multiplier = 0

        win_amount = bet_amount * multiplier
        return winning_number, is_red, win_amount, multiplier > 0

    @staticmethod
    def play_blackjack():
        # Упрощенный блэкджек
        player_cards = [random.randint(1, 11), random.randint(1, 10)]
        dealer_cards = [random.randint(1, 11), random.randint(1, 10)]

        player_total = sum(player_cards)
        dealer_total = sum(dealer_cards)

        # Игрок может взять еще карту
        if player_total <= 16 and random.random() > 0.5:
            player_cards.append(random.randint(1, 11))
            player_total = sum(player_cards)

        # Дилер берет карты до 17
        while dealer_total < 17:
            dealer_cards.append(random.randint(1, 11))
            dealer_total = sum(dealer_cards)

        # Определяем победителя
        if player_total > 21:
            return player_cards, dealer_cards, 'lose'
        elif dealer_total > 21:
            return player_cards, dealer_cards, 'win'
        elif player_total > dealer_total:
            return player_cards, dealer_cards, 'win'
        elif player_total < dealer_total:
            return player_cards, dealer_cards, 'lose'
        else:
            return player_cards, dealer_cards, 'push'

    @staticmethod
    def play_dice(bet_type, bet_amount):
        dice1 = random.randint(1, 6)
        dice2 = random.randint(1, 6)
        total = dice1 + dice2

        if bet_type == '7' and total == 7:
            multiplier = 4
        elif bet_type == '11' and total == 11:
            multiplier = 6
        elif bet_type == 'double' and dice1 == dice2:
            multiplier = 8
        elif bet_type == 'high' and total >= 8:
            multiplier = 2
        elif bet_type == 'low' and total <= 6:
            multiplier = 2
        else:
            multiplier = 0

        win_amount = bet_amount * multiplier
        return dice1, dice2, total, win_amount, multiplier > 0

    @staticmethod
    def trade_binary(asset, direction, bet_amount):
        # Симуляция движения цены
        price_movement = random.uniform(-2.0, 2.0)
        is_win = (direction == 'up' and price_movement > 0.5) or (direction == 'down' and price_movement < -0.5)

        if is_win:
            win_amount = int(bet_amount * 1.85)  # 85% прибыль
        else:
            win_amount = 0

        return price_movement, win_amount, is_win


# ===== КЛАВИАТУРЫ =====
def main_menu():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.row('🎮 Игры', '⚽ Ставки на спорт')
    keyboard.row('🏆 Турниры', '💎 VIP программа')
    keyboard.row('🎁 Акции и бонусы', '💬 Поддержка')
    keyboard.row('💰 Баланс', '👤 Профиль')
    return keyboard


def games_menu():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.row('🎰 Игровые автоматы', '🎲 Рулетка')
    keyboard.row('♠️ Блэкджек', '🃏 Покер')
    keyboard.row('🎯 Кости', '📊 Бинарные опционы')
    keyboard.row('🔙 Назад')
    return keyboard


def sports_menu():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.row('⚽ Футбол', '🏀 Баскетбол')
    keyboard.row('🎾 Теннис', '🏒 Хоккей')
    keyboard.row('📊 Live ставки', '🏆 Мои ставки')
    keyboard.row('🔙 Назад')
    return keyboard


# ===== ОСНОВНЫЕ КОМАНДЫ =====
@bot.message_handler(commands=['start'])
def start_command(message):
    user_id = message.from_user.id
    username = message.from_user.username or message.from_user.first_name

    UserManager.create_user(user_id, username)

    welcome_text = f"""
🎰 *Добро пожаловать в Neon Casino!* 🎰

*Игроков онлайн:* {online_players} 👥

✨ *Наши преимущества:*
• 🎮 Более 1000 азартных игр
• ⚽ Ставки на спорт с кэфом до 10.0
• 💎 VIP программа с кэшбэком до 15%
• 🎁 Щедрые бонусы новичкам
• 🔒 Быстрые и безопасные выплаты

💫 *Выберите раздел из меню ниже:*
    """

    bot.send_message(
        message.chat.id,
        welcome_text,
        reply_markup=main_menu(),
        parse_mode='Markdown'
    )


@bot.message_handler(commands=['admin'])
def admin_command(message):
    if message.from_user.id != ADMIN_ID:
        return

    total_users = len(users_data)
    total_balance = sum(user['balance'] for user in users_data.values())
    total_bets = sum(user['total_bets'] for user in users_data.values())

    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton('📊 Статистика', callback_data='admin_stats'))
    keyboard.add(types.InlineKeyboardButton('🔄 Сбросить данные', callback_data='admin_reset'))
    keyboard.add(types.InlineKeyboardButton('🎁 Выдать бонус', callback_data='admin_bonus'))

    admin_text = f"""
⚙️ *Панель администратора*

👥 *Пользователей:* {total_users}
💰 *Общий баланс:* {total_balance} ₽
🎮 *Всего ставок:* {total_bets}
🕒 *Онлайн:* {online_players}
    """

    bot.send_message(message.chat.id, admin_text,
                     reply_markup=keyboard, parse_mode='Markdown')


# ===== ОБРАБОТЧИКИ ГЛАВНОГО МЕНЮ =====
@bot.message_handler(func=lambda message: message.text == '💰 Баланс')
def show_balance(message):
    user = UserManager.get_user(message.from_user.id)
    if not user:
        UserManager.create_user(message.from_user.id, message.from_user.first_name)
        user = UserManager.get_user(message.from_user.id)

    vip_levels = {
        'standard': 'Стандартный',
        'bronze': 'Бронзовый',
        'silver': 'Серебряный',
        'gold': 'Золотой',
        'platinum': 'Платиновый'
    }

    balance_text = f"""
💳 *Ваш баланс*

💰 *Доступно:* {user['balance']} ₽
💎 *VIP статус:* {vip_levels[user['vip_level']]}
🎁 *Бонусы доступны:* {'Да' if user['last_bonus_date'] != datetime.datetime.now().date().isoformat() else 'Нет'}

*Действия:*
    """

    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton('💵 Пополнить', callback_data='deposit'))
    keyboard.add(types.InlineKeyboardButton('📤 Вывести', callback_data='withdraw'))
    keyboard.add(types.InlineKeyboardButton('🎁 Получить бонус', callback_data='daily_bonus'))
    keyboard.add(types.InlineKeyboardButton('📊 Live ставки', callback_data='live_bets'))

    bot.send_message(
        message.chat.id,
        balance_text,
        reply_markup=keyboard,
        parse_mode='Markdown'
    )


@bot.message_handler(func=lambda message: message.text == '👤 Профиль')
def show_profile(message):
    user = UserManager.get_user(message.from_user.id)
    if not user:
        UserManager.create_user(message.from_user.id, message.from_user.first_name)
        user = UserManager.get_user(message.from_user.id)

    win_rate = (user['total_wins'] / user['total_bets'] * 100) if user['total_bets'] > 0 else 0
    vip_levels = {
        'standard': '🥉 Стандартный',
        'bronze': '🥈 Бронзовый',
        'silver': '🥇 Серебряный',
        'gold': '💎 Золотой',
        'platinum': '👑 Платиновый'
    }

    profile_text = f"""
👤 *Ваш профиль*

*ID:* {user['user_id']}
*Имя:* {user['username']}
*Баланс:* {user['balance']} ₽
*Дата регистрации:* {user['registration_date'][:10]}

📊 *Статистика:*
🎮 *Сыграно игр:* {user['total_bets']}
✅ *Выиграно игр:* {user['total_wins']}
📈 *Процент побед:* {win_rate:.1f}%
💵 *Всего пополнено:* {user['total_deposited']} ₽
💰 *Макс. выигрыш:* {user.get('max_win', 0)} ₽

{vip_levels[user['vip_level']]} *VIP статус*
    """

    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton('📊 Подробная статистика', callback_data='detailed_stats'))
    keyboard.add(types.InlineKeyboardButton('🏆 Достижения', callback_data='achievements'))

    bot.send_message(
        message.chat.id,
        profile_text,
        reply_markup=keyboard,
        parse_mode='Markdown'
    )


@bot.message_handler(func=lambda message: message.text == '🎮 Игры')
def show_games(message):
    games_text = """
🎮 *Игровые разделы*

Выберите тип игры:

*🎰 Игровые автоматы* - Более 500 слотов с джекпотами
*🎲 Рулетка* - Классическая европейская рулетка  
*♠️ Блэкджек* - 21 очко против дилера
*🃏 Покер* - Техасский Холдем и Омаха
*🎯 Кости* - Простая игра с высокими кэфами
*📊 Бинарные опционы* - Торговля с доходностью до 90%
    """

    bot.send_message(
        message.chat.id,
        games_text,
        reply_markup=games_menu(),
        parse_mode='Markdown'
    )


@bot.message_handler(func=lambda message: message.text == '⚽ Ставки на спорт')
def sports_betting(message):
    sports_text = """
⚽ *Ставки на спорт*

*Текущие события:*
    """

    for event in sports_events[:3]:
        odds_text = " | ".join([f"{outcome}: {odd}" for outcome, odd in event['odds'].items()])
        sports_text += f"\n\n*{event['teams']}* ({event['time']})\n{odds_text}"

    sports_text += "\n\n*Коэффициенты обновляются в реальном времени!*"

    bot.send_message(
        message.chat.id,
        sports_text,
        reply_markup=sports_menu(),
        parse_mode='Markdown'
    )


@bot.message_handler(func=lambda message: message.text == '🏆 Турниры')
def show_tournaments(message):
    tournament_text = """
🏆 *Текущие турниры*
    """

    for tournament in tournaments_list:
        fee_text = "БЕСПЛАТНО" if tournament['fee'] == 0 else f"{tournament['fee']} ₽"
        tournament_text += f"""

*{tournament['name']}*
• Призовой фонд: {tournament['prize']:,} ₽
• Участников: {tournament['players']}
• Взнос: {fee_text}
• Дата: {tournament['date']}
"""

    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton('🎯 Записаться на покер', callback_data='tournament_poker'))
    keyboard.add(types.InlineKeyboardButton('🎰 Участвовать в слотах', callback_data='tournament_slots'))
    keyboard.add(types.InlineKeyboardButton('📋 Правила турниров', callback_data='tournament_rules'))

    bot.send_message(
        message.chat.id,
        tournament_text,
        reply_markup=keyboard,
        parse_mode='Markdown'
    )


@bot.message_handler(func=lambda message: message.text == '💎 VIP программа')
def vip_program(message):
    user = UserManager.get_user(message.from_user.id)
    if not user:
        user = UserManager.create_user(message.from_user.id, message.from_user.first_name)

    next_level_amount = {
        'standard': 10000,
        'bronze': 50000,
        'silver': 200000,
        'gold': 1000000
    }

    current_level = user['vip_level']
    needed = next_level_amount.get(current_level, 0) - user['total_deposited']

    vip_text = f"""
💎 *VIP программа*

*Ваш статус:* {current_level.title()}
*До следующего уровня:* {max(0, needed)} ₽

*Уровни и преимущества:*

*🥉 Бронзовый* (от 10,000 ₽ депозита)
• Кэшбэк 5% еженедельно
• Персональный менеджер

*🥈 Серебряный* (от 50,000 ₽ депозита)  
• Кэшбэк 7% + все предыдущие бонусы
• Ускоренный вывод средств

*🥇 Золотой* (от 200,000 ₽ депозита)
• Кэшбэк 10% + эксклюзивные промо
• Приглашения на живые события

*💎 Платиновый* (от 1,000,000 ₽ депозита)
• Кэшбэк 15% + индивидуальные условия
• Подарки и специальные предложения
    """

    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton('📊 Мой прогресс', callback_data='vip_progress'))
    keyboard.add(types.InlineKeyboardButton('🎁 VIP бонусы', callback_data='vip_bonuses'))
    keyboard.add(types.InlineKeyboardButton('💬 VIP поддержка', callback_data='vip_support'))

    bot.send_message(
        message.chat.id,
        vip_text,
        reply_markup=keyboard,
        parse_mode='Markdown'
    )


@bot.message_handler(func=lambda message: message.text == '🎁 Акции и бонусы')
def promotions(message):
    promo_text = """
🎁 *Акции и бонусы*

*🔥 Горячие предложения:*

*🎉 Приветственный бонус*
• +500% к первому депозиту
• Максимум 50,000 ₽

*💫 Ежедневный бонус*
• До 1,000 ₽ каждый день
• Минимальный депозит 100 ₽

*↩️ Кэшбэк 10%*
• Каждую неделю
• От проигрышей за 7 дней

*🏆 Турнирные события*
• Призовые фонды до 1,000,000 ₽
• Бесплатное участие
    """

    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton('🎁 Получить бонус', callback_data='get_bonus'))
    keyboard.add(types.InlineKeyboardButton('📅 Ежедневный бонус', callback_data='daily_bonus'))
    keyboard.add(types.InlineKeyboardButton('↩️ Кэшбэк', callback_data='cashback'))
    keyboard.add(types.InlineKeyboardButton('📋 Условия акций', callback_data='promo_terms'))

    bot.send_message(
        message.chat.id,
        promo_text,
        reply_markup=keyboard,
        parse_mode='Markdown'
    )


@bot.message_handler(func=lambda message: message.text == '💬 Поддержка')
def support(message):
    support_text = """
💬 *Служба поддержки*

*🕒 Работаем 24/7*
*⚡ Среднее время ответа: 2 минуты*

*📞 Контакты:*
• Чат-бот: @NeonCasinoSupportBot
• Email: support@neon-casino.ru
• Telegram: @NeonCasinoManager

*❓ Частые вопросы:*
• Как пополнить счет?
• Как вывести средства?  
• Какие документы нужны для верификации?
• Как участвовать в турнирах?
    """

    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton('💳 Пополнение/Вывод', callback_data='support_payments'))
    keyboard.add(types.InlineKeyboardButton('🎮 Технические вопросы', callback_data='support_technical'))
    keyboard.add(types.InlineKeyboardButton('📋 Правила и условия', callback_data='support_rules'))
    keyboard.add(types.InlineKeyboardButton('👤 Верификация', callback_data='support_verification'))
    keyboard.add(types.InlineKeyboardButton('💬 Написать оператору', url='https://t.me/NeonCasinoManager'))

    bot.send_message(
        message.chat.id,
        support_text,
        reply_markup=keyboard,
        parse_mode='Markdown'
    )


@bot.message_handler(func=lambda message: message.text == '🔙 Назад')
def back_to_main(message):
    bot.send_message(
        message.chat.id,
        "🔙 Возвращаемся в главное меню",
        reply_markup=main_menu()
    )


# ===== ИГРОВЫЕ ОБРАБОТЧИКИ =====
@bot.message_handler(func=lambda message: message.text == '🎰 Игровые автоматы')
def slots_game(message):
    slots_text = """
🎰 *Игровые автоматы*

Выберите слот для игры:

*🍒 Fruit Party* - RTP 96.5%, Джекпот 5000x
*💰 Mega Moolah* - Прогрессивный джекпот
*🐲 Dragon's Myth* - Бонусные вращения

*💰 Минимальная ставка:* 100 ₽
    """

    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton('🍒 Fruit Party (100₽)', callback_data='slots_fruit'))
    keyboard.add(types.InlineKeyboardButton('💰 Mega Moolah (500₽)', callback_data='slots_mega'))
    keyboard.add(types.InlineKeyboardButton('🐲 Dragon Myth (200₽)', callback_data='slots_dragon'))
    keyboard.add(types.InlineKeyboardButton('🔙 Назад к играм', callback_data='back_games'))

    bot.send_message(
        message.chat.id,
        slots_text,
        reply_markup=keyboard,
        parse_mode='Markdown'
    )


@bot.message_handler(func=lambda message: message.text == '🎲 Рулетка')
def roulette_game(message):
    roulette_text = """
🎲 *Рулетка*

*Ставки:*
🔴 *Красное* (x2) - выигрыш если выпадет красное число
⚫ *Черное* (x2) - выигрыш если выпадет черное число
🟢 *Зеленое* (x14) - выигрыш если выпадет 0
🔢 *Число* (x35) - выигрыш если угадаете число

*Минимальная ставка:* 100 ₽
    """

    keyboard = types.InlineKeyboardMarkup()
    keyboard.row(
        types.InlineKeyboardButton('🔴 Красное', callback_data='roulette_red'),
        types.InlineKeyboardButton('⚫ Черное', callback_data='roulette_black')
    )
    keyboard.row(
        types.InlineKeyboardButton('🟢 Зеленое', callback_data='roulette_green'),
        types.InlineKeyboardButton('🔢 Число', callback_data='roulette_number')
    )
    keyboard.add(types.InlineKeyboardButton('🔙 Назад к играм', callback_data='back_games'))

    bot.send_message(
        message.chat.id,
        roulette_text,
        reply_markup=keyboard,
        parse_mode='Markdown'
    )


@bot.message_handler(func=lambda message: message.text == '♠️ Блэкджек')
def blackjack_game(message):
    blackjack_text = """
♠️ *Блэкджек*

*Правила:*
• Цель - набрать больше очков чем дилер, но не более 21
• Карты 2-10 = номиналу, J/Q/K = 10, A = 1 или 11
• Blackjack (21 с двумя картами) = x2.5

*Минимальная ставка:* 100 ₽
    """

    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton('🎯 Начать игру (100₽)', callback_data='blackjack_start'))
    keyboard.add(types.InlineKeyboardButton('📖 Правила', callback_data='blackjack_rules'))
    keyboard.add(types.InlineKeyboardButton('🔙 Назад к играм', callback_data='back_games'))

    bot.send_message(
        message.chat.id,
        blackjack_text,
        reply_markup=keyboard,
        parse_mode='Markdown'
    )


@bot.message_handler(func=lambda message: message.text == '🎯 Кости')
def dice_game(message):
    dice_text = """
🎯 *Игра в кости*

*Варианты ставок:*
• *7* (x4) - выпадет 7
• *11* (x6) - выпадет 11  
• *Дубль* (x8) - одинаковые числа на обоих костях
• *Больше* (x2) - сумма от 8 до 12
• *Меньше* (x2) - сумма от 2 до 6

*Минимальная ставка:* 100 ₽
    """

    keyboard = types.InlineKeyboardMarkup()
    keyboard.row(
        types.InlineKeyboardButton('7 (x4)', callback_data='dice_7'),
        types.InlineKeyboardButton('11 (x6)', callback_data='dice_11')
    )
    keyboard.row(
        types.InlineKeyboardButton('Дубль (x8)', callback_data='dice_double'),
        types.InlineKeyboardButton('Больше (x2)', callback_data='dice_high')
    )
    keyboard.add(types.InlineKeyboardButton('Меньше (x2)', callback_data='dice_low'))
    keyboard.add(types.InlineKeyboardButton('🔙 Назад к играм', callback_data='back_games'))

    bot.send_message(
        message.chat.id,
        dice_text,
        reply_markup=keyboard,
        parse_mode='Markdown'
    )


@bot.message_handler(func=lambda message: message.text == '📊 Бинарные опционы')
def binary_options(message):
    binary_text = """
📊 *Бинарные опционы*

*Что такое бинарные опционы?*
Простой финансовый инструмент - предскажите направление цены актива.

*📈 ВВЕРХ* - цена вырастет (x1.85)
*📉 ВНИЗ* - цена упадет (x1.85)

*Доходность:* 85%
*Экспирация:* 5 минут
*Минимальная ставка:* 100 ₽
    """

    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton('📈 Начать торговлю', callback_data='binary_start'))
    keyboard.add(types.InlineKeyboardButton('📚 Обучение', callback_data='binary_learn'))
    keyboard.add(types.InlineKeyboardButton('🔙 Назад к играм', callback_data='back_games'))

    bot.send_message(
        message.chat.id,
        binary_text,
        reply_markup=keyboard,
        parse_mode='Markdown'
    )


# ===== СПОРТИВНЫЕ СТАВКИ =====
@bot.message_handler(func=lambda message: message.text in ['⚽ Футбол', '🏀 Баскетбол', '🎾 Теннис', '🏒 Хоккей'])
def show_sport_events(message):
    sport_emoji = message.text.split(' ')[0]
    sport_name = {
        '⚽': 'Футбол',
        '🏀': 'Баскетбол',
        '🎾': 'Теннис',
        '🏒': 'Хоккей'
    }.get(sport_emoji, 'Спорт')

    events = [e for e in sports_events if e['sport'] == message.text]

    if not events:
        bot.send_message(message.chat.id, f"*{sport_name}*\n\nНа данный момент нет активных событий.",
                         parse_mode='Markdown')
        return

    events_text = f"*{sport_name} - Активные события:*\n\n"

    for event in events:
        odds_text = " | ".join([f"{outcome}: {odd}" for outcome, odd in event['odds'].items()])
        events_text += f"*{event['teams']}* ({event['time']})\n{odds_text}\n\n"

    keyboard = types.InlineKeyboardMarkup()
    for event in events[:3]:
        keyboard.add(types.InlineKeyboardButton(f"📊 {event['teams']}", callback_data=f"sport_event_{event['id']}"))
    keyboard.add(types.InlineKeyboardButton('🔙 Назад', callback_data='back_sports'))

    bot.send_message(
        message.chat.id,
        events_text,
        reply_markup=keyboard,
        parse_mode='Markdown'
    )


@bot.message_handler(func=lambda message: message.text == '📊 Live ставки')
def show_live_bets(message):
    if not live_bets:
        bot.send_message(message.chat.id, "Пока нет активных ставок. Будьте первым!")
        return

    bets_text = "🎯 *Последние ставки игроков*\n\n"

    for i, bet in enumerate(live_bets[:5]):
        result = "✅ +" if bet['is_win'] else "❌"
        bets_text += f"{bet['user']} - {bet['game']} - {bet['amount']} ₽ {result}\n"

    if recent_wins:
        wins_text = "\n🎉 *Крупные выигрыши*\n\n"
        for i, win in enumerate(recent_wins[:3]):
            wins_text += f"{win['user']} - {win['game']} - {win['amount']} ₽ 🎊\n"
        bets_text += wins_text

    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton('🔄 Обновить', callback_data='live_bets'))
    keyboard.add(types.InlineKeyboardButton('🔙 Назад', callback_data='back_sports'))

    bot.send_message(
        message.chat.id,
        bets_text,
        reply_markup=keyboard,
        parse_mode='Markdown'
    )


# ===== ОБРАБОТЧИКИ INLINE КНОПОК =====
@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    user_id = call.from_user.id
    user = UserManager.get_user(user_id)

    if not user:
        UserManager.create_user(user_id, call.from_user.first_name)
        user = UserManager.get_user(user_id)

    # === БАЛАНС И ФИНАНСЫ ===
    if call.data == 'deposit':
        deposit_text = """
💵 *Пополнение счета*

*Доступные методы:*
• 💳 Банковские карты (Visa/MasterCard/Мир)
• 📱 Электронные кошельки (Qiwi, YooMoney)
• ₿ Криптовалюты (BTC, ETH, USDT)

*Минимальная сумма:* 100 ₽
*Зачисление:* Мгновенно

Для тестирования используйте команду:
`/deposit [сумма]`
        """

        bot.edit_message_text(
            deposit_text,
            call.message.chat.id,
            call.message.message_id,
            parse_mode='Markdown'
        )

    elif call.data == 'withdraw':
        withdraw_text = f"""
📤 *Вывод средств*

*Текущий баланс:* {user['balance']} ₽

*Условия вывода:*
• Минимальная сумма: 500 ₽
• Срок обработки: 1-24 часа
• Комиссия: 0%

Для тестирования используйте команду:
`/withdraw [сумма]`
        """

        keyboard = types.InlineKeyboardMarkup()
        if user['balance'] >= 500:
            keyboard.add(types.InlineKeyboardButton('💳 Вывести 500₽', callback_data='withdraw_500'))
        keyboard.add(types.InlineKeyboardButton('🔙 Назад', callback_data='back_balance'))

        bot.edit_message_text(
            withdraw_text,
            call.message.chat.id,
            call.message.message_id,
            reply_markup=keyboard,
            parse_mode='Markdown'
        )

    elif call.data == 'daily_bonus':
        today = datetime.datetime.now().date().isoformat()

        if user['last_bonus_date'] == today:
            bonus_text = "❌ Вы уже получали ежедневный бонус сегодня. Возвращайтесь завтра!"
        else:
            bonus_multipliers = {
                'standard': 1, 'bronze': 1.2, 'silver': 1.5, 'gold': 2, 'platinum': 3
            }

            base_bonus = random.randint(50, 200)
            bonus_amount = int(base_bonus * bonus_multipliers[user['vip_level']])

            UserManager.update_balance(user_id, bonus_amount)
            UserManager.update_bonus_date(user_id)

            bonus_text = f"""
🎁 *Ежедневный бонус получен!*

+ {bonus_amount} ₽ на ваш счет
💎 *VIP множитель:* x{bonus_multipliers[user['vip_level']]}

💰 *Текущий баланс:* {user['balance'] + bonus_amount} ₽

Следующий бонус через 24 часа!
            """

        bot.edit_message_text(
            bonus_text,
            call.message.chat.id,
            call.message.message_id,
            parse_mode='Markdown'
        )

    # === ИГРОВЫЕ АВТОМАТЫ ===
    elif call.data.startswith('slots_'):
        slot_type = call.data.replace('slots_', '')
        bet_amounts = {'fruit': 100, 'mega': 500, 'dragon': 200}
        bet_amount = bet_amounts.get(slot_type, 100)

        if user['balance'] < bet_amount:
            bot.answer_callback_query(call.id, f"❌ Недостаточно средств! Нужно {bet_amount} ₽")
            return

        UserManager.update_balance(user_id, -bet_amount)
        UserManager.update_stats(user_id)

        result, win_amount, is_win = GameEngine.play_slots(bet_amount, slot_type)

        if is_win:
            UserManager.update_balance(user_id, win_amount)
            UserManager.update_stats(user_id, is_win=True)
            if win_amount > user.get('max_win', 0):
                user['max_win'] = win_amount

            result_text = f"""
🎰 *Результат:*

| {result[0]} | {result[1]} | {result[2]} |

🎉 *ВЫИГРЫШ!* +{win_amount} ₽
            """
        else:
            result_text = f"""
🎰 *Результат:*

| {result[0]} | {result[1]} | {result[2]} |

😔 *Попробуйте еще раз!*
            """

        result_text += f"\n💰 *Баланс:* {user['balance'] - bet_amount + (win_amount if is_win else 0)} ₽"

        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton('🎰 Крутить еще', callback_data=call.data))
        keyboard.add(types.InlineKeyboardButton('🔙 К слотам', callback_data='back_slots'))

        bot.edit_message_text(
            result_text,
            call.message.chat.id,
            call.message.message_id,
            reply_markup=keyboard,
            parse_mode='Markdown'
        )

    # === РУЛЕТКА ===
    elif call.data.startswith('roulette_'):
        bet_type = call.data.replace('roulette_', '')
        bet_amount = 100

        if user['balance'] < bet_amount:
            bot.answer_callback_query(call.id, f"❌ Недостаточно средств! Нужно {bet_amount} ₽")
            return

        UserManager.update_balance(user_id, -bet_amount)
        UserManager.update_stats(user_id)

        if bet_type == 'number':
            number = random.randint(1, 36)
        else:
            number = None

        winning_number, is_red, win_amount, is_win = GameEngine.play_roulette(bet_type, bet_amount, number)

        if is_win:
            UserManager.update_balance(user_id, win_amount)
            UserManager.update_stats(user_id, is_win=True)
            result_text = f"🎉 *ВЫИГРЫШ!* +{win_amount} ₽"
        else:
            result_text = "😔 *Проигрыш*"

        color = "🔴" if is_red else "⚫" if winning_number != 0 else "🟢"

        roulette_result = f"""
🎲 *Рулетка - Результат:*

Выпало: {winning_number} {color}
Ставка: {bet_type}
{result_text}

💰 *Баланс:* {user['balance'] - bet_amount + (win_amount if is_win else 0)} ₽
        """

        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton('🎲 Крутить еще', callback_data='roulette_again'))
        keyboard.add(types.InlineKeyboardButton('🔙 К рулетке', callback_data='back_roulette'))

        bot.edit_message_text(
            roulette_result,
            call.message.chat.id,
            call.message.message_id,
            reply_markup=keyboard,
            parse_mode='Markdown'
        )

    # === КОСТИ ===
    elif call.data.startswith('dice_'):
        bet_type = call.data.replace('dice_', '')
        bet_amount = 100

        if user['balance'] < bet_amount:
            bot.answer_callback_query(call.id, f"❌ Недостаточно средств! Нужно {bet_amount} ₽")
            return

        UserManager.update_balance(user_id, -bet_amount)
        UserManager.update_stats(user_id)

        dice1, dice2, total, win_amount, is_win = GameEngine.play_dice(bet_type, bet_amount)

        if is_win:
            UserManager.update_balance(user_id, win_amount)
            UserManager.update_stats(user_id, is_win=True)
            result_text = f"🎉 *ВЫИГРЫШ!* +{win_amount} ₽"
        else:
            result_text = "😔 *Проигрыш*"

        dice_result = f"""
🎯 *Кости - Результат:*

🎲 {dice1} + {dice2} = {total}
Ставка: {bet_type}
{result_text}

💰 *Баланс:* {user['balance'] - bet_amount + (win_amount if is_win else 0)} ₽
        """

        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton('🎯 Бросить еще', callback_data='dice_again'))
        keyboard.add(types.InlineKeyboardButton('🔙 К костям', callback_data='back_dice'))

        bot.edit_message_text(
            dice_result,
            call.message.chat.id,
            call.message.message_id,
            reply_markup=keyboard,
            parse_mode='Markdown'
        )

    # === БЛЭКДЖЕК ===
    elif call.data == 'blackjack_start':
        bet_amount = 100

        if user['balance'] < bet_amount:
            bot.answer_callback_query(call.id, f"❌ Недостаточно средств! Нужно {bet_amount} ₽")
            return

        UserManager.update_balance(user_id, -bet_amount)
        UserManager.update_stats(user_id)

        player_cards, dealer_cards, result = GameEngine.play_blackjack()

        player_total = sum(player_cards)
        dealer_total = sum(dealer_cards)

        if result == 'win':
            win_amount = bet_amount * 2
            UserManager.update_balance(user_id, win_amount)
            UserManager.update_stats(user_id, is_win=True)
            result_text = f"🎉 *ВЫ ВЫИГРАЛИ!* +{win_amount} ₽"
        elif result == 'push':
            win_amount = bet_amount
            UserManager.update_balance(user_id, win_amount)
            result_text = "🤝 *Ничья!* Ставка возвращена"
        else:
            win_amount = 0
            result_text = "😔 *Вы проиграли*"

        blackjack_result = f"""
♠️ *Блэкджек - Результат:*

*Ваши карты:* {player_cards} (сумма: {player_total})
*Карты дилера:* {dealer_cards} (сумма: {dealer_total})

{result_text}

💰 *Баланс:* {user['balance'] - bet_amount + win_amount} ₽
        """

        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton('♠️ Играть еще', callback_data='blackjack_start'))
        keyboard.add(types.InlineKeyboardButton('🔙 К играм', callback_data='back_games'))

        bot.edit_message_text(
            blackjack_result,
            call.message.chat.id,
            call.message.message_id,
            reply_markup=keyboard,
            parse_mode='Markdown'
        )

    # === БИНАРНЫЕ ОПЦИОНЫ ===
    elif call.data == 'binary_start':
        binary_trade_text = """
📊 *Торговля бинарными опционами*

*Выберите актив:*
        """

        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton('💶 EUR/USD', callback_data='binary_eurusd'))
        keyboard.add(types.InlineKeyboardButton('₿ Bitcoin', callback_data='binary_btc'))
        keyboard.add(types.InlineKeyboardButton('📈 Apple', callback_data='binary_aapl'))
        keyboard.add(types.InlineKeyboardButton('🔙 Назад', callback_data='back_binary'))

        bot.edit_message_text(
            binary_trade_text,
            call.message.chat.id,
            call.message.message_id,
            reply_markup=keyboard,
            parse_mode='Markdown'
        )

    elif call.data.startswith('binary_'):
        asset = call.data.replace('binary_', '')
        asset_names = {
            'eurusd': 'EUR/USD',
            'btc': 'Bitcoin',
            'aapl': 'Apple Inc.'
        }

        trade_text = f"""
📈 *Торговля: {asset_names[asset]}*

*Текущая цена:* {random.randint(100, 10000)}
*Экспирация:* 5 минут
*Доходность:* 85%

Сделайте прогноз:
        """

        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(
            types.InlineKeyboardButton('📈 ВВЕРХ', callback_data=f'trade_{asset}_up'),
            types.InlineKeyboardButton('📉 ВНИЗ', callback_data=f'trade_{asset}_down')
        )
        keyboard.add(types.InlineKeyboardButton('🔙 Назад', callback_data='binary_start'))

        bot.edit_message_text(
            trade_text,
            call.message.chat.id,
            call.message.message_id,
            reply_markup=keyboard,
            parse_mode='Markdown'
        )

    elif call.data.startswith('trade_'):
        parts = call.data.split('_')
        asset = parts[1]
        direction = parts[2]
        bet_amount = 100

        if user['balance'] < bet_amount:
            bot.answer_callback_query(call.id, "❌ Недостаточно средств!")
            return

        UserManager.update_balance(user_id, -bet_amount)
        UserManager.update_stats(user_id)

        price_movement, win_amount, is_win = GameEngine.trade_binary(asset, direction, bet_amount)

        if is_win:
            UserManager.update_balance(user_id, win_amount)
            UserManager.update_stats(user_id, is_win=True)
            result_text = f"✅ *СДЕЛКА УСПЕШНА!* +{win_amount} ₽"
        else:
            result_text = "❌ *СДЕЛКА ПРОИГРАНА*"

        trade_result = f"""
📊 *Результат торговли:*

Направление: {direction}
Изменение цены: {price_movement:.2f}%
{result_text}

💰 *Баланс:* {user['balance'] - bet_amount + (win_amount if is_win else 0)} ₽
        """

        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton('📊 Новая сделка', callback_data='binary_start'))
        keyboard.add(types.InlineKeyboardButton('🔙 К опционам', callback_data='back_binary'))

        bot.edit_message_text(
            trade_result,
            call.message.chat.id,
            call.message.message_id,
            reply_markup=keyboard,
            parse_mode='Markdown'
        )

    # === СПОРТИВНЫЕ СТАВКИ ===
    elif call.data.startswith('sport_event_'):
        event_id = int(call.data.replace('sport_event_', ''))
        event = next((e for e in sports_events if e['id'] == event_id), None)

        if event:
            event_text = f"""
⚽ *Событие: {event['teams']}*

Время: {event['time']}

*Коэффициенты:*
"""
            for outcome, odd in event['odds'].items():
                outcome_name = {'1': 'Победа 1', '2': 'Победа 2', 'X': 'Ничья'}.get(outcome, outcome)
                event_text += f"{outcome_name}: {odd}\n"

            event_text += "\n*Выберите исход:*"

            keyboard = types.InlineKeyboardMarkup()
            for outcome in event['odds'].keys():
                outcome_name = {'1': 'П1', '2': 'П2', 'X': 'X'}.get(outcome, outcome)
                keyboard.add(types.InlineKeyboardButton(
                    f"{outcome_name} ({event['odds'][outcome]})",
                    callback_data=f'sport_bet_{event_id}_{outcome}'
                ))
            keyboard.add(types.InlineKeyboardButton('🔙 Назад', callback_data='back_sports'))

            bot.edit_message_text(
                event_text,
                call.message.chat.id,
                call.message.message_id,
                reply_markup=keyboard,
                parse_mode='Markdown'
            )

    elif call.data.startswith('sport_bet_'):
        parts = call.data.split('_')
        event_id = int(parts[2])
        outcome = parts[3]
        bet_amount = 100

        if user['balance'] < bet_amount:
            bot.answer_callback_query(call.id, "❌ Недостаточно средств!")
            return

        UserManager.update_balance(user_id, -bet_amount)
        UserManager.update_stats(user_id)

        event = next((e for e in sports_events if e['id'] == event_id), None)
        if event:
            odd = event['odds'][outcome]
            is_win = random.random() < 0.4  # 40% шанс на выигрыш

            if is_win:
                win_amount = int(bet_amount * odd)
                UserManager.update_balance(user_id, win_amount)
                UserManager.update_stats(user_id, is_win=True)
                result_text = f"🎉 *СТАВКА ВЫИГРАЛА!* +{win_amount} ₽"
            else:
                win_amount = 0
                result_text = "😔 *Ставка проиграла*"

            bet_result = f"""
⚽ *Результат ставки:*

Событие: {event['teams']}
Ставка: {outcome} ({odd})
Сумма: {bet_amount} ₽
{result_text}

💰 *Баланс:* {user['balance'] - bet_amount + win_amount} ₽
            """

            keyboard = types.InlineKeyboardMarkup()
            keyboard.add(types.InlineKeyboardButton('⚽ Новая ставка', callback_data='back_sports'))
            keyboard.add(types.InlineKeyboardButton('🔙 В меню', callback_data='back_main'))

            bot.edit_message_text(
                bet_result,
                call.message.chat.id,
                call.message.message_id,
                reply_markup=keyboard,
                parse_mode='Markdown'
            )

    # === ТУРНИРЫ ===
    elif call.data == 'tournament_poker':
        tournament = tournaments_list[0]

        if user['balance'] < tournament['fee']:
            bot.answer_callback_query(call.id, f"❌ Недостаточно средств! Нужно {tournament['fee']} ₽")
            return

        UserManager.update_balance(user_id, -tournament['fee'])
        UserManager.update_vip_level(user_id)

        confirm_text = f"""
✅ *Вы успешно записались на турнир!*

🎯 *{tournament['name']}*
💰 *Взнос:* {tournament['fee']} ₽
📅 *Дата:* {tournament['date']}
🎫 *Номер участника:* {random.randint(1000, 9999)}

*Оставшийся баланс:* {user['balance'] - tournament['fee']} ₽

Удачи за игровым столом! 🃏
        """

        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton('🏆 Другие турниры', callback_data='back_tournaments'))

        bot.edit_message_text(
            confirm_text,
            call.message.chat.id,
            call.message.message_id,
            reply_markup=keyboard,
            parse_mode='Markdown'
        )

    # === АДМИН ПАНЕЛЬ ===
    elif call.data == 'admin_stats':
        if call.from_user.id != ADMIN_ID:
            return

        total_users = len(users_data)
        total_balance = sum(user['balance'] for user in users_data.values())
        total_bets = sum(user['total_bets'] for user in users_data.values())
        total_deposits = sum(user['total_deposited'] for user in users_data.values())

        stats_text = f"""
📊 *Статистика бота*

👥 *Пользователей:* {total_users}
💰 *Общий баланс:* {total_balance} ₽
🎮 *Всего ставок:* {total_bets}
💳 *Всего пополнений:* {total_deposits} ₽
🕒 *Онлайн:* {online_players}
        """

        bot.edit_message_text(
            stats_text,
            call.message.chat.id,
            call.message.message_id,
            parse_mode='Markdown'
        )

    elif call.data == 'admin_reset':
        if call.from_user.id != ADMIN_ID:
            return

        users_data.clear()
        live_bets.clear()
        recent_wins.clear()
        initialize_data()

        bot.edit_message_text(
            "✅ Все данные сброшены!",
            call.message.chat.id,
            call.message.message_id
        )

    # === НАВИГАЦИЯ ===
    elif call.data == 'back_games':
        show_games(call.message)

    elif call.data == 'back_sports':
        sports_betting(call.message)

    elif call.data == 'back_tournaments':
        show_tournaments(call.message)

    elif call.data == 'back_balance':
        show_balance(call.message)

    elif call.data == 'back_main':
        start_command(call.message)

    elif call.data == 'back_slots':
        slots_game(call.message)

    elif call.data == 'back_roulette':
        roulette_game(call.message)

    elif call.data == 'back_dice':
        dice_game(call.message)

    elif call.data == 'back_binary':
        binary_options(call.message)

    elif call.data in ['roulette_again', 'dice_again']:
        game_type = call.data.replace('_again', '')
        if game_type == 'roulette':
            roulette_game(call.message)
        else:
            dice_game(call.message)


# ===== КОМАНДЫ ДЛЯ ТЕСТИРОВАНИЯ =====
@bot.message_handler(commands=['deposit'])
def deposit_command(message):
    try:
        amount = int(message.text.split()[1])
        user_id = message.from_user.id
        UserManager.update_balance(user_id, amount)

        user = UserManager.get_user(user_id)
        bot.reply_to(message, f"✅ Баланс пополнен на {amount} ₽\n💰 Текущий баланс: {user['balance']} ₽")
    except:
        bot.reply_to(message, "❌ Использование: /deposit [сумма]")


@bot.message_handler(commands=['withdraw'])
def withdraw_command(message):
    try:
        amount = int(message.text.split()[1])
        user_id = message.from_user.id
        user = UserManager.get_user(user_id)

        if user['balance'] < amount:
            bot.reply_to(message, "❌ Недостаточно средств!")
            return

        UserManager.update_balance(user_id, -amount)
        bot.reply_to(message, f"✅ Выведено {amount} ₽\n💰 Текущий баланс: {user['balance'] - amount} ₽")
    except:
        bot.reply_to(message, "❌ Использование: /withdraw [сумма]")


@bot.message_handler(commands=['balance'])
def balance_command(message):
    user_id = message.from_user.id
    user = UserManager.get_user(user_id)
    if user:
        bot.reply_to(message, f"💰 Ваш баланс: {user['balance']} ₽")
    else:
        bot.reply_to(message, "❌ Пользователь не найден. Используйте /start")


# ===== ЗАПУСК БОТА =====
if __name__ == '__main__':
    print("🎰 Инициализация Neon Casino Bot...")
    initialize_data()
    print("✅ Данные инициализированы")

    # Запуск фоновых процессов
    threading.Thread(target=update_online_players, daemon=True).start()
    threading.Timer(5, generate_live_activity).start()

    print("🔄 Запуск фоновых процессов...")
    print("🚀 Бот запущен!")

    try:
        bot.infinity_polling()
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        print("🔄 Перезапуск через 5 секунд...")
        time.sleep(5)