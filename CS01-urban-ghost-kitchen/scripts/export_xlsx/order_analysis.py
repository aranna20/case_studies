
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
    "Total Orders": """
        select count(*) as total_orders
        from orders;
    """,

    "Order By Status": """
        select order_status, count(*) as total_orders
        from orders
        group by order_status
        order by total_orders desc
    """,

    "Average Order Value": """
       select round(avg(order_value), 2) as average_order_value
       from orders
    """,

    "Orders by Kitchen": """
        select kitchen_id, count(order_id) as total_orders
        from orders
        group by kitchen_id
        order by total_orders desc;
     """,

    "Orders by Customer": """
        select customer_id, count(order_id) as total_orders
        from orders
        group by customer_id
        order by total_orders desc;
    """
}


# Create output folder

output_folder = project_folder / "outputs" / "tables"
output_folder.mkdir(parents=True, exist_ok=True)

output_file = output_folder / "order_analysis.xlsx"


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