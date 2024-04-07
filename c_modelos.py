# -------------------------- Librerias necesarias ------------------------------------------
# Tratamiento de datos 
import numpy as np
import pandas as pd
import sqlite3 as sql
import datetime
from sklearn.preprocessing import MinMaxScaler

# Gráficos 
import plotly.graph_objs as go 
import plotly.express as px
import matplotlib.pyplot as plt

#Librerías para actualizar archivo a_funciones cuando se hagan cambios
import importlib 
import a_funciones as funciones
importlib.reload(funciones) 

# Preprocesamiento 
from mlxtend.preprocessing import TransactionEncoder

#Modelos
from sklearn import neighbors 
from ipywidgets import interact
import joblib

# -------------------------- Creamos conexión con SQL ---------------------------------------
conn = sql.connect('data\\db_movies') 
cur = conn.cursor() 

# ------------------------- Verificamos tablas en db ----------------------------------------
cur.execute("Select name from sqlite_master where type='table'")  
cur.fetchall()

# ------------------------- Leemos tablas como DataFrames -----------------------------------
ratings = pd.read_sql("SELECT * FROM ratings_1", conn)
movies = pd.read_sql("SELECT * FROM movies_1", conn)
df_full = pd.read_sql("SELECT * FROM ratings_final", conn)


# ---------------------------------------------------------------------------------------------------------------------------------------
# ------------------------- Sistemas de recomendación por valoración (popularidad) ------------------------------------------------------
# ---------------------------------------------------------------------------------------------------------------------------------------

# Películas que han calificado > 4 en promedio y el número de personas que las han calificado es mayor a 70
m1 = pd.read_sql("""
                SELECT movieId, AVG(rating) AS promedio_calificacion, COUNT(CASE WHEN rating > 4 THEN 1 END) AS num_personas_calificaron
                FROM ratings 
                GROUP BY movieId
                HAVING promedio_calificacion > 4.2 AND num_personas_calificaron >= 70
                ORDER BY num_personas_calificaron ASC""", conn)

joined_df = pd.merge(m1, movies, how = 'inner', on = 'movieId')
fig = px.pie(joined_df, values = 'num_personas_calificaron', names = 'titulo', 
             title = 'Top 10 películas mejor calificadas')
fig.show()

# Películas que han calificado mayor a 4 en promedio para el último año (2018)

# -------------------------------------------------------------------------------------------
# ------------------------- Sistemas de recomendación por contenido ------------------------- 
# -------------------------------------------------------------------------------------------

# Tratamiento de datos para este sistema 
genres = movies['genres'].str.split('|')
te = TransactionEncoder()
genres = te.fit_transform(genres)
genres = pd.DataFrame(genres, columns = te.columns_)
genres  = genres.astype(int)
movies_1 = movies.drop(['genres'], axis = 1, inplace = True) 
movies_1 =pd.concat([movies, genres], axis = 1)
movies_1

# Se trabajo con esta tabla dado que las comparaciónes ahora son por contenido no por rating 
movies_1.dtypes
movies_1 = movies_1.drop('movieId', axis = 1) # No se necesita el ID
sc = MinMaxScaler()
movies_1[['estreno']] = sc.fit_transform(movies_1[['estreno']]) # Se escala el año
movies_dum = pd.get_dummies(movies_1, dtype = int)

# Convertimos a dummies
movies_dum.shape # Dimensión de la tabla

# Peliculas recomendadas para visualizacion de todas las pelicualas 

def recomendacion(peliculas = list(movies['titulo'])):
    ind_movies = movies[movies['titulo'] == peliculas].index.values.astype(int)[0]
    similar_movies = movies_dum.corrwith(movies_dum.iloc[ind_movies,:], axis = 1)
    similar_movies = similar_movies.sort_values(ascending = False)
    del similar_movies[0]
    top_similar_movies = similar_movies.to_frame(name = "correlación").iloc[0:11,]
    top_similar_movies['titulo'] = movies["titulo"]

    return top_similar_movies

print(interact(recomendacion))


# ------------------------------------------------------------------------------------------------------
# -------------------------Sistema de recomendación basado en contenido KNN, un solo producto visto -----
# ------------------------------------------------------------------------------------------------------

# Entrenar modelo
model = neighbors.NearestNeighbors(n_neighbors = 10, metric = 'cosine')
model.fit(movies_dum)

# Distancias entre las películas
dist, idlist = model.kneighbors(movies_dum)
distancias = pd.DataFrame(dist)
id_list = pd.DataFrame(idlist)

# Sistema de recomendación
def MovieRecommender(movie_name = list(movies['titulo'].value_counts().index)):
    movie_list_name = []
    movie_id = movies[movies['titulo'] == movie_name].index
    movie_id = movie_id[0]
    for newid in idlist[movie_id]:
        movie_list_name.append(movies.loc[newid].titulo)
    return movie_list_name

print(interact(MovieRecommender))