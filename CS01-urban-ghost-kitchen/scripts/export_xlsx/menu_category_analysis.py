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


# Menu/Category Analysis queries

queries = {
    "Quantity by Category": """
        select
        category,
        sum(quantity) as total_quantity_sold
        from menu_items
        group by category
        order by total_quantity_sold desc
    """,

    "Revenue by Category": """
        select
        category,
        round(sum(quantity * unit_price), 2) as total_sales
        from menu_items
        group by category
        order by total_sales desc
    """,

    "Average Unit Price": """
        select
        category,
        round(avg(unit_price), 2) as average_unit_price
        from menu_items
        group by category
        order by average_unit_price desc
    """,

    "Orders by Category": """
        select
        category,
        count(distinct order_id) as total_orders
        from menu_items
        group by category
        order by total_orders desc
    """,

    "Top 10 Menu Items": """
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
}


# Create output folder

output_folder = project_folder / "outputs" / "tables"

output_folder.mkdir(
    parents=True,
    exist_ok=True
)


# Output file

output_file = output_folder / "11_6_menu_category_analysis.xlsx"


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

print("Menu/Category Analysis exported successfully!")
print(f"File: {output_file}")