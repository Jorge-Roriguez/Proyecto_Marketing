# Librerías de ciencia de datos 
import numpy as np
import pandas as pd
import sqlite3 as sql

# Librerías para preprocesamiento 
from sklearn.preprocessing import MinMaxScaler

#Librerías para análisis interactivo 
from ipywidgets import interact 
from sklearn import neighbors 
import joblib

####Paquete para sistemas de recomendación surprise
###Puede generar problemas en instalación local de pyhton. Genera error instalando con pip
#### probar que les funcione para la próxima clase 

from surprise import Reader, Dataset
from surprise.model_selection import cross_validate, GridSearchCV
from surprise import KNNBasic, KNNWithMeans, KNNWithZScore, KNNBaseline
from surprise.model_selection import train_test_split