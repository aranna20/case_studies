
# Import required libraries

import os
import pandas as pd

from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL


# Load database configuration

project_folder = Path(__file__).resolve().parent.parent

load_dotenv(project_folder / ".env")

connection_url = URL.create(
    "mysql+pymysql",
    username=os.getenv("MYSQL_USER"),
    password=os.getenv("MYSQL_PASSWORD"),
    host=os.getenv("MYSQL_HOST"),
    port=int(os.getenv("MYSQL_PORT", "3306")),
    database=os.getenv("MYSQL_DATABASE")
)

engine = create_engine(connection_url)


# Customer analysis queries

queries = {
    "Customer Order Frequency": """
        select
        customer_id,
        count(order_id) as total_orders
        from orders
        group by customer_id
        order by total_orders desc
    """,

    "Customer Spending": """
        select
        customer_id,
        sum(order_value) as total_spend
        from orders
        group by customer_id
        order by total_spend desc
    """,

    "Average Order Value": """
        select
        customer_id,
        round(avg(order_value), 2) as average_order_value
        from orders
        group by customer_id
        order by average_order_value desc
    """,

    "Customer Order Status": """
        select
        customer_id,
        sum(order_status = 'Delivered') as delivered_orders,
        sum(order_status = 'Cancelled') as cancelled_orders,
        sum(order_status = 'Refunded') as refunded_orders
        from orders
        group by customer_id
        order by cancelled_orders desc
    """,

    "Revenue Contribution": """
        select
        customer_id,
        sum(order_value) as total_spend,
        round(
        sum(order_value) * 100.0 / sum(sum(order_value)) over (),
        2
        ) as revenue_contribution_percentage
        from orders
        group by customer_id
        order by revenue_contribution_percentage desc
    """
}


# Create output folder

output_folder = project_folder / "outputs" / "tables"
output_folder.mkdir(parents=True, exist_ok=True)

output_file = output_folder / "customer_analysis.xlsx"


# Execute queries and export results

with pd.ExcelWriter(output_file, engine="openpyxl") as writer:

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

            print(f"{sheet_name}: {len(df)} rows exported")


print(f"Export completed: {output_file}")