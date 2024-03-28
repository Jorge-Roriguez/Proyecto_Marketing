# Datos 
import numpy as np
import pandas as pd
import sqlite3 as sql
import datetime


# Gráficos 
import plotly.graph_objs as go 
import plotly.express as px

#Librerías para actualizar archivo a_funciones cuando se hagan cambios
import importlib 
import a_funciones as funciones
importlib.reload(funciones) 


# -------------------------- Creamos conexión con SQL ----------------------------------------#
conn=sql.connect('data\\db_movies') 
cur=conn.cursor() 

# ------------------------- Verificamos tablas en db ----------------------------------------#
cur.execute("Select name from sqlite_master where type='table'") ### consultar bases de datos
cur.fetchall()

# ------------------------- Leemos tablas como DataFrames -----------------------------------#
ratings = pd.read_sql("SELECT * FROM ratings", conn)
movies = pd.read_sql("SELECT * FROM movies", conn)

# Pasamos de formato UNIX a datetime para entender los datos
ratings['date'] = pd.to_datetime(ratings['timestamp'], unit='s') 


# ------------------------ Exploración tablas ------------------------------------------------#

ratings.head()
ratings.info()
ratings[['rating','date']].describe() # Solamente rating y date vale la pena analizar

movies.head()
movies.info()

# ------------------- Descripción tabla ratings ---------------------------------------------#

# Borramos la columna timestamp, ya la tenemos convertida como date 
ratings.drop([ 'timestamp'], axis = 1, inplace = True)
ratings.head()

# Conteo de los ratings que hay en total
rc = pd.read_sql("""SELECT rating, COUNT(*) as conteo 
                            FROM ratings
                            GROUP BY rating
                            ORDER BY conteo DESC""", conn)

data  = go.Bar( x=rc.rating,y=rc.conteo, text=rc.conteo, textposition="outside")
Layout=go.Layout(title="Conteo de ratings",xaxis={'title':'Rating'},yaxis={'title':'Conteo'})
go.Figure(data,Layout)

# Número de películas calificadas por cada usuario 

cu = pd.read_sql("""SELECT userId, COUNT(*) AS conteo_user
                    FROM ratings
                    GROUP BY userId
                    ORDER BY conteo_user ASC""", conn)

fig  = px.histogram(cu, x= 'conteo_user', title= 'Frecuencia de numero de calificaciones por usario')
fig.show() 



# ----------------- Descripción tabla movies 

