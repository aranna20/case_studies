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


# Delivery Performance queries

queries = {
    "Average Delivery Time": """
        select
        round(avg(delivery_time_min), 2) as average_delivery_time
        from orders
    """,

    "Average Delivery Distance": """
        select
        round(avg(delivery_distance_km), 2) as average_delivery_distance
        from orders
    """,

    "Delivery Time by Category": """
        select
        case
        when delivery_time_min <= 30 then 'Fast'
        when delivery_time_min <= 60 then 'Moderate'
        else 'Slow'
        end as delivery_time_category,
        count(*) as total_orders
        from orders
        group by
        case
        when delivery_time_min <= 30 then 'Fast'
        when delivery_time_min <= 60 then 'Moderate'
        else 'Slow'
        end
        order by total_orders desc
    """,

    "Time by Distance Category": """
        select
        case
        when delivery_distance_km <= 5 then 'Short'
        when delivery_distance_km <= 10 then 'Medium'
        else 'Long'
        end as distance_category,
        count(*) as total_orders,
        round(avg(delivery_time_min), 2) as average_delivery_time
        from orders
        group by
        case
        when delivery_distance_km <= 5 then 'Short'
        when delivery_distance_km <= 10 then 'Medium'
        else 'Long'
        end
        order by average_delivery_time
    """,

    "Delivery Cost per Kilometer": """
        select
        round(
        avg(delivery_fee / delivery_distance_km),
        2
        ) as average_delivery_cost_per_km
        from orders
        where delivery_distance_km > 0
    """,

    "Delivery Efficiency by Kitchen": """
        select
        kitchen_id,
        round(
        avg(delivery_distance_km / delivery_time_min),
        2
        ) as average_delivery_efficiency
        from orders
        where delivery_time_min > 0
        group by kitchen_id
        order by average_delivery_efficiency desc
    """
}


# Create output folder

output_folder = project_folder / "outputs" / "tables"

output_folder.mkdir(
    parents=True,
    exist_ok=True
)


# Output file

output_file = output_folder / "delivery_performance.xlsx"


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

print("Delivery Performance Analysis exported successfully!")
print(f"File: {output_file}")