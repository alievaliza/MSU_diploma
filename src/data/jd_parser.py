import pandas as pd
import gdown
import argparse
from typing import List, Dict
from googletrans import Translator
import langid
import re
import requests
import json

parser = argparse.ArgumentParser(description='Parsing job descriptions')
parser.add_argument(
    '--output_path',
    type= str,
    default='.',
    help='input output_path (default: ".")'
)
parser.add_argument(
    '--translate_description',
    type= bool,
    default=False,
    help='input translate_description (default: False)'
)
output_path = parser.parse_args().output_path
translate_description = parser.parse_args().translate_description

# Загружаем таблицу с гугл-диска
url = '15_FfenvHFoJVcPu6gGx9osLn71uDJ-Et'
output = f"{output_path}/vacancies_interim.csv"
gdown.download('https://drive.google.com/uc?export=download&id=' + url, output, quiet=False)

df = pd.read_csv(output)

# Удаляем идентичные столбцы
cols = ['billing_type_id', 'experience_id', 'employment_id', 'alternate_url', 'schedule_id', 'area_url', 'working_time_modes_id', 'type_id']
for col in cols:
  del df[col]

# Получаем все города и их parent_id
req = requests.get('https://api.hh.ru/areas')  # Посылаем запрос к API
data = req.content.decode()  # Декодируем его ответ, чтобы Кириллица отображалась корректно
req.close()
jsonObj = json.loads(data)
cities, countries_name, areas_name = [], [], []
for i in range(len(jsonObj)):
    for area in jsonObj[i]['areas']:
      if area['areas'] == []:
        cities.append(area)
        countries_name.append(jsonObj[i]['name'])
        areas_name.append(area['name'])
      else:
        for city in area['areas']:
          cities.append(city)
          countries_name.append(jsonObj[i]['name'])
          areas_name.append(area['name'])
df_cities = pd.DataFrame(cities)
df_cities['country_name'] = countries_name
df_cities['areas_name'] = areas_name

# Переименовываем столбец
df_cities['area_id'] = df_cities['id']
df_cities = df_cities.drop('id', axis=1)

# Конвертируем в формат int, чтобы сопоставить
df_cities['area_id'] = df_cities['area_id'].astype(str).astype(int)

# Присваиваем каждой строке имя региона и страны
df['areas_name'] = df['area_id'].map(df_cities.set_index('area_id')['areas_name'])
df['country_name'] = df['area_id'].map(df_cities.set_index('area_id')['country_name'])

# Создаём столбец prof_area
df['specializations_profarea_name'] = df['specializations_profarea_name'].apply(lambda x: eval(x))
df['prof_area'] = df['specializations_profarea_name'].apply(lambda x: x[0])

# Создаём столбец spezialization
df['specialization'] = df['specializations_name'].apply(lambda x: eval(x)[0])

# Добавляем фичи с длиной специализаций и сфер
df['len_specializations'] = df['specializations_name'].apply(lambda x: len(eval(x)))
df['len_profarea'] = df['specializations_profarea_name'].apply(lambda x: len(set(x)))

# Удаляем столбцы, в которых больше 85% NaN:
# 'department_id', 'department_name', 'driver_license_types_id', 'test_required', 'working_days_id', 'working_days_name', 'working_time_intervals_id', 'working_time_intervals_name',
# 'branded_description', 'response_url', 'code', 'immediate_redirect_url', 'insider_interview_id', 'insider_interview_url', 'vacancy_constructor_template_id',
# 'vacancy_constructor_template_name', 'vacancy_constructor_template_top_picture_height', 'vacancy_constructor_template_top_picture_width',
# 'vacancy_constructor_template_top_picture_path', 'vacancy_constructor_template_top_picture_blurred_path', 'vacancy_constructor_template_bottom_picture_height',
# 'vacancy_constructor_template_bottom_picture_width', 'vacancy_constructor_template_bottom_picture_path', 'vacancy_constructor_template_bottom_picture_blurred_path'
for col in df.columns:
  if df[col].isna().sum()/len(df) > 0.85:
    del df[col]

