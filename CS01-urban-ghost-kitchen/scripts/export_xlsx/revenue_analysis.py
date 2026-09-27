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


# Revenue Analysis queries

queries = {
    "Total Revenue": """
        select
        sum(order_value) as total_revenue
        from orders
    """,

    "Revenue by Customer": """
        select
        customer_id,
        sum(order_value) as total_revenue
        from orders
        group by customer_id
        order by total_revenue desc
    """,

    "Revenue by Kitchen": """
        select
        kitchen_id,
        sum(order_value) as total_revenue
        from orders
        group by kitchen_id
        order by total_revenue desc
    """,

    "Revenue by Status": """
        select
        order_status,
        sum(order_value) as total_revenue
        from orders
        group by order_status
        order by total_revenue desc
    """,

    "Monthly Revenue": """
        select
        year(order_date) as order_year,
        month(order_date) as order_month,
        monthname(order_date) as month_name,
        sum(order_value) as total_revenue
        from orders
        group by
        year(order_date),
        month(order_date),
        monthname(order_date)
        order by
        order_year,
        order_month
    """
}


# Create output folder

output_folder = project_folder / "outputs" / "tables"

output_folder.mkdir(
    parents=True,
    exist_ok=True
)


# Output file

output_file = output_folder / "revenue_analysis.xlsx"


# Execute queries and export results

with pd.ExcelWriter(
    output_file,
    engine="openpyxl"
) as writer:

    with engine.connect() as connection:

        for sheet_name, query in queries.items():

            df = pd.read_sql_query(
                text(query),
                connection
            )

            df.to_excel(
                writer,
                sheet_name=sheet_name,
                index=False
            )

            print(
                f"{sheet_name}: {len(df)} rows exported"
            )


# Completion message

print("Revenue Analysis exported successfully!")
print(f"File: {output_file}")