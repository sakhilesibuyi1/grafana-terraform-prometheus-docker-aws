-- Create the database
CREATE DATABASE flask_db;

-- Connect to the database
\c myapp;

-- Create a table
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) NOT NULL,
    password VARCHAR(100) NOT NULL
);
insert into "user"(id, username, password)
values(1,"sakhile","admin23");