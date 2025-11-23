import requests
from bs4 import BeautifulSoup
import re

# URL сайта
url = 'https://тольятти.натяжные-потолки24.рф/?ysclid=me2vw7erul2953800'

# Загружаем страницу
response = requests.get(url)
response.raise_for_status()

# Парсим HTML
soup = BeautifulSoup(response.text, 'html.parser')

# Предположим, что номер телефона находится в виде текста или в ссылке
# Например, в виде номера телефона в виде текста или в атрибуте href="tel:..."
# Ищем все ссылки с tel:
tel_links = soup.find_all('a', href=re.compile(r'tel:'))

if tel_links:
    for link in tel_links:
        phone_number = link['href'].replace('tel:', '').strip()
        print(f'Найден номер телефона: {phone_number}')
else:
    # Можно искать по другим признакам или искать текст, содержащий номера
    # Например, поиск по тексту, содержащему цифры и символы + - ()
    text = soup.get_text()
    phone_numbers = re.findall(r'\+?\d[\d\s\-\(\)]{7,}', text)
    if phone_numbers:
        for number in set(phone_numbers):
            print(f'Обнаружен номер: {number}')
    else:
        print('Номера телефона не найдены.')