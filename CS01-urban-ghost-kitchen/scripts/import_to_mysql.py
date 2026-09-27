# Import required libraries

import os
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.engine import URL


# Load the .env file

env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(env_path)


# Load MySQL configuration

username = os.getenv("MYSQL_USER")
password = os.getenv("MYSQL_PASSWORD")
host = os.getenv("MYSQL_HOST")
port = os.getenv("MYSQL_PORT", "3306")
database = os.getenv("MYSQL_DATABASE")


# Check MySQL configuration

print("MYSQL_USER:", username)
print("MYSQL_HOST:", host)
print("MYSQL_PORT:", port)
print("MYSQL_DATABASE:", database)


if not all([username, password, host, database]):
    print("MySQL configuration is incomplete.")
    raise SystemExit


# Create MySQL connection

connection_url = URL.create(
    "mysql+pymysql",
    username=username,
    password=password,
    host=host,
    port=int(port),
    database=database
)

engine = create_engine(connection_url)


# Path to cleaned datasets

cleaned_folder = Path(
    r"D:\IVY Files\15 Days Data Analytics Sprint\day01-urban-ghost-kitchen\Datasets\Cleaned"
)


# Datasets and MySQL table names

datasets = {
    "customers_clean.csv": "customers",
    "kitchens_clean.csv": "kitchens",
    "orders_clean.csv": "orders",
    "menu_items_clean.csv": "menu_items"
}


# Import datasets into MySQL

for file_name, table_name in datasets.items():

    file_path = cleaned_folder / file_name

    if file_path.exists():

        df = pd.read_csv(file_path)

        df.to_sql(
            table_name,
            con=engine,
            if_exists="append",
            index=False
        )

        print(
            f"{table_name}: {len(df)} rows imported successfully"
        )

    else:

        print(
            f"File not found: {file_path}"
        )


print("All datasets imported successfully")