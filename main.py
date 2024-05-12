import csv
import time

import aiohttp
import asyncio
import random
import requests

from bs4 import BeautifulSoup

URL = 'https://work24.ru/orders'

with open('proxies.txt') as file:
    PROXIES_LIST = file.read().splitlines()


# async def get_html(url, proxy=None) -> str:
#     async with aiohttp.ClientSession() as session:
#         try:
#             async with session.get(url) as response:
#                 print(response.status)
#                 return await response.text(encoding='utf-8')
#         except Exception as e:
#             print(e)


def get_html(url):
    return requests.get(url).text


def parse_data(html):
    soup = BeautifulSoup(html, 'lxml')
    items = soup.find_all('div', class_='order-item')
    for item in items:
        item_name = item.find('div', class_='order-item__title').text.strip()
        item_customer = item.find('div', class_='user-link').text.strip()
        item_created = item.find('div', class_='time-span__item_started').text.strip()
        item_deadline = (
                item.find('div', class_='date time-span__item_ok') or
                item.find('div', class_='date time-span__item_short') or
                item.find('div', class_='date time-span__item_overdue') or
                item.find('div', class_='date time-span__item_finished time-span__item_overdue') or
                item.find('div', class_='date time-span__item_finished time-span__item_ok')
        ).text.strip()
        item_category = [category.text.strip() for category in item.find_all('li', class_='essential__item')[-2:]]
        print('*' * 50)
        print(f'Заказчик: {item_customer}')
        print(f'Заказ: {item_name}')
        print(f'Дата загрузки / Срок сдачи: {item_created} / {item_deadline}')
        print(f'Категория: {item_category[0]} / {item_category[1]}')
        cols = (item_customer, item_name, f'{item_created} / {item_deadline}', item_category[0], item_category[1])
        write_to_csv(cols)


def check_proxies(proxy_list):
    attempts = 0
    while True:
        proxy = random.choice(proxy_list)
        try:
            response = requests.get(URL, proxies={'http': proxy})
        except aiohttp.client_exceptions.ClientConnectorError:
            attempts += 1
            continue
        else:
            if response.status_code == 200:
                return proxy
        if attempts == 10:
            raise ConnectionError('Bad Proxies')


def create_csv():
    with open('orders.csv', 'w') as file:
        writer = csv.writer(file)
        writer.writerow(['Заказчик', 'Заказ', 'Дата загрузки / Срок сдачи', 'Категория', 'Подкатегория'])


def write_to_csv(data):
    with open('orders.csv', 'a') as file:
        writer = csv.writer(file)
        print(data)
        writer.writerow(data)


def main():
    create_csv()
    html = get_html(URL)
    soup = BeautifulSoup(html, 'lxml')
    pages_count = soup.find_all('button', class_='pagination__number')[-1].text.strip()
    print(pages_count)
    start = time.time()
    for page in range(1, int(pages_count) + 1):
        print(f'Страница №{page}')
        html = get_html(URL + f'?page={page}')
        parse_data(html)
    print('Парсинг завершён!')
    print(f'{int(time.time() - start)}сек.')


if __name__ == '__main__':
    main()
