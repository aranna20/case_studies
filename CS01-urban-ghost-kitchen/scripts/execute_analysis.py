# Import required libraries

import os

import pandas as pd

from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL


# Load the .env file

project_folder = Path(__file__).resolve().parent.parent

load_dotenv(project_folder / ".env")


# Load MySQL configuration

username = os.getenv("MYSQL_USER")
password = os.getenv("MYSQL_PASSWORD")
host = os.getenv("MYSQL_HOST")
port = os.getenv("MYSQL_PORT", "3306")
database = os.getenv("MYSQL_DATABASE")


# Check MySQL configuration

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


# SQL query

query = """
select
order_status,
count(*) as total_orders,
round(
count(*) * 100.0 / sum(count(*)) over (),
2
) as order_percentage
from orders
group by order_status
order by total_orders desc
"""


# Execute SQL query

with engine.connect() as connection:

    result = pd.read_sql_query(
        text(query),
        connection
    )


# Display result

print("SQL Query Result")
print(result)