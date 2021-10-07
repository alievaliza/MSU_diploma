from matplotlib import pyplot
from typing import Dict
import pandas as pd
import numpy as np
from IPython.display import display

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

def find_best_prof_area(prof_areas: Dict, row: str) -> str:
  """
  Создаём метод, который из всех специализаций выбирает ту, которая встречается чаще всего
  Аргумент:
  row - строка в датафрейме
  """
  max = 1
  for el in row:
    if prof_areas[el] > max:
      res = el
      max = prof_areas[el]
  return el

def plot_dict(d: Dict):
  """
  Создаём метод, который строит гистограмму для словаря
  Аргумент:
  d - словарь, который нужно изобразить на гистограмме
  """
  pyplot.bar(d.keys(), d.values(), color='g')
  pyplot.xticks(rotation=45, ha="right");
  pyplot.show()

def plot_salary(df: pd.DataFrame, col: str, Q: float, currency: bool):
  """
  Создаём метод, который рисует распределение зарплат по какому-то параметру
  Аргументы:
  df - датафрейм со всем массивом данных
  col - по какому параметру (столбцу) строим распределение
  Q - выше какого-то перцентиля не учитываем з/п
  currency - бинарная переменная, нужно ли условие на российскую валюту
  """
  for el in df[col].dropna().unique():
    Q_from = np.nanpercentile(df['salary_from'][df[col] == el], Q)
    Q_to = np.nanpercentile(df['salary_to'][df[col] == el], Q)
    Q_avg = np.nanpercentile(df['salary_avg'][df[col] == el], Q)
    if currency:
      pyplot.hist(df['salary_avg'][df['salary_avg'] < Q_avg][df[col] == el][df['salary_currency'] == 'RUR']/1000, bins = 15, alpha=0.5, label='avg')
      pyplot.hist(df['salary_from'][df['salary_from'] < Q_from][df[col] == el][df['salary_currency'] == 'RUR']/1000, bins = 15, alpha=0.5, label='from')
      pyplot.hist(df['salary_to'][df['salary_to'] < Q_to][df[col] == el][df['salary_currency'] == 'RUR']/1000,bins = 15, alpha=0.5, label='to')
    else:
      pyplot.hist(df['salary_avg'][df['salary_avg'] < Q_avg][df[col] == el]/1000, bins = 15, alpha=0.5, label='avg')
      pyplot.hist(df['salary_from'][df['salary_from'] < Q_from][df[col] == el]/1000, bins = 15, alpha=0.5, label='from')
      pyplot.hist(df['salary_to'][df['salary_to'] < Q_to][df[col] == el]/1000,bins = 15, alpha=0.5, label='to')
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