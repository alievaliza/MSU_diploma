<pre>
1. raw_desc_tfidf_RF_specialization - RandomForestClassifier, классифицирующий specialization features - tfidf над столбцом raw_description (max_features=3500)
2. raw_desc_tfidf_RF_prof_area - RandomForestClassifier, классифицирующий prof_area. features - tfidf над столбцом raw_description (max_features=3500)
3. lem_desc_tfidf_RF_prof_area - RandomForestClassifier, классифицирующий prof_area. features - tfidf над столбцом lem_raw_desc (max_features=3500)

                  					precision    recall  f1-score   support

                                 Автомобильный бизнес       0.83      0.44      0.57       535
                            Административный персонал       0.56      0.53      0.55      1389
                            Банки, инвестиции, лизинг       0.89      0.81      0.85       767
                                         Безопасность       0.88      0.63      0.74       420
Бухгалтерия, управленческий учет, финансы предприятия       0.71      0.78      0.74       798
                                    Высший менеджмент       0.79      0.19      0.31       137
   Государственная служба, некоммерческие организации       0.90      0.52      0.66       123
                                         Добыча сырья       0.84      0.36      0.50       289
                                    Домашний персонал       0.80      0.17      0.28        94
                                              Закупки       0.85      0.21      0.34       157
                                 Инсталляция и сервис       0.90      0.29      0.44        95
         Информационные технологии, интернет, телеком       0.72      0.77      0.74       941
                   Искусство, развлечения, масс-медиа       0.78      0.17      0.27       216
                                     Консультирование       0.89      0.29      0.44       136
                               Маркетинг, реклама, PR       0.73      0.36      0.48       491
                               Медицина, фармацевтика       0.87      0.83      0.85      1009
                                   Наука, образование       0.73      0.62      0.67       301
                             Начало карьеры, студенты       0.77      0.23      0.36       558
                                              Продажи       0.70      0.90      0.79      4542
                     Производство, сельское хозяйство       0.49      0.53      0.51      1441
                                     Рабочий персонал       0.53      0.75      0.62      2221
             Спортивные клубы, фитнес, салоны красоты       0.78      0.20      0.31       264
                                          Страхование       0.89      0.41      0.56        58
                          Строительство, недвижимость       0.68      0.62      0.65      1377
                                 Транспорт, логистика       0.71      0.71      0.71      1768
                         Туризм, гостиницы, рестораны       0.74      0.75      0.74      1122
                      Управление персоналом, тренинги       0.80      0.64      0.71       414
                                               Юристы       0.85      0.64      0.73       208

                                             accuracy                           0.68     21871
                                            macro avg       0.77      0.51      0.58     21871
                                         weighted avg       0.70      0.68      0.66     21871


4. lem_desc_tfidf_RF_specialization - RandomForestClassifier, классифицирующий specialization. features - tfidf над столбцом lem_raw_desc (max_features=3500)
</pre>