import pandas as pd
import gdown
import argparse
from typing import List, Dict
from googletrans import Translator
import langid
import re

parser = argparse.ArgumentParser(description='Parsing job descriptions')
parser.add_argument(
    '--output_path',
    type= str,
    default='.',
    help='input output_path (default: ".")'
)
parser.add_argument(
    '--detect_translate_language',
    type= bool,
    default=False,
    help='input detect_translate_language (default: False)'
)
output_path = parser.parse_args().output_path
detect_translate_language = parser.parse_args().detect_translate_language

# Загружаем таблицу с гугл-диска
url = '15_FfenvHFoJVcPu6gGx9osLn71uDJ-Et'
output = f"{output_path}/vacancies_interim.csv"
gdown.download('https://drive.google.com/uc?export=download&id=' + url, output, quiet=False)

df = pd.read_csv(output)

if detect_translate_language:
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

    # переводим не русскоязычные описания
    translator = Translator()
    df['description'][df['language'] != 'ru'] = df['description'][df['language'] != 'ru'].apply(lambda x: translator.translate(x, dest='ru').text)

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