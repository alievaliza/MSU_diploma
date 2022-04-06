import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_absolute_percentage_error
import numpy as np
from typing import Union, List, Dict
import joblib
from sklearn.model_selection import train_test_split
from sklearn import metrics
import sys, os
from sklearn.model_selection import KFold

sys.path.append(os.path.abspath('../'))
from src.data import eda_utils

def salary_process(df: pd.DataFrame):
  """
  Создаём метод, который нормирует salary_from на НДФЛ и переводит нерублевые валюты по курсу
  Аргумент:
  df - датафрейм с исходным массивом данных
  """
  # Переводим з/п в рубли по курсу на 09.12.2021
  currency = {'RUR': 1, 'BYR': 29.04, 'KZT': 0.17, 'UZS': 0.0068, 'UAH': 2.72, 'USD': 73.66, 'KGS': 0.87, 'EUR': 83.32, 'AZN': 43.33, 'GEL': 23.73}
  # Переводим з/п в нерублёвых валютах в рубли
  for curr in df['salary_currency'].unique():
      df['salary_from'][df['salary_currency'] == curr] = df['salary_from'][df['salary_currency'] == curr].apply(lambda x: x*currency[curr])
  # Нормируем на НДФЛ для каждой страны
  df.loc[(df['salary_gross'] == False) & ((df['country_name'] == 'Россия') | (df['country_name'] == 'Беларусь')), 'salary_from'] = df['salary_from'] / 0.87
  df.loc[(df['salary_gross'] == False) & ((df['country_name'] == 'Казахстан') | (df['country_name'] == 'Кыргызстан')), 'salary_from'] = df['salary_from'] / 0.9
  df.loc[(df['salary_gross'] == False) & (df['country_name'] == 'Украина'), 'salary_from'] = df['salary_from'] / 0.82
  df.loc[(df['salary_gross'] == False) & (df['country_name'] == 'Грузия'), 'salary_from'] = df['salary_from'] / 0.8

def report(df: pd.DataFrame, y_test: list, y_pred: np.array, col: str) -> Union[List, pd.DataFrame]:
  """
  Создаём метод, который создаёт регрессионный репорт для моделей, классифицирующих сферу/пециализацию
  Аргументы:
  df - датасет со всем массивом данных
  y_test - датасет с тестовой выборкой
  y_pred - датасет с предсказанными сферами/специализациями
  col - название столбца, по которому происходит группировка: либо 'prof_area', либо 'specialization'
  Возвращает:
  regression_report - репорт с MAE, средним и стандартным отклонением salary_from по сферам и в совокупности
  salary - репорт с MAE, средним и стандартным отклонением salary_from по сферам и в совокупности, где хранятся индексы (сферы)
  """
  y_valid, y_test, y_pred_valid, y_pred = train_test_split(y_test, y_pred, test_size=0.5, random_state=42)
  salary_valid = df.loc[y_valid.index, [col, 'salary_from']].groupby([col]).mean()
  salary_groupped_prof_area = df.loc[y_test.index, [col, 'salary_from']].groupby([col]).mean()
  salary_groupped_prof_area_std = df.loc[y_test.index, [col, 'salary_from']].groupby([col]).std()
  salary_pred = salary_valid.loc[y_pred]
  salary_test = df.loc[y_test.index, 'salary_from']
  salary = pd.DataFrame()
  salary['y_pred'] = y_pred
  salary['test'] =  list(salary_test)
  salary['pred'] = list(salary_pred['salary_from'])
  salary['true'] = list(df.loc[y_test.index, col])
  salary = salary.dropna()
  regression_report = []
  for area in salary['true'].unique():
    regression_report.append([round(mean_absolute_error(salary['pred'][salary['true'] == area], salary['test'][salary['true'] == area]), 1),
                              round(mean_absolute_percentage_error(salary['pred'][salary['true'] == area], salary['test'][salary['true'] == area]), 1),
    round(float(salary_groupped_prof_area.loc[area]), 1), round(float(salary_groupped_prof_area_std.loc[area]), 1)])
  return regression_report, salary


def decrease_specializations(df: pd.DataFrame, specializations: Dict, x: str) -> str:
  """
  Создаём метод, которые вместо наименее популярных специализаций пишет "Другое"
  Аргумент:
  df - датасет со всем массивом данных
  specializations -
  х - специализация
  Возвращает:
  х - специализация
  """
  try:
    if specializations[x]/len(df) < 0.01:
      return 'Другое'
    else:
      return x
  except:
    return x

