import requests
from bs4 import BeautifulSoup as bs
from pprint import pprint
import re
import pandas as pd

vac_name = input('ведите нименование вакансии: ')

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

        vacancy_data['link'] = vacancy_link
        vacancy_data['name'] = vacancy_name
        vacancy_data['site'] = vacancy_site
        vacancy_data['remun_min'] = vacancy_remun_min
        vacancy_data['remun_max'] = vacancy_remun_max
        vacancy_data['remun_curr'] = vacancy_remun_curr

        vacancies.append(vacancy_data)

    try:
        next_page = hh_data.find('a', attrs={'data-qa': 'pager-next'}).getText()
    except AttributeError:
        next_page = None
    p_i += 1


df_vacancies = pd.DataFrame(vacancies)
df_vacancies.to_csv('vacansies_list.csv', sep=',', index=False)

pprint(vacancies)
print(len(vacancies))
print(response.ok)
print(p_i)
print(vac_name)
print(df_vacancies)

