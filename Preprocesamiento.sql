----procesamientos---

SELECT userId, COUNT(*) AS numero_filas
FROM ratings
GROUP BY userId
ORDER BY COUNT(*) DESC;

---El usuario que mas a visto peliculas tiene un total de 2698, y el que menos a visto; 20 

---crear tabla con usuarios con más de 25 peliculas vistas y menos de 2600

drop table if exists usuarios_sel;
create table usuarios_sel as 

select "userId" as user_id, count(*) as user_pel
from ratings
group by "userId"
having user_pel > 25 and user_pel <= 2600

order by user_pel desc ;

---

SELECT rating, COUNT(*) AS numero_filas
FROM ratings
GROUP BY rating
ORDER BY COUNT(*) DESC;

--La mayor calificacion es 5.0 y la menor 0.5 

-- Tabla de peliculas con 5.0 de calificacion 

DROP TABLE IF EXISTS peliculas_sel;
CREATE TABLE peliculas_sel AS
SELECT movies.title, COUNT(*) AS rating_cou
FROM movies
INNER JOIN ratings ON movies.movieID = ratings.movieID
GROUP BY movies.title
HAVING rating_cou IN (5.0)
ORDER BY rating_cou DESC;

-- Base de datos peliculas, final

DROP TABLE IF EXISTS pel_fin;
CREATE TABLE pel_fin AS
SELECT movies.movieID, movies.title, movies.genres, peliculas_sel.rating_cou
FROM movies
INNER JOIN peliculas_sel ON movies.title = peliculas_sel.title;

-- Base de datos calificaciones, final

DROP TABLE IF EXISTS cal_fin;
CREATE TABLE cal_fin AS
SELECT ratings.userId, movieID, rating, timestamp
FROM ratings
INNER JOIN usuarios_sel ON ratings.userId = usuarios_sel.user_id;

-- Base de datos final

DROP TABLE IF EXISTS df;
CREATE TABLE df AS
SELECT cal_fin.userID, pel_fin.movieID, pel_fin.title, pel_fin.genres, cal_fin.rating, cal_fin.timestamp
FROM pel_fin
INNER JOIN cal_fin ON pel_fin.movieID = cal_fin.movieID

