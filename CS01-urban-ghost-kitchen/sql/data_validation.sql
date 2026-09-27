use ghost_kitchen_analysis;

-- row counts 

select count(*) as total_customers
from customers;

select count(*) as total_kitchens
from kitchens;

select count(*) as total_menu_items
from menu_items;

select count(*) as total_orders
from orders;

-- check duplicate primary keys

select customer_id, count(*) as duplicate_count
from customers
group by customer_id
having count(*) > 1;

select kitchen_id, count(*) as duplicate_count
from kitchens
group by kitchen_id
having count(*) > 1;

select order_id, count(*) as duplicate_count
from orders
group by order_id
having count(*) > 1;

select item_id, count(*) as duplicate_count
from menu_items
group by item_id
having count(*) > 1; 

-- check orphan customer IDs

select count(*) as orphan_orders
from orders o
left join customers c
on o.customer_id = c.customer_id
where c.customer_id is null;

-- check orphan kitchen IDs

select count(*) as orphan_orders
from orders o
left join kitchens k
on o.kitchen_id = k.kitchen_id
where k.kitchen_id is null;

-- check orphan order IDs

select count(*) as orphan_menu_items
from menu_items m
left join orders o
on m.order_id = o.order_id
where o.order_id is null;

-- check null values

select
count(*) as total_orders,
sum(order_id is null) as missing_order_id,
sum(customer_id is null) as missing_customer_id,
sum(kitchen_id is null) as missing_kitchen_id,
sum(order_date is null) as missing_order_date
from orders;

-- check order status

select order_status, count(*) as total_orders
from orders
group by order_status
order by total_orders desc;



