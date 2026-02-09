"""
Flask API for E-Commerce Clickstream Data
Exposes database data via RESTful API endpoints
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import mysql.connector
from mysql.connector import Error
from datetime import datetime
import os

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Database configuration
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', 'your_password'),
    'database': os.getenv('DB_NAME', 'ecommerce_clickstream')
}

def get_db_connection():
    """Create and return database connection"""
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        return connection
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None

def dict_fetchall(cursor):
    """Convert cursor results to list of dictionaries"""
    columns = [col[0] for col in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]

# ============================================
# API ENDPOINTS
# ============================================

@app.route('/')
def home():
    """API documentation"""
    return jsonify({
        'message': 'E-Commerce Clickstream API',
        'version': '1.0',
        'endpoints': {
            '/': 'API documentation (this page)',
            '/api/sessions': 'Get all sessions (with pagination)',
            '/api/sessions/<id>': 'Get specific session details',
            '/api/sessions/<id>/clicks': 'Get all clicks for a session',
            '/api/products': 'Get all products (with pagination)',
            '/api/products/<id>': 'Get specific product details',
            '/api/products/popular': 'Get most popular products',
            '/api/clicks': 'Get all clicks (with pagination)',
            '/api/stats': 'Get database statistics',
            '/api/stats/countries': 'Get statistics by country',
            '/api/stats/categories': 'Get statistics by category'
        },
        'query_parameters': {
            'page': 'Page number (default: 1)',
            'per_page': 'Items per page (default: 20, max: 100)',
            'limit': 'Limit results (for popular products)'
        }
    })

@app.route('/api/sessions', methods=['GET'])
def get_sessions():
    """Get all sessions with pagination"""
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 20, type=int), 100)
    offset = (page - 1) * per_page
    
    connection = get_db_connection()
    if not connection:
        return jsonify({'error': 'Database connection failed'}), 500
    
    cursor = connection.cursor()
    
    # Get total count
    cursor.execute("SELECT COUNT(*) FROM session_summary")
    total = cursor.fetchone()[0]
    
    # Get paginated data
    query = f"SELECT * FROM session_summary LIMIT {per_page} OFFSET {offset}"
    cursor.execute(query)
    sessions = dict_fetchall(cursor)
    
    cursor.close()
    connection.close()
    
    return jsonify({
        'page': page,
        'per_page': per_page,
        'total': total,
        'total_pages': (total + per_page - 1) // per_page,
        'data': sessions
    })

@app.route('/api/sessions/<int:session_id>', methods=['GET'])
def get_session(session_id):
    """Get specific session details"""
    connection = get_db_connection()
    if not connection:
        return jsonify({'error': 'Database connection failed'}), 500
    
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM session_summary WHERE session_id = %s", (session_id,))
    session = dict_fetchall(cursor)
    
    cursor.close()
    connection.close()
    
    if not session:
        return jsonify({'error': 'Session not found'}), 404
    
    return jsonify(session[0])

@app.route('/api/sessions/<int:session_id>/clicks', methods=['GET'])
def get_session_clicks(session_id):
    """Get all clicks for a specific session"""
    connection = get_db_connection()
    if not connection:
        return jsonify({'error': 'Database connection failed'}), 500
    
    cursor = connection.cursor()
    query = """
        SELECT * FROM click_details 
        WHERE session_id = %s 
        ORDER BY click_order
    """
    cursor.execute(query, (session_id,))
    clicks = dict_fetchall(cursor)
    
    cursor.close()
    connection.close()
    
    return jsonify({
        'session_id': session_id,
        'total_clicks': len(clicks),
        'clicks': clicks
    })

@app.route('/api/products', methods=['GET'])
def get_products():
    """Get all products with pagination"""
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 20, type=int), 100)
    offset = (page - 1) * per_page
    
    connection = get_db_connection()
    if not connection:
        return jsonify({'error': 'Database connection failed'}), 500
    
    cursor = connection.cursor()
    
    # Get total count
    cursor.execute("SELECT COUNT(*) FROM products")
    total = cursor.fetchone()[0]
    
    # Get paginated data
    query = f"SELECT * FROM products LIMIT {per_page} OFFSET {offset}"
    cursor.execute(query)
    products = dict_fetchall(cursor)
    
    cursor.close()
    connection.close()
    
    return jsonify({
        'page': page,
        'per_page': per_page,
        'total': total,
        'total_pages': (total + per_page - 1) // per_page,
        'data': products
    })

@app.route('/api/products/<int:product_id>', methods=['GET'])
def get_product(product_id):
    """Get specific product details"""
    connection = get_db_connection()
    if not connection:
        return jsonify({'error': 'Database connection failed'}), 500
    
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM product_popularity WHERE product_id = %s", (product_id,))
    product = dict_fetchall(cursor)
    
    cursor.close()
    connection.close()
    
    if not product:
        return jsonify({'error': 'Product not found'}), 404
    
    return jsonify(product[0])

@app.route('/api/products/popular', methods=['GET'])
def get_popular_products():
    """Get most popular products"""
    limit = min(request.args.get('limit', 10, type=int), 100)
    
    connection = get_db_connection()
    if not connection:
        return jsonify({'error': 'Database connection failed'}), 500
    
    cursor = connection.cursor()
    query = f"SELECT * FROM product_popularity ORDER BY total_clicks DESC LIMIT {limit}"
    cursor.execute(query)
    products = dict_fetchall(cursor)
    
    cursor.close()
    connection.close()
    
    return jsonify({
        'limit': limit,
        'data': products
    })

@app.route('/api/clicks', methods=['GET'])
def get_clicks():
    """Get all clicks with pagination"""
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 20, type=int), 100)
    offset = (page - 1) * per_page
    
    connection = get_db_connection()
    if not connection:
        return jsonify({'error': 'Database connection failed'}), 500
    
    cursor = connection.cursor()
    
    # Get total count
    cursor.execute("SELECT COUNT(*) FROM clicks")
    total = cursor.fetchone()[0]
    
    # Get paginated data
    query = f"SELECT * FROM click_details LIMIT {per_page} OFFSET {offset}"
    cursor.execute(query)
    clicks = dict_fetchall(cursor)
    
    cursor.close()
    connection.close()
    
    return jsonify({
        'page': page,
        'per_page': per_page,
        'total': total,
        'total_pages': (total + per_page - 1) // per_page,
        'data': clicks
    })

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get overall database statistics"""
    connection = get_db_connection()
    if not connection:
        return jsonify({'error': 'Database connection failed'}), 500
    
    cursor = connection.cursor()
    
    stats = {}
    
    # Total counts
    cursor.execute("SELECT COUNT(*) FROM sessions")
    stats['total_sessions'] = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM products")
    stats['total_products'] = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM clicks")
    stats['total_clicks'] = cursor.fetchone()[0]
    
    # Average clicks per session
    cursor.execute("SELECT AVG(total_clicks) FROM session_summary")
    stats['avg_clicks_per_session'] = round(cursor.fetchone()[0], 2)
    
    # Date range
    cursor.execute("SELECT MIN(year), MIN(month), MAX(year), MAX(month) FROM sessions")
    min_year, min_month, max_year, max_month = cursor.fetchone()
    stats['date_range'] = {
        'start': f"{min_year}-{min_month:02d}",
        'end': f"{max_year}-{max_month:02d}"
    }
    
    cursor.close()
    connection.close()
    
    return jsonify(stats)

