from sklearn.base import BaseEstimator
from sklearn.feature_extraction.text import TfidfVectorizer
import pickle
import scipy.sparse as sp
from category_encoders.target_encoder import TargetEncoder
import pandas as pd
import numpy as np

class MyMetaModel(BaseEstimator):
    def __init__(self, model1, meta_model, model_name: str):
        self.meta_model = meta_model
        self.model_name = model_name
        self.model1 = model1

    def tfidf(self, text_features_train, text_features_valid, text_features_test):
        tfidf1 = TfidfVectorizer(sublinear_tf=True, min_df=5,
                                ngram_range=(1, 2),
                                stop_words={'russian', 'english'}, max_features=10000)
        tfidf1.fit(text_features_train['raw_description'])
        features1 = tfidf1.transform(text_features_train['raw_description'])
        features_valid1 = tfidf1.transform(text_features_valid['raw_description'])
        features_test1 = tfidf1.transform(text_features_test['raw_description'])

        tfidf2 = TfidfVectorizer(sublinear_tf=True, min_df=5,
                                 ngram_range=(1, 2),
                                 stop_words={'russian', 'english'}, max_features=10000)
        tfidf2.fit(text_features_train['lem_desc_resp'])
        features2 = tfidf2.transform(text_features_train['lem_desc_resp'])
        features_valid2 = tfidf2.transform(text_features_valid['raw_description'])
        features_test2 = tfidf2.transform(text_features_test['raw_description'])
        tfidf3 = TfidfVectorizer(sublinear_tf=True, min_df=5,
                                 ngram_range=(1, 2),
                                 stop_words={'russian', 'english'}, max_features=10000)
        tfidf3.fit(text_features_train['lem_desc_con'])
        features3 = tfidf3.transform(text_features_train['lem_desc_con'])
        features_valid3 = tfidf3.transform(text_features_valid['raw_description'])
        features_test3 = tfidf3.transform(text_features_test['raw_description'])

        text_features_train = sp.hstack((features1, features2, features3))
        text_features_valid = sp.hstack((features_valid1, features_valid2, features_valid3))
        text_features_test = sp.hstack((features_test1, features_test2, features_test3))

        pickle.dump(tfidf1.vocabulary_, open(f"../models/{self.model_name}/lem_desc_tfidf.pkl", "wb"))
        pickle.dump(tfidf2.vocabulary_, open(f"../models/{self.model_name}/lem_desc_resp_tfidf.pkl", "wb"))
        pickle.dump(tfidf3.vocabulary_, open(f"../models/{self.model_name}/lem_desc_con_tfidf.pkl", "wb"))

        return text_features_train, text_features_valid, text_features_test

    def encoding(self, nontext_features_train, nontext_features_valid, nontext_features_test, y_train):
        encoder = TargetEncoder()
        encoder.fit(nontext_features_train['prof_area'], y_train)
        features1 = encoder.transform(nontext_features_train['prof_area'], y_train)
        features_valid1 = encoder.transform(nontext_features_valid['prof_area'])
        features_test1 = encoder.transform(nontext_features_test['prof_area'])

        encoder = TargetEncoder()
        encoder.fit(nontext_features_train['areas_name'], y_train)
        features2 = encoder.transform(nontext_features_train['areas_name'], y_train)
        features_valid2 = encoder.transform(nontext_features_valid['areas_name'])
        features_test2 = encoder.transform(nontext_features_test['areas_name'])

        encoder = TargetEncoder()
        encoder.fit(nontext_features_train['specialization'], y_train)
        features3 = encoder.transform(nontext_features_train['specialization'], y_train)
        features_valid3 = encoder.transform(nontext_features_valid['specialization'])
        features_test3 = encoder.transform(nontext_features_test['specialization'])

        nontext_features_train = np.concatenate([features1, features2, features3], axis=1)
        nontext_features_valid = np.concatenate([features_valid1, features_valid2, features_valid3], axis=1)
        nontext_features_test = np.concatenate([features_test1, features_test2, features_test3], axis=1)

        return nontext_features_train, nontext_features_valid, nontext_features_test

    def predict_first(self, text_features_train, text_features_valid, text_features_test, y_train):

        self.model1.fit(text_features_train, y_train)
        y_pred1_valid = self.model1.predict(text_features_valid)
        y_pred1_test = self.model1.predict(text_features_test)

        return y_pred1_test, y_pred1_valid

    def fit(self, y_pred1_valid, y_valid, features_valid):

        self.meta_model.fit(np.concatenate([pd.DataFrame(y_pred1_valid), features_valid], axis=1), y_valid)

        return self

    def predict(self, y_pred1_test, features_test):

        y_final_predict = self.meta_model.predict(np.concatenate([pd.DataFrame(y_pred1_test), features_test], axis=1))

        return y_final_predict