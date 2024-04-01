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


# -------------------------- Creamos conexión con SQL ----------------------------------------#
conn=sql.connect('data\\db_movies') 
cur=conn.cursor() 

# funciones.ejecutar_sql('Preprocesamiento.sql', cur) Ejecutar sólo si no tienes aún los cambios en db 

# ------------------------- Verificamos tablas en db ----------------------------------------#
cur.execute("Select name from sqlite_master where type='table'") ### consultar bases de datos
cur.fetchall()

# ------------------------- Leemos tablas como DataFrames -----------------------------------#
ratings = pd.read_sql("SELECT * FROM ratings", conn)
movies = pd.read_sql("SELECT * FROM movies", conn)