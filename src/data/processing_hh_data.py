import pandas as pd
import gdown
import argparse
from typing import List, Dict

parser = argparse.ArgumentParser(description='Processing data from api.hh.ru')
parser.add_argument(
    '--output_path',
    type= str,
    default='.',
    help='input output_path (default: ".")'
)
output_path = parser.parse_args().output_path

# Загружаем таблицу с гугл-диска
url = '1OxQupfqEt36O2GwnP7gL-2Kq9pdR5Eii'
output = f"{output_path}/vacancies.xlsx"
gdown.download('https://drive.google.com/uc?export=download&id=' + url, output, quiet=False)

df = pd.read_excel(output)

def removing_trash(df):
  """
  Создаём метод, который удаляет пустые или полностью одинаковые столбцы
  Аргумент:
  df - датафрейм
  """
  for col in df.columns:
    if sum(~df[col].isnull()) == 0 or df[col].astype(str).nunique() == 1:
      del df[col]
  return df

df = removing_trash(df)

# Переводим текст в словари в каждом столбце
for col in df.columns:
  try:
    df[col] = df[col].apply(lambda x: eval(x) if not pd.isnull(x) else None)
  except:
    pass

# Переводим текст в формат даты
df['created_at'] = pd.to_datetime(df['created_at'])

def func(x: List[Dict], key: str):
  """
  Создаём метод, который создаёт столбец, состоящий из списков для каждого ключа словаря
  Аргументы:
  x - список из словарей
  key - ключ словаря
  """
  output = []
  if x != []:
    for i in range(len(x)):
      output.append(x[i][key])
  return output

# Разбиваем словари и списки по столбцам
def splitting(df):
  """
  Создаём метод, который разбивает столбцы, состоящие из словарей или списков по столбцам
  Аргументы:
  df - датафрейм
  """
  for col in df.columns:
    i = 0
    while df[col][i] is None or df[col][i] == []:
      i += 1
    if col == 'employer':
      i = 1966
    if type(df[col][i]) == dict:
      for key in df[col][i].keys():
        df[f'{col}_{key}'] = df[col].apply(lambda x: x[key] if x is not None else None)
      df = df.drop(col, 1)
    elif type(df[col][i]) == list:
      try:
        for key in df[col][i][0].keys():
          df[f'{col}_{key}'] = df[col].apply(lambda x: func(x, key) if (x != [] and x is not None) else None)
        df = df.drop(col, 1)
      except:
        pass
  return(df)

df = splitting(df)
df = removing_trash(df)
df = splitting(df)

# Столбцы, которые можно удалить
cols_to_remove = ["published_at"]

# Удаляем столбцы из списка cols_to_remove
for col in cols_to_remove:
  del df[col]

# Избавляемся от html-кода в столбце 'description'
# code = ['<li>', '</li>', '<strong>', '</strong>','<p>', '</p>','<ul>', '</ul>','&quot', '<em>', '<br />']
# for word in code:
#   df['description'] = df['description'].str.replace(word, '')

df.to_csv(f'{output_path}/vacancies.csv', index=False)