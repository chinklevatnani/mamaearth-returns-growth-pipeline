Use capstone_project;
SELECT
    COUNT(*) AS total_orders,
    ROUND(SUM(quantity * price * (1 - COALESCE(discount_pct, 0) / 100)), 2) AS total_revenue,
    ROUND(AVG(quantity * price * (1 - COALESCE(discount_pct, 0) / 100)), 2) AS avg_order_value
FROM orders
JOIN products
ON orders.product_id = products.product_id;

SELECT
    COUNT(*) AS total_orders,
    COUNT(rating) AS rated_orders,
    COUNT(*) - COUNT(rating) AS missing_ratings
FROM orders;
SELECT customers.customer_id, customers.name
FROM customers
LEFT JOIN orders
ON customers.customer_id = orders.customer_id
GROUP BY customers.customer_id, customers.name
HAVING COUNT(orders.order_id) = 0;
SELECT customer_id, name
FROM customers
WHERE customer_id NOT IN (
    SELECT DISTINCT customer_id
    FROM orders
);
SELECT
    customers.city,
    COUNT(*) AS total_orders,
    SUM(orders.returned) AS returned_orders,
    ROUND(SUM(orders.returned) / COUNT(*) * 100, 1) AS return_rate_pct
FROM orders
JOIN customers
ON orders.customer_id = customers.customer_id
GROUP BY customers.city
HAVING return_rate_pct > 20
ORDER BY return_rate_pct DESC;

SELECT
    customers.customer_id,
    customers.name,
    ROUND(SUM(orders.quantity * products.price *
        (1 - COALESCE(orders.discount_pct, 0) / 100)), 2) AS total_spend
FROM orders
JOIN customers
ON orders.customer_id = customers.customer_id
JOIN products
ON orders.product_id = products.product_id
GROUP BY customers.customer_id, customers.name
ORDER BY total_spend DESC, customers.customer_id ASC
LIMIT 5;

SELECT
    customers.customer_id,
    customers.name,
    ROUND(SUM(orders.quantity * products.price *
        (1 - COALESCE(orders.discount_pct, 0) / 100)), 2) AS total_spend
FROM orders
JOIN customers
ON orders.customer_id = customers.customer_id
JOIN products
ON orders.product_id = products.product_id
GROUP BY customers.customer_id, customers.name
ORDER BY total_spend DESC, customers.customer_id ASC
LIMIT 3 OFFSET 2;

SELECT
    products.category,
    COUNT(*) AS order_count,
    ROUND(
        SUM(orders.quantity * products.price *
        (1 - COALESCE(orders.discount_pct, 0) / 100)),
        2
    ) AS category_revenue
FROM orders
JOIN products
ON orders.product_id = products.product_id
JOIN customers
ON orders.customer_id = customers.customer_id
GROUP BY products.category
ORDER BY category_revenue DESC;

SELECT customer_id, name
FROM customers
WHERE name LIKE 'A%';
SELECT DISTINCT acquisition_source
FROM customers;
ALTER TABLE customers
ADD COLUMN loyalty_tier VARCHAR(10);
SET SQL_SAFE_UPDATES = 0;

UPDATE customers
SET loyalty_tier =
    CASE
        WHEN city_tier = 1 THEN 'Gold'
        ELSE 'Silver'
    END;

SET SQL_SAFE_UPDATES = 0;
UPDATE customers
SET loyalty_tier =
    CASE
        WHEN city_tier = 1 THEN 'Gold'
        ELSE 'Silver'
    END;
SELECT loyalty_tier, COUNT(*) AS customer_count
FROM customers
GROUP BY loyalty_tier;
SET SQL_SAFE_UPDATES = 1;