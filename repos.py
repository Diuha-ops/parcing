import requests
from pprint import pprint
import json
my_login = str(input('Введите логин в GitHub: ')) # мой логин diuha-ops
my_headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.164 Safari/537.36'}

url = 'https://api.github.com/users/' + my_login + '/repos'

response = requests.get(url, headers=my_headers)
j_data = response.json()

rep = [item['name'] for item in j_data]

print(rep)
with open('repos_list.jsn', 'w') as fp:
    json.dump(rep, fp)