from selenium import webdriver
from bs4 import BeautifulSoup

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from time import sleep
import sqlite3

con = sqlite3.connect('database.db')
cursor = con.cursor()

options = webdriver.FirefoxOptions()

options.add_argument('user-agent=Mozilla 5.0 (X11; Ubuntu)')
options.add_argument('--disable-blink-features=AutomationControlled')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
# options.add_argument('-headless')

driver = webdriver.Firefox(options=options)


def scroll_down(driver, distance, speed):
    current_position = driver.execute_script("return window.pageYOffset;")
    target_position = current_position + distance
    while current_position < target_position:
        current_position += speed
        driver.execute_script(f"window.scrollTo(0, {current_position});")
        sleep(0.01)


# вызов функции для прокрутки страницы вниз на 500 пикселей с скоростью 20 пикселей за шаг
scroll_down(driver, 500, 20)
for num in range(1, 50):
    if len(cursor.execute('SELECT url from urls').fetchall()) >= 2500:
        break

    url = f'https://www.wildberries.ru/catalog/0/search.aspx?page={num}&sort=popular&search=%D1%82%D1%83%D0%B0%D0%BB%D0%B5%D1%82%D0%BD%D1%8B%D0%B9+%D1%81%D1%82%D0%BE%D0%BB%D0%B8%D0%BA'
    driver.get(url)
    WebDriverWait(driver, 5).until(
        EC.presence_of_element_located((By.CLASS_NAME, "searching-results__title"))
    )

    scroll_down(driver, 11000, 300)
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    soup.find('div', {'class': 'j-b-recommended-goods-wrapper'}).decompose()
    temp = soup.findAll('a', class_='product-card__link j-card-link j-open-full-product-card')
    for i in temp:
        print(i['href'])
        cursor.execute(f"INSERT INTO 'urls' (url) VALUES('{i['href']}')")
        con.commit()
driver.close()
