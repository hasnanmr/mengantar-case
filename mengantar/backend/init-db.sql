-- =======================================================
-- Mengantar Backend - Database Initialization
-- Run once on first PostgreSQL container start
-- =======================================================

-- Create application schema
CREATE SCHEMA IF NOT EXISTS mengantar_test;

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Set default search path
ALTER DATABASE postgres SET search_path TO mengantar_test, public;

-- Grant permissions to postgres user
GRANT USAGE ON SCHEMA mengantar_test TO postgres;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA mengantar_test TO postgres;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA mengantar_test TO postgres;
ALTER DEFAULT PRIVILEGES IN SCHEMA mengantar_test GRANT ALL ON TABLES TO postgres;
ALTER DEFAULT PRIVILEGES IN SCHEMA mengantar_test GRANT ALL ON SEQUENCES TO postgres;
