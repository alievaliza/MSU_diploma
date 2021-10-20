import matplotlib
from matplotlib import pyplot
from typing import Dict
import pandas as pd
from IPython.display import display
import seaborn as sns

matplotlib.rcParams['figure.figsize'] = (10, 10)
sns.set_style('whitegrid')

def fill_prof_area(prof_areas: Dict, row:  list):
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

def find_best_prof_area(prof_areas: Dict, row:  list, type: str) -> str:
  """
  Создаём метод, который из всех специализаций выбирает одну
  Аргументы:
  prof_areas - словарь со сферами вакансий
  row - строка в датафрейме
  type - тип, по которому вакансии присваивается однозначным образом сфера занятости:
    ('max' - наиболее часто встречающаяся среди всего датафрейма,
    'min' - наиболее редко встречающаяся среди всего датафрейма,
    'last' - последняя по счёту,
    'first' - первая по счёту)
  Возвращает:
  res - сферу, соответствующую вакансии
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

def mostcommon_specialization(prof_area: str, row: list, sp: pd.DataFrame) -> str:
    """
    Создаём метод, который сопоставляет вакансии специализацию
    Аргументы:
    prof_area - сфера занятости для вакансии
    row - список специализаций в вакансии
    sp - датафрейм с сопоставлением сфер и специализаций
    Возвращает:
    одну специализацию
    """
    for specialization in row:
        try:
            if pd.notna(sp[prof_area][specialization]):
                return specialization
        except:
            pass
    return 'Другое'

def prof_area_matrix(len_profareas: pd.DataFrame, row: set):
    """
    Создаём метод, который заполняет матрицу сопоставлений сфер в одной вакансии
    Аргументы:
    len_profareas - матрица, которую заполняет метод
    row - строка в столбце со всеми сферами в исхдном датафрейме
    """
    for el_1 in row:
        for el_2 in row:
            len_profareas[el_1][el_2] += 1
        len_profareas[el_1] = 100* len_profareas[el_1] / len_profareas[el_1][el_1]

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

def plot_salary(df: pd.DataFrame, col: str, currency: bool, diff: bool, figsize: (float, float)):
  """
  Создаём метод, который рисует распределение зарплат по какому-то параметру
  Аргументы:
  df - датафрейм со всем массивом данных
  col - по какому параметру (столбцу) строим распределение
  currency - бинарная переменная, нужно ли условие на российскую валюту
  diff - бинарная переменная, нужно рисовать salary_diff или salary_from, dalary_to, salary_avg
  figsize - размер графика
  """
  els = df[col].dropna().unique()
  nrows = int(len(els)/3)+1 if len(els) % 3 != 0 else int(len(els)/3)
  fig, ax = pyplot.subplots(nrows=nrows, ncols=3, figsize=figsize)
  k = 0
  for i in range(nrows):
    for j in range(3):
        try:
            if currency and diff:
              sns.histplot(df['salary_diff'][df[col] == els[k]][df['salary_currency'] == 'RUR'] / 1000, ax = ax[i, j], color='green', kde=True, bins = 15)
              ax[i, j].set_xlim([0, 300])
            elif currency:
              sns.distplot(df['salary_avg'][df[col] == els[k]][df['salary_currency'] == 'RUR']/1000, ax = ax[i, j], color = 'green', label='среднее', hist=False, kde=True)
              sns.distplot(df['salary_from'][df[col] == els[k]][df['salary_currency'] == 'RUR']/1000, ax = ax[i, j], color = 'blue', label='от', hist=False, kde=True)
              sns.distplot(df['salary_to'][df[col] == els[k]][df['salary_currency'] == 'RUR']/1000, ax = ax[i, j], color = 'orange', label='до', hist=False, kde=True)
              ax[i, j].set_xlim([1, 350])
            else:
              sns.distplot(df['salary_avg'][df[col] == els[k]]/1000, ax = ax[i, j], color = 'green', label='среднее', hist=False, kde=True)
              sns.distplot(df['salary_from'][df[col] == els[k]]/1000, ax = ax[i, j], color = 'blue', label='от', hist=False, kde=True)
              sns.distplot(df['salary_to'][df[col] == els[k]]/1000, ax = ax[i, j], color = 'orange', label='до', hist=False, kde=True)
            ax[i, j].set_title(els[k], fontsize = 20)
            ax[i, j].set_xlabel("З/п, тыс.", fontsize = 20)
            ax[i, j].set_ylabel("Количество вакансий", fontsize = 20)
            ax[i, j].legend(loc='upper right', fontsize = 20)
            ax[i, j].tick_params(labelsize=20)
        except:
            pass
        k += 1
  fig.tight_layout(pad=2)
  pyplot.show()

def tax(df: pd.DataFrame, col: str):
  """
  Создвём метод, который нормирует на НДФЛ для каждой страны
  Аргументы:
  df - исходный массив данных
  col - столбец с з/п, который нужно нормировать
  """
  df.loc[(df['salary_gross'] == False) & ((df['country_name'] == 'Россия') | (df['country_name'] == 'Беларусь')), col] = df[col] / 0.87
  df.loc[(df['salary_gross'] == False) & ((df['country_name'] == 'Казахстан') | (df['country_name'] == 'Кыргызстан')), col] = df[col] / 0.9
  df.loc[(df['salary_gross'] == False) & (df['country_name'] == 'Украина'), col] = df[col] / 0.82
  df.loc[(df['salary_gross'] == False) & (df['country_name'] == 'Грузия'), col] = df[col] / 0.8
