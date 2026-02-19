CREATE SCHEMA IF NOT EXISTS gold;

-- warehouse/gold/ddl/01_dim_date.sql

DROP TABLE IF EXISTS gold.dim_date CASCADE;

CREATE TABLE gold.dim_date (
    date_id             INT PRIMARY KEY, -- Format: YYYYMMDD (Smart Key)
    full_date           DATE NOT NULL,
    year                INTEGER NOT NULL,
    quarter             INTEGER NOT NULL,
    month               INTEGER NOT NULL,
    month_name          VARCHAR(20) NOT NULL,
    week                INTEGER NOT NULL,
    day                 INTEGER NOT NULL,
    day_of_week         INTEGER NOT NULL,
    day_name            VARCHAR(20) NOT NULL,
    is_weekend          BOOLEAN NOT NULL
);

-- Index for analytics
CREATE INDEX idx_dim_date_year ON gold.dim_date (year);
CREATE INDEX idx_dim_date_month ON gold.dim_date (month);


-- Generates dates from 2020-01-01 to 2030-12-31
INSERT INTO gold.dim_date
SELECT 
    TO_CHAR(datum, 'YYYYMMDD')::INT AS date_id,
    datum AS full_date,
    EXTRACT(YEAR FROM datum) AS year,
    EXTRACT(QUARTER FROM datum) AS quarter,
    EXTRACT(MONTH FROM datum) AS month,
    TO_CHAR(datum, 'FMMonth') AS month_name,
    EXTRACT(WEEK FROM datum) AS week,
    EXTRACT(DAY FROM datum) AS day,
    EXTRACT(ISODOW FROM datum) AS day_of_week,
    TO_CHAR(datum, 'FMDay') AS day_name,
    CASE WHEN EXTRACT(ISODOW FROM datum) IN (6, 7) THEN TRUE ELSE FALSE END AS is_weekend
FROM generate_series('2010-01-01'::DATE, '2028-12-31'::DATE, '1 day') AS datum
ON CONFLICT (date_id) DO NOTHING;