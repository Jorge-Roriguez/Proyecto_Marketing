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
import seaborn as sns

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

# ------------------------- Preprocesamiento para próxmios sistemas ------------------------- 
genres = df_full['genres'].str.split('|')
te = TransactionEncoder()
genres = te.fit_transform(genres)
genres = pd.DataFrame(genres, columns = te.columns_)
genres  = genres.astype(int)
df_final = df_full.drop(['genres'], axis = 1) 
df_final = pd.concat([df_final, genres], axis = 1)


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
fig = px.bar(joined_df, x = 'num_personas_calificaron', y = 'titulo', 
             title = 'Top 10 películas mejor calificadas')
fig.show()


# Películas basadas en los géneros más populares
df_generos = df_final[df_final['rating'] >= 4.0]
df_generos.drop(['userId', 'movieId', 'year', 'month', 'day', 'titulo', 'estreno', '(no genres listed)'], axis = 1, inplace =  True)
df_generos = pd.DataFrame(df_generos.sum())
df_generos = pd.DataFrame(
    {'Género':['Action','Adventure','Animation','Children','Comedy','Crime','Documentary','Drama','Fantasy','Film-Noir','Horror','IMAX','Musical','Mystery','Romance','Sci-Fi','Thriller','War','Western'],	
    'Vistas': [13891, 11569, 3652, 4067, 16880, 9077, 729, 22925, 5545, 588, 2892, 2130, 2049, 4124, 8668, 8011, 12536, 2994, 996]}
)

df_generos = df_generos.sort_values(ascending = False, by = 'Vistas').head(10)
sns.barplot(x = 'Género', y = 'Vistas', data =  df_generos, hue = 'Género')
plt.title('Popularidad de los géneros')
plt.xticks(rotation = 40)
plt.show()


# -------------------------------------------------------------------------------------------
# ---------- Sistemas de recomendación por contenido (un solo producto) --------------------- 
# -------------------------------------------------------------------------------------------

# Tratamiento de datos para este sistema 
genres = movies['genres'].str.split('|')
te = TransactionEncoder()
genres = te.fit_transform(genres)
genres = pd.DataFrame(genres, columns = te.columns_)
genres  = genres.astype(int)
movies_1 = movies.drop(['genres'], axis = 1, inplace = True) 
movies_1 =pd.concat([movies, genres], axis = 1)

# Se trabajo con esta tabla dado que las comparaciónes ahora son por contenido no por rating 
movies_1.dtypes
movies_1 = movies_1.drop('movieId', axis = 1) # No se necesita el ID
sc = MinMaxScaler()
movies_1[['estreno']] = sc.fit_transform(movies_1[['estreno']]) # Se escala el año
movies_dum = pd.get_dummies(movies_1, dtype = int)

# Convertimos a dummies
movies_dum.shape # Dimensión de la tabla

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


# -------------------------------------------------------------------------------------------
# ---------- Sistemas de recomendación por contenido (Todo lo visto) ------------------------ 
# -------------------------------------------------------------------------------------------


# Vamos a trabajar con el dataframe escalado y con dummies movies_dum 
movies_dum

# Se selecciona un usuario para realizar las recomendaciones 

usuarios = pd.read_sql('SELECT distinct (userId) as user_id from ratings_final',conn)

# Seleccionamos un usuarios para realizar el sistema de recomendación
user_id= 607 
movies
prueba = pd.read_sql('SELECT * FROM ratings_final', conn)
ratings

def recomendar(user_id=list(usuarios['user_id'].value_counts().index)):
    
    # Se seleccionan los ratings del usuario establecido
    ratings = pd.read_sql('SELECT * from ratings_final where userId=:user',conn, params={'user':user_id,})
    
    ###convertir ratings del usuario a array
    ratings_array = ratings['movieId'].to_numpy()
    
    ###agregar la columna de isbn y titulo del libro a dummie para filtrar y mostrar nombre
    movies_dum[['movieId','titulo']]= movies[['movieId','titulo']]
    
    ### filtrar libros calificados por el usuario
    movies_r = movies_dum[movies_dum['movieId'].isin(ratings_array)]
    
    ## eliminar columna nombre e isbn
    movies_r = movies_r.drop(columns=['movieId','titulo'])
    movies_r["indice"] = 1 ### para usar group by y que quede en formato pandas tabla de centroide
    ##centroide o perfil del usuario
    centroide=movies_r.groupby("indice").mean()
    
    
    ### filtrar libros no leídos
    movies_ns = movies_dum[~movies_dum['movieId'].isin(ratings_array)]
    ## eliminbar nombre e isbn
    movies_ns = movies_ns.drop(columns=['movieId','titulo'])
    
    ### entrenar modelo 
    model=neighbors.NearestNeighbors(n_neighbors=11, metric='cosine')
    model.fit(movies_ns)
    dist, idlist = model.kneighbors(centroide)
    
    ids=idlist[0] ### queda en un array anidado, para sacarlo
    recomend_m = movies.loc[ids][['titulo','movieId']]
    leidos = movies[movies['movieId'].isin(ratings_array)][['titulo','movieId']]
    
    return recomend_m

recomendar(609)
