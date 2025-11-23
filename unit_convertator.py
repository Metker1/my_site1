import  requests
from bs4 import  BeautifulSoup as b
import random
import  telebot


API_KEY = '8158786514:AAHoOT9OI_ppM2IumY9AWOBoh3ZoA0JiE-o'





bot = telebot.TeleBot(API_KEY)
@bot.message_handler(commands=['start'])
def hello(message):
    bot.send_message(message.chat.id, 'Привет, напиши героя чтобы узнать его контрпик')


@bot.message_handler(content_types=['text'])
def jokes(message):
    if message.text.lower() in 'viper':
        bot.send_message('Chaos Knight. По статистике, ЦК — один из лучших контрпиков для Viper Viper')

    else:
        bot.send_message(message.chat.id, 'Введите любую цифру:')



bot.polling()