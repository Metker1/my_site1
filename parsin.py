import telebot
import requests
import re
from bs4 import BeautifulSoup
import csv
import io

BOT_TOKEN = '8421270114:AAGWIyRCWX_ncdlhVs_B45HpNLwKyjcAyoQ'
API_KEY = 'AIzaSyDHRToDzcO1q-5HVjPeIZGmjFt7OeTV65o'
CX = 'e4f64baee0aa34498'

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
                # Заменяем 8 на +7
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

    # Поиск названия (title или h1)
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

    bot.send_message(message.chat.id, "Обработка данных, пожалуйста, подождите...")

    search_url = "https://www.googleapis.com/customsearch/v1"
    links_info = []

    # Поиск по 1 странице (можно увеличить по необходимости)
    for start_index in [1,2]:
        params = {
            'key': API_KEY,
            'cx': CX,
            'q': query,
            'num': 10,
            'start': start_index
        }
        try:
            response = requests.get(search_url, params=params)
            data = response.json()
        except:
            continue

        if 'items' in data:
            for item in data['items']:
                link = item['link']
                # Исключаем нежелательные ссылки
                if 'avito' not in link.lower() and 'youtube' not in link.lower() and 'vk' not in link.lower():
                    links_info.append(link)

    results = []

    for url in links_info:
        try:
            resp = requests.get(url, timeout=10)
            if resp.status_code == 200:
                contact = extract_contact_info(resp.text)
                title = contact['title'] if contact['title'] else 'Нет названия'
                phones = contact['phones']
                phones_str = ', '.join(phones) if phones else 'Нет номера'
                results.append({'title': title, 'url': url, 'phones': phones_str})
        except:
            continue

    # Создаем CSV файл в памяти
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

    # Формируем сообщение
    if results:
        reply_lines = []
        for idx, item in enumerate(results, start=1):
            reply_lines.append(f"{idx}. Название: {item['title']}\nСсылка: {item['url']}\nТелефон: {item['phones']}\n")
        reply = "Вот найденные контакты:\n" + "\n".join(reply_lines)
    else:
        reply = "Не удалось получить контакты по найденным ссылкам."

    # Отправляем сообщение
    bot.send_message(message.chat.id, reply)

    # Отправляем CSV файл
    csv_bytes = io.BytesIO()
    csv_bytes.write(csv_data.encode('utf-8'))
    csv_bytes.seek(0)
    bot.send_document(message.chat.id, ('contacts.csv', csv_bytes, 'text/csv'))

bot.polling()