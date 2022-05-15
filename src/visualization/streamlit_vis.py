import streamlit as st
import joblib
import scipy.sparse as sp
import seaborn as sns
import pymorphy2
import re

st.cache(suppress_st_warning=True)
morph = pymorphy2.MorphAnalyzer()
def lemmatize(text):
  """
  Создаём метод, который лемматизирует текст.
  Аргумент:
  text - текст, который нужно лемматизировать
  Возвращает:
  res - лемматизированный текст
  """
  try:
      words = re.split(r'\W+', text) # разбиваем текст на слова
  except:
    return text
  res = str()
  for word in words:
      p = morph.parse(word)[0]
      res += (p.normal_form) + ' '
  return res

sns.set()

st.title('Прогнозирование нижней вилки заработной платы по описанию вакансии')
full = st.text_area("Описание вакансии:")
resp = st.text_area("Обязанности:")
con = st.text_area("Условия:")
button = st.button('Спрогнозировать нижнюю вилку зарплаты')
tfidf_con = joblib.load('lem_desc_con_tfidf.pkl')
tfidf_resp = joblib.load('lem_desc_resp_tfidf.pkl')
tfidf_full = joblib.load('lem_desc_tfidf.pkl')
model = joblib.load('model.pkl')
# sns.set_theme(style="darkgrid")
if button:
    full = lemmatize(full)
    resp = lemmatize(resp)
    con = lemmatize(con)
    full = tfidf_full.transform([full])
    resp = tfidf_resp.transform([resp])
    con = tfidf_con.transform([con])
    features = sp.hstack((full, resp, con))
    y_pred = model.predict(features)
    st.write('{:,.0f} {}'.format(float(y_pred), 'руб. до вычета налогов'))
    st.write('{:,.0f} {}'.format(float(y_pred)*0.87, 'руб. на руки'))