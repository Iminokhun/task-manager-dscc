CREATE DATABASE cloud_db;
CREATE USER cloud_user WITH PASSWORD 'cloud_pass_123';
ALTER ROLE cloud_user SET client_encoding TO 'utf8';
ALTER ROLE cloud_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE cloud_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE cloud_db TO cloud_user;
