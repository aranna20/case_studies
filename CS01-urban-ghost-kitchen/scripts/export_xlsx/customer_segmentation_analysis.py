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


# Customer Segmentation Analysis queries

queries = {
    "Customer Count by Segment": """
        select
        customer_segment,
        count(*) as total_customers
        from customers
        group by customer_segment
        order by total_customers desc
    """,

    "Orders by Segment": """
        select
        c.customer_segment,
        count(o.order_id) as total_orders
        from customers c
        join orders o
        on c.customer_id = o.customer_id
        group by c.customer_segment
        order by total_orders desc
    """,

    "Revenue by Segment": """
        select
        c.customer_segment,
        round(sum(o.order_value), 2) as total_revenue
        from customers c
        join orders o
        on c.customer_id = o.customer_id
        group by c.customer_segment
        order by total_revenue desc
    """,

    "Average Order Value": """
        select
        c.customer_segment,
        round(avg(o.order_value), 2) as average_order_value
        from customers c
        join orders o
        on c.customer_id = o.customer_id
        group by c.customer_segment
        order by average_order_value desc
    """,

    "Average Customer Spending": """
        select
        c.customer_segment,
        round(
        sum(o.order_value) / count(distinct c.customer_id),
        2
        ) as average_customer_spend
        from customers c
        join orders o
        on c.customer_id = o.customer_id
        group by c.customer_segment
        order by average_customer_spend desc
    """
}


# Create output folder

output_folder = project_folder / "outputs" / "tables"

output_folder.mkdir(
    parents=True,
    exist_ok=True
)


# Output file

output_file = output_folder / "customer_segmentation.xlsx"


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

print("Customer Segmentation Analysis exported successfully!")
print(f"File: {output_file}")