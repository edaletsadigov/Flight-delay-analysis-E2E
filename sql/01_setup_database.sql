IF DB_ID('Datacube') IS NULL
    CREATE DATABASE Datacube;
GO

USE Datacube;
GO

IF SCHEMA_ID('bronze') IS NULL EXEC('CREATE SCHEMA bronze');   -- raw data, exactly as received
GO
IF SCHEMA_ID('silver') IS NULL EXEC('CREATE SCHEMA silver');   -- cleaned & typed data
GO
IF SCHEMA_ID('gold')   IS NULL EXEC('CREATE SCHEMA gold');     -- business tables for BI + ML
GO