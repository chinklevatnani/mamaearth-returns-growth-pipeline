USE capstone_project;

SELECT COUNT(*) FROM customers;
SELECT COUNT(*) FROM products;
SELECT COUNT(*) FROM orders;
SELECT
    COUNT(*) AS total_orders,
    COUNT(rating) AS rated_orders,
    COUNT(*) - COUNT(rating) AS missing_ratings
FROM orders;
SELECT
    customers.customer_id,
    customers.name
FROM customers
LEFT JOIN orders
    ON customers.customer_id = orders.customer_id
WHERE orders.order_id IS NULL;
SELECT
    customers.city,
    COUNT(orders.order_id) AS total_orders,
    SUM(orders.returned) AS returned_orders,
    ROUND(
        SUM(orders.returned) * 100.0 / COUNT(orders.order_id),
        1
    ) AS return_rate_pct
FROM customers
JOIN orders
    ON customers.customer_id = orders.customer_id
GROUP BY customers.city
HAVING SUM(orders.returned) * 100.0 / COUNT(orders.order_id) > 20
ORDER BY return_rate_pct DESC;
SELECT
    customers.customer_id,
    customers.name,
    ROUND(SUM(orders.quantity * products.price * (1 - orders.discount_pct / 100)), 2) AS total_spent
FROM customers
JOIN orders
    ON customers.customer_id = orders.customer_id
JOIN products
    ON orders.product_id = products.product_id
GROUP BY customers.customer_id, customers.name
ORDER BY total_spent DESC, customers.customer_id ASC
LIMIT 5;
SELECT
    COUNT(*) AS total_orders,
    SUM(discount_pct IS NULL) AS missing_discounts,
    SUM(discount_pct = '') AS empty_discounts
FROM orders;
UPDATE orders
SET discount_pct = NULL
WHERE discount_pct = ''
  AND order_id IS NOT NULL;
  SELECT
    COUNT(*) AS total_orders,
    SUM(discount_pct IS NULL) AS missing_discounts,
    SUM(discount_pct = '') AS empty_discounts
FROM orders;
SELECT
    discount_pct,
    COUNT(*) AS row_count
FROM orders
GROUP BY discount_pct
ORDER BY discount_pct;
SELECT
    customers.customer_id,
    customers.name,
    ROUND(
        SUM(
            orders.quantity * products.price *
            (1 - IFNULL(orders.discount_pct, 0) / 100.0)
        ),
        2
    ) AS total_spent
FROM customers
JOIN orders
    ON customers.customer_id = orders.customer_id
JOIN products
    ON orders.product_id = products.product_id
GROUP BY customers.customer_id, customers.name
ORDER BY total_spent DESC, customers.customer_id ASC
LIMIT 5;
SELECT
    products.category,
    COUNT(orders.order_id) AS order_count,
    ROUND(
        SUM(
            orders.quantity * products.price *
            (1 - IFNULL(orders.discount_pct, 0) / 100.0)
        ),
        2
    ) AS category_revenue
FROM orders
JOIN products
    ON orders.product_id = products.product_id
JOIN customers
    ON orders.customer_id = customers.customer_id
GROUP BY products.category
ORDER BY category_revenue DESC;
SELECT
    customer_id,
    name
FROM customers
WHERE name LIKE 'A%'
ORDER BY name;
SELECT DISTINCT acquisition_source
FROM customers
ORDER BY acquisition_source;
UPDATE customers
SET loyalty_tier = CASE
    WHEN city_tier = 1 THEN 'Gold'
    ELSE 'Silver'
END
WHERE customer_id IS NOT NULL;
SELECT
    loyalty_tier,
    COUNT(*) AS customer_count
FROM customers
GROUP BY loyalty_tier
ORDER BY loyalty_tier;
SELECT COUNT(*) AS total_customers
FROM customers;

SELECT COUNT(*) AS total_products
FROM products;

SELECT COUNT(*) AS total_orders
FROM orders;

SELECT loyalty_tier, COUNT(*) AS customer_count
FROM customers
GROUP BY loyalty_tier
ORDER BY loyalty_tier;

SELECT
    customers.customer_id,
    customers.name,
    ROUND(
        SUM(
            orders.quantity * products.price *
            (1 - IFNULL(orders.discount_pct, 0) / 100.0)
        ),
        2
    ) AS total_spend
FROM customers
JOIN orders
    ON customers.customer_id = orders.customer_id
JOIN products
    ON orders.product_id = products.product_id
GROUP BY customers.customer_id, customers.name
ORDER BY total_spend DESC, customers.customer_id ASC
LIMIT 3 OFFSET 2;