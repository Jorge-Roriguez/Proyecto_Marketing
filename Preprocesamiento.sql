/* Tratamiento de la tabla ratings */

/* Cambio del tipo formato de fecha */
ALTER TABLE ratings
ADD COLUMN date DATETIME;

UPDATE ratings
SET date = DATETIME(timestamp, 'unixepoch');


/* Cambio del tipo de datos las fechas */
ALTER TABLE ratings 
ADD COLUMN year INT;

ALTER TABLE ratings
ADD COLUMN month INT;

ALTER TABLE ratings
ADD COLUMN day INT;


/* Separar las fechas en varias columnas */
UPDATE ratings
SET 
    year = CAST(strftime('%Y', date) AS INTEGER),
    month = CAST(strftime('%m', date) AS INTEGER),
    day = CAST(strftime('%d', date) AS INTEGER);
	
ALTER TABLE ratings 
DROP COLUMN timestamp;

ALTER TABLE ratings
Drop COLUMN date;


/* Separación del título y año de las películas */
ALTER TABLE movies
ADD COLUMN titulo VARCHAR;

ALTER TABLE movies
ADD COLUMN year INT;

UPDATE movies
SET
	titulo = SUBSTRING(title, 1, LENGTH(title) - 6),
	year = SUBSTRING(title, LENGTH(title) - 4, 4);

ALTER TABLE movies
RENAME COLUMN year TO estreno;


/* Tabla con toda la información consolidada*/
CREATE TABLE ratings_final AS
SELECT * FROM ratings
INNER JOIN movies ON ratings.movieId = movies.movieId;

ALTER TABLE ratings_final
DROP COLUMN 'movieId:1';