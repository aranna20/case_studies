# Import required libraries

import os

import pandas as pd
import matplotlib.pyplot as plt

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


# Create chart output folder

chart_folder = project_folder / "outputs" / "charts"

chart_folder.mkdir(
    parents=True,
    exist_ok=True
)


# Create monthly revenue chart

monthly_revenue_query = """
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
"""

monthly_revenue = pd.read_sql_query(
    text(monthly_revenue_query),
    engine
)

monthly_revenue["period"] = (
    monthly_revenue["month_name"].str[:3]
    + " "
    + monthly_revenue["order_year"].astype(str)
)

plt.figure(figsize=(12, 6))

plt.plot(
    monthly_revenue["period"],
    monthly_revenue["total_revenue"],
    marker="o"
)

plt.title("Monthly Revenue Trend")
plt.xlabel("Month")
plt.ylabel("Revenue")
plt.xticks(rotation=45)
plt.tight_layout()

plt.savefig(
    chart_folder / "monthly_revenue.png",
    dpi=300,
    bbox_inches="tight"
)

plt.close()


# Create kitchen order volume chart

kitchen_orders_query = """
select
kitchen_id,
count(order_id) as total_orders
from orders
group by kitchen_id
order by total_orders desc
"""

kitchen_orders = pd.read_sql_query(
    text(kitchen_orders_query),
    engine
)

plt.figure(figsize=(10, 8))

plt.barh(
    kitchen_orders["kitchen_id"],
    kitchen_orders["total_orders"]
)

plt.title("Orders by Kitchen")
plt.xlabel("Total Orders")
plt.ylabel("Kitchen")
plt.gca().invert_yaxis()
plt.tight_layout()

plt.savefig(
    chart_folder / "kitchen_orders.png",
    dpi=300,
    bbox_inches="tight"
)

plt.close()


# Create kitchen cancellation rate chart

kitchen_cancellation_query = """
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

kitchen_cancellation = pd.read_sql_query(
    text(kitchen_cancellation_query),
    engine
)

plt.figure(figsize=(10, 8))

plt.barh(
    kitchen_cancellation["kitchen_id"],
    kitchen_cancellation["cancellation_rate"]
)

plt.title("Kitchen Cancellation Rate")
plt.xlabel("Cancellation Rate (%)")
plt.ylabel("Kitchen")
plt.gca().invert_yaxis()
plt.tight_layout()

plt.savefig(
    chart_folder / "kitchen_cancellation_rate.png",
    dpi=300,
    bbox_inches="tight"
)

plt.close()


# Create category revenue chart

category_revenue_query = """
select
category,
round(sum(quantity * unit_price), 2) as total_sales
from menu_items
group by category
order by total_sales desc
"""

category_revenue = pd.read_sql_query(
    text(category_revenue_query),
    engine
)

plt.figure(figsize=(10, 7))

plt.barh(
    category_revenue["category"],
    category_revenue["total_sales"]
)

plt.title("Revenue by Menu Category")
plt.xlabel("Revenue")
plt.ylabel("Category")
plt.gca().invert_yaxis()
plt.tight_layout()

plt.savefig(
    chart_folder / "category_revenue.png",
    dpi=300,
    bbox_inches="tight"
)

plt.close()


# Create hourly orders chart

hourly_orders_query = """
select
hour(order_date) as order_hour,
count(*) as total_orders
from orders
group by hour(order_date)
order by order_hour
"""

hourly_orders = pd.read_sql_query(
    text(hourly_orders_query),
    engine
)

plt.figure(figsize=(12, 6))

plt.plot(
    hourly_orders["order_hour"],
    hourly_orders["total_orders"],
    marker="o"
)

plt.title("Orders by Hour")
plt.xlabel("Hour of Day")
plt.ylabel("Total Orders")
plt.xticks(range(0, 24))
plt.tight_layout()

plt.savefig(
    chart_folder / "hourly_orders.png",
    dpi=300,
    bbox_inches="tight"
)

plt.close()


# Create customer segment order chart

segment_orders_query = """
select
c.customer_segment,
count(o.order_id) as total_orders
from customers c
join orders o
on c.customer_id = o.customer_id
group by c.customer_segment
order by total_orders desc
"""

segment_orders = pd.read_sql_query(
    text(segment_orders_query),
    engine
)

plt.figure(figsize=(8, 6))

plt.bar(
    segment_orders["customer_segment"],
    segment_orders["total_orders"]
)

plt.title("Orders by Customer Segment")
plt.xlabel("Customer Segment")
plt.ylabel("Total Orders")
plt.tight_layout()

plt.savefig(
    chart_folder / "segment_orders.png",
    dpi=300,
    bbox_inches="tight"
)

# Create order status donut chart

order_status_query = """
select
order_status,
count(*) as total_orders
from orders
group by order_status
order by total_orders desc
"""

order_status = pd.read_sql_query(
    text(order_status_query),
    engine
)

plt.figure(figsize=(8, 8))

plt.pie(
    order_status["total_orders"],
    labels=order_status["order_status"],
    autopct="%1.1f%%",
    startangle=90,
    wedgeprops=dict(width=0.4)
)

plt.title("Order Status Distribution")

plt.tight_layout()

plt.savefig(
    chart_folder / "order_status_distribution.png",
    dpi=300,
    bbox_inches="tight"
)

plt.close()


# Completion message

print("All charts created successfully!")
print(f"Chart folder: {chart_folder}")