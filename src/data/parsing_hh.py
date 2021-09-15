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
# Библиотека для работы с СУБД
#from sqlalchemy import engine as sql
import pandas as pd
import json
import os
from os.path import join as pjoin
import shutil
import gdown

print('Введите path_dst:')
path_dst = input()
path_dst = path_dst if path_dst != '' else 'C:/Users/Lisa/diploma/src/data/pagination_done/'
print('Введите path_src:')
path_src = input()
path_src = path_src if path_src != '' else 'C:/Users/Lisa/diploma/src/data/pagination/'

# PART 0 'Areas'

f = open('areas.txt', encoding='utf8')
jsonText = f.read()
f.close()
# Преобразуем полученный текст в объект справочника
jsonObj = json.loads(jsonText)
areas_id, countries_name = [], []
# 9 стран
for i in range(9):
  for area in jsonObj[i]['areas']:
    areas_id.append(area)
    countries_name.append(jsonObj[i]['name'])

df_areas = pd.DataFrame(areas_id)
df_areas['country_name'] = countries_name
df_areas.to_excel('areas.xlsx', index=False)

# PART 1

def getPage(page, area):
    """
    Создаем метод для получения страницы со списком вакансий.
    Аргументы:
        page - Индекс страницы
    """

    # Справочник для параметров GET-запроса
    params = {
        'area': area,  # Поиск ощуществляется по вакансиям города area
        'page': page,  # Индекс страницы поиска на HH
        'per_page': 100  # Кол-во вакансий на 1 странице
    }

    req = requests.get('https://api.hh.ru/vacancies', params)  # Посылаем запрос к API
    data = req.content.decode()  # Декодируем его ответ, чтобы Кириллица отображалась корректно
    req.close()
    return data

areas = len(df_areas)

for i in range(areas):
        area = df_areas['id'][i]
        print(area)
        # Считываем первые 2000 вакансий
        for page in range(20):
            # Преобразуем текст ответа запроса в справочник Python
            try:
                jsObj = json.loads(getPage(page, area))
            # Сохраняем файлы в папку {путь до текущего документа со скриптом}\docs\pagination
            # Определяем количество файлов в папке для сохранения документа с ответом запроса
            # Полученное значение используем для формирования имени документа
                if not os.path.exists('./pagination'):
                    os.mkdir('./pagination')
                nextFileName = './pagination/{}.json'.format(len(os.listdir('./pagination')))
            # Создаем новый документ, записываем в него ответ запроса, после закрываем
                f = open(nextFileName, mode='w', encoding='utf8')
                f.write(json.dumps(jsObj, ensure_ascii=False))
                f.close()
            # Проверка на последнюю страницу, если вакансий меньше 2000
            #if (jsObj['pages'] - page) <= 1:
            #    break
            # Необязательная задержка, но чтобы не нагружать сервисы hh, оставим. 5 сек мы может подождать
                time.sleep(0.25)
            except:
                pass
        print('Страницы поиска собраны', area)

# PART 2
start_time = time.time()

# path_dst = 'C:/Users/Lisa/diploma/src/data/pagination_done/'
# path_src = 'C:/Users/Lisa/diploma/src/data/pagination/'
stop = 0

for fl in os.listdir('./pagination'):
    if stop == 1:
        break
    print(fl)
    # Открываем файл, читаем его содержимое, закрываем файл
    f = open('./pagination/{}'.format(fl), encoding='utf8')
    jsonText = f.read()
    f.close()
    # Преобразуем полученный текст в объект справочника
    jsonObj = json.loads(jsonText)
    # Получаем и проходимся по непосредственно списку вакансий
    for v in jsonObj['items']:
        # Обращаемся к API и получаем детальную информацию по конкретной вакансии
        req = requests.get(v['url'])
        data = req.content.decode()
        req.close()
        # Создаем файл в формате json с идентификатором вакансии в качестве названия
        # Записываем в него ответ запроса и закрываем файл
        fileName = f'./vacancies/{v["id"]}.json'
        f = open(fileName, mode='w', encoding='utf8')
        f.write(data)
        f.close()
        f = open(fileName, mode='r', encoding='utf8')
        jsonText = f.read()
        f.close()
        jsonObj = json.loads(jsonText)
        try:
            if jsonObj['request_id']:
                print('Лимит исчерпан')
                print("--- %s minutes ---" % ((time.time() - start_time)/60))
                stop = 1
                break
        except:
            try:
                shutil.move(path_src + fl, path_dst + fl)
            except:
                print(f'Не удалось переместить {fl}')
#         time.sleep(0.25)

print('Вакансии собраны')

# PART 3 (released in Colab)

# Загрузка файла 'vacancies.zip' с гугл-драйва и его распаковка
url = '1vGZg5w7mFYwxRzE96xZuxn_Lv_uq_soy'
output = "vacancies.zip"
gdown.download('https://drive.google.com/uc?export=download&id=' + url, output, quiet=False)
zf = zipfile.ZipFile("vacancies.zip")
zf.extractall()

# В выводе будем отображать прогресс
# Для этого узнаем общее количество файлов, которые надо обработать
# Счетчик обработанных файлов установим в ноль
cnt_docs = len(os.listdir('./vacancies'))
i = 0
vac = []
# Проходимся по всем файлам в папке vacancies
for fl in os.listdir('./vacancies'):
    # Открываем, читаем и закрываем файл
    f = open('./vacancies/{}'.format(fl), encoding='utf8')
    jsonText = f.read()
    f.close()
    # Текст файла переводим в справочник
    try:
        jsonObj = json.loads(jsonText)
        vac.append(jsonObj)
    except:
        print('Ошибка')
    # Увеличиваем счетчик обработанных файлов на 1, очищаем вывод ячейки и выводим прогресс
    i += 1
    display.clear_output(wait=True)
    display.display('Готово {} из {}'.format(i, cnt_docs))

# Создадим соединение с БД
#"postgres://YourUserName:YourPassword@YourHostname:5432/YourDatabaseName"
#eng = sql.create_engine('postgresql://liolive@parseddatafromhhru:password@parseddatafromhhru.database.windows.net:1433/hh.ru')
#conn = eng.connect()

#df.to_sql('vacancies', conn, schema='public', if_exists='append', index=False)

# Создаем пандосовский датафрейм, который затем сохраняем в БД в таблицу vacancies
df = pd.DataFrame(vac)
df.to_excel('vacancies.xlsx', index=False)
#df.to_sql('skills', conn, schema='public', if_exists='append', index=False)
# Закрываем соединение с БД
#conn.close()

# Выводим сообщение об окончании программы
display.clear_output(wait=True)
display.display('Вакансии загружены в файл')