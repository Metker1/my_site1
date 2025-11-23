from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import requests
from bs4 import BeautifulSoup
import re
import psycopg2

# Создаем функцию для получения ссылок через Selenium
def get_links_via_selenium():
    driver = webdriver.Chrome()
    driver.get('https://www.google.com/search?q=%D0%9F%D0%BE%D1%81%D1%82%D0%B0%D0%B2%D1%89%D0%B8%D0%BA%D0%B8+%D0%BA%D0%B0%D0%B1%D0%B5%D0%BB%D1%8F+%D0%B2+%D1%85%D0%BC%D0%B0%D0%BE&sca_esv=e91c7cd3479a9137&ei=EcnSaIDgINLIwPAPoe6FmAg&start=10&sa=N&sstk=Ac65TH4SGdvVJ4GIFLGFXW5C9j4TJ_R17vF6BZszK9cgYicxmFPeg1x8QnzWj7kvTqovBK0Ahe1cO6ArupDF6EjwWYrJnUNe-EPCCg&ved=2ahUKEwjArL-kpe-PAxVSJBAIHSF3AYMQ8tMDegQIChAE&biw=2560&bih=1313&dpr=1')
    time.sleep(10)
    links = driver.find_elements(By.CSS_SELECTOR, 'a')
    hrefs = [link.get_attribute('href') for link in links if link.get_attribute('href')]
    driver.quit()
    return hrefs

# Получаем список ссылок
all_links = get_links_via_selenium()

# Настройка подключения к базе данных
conn = psycopg2.connect(
    host='127.0.0.1',
    port='5432',
    dbname='metaloprocat_db',
    user='postgres',
    password='Mashinist132'
)
cursor = conn.cursor()

# Создаем таблицу, если не существует
cursor.execute('''
CREATE TABLE IF NOT EXISTS contact (
    id SERIAL PRIMARY KEY,
    name TEXT,
    url TEXT,
    phone TEXT
)
''')
conn.commit()

def extract_phone_numbers(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        phone_regex = re.compile(r'\+?\d[\d\s\-\(\)]{7,}\d')
        phone_numbers = phone_regex.findall(soup.get_text())
        cleaned_numbers = [re.sub(r'[^+\d]', '', number) for number in phone_numbers]
        return cleaned_numbers
    except requests.exceptions.RequestException as e:
        print(f"Ошибка при получении страницы {url}: {e}")
        return []
    except Exception as e:
        print(f"Ошибка при обработке страницы {url}: {e}")
        return []

def get_company_name(soup):
    title = soup.find('title')
    if title:
        return title.text.strip()
    return None

def save_to_db(name, url, phone):
    try:
        cursor.execute(
            'INSERT INTO contact (name, url, phone) VALUES (%s, %s, %s)',
            (name, url, phone)
        )
        conn.commit()
    except Exception as e:
        print(f"Ошибка при сохранении в БД: {e}")

def main():
    for url in all_links:
        # Проверяем, чтобы в ссылке не было google или youtube
        lower_url = url.lower()
        if 'google' in lower_url or 'youtube' in lower_url:
            continue  # пропускаем такие ссылки

        try:
            response = requests.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')

            company_name = get_company_name(soup)
            if not company_name:
                company_name = "Название не найдено"

            phone_numbers = extract_phone_numbers(url)

            if phone_numbers:
                for number in phone_numbers:
                    save_to_db(company_name, url, number)
            else:
                # Если телефон не найден, сохраняем без номера
                save_to_db(company_name, url, 'Телефон не найден')

            print(f"Обработан сайт: {url}")
            print(f"Кампания: {company_name}")
            print(f"Номера: {', '.join(phone_numbers) if phone_numbers else 'Не найдены'}")
            print("-" * 40)

        except requests.exceptions.RequestException as e:
            print(f"Ошибка при обработке {url}: {e}")
        except Exception as e:
            print(f"Непредвиденная ошибка при обработке {url}: {e}")

    cursor.close()
    conn.close()

if __name__ == "__main__":
    main()