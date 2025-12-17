-- The database named in the POSTGRES_DB environment variable
-- is created automatically by the Docker entrypoint.
-- This script only handles creation of the test database specified by POSTGRES_TEST_DB.
-- Abort on any error in this script
\set ON_ERROR_STOP on
\getenv test_db POSTGRES_TEST_DB
SELECT
  format('CREATE DATABASE %I', :'test_db')
WHERE NOT EXISTS (
  SELECT 1
    FROM pg_database
   WHERE datname = :'test_db'
)\gexec
