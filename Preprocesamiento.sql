------------ Preprocesamientos
ALTER TABLE ratings
ADD COLUMN date DATETIME;

SELECT * FROM ratings;

UPDATE ratings
SET date = DATETIME(timestamp, 'unixepoch');

SELECT * FROM ratings;

ALTER TABLE ratings 
ADD COLUMN year INT;

ALTER TABLE ratings
ADD COLUMN month INT;

ALTER TABLE ratings
ADD COLUMN day INT;

UPDATE ratings
SET 
    year = CAST(strftime('%Y', date) AS INTEGER),
    month = CAST(strftime('%m', date) AS INTEGER),
    day = CAST(strftime('%d', date) AS INTEGER);
	
ALTER TABLE ratings 
DROP COLUMN timestamp;

ALTER TABLE ratings
Drop COLUMN date;

SELECT * FROM ratings; 


