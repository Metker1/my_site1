import requests
from bs4 import BeautifulSoup as b
import random
import telebot

url = 'https://pogoda.mail.ru/prognoz/toliatti/24hours/'
API_KEY = '8158786514:AAHoOT9OI_ppM2IumY9AWOBoh3ZoA0JiE-o'


def parser(url):
    r = requests.get(url)
    soup = b(r.text, 'html.parser')
    anekdots = soup.find_all('div', class_='p-forecast__current')
    return [c.text for c in anekdots]


list_of_jokes = parser(url)
random.shuffle(list_of_jokes)
bot = telebot.TeleBot(API_KEY)


@bot.message_handler(commands=['start'])
def hello(message):
    bot.send_message(message.chat.id, 'Чтобы узнать прогноз погоды нажмите 1:')


@bot.message_handler(content_types=['text'])
def jokes(message):
    if message.text.lower() in '123456789':
        bot.send_message(message.chat.id, list_of_jokes[0])

    else:
        bot.send_message(message.chat.id, 'Введите любую цифру:')


bot.polling()