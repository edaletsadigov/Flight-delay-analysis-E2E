import re
from pathlib import Path
import pandas as pd
from sqlalchemy import create_engine, text, URL

DB_SERVER = "localhost"
DB_PORT   = 1433
DB_NAME   = "Datacube"

ADMIN_USER     = "sa"
ADMIN_PASSWORD = "DataCube123!"

APP_USER     = "datacube_analytics"
APP_PASSWORD = "Analytics_Pass123!"  

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SQL_DIR      = PROJECT_ROOT / "sql"


def get_engine(database=DB_NAME, admin=False):
    user, pwd = (ADMIN_USER, ADMIN_PASSWORD) if admin else (APP_USER, APP_PASSWORD)
    url = URL.create("mssql+pymssql", username=user, password=pwd,
                     host=DB_SERVER, port=DB_PORT, database=database)
    return create_engine(url)


def run_sql_file(path, engine, autocommit=False):
    """Run a .sql file that uses GO as batch separator."""
    sql = Path(path).read_text(encoding="utf-8")
    batches = [b.strip() for b in re.split(r"^\s*GO\s*$", sql,
               flags=re.MULTILINE | re.IGNORECASE) if b.strip()]
    conn = engine.connect()
    if autocommit:
        conn = conn.execution_options(isolation_level="AUTOCOMMIT")
    with conn:
        for batch in batches:
            if batch.upper().startswith("USE "):
                continue
            conn.execute(text(batch))
        if not autocommit:
            conn.commit()


def setup_database():
    """One-time (safe to re-run): database, schemas, and the datacube_analytics login."""
    pwd = APP_PASSWORD.replace("'", "''")


    with get_engine("master", admin=True).connect().execution_options(
            isolation_level="AUTOCOMMIT") as conn:
        print(conn.execute(text("SELECT @@VERSION")).scalar()[:60])
        conn.execute(text(f"IF DB_ID('{DB_NAME}') IS NULL CREATE DATABASE [{DB_NAME}]"))
        conn.execute(text(f"""
            IF NOT EXISTS (SELECT 1 FROM sys.server_principals WHERE name = '{APP_USER}')
                CREATE LOGIN [{APP_USER}] WITH PASSWORD = '{pwd}',
                    DEFAULT_DATABASE = [{DB_NAME}], CHECK_EXPIRATION = OFF
        """))

    admin = get_engine(admin=True)
    run_sql_file(SQL_DIR / "01_setup_database.sql", admin, autocommit=True)
    with admin.connect().execution_options(isolation_level="AUTOCOMMIT") as conn:
        conn.execute(text(f"""
            IF USER_ID('{APP_USER}') IS NULL
                CREATE USER [{APP_USER}] FOR LOGIN [{APP_USER}]
        """))
        conn.execute(text(f"ALTER ROLE db_owner ADD MEMBER [{APP_USER}]"))

    with get_engine().connect() as conn:
        print("Logged in as:", conn.execute(text("SELECT SUSER_NAME()")).scalar())
        print(pd.read_sql("SELECT name FROM sys.schemas "
                          "WHERE name IN ('bronze','silver','gold')", conn))