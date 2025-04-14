# export PREFECT_API_DATABASE_CONNECTION_URL="postgresql+asyncpg://prefect_user:password@localhost:5432/prefect_db"
# -- Switch to the PostgreSQL shell (if not already in it)
# psql -U postgres

# -- Grant all privileges to prefect_user on prefect_db
# GRANT ALL PRIVILEGES ON DATABASE prefect_db TO prefect_user;

#-- Connect to the database
#\c prefect_db

#-- Grant privileges on all existing tables
#GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO prefect_user;

#-- Grant privileges on all existing sequences (important for auto-incrementing IDs)
#GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO prefect_user;

#-- Ensure future tables and sequences also get the correct permissions
#ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL PRIVILEGES ON TABLES TO prefect_user;
#ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL PRIVILEGES ON SEQUENCES TO prefect_user;
