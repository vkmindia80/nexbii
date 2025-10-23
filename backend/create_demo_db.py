import sqlite3
import random
from datetime import datetime, timedelta
import uuid

def create_demo_database():
    """Create a comprehensive demo SQLite database with realistic sales data"""
    
    db_path = '/app/backend/demo_database.db'
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Drop existing tables if they exist
    cursor.execute('DROP TABLE IF EXISTS order_items')
    cursor.execute('DROP TABLE IF EXISTS orders')
    cursor.execute('DROP TABLE IF EXISTS products')
    cursor.execute('DROP TABLE IF EXISTS customers')
    cursor.execute('DROP TABLE IF EXISTS user_activities')
    
    # Create Products table
    cursor.execute('''
        CREATE TABLE products (
            id TEXT PRIMARY KEY,
            product_name TEXT NOT NULL,
            category TEXT NOT NULL,
            price REAL NOT NULL,
            cost REAL NOT NULL,
            stock_quantity INTEGER NOT NULL
        )
    ''')
    
    # Create Customers table
    cursor.execute('''
        CREATE TABLE customers (
            id TEXT PRIMARY KEY,
            customer_name TEXT NOT NULL,
            email TEXT NOT NULL,
            customer_segment TEXT NOT NULL,
            region TEXT NOT NULL,
            joined_date TEXT NOT NULL
        )
    ''')
    
    # Create Orders table
    cursor.execute('''
        CREATE TABLE orders (
            id TEXT PRIMARY KEY,
            customer_id TEXT NOT NULL,
            order_date TEXT NOT NULL,
            amount REAL NOT NULL,
            status TEXT NOT NULL,
            region TEXT NOT NULL,
            FOREIGN KEY (customer_id) REFERENCES customers(id)
        )
    ''')
    
    # Create Order Items table
    cursor.execute('''
        CREATE TABLE order_items (
            id TEXT PRIMARY KEY,
            order_id TEXT NOT NULL,
            product_id TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            price REAL NOT NULL,
            FOREIGN KEY (order_id) REFERENCES orders(id),
            FOREIGN KEY (product_id) REFERENCES products(id)
        )
    ''')
    
    # Create User Activities table
    cursor.execute('''
        CREATE TABLE user_activities (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            activity_type TEXT NOT NULL,
            activity_timestamp TEXT NOT NULL,
            region TEXT NOT NULL
        )
    ''')
    
    # Insert Products - More realistic business inventory
    products = [
        ('Laptop Pro 15', 'Electronics', 1299.99, 800),
        ('Wireless Mouse', 'Electronics', 29.99, 15),
        ('USB-C Cable', 'Accessories', 19.99, 8),
        ('Desk Chair Executive', 'Furniture', 299.99, 150),
        ('Standing Desk Electric', 'Furniture', 599.99, 350),
        ('Monitor 27" 4K', 'Electronics', 349.99, 200),
        ('Keyboard Mechanical RGB', 'Electronics', 149.99, 80),
        ('Webcam HD 1080p', 'Electronics', 89.99, 45),
        ('LED Desk Lamp', 'Accessories', 49.99, 25),
        ('Premium Notebook Set', 'Office Supplies', 14.99, 5),
        ('Aluminum Phone Stand', 'Accessories', 24.99, 12),
        ('Noise Cancelling Headphones', 'Electronics', 199.99, 100),
        ('Tablet 10" WiFi', 'Electronics', 449.99, 280),
        ('External SSD 1TB', 'Electronics', 129.99, 70),
        ('Wireless Charger Fast', 'Accessories', 39.99, 18),
        ('Ergonomic Keyboard', 'Electronics', 89.99, 45),
        ('USB Hub 7-Port', 'Accessories', 34.99, 18),
        ('Monitor Arm Dual', 'Furniture', 179.99, 90),
        ('Laptop Stand Aluminum', 'Accessories', 59.99, 30),
        ('Cable Management Kit', 'Accessories', 19.99, 10),
        ('Bluetooth Speaker', 'Electronics', 79.99, 40),
        ('Desk Organizer Set', 'Office Supplies', 24.99, 12),
        ('Mousepad Extended', 'Accessories', 29.99, 15),
        ('Webcam Privacy Cover', 'Accessories', 9.99, 3),
        ('Portable Hard Drive 2TB', 'Electronics', 89.99, 50),
    ]
    
    product_ids = []
    for name, category, price, cost in products:
        product_id = str(uuid.uuid4())
        product_ids.append((product_id, name, category, price))
        stock = random.randint(50, 500)
        cursor.execute(
            'INSERT INTO products VALUES (?, ?, ?, ?, ?, ?)',
            (product_id, name, category, price, cost, stock)
        )
    
    # Insert Customers
    segments = ['Enterprise', 'SMB', 'Startup', 'Individual']
    regions = ['North America', 'Europe', 'Asia Pacific', 'Latin America']
    
    customer_ids = []
    first_names = ['John', 'Jane', 'Michael', 'Sarah', 'David', 'Emily', 'Robert', 'Lisa', 'James', 'Maria', 
                   'William', 'Jennifer', 'Richard', 'Linda', 'Thomas', 'Patricia', 'Charles', 'Barbara', 
                   'Daniel', 'Susan', 'Matthew', 'Jessica', 'Anthony', 'Karen', 'Mark', 'Nancy']
    last_names = ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis', 'Rodriguez', 
                  'Martinez', 'Hernandez', 'Lopez', 'Gonzalez', 'Wilson', 'Anderson', 'Thomas', 'Taylor', 
                  'Moore', 'Jackson', 'Martin', 'Lee', 'Thompson', 'White', 'Harris', 'Clark', 'Lewis']
    
    for i in range(200):
        customer_id = str(uuid.uuid4())
        customer_ids.append(customer_id)
        first_name = random.choice(first_names)
        last_name = random.choice(last_names)
        name = f'{first_name} {last_name}'
        email = f'{first_name.lower()}.{last_name.lower()}{random.randint(1, 999)}@example.com'
        segment = random.choice(segments)
        region = random.choice(regions)
        joined_date = (datetime.now() - timedelta(days=random.randint(30, 730))).strftime('%Y-%m-%d')
        
        cursor.execute(
            'INSERT INTO customers VALUES (?, ?, ?, ?, ?, ?)',
            (customer_id, name, email, segment, region, joined_date)
        )
    
    # Insert Orders and Order Items - More realistic distribution
    start_date = datetime.now() - timedelta(days=365)
    
    for i in range(1500):  # Increased from 1000 to 1500 orders
        order_id = str(uuid.uuid4())
        customer_id = random.choice(customer_ids)
        order_date = (start_date + timedelta(days=random.randint(0, 365))).strftime('%Y-%m-%d')
        status = random.choice(['completed', 'completed', 'completed', 'pending', 'cancelled'])
        region = random.choice(regions)
        
        # Get customer's region
        cursor.execute('SELECT region FROM customers WHERE id = ?', (customer_id,))
        customer_region = cursor.fetchone()[0]
        
        # Generate 1-5 items per order
        num_items = random.randint(1, 5)
        order_total = 0
        
        for _ in range(num_items):
            item_id = str(uuid.uuid4())
            product_id, product_name, category, price = random.choice(product_ids)
            quantity = random.randint(1, 3)
            item_total = price * quantity
            order_total += item_total
            
            cursor.execute(
                'INSERT INTO order_items VALUES (?, ?, ?, ?, ?)',
                (item_id, order_id, product_id, quantity, price)
            )
        
        cursor.execute(
            'INSERT INTO orders VALUES (?, ?, ?, ?, ?, ?)',
            (order_id, customer_id, order_date, order_total, status, customer_region)
        )
    
    # Insert User Activities
    activity_types = ['login', 'view_product', 'add_to_cart', 'purchase', 'logout']
    
    for i in range(5000):
        activity_id = str(uuid.uuid4())
        user_id = f'user_{random.randint(1, 300)}'
        activity_type = random.choice(activity_types)
        activity_timestamp = (datetime.now() - timedelta(days=random.randint(0, 90), 
                                                         hours=random.randint(0, 23),
                                                         minutes=random.randint(0, 59))).strftime('%Y-%m-%d %H:%M:%S')
        region = random.choice(regions)
        
        cursor.execute(
            'INSERT INTO user_activities VALUES (?, ?, ?, ?, ?)',
            (activity_id, user_id, activity_type, activity_timestamp, region)
        )
    
    conn.commit()
    conn.close()
    
    print(f'✅ Demo database created successfully at {db_path}')
    print(f'   - Products: {len(products)}')
    print(f'   - Customers: 200')
    print(f'   - Orders: 1500')
    print(f'   - Order Items: ~3750')
    print(f'   - User Activities: 5000')
    print(f'\\n📊 Database includes realistic business scenarios:')
    print(f'   - Sales analytics across multiple regions')
    print(f'   - Customer segmentation (Enterprise, SMB, Startup, Individual)')
    print(f'   - Product inventory with categories')
    print(f'   - User activity tracking for analytics')

if __name__ == '__main__':
    create_demo_database()
