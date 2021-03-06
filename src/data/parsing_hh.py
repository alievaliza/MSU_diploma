# Библиотека для работы с HTTP-запросами. Будем использовать ее для обращения к API HH
import requests
# Пакет для удобной работы с данными в формате json
import json
# Модуль для работы с отображением вывода Jupyter
from IPython import display
import pandas as pd
import argparse
from parsing_utils import *

parser = argparse.ArgumentParser(description='Parsing vacancies from api.hh.ru')
parser.add_argument(
    '--from_area',
    type=int,
    default=0,
    help='input from_area (default: 0)'
)

# PART 0 Получаем id регионов
req = requests.get('https://api.hh.ru/areas')  # Посылаем запрос к API
data = req.content.decode()  # Декодируем его ответ, чтобы Кириллица отображалась корректно
req.close()
# Преобразуем полученный текст в объект справочника
jsonObj = json.loads(data)
areas_id, countries_name = [], []
for i in range(len(jsonObj)):
    for area in jsonObj[i]['areas']:
        areas_id.append(area)
        countries_name.append(jsonObj[i]['name'])
df_areas = pd.DataFrame(areas_id)
df_areas['country_name'] = countries_name

# PART 1
# Зададим время ожидания, равное 70 минутам, установленное эмпирически
wait = 4200
from_area = parser.parse_args().from_area
getAllPages(df_areas, wait, from_area)
print('\nСтраницы поиска собраны')

# PART 2
getAllVacancies(wait)
print('\nВакансии собраны')

# PART 3 (released in Colab)

# Часть для Google Colab. Загрузка файла 'vacancies.zip' с гугл-драйва и его распаковка
# url = '1vGZg5w7mFYwxRzE96xZuxn_Lv_uq_soy'
# output = "vacancies.zip"
# gdown.download('https://drive.google.com/uc?export=download&id=' + url, output, quiet=False)
# zf = zipfile.ZipFile("vacancies.zip")
# zf.extractall()

try:
    df = makeDataframe()
except:
    print("Нехватка оперативной памяти. Попробуйте реализовать в Google Colab")
    quit()

try:
    df.to_excel('vacancies.xlsx', index=False)
except:
    print("Нехватка оперативной памяти. Попробуйте разбить df на 2 или более частей")
    quit()
# Выводим сообщение об окончании программы
display.clear_output(wait=True)
display.display('Вакансии загружены в файл')