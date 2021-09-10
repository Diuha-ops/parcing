import requests
from pprint import pprint
from lxml import html

"""1.	Написать приложение, которое собирает основные новости с сайта на выбор news.mail.ru,
lenta.ru, yandex-новости. Для парсинга использовать XPath. Структура данных должна содержать:
o	название источника;
o	наименование новости;
o	ссылку на новость;
o	дата публикации.
2.	Сложить собранные данные в БД
Минимум один сайт, максимум - все три
"""

import requests
from pprint import pprint
from lxml import html
from pymongo import MongoClient
from datetime import datetime
import locale
# locale.setlocale(locale.LC_TIME, '')
# locale.setlocale(locale.LC_TIME, 'ru_RU.UTF-8')
# date_format = '%d %B %Y'

client = MongoClient('127.0.0.1', 27017)
db = client['hh_vac']
current_news = db.current_news


"""Собираем данные с Lenta.ru"""

url = 'https://lenta.ru/'

header = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36'}

response = requests.get(url, headers=header)
dom = html.fromstring(response.text)

news_items = dom.xpath("//div[@class='span4']/div[@class='item'] | //h2/a")

news_list = []

for item in news_items:
    news = {}
    news_name = ' '.join(item.xpath("./a/text() | ./text()")).replace('\xa0', ' ')
    # убирая элемент \xa0 у нас может пробел появиться в начале или в конце строки, поэтому убираем
    # эти пробелы
    if news_name[0] == ' ':
        news_name = list(news_name)
        news_name[0] = ''
        news_name = ' '.join(news_name)
    elif news_name[-1] == ' ':
        news_name = list(news_name)
        news_name[-1] = ''
        news_name = ' '.join(news_name)
    #вставляем /text(), чтоб вытащить не объект, а текст
    link = ''.join(item.xpath("./a/@href | ./@href"))
    # через @ прописываем атрибут href, который также является узлом
    if link.find('https:') == -1:
        link = url + link

    news_date = ''.join(item.xpath(".//time[@class='g-time']/@title | .//time[@class='g-time']/@title"))
    news_date = list(news_date)
    news_date = ''.join(news_date)
    # news_date = datetime.strptime(news_date, date_format)


    news['site'] = url
    news['news_agency'] = 'Lenta.ru'
    news['news'] = news_name
    news['link'] = link
    news['date'] = news_date

    news_list.append(news)

    current_news.update_one(
                            {'link': news['link']},
                            {'$set': news},
                            upsert=True)



"""Собираем данные с Nes.mail.ru"""

url = 'https://news.mail.ru/'

response = requests.get(url, headers=header)
dom = html.fromstring(response.text)

news_items = dom.xpath("//td[position()=1] | "
                    "//a[@class='photo photo_small photo_scale photo_full js-topnews__item'] |"
                    "//li[position()>2]/a[@class='list__text']")

for item in news_items:
    news = {}
    news_name = ' '.join(item.xpath(".//span[@class='photo__title photo__title_new photo__title_new_hidden "
    "js-topnews__notification']/text() | .//text() | ./text()")).replace('\xa0', ' ').replace('\r\n', '')
    if news_name[0] == ' ':
        news_name = list(news_name)
        news_name[0] = ''
        news_name = ' '.join(news_name)
    elif news_name[-1] == ' ':
        news_name = list(news_name)
        news_name[-1] = ''
        news_name = ' '.join(news_name)

    link = ''.join(item.xpath(".//a[contains(@class, 'photo_scale')]/@href | ./@href | ./@href"))

    url_item = link
    response_item = requests.get(url_item, headers=header)
    dom_item = html.fromstring(response_item.text)

    news_date = ''.join(dom_item.xpath("//span[@class='note']//@datetime"))[0:10]

    news_agency = dom_item.xpath("//span[@class='note']//text()")[2]

    news['site'] = url
    news['news_agency'] = news_agency
    news['news'] = news_name
    news['link'] = link
    news['date'] = news_date

    news_list.append(news)

    current_news.update_one(
        {'link': news['link']},
        {'$set': news},
        upsert=True)

# pprint(news_list)
# print(len(news_list))

for item in current_news.find({}):
    print(item)

print(f'В базе данных {current_news.count_documents({})} новостей')