def report_regression(df: pd.DataFrame, y_test: pd.DataFrame, y_pred: np.array, col: str) -> Union[List, pd.DataFrame]:
  """
  Создаём метод, который создаёт регрессионный репорт для моделей, прогнозирующих з/п
  Аргументы:
  df - датасет со всем массивом данных
  y_test - датасет с тестовой выборкой
  y_pred - датасет с прогнозом з/п
  col - название столбца, по которому происходит группировка: либо 'prof_area', либо 'specialization'
  Возвращает:
  regression_report - репорт с MAE, средним и стандартным отклонением salary_from по сферам и в совокупности
  salary - репорт с MAE, средним и стандартным отклонением salary_from по сферам и в совокупности, где хранятся индексы (сферы)
  """
  salary_groupped_prof_area = df.loc[y_test.index, [col, 'salary_from']].groupby([col]).mean()
  salary_groupped_prof_area_std = df[[col, 'salary_from']].groupby([col]).std()
  salary_test = df.loc[y_test.index, 'salary_from']
  salary = pd.DataFrame()
  salary['test'] =  list(salary_test)
  salary['pred'] = list(y_pred)
  salary['true'] = list(df.loc[y_test.index, col])
  regression_report = []
  for area in salary['true'].unique():
    regression_report.append([round(mean_absolute_error(salary['pred'][salary['true'] == area], salary['test'][salary['true'] == area]), 1),
                              round(mean_absolute_percentage_error(salary['pred'][salary['true'] == area], salary['test'][salary['true'] == area]), 1),
    round(float(salary_groupped_prof_area.loc[area]), 1), round(float(salary_groupped_prof_area_std.loc[area]), 1)])
  regression_report.append([round(mean_absolute_error(salary['pred'], salary['test']), 1),
                            round(mean_absolute_percentage_error(salary['pred'], salary['test']), 1),
    round(float(df.loc[y_test.index, 'salary_from'].mean()), 1), round(float(df['salary_from'].std()), 1)])
  return regression_report, salary

def specialization(df: pd.DataFrame, y_pred: str) -> Union[pd.DataFrame, pd.DataFrame]:
  """
  Создаём метод, который создаёт отчёты (классификационный и регрессионный) для моделей, классифицирующих специализацию
  Аргументы:
  df - датасет со всем массивом данных, который использовался в модели
  y_pred - название файла pkl, который содержит предсказанные значения на тестовой выборке
  Возвращает:
  report_class - классификационный отчёт
  regression_report - регрессионный отчёт
  """
  y_pred = joblib.load(y_pred)
  df = df[~df['specialization'].isnull()]
  specializations = dict()
  df['specializations_name'].apply(lambda x: eda_utils.fill_prof_area(specializations, eval(x)));
  df['specialization'] = df['specialization'].apply(lambda x: decrease_specializations(df, specializations, x))
  y_train, y_test = train_test_split(df['specialization'], test_size=0.2, random_state=42)
  report_class = pd.DataFrame(metrics.classification_report(y_test, y_pred, output_dict=True)).T
  regression_report, salary = report(df=df, y_test=y_test, y_pred=y_pred, col='specialization')
  regression_report = pd.DataFrame(regression_report)
  regression_report.columns = ['MAE', 'MAPE','salary_from_mean', 'salary_from_std']
  regression_report.index = salary['true'].unique()
  return report_class, regression_report

def prof_area(df: pd.DataFrame, y_pred: str) -> Union[pd.DataFrame, pd.DataFrame]:
  """
  Создаём метод, который создаёт отчёты (классификационный и регрессионный) для моделей, классифицирующих сферу
  Аргументы:
  df - датасет со всем массивом данных, который использовался в модели
  y_pred - название файла pkl, который содержит предсказанные значения на тестовой выборке
  Возвращает:
  report_class - классификационный отчёт
  regression_report - регрессионный отчёт
  """
  y_pred = joblib.load(y_pred)
  y_train, y_test = train_test_split(df['prof_area'], test_size=0.2, random_state=42)
  report_class = pd.DataFrame(metrics.classification_report(y_test, y_pred, output_dict=True)).T
  regression_report, salary = report(df=df, y_test=y_test, y_pred=y_pred, col='prof_area')
  regression_report = pd.DataFrame(regression_report)
  regression_report.columns = ['MAE', 'MAPE','salary_from_mean', 'salary_from_std']
  regression_report.index = salary['true'].unique()
  return report_class, regression_report