# Перекодируем столбец с опытом работы в числа
df['experience_name'] = df['experience_name'].replace('Нет опыта', 0)
df['experience_name'] = df['experience_name'].replace('От 1 года до 3 лет', 2)
df['experience_name'] = df['experience_name'].replace('От 3 до 6 лет', 4.5)
df['experience_name'] = df['experience_name'].replace('Более 6 лет', 6)

# определяем язык описаний
lang_list = []
def lang_variety(x: str):
    """
    Создаём метод, который определяет язык и создаёт список с языками
    Аргумент:
    x - текст, у которого нужно определить язык
    """
    language = langid.classify(x)[0]
    lang_list.append(language)

df['description'].apply(lambda x: lang_variety(x))
df['language'] = pd.DataFrame(lang_list)

if translate_description:
    # переводим не русскоязычные описания
    translator = Translator()
    df['description'][df['language'] != 'ru'] = df['description'][df['language'] != 'ru'].apply(lambda x: translator.translate(x, dest='ru').text)

# Сохраняем столбец с непреобразованным описанием вакансий
df['raw_description'] = df['description']

def jd(x: str, regular_try: str, regular_except: str, regular_except_try: str, result: list, result_: list):
  """
  Создаём метод, который ищет по заданному регулярному выражению в строке
  Аргументы:
  x - строка в датафрейме с описанием вакансий
  regular_try, regular_except, regular_except_try - регулярные выражения, согласно которым работает парсер
  result - список, куда записывается результат работы метода
  result_ - список (для столбца description), из которого удаляются регулярные выражения
  """
  try:
    result.append(re.search(regular_try, x).group(0))
    result_.append(re.sub(regular_try, '', x))
  except:
    try:
      result.append(re.search(regular_except, x).group(0))
      result_.append(re.sub(regular_except, '', x))
    except:
      try:
        result.append(re.search(regular_except_try, x).group(0))
        result_.append(re.sub(regular_except_try, '', x))
      except:
        result.append(re.search(regular_except, x))
        result_.append(re.sub(regular_except, '', x))

def jd_new_column(regular_try: str, regular_except: str, regular_except_try: str, new_column: str, df: pd.DataFrame):
  """
  Создаём метод, который создаёт новый столбец после парсинга
  Аргументы:
  regular_try, regular_except, regular_except_try - регулярные выражения, согласно которым работает парсер
  new_column - название столбца, который создаётся
  df - датафрейм, который содержит описание вакансий
  """
  result, result_ = [], []
  df['description'].apply(lambda x: jd(x, regular_try, regular_except, regular_except_try, result, result_));
  df[f'description_{new_column}'] = pd.DataFrame(result)[0]
  df['description'] = pd.DataFrame(result_)

jd_new_column(r'(?i)обязанности:.*?(?=(<strong>|<\/ul>|требования|требование|условия|предлагаем))|чем предстоит заниматься.*?(?=(<strong>|<\/ul>|требования|требование|условия|предлагаем))|(задачи|задачах):.*?(?=(<strong>|<\/ul>|требования|требование|условия|предлагаем))|ищем.{1,25}которые\s{1,}будут.*?(?=(<strong>|<\/ul>|требования|требование|условия|предлагаем))|что нужно делать.*?(?=(<strong>|<\/ul>|требования|требование|условия|предлагаем))',
              r'(?i)обязанности.*?(\.|требования|требование|условия|предлагаем)|чем предстоит заниматься.*?(\.|требования|требование|условия|предлагаем)|(задачи|задачах).*?(\.|требования|требование|условия|предлагаем)|ищем.{1,15}которые\s{1,}будут.*?(\.|требования|требование|условия|предлагаем)|что нужно делать.*?(\.|требования|требование|условия|предлагаем)',
              r'(?i)обязанности.+|чем предстоит заниматься.+|(задачи|задачах).+|ищем.{1,15}которые\s{1,}будут.+|что нужно делать.+',
                       'responsibilities', df)

