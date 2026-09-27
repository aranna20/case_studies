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


# Create output folder

output_folder = project_folder / "outputs" / "tables"

output_folder.mkdir(
    parents=True,
    exist_ok=True
)


# Final analysis queries

queries = {

    "customer_analysis": {
        "Customer Order Frequency": """
            select
            customer_id,
            count(order_id) as total_orders
            from orders
            group by customer_id
            order by total_orders desc
        """,

        "Customer Revenue": """
            select
            customer_id,
            round(sum(order_value), 2) as total_revenue
            from orders
            group by customer_id
            order by total_revenue desc
        """
    },


    "kitchen_analysis": {
        "Kitchen Performance": """
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

        "Kitchen Cancellation": """
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
    },


    "menu_analysis": {
        "Category Performance": """
            select
            category,
            sum(quantity) as total_quantity_sold,
            round(sum(quantity * unit_price), 2) as total_sales,
            round(avg(unit_price), 2) as average_unit_price
            from menu_items
            group by category
            order by total_sales desc
        """,

        "Top Menu Items": """
            select
            item_id,
            item_name,
            category,
            sum(quantity) as total_quantity_sold,
            round(sum(quantity * unit_price), 2) as total_sales
            from menu_items
            group by
            item_id,
            item_name,
            category
            order by total_sales desc
            limit 10
        """
    },


    "time_analysis": {
        "Monthly Performance": """
            select
            year(order_date) as order_year,
            month(order_date) as order_month,
            monthname(order_date) as month_name,
            count(*) as total_orders,
            round(sum(order_value), 2) as total_revenue,
            round(avg(order_value), 2) as average_order_value
            from orders
            group by
            year(order_date),
            month(order_date),
            monthname(order_date)
            order by
            order_year,
            order_month
        """,

        "Weekend vs Weekday": """
            select
            case
            when dayofweek(order_date) in (1, 7)
            then 'Weekend'
            else 'Weekday'
            end as day_type,
            count(*) as total_orders,
            round(sum(order_value), 2) as total_revenue,
            round(avg(order_value), 2) as average_order_value
            from orders
            group by
            case
            when dayofweek(order_date) in (1, 7)
            then 'Weekend'
            else 'Weekday'
            end
        """
    },


    "business_kpis": {
        "Overall KPIs": """
            select
            count(*) as total_orders,
            round(sum(order_value), 2) as total_revenue,
            round(avg(order_value), 2) as average_order_value,
            round(avg(delivery_time_min), 2) as average_delivery_time,
            round(avg(delivery_distance_km), 2) as average_delivery_distance,
            sum(order_status = 'Delivered') as delivered_orders,
            sum(order_status = 'Cancelled') as cancelled_orders,
            sum(order_status = 'Refunded') as refunded_orders,
            round(
            sum(order_status = 'Cancelled') * 100.0 / count(*),
            2
            ) as cancellation_rate,
            round(
            sum(order_status = 'Refunded') * 100.0 / count(*),
            2
            ) as refund_rate
            from orders
        """
    }
}


# Export final analysis tables

with engine.connect() as connection:

    for table_name, table_queries in queries.items():

        output_file = (
            output_folder /
            f"final_{table_name}.xlsx"
        )

        with pd.ExcelWriter(
            output_file,
            engine="openpyxl"
        ) as writer:

            for sheet_name, query in table_queries.items():

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
                    f"{table_name} -> "
                    f"{sheet_name}: "
                    f"{len(df)} rows exported"
                )


# Completion message

print("\nFinal analysis tables created successfully!")
print(f"Output folder: {output_folder}")