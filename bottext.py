
import telebot
import requests
from datetime import datetime
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# API-ключ вашего бота (получите его у @BotFather в Telegram)
API_TOKEN = '8158786514:AAHoOT9OI_ppM2IumY9AWOBoh3ZoA0JiE-o'

# Создание экземпляра бота
bot = telebot.TeleBot(API_TOKEN)

# URL для получения курсов валют (используем API Центробанка России)
CURRENCY_API_URL = 'https://www.cbr-xml-daily.ru/daily_json.js'

COMMON_CURRENCIES = ['USD', 'EUR', 'GBP', 'CNY']

def get_currency_rates():
    """Получает актуальные курсы валют"""
    try:
        response = requests.get(CURRENCY_API_URL)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"Ошибка при получении курса валют: {e}")
        return None

def format_currency_message(currency_data):
    """Форматирует сообщение с курсами валют"""
    if not currency_data:
        return "Извините, не удалось получить информацию о курсах валют."

    try:
        date = datetime.strptime(currency_data['Date'], '%Y-%m-%dT%H:%M:%S%z').strftime('%d.%m.%Y %H:%M')
        rates = currency_data['Valute']

        message = f"Курсы валют на {date}:\n\n"

        for code in COMMON_CURRENCIES:
            if code in rates:
                currency = rates[code]
                message += f"🔹 {currency['Name']} ({code}): {currency['Value']} ₽ "

                # Изменение курса (рост/падение)
                change = currency['Value'] - currency['Previous']
                if change > 0:
                    message += f"🔼 (+{change:.2f})\n"
                elif change < 0:
                    message += f"🔽 ({change:.2f})\n"
                else:
                    message += "➡️ (без изменений)\n"

        return message
    except (KeyError, ValueError) as e:
        logger.error(f"Ошибка при форматировании сообщения: {e}")
        return "Извините, не удалось сформировать сообщение с курсами валют."

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "Привет! Я бот, который показывает курсы валют. Используй команду /rates, чтобы узнать актуальные курсы.")

@bot.message_handler(commands=['rates'])
def send_rates(message):
    currency_data = get_currency_rates()
    response_message = format_currency_message(currency_data)
    bot.reply_to(message, response_message)

if __name__ == '__main__':
    bot.polling(none_stop=True)
