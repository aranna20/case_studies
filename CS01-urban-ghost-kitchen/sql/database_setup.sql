create database ghost_kitchen_analysis;

use ghost_kitchen_analysis;

create table customers (
customer_id varchar(20) primary key,
city varchar(50),
signup_date date,
customer_segment varchar(20)
);

create table kitchens (
kitchen_id varchar(20) primary key,
kitchen_name varchar(100),
zone varchar(50),
monthly_rent decimal(12,2),
staff_count int
);

create table orders (
order_id varchar(20) primary key,
customer_id varchar(20),
kitchen_id varchar(20),
order_date datetime,
order_value decimal(12,2),
discount decimal(12,2),
delivery_fee decimal(12,2),
delivery_distance_km decimal(10,2),
delivery_time_min decimal(10,2),
order_status varchar(20),
foreign key (customer_id) references customers(customer_id),
foreign key (kitchen_id) references kitchens(kitchen_id)
);

create table menu_items (
item_id varchar(20) primary key,
order_id varchar(20),
item_name varchar(100),
category varchar(50),
quantity int,
unit_price decimal(12,2),
foreign key (order_id) references orders(order_id)
);