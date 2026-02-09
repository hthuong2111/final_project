"""
Load E-Commerce Clickstream Data into MySQL Database
This script reads the cleaned CSV data and populates the MySQL database.
"""

import pandas as pd
import mysql.connector
from mysql.connector import Error
import sys
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Database configuration from environment variables
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', ''),
    'database': os.getenv('DB_NAME', 'ecommerce_clickstream')
}

def create_connection():
    """Create database connection"""
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        if connection.is_connected():
            print("✓ Successfully connected to MySQL database")
            return connection
    except Error as e:
        print(f"✗ Error connecting to MySQL: {e}")
        sys.exit(1)

def load_csv_data(csv_path):
    """Load and prepare data from CSV"""
    try:
        df = pd.read_csv(csv_path)
        print(f"✓ Loaded {len(df)} rows from CSV")
        return df
    except Exception as e:
        print(f"✗ Error loading CSV: {e}")
        sys.exit(1)

def populate_sessions(connection, df):
    """Populate sessions table"""
    cursor = connection.cursor()
    
    # Get unique sessions
    sessions = df[['session_id', 'country', 'year', 'month', 'day']].drop_duplicates()
    
    insert_query = """
        INSERT INTO sessions (session_id, country, year, month, day)
        VALUES (%s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE session_id=session_id
    """
    
    data = sessions.values.tolist()
    cursor.executemany(insert_query, data)
    connection.commit()
    
    print(f"✓ Inserted {len(sessions)} sessions")
    cursor.close()

def populate_products(connection, df):
    """Populate products table"""
    cursor = connection.cursor()
    
    # Get unique products
    products = df[['clothing_model', 'main_category', 'colour', 
                   'price_usd', 'price_vs_category_avg']].drop_duplicates()
    
    insert_query = """
        INSERT INTO products (clothing_model, main_category, colour, price_usd, price_vs_category_avg)
        VALUES (%s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE clothing_model=clothing_model
    """
    
    data = products.values.tolist()
    cursor.executemany(insert_query, data)
    connection.commit()
    
    print(f"✓ Inserted {len(products)} unique products")
    cursor.close()

def populate_clicks(connection, df):
    """Populate clicks table"""
    cursor = connection.cursor()
    
    # First, get product_id mapping
    cursor.execute("SELECT product_id, clothing_model FROM products")
    product_map = {model: pid for pid, model in cursor.fetchall()}
    
    # Prepare clicks data
    clicks_data = []
    for _, row in df.iterrows():
        product_id = product_map.get(row['clothing_model'])
        if product_id:
            clicks_data.append((
                row['session_id'],
                product_id,
                row['order'],
                row['location'],
                row['model_photography'],
                row['page']
            ))
    
    insert_query = """
        INSERT INTO clicks (session_id, product_id, click_order, location, model_photography, page)
        VALUES (%s, %s, %s, %s, %s, %s)
    """
    
    # Insert in batches for better performance
    batch_size = 1000
    for i in range(0, len(clicks_data), batch_size):
        batch = clicks_data[i:i + batch_size]
        cursor.executemany(insert_query, batch)
        connection.commit()
        print(f"  Inserted clicks {i+1} to {min(i+batch_size, len(clicks_data))}")
    
    print(f"✓ Inserted {len(clicks_data)} clicks")
    cursor.close()

def verify_data(connection):
    """Verify data was loaded correctly"""
    cursor = connection.cursor()
    
    print("\n" + "="*50)
    print("DATA VERIFICATION")
    print("="*50)
    
    # Count records
    cursor.execute("SELECT COUNT(*) FROM sessions")
    sessions_count = cursor.fetchone()[0]
    print(f"Sessions: {sessions_count}")
    
    cursor.execute("SELECT COUNT(*) FROM products")
    products_count = cursor.fetchone()[0]
    print(f"Products: {products_count}")
    
    cursor.execute("SELECT COUNT(*) FROM clicks")
    clicks_count = cursor.fetchone()[0]
    print(f"Clicks: {clicks_count}")
    
    # Sample data
    print("\nSample session summary:")
    cursor.execute("SELECT * FROM session_summary LIMIT 5")
    for row in cursor.fetchall():
        print(f"  Session {row[0]}: {row[1]}, {row[5]} clicks, {row[6]} unique products")
    
    print("\nTop 5 popular products:")
    cursor.execute("SELECT * FROM product_popularity ORDER BY total_clicks DESC LIMIT 5")
    for row in cursor.fetchall():
        print(f"  {row[1]} ({row[2]}): {row[5]} clicks from {row[6]} sessions")
    
    cursor.close()

def main():
    """Main execution function"""
    print("="*50)
    print("E-COMMERCE CLICKSTREAM DATA LOADER")
    print("="*50)
    
    # Path to cleaned CSV file
    csv_path = '../data/clean/e-shop_clothing_2008_processed.csv'
    
    # Check if file exists, if not use raw data
    if not os.path.exists(csv_path):
        csv_path = '../data/raw/e-shop_clothing_2008.csv'
        print(f"⚠ Using raw data file: {csv_path}")
    else:
        print(f"Using cleaned data file: {csv_path}")
    
    # Load data
    df = load_csv_data(csv_path)
    
    # Connect to database
    connection = create_connection()
    
    try:
        # Populate tables
        print("\nPopulating database tables...")
        populate_sessions(connection, df)
        populate_products(connection, df)
        populate_clicks(connection, df)
        
        # Verify
        verify_data(connection)
        
        print("\n" + "="*50)
        print("✓ DATA LOADING COMPLETED SUCCESSFULLY")
        print("="*50)
        
    except Error as e:
        print(f"\n✗ Error during data loading: {e}")
        connection.rollback()
    finally:
        if connection.is_connected():
            connection.close()
            print("\n✓ Database connection closed")

if __name__ == "__main__":
    main()
