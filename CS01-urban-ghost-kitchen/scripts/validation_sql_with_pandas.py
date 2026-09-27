# Import required libraries

import os

import pandas as pd

from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import create_engine
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


# Load orders table

orders = pd.read_sql(
    "select * from orders",
    engine
)


# SQL result values

sql_total_orders = 20000
sql_delivered_orders = 17162
sql_cancelled_orders = 2038
sql_refunded_orders = 800


# Calculate order metrics using Pandas

pandas_total_orders = len(orders)

pandas_delivered_orders = (
    orders["order_status"] == "Delivered"
).sum()

pandas_cancelled_orders = (
    orders["order_status"] == "Cancelled"
).sum()

pandas_refunded_orders = (
    orders["order_status"] == "Refunded"
).sum()


# Compare SQL and Pandas results

validation = pd.DataFrame({
    "metric": [
        "Total Orders",
        "Delivered Orders",
        "Cancelled Orders",
        "Refunded Orders"
    ],
    "sql_value": [
        sql_total_orders,
        sql_delivered_orders,
        sql_cancelled_orders,
        sql_refunded_orders
    ],
    "pandas_value": [
        pandas_total_orders,
        pandas_delivered_orders,
        pandas_cancelled_orders,
        pandas_refunded_orders
    ]
})


# Check whether results match

validation["match"] = (
    validation["sql_value"]
    == validation["pandas_value"]
)


# Display validation results

print("SQL vs Pandas Validation")

print(validation)


# Overall validation status

if validation["match"].all():

    print("\nValidation Successful")
    print("SQL and Pandas results match.")

else:

    print("\nValidation Failed")
    print("SQL and Pandas results do not match.")