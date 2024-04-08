# Librerías de ciencia de datos 
import numpy as np
import pandas as pd
import sqlite3 as sql
import a_funciones as fn
import openpyxl

# Para preprocesamiento
from sklearn.preprocessing import MinMaxScaler
from mlxtend.preprocessing import TransactionEncoder


# Sistemas de recomendación 
from sklearn import neighbors


# ---------------------------------------------------------------------------------------------------------------------------------------
# --------------------------------------- Preprocesamiento  -----------------------------------------------------------------------------
# ---------------------------------------------------------------------------------------------------------------------------------------

def preprocesar():

    # Nos conectamos a la base de datos
    conn = sql.connect("C:\\Users\\ESTEBAN\\Desktop\\Proyecto_Marketing\\Data\\db_movies")
    cur = conn.cursor()

    # fn.ejecutar_sql("C:\\Users\\ESTEBAN\\Desktop\\Proyecto_Marketing\\Preprocesamiento.sql", cur)

    # Llevamo datos a Python (estos serían los que cambian con periodicidad semanal en nuestro diseño de la solución)
    movies =pd.read_sql('select * from movies_1', conn )
    ratings=pd.read_sql('SELECT * from ratings_final', conn)
    usuarios=pd.read_sql('select distinct (userId) as user_id from ratings_final',conn)

    # Transformación de datos crudos 
    movies['estreno']= movies.estreno.astype('int')
    
    # Escalamos para que el año esté en el mismo rango 
    sc=MinMaxScaler()
    movies[["estreno_escalado"]]=sc.fit_transform(movies[['estreno']])

    # Eliminamos filas que no vamos a utilizar
    genres = movies['genres'].str.split('|')
    te = TransactionEncoder()
    genres = te.fit_transform(genres)
    genres = pd.DataFrame(genres, columns = te.columns_)
    genres  = genres.astype(int)
    movies_1 = movies.drop(['genres'], axis = 1, inplace = True) 
    movies_1 =pd.concat([movies, genres], axis = 1)

    movies_1 = movies_1.drop('movieId', axis = 1) # No se necesita el ID
    sc = MinMaxScaler()
    movies_1[['estreno']] = sc.fit_transform(movies_1[['estreno']]) # Se escala el año
    movies_dum = pd.get_dummies(movies_1, dtype = int)

    return movies_dum, movies, conn, cur


# -------------------------------------------------------------------------------------------
# ---------- Sistemas de recomendación por contenido (Todo lo visto) ------------------------ 
# -------------------------------------------------------------------------------------------

def recomendar(user_id):
    
    movies_dum, movies, conn, cur= preprocesar()
    
    ratings=pd.read_sql('SELECT * from ratings_final where userId=:user',conn, params={'user':user_id})
    ratings_array =ratings['movieId'].to_numpy()
    movies_dum[['movieId','titulo']]= movies[['movieId','titulo']]
    movies_r = movies_dum[movies_dum['movieId'].isin(ratings_array)]
    movies_r = movies_r.drop(columns=['movieId','titulo'])
    movies_r["indice"] = 1 
    centroide=movies_r.groupby("indice").mean()
    
    
    movies_ns = movies_dum[~movies_dum['movieId'].isin(ratings_array)]
    movies_ns = movies_ns.drop(columns=['movieId','titulo'])
    model=neighbors.NearestNeighbors(n_neighbors=11, metric='cosine')
    model.fit(movies_ns)
    dist, idlist = model.kneighbors(centroide)
    
    ids=idlist[0]
    recomend_m = movies.loc[ids][['titulo','movieId']]
    

    return recomend_m


# -------------------------------------------------------------------------------------------
# ---------- Generamos recomendaciones para usuarios y llevamos a Excel --------------------- 
# -------------------------------------------------------------------------------------------

def main(list_user):
    
    recomendaciones_todos=pd.DataFrame()
    for user_id in list_user:
            
        recomendaciones=recomendar(user_id)
        recomendaciones["user_id"]=user_id
        recomendaciones.reset_index(inplace=True,drop=True)
        
        recomendaciones_todos=pd.concat([recomendaciones_todos, recomendaciones])

    recomendaciones_todos.to_excel('C:\\Users\\ESTEBAN\\Desktop\\Proyecto_Marketing\\salidas\\recomendaciones.xlsx')
    recomendaciones_todos.to_csv('C:\\Users\\ESTEBAN\\Desktop\\Proyecto_Marketing\\salidas\\recomendaciones.csv')


if __name__=="__main__":
    list_user=[1,2,3,608,609,610]
    main(list_user)
    

import sys
sys.executable