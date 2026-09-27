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


# Cancellation/Refund Analysis queries

queries = {
    "Overall Cancellation Refund": """
        select
        count(*) as total_orders,
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
    """,

    "Cancellation Refund by Kitchen": """
        select
        kitchen_id,
        count(*) as total_orders,
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
        group by kitchen_id
        order by cancellation_rate desc
    """,

    "Cancellation Refund by Segment": """
        select
        c.customer_segment,
        count(o.order_id) as total_orders,
        sum(o.order_status = 'Cancelled') as cancelled_orders,
        sum(o.order_status = 'Refunded') as refunded_orders,
        round(
        sum(o.order_status = 'Cancelled') * 100.0 / count(o.order_id),
        2
        ) as cancellation_rate,
        round(
        sum(o.order_status = 'Refunded') * 100.0 / count(o.order_id),
        2
        ) as refund_rate
        from customers c
        join orders o
        on c.customer_id = o.customer_id
        group by c.customer_segment
        order by cancellation_rate desc
    """,

    "Cancellation Refund by Month": """
        select
        year(order_date) as order_year,
        month(order_date) as order_month,
        monthname(order_date) as month_name,
        count(*) as total_orders,
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
        group by
        year(order_date),
        month(order_date),
        monthname(order_date)
        order by
        order_year,
        order_month
    """,

    "Cancellation Refund by Distance": """
        select
        case
        when delivery_distance_km <= 5 then 'Short'
        when delivery_distance_km <= 10 then 'Medium'
        else 'Long'
        end as distance_category,
        count(*) as total_orders,
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
        group by
        case
        when delivery_distance_km <= 5 then 'Short'
        when delivery_distance_km <= 10 then 'Medium'
        else 'Long'
        end
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

output_file = output_folder / "cancellation_refund.xlsx"


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

print("Cancellation/Refund Analysis exported successfully!")
print(f"File: {output_file}")