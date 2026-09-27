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


# Kitchen Performance Analysis queries

queries = {
    "Orders by Kitchen": """
        select
        kitchen_id,
        count(order_id) as total_orders
        from orders
        group by kitchen_id
        order by total_orders desc
    """,

    "Revenue by Kitchen": """
        select
        kitchen_id,
        sum(order_value) as total_revenue
        from orders
        group by kitchen_id
        order by total_revenue desc
    """,

    "AOV by Kitchen": """
        select
        kitchen_id,
        round(avg(order_value), 2) as average_order_value
        from orders
        group by kitchen_id
        order by average_order_value desc
    """,

    "Delivery Time by Kitchen": """
        select
        kitchen_id,
        round(avg(delivery_time_min), 2) as average_delivery_time
        from orders
        group by kitchen_id
        order by average_delivery_time
    """,

    "Cancellation Rate": """
        select
        kitchen_id,
        count(*) as total_orders,
        sum(order_status = 'Cancelled') as cancelled_orders,
        round(
        sum(order_status = 'Cancelled') * 100.0 / count(*),
        2
        ) as cancellation_rate
        from orders
        group by kitchen_id
        order by cancellation_rate desc
    """
}


# Create output folder

output_folder = project_folder / "outputs" / "tables"

output_folder.mkdir(
    parents=True,
    exist_ok=True
)


# Output file

output_file = output_folder / "kitchen_performance.xlsx"


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

print("Kitchen Performance Analysis exported successfully!")
print(f"File: {output_file}")
