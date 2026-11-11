-- Структура базы данных «Четверть».
-- Выполняется автоматически при запуске app.py.
-- IF NOT EXISTS: существующие таблицы не пересоздаются, данные не теряются.

CREATE TABLE IF NOT EXISTS vehicles (
    id              SERIAL        PRIMARY KEY,
    inventory_no    VARCHAR(20)   NOT NULL UNIQUE,
    type            VARCHAR(20)   NOT NULL,
    model           VARCHAR(100)  NOT NULL,
    status          VARCHAR(20)   NOT NULL,
    price_per_hour  INTEGER       NOT NULL CHECK (price_per_hour > 0),
    battery         INTEGER       CHECK (battery BETWEEN 0 AND 100),
    station         VARCHAR(200)  NOT NULL
);

CREATE TABLE IF NOT EXISTS clients (
    id          SERIAL        PRIMARY KEY,
    full_name   VARCHAR(150)  NOT NULL,
    phone       VARCHAR(20)   NOT NULL UNIQUE,
    email       VARCHAR(100),
    license_no  VARCHAR(20)
);

CREATE TABLE IF NOT EXISTS stations (
    id        SERIAL        PRIMARY KEY,
    name      VARCHAR(100)  NOT NULL UNIQUE,
    address   VARCHAR(200)  NOT NULL,
    capacity  INTEGER       NOT NULL CHECK (capacity BETWEEN 1 AND 500)
);


