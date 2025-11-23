from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time
import random

def create_driver():
    options = Options()
    # Запускаем браузер в безголовом режиме
    options.headless = True
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                         "AppleWebKit/537.36 (KHTML, like Gecko) "
                         "Chrome/115.0.0.0 Safari/537.36")
    options.add_argument("--no-sandbox")  # Не запускайте на песочнице
    options.add_argument("--disable-dev-shm-usage")  # Отключите использование dev/shm
    driver = webdriver.Chrome(options=options)
    return driver

def get_google_links(query, num_pages=1):
    driver = create_driver()
    links = []

    # Список доменов для исключения
    exclude_domains = ['google.com', 'yandex.ru', 'avito.ru', 'youtube.com']

    try:
        driver.get("https://www.google.com")
        time.sleep(random.uniform(2, 4))

        # Поиск по запросу
        search_box = driver.find_element(By.NAME, "q")
        search_box.send_keys(query)
        search_box.submit()
        time.sleep(random.uniform(2, 4))

        # Сбор ссылок
        for _ in range(num_pages):
            results = driver.find_elements(By.CSS_SELECTOR, 'a')
            for result in results:
                href = result.get_attribute('href')
                if href:
                    # Проверяем, чтобы ссылка не содержала исключаемые домены
                    if not any(domain in href for domain in exclude_domains):
                        links.append(href)

            # Переход на следующую страницу
            try:
                next_button = driver.find_element(By.ID, 'pnnext')
                next_button.click()
                time.sleep(random.uniform(2, 4))
            except Exception as e:
                print("Нет кнопки следующей страницы или ошибка:", e)
                break  # Если кнопки нет или ошибка, выходим
    finally:
        driver.quit()  # Закрываем драйвер

    return links

if __name__ == "__main__":
    query = input("Введите поисковый запрос: ")
    links = get_google_links(query, num_pages=2)
    print("Найденные ссылки:")
    for link in links:
        print(link)