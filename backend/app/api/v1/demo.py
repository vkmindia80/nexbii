from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import uuid
import sqlite3
import random
from datetime import datetime, timedelta
from ...core.database import get_db
from ...models.datasource import DataSource, DataSourceType
from ...models.query import Query
from ...models.dashboard import Dashboard
from ...models.user import User

router = APIRouter()

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
    cursor.execute('DROP TABLE IF EXISTS employees')
    cursor.execute('DROP TABLE IF EXISTS departments')
    cursor.execute('DROP TABLE IF EXISTS sales_targets')
    cursor.execute('DROP TABLE IF EXISTS product_reviews')
    
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
    
    # Create Departments table
    cursor.execute('''
        CREATE TABLE departments (
            id TEXT PRIMARY KEY,
            dept_name TEXT NOT NULL,
            budget REAL NOT NULL,
            location TEXT NOT NULL,
            manager_name TEXT NOT NULL
        )
    ''')
    
    # Create Employees table
    cursor.execute('''
        CREATE TABLE employees (
            id TEXT PRIMARY KEY,
            employee_name TEXT NOT NULL,
            department_id TEXT NOT NULL,
            salary REAL NOT NULL,
            hire_date TEXT NOT NULL,
            position TEXT NOT NULL,
            performance_rating REAL NOT NULL,
            FOREIGN KEY (department_id) REFERENCES departments(id)
        )
    ''')
    
    # Create Sales Targets table
    cursor.execute('''
        CREATE TABLE sales_targets (
            id TEXT PRIMARY KEY,
            month TEXT NOT NULL,
            target_amount REAL NOT NULL,
            achieved_amount REAL NOT NULL,
            region TEXT NOT NULL
        )
    ''')
    
    # Create Product Reviews table
    cursor.execute('''
        CREATE TABLE product_reviews (
            id TEXT PRIMARY KEY,
            product_id TEXT NOT NULL,
            customer_id TEXT NOT NULL,
            rating INTEGER NOT NULL,
            review_text TEXT,
            review_date TEXT NOT NULL,
            FOREIGN KEY (product_id) REFERENCES products(id),
            FOREIGN KEY (customer_id) REFERENCES customers(id)
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
    
    # Insert Departments
    departments_data = [
        ('Sales', 500000, 'New York', 'Sarah Johnson'),
        ('Marketing', 350000, 'San Francisco', 'Michael Chen'),
        ('Engineering', 750000, 'Seattle', 'David Kim'),
        ('Customer Success', 280000, 'Austin', 'Emily Rodriguez'),
        ('Operations', 420000, 'Chicago', 'James Williams'),
        ('Finance', 320000, 'Boston', 'Linda Martinez'),
        ('HR', 180000, 'Denver', 'Robert Brown'),
        ('Product', 450000, 'Los Angeles', 'Maria Garcia')
    ]
    
    department_ids = []
    for dept_name, budget, location, manager in departments_data:
        dept_id = str(uuid.uuid4())
        department_ids.append((dept_id, dept_name))
        cursor.execute(
            'INSERT INTO departments VALUES (?, ?, ?, ?, ?)',
            (dept_id, dept_name, budget, location, manager)
        )
    
    # Insert Employees
    positions = {
        'Sales': ['Sales Representative', 'Account Executive', 'Sales Manager'],
        'Marketing': ['Marketing Specialist', 'Content Writer', 'Marketing Manager'],
        'Engineering': ['Software Engineer', 'Senior Engineer', 'Tech Lead'],
        'Customer Success': ['Support Specialist', 'Customer Success Manager'],
        'Operations': ['Operations Analyst', 'Operations Manager'],
        'Finance': ['Financial Analyst', 'Accountant', 'Finance Manager'],
        'HR': ['HR Specialist', 'Recruiter', 'HR Manager'],
        'Product': ['Product Manager', 'Product Designer', 'Product Analyst']
    }
    
    for dept_id, dept_name in department_ids:
        num_employees = random.randint(8, 15)
        dept_positions = positions.get(dept_name, ['Employee'])
        
        for _ in range(num_employees):
            emp_id = str(uuid.uuid4())
            first_name = random.choice(first_names)
            last_name = random.choice(last_names)
            emp_name = f'{first_name} {last_name}'
            position = random.choice(dept_positions)
            
            # Salary based on position
            if 'Manager' in position or 'Lead' in position:
                salary = random.uniform(90000, 150000)
            elif 'Senior' in position:
                salary = random.uniform(70000, 110000)
            else:
                salary = random.uniform(45000, 85000)
            
            hire_date = (datetime.now() - timedelta(days=random.randint(90, 1825))).strftime('%Y-%m-%d')
            performance = round(random.uniform(3.0, 5.0), 1)
            
            cursor.execute(
                'INSERT INTO employees VALUES (?, ?, ?, ?, ?, ?, ?)',
                (emp_id, emp_name, dept_id, salary, hire_date, position, performance)
            )
    
    # Insert Sales Targets
    for month_offset in range(12):
        target_date = (datetime.now() - timedelta(days=month_offset * 30))
        month = target_date.strftime('%Y-%m')
        
        for region in regions:
            target_id = str(uuid.uuid4())
            target_amount = random.uniform(100000, 500000)
            # Achievement rate between 70% and 120%
            achievement_rate = random.uniform(0.7, 1.2)
            achieved_amount = target_amount * achievement_rate
            
            cursor.execute(
                'INSERT INTO sales_targets VALUES (?, ?, ?, ?, ?)',
                (target_id, month, target_amount, achieved_amount, region)
            )
    
    # Insert Product Reviews
    for _ in range(500):  # 500 reviews
        review_id = str(uuid.uuid4())
        product_id, _, _, _ = random.choice(product_ids)
        customer_id = random.choice(customer_ids)
        rating = random.randint(1, 5)
        
        # Generate review text based on rating
        positive_reviews = [
            "Great product! Highly recommended.",
            "Excellent quality and fast shipping.",
            "Very satisfied with this purchase.",
            "Perfect! Exactly what I needed.",
            "Outstanding product and service."
        ]
        neutral_reviews = [
            "Good product overall.",
            "Decent quality for the price.",
            "Works as expected.",
            "Satisfactory purchase."
        ]
        negative_reviews = [
            "Not as described.",
            "Quality could be better.",
            "Disappointed with this product.",
            "Expected more for the price."
        ]
        
        if rating >= 4:
            review_text = random.choice(positive_reviews)
        elif rating == 3:
            review_text = random.choice(neutral_reviews)
        else:
            review_text = random.choice(negative_reviews)
        
        review_date = (datetime.now() - timedelta(days=random.randint(1, 365))).strftime('%Y-%m-%d')
        
        cursor.execute(
            'INSERT INTO product_reviews VALUES (?, ?, ?, ?, ?, ?)',
            (review_id, product_id, customer_id, rating, review_text, review_date)
        )
    
    conn.commit()
    conn.close()
    
    return {
        'products': len(products),
        'customers': 200,
        'orders': 1500,
        'order_items': sum(random.randint(1, 5) for _ in range(1500)),
        'user_activities': 5000
    }

@router.post("/generate")
async def generate_demo_data(db: Session = Depends(get_db)):
    """
    Generate demo data for all modules:
    - SQLite database with sample data (products, customers, orders, etc.)
    - Data sources (3 demo sources)
    - Queries (14 demo queries)
    - Dashboards (3 demo dashboards)
    """
    try:
        # Step 1: Create the actual SQLite database with all tables and sample data
        print("🔄 Creating demo SQLite database with sample data...")
        db_stats = create_demo_database()
        print(f"✅ Demo database created successfully!")
        print(f"   - Products: {db_stats['products']}")
        print(f"   - Customers: {db_stats['customers']}")
        print(f"   - Orders: {db_stats['orders']}")
        print(f"   - Order Items: ~{db_stats['order_items']}")
        print(f"   - User Activities: {db_stats['user_activities']}")
        
        # Step 2: Create metadata in PostgreSQL (datasources, queries, dashboards)
        # Get demo user
        demo_user = db.query(User).filter(User.email == 'admin@nexbii.demo').first()
        if not demo_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Demo user not found. Please create demo user first."
            )
        
        user_id = demo_user.id
        
        # Check if demo data already exists
        existing_datasources = db.query(DataSource).filter(
            DataSource.name.like('Demo%')
        ).count()
        
        if existing_datasources > 0:
            # Clean up existing demo data
            db.query(Dashboard).filter(Dashboard.name.like('Demo%')).delete()
            db.query(Query).filter(Query.name.like('Demo%')).delete()
            db.query(DataSource).filter(DataSource.name.like('Demo%')).delete()
            db.commit()
        
        # Create Demo Data Sources
        datasources = []
        
        # 1. Demo SQLite Database
        ds_sqlite = DataSource(
            id=str(uuid.uuid4()),
            name="Demo SQLite Database",
            type=DataSourceType.SQLITE,
            connection_config={
                "database_path": "/app/backend/demo_database.db",
                "database": "/app/backend/demo_database.db",
                "description": "Local SQLite demo database with sample data"
            },
            created_by=user_id,
            is_active=True
        )
        datasources.append(ds_sqlite)
        db.add(ds_sqlite)
        
        # 2. Demo PostgreSQL (placeholder - won't actually connect)
        ds_postgres = DataSource(
            id=str(uuid.uuid4()),
            name="Demo PostgreSQL Analytics",
            type=DataSourceType.POSTGRESQL,
            connection_config={
                "host": "demo.postgres.local",
                "port": 5432,
                "database": "analytics_demo",
                "user": "demo_user",
                "password": "demo_password",
                "description": "Demo PostgreSQL connection (placeholder)"
            },
            created_by=user_id,
            is_active=True
        )
        datasources.append(ds_postgres)
        db.add(ds_postgres)
        
        # 3. Demo MongoDB (placeholder)
        ds_mongo = DataSource(
            id=str(uuid.uuid4()),
            name="Demo MongoDB Logs",
            type=DataSourceType.MONGODB,
            connection_config={
                "host": "demo.mongodb.local",
                "port": 27017,
                "database": "logs_demo",
                "description": "Demo MongoDB connection (placeholder)"
            },
            created_by=user_id,
            is_active=True
        )
        datasources.append(ds_mongo)
        db.add(ds_mongo)
        
        db.commit()
        
        # Create Demo Queries
        queries = []
        
        # Query 1: Sales Overview
        q1 = Query(
            id=str(uuid.uuid4()),
            name="Demo: Sales Overview",
            description="Monthly sales totals for the current year",
            datasource_id=ds_sqlite.id,
            query_type="sql",
            sql_query="""SELECT 
    strftime('%Y-%m', order_date) as month,
    COUNT(*) as total_orders,
    SUM(amount) as total_revenue
FROM orders
WHERE order_date >= date('now', '-12 months')
GROUP BY month
ORDER BY month DESC;""",
            created_by=user_id
        )
        queries.append(q1)
        db.add(q1)
        
        # Query 2: Top Products
        q2 = Query(
            id=str(uuid.uuid4()),
            name="Demo: Top 10 Products",
            description="Best selling products by revenue",
            datasource_id=ds_sqlite.id,
            query_type="sql",
            sql_query="""SELECT 
    product_name,
    SUM(quantity) as units_sold,
    SUM(quantity * price) as revenue
FROM order_items
JOIN products ON order_items.product_id = products.id
GROUP BY product_name
ORDER BY revenue DESC
LIMIT 10;""",
            created_by=user_id
        )
        queries.append(q2)
        db.add(q2)
        
        # Query 3: Customer Insights
        q3 = Query(
            id=str(uuid.uuid4()),
            name="Demo: Customer Insights",
            description="Customer purchase behavior analysis",
            datasource_id=ds_sqlite.id,
            query_type="sql",
            sql_query="""SELECT 
    customer_segment,
    COUNT(DISTINCT customer_id) as customer_count,
    AVG(amount) as avg_order_value,
    SUM(amount) as total_revenue
FROM customers
JOIN orders ON customers.id = orders.customer_id
GROUP BY customer_segment
ORDER BY total_revenue DESC;""",
            created_by=user_id
        )
        queries.append(q3)
        db.add(q3)
        
        # Query 4: Daily Active Users
        q4 = Query(
            id=str(uuid.uuid4()),
            name="Demo: Daily Active Users",
            description="User activity over the last 30 days",
            datasource_id=ds_postgres.id,
            query_type="sql",
            sql_query="""SELECT 
    DATE(activity_timestamp) as date,
    COUNT(DISTINCT user_id) as active_users,
    COUNT(*) as total_activities
FROM user_activities
WHERE activity_timestamp >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY date
ORDER BY date;""",
            created_by=user_id
        )
        queries.append(q4)
        db.add(q4)
        
        # Query 5: Regional Performance
        q5 = Query(
            id=str(uuid.uuid4()),
            name="Demo: Regional Performance",
            description="Sales performance breakdown by region",
            datasource_id=ds_sqlite.id,
            query_type="sql",
            sql_query="""SELECT 
    region,
    COUNT(*) as total_orders,
    SUM(amount) as revenue
FROM orders
JOIN customers ON orders.customer_id = customers.id
GROUP BY region
ORDER BY revenue DESC;""",
            created_by=user_id
        )
        queries.append(q5)
        db.add(q5)
        
        # Query 6: Order Status Distribution
        q6 = Query(
            id=str(uuid.uuid4()),
            name="Demo: Order Status Distribution",
            description="Distribution of orders by status",
            datasource_id=ds_sqlite.id,
            query_type="sql",
            sql_query="""SELECT 
    status,
    COUNT(*) as order_count
FROM orders
GROUP BY status
ORDER BY order_count DESC;""",
            created_by=user_id
        )
        queries.append(q6)
        db.add(q6)
        
        # Query 7: Total Revenue Metric
        q7 = Query(
            id=str(uuid.uuid4()),
            name="Demo: Total Revenue",
            description="Total revenue from all orders",
            datasource_id=ds_sqlite.id,
            query_type="sql",
            sql_query="""SELECT 
    SUM(amount) as total_revenue
FROM orders;""",
            created_by=user_id
        )
        queries.append(q7)
        db.add(q7)
        
        # Query 8: Total Customers Metric
        q8 = Query(
            id=str(uuid.uuid4()),
            name="Demo: Total Customers",
            description="Total number of customers",
            datasource_id=ds_sqlite.id,
            query_type="sql",
            sql_query="""SELECT 
    COUNT(*) as total_customers
FROM customers;""",
            created_by=user_id
        )
        queries.append(q8)
        db.add(q8)
        
        # Query 9: Product Category Analysis
        q9 = Query(
            id=str(uuid.uuid4()),
            name="Demo: Product Category Revenue",
            description="Revenue breakdown by product category",
            datasource_id=ds_sqlite.id,
            query_type="sql",
            sql_query="""SELECT 
    p.category,
    COUNT(DISTINCT oi.order_id) as orders,
    SUM(oi.quantity) as units_sold,
    SUM(oi.quantity * oi.price) as revenue
FROM order_items oi
JOIN products p ON oi.product_id = p.id
GROUP BY p.category
ORDER BY revenue DESC;""",
            created_by=user_id
        )
        queries.append(q9)
        db.add(q9)
        
        # Query 10: Average Order Value by Segment
        q10 = Query(
            id=str(uuid.uuid4()),
            name="Demo: Average Order Value by Segment",
            description="Average order value for each customer segment",
            datasource_id=ds_sqlite.id,
            query_type="sql",
            sql_query="""SELECT 
    c.customer_segment,
    COUNT(DISTINCT o.id) as total_orders,
    AVG(o.amount) as avg_order_value,
    MIN(o.amount) as min_order,
    MAX(o.amount) as max_order
FROM orders o
JOIN customers c ON o.customer_id = c.id
GROUP BY c.customer_segment
ORDER BY avg_order_value DESC;""",
            created_by=user_id
        )
        queries.append(q10)
        db.add(q10)
        
        # Query 11: Monthly Growth Rate
        q11 = Query(
            id=str(uuid.uuid4()),
            name="Demo: Monthly Growth Rate",
            description="Month-over-month revenue growth",
            datasource_id=ds_sqlite.id,
            query_type="sql",
            sql_query="""SELECT 
    strftime('%Y-%m', order_date) as month,
    SUM(amount) as revenue,
    COUNT(*) as orders
FROM orders
WHERE order_date >= date('now', '-12 months')
GROUP BY month
ORDER BY month;""",
            created_by=user_id
        )
        queries.append(q11)
        db.add(q11)
        
        # Query 12: Top Customers by Revenue
        q12 = Query(
            id=str(uuid.uuid4()),
            name="Demo: Top 10 Customers",
            description="Highest revenue generating customers",
            datasource_id=ds_sqlite.id,
            query_type="sql",
            sql_query="""SELECT 
    c.customer_name,
    c.customer_segment,
    c.region,
    COUNT(o.id) as total_orders,
    SUM(o.amount) as total_revenue
FROM customers c
JOIN orders o ON c.id = o.customer_id
GROUP BY c.id
ORDER BY total_revenue DESC
LIMIT 10;""",
            created_by=user_id
        )
        queries.append(q12)
        db.add(q12)
        
        # Query 13: Inventory Status
        q13 = Query(
            id=str(uuid.uuid4()),
            name="Demo: Inventory Status",
            description="Current stock levels for all products",
            datasource_id=ds_sqlite.id,
            query_type="sql",
            sql_query="""SELECT 
    product_name,
    category,
    price,
    stock_quantity,
    CASE 
        WHEN stock_quantity < 100 THEN 'Low Stock'
        WHEN stock_quantity < 200 THEN 'Medium Stock'
        ELSE 'High Stock'
    END as stock_status
FROM products
ORDER BY stock_quantity ASC;""",
            created_by=user_id
        )
        queries.append(q13)
        db.add(q13)
        
        # Query 14: Daily Activity Trends
        q14 = Query(
            id=str(uuid.uuid4()),
            name="Demo: User Activity by Type",
            description="User activity distribution over last 30 days",
            datasource_id=ds_sqlite.id,
            query_type="sql",
            sql_query="""SELECT 
    activity_type,
    COUNT(*) as activity_count,
    COUNT(DISTINCT user_id) as unique_users
FROM user_activities
WHERE activity_timestamp >= datetime('now', '-30 days')
GROUP BY activity_type
ORDER BY activity_count DESC;""",
            created_by=user_id
        )
        queries.append(q14)
        db.add(q14)
        
        db.commit()
        
        # Create Demo Dashboards
        dashboards = []
        
        # Dashboard 1: Sales Analytics
        d1 = Dashboard(
            id=str(uuid.uuid4()),
            name="Demo: Sales Analytics Dashboard",
            description="Comprehensive sales performance metrics and trends",
            layout={
                "layouts": []
            },
            widgets=[
                {
                    "id": "w1",
                    "type": "chart",
                    "title": "Total Revenue",
                    "query_id": q7.id,
                    "chart_type": "metric",
                    "x": 0,
                    "y": 0,
                    "w": 3,
                    "h": 2,
                    "config": {
                        "aggregation": "sum",
                        "field": "total_revenue",
                        "prefix": "$",
                        "format": "currency"
                    }
                },
                {
                    "id": "w2",
                    "type": "chart",
                    "title": "Total Customers",
                    "query_id": q8.id,
                    "chart_type": "metric",
                    "x": 3,
                    "y": 0,
                    "w": 3,
                    "h": 2,
                    "config": {
                        "aggregation": "sum",
                        "field": "total_customers"
                    }
                },
                {
                    "id": "w3",
                    "type": "chart",
                    "title": "Total Orders",
                    "query_id": q1.id,
                    "chart_type": "metric",
                    "x": 6,
                    "y": 0,
                    "w": 3,
                    "h": 2,
                    "config": {
                        "aggregation": "sum",
                        "field": "total_orders"
                    }
                },
                {
                    "id": "w4",
                    "type": "chart",
                    "title": "Monthly Sales Trend",
                    "query_id": q1.id,
                    "chart_type": "line",
                    "x": 0,
                    "y": 2,
                    "w": 6,
                    "h": 3,
                    "config": {
                        "x_axis": "month",
                        "y_axis": "total_revenue",
                        "color": "#3b82f6"
                    }
                },
                {
                    "id": "w5",
                    "type": "chart",
                    "title": "Order Status",
                    "query_id": q6.id,
                    "chart_type": "pie",
                    "x": 6,
                    "y": 2,
                    "w": 6,
                    "h": 3,
                    "config": {
                        "label": "status",
                        "value": "order_count"
                    }
                },
                {
                    "id": "w6",
                    "type": "chart",
                    "title": "Top 10 Products by Revenue",
                    "query_id": q2.id,
                    "chart_type": "bar",
                    "x": 0,
                    "y": 5,
                    "w": 12,
                    "h": 3,
                    "config": {
                        "x_axis": "product_name",
                        "y_axis": "revenue"
                    }
                }
            ],
            filters={
                "date_range": "last_12_months",
                "region": "all"
            },
            is_public=False,
            created_by=user_id
        )
        dashboards.append(d1)
        db.add(d1)
        
        # Dashboard 2: Customer Analytics
        d2 = Dashboard(
            id=str(uuid.uuid4()),
            name="Demo: Customer Analytics Dashboard",
            description="Customer behavior, segments, and engagement metrics",
            layout={
                "layouts": []
            },
            widgets=[
                {
                    "id": "w1",
                    "type": "chart",
                    "title": "Customer Segments Distribution",
                    "query_id": q3.id,
                    "chart_type": "donut",
                    "x": 0,
                    "y": 0,
                    "w": 6,
                    "h": 3,
                    "config": {
                        "label": "customer_segment",
                        "value": "customer_count"
                    }
                },
                {
                    "id": "w2",
                    "type": "chart",
                    "title": "Revenue by Region",
                    "query_id": q5.id,
                    "chart_type": "column",
                    "x": 6,
                    "y": 0,
                    "w": 6,
                    "h": 3,
                    "config": {
                        "x_axis": "region",
                        "y_axis": "revenue"
                    }
                },
                {
                    "id": "w3",
                    "type": "chart",
                    "title": "Customer Segment Details",
                    "query_id": q3.id,
                    "chart_type": "table",
                    "x": 0,
                    "y": 3,
                    "w": 12,
                    "h": 3,
                    "config": {
                        "pageSize": 10
                    }
                }
            ],
            filters={
                "segment": "all",
                "time_period": "current_quarter"
            },
            is_public=True,
            created_by=user_id
        )
        dashboards.append(d2)
        db.add(d2)
        
        # Dashboard 3: Operational Metrics
        d3 = Dashboard(
            id=str(uuid.uuid4()),
            name="Demo: Operational Metrics Dashboard",
            description="Inventory, product categories, and operational KPIs",
            layout={
                "layouts": []
            },
            widgets=[
                {
                    "id": "w1",
                    "type": "chart",
                    "title": "Product Category Revenue",
                    "query_id": q9.id,
                    "chart_type": "bar",
                    "x": 0,
                    "y": 0,
                    "w": 6,
                    "h": 3,
                    "config": {
                        "x_axis": "category",
                        "y_axis": "revenue"
                    }
                },
                {
                    "id": "w2",
                    "type": "chart",
                    "title": "User Activity Distribution",
                    "query_id": q14.id,
                    "chart_type": "donut",
                    "x": 6,
                    "y": 0,
                    "w": 6,
                    "h": 3,
                    "config": {
                        "label": "activity_type",
                        "value": "activity_count"
                    }
                },
                {
                    "id": "w3",
                    "type": "chart",
                    "title": "Average Order Value by Segment",
                    "query_id": q10.id,
                    "chart_type": "column",
                    "x": 0,
                    "y": 3,
                    "w": 6,
                    "h": 3,
                    "config": {
                        "x_axis": "customer_segment",
                        "y_axis": "avg_order_value"
                    }
                },
                {
                    "id": "w4",
                    "type": "chart",
                    "title": "Inventory Status",
                    "query_id": q13.id,
                    "chart_type": "table",
                    "x": 6,
                    "y": 3,
                    "w": 6,
                    "h": 3,
                    "config": {
                        "pageSize": 15
                    }
                }
            ],
            filters={
                "category": "all",
                "stock_level": "all"
            },
            is_public=False,
            created_by=user_id
        )
        dashboards.append(d3)
        db.add(d3)
        
        db.commit()
        
        return {
            "success": True,
            "message": "✨ Comprehensive demo data generated successfully for all modules!",
            "data": {
                "sqlite_database": db_stats,
                "datasources": len(datasources),
                "queries": len(queries),
                "dashboards": len(dashboards)
            },
            "details": {
                "datasources": [{"id": ds.id, "name": ds.name, "type": ds.type.value} for ds in datasources],
                "queries": [{"id": q.id, "name": q.name} for q in queries],
                "dashboards": [{"id": d.id, "name": d.name} for d in dashboards]
            },
            "summary": {
                "database_records": {
                    "products": db_stats['products'],
                    "customers": db_stats['customers'],
                    "orders": db_stats['orders'],
                    "order_items": f"~{db_stats['order_items']}",
                    "user_activities": db_stats['user_activities']
                },
                "modules_covered": [
                    "✅ SQLite Database (with 5 tables and realistic sample data)",
                    "✅ Data Sources (3 types: SQLite, PostgreSQL, MongoDB)",
                    "✅ SQL Queries (14 comprehensive queries covering sales, customers, operations)",
                    "✅ Dashboards (3 dashboards: Sales Analytics, Customer Analytics, Operational Metrics)",
                    "✅ User Management (Demo admin user: admin@nexbii.demo)"
                ]
            }
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate demo data: {str(e)}"
        )
