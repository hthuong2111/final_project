USE ecommerce_clickstream;

-- Top 10 most popular products by total clicks
SELECT 
    product_id,
    clothing_model,
    main_category,
    colour,
    price_usd,
    total_clicks,
    unique_sessions
FROM product_popularity 
ORDER BY total_clicks DESC 
LIMIT 10;

-- Sessions with highest engagement (most clicks)
SELECT * FROM session_summary 
ORDER BY total_clicks DESC 
LIMIT 10;

-- Price analysis by category
SELECT 
    main_category,
    COUNT(*) as product_count,
    MIN(price_usd) as min_price,
    AVG(price_usd) as avg_price,
    MAX(price_usd) as max_price
FROM products
GROUP BY main_category
ORDER BY avg_price DESC;

-- Click distribution by location
SELECT 
    location,
    COUNT(*) as total_clicks,
    COUNT(DISTINCT session_id) as unique_sessions,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM clicks), 2) as percentage
FROM clicks
GROUP BY location
ORDER BY total_clicks DESC;

-- Product color popularity
SELECT 
    colour,
    COUNT(*) as product_count,
    SUM(total_clicks) as total_clicks,
    AVG(total_clicks) as avg_clicks_per_product
FROM product_popularity
GROUP BY colour
ORDER BY total_clicks DESC
LIMIT 10;