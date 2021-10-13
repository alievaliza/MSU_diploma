import matplotlib
from matplotlib import pyplot
from typing import Dict
import pandas as pd
import numpy as np
from IPython.display import display
import seaborn as sns

matplotlib.rcParams['figure.figsize'] = (10, 10)
sns.set_style('whitegrid')

def fill_prof_area(prof_areas: Dict, row: str):
  """
  Создаём метод, который заполняет словарь prof_area сферами и частотой их встречания в вакансиях
  Аргумент:
  row - строка в датафрейме
  """
  for el in row:
    if el in prof_areas:
      prof_areas[el] += 1
    else:
      prof_areas[el] = 1

def find_best_prof_area(prof_areas: Dict, row: str, type: str) -> str:
  """
  Создаём метод, который из всех специализаций выбирает ту, которая встречается чаще всего
  Аргумент:
  row - строка в датафрейме
  """
  if type == 'max':
    max = 1
    for el in row:
      if prof_areas[el] > max:
        res = el
        max = prof_areas[el]
  elif type == 'min':
    min = 10**10
    for el in row:
      if prof_areas[el] < min:
        res = el
        min = prof_areas[el]
  elif type == 'last':
    res = row[-1]
  else:
    res = row[0]
  return res

def plot_dict(d: Dict):
  """
  Создаём метод, который строит гистограмму для словаря
  Аргумент:
  d - словарь, который нужно изобразить на гистограмме
  """
  keys = list(d.keys())
  vals = [(d[k]) for k in keys]
  sns.barplot(x=keys, y=vals, color='green')
  pyplot.xticks(rotation=45, ha="right");

def plot_salary(df: pd.DataFrame, col: str, currency: bool):
  """
  Создаём метод, который рисует распределение зарплат по какому-то параметру
  Аргументы:
  df - датафрейм со всем массивом данных
  col - по какому параметру (столбцу) строим распределение
  currency - бинарная переменная, нужно ли условие на российскую валюту
  """
  for el in df[col].dropna().unique():
    if currency:
      sns.kdeplot(df['salary_avg'][df[col] == el][df['salary_currency'] == 'RUR']/1000, color = 'green', label='среднне')
      sns.kdeplot(df['salary_from'][df[col] == el][df['salary_currency'] == 'RUR']/1000, color = 'blue', label='от')
      sns.kdeplot(df['salary_to'][df[col] == el][df['salary_currency'] == 'RUR']/1000, color = 'orange', label='до')
      pyplot.xlim(10, 230)
    else:
      sns.kdeplot(df['salary_avg'][df[col] == el]/1000, color = 'green', label='среднне')
      sns.kdeplot(df['salary_from'][df[col] == el]/1000, color = 'blue', label='от')
      sns.kdeplot(df['salary_to'][df[col] == el]/1000, color = 'orange', label='до')
    pyplot.legend(loc='upper right')
    pyplot.title(el)
    pyplot.xlabel("З/п, тыс.")
    pyplot.ylabel("Количество вакансий")
    pyplot.show()

def statistics(df: pd.DataFrame, col: str, currency: bool):
  """
  Создаём метод, который делает описательную статистику з/п по какому-то параметру (столбцу)
  Аргументы:
  df - датафрейм со всем массивом данных
  col - по какому параметру (столбцу) строим распределение
  currency - переменная, нужно ли условие на российскую валюту
  """
  for el in df[col].dropna().unique():
        print(f'\n{el}\n')
        if currency:
            x = df[df[col] == el][df['salary_currency'] == 'RUR'].describe()[
                ['salary_from', 'salary_to', 'salary_avg']]
        else:
            x = df[df[col] == el].describe()[['salary_from', 'salary_to', 'salary_avg']]
        s = x.style.format(formatter='{:,.0f}')
        display(s)

def tax(df: pd.DataFrame, col: str):
  """
  Создвём метод, который нормирует на НДФЛ для каждой страны
  Аргументы:
  df - исходный массив данных
  col - столбец с з/п, который нужно нормировать
  """
  df[col][(df['salary_gross'] == False) & ((df['country_name'] == 'Россия') | (df['country_name'] == 'Беларусь'))] = df[col] / 0.87
  df[col][(df['salary_gross'] == False) & ((df['country_name'] == 'Казахстан') | (df['country_name'] == 'Кыргызстан'))] = df[col] / 0.9
  df[col][(df['salary_gross'] == False) & (df['country_name'] == 'Украина')] = df[col] / 0.82
  df[col][(df['salary_gross'] == False) & (df['country_name'] == 'Грузия')] = df[col] / 0.8