@app.route('/api/stats/countries', methods=['GET'])
def get_country_stats():
    """Get statistics by country"""
    connection = get_db_connection()
    if not connection:
        return jsonify({'error': 'Database connection failed'}), 500
    
    cursor = connection.cursor()
    query = """
        SELECT 
            country,
            COUNT(*) as total_sessions,
            SUM(total_clicks) as total_clicks,
            AVG(total_clicks) as avg_clicks_per_session,
            AVG(unique_products) as avg_unique_products
        FROM session_summary
        GROUP BY country
        ORDER BY total_sessions DESC
    """
    cursor.execute(query)
    stats = dict_fetchall(cursor)
    
    cursor.close()
    connection.close()
    
    return jsonify(stats)

@app.route('/api/stats/categories', methods=['GET'])
def get_category_stats():
    """Get statistics by product category"""
    connection = get_db_connection()
    if not connection:
        return jsonify({'error': 'Database connection failed'}), 500
    
    cursor = connection.cursor()
    query = """
        SELECT 
            main_category,
            COUNT(*) as total_products,
            SUM(total_clicks) as total_clicks,
            AVG(total_clicks) as avg_clicks_per_product,
            SUM(unique_sessions) as total_sessions
        FROM product_popularity
        GROUP BY main_category
        ORDER BY total_clicks DESC
    """
    cursor.execute(query)
    stats = dict_fetchall(cursor)
    
    cursor.close()
    connection.close()
    
    return jsonify(stats)

# ============================================
# ERROR HANDLERS
# ============================================

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

# ============================================
# RUN APPLICATION
# ============================================

if __name__ == '__main__':
    print("="*50)
    print("E-COMMERCE CLICKSTREAM API")
    print("="*50)
    print("Starting Flask server...")
    print("API Documentation: http://localhost:5000/")
    print("="*50)
    app.run(debug=True, host='0.0.0.0', port=5000)
