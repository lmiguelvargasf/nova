-- The database named in the POSTGRES_DB environment variable
-- is created automatically by the Docker entrypoint.
-- This script creates the test database by appending _test to POSTGRES_DB.
\set ON_ERROR_STOP on
\getenv main_db POSTGRES_DB
SELECT
  format('CREATE DATABASE %I', :'main_db' || '_test')
WHERE NOT EXISTS (
  SELECT 1
    FROM pg_database
   WHERE datname = :'main_db' || '_test'
)\gexec
