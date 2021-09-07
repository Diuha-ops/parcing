import requests
from bs4 import BeautifulSoup as bs
from pprint import pprint
import re
import pandas as pd
from pymongo import MongoClient
import datetime

vac_name = input('ведите наименование вакансии: ')

client = MongoClient('127.0.0.1', 27017)
db = client['hh_vac']
hh_vacancies = db.hh_vacancies

# создаем структуру коллекции
vacancy_data = {}

vacancy_data['1_source_site'] = None
vacancy_data['2_name'] = None
vacancy_data['3_id_hh'] = None
vacancy_data['4_link'] = None
vacancy_data['5.1_remun_min'] = None
vacancy_data['5.2_remun_max'] = None
vacancy_data['5.3_remun_curr'] = None
vacancy_data['6.1_inserted_at_Y'] = None
vacancy_data['6.2_inserted_at_M'] = None
vacancy_data['6.3_inserted_at_D'] = None
vacancy_data['7.1_modified_at_Y'] = None
vacancy_data['7.2_modified_at_M'] = None
vacancy_data['7.3_modified_at_D'] = None

# проверяем наличие шаблонного документа, чтобы БД не плодила новые одинаковоей документы
# и загружаем шаблон документа в коллекцию
if not hh_vacancies.find_one({'3_id_hh': None}):
    hh_vacancies.insert_one(vacancy_data)


url = 'https://hh.ru'

p_i = 0 # счетчик страниц
next_page = 'дальше'
headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36'}

vacancies = []
while next_page == 'дальше':
    params = {'clusters': 'true',
              'ored_clusters': 'true',
            'enable_snippets': 'true',
            'salary': '',
            'st': 'searchVacancy',
            'text': vac_name,
            'page': p_i}


    response = requests.get(url + '/search/vacancy', headers=headers, params=params)

    hh_data = bs(response.text, 'html.parser')

    vacancy_list = hh_data.find_all('div', attrs={'class': 'vacancy-serp-item__row vacancy-serp-item__row_header'})

    for vacancy in vacancy_list:

        vacancy_data = {}
        vacancy_site = 'HH'
        vacancy_name = vacancy.find('a', attrs={'class': 'bloko-link'}).getText()
        vacancy_link = vacancy.find('a', attrs={'class': 'bloko-link'}).get('href')
        vacancy_id = re.findall('[0-9]+', vacancy_link)
        try:
            vacancy_remun = vacancy.find('span', attrs={'data-qa': 'vacancy-serp__vacancy-compensation'}).getText()
            simbol = '\u202f'
            vacancy_remun = vacancy_remun.replace(simbol, '')
            amount = re.findall('[0-9]+', vacancy_remun) # Ищем значения зарплат
            if 'от' in vacancy_remun:
                vacancy_remun_min = int(amount[0])
                vacancy_remun_max = None
            elif 'до' in vacancy_remun:
                vacancy_remun_min = None
                vacancy_remun_max = int(amount[0])
            else:
                vacancy_remun_min = int(amount[0])
                vacancy_remun_max = int(amount[1])
            vacancy_remun_curr = vacancy_remun[-4:].replace(' ', '') # выделяем валюту, если в ней 3 знака, то убираем пробел
        except AttributeError:
            vacancy_remun = None
            vacancy_remun_min = None
            vacancy_remun_max = None
            vacancy_remun_curr = None

        vacancy_data['1_source_site'] = vacancy_site
        vacancy_data['2_name'] = vacancy_name
        vacancy_data['3_id_hh'] = vacancy_id
        vacancy_data['4_link'] = vacancy_link
        vacancy_data['5.1_remun_min'] = vacancy_remun_min
        vacancy_data['5.2_remun_max'] = vacancy_remun_max
        vacancy_data['5.3_remun_curr'] = vacancy_remun_curr
        vacancy_data['6.1_inserted_at_Y'] = int(datetime.datetime.now().strftime('%Y'))
        vacancy_data['6.2_inserted_at_M'] = int(datetime.datetime.now().strftime('%m'))
        vacancy_data['6.3_inserted_at_D'] = int(datetime.datetime.now().strftime('%d'))
        vacancy_data['7.1_modified_at_Y'] = None
        vacancy_data['7.2_modified_at_M'] = None
        vacancy_data['7.3_modified_at_D'] = None

        hh_vacancies.replace_one({'3_id_hh': vacancy_id}, vacancy_data, upsert=True)

    try:
        next_page = hh_data.find('a', attrs={'data-qa': 'pager-next'}).getText()
    except AttributeError:
        next_page = None
    p_i += 1

for doc in hh_vacancies.find({}):
    pprint(doc)

salary_min = int(input('Укажите минимальную зарплату для вашего поиска: '))

for doc in hh_vacancies.find({'$or': [{'5.1_remun_min': {'$gt': salary_min}},
                                      {'5.2_remun_max': {'$gt': salary_min}}]}):
    pprint(doc)




