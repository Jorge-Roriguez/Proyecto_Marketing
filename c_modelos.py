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


# -------------------------- Creamos conexión con SQL ---------------------------------------
conn = sql.connect('data\\db_movies') 
cur = conn.cursor() 

# ------------------------- Verificamos tablas en db ----------------------------------------
cur.execute("Select name from sqlite_master where type='table'")  
cur.fetchall()

# ------------------------- Leemos tablas como DataFrames -----------------------------------
ratings = pd.read_sql("SELECT * FROM ratings", conn)
movies = pd.read_sql("SELECT * FROM movies", conn)


# -------------------------------------------------------------------------------------------
# ------------------------- Sistemas de recomendación por valoración (popularidad) ------------------------ 
# -------------------------------------------------------------------------------------------

# Películas que han calificado > 4 en promedio y el número de personas que las han calificado es mayor a 70
m1 = pd.read_sql("""
                SELECT movieId, AVG(rating) AS promedio_calificacion, COUNT(CASE WHEN rating > 4 THEN 1 END) AS num_personas_calificaron
                FROM ratings 
                GROUP BY movieId
                HAVING promedio_calificacion > 4.2 AND num_personas_calificaron >= 70
                ORDER BY num_personas_calificaron ASC""", conn)

joined_df = pd.merge(m1, movies, how = 'inner', on = 'movieId')
fig = px.pie(joined_df, values = 'num_personas_calificaron', names = 'title', 
             title = 'Top 10 películas mejor calificadas')
fig.show()

# Películas que han calificado mayor a 4 en promedio para el último año (2018)
m2 = pd.read_sql("""
                SELECT movieId, AVG(rating) AS promedio_calificacion, COUNT(CASE WHEN rating > 4 THEN 1 END) AS num_personas_calificaron
                FROM ratings 
                GROUP BY movieId
                HAVING promedio_calificacion > 4.2 AND num_personas_calificaron >= 70
                ORDER BY num_personas_calificaron ASC
                 """, conn)



# -------------------------------------------------------------------------------------------
# ------------------------- Sistemas de recomendación por contenido ------------------------- 
# -------------------------------------------------------------------------------------------

# Se trabajo con esta tabla dado que las comparaciónes ahora son por contenido no por rating 
movies.info()
movies = movies.drop('movieId', axis = 1) # No se necesita el ID 

# Cantidad total de títulos y géneros
movies['title'].nunique()
movies['genres'].nunique()

# Convertimos a dummies
movies_dum = pd.get_dummies(movies, dtype = int)
movies_dum.shape # Dimensión de la tabla

# Peliculas recomendadas a partir de una película 
pelicula = 'Toy Story (1995)'
id_pelicula = movies[movies['title'] == pelicula].index.values.astype(int)[0]
pelicula_similar = movies_dum.corrwith(movies_dum.iloc[id_pelicula,:], axis = 1)
pelicula_similar = pelicula_similar.sort_values(ascending = False)
top_similar = pelicula_similar.to_frame(name = 'correlación').iloc[0:12,]
top_similar['title'] = movies['title']
top_similar

