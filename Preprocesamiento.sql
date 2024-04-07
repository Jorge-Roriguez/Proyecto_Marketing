/* Visualización de las tablas */
SELECT * FROM ratings;
SELECT * FROM movies;

/* ---------------- Tratamiento de la tabla ratings ---------------- */

/* Creamos una copia de cada una de las tablas */
CREATE TABLE ratings_1 AS SELECT * FROM ratings;
CREATE TABLE movies_1 AS SELECT * FROM movies;


/* Cambio del tipo formato de fecha */
ALTER TABLE ratings_1
ADD COLUMN date DATETIME;

UPDATE ratings_1
SET date = DATETIME(timestamp, 'unixepoch');


/* Agregar las columnas nuevas para fecha */
ALTER TABLE ratings_1 
ADD COLUMN year INT;

ALTER TABLE ratings_1
ADD COLUMN month INT;

ALTER TABLE ratings_1
ADD COLUMN day INT;


/* Anexar el contenido de las columnas creadas */
UPDATE ratings_1
SET 
    year = CAST(strftime('%Y', date) AS INTEGER),
    month = CAST(strftime('%m', date) AS INTEGER),
    day = CAST(strftime('%d', date) AS INTEGER);
	
ALTER TABLE ratings_1 
DROP COLUMN timestamp;

ALTER TABLE ratings_1
Drop COLUMN date;


/* ---------------- Tratamiento de la tabla movies ---------------- */

/* Separación del título y año de las películas */
ALTER TABLE movies_1
ADD COLUMN titulo VARCHAR;

ALTER TABLE movies_1
ADD COLUMN estreno INT;


/* Agregamos el contenido a las nuevas columnas*/
UPDATE movies_1
SET
	titulo = SUBSTRING(title, 1, LENGTH(title) - 7),
	estreno = SUBSTRING(title, LENGTH(title) - 4, 4);

ALTER TABLE movies_1
DROP COLUMN title;


/* Eliminar la información no necesaria*/
DELETE FROM movies_1
WHERE estreno NOT REGEXP '^[0-9]+$';


/* ---------------- Tabla datos consolidados ---------------- */
CREATE TABLE ratings_final AS
SELECT * FROM ratings_1
INNER JOIN movies_1 ON ratings_1.movieId = movies_1.movieId;

ALTER TABLE ratings_final
DROP COLUMN 'movieId:1';