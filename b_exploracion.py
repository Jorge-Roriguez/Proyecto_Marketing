# -------------------------- Librerias necesarias ---------------------------------------------
# Datos 
import numpy as np
import pandas as pd
import sqlite3 as sql
import datetime

# Gráficos 
import plotly.graph_objs as go 
import plotly.express as px
import matplotlib.pyplot as plt

# Preprocesamiento 
from mlxtend.preprocessing import TransactionEncoder

#Librerías para actualizar archivo a_funciones cuando se hagan cambios
import importlib 
import a_funciones as funciones
importlib.reload(funciones) 


# -------------------------- Creamos conexión con SQL ----------------------------------------
conn = sql.connect('data\\db_movies') 
cur = conn.cursor() 

# Para ejecutar archivo de preprocesamiento de datos 
# funciones.ejecutar_sql('Preprocesamiento.sql', cur)

# ------------------------- Verificamos tablas en db ----------------------------------------
cur.execute("Select name from sqlite_master where type='table'") ### consultar bases de datos
cur.fetchall()

# ------------------------- Leemos tablas como DataFrames -----------------------------------
ratings = pd.read_sql("SELECT * FROM ratings_1", conn)
movies = pd.read_sql("SELECT * FROM movies_1", conn)
df_full = pd.read_sql("SELECT * FROM ratings_final", conn)

# Preprocesamiento de la tabla movies - generación de dummies 

genres=movies['genres'].str.split('|')
te = TransactionEncoder()
genres = te.fit_transform(genres)
genres = pd.DataFrame(genres, columns = te.columns_)
genres  = genres.astype(int)
movies = movies.drop(['genres'], axis = 1) 
movies =pd.concat([movies, genres],axis=1)
movies


# ------------------------ Exploración tablas ------------------------------------------------
ratings.head()
ratings.info()
ratings[['rating','year','month','day']].describe() # Solamente rating y date vale la pena analizar

movies.info()

# ------------------- Descripción tabla ratings ---------------------------------------------

# Conteo por cada rating 
rc = pd.read_sql("""SELECT rating, COUNT(*) as conteo 
                            FROM ratings
                            GROUP BY rating
                            ORDER BY conteo DESC""", conn)

data  = go.Bar( x = rc.rating, y = rc.conteo, text = rc.conteo, textposition = "outside")
Layout = go.Layout(title = "Conteo de ratings", xaxis = {'title':'Rating'}, yaxis = {'title':'Conteo'})
go.Figure(data, Layout)

# Número de películas calificadas por cada usuario 
cu = pd.read_sql("""SELECT userId, COUNT(*) AS conteo_user
                    FROM ratings
                    GROUP BY userId
                    ORDER BY conteo_user ASC""", conn)

fig  = px.histogram(cu, x = 'conteo_user', title = 'Frecuencia de numero de calificaciones por usario')
fig.show() 

# Promedio de calificación por usuario 
mu = pd.read_sql("""
            SELECT userId, AVG(rating) AS promedio_calificacion 
            FROM ratings 
            GROUP BY userId
            ORDER BY promedio_calificacion ASC""", conn)

fig  = px.histogram(mu, x = 'promedio_calificacion', title = 'Promedio de calificaciones de los usuarios')
fig.show() 

# Promedio de calificaciones por cada película 
mm = pd.read_sql(""" 
                SELECT movieId, avg(rating) AS promedio_calificacion 
                FROM ratings 
                GROUP BY movieId
                ORDER BY promedio_calificacion ASC""", conn)

# Número de calificaciones que tiene cada película 
mn = pd.read_sql("""
                SELECT movieId, COUNT(rating) AS numero_calificacion 
                FROM ratings 
                GROUP BY movieId
                ORDER BY numero_calificacion ASC""", conn)

joined_mn = pd.merge(mm,mn, on='movieId', how ='inner')
joined_mn

# Actividad de los usuarios por cada mes en el último año 
df_2018 = ratings[ratings['year'] == 2018]
df_2018 = pd.DataFrame(df_2018.groupby('month')['rating'].size())
df_2018 = df_2018.reset_index()
df_2018

fig = px.line(df_2018, x = "month", y = "rating", title = 'Actividad de los usuarios por mes año 2018')
fig.update_layout(xaxis_title = 'Mes', yaxis_title = 'Número de Calificaciones realizadas')
fig.show()

# Actividad de los usuarios por cada mes año 2017
df_2017 = ratings[ratings['year'] == 2017]
df_2017 = pd.DataFrame(df_2017.groupby('month')['rating'].size())
df_2017 = df_2017.reset_index()
df_2017

fig = px.line(df_2017, x = "month", y = "rating", title = 'Actividad de los usuarios por mes año 2017')
fig.update_layout(xaxis_title = 'Mes', yaxis_title = 'Número de Calificaciones realizadas')
fig.show()
