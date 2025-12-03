import telebot
import requests
import re
from bs4 import BeautifulSoup
import csv
import io

# Замените эти значения на свои реальные ключи
BOT_TOKEN = '8421270114:AAGWIyRCWX_ncdlhVs_B45HpNLwKyjcAyoQ'  # Получите у @BotFather
API_KEY = 'AIzaSyDHRToDzcO1q-5HVjPeIZGmjFt7OeTV65o'  # Получите в Google Cloud Console
CX = 'e4f64baee0aa34498'  # Создайте в Programmable Search Engine

bot = telebot.TeleBot(BOT_TOKEN)


def extract_contact_info(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    text = soup.get_text()

    # Регулярные выражения для поиска российских номеров
    phone_patterns = [
        r'(?:\+7|8)[\s\-\(\)]*\d{3}[\s\-\(\)]*\d{3}[\s\-\(\)]*\d{2}[\s\-\(\)]*\d{2}',
        r'(?:\+7|8)\d{10}',
        r'(?:\+7|8)\s?\(\d{3}\)\s?\d{3}[\s\-]?\d{2}[\s\-]?\d{2}',
    ]

    phones = set()

    # Поиск по шаблонам
    for pattern in phone_patterns:
        found_numbers = re.findall(pattern, text)
        for number in found_numbers:
            clean_number = re.sub(r'[^\d+]', '', number)
            if clean_number.startswith('8'):
                clean_number = '+7' + clean_number[1:]
            phones.add(clean_number)

    # Поиск номеров в ссылках tel:
    tel_links = soup.find_all(href=re.compile(r'tel:'))
    for link in tel_links:
        tel_number = link.get('href', '').replace('tel:', '').strip()
        if tel_number:
            clean_number = re.sub(r'[^\d+]', '', tel_number)
            if clean_number.startswith('8'):
                clean_number = '+7' + clean_number[1:]
            phones.add(clean_number)

    # Поиск названия
    title = ''
    if soup.title and soup.title.string:
        title = soup.title.string.strip()
    else:
        h1 = soup.find('h1')
        if h1:
            title = h1.get_text().strip()

    return {
        'title': title,
        'phones': list(phones)
    }


@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Привет! Введите ваш поисковый запрос, и я отправлю вам результаты с контактами.")


@bot.message_handler(func=lambda m: True)
def search_and_reply(message):
    query = message.text

    bot.send_message(message.chat.id, "Идет поиск... Пожалуйста, подождите.")

    search_url = "https://www.googleapis.com/customsearch/v1"
    links_info = []

    # Поиск по 2 страницам
    for start_index in [1, 11]:  # start=1 и start=11 для второй страницы
        params = {
            'key': API_KEY,
            'cx': CX,
            'q': query,
            'num': 10,
            'start': start_index
        }
        try:
            response = requests.get(search_url, params=params, timeout=10)
            data = response.json()

            if 'items' in data:
                for item in data['items']:
                    link = item['link']
                    # Фильтрация ненужных сайтов
                    if not any(domain in link.lower() for domain in ['avito', 'youtube', 'vk']):
                        links_info.append(link)
        except Exception as e:
            print(f"Ошибка при поиске: {e}")
            continue

    if not links_info:
        bot.send_message(message.chat.id, "По вашему запросу ничего не найдено.")
        return

    results = []
    bot.send_message(message.chat.id, f"Найдено много сайтов. Ищу контакты...")

    for url in links_info[:40]:  # Ограничим 10 сайтами чтобы не долго
        try:
            resp = requests.get(url, timeout=10)
            if resp.status_code == 200:
                contact = extract_contact_info(resp.text)
                title = contact['title'] if contact['title'] else 'Нет названия'
                phones = contact['phones']
                phones_str = ', '.join(phones) if phones else 'Нет номера'

                if phones:  # Добавляем только если есть телефоны
                    results.append({
                        'title': title[:100],  # Обрезаем длинные названия
                        'url': url,
                        'phones': phones_str
                    })
        except Exception as e:
            print(f"Ошибка при обработке {url}: {e}")
            continue

    if not results:
        bot.send_message(message.chat.id, "Не удалось найти контакты на найденных сайтах.")
        return

    # Создаем CSV файл
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=['Название', 'Ссылка', 'Телефоны'])
    writer.writeheader()
    for item in results:
        writer.writerow({
            'Название': item['title'],
            'Ссылка': item['url'],
            'Телефоны': item['phones']
        })
    csv_data = output.getvalue()
    output.close()

    # Формируем текстовый ответ
    reply_lines = []
    for idx, item in enumerate(results, start=1):
        reply_lines.append(f"{idx}. {item['title']}\n📞 {item['phones']}\n🔗 {item['url']}\n")

    # Разбиваем сообщение если слишком длинное
    message_text = "Найденные контакты:\n\n" + "\n".join(reply_lines)
    if len(message_text) > 4096:
        parts = [message_text[i:i + 4096] for i in range(0, len(message_text), 4096)]
        for part in parts:
            bot.send_message(message.chat.id, part)
    else:
        bot.send_message(message.chat.id, message_text)

    # Отправляем CSV файл
    csv_bytes = io.BytesIO()
    csv_bytes.write(csv_data.encode('utf-8'))
    csv_bytes.seek(0)
    bot.send_document(message.chat.id,
                      document=csv_bytes,
                      visible_file_name='contacts.csv',
                      caption='Результаты поиска в CSV формате')


if __name__ == '__main__':
    print("Бот запущен...")
    bot.polling()