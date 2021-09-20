# Библиотека для работы с HTTP-запросами. Будем использовать ее для обращения к API HH
import requests
# Пакет для удобной работы с данными в формате json
import json
# Модуль для работы со значением времени
import time
# Модуль для работы с операционной системой. Будем использовать для работы с файлами
import os
# Модуль для работы с отображением вывода Jupyter
from IPython import display
import pandas as pd
import json
import os
from os.path import join as pjoin
import shutil
import gdown

# PART 0 Получаем id регионов
try:
    f = open('areas.txt', encoding='utf8')
    jsonText = f.read()
    f.close()
    # Преобразуем полученный текст в объект справочника
    jsonObj = json.loads(jsonText)
    areas_id, countries_name = [], []
    countries = 9
    for i in range(countries):
      for area in jsonObj[i]['areas']:
        areas_id.append(area)
        countries_name.append(jsonObj[i]['name'])

    df_areas = pd.DataFrame(areas_id)
    df_areas['country_name'] = countries_name
    # df_areas.to_excel('areas.xlsx', index=False)
except:
    print('Загрузите файл "areas.txt"')

# PART 1
getAllPages(df_areas)

# PART 2
getAllvacancies()
print('Вакансии собраны')

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

try:
    df.to_csv('vacancies.csv', index=False)
except:
    print("Нехватка оперативной памяти. Разбить df на 2 или более частей")

# Выводим сообщение об окончании программы
display.clear_output(wait=True)
display.display('Вакансии загружены в файл')