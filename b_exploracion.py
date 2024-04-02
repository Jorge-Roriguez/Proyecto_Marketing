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
ratings = pd.read_sql("SELECT * FROM ratings", conn)
movies = pd.read_sql("SELECT * FROM movies", conn)

# ------------------------ Exploración tablas ------------------------------------------------
ratings.head()
ratings.info()
ratings[['rating','year','month','day']].describe() # Solamente rating y date vale la pena analizar

movies.head()
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

# Actividad de los usuarios en cada mes (ultimos 5 años)
df_m = pd.DataFrame(ratings.groupby('month')['rating'].size())
df_m = df_m.reset_index()
df_m


fig = px.line(df_m, x = "month", y = "rating", title = 'Actividad de los usuarios por mes')
fig.update_layout(xaxis_title = 'Mes', yaxis_title = 'Número de Visitas')
fig.show()
