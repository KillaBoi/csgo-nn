from __future__ import division
import csv
import numpy as np
import pickle
import pandas
import database as db
from sklearn.model_selection import cross_val_score
from sklearn.neural_network import MLPClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import GridSearchCV
import itertools

CSV_NAMES = ['wins','elo','score','momentum','vs','rating','ts','outcome']

def search_mlp():
    df = pandas.read_csv('data/training.csv', names=CSV_NAMES)
    array = df.values
    X = array[:,0:-1]
    y = array[:,-1]

    scaler = StandardScaler()
    X = scaler.fit_transform(X)

    params = { 
        'hidden_layer_sizes': [x for x in itertools.product(range(2,75),repeat=2)],
        'activation': ['tanh','relu'],
    }

    mlp = MLPClassifier(early_stopping=True,random_state=0,max_iter=100,solver='adam')
    CV_rfc = GridSearchCV(estimator=mlp,param_grid=params, cv=5, n_jobs=-1, verbose=1)
    CV_rfc.fit(X, y)
    print(round(CV_rfc.best_score_,4)*100)
    print(CV_rfc.best_params_)


def train_mlp():
    df = pandas.read_csv('data/training.csv', names=CSV_NAMES)
    array = df.values
    X = array[:,0:-1]
    y = array[:,-1]

    scaler = StandardScaler()
    X = scaler.fit_transform(X)

    mlp = MLPClassifier(hidden_layer_sizes=(29,67), activation="relu", solver='adam',random_state=0,early_stopping=True,max_iter=500)
    scores = cross_val_score(mlp, X, y, cv=5)
    print(scores)
    print(scores.mean())
    
    mlp.fit(X,y)

    pickle_file = open('model/mlp_model.pkl', 'wb')
    pickle.dump(mlp,pickle_file)
    pickle_file.close()


def main():
    #search_mlp()
    train_mlp()


if __name__ == "__main__":
    main()