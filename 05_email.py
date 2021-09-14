"""1) Написать программу, которая собирает входящие письма из своего или тестового почтового ящика и сложить данные о письмах в базу данных (от кого, дата отправки, тема письма, текст письма полный)
Логин тестового ящика: study.ai_172@mail.ru
Пароль тестового ящика: NextPassword172???
"""
import time
import re
from pprint import pprint
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys # импортируем блок по эмитации кнопок
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from pymongo import MongoClient

Log = 'study.ai_172@mail.ru'
PWD = 'NextPassword172???'

chrome_options = Options()
chrome_options.add_argument('start-maximized')

driver = webdriver.Chrome(executable_path='./chromedriver.exe', options=chrome_options)

driver.get("https://mail.ru/")

login = driver.find_element_by_xpath("//input[@name='login']")
login.send_keys(Log.split('@')[0])
login.send_keys(Keys.ENTER)

time.sleep(1)
passw = driver.find_element_by_xpath("//input[@name='password']")
passw.send_keys(PWD)
passw.send_keys(Keys.ENTER)

time.sleep(1)

wait_ = WebDriverWait(driver, 10)
wait_.until(EC.element_to_be_clickable((By.CLASS_NAME, 'js-tooltip-direction_letter-bottom')))

message_no = driver.find_element_by_xpath("//a[contains(@title, 'Входящие')]").get_attribute('title')
message_no = int(re.findall('[0-9]+', message_no)[0])

links = set()

while len(links) < message_no:

    try:
        message_links = driver.find_elements_by_class_name('js-tooltip-direction_letter-bottom')
        for message_link in message_links:
            links.add(message_link.get_attribute('href'))

        actions = ActionChains(driver)
        actions.move_to_element(message_links[-1])
        actions.perform()
    except Exception:
        break


client = MongoClient('127.0.0.1', 27017)
db = client['hh_vac']
mail_info = db.mail_info

for url in links:
    driver.get(url)

    wait_ = WebDriverWait(driver, 10)
    wait_.until(EC.presence_of_element_located((By.CLASS_NAME, 'letter-contact')))

    data = {
        'link': url,
        'to': Log,
        'from': driver.find_element_by_class_name("letter-contact").get_attribute("title"),
        'date': driver.find_element_by_xpath("//div[@class='letter__date']").text,
        'text': driver.find_element_by_xpath("//div[@class='letter-body__body']").text
    }

    mail_info.update_one(
        {'link': data['link']},
        {'$set': data},
        upsert=True)



