jd_new_column(r'(?i)(требования|требование):.*?(?=(<strong>|<\/ul>|обязанности|задачи|задачах|ищем.{1,25}которые\s{1,}будут|что нужно делать|условия|предлагаем))',
              r'(?i)(требования|требование).*?(\.|обязанности|задачи|задачах|ищем.{1,25}которые\s{1,}будут|что нужно делать|условия|предлагаем)',
              r'(?i)(требования|требование).+',
                       'requirements', df)

jd_new_column(r'(?i)условия:.*?(?=(<strong>|<\/ul>|обязанности|задачи|задачах|ищем.{1,25}которые\s{1,}будут|что нужно делать|требование|требования))|предлагаем.*?(?=(<strong>|<\/ul>|обязанности|задачи|задачах|ищем.{1,25}которые\s{1,}будут|что нужно делать|требование|требования))',
              r'(?i)условия.*?(\.|обязанности|задачи|задачах|ищем.{1,25}которые\s{1,}будут|что нужно делать|требование|требования)|предлагаем.*?(\.|обязанности|задачи|задачах|ищем.{1,25}которые\s{1,}будут|что нужно делать|требование|требования)',
              r'(?i)условия.+|предлагаем.+',
                       'conditions', df)

# Убираем из столбцов слова, по которым выделялись столбцы
df['description_responsibilities'] = df['description_responsibilities'].apply(lambda x: re.sub(r'(?i)(обязанности:|обязанности|чем предстоит заниматься|задачи|задачах|ищем.{1,25}которые\s{1,}будут|что нужно делать)', '', str(x)))
df['description_requirements'] = df['description_requirements'].apply(lambda x: re.sub(r'(?i)(требования|требование)', '', str(x)))
df['description_conditions'] = df['description_conditions'].apply(lambda x: re.sub(r'(?i)(условия|предлагаем)', '', str(x)))

# Разделяем столбец из строк на столбец из списков
df['description_responsibilities'] = df['description_responsibilities'].apply(lambda x: re.split('<li>|<br />|<p>', str(x)))
df['description_requirements'] = df['description_requirements'].apply(lambda x: re.split('<li>|<br />|<p>', str(x)))
df['description_conditions'] = df['description_conditions'].apply(lambda x: re.split('<li>|<br />|<p>', str(x)))

def delete_code(x: list) -> list:
  """
  Создаём метод, который сначала удаляет код из каждого элемента списка, далее удаляет элементы, состоящие только из символов,
  и далее удаляет тег </li>, </p>
  Аргумент:
  x - список с набором обязанностей/требований и т.д.
  Возвращает:
  x - очищенный от элементов, состоящих только из кода, список
  """
  x_copy = x.copy()
  x_copy = [re.sub('<.*?>|&quot', '', el) for el in x_copy]
  x_ = x.copy()
  for i in range(len(x_)):
    if re.match(r"^[! #$%&()*+,.\/:;<=>?@[\]^_`{|}~—\"\-]*$", x_copy[i]) is not None or x_copy[i] == 'None' or x_copy[i] == '':
      x.remove(x_[i])
  x = [re.sub('</li>|</p>', '', el) for el in x]
  return x

df['description_responsibilities'] = df['description_responsibilities'].apply(delete_code)
df['description_requirements'] = df['description_requirements'].apply(delete_code)
df['description_conditions'] = df['description_conditions'].apply(delete_code)

# Добавляем фичи с длиной списков для 3 столбцов
df['len_description_responsibilities'] = df['description_responsibilities'].apply(len)
df['len_description_requirements'] = df['description_requirements'].apply(len)
df['len_description_conditions'] = df['description_conditions'].apply(len)

# Сохраняем распарсенный датафрейм
df.to_csv(f'{output_path}/vacancies_processed.csv', index=False)