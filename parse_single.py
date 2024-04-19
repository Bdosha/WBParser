import selenium.common.exceptions
from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

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

print(len(set(cursor.execute('SELECT * FROM Tstol').fetchall())))

def get(soup, name):
    for table in soup.findAll("table", class_="product-params__table"):

        rows = table.findAll("tr")

        for row in rows:
            cells = row.findAll("th")
            for first_column in cells:
                # print(first_column.text)
                if name in first_column.text.strip():
                    return row.findAll('td')[cells.index(first_column)].text
    return "-1"


for url in cursor.execute('SELECT * from "urls"').fetchall():
    try:
        if cursor.execute(f'SELECT url FROM Tstol WHERE url = "{url[0]}"').fetchall():
            continue
        driver.get(url[0])
        try:
            WebDriverWait(driver, 2).until(
                EC.presence_of_element_located((By.LINK_TEXT, "Мебель"))
            )
        except selenium.common.exceptions.TimeoutException:
            try:
                WebDriverWait(driver, 0).until(
                    EC.presence_of_element_located((By.LINK_TEXT, "Для ремонта"))
                )
            except selenium.common.exceptions.TimeoutException:
                continue
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        try:
            color = soup.find('span', {'class': 'color'}).text
        except:
            color = 'None'

        cortage = (
            url[0],
            soup.find('h1', {'data-link': "text{:selectedNomenclature^goodsName}"}).text,
            soup.find('ins', {'class': 'price-block__final-price'}).text.replace('\xa0', '').replace(' ', '')[:-1],
            color,
            soup.find('p', {'class': 'collapsable__text'}).text.replace('\t', ' ').replace('\n', ' '),
            soup.find('span', {'id': 'productNmId'}).text,
            soup.find('span', {'data-link': 'text{: selectedNomenclature^star}'}).text,
            soup.find('span', {'class': 'product-review__count-review'}).text.replace(' ', '').split('о')[0],
            soup.find('span', {
                'data-link': "{include tmpl='productCardOrderCount' ^~ordersCount=selectedNomenclature^ordersCount}"}).text.replace(
                '\xa0', ''),
            get(soup, "Вес с упаковкой").split()[0],
            float(get(soup, "Ширина упаковки").split()[0].replace(',', '.'))*10,
            float(get(soup, "Высота упаковки").split()[0].replace(',', '.'))*10,
            float(get(soup, "Длина упаковки").split()[0].replace(',', '.'))*10,
            get(soup, "Ширина предмета").split()[0],
            get(soup, "Высота предмета").split()[0],
            get(soup, "Глубина предмета").split()[0],
            get(soup, "Вес без упаковки").split()[0],
            color,
            get(soup, 'Количество отделений').split()[0],
            soup.find('h1', {'data-link': "text{:selectedNomenclature^goodsName}"}).text,
            get(soup, 'Материал изделия'),
            get(soup, 'Комплектация'),
            get(soup, 'Нагрузка максимальная'),
            soup.find('div', {'data-name-for-wba': 'Item_Photo'}).find('img')['src'][2:].replace('c246x328', 'big').replace('basket0.wb.ru', 'basket-10.wb.ru'),
            ', '.join([i.find('img')['src'][2:].replace('c246x328', 'big').replace('basket0.wb.ru', 'basket-10.wb.ru') for i in soup.findAll('div', {'data-name-for-wba': 'Item_Photo'})[1:]
                       if '1.jpg' not in i.find('img')['src'][2:].replace('c246x328', 'big').replace('basket0.wb.ru', 'basket-10.wb.ru')]),
            soup.find('ul', {'class': 'breadcrumbs__list'}).findAll('li')[1].text[2:-3],
            soup.find('ul', {'class': 'breadcrumbs__list'}).findAll('li')[2].text[2:-3],
            soup.find('ul', {'class': 'breadcrumbs__list'}).findAll('li')[3].text[2:-3],
            soup.find('ul', {'class': 'breadcrumbs__list'}).findAll('li')[4].text[2:-3]
        )
        print(cortage)
        cursor.execute(
            f"INSERT INTO 'Tstol' (url, name, price, color, desc, artic, mark, review, buyes, Pwg, Pw, Ph,Pl, Uw, Uh, Ul, Uwg, product_color, len_box, model_name, material, equi, max, main_photo, other_photo, cat1, cat2, cat3, cat4) VALUES{cortage}")
        con.commit()
    except ValueError:
        continue
    except IndexError:
        continue
    except AttributeError:
        continue
driver.close()