def regression(df: pd.DataFrame, y_pred: str) -> pd.DataFrame:
  """
  Создаём метод, который создаёт отчёты (классификационный и регрессионный) для моделей, прогнозирующих з/п
  Аргументы:
  df - датасет со всем массивом данных, который использовался в модели
  y_pred - название файла pkl, который содержит предсказанные значения на тестовой выборке
  Возвращает:
  regression_report - регрессионный отчёт
  """
  df = df[['raw_description', 'salary_from', 'prof_area']].dropna()
  y_pred = joblib.load(y_pred)
  y_train, y_test = train_test_split(df['salary_from'], test_size=0.2, random_state=42)
  col = 'prof_area'
  salary_groupped_prof_area = df.loc[y_test.index, [col, 'salary_from']].groupby([col]).mean()
  salary_groupped_prof_area_std = df.loc[y_test.index, [col, 'salary_from']].groupby([col]).std()
  salary_test = df.loc[y_test.index, 'salary_from']
  salary = pd.DataFrame()
  salary['test'] =  list(salary_test)
  salary['pred'] = list(y_pred)
  salary['true'] = list(df.loc[y_test.index, col])
  regression_report = []
  for area in salary['true'].unique():
    regression_report.append([round(mean_absolute_error(salary['pred'][salary['true'] == area], salary['test'][salary['true'] == area]), 1),
                              round(mean_absolute_percentage_error(salary['pred'][salary['true'] == area], salary['test'][salary['true'] == area]), 1),
    round(float(salary_groupped_prof_area.loc[area]), 1), round(float(salary_groupped_prof_area_std.loc[area]), 1)])
  regression_report = pd.DataFrame(regression_report)
  regression_report.columns = ['MAE', 'MAPE','salary_from_mean', 'salary_from_std']
  regression_report.index = salary['true'].unique()
  return regression_report

class mean_vectorizer(object):

  def __init__(self, word2vec: Dict[str, float]):
    self.word2vec = word2vec
    self.dim = len(next(iter(word2vec.values())))

  def fit(self):
    return self

  def transform_one_sentence(self, sentence: str, idf_w: Dict[str, float]) -> np.ndarray:
    res = np.zeros(self.dim)
    denominator = 0
    for word in sentence.split():
      vect = self.word2vec[word] if word in self.word2vec else np.zeros(self.dim)
      curr_idf_weight = idf_w.get(word, 1)
      res += vect * curr_idf_weight
      denominator += curr_idf_weight
    return res / denominator

  def transform(self, X: pd.Series, idf_w: Dict[str, float]):
    return np.array([self.transform_one_sentence(text, idf_w) for text in X])

def cv_and_predict(
          df_train,
          df_test,
          train_y,
          model_kf,
          n_splits=12,
          random_state=42,
          verbose=True,
  ):
    """
    Функция для кросс-валидации и предикта на тест

    :param df_train: Трейн-датафрейм
    :param df_test: Тест-датафрейм
    :param train_y: Ответы на трейн
    :param model_kf: Модель, которую мы хотим учить
    :param n_splits: Количество сплитов для KFold
    :param random_state: random_state для KFold
    :param verbose: Делаем ли print'ы

    :return: pred_test: Предсказания на тест; oof_df: OOF предсказания
    """
    kf = KFold(n_splits=n_splits, shuffle=True, random_state=random_state)
    # В датафрейме oof_df будут храниться настоящий таргет трейна и OOF предсказания на трейн.
    # Инициализируем prediction_oof нулями и будем заполнять предсказаниями в процессе валидации
    oof_df = pd.DataFrame()
    oof_df["target"] = train_y
    oof_df["prediction_oof"] = np.zeros(oof_df.shape[0])
    # Список с метриками по фолдам
    metrics = []
    # Предсказания на тест. Инициализируем нулями и будем заполнять предсказаниями в процессе валидации.
    # Наши предсказания будут усреднением n_splits моделей
    pred_test = np.zeros(df_test.shape[0])
    # Кросс-валидация
    for i, (train_index, valid_index) in enumerate(kf.split(df_train, train_y)):
      if verbose:
        print(f"fold_{i} started")

      X_train = df_train[train_index]
      y_train = train_y[train_index]
      X_valid = df_train[valid_index]
      y_valid = train_y[valid_index]
      model_kf.fit(X_train, y_train)
      prediction = model_kf.predict(df_test)
      pred_test += prediction / n_splits
      prediction_kf = model_kf.predict(X_valid)

      oof_df.loc[valid_index, "prediction_oof"] = prediction_kf

      cur_metric = mean_absolute_error(y_valid, prediction_kf)
      metrics.append(cur_metric)
      if verbose:
        print(f"metric_{i}: {cur_metric}")
        print()
        print("_" * 100)
        print()
    metric_OOF = mean_absolute_error(train_y, oof_df["prediction_oof"])

    if verbose:
      print(f"metric_OOF: {metric_OOF}")
      print(f"metric_AVG: {np.mean(metrics)}")
      print(f"metric_std: {np.std(metrics)}")
      print()
      print("*" * 100)
      print()

    return pred_test, oof_df, metric_OOF

