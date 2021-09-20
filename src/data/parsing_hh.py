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
from tqdm import tqdm

# PART 0 Получаем id регионов
try:
    f = open('areas.txt', encoding='utf8')
    jsonText = f.read()
    f.close()
except:
    print('Загрузите файл "areas.txt"')
    quit()
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



# PART 1
# Зададим время ожидания, равное 80 минутам, установленное эмпирически
wait = 4800
print("Введите from_area от 0 до 647 включительно (0 если сборка первая, 647 если сборка не нужна):")
try:
    from_area = int(input())
except:
    from_area = 0
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