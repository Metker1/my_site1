import telebot
from datetime import datetime, timedelta
import requests
from bs4 import BeautifulSoup
import re
import random  # Для симуляции анализа (вместо реального)

# Замените на ваш API-ключ
BOT_TOKEN = '8158786514:AAHoOT9OI_ppM2IumY9AWOBoh3ZoA0JiE-o'

bot = telebot.TeleBot(BOT_TOKEN)

# --- Функции для получения данных о матчах ---

def get_upcoming_matches(country_code='england'):
    """
    Получает информацию о предстоящих футбольных матчах с сайта.
    """
    try:
        url = f"https://www.sportytrader.com/ru/prognoz/futbol/p/{country_code}"  # Пример для Англии
        response = requests.get(url)
        response.raise_for_status()  # Проверка на ошибки HTTP

        soup = BeautifulSoup(response.content, 'html.parser')
        matches = []

        match_elements = soup.find_all('div', class_='match-item')  # Анализ HTML структуры

        for match_element in match_elements:
            try:
                date_time_str = match_element.find('span', class_='match-date-time').text.strip()
                # Парсинг даты и времени (пример обработки)
                try:
                    # Попытка распознать дату и время с учетом формата (например, "сегодня, 15:30" или "Завтра, 17:00")
                    if "Сегодня" in date_time_str or "Завтра" in date_time_str:
                        time_str = re.search(r'\d{2}:\d{2}', date_time_str).group(0)  # Извлекаем только время
                        now = datetime.now()
                        if "Завтра" in date_time_str:
                            match_date = now + timedelta(days=1)
                        else:
                            match_date = now

                        match_datetime = datetime(match_date.year, match_date.month, match_date.day, int(time_str.split(':')[0]), int(time_str.split(':')[1]))

                    else:

                        date_str = re.search(r'\d{2}\.\d{2}\.\d{4}', date_time_str).group(0)
                        time_str = re.search(r'\d{2}:\d{2}', date_time_str).group(0)
                        match_datetime = datetime.strptime(f"{date_str} {time_str}", "%d.%m.%Y %H:%M")

                except (ValueError, AttributeError) as e:
                    print(f"Ошибка при парсинге даты и времени: {e}")
                    continue  # Пропускаем этот матч, если не удалось распознать дату

                team1 = match_element.find('span', class_='team-name team1').text.strip()
                team2 = match_element.find('span', class_='team-name team2').text.strip()

                matches.append({
                    'datetime': match_datetime,
                    'team1': team1,
                    'team2': team2,
                    'country': country_code.upper() # Добавляем код страны
                })
            except Exception as e:
                print(f"Ошибка при парсинге матча: {e}")
                continue # Продолжаем, если ошибка в одном матче

        # Сортировка матчей по дате и времени
        matches.sort(key=lambda x: x['datetime'])
        return matches

    except requests.exceptions.RequestException as e:
        print(f"Ошибка при запросе к сайту: {e}")
        return None
    except Exception as e:
        print(f"Общая ошибка при получении матчей: {e}")
        return None

# --- Функции для анализа (симуляция) ---

def analyze_match(team1, team2):
    """
    Симулирует анализ матча и предсказывает победителя.  В РЕАЛЬНОМ приложении здесь должен быть более сложный анализ.
    """
    # Симуляция: случайным образом выбираем победителя
    if random.random() < 0.5:
        winner = team1
        loser = team2
    else:
        winner = team2
        loser = team1

    return winner, loser

# --- Обработчики команд бота ---

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    """
    Отправляет приветственное сообщение и инструкции.
    """
    bot.reply_to(message, "Привет! Я бот предсказатель футбольных матчей.\n\n"
                         "Доступные команды:\n"
                         "/upcoming - Показать ближайшие матчи.\n"
                         "/predict - Сделать предсказание для указанного матча (пример: /predict Manchester_United vs Liverpool).\n" # Исправлено: добавлена команда
                         "/help - Показать это сообщение.")

@bot.message_handler(commands=['upcoming'])
def show_upcoming_matches(message):
    """
    Показывает ближайшие матчи.
    """
    matches = get_upcoming_matches()

    if matches:
        if not matches:
            bot.send_message(message.chat.id, "Ближайшие матчи не найдены.")
            return

        output = "<b>Ближайшие футбольные матчи:</b>\n\n"
        for match in matches:
             try:
                output += f"<b>{match['country']}</b>\n"
                output += f"📅 Дата и время: {match['datetime'].strftime('%d.%m.%Y %H:%M')} (МСК) \n" # Форматируем дату и время
                output += f"⚽️ {match['team1']} vs {match['team2']}\n\n"

             except Exception as e:
                 print(f"Ошибка при форматировании вывода матча: {e}") #Добавили обработку ошибок
                 continue

        bot.send_message(message.chat.id, output, parse_mode='HTML')
    else:
        bot.send_message(message.chat.id, "Не удалось получить информацию о матчах.")

@bot.message_handler(commands=['predict'])
def predict_match(message):
    """
    Предсказывает результат матча, основываясь на введенных командах.
    Использует симуляцию вместо реального анализа.
    """
    try:
        # Получаем аргументы (команды) из сообщения
        args = message.text.split()[1:] # Разделяем сообщение на слова, исключая команду /predict
        if len(args) != 3 or args[1].lower() != 'vs': # Проверяем формат ввода
            bot.reply_to(message, "Неверный формат команды. Используйте: /predict Команда1 vs Команда2")
            return

        team1 = args[0].replace('_', ' ').strip() # Заменяем '_' на пробелы и удаляем лишние пробелы
        team2 = args[2].replace('_', ' ').strip()

        # Симулируем анализ
        winner, loser = analyze_match(team1, team2)

        output = f"🔮 <b>Предсказание:</b>\n"
        output += f"Победитель: <b>{winner}</b>\n"
        output += f"Проигравший: <b>{loser}</b>\n"

        bot.send_message(message.chat.id, output, parse_mode='HTML')
    except Exception as e:
        print(f"Ошибка при предсказании матча: {e}")
        bot.reply_to(message, "Произошла ошибка при предсказании матча.")


# --- Запуск бота ---
if __name__ == '__main__':
    print("Бот запущен...")
    bot.infinity_polling()