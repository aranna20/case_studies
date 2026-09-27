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


# Business analysis queries

queries = {
    "customer_analysis": """
        select
        customer_id,
        count(order_id) as total_orders
        from orders
        group by customer_id
        order by total_orders desc
    """,

    "revenue_analysis": """
        select
        kitchen_id,
        sum(order_value) as total_revenue
        from orders
        group by kitchen_id
        order by total_revenue desc
    """,

    "order_analysis": """
        select
        order_status,
        count(*) as total_orders
        from orders
        group by order_status
        order by total_orders desc
    """,

    "kitchen_performance": """
        select
        kitchen_id,
        count(order_id) as total_orders,
        round(sum(order_value), 2) as total_revenue,
        round(avg(order_value), 2) as average_order_value,
        round(avg(delivery_time_min), 2) as average_delivery_time
        from orders
        group by kitchen_id
        order by total_revenue desc
    """,

    "delivery_performance": """
        select
        round(avg(delivery_time_min), 2) as average_delivery_time,
        round(avg(delivery_distance_km), 2) as average_delivery_distance,
        round(avg(delivery_fee / delivery_distance_km), 2) as average_delivery_cost_per_km
        from orders
        where delivery_distance_km > 0
    """,

    "menu_analysis": """
        select
        category,
        sum(quantity) as total_quantity_sold,
        round(sum(quantity * unit_price), 2) as total_sales,
        round(avg(unit_price), 2) as average_unit_price
        from menu_items
        group by category
        order by total_sales desc
    """,

    "customer_segmentation": """
        select
        c.customer_segment,
        count(distinct c.customer_id) as total_customers,
        count(o.order_id) as total_orders,
        round(sum(o.order_value), 2) as total_revenue,
        round(avg(o.order_value), 2) as average_order_value
        from customers c
        join orders o
        on c.customer_id = o.customer_id
        group by c.customer_segment
        order by total_revenue desc
    """,

    "cancellation_refund": """
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
    """,

    "time_based": """
        select
        year(order_date) as order_year,
        month(order_date) as order_month,
        monthname(order_date) as month_name,
        count(*) as total_orders,
        round(sum(order_value), 2) as total_revenue
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


# Retrieve analysis results

results = {}

with engine.connect() as connection:

    for name, query in queries.items():

        df = pd.read_sql_query(
            text(query),
            connection
        )

        results[name] = df

        print(
            f"{name}: {df.shape}"
        )


# Display retrieved results

print("\nAnalysis Results Retrieved Successfully")

for name, df in results.items():

    print(f"\n{name}")
    print(df.head())