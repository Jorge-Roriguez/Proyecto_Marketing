# Librerías de ciencia de datos 
import numpy as np
import pandas as pd
import sqlite3 as sql

# Librerías para preprocesamiento 
from sklearn.preprocessing import MinMaxScaler

# Librerías para análisis interactivo 
from ipywidgets import interact 
from sklearn import neighbors 
import joblib

# Paquete para sistemas de recomendación surprise 
from surprise import Reader, Dataset
from surprise.model_selection import cross_validate, GridSearchCV
from surprise import KNNBasic, KNNWithMeans, KNNWithZScore, KNNBaseline
from surprise.model_selection import train_test_split

# -------------------------- Creamos conexión con SQL ---------------------------------------
conn = sql.connect('data\\db_movies') 
cur = conn.cursor()

#######################################################################
#### Sistema de recomendación filtro colaborativo #######################
#######################################################################

# Obtener datos; se filtran los mayores a 0
rat = pd.read_sql('select * from ratings_final where rating>0', conn)

# Definir escala
Reader = Reader(rating_scale=(1,5))

# Leer datos con suprise
data = Dataset.load_from_df(rat[['userId','movieId','rating']], Reader)

# Modelos 
models  = [KNNBasic(),KNNWithMeans(),KNNWithZScore(),KNNBaseline()] 
results = {}

# Probar modelos
model = models[1]
for model in models:
 
    CV_scores = cross_validate(model, data, measures=["MAE","RMSE"], cv=5, n_jobs=-1)  
    
    result = pd.DataFrame.from_dict(CV_scores).mean(axis=0).\
             rename({'test_mae':'MAE', 'test_rmse': 'RMSE'})
    results[str(model).split("algorithms.")[1].split("object ")[0]] = result

performance_df = pd.DataFrame.from_dict(results).T
performance_df.sort_values(by='RMSE')

# Se selecciono el KNNBasic porque tiene mejores metricas en "MAE Y RMSE"

# Definir la grilla de parámetros para la búsqueda de hiperparámetros
param_grid = {
    'sim_options': {
        'name': ['msd', 'cosine'],
        'min_support': [5],
        'user_based': [False, True]
    }
}

gridsearchKNNBasic = GridSearchCV(KNNBasic, param_grid, measures=['rmse'], cv=2, n_jobs=-1)

gridsearchKNNBasic.fit(data)

gridsearchKNNBasic.best_params["rmse"]
gridsearchKNNBasic.best_score["rmse"]
gs_model=gridsearchKNNBasic.best_estimator['rmse'] 

# Entrenar con todos los datos, y realizar predicciones con el modelo afinado
trainset = data.build_full_trainset()
model1 = gs_model.fit(trainset)
predset = trainset.build_anti_testset()
len(predset)
predictions = gs_model.test(predset)

# Crear base; peliculas no vistas por usuario + calificacion predicha 
predictions_df = pd.DataFrame(predictions) 
predictions_df.shape
predictions_df.head()
predictions_df['r_ui'].unique()
predictions_df.sort_values(by='est',ascending=False)

# Función para recomendar 11 películas a un usuario específico
def recomendaciones(user_id,n_recomend=11):
    
    predictions_userID = predictions_df[predictions_df['uid'] == user_id].\
                    sort_values(by="est", ascending = False).head(n_recomend)

    recomendados = predictions_userID[['iid','est']]
    recomendados.to_sql('reco',conn,if_exists="replace")
    
    mov = pd.read_sql('''select a.*, b.titulo from reco a left join movies_1 b on a.iid=b.movieId''', conn)
    return mov

# Obtener y mostrar las 11 peliculas recomendadas al usuario 50
peliculas = recomendaciones(user_id=50, n_recomend=11)
peliculas

