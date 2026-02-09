-- ============================================
-- E-Commerce Clickstream Database Schema
-- Database: ecommerce_clickstream
-- ============================================

-- Create database
CREATE DATABASE IF NOT EXISTS ecommerce_clickstream;
USE ecommerce_clickstream;

-- Drop tables if they exist (for clean setup)
DROP TABLE IF EXISTS clicks;
DROP TABLE IF EXISTS products;
DROP TABLE IF EXISTS sessions;

-- ============================================
-- Table: sessions
-- Stores unique user browsing sessions
-- ============================================
CREATE TABLE sessions (
    session_id INT PRIMARY KEY,
    country VARCHAR(50) NOT NULL,
    year INT NOT NULL,
    month INT NOT NULL,
    day INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_country (country),
    INDEX idx_date (year, month, day)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============================================
-- Table: products
-- Stores unique product information
-- ============================================
CREATE TABLE products (
    product_id INT PRIMARY KEY AUTO_INCREMENT,
    clothing_model VARCHAR(20) UNIQUE NOT NULL,
    main_category VARCHAR(50) NOT NULL,
    colour VARCHAR(50) NOT NULL,
    price_usd DECIMAL(10,2) NOT NULL,
    price_vs_category_avg VARCHAR(20) NOT NULL,
    INDEX idx_category (main_category),
    INDEX idx_colour (colour)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============================================
-- Table: clicks
-- Stores individual click events
-- ============================================
CREATE TABLE clicks (
    click_id INT PRIMARY KEY AUTO_INCREMENT,
    session_id INT NOT NULL,
    product_id INT NOT NULL,
    click_order INT NOT NULL,
    location VARCHAR(50) NOT NULL,
    model_photography VARCHAR(20) NOT NULL,
    page INT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES sessions(session_id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(product_id) ON DELETE CASCADE,
    INDEX idx_session_order (session_id, click_order),
    INDEX idx_product (product_id),
    INDEX idx_location (location)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============================================
-- Create Views for Common Queries
-- ============================================

-- View: Session summary with click counts
CREATE OR REPLACE VIEW session_summary AS
SELECT 
    s.session_id,
    s.country,
    s.year,
    s.month,
    s.day,
    COUNT(c.click_id) as total_clicks,
    COUNT(DISTINCT c.product_id) as unique_products,
    MIN(c.click_order) as first_click,
    MAX(c.click_order) as last_click
FROM sessions s
LEFT JOIN clicks c ON s.session_id = c.session_id
GROUP BY s.session_id, s.country, s.year, s.month, s.day;

-- View: Product popularity
CREATE OR REPLACE VIEW product_popularity AS
SELECT 
    p.product_id,
    p.clothing_model,
    p.main_category,
    p.colour,
    p.price_usd,
    COUNT(c.click_id) as total_clicks,
    COUNT(DISTINCT c.session_id) as unique_sessions
FROM products p
LEFT JOIN clicks c ON p.product_id = c.product_id
GROUP BY p.product_id, p.clothing_model, p.main_category, p.colour, p.price_usd;

-- View: Complete click details (denormalized for easy querying)
CREATE OR REPLACE VIEW click_details AS
SELECT 
    c.click_id,
    c.session_id,
    s.country,
    s.year,
    s.month,
    s.day,
    c.click_order,
    c.product_id,
    p.clothing_model,
    p.main_category,
    p.colour,
    p.price_usd,
    p.price_vs_category_avg,
    c.location,
    c.model_photography,
    c.page,
    c.timestamp
FROM clicks c
JOIN sessions s ON c.session_id = s.session_id
JOIN products p ON c.product_id = p.product_id;