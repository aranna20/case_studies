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


# Time-Based Analysis queries

queries = {
    "Orders by Month": """
        select
        year(order_date) as order_year,
        month(order_date) as order_month,
        monthname(order_date) as month_name,
        count(*) as total_orders
        from orders
        group by
        year(order_date),
        month(order_date),
        monthname(order_date)
        order by
        order_year,
        order_month
    """,

    "Revenue by Month": """
        select
        year(order_date) as order_year,
        month(order_date) as order_month,
        monthname(order_date) as month_name,
        round(sum(order_value), 2) as total_revenue
        from orders
        group by
        year(order_date),
        month(order_date),
        monthname(order_date)
        order by
        order_year,
        order_month
    """,

    "Orders by Day": """
        select
        dayofweek(order_date) as day_number,
        dayname(order_date) as day_name,
        count(*) as total_orders
        from orders
        group by
        dayofweek(order_date),
        dayname(order_date)
        order by day_number
    """,

    "Orders by Hour": """
        select
        hour(order_date) as order_hour,
        count(*) as total_orders
        from orders
        group by hour(order_date)
        order by order_hour
    """,

    "Weekend vs Weekday": """
        select
        case
        when dayofweek(order_date) in (1, 7) then 'Weekend'
        else 'Weekday'
        end as day_type,
        count(*) as total_orders,
        round(sum(order_value), 2) as total_revenue,
        round(avg(order_value), 2) as average_order_value
        from orders
        group by
        case
        when dayofweek(order_date) in (1, 7) then 'Weekend'
        else 'Weekday'
        end
        order by total_orders desc
    """
}


# Create output folder

output_folder = project_folder / "outputs" / "tables"

output_folder.mkdir(
    parents=True,
    exist_ok=True
)


# Output file

output_file = output_folder / "time_based_analysis.xlsx"


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

print("Time-Based Analysis exported successfully!")
print(f"File: {output_file}")