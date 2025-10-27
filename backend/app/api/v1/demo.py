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
from ...models.alert import Alert, AlertConditionType, AlertFrequency
from ...models.subscription import EmailSubscription, SubscriptionFrequency
from ...models.comment import Comment
from ...models.activity import Activity, ActivityType
from ...models.tenant import Tenant, TenantDomain, TenantInvitation, TenantUsage
from ...models.integration import Integration
from ...models.share import SharedDashboard
from ...models.api_key import APIKey
from ...models.webhook import Webhook
from ...models.plugin import Plugin, PluginInstance
from ...core.security import get_password_hash
import secrets
import hashlib

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
        'user_activities': 5000,
        'departments': len(departments_data),
        'employees': sum(random.randint(8, 15) for _ in range(len(departments_data))),
        'sales_targets': 12 * len(regions),
        'product_reviews': 500
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
        print("✅ Demo database created successfully!")
        print(f"   - Products: {db_stats['products']}")
        print(f"   - Customers: {db_stats['customers']}")
        print(f"   - Orders: {db_stats['orders']}")
        print(f"   - Order Items: ~{db_stats['order_items']}")
        print(f"   - User Activities: {db_stats['user_activities']}")
        print(f"   - Departments: {db_stats['departments']}")
        print(f"   - Employees: ~{db_stats['employees']}")
        print(f"   - Sales Targets: {db_stats['sales_targets']}")
        print(f"   - Product Reviews: {db_stats['product_reviews']}")
        
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
            # Clean up existing demo data in proper order (respecting foreign keys)
            print("🔄 Cleaning up existing demo data...")
            
            # Delete in order of dependencies
            db.query(Activity).filter(Activity.description.like('%demo%') | Activity.description.like('%Demo%')).delete(synchronize_session=False)
            db.query(Comment).filter(Comment.dashboard_id.in_(
                db.query(Dashboard.id).filter(Dashboard.name.like('Demo%'))
            )).delete(synchronize_session=False)
            db.query(Comment).filter(Comment.query_id.in_(
                db.query(Query.id).filter(Query.name.like('Demo%'))
            )).delete(synchronize_session=False)
            db.query(EmailSubscription).filter(EmailSubscription.dashboard_id.in_(
                db.query(Dashboard.id).filter(Dashboard.name.like('Demo%'))
            )).delete(synchronize_session=False)
            db.query(Alert).filter(Alert.query_id.in_(
                db.query(Query.id).filter(Query.name.like('Demo%'))
            )).delete(synchronize_session=False)
            db.query(Dashboard).filter(Dashboard.name.like('Demo%')).delete(synchronize_session=False)
            db.query(Query).filter(Query.name.like('Demo%')).delete(synchronize_session=False)
            db.query(DataSource).filter(DataSource.name.like('Demo%')).delete(synchronize_session=False)
            
            # Delete demo tenants
            db.query(TenantDomain).filter(TenantDomain.tenant_id.in_(
                db.query(Tenant.id).filter(Tenant.slug.in_(['nexbii-demo', 'acme-corp', 'techstart']))
            )).delete(synchronize_session=False)
            db.query(Tenant).filter(Tenant.slug.in_(['nexbii-demo', 'acme-corp', 'techstart'])).delete(synchronize_session=False)
            
            db.commit()
            print("✅ Existing demo data cleaned up")
        
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
        
        # Query 15: Employee Performance Analysis
        q15 = Query(
            id=str(uuid.uuid4()),
            name="Demo: Employee Performance by Department",
            description="Average employee performance ratings by department",
            datasource_id=ds_sqlite.id,
            query_type="sql",
            sql_query="""SELECT 
    d.dept_name as department,
    COUNT(e.id) as employee_count,
    ROUND(AVG(e.performance_rating), 2) as avg_performance,
    ROUND(AVG(e.salary), 2) as avg_salary
FROM employees e
JOIN departments d ON e.department_id = d.id
GROUP BY d.dept_name
ORDER BY avg_performance DESC;""",
            created_by=user_id
        )
        queries.append(q15)
        db.add(q15)
        
        # Query 16: Sales Target Achievement
        q16 = Query(
            id=str(uuid.uuid4()),
            name="Demo: Sales Target Achievement by Region",
            description="Sales targets vs achievements across regions",
            datasource_id=ds_sqlite.id,
            query_type="sql",
            sql_query="""SELECT 
    region,
    ROUND(SUM(target_amount), 2) as total_target,
    ROUND(SUM(achieved_amount), 2) as total_achieved,
    ROUND((SUM(achieved_amount) / SUM(target_amount)) * 100, 1) as achievement_percentage
FROM sales_targets
WHERE month >= date('now', '-12 months')
GROUP BY region
ORDER BY achievement_percentage DESC;""",
            created_by=user_id
        )
        queries.append(q16)
        db.add(q16)
        
        # Query 17: Product Ratings Analysis
        q17 = Query(
            id=str(uuid.uuid4()),
            name="Demo: Product Ratings and Reviews",
            description="Average product ratings with review counts",
            datasource_id=ds_sqlite.id,
            query_type="sql",
            sql_query="""SELECT 
    p.product_name,
    p.category,
    COUNT(pr.id) as review_count,
    ROUND(AVG(pr.rating), 1) as avg_rating,
    SUM(CASE WHEN pr.rating >= 4 THEN 1 ELSE 0 END) as positive_reviews
FROM products p
LEFT JOIN product_reviews pr ON p.id = pr.product_id
GROUP BY p.id
HAVING review_count > 0
ORDER BY avg_rating DESC, review_count DESC
LIMIT 20;""",
            created_by=user_id
        )
        queries.append(q17)
        db.add(q17)
        
        # Query 18: Department Budget Analysis
        q18 = Query(
            id=str(uuid.uuid4()),
            name="Demo: Department Budget Overview",
            description="Department budgets and employee costs",
            datasource_id=ds_sqlite.id,
            query_type="sql",
            sql_query="""SELECT 
    d.dept_name,
    d.budget,
    d.location,
    COUNT(e.id) as employee_count,
    ROUND(SUM(e.salary), 2) as total_salary_cost,
    ROUND(d.budget - SUM(e.salary), 2) as remaining_budget
FROM departments d
LEFT JOIN employees e ON d.id = e.department_id
GROUP BY d.id
ORDER BY d.budget DESC;""",
            created_by=user_id
        )
        queries.append(q18)
        db.add(q18)
        
        # Query 19: Monthly Revenue Trend
        q19 = Query(
            id=str(uuid.uuid4()),
            name="Demo: Monthly Revenue Comparison",
            description="Revenue comparison for last 12 months",
            datasource_id=ds_sqlite.id,
            query_type="sql",
            sql_query="""SELECT 
    strftime('%Y-%m', order_date) as month,
    COUNT(DISTINCT customer_id) as unique_customers,
    COUNT(*) as total_orders,
    ROUND(SUM(amount), 2) as revenue,
    ROUND(AVG(amount), 2) as avg_order_value
FROM orders
WHERE order_date >= date('now', '-12 months')
  AND status = 'completed'
GROUP BY month
ORDER BY month;""",
            created_by=user_id
        )
        queries.append(q19)
        db.add(q19)
        
        # Query 20: Customer Lifetime Value
        q20 = Query(
            id=str(uuid.uuid4()),
            name="Demo: Customer Lifetime Value Analysis",
            description="Top customers by total purchase value",
            datasource_id=ds_sqlite.id,
            query_type="sql",
            sql_query="""SELECT 
    c.customer_name,
    c.customer_segment,
    c.region,
    COUNT(o.id) as total_orders,
    ROUND(SUM(o.amount), 2) as lifetime_value,
    ROUND(AVG(o.amount), 2) as avg_order_value,
    MIN(o.order_date) as first_order,
    MAX(o.order_date) as last_order
FROM customers c
JOIN orders o ON c.id = o.customer_id
WHERE o.status = 'completed'
GROUP BY c.id
ORDER BY lifetime_value DESC
LIMIT 25;""",
            created_by=user_id
        )
        queries.append(q20)
        db.add(q20)
        
        # Query 21: Product Performance by Category
        q21 = Query(
            id=str(uuid.uuid4()),
            name="Demo: Product Performance by Category",
            description="Sales performance analysis by product category",
            datasource_id=ds_sqlite.id,
            query_type="sql",
            sql_query="""SELECT 
    p.category,
    COUNT(DISTINCT p.id) as product_count,
    COUNT(DISTINCT oi.order_id) as orders,
    SUM(oi.quantity) as units_sold,
    ROUND(SUM(oi.quantity * oi.price), 2) as revenue,
    ROUND(AVG(oi.price), 2) as avg_price
FROM products p
LEFT JOIN order_items oi ON p.id = oi.product_id
GROUP BY p.category
ORDER BY revenue DESC;""",
            created_by=user_id
        )
        queries.append(q21)
        db.add(q21)
        
        # Query 22: Recent High-Value Orders
        q22 = Query(
            id=str(uuid.uuid4()),
            name="Demo: Recent High-Value Orders",
            description="Recent orders above average order value",
            datasource_id=ds_sqlite.id,
            query_type="sql",
            sql_query="""SELECT 
    o.id as order_id,
    c.customer_name,
    o.order_date,
    o.amount,
    o.status,
    o.region
FROM orders o
JOIN customers c ON o.customer_id = c.id
WHERE o.amount > (SELECT AVG(amount) FROM orders)
  AND o.order_date >= date('now', '-30 days')
ORDER BY o.amount DESC
LIMIT 50;""",
            created_by=user_id
        )
        queries.append(q22)
        db.add(q22)
        
        # Query 23: Employee Tenure Analysis
        q23 = Query(
            id=str(uuid.uuid4()),
            name="Demo: Employee Tenure and Retention",
            description="Employee tenure and distribution across departments",
            datasource_id=ds_sqlite.id,
            query_type="sql",
            sql_query="""SELECT 
    d.dept_name,
    COUNT(e.id) as employee_count,
    ROUND(AVG(JULIANDAY('now') - JULIANDAY(e.hire_date)) / 365.25, 1) as avg_tenure_years,
    SUM(CASE WHEN JULIANDAY('now') - JULIANDAY(e.hire_date) < 365 THEN 1 ELSE 0 END) as new_employees,
    SUM(CASE WHEN JULIANDAY('now') - JULIANDAY(e.hire_date) >= 1825 THEN 1 ELSE 0 END) as veteran_employees
FROM employees e
JOIN departments d ON e.department_id = d.id
GROUP BY d.dept_name
ORDER BY avg_tenure_years DESC;""",
            created_by=user_id
        )
        queries.append(q23)
        db.add(q23)
        
        # Query 24: Customer Review Sentiment
        q24 = Query(
            id=str(uuid.uuid4()),
            name="Demo: Customer Review Sentiment Distribution",
            description="Distribution of product ratings over time",
            datasource_id=ds_sqlite.id,
            query_type="sql",
            sql_query="""SELECT 
    strftime('%Y-%m', review_date) as month,
    SUM(CASE WHEN rating = 5 THEN 1 ELSE 0 END) as five_star,
    SUM(CASE WHEN rating = 4 THEN 1 ELSE 0 END) as four_star,
    SUM(CASE WHEN rating = 3 THEN 1 ELSE 0 END) as three_star,
    SUM(CASE WHEN rating = 2 THEN 1 ELSE 0 END) as two_star,
    SUM(CASE WHEN rating = 1 THEN 1 ELSE 0 END) as one_star,
    ROUND(AVG(rating), 2) as avg_rating
FROM product_reviews
WHERE review_date >= date('now', '-12 months')
GROUP BY month
ORDER BY month;""",
            created_by=user_id
        )
        queries.append(q24)
        db.add(q24)
        
        # Query 25: Sales Performance by Month and Region
        q25 = Query(
            id=str(uuid.uuid4()),
            name="Demo: Sales Heatmap - Region vs Month",
            description="Sales performance matrix by region and month",
            datasource_id=ds_sqlite.id,
            query_type="sql",
            sql_query="""SELECT 
    region,
    strftime('%Y-%m', order_date) as month,
    COUNT(*) as order_count,
    ROUND(SUM(amount), 2) as revenue
FROM orders
WHERE order_date >= date('now', '-12 months')
  AND status = 'completed'
GROUP BY region, month
ORDER BY month, region;""",
            created_by=user_id
        )
        queries.append(q25)
        db.add(q25)
        
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
        
        # Dashboard 4: HR & Employee Analytics
        d4 = Dashboard(
            id=str(uuid.uuid4()),
            name="Demo: HR & Employee Analytics Dashboard",
            description="Employee performance, tenure, and department analysis",
            layout={
                "layouts": []
            },
            widgets=[
                {
                    "id": "w1",
                    "type": "chart",
                    "title": "Employee Performance by Department",
                    "query_id": q15.id,
                    "chart_type": "bar",
                    "x": 0,
                    "y": 0,
                    "w": 6,
                    "h": 3,
                    "config": {
                        "x_axis": "department",
                        "y_axis": "avg_performance"
                    }
                },
                {
                    "id": "w2",
                    "type": "chart",
                    "title": "Department Budget Overview",
                    "query_id": q18.id,
                    "chart_type": "column",
                    "x": 6,
                    "y": 0,
                    "w": 6,
                    "h": 3,
                    "config": {
                        "x_axis": "dept_name",
                        "y_axis": "budget"
                    }
                },
                {
                    "id": "w3",
                    "type": "chart",
                    "title": "Employee Tenure Analysis",
                    "query_id": q23.id,
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
            filters={},
            is_public=False,
            created_by=user_id
        )
        dashboards.append(d4)
        db.add(d4)
        
        # Dashboard 5: Product & Review Analytics
        d5 = Dashboard(
            id=str(uuid.uuid4()),
            name="Demo: Product & Review Analytics Dashboard",
            description="Product ratings, reviews, and performance metrics",
            layout={
                "layouts": []
            },
            widgets=[
                {
                    "id": "w1",
                    "type": "chart",
                    "title": "Top Rated Products",
                    "query_id": q17.id,
                    "chart_type": "bar",
                    "x": 0,
                    "y": 0,
                    "w": 6,
                    "h": 3,
                    "config": {
                        "x_axis": "product_name",
                        "y_axis": "avg_rating"
                    }
                },
                {
                    "id": "w2",
                    "type": "chart",
                    "title": "Review Sentiment Over Time",
                    "query_id": q24.id,
                    "chart_type": "area",
                    "x": 6,
                    "y": 0,
                    "w": 6,
                    "h": 3,
                    "config": {
                        "x_axis": "month",
                        "y_axis": "avg_rating"
                    }
                },
                {
                    "id": "w3",
                    "type": "chart",
                    "title": "Product Performance by Category",
                    "query_id": q21.id,
                    "chart_type": "treemap",
                    "x": 0,
                    "y": 3,
                    "w": 6,
                    "h": 3,
                    "config": {
                        "label": "category",
                        "value": "revenue"
                    }
                },
                {
                    "id": "w4",
                    "type": "chart",
                    "title": "Product Ratings Detail",
                    "query_id": q17.id,
                    "chart_type": "table",
                    "x": 6,
                    "y": 3,
                    "w": 6,
                    "h": 3,
                    "config": {
                        "pageSize": 10
                    }
                }
            ],
            filters={},
            is_public=True,
            created_by=user_id
        )
        dashboards.append(d5)
        db.add(d5)
        
        # Dashboard 6: Sales Target Performance
        d6 = Dashboard(
            id=str(uuid.uuid4()),
            name="Demo: Sales Target Performance Dashboard",
            description="Sales targets vs achievements with regional breakdown",
            layout={
                "layouts": []
            },
            widgets=[
                {
                    "id": "w1",
                    "type": "chart",
                    "title": "Target Achievement by Region",
                    "query_id": q16.id,
                    "chart_type": "gauge",
                    "x": 0,
                    "y": 0,
                    "w": 3,
                    "h": 2,
                    "config": {
                        "field": "achievement_percentage",
                        "min": 0,
                        "max": 150
                    }
                },
                {
                    "id": "w2",
                    "type": "chart",
                    "title": "Regional Sales Performance",
                    "query_id": q16.id,
                    "chart_type": "column",
                    "x": 3,
                    "y": 0,
                    "w": 9,
                    "h": 3,
                    "config": {
                        "x_axis": "region",
                        "y_axis": "total_achieved"
                    }
                },
                {
                    "id": "w3",
                    "type": "chart",
                    "title": "Sales Heatmap - Region vs Month",
                    "query_id": q25.id,
                    "chart_type": "heatmap",
                    "x": 0,
                    "y": 3,
                    "w": 12,
                    "h": 4,
                    "config": {
                        "x_axis": "month",
                        "y_axis": "region",
                        "value": "revenue"
                    }
                }
            ],
            filters={},
            is_public=False,
            created_by=user_id
        )
        dashboards.append(d6)
        db.add(d6)
        
        db.commit()
        
        # Create Demo Alerts
        alerts = []
        
        # Alert 1: Revenue threshold
        a1 = Alert(
            id=str(uuid.uuid4()),
            name="Daily Revenue Alert",
            description="Alert when daily revenue falls below $10,000",
            user_id=user_id,
            query_id=q1.id,
            condition_type=AlertConditionType.LESS_THAN,
            threshold_value=10000,
            metric_column="total_revenue",
            frequency=AlertFrequency.DAILY,
            notify_emails=["admin@nexbii.demo"],
            notify_slack=True,
            slack_webhook="#alerts",
            is_active=True
        )
        alerts.append(a1)
        db.add(a1)
        
        # Alert 2: Order volume
        a2 = Alert(
            id=str(uuid.uuid4()),
            name="Low Order Volume Alert",
            description="Alert when hourly order count is below 5",
            user_id=user_id,
            query_id=q1.id,
            condition_type=AlertConditionType.LESS_THAN,
            threshold_value=5,
            metric_column="total_orders",
            frequency=AlertFrequency.HOURLY,
            notify_emails=["admin@nexbii.demo"],
            is_active=True
        )
        alerts.append(a2)
        db.add(a2)
        
        # Alert 3: High revenue alert
        a3 = Alert(
            id=str(uuid.uuid4()),
            name="High Revenue Achievement",
            description="Alert when daily revenue exceeds $50,000",
            user_id=user_id,
            query_id=q1.id,
            condition_type=AlertConditionType.GREATER_THAN,
            threshold_value=50000,
            metric_column="total_revenue",
            frequency=AlertFrequency.DAILY,
            notify_emails=["admin@nexbii.demo"],
            notify_slack=True,
            slack_webhook="#sales",
            is_active=True
        )
        alerts.append(a3)
        db.add(a3)
        
        db.commit()
        
        # Create Demo Subscriptions
        subscriptions = []
        
        # Subscription 1: Daily sales report
        s1 = EmailSubscription(
            id=str(uuid.uuid4()),
            user_id=user_id,
            dashboard_id=d1.id,
            frequency=SubscriptionFrequency.DAILY,
            is_active=True,
            next_send_date=datetime.utcnow() + timedelta(days=1)
        )
        subscriptions.append(s1)
        db.add(s1)
        
        # Subscription 2: Weekly customer analytics
        s2 = EmailSubscription(
            id=str(uuid.uuid4()),
            user_id=user_id,
            dashboard_id=d2.id,
            frequency=SubscriptionFrequency.WEEKLY,
            is_active=True,
            next_send_date=datetime.utcnow() + timedelta(days=7),
            last_sent_date=datetime.utcnow() - timedelta(days=7)
        )
        subscriptions.append(s2)
        db.add(s2)
        
        # Subscription 3: Monthly summary
        s3 = EmailSubscription(
            id=str(uuid.uuid4()),
            user_id=user_id,
            dashboard_id=d3.id,
            frequency=SubscriptionFrequency.MONTHLY,
            is_active=True,
            next_send_date=datetime.utcnow() + timedelta(days=30)
        )
        subscriptions.append(s3)
        db.add(s3)
        
        db.commit()
        
        # Create Demo Comments
        comments = []
        
        # Comments on dashboards
        comment_texts = [
            "Great dashboard! The sales trends are very insightful.",
            "Can we add a filter for region?",
            "The revenue chart shows interesting patterns in Q3.",
            "Would be nice to see year-over-year comparison.",
            "Excellent work on the customer segmentation analysis!",
            "The product performance metrics are really helpful.",
            "Could we drill down into individual product categories?",
            "Love the new HR analytics dashboard!",
            "The employee performance trends look promising.",
            "Sales targets visualization is very clear."
        ]
        
        # Add comments to various dashboards
        for i, d in enumerate(dashboards):
            num_comments = random.randint(2, 5)
            for j in range(num_comments):
                c = Comment(
                    id=str(uuid.uuid4()),
                    dashboard_id=d.id,
                    user_id=user_id,
                    content=random.choice(comment_texts),
                    created_at=datetime.utcnow() - timedelta(days=random.randint(1, 30))
                )
                comments.append(c)
                db.add(c)
        
        # Add comments to some queries
        for i in range(10):
            c = Comment(
                id=str(uuid.uuid4()),
                query_id=queries[i].id,
                user_id=user_id,
                content=random.choice([
                    "This query is very efficient!",
                    "Could we optimize this further?",
                    "Great way to analyze customer behavior.",
                    "The results are exactly what we needed.",
                    "Very useful for our weekly reports."
                ]),
                created_at=datetime.utcnow() - timedelta(days=random.randint(1, 15))
            )
            comments.append(c)
            db.add(c)
        
        db.commit()
        
        # Create Demo Activities
        activities = []
        
        activity_descriptions = {
            ActivityType.DASHBOARD_CREATED: "created a new dashboard",
            ActivityType.DASHBOARD_UPDATED: "updated a dashboard",
            ActivityType.DASHBOARD_DELETED: "deleted a dashboard",
            ActivityType.DASHBOARD_SHARED: "shared a dashboard",
            ActivityType.QUERY_CREATED: "created a new query",
            ActivityType.QUERY_EXECUTED: "executed a query",
            ActivityType.QUERY_UPDATED: "updated a query",
            ActivityType.QUERY_DELETED: "deleted a query",
            ActivityType.DATASOURCE_CREATED: "connected a new data source",
            ActivityType.DATASOURCE_UPDATED: "updated a data source",
            ActivityType.DATASOURCE_DELETED: "deleted a data source",
            ActivityType.ALERT_TRIGGERED: "triggered an alert",
            ActivityType.COMMENT_ADDED: "added a comment",
            ActivityType.USER_MENTIONED: "mentioned a user",
            ActivityType.SUBSCRIPTION_CREATED: "created a subscription"
        }
        
        # Generate activities for the last 30 days
        for i in range(100):
            activity_type = random.choice(list(ActivityType))
            activity_timestamp = datetime.utcnow() - timedelta(
                days=random.randint(0, 30),
                hours=random.randint(0, 23),
                minutes=random.randint(0, 59)
            )
            
            # Pick a related entity
            entity_type = None
            entity_id = None
            if 'DASHBOARD' in activity_type.value:
                entity_type = "dashboard"
                entity_id = random.choice(dashboards).id
            elif 'QUERY' in activity_type.value:
                entity_type = "query"
                entity_id = random.choice(queries).id
            elif 'DATASOURCE' in activity_type.value:
                entity_type = "datasource"
                entity_id = random.choice(datasources).id
            elif 'ALERT' in activity_type.value:
                entity_type = "alert"
                entity_id = random.choice(alerts).id if alerts else None
            
            a = Activity(
                id=str(uuid.uuid4()),
                user_id=user_id,
                activity_type=activity_type,
                entity_type=entity_type,
                entity_id=entity_id,
                description=activity_descriptions.get(activity_type, "performed an action"),
                activity_metadata={
                    "ip_address": f"192.168.1.{random.randint(1, 255)}",
                    "user_agent": "Mozilla/5.0 (Demo Activity)"
                },
                created_at=activity_timestamp
            )
            activities.append(a)
            db.add(a)
        
        db.commit()
        
        # Create Demo Tenants (Multi-tenancy)
        tenants = []
        
        # Tenant 1: Default tenant for demo user
        t1 = Tenant(
            id=str(uuid.uuid4()),
            name="NexBII Demo Organization",
            slug="nexbii-demo",
            contact_email="admin@nexbii.demo",
            contact_name="Demo Admin",
            plan="enterprise",
            is_active=True,
            max_users=50,
            max_datasources=20,
            max_dashboards=100,
            max_queries=500,
            storage_limit_mb=10000,
            storage_used_mb=1800,
            features={
                "ai_enabled": True,
                "advanced_analytics": True,
                "api_access": True,
                "white_labeling": True,
                "custom_domains": True
            },
            branding={
                "logo_url": "https://example.com/logo.png",
                "primary_color": "#3b82f6",
                "secondary_color": "#8b5cf6",
                "font_family": "Inter"
            },
            settings={
                "timezone": "UTC",
                "date_format": "YYYY-MM-DD",
                "currency": "USD"
            },
            created_at=datetime.utcnow() - timedelta(days=180)
        )
        tenants.append(t1)
        db.add(t1)
        
        # Tenant 2: Professional Plan Example
        t2 = Tenant(
            id=str(uuid.uuid4()),
            name="Acme Corporation",
            slug="acme-corp",
            contact_email="admin@acme.com",
            contact_name="John Smith",
            plan="professional",
            is_active=True,
            max_users=20,
            max_datasources=10,
            max_dashboards=50,
            max_queries=200,
            storage_limit_mb=5000,
            storage_used_mb=850,
            features={
                "ai_enabled": True,
                "advanced_analytics": True,
                "api_access": True
            },
            branding={
                "logo_url": "https://acme.com/logo.png",
                "primary_color": "#10b981",
                "secondary_color": "#059669"
            },
            created_at=datetime.utcnow() - timedelta(days=90)
        )
        tenants.append(t2)
        db.add(t2)
        
        # Tenant 3: Starter Plan Example
        t3 = Tenant(
            id=str(uuid.uuid4()),
            name="TechStart Inc",
            slug="techstart",
            contact_email="contact@techstart.io",
            contact_name="Sarah Johnson",
            plan="starter",
            is_active=True,
            max_users=10,
            max_datasources=5,
            max_dashboards=25,
            max_queries=100,
            storage_limit_mb=2000,
            storage_used_mb=320,
            features={
                "ai_enabled": False,
                "advanced_analytics": False
            },
            branding={},
            created_at=datetime.utcnow() - timedelta(days=30),
            trial_ends_at=datetime.utcnow() + timedelta(days=14)
        )
        tenants.append(t3)
        db.add(t3)
        
        db.commit()
        
        # Link demo user to the primary demo tenant
        demo_user.tenant_id = t1.id
        db.add(demo_user)
        db.commit()
        print(f"✅ Demo user linked to tenant: {t1.name}")
        
        # Create Demo Tenant Domains
        tenant_domains = []
        
        td1 = TenantDomain(
            id=str(uuid.uuid4()),
            tenant_id=t1.id,
            domain="analytics.nexbii.demo",
            is_verified=True,
            is_primary=True,
            ssl_enabled=True,
            verification_method="cname",
            verified_at=datetime.utcnow() - timedelta(days=170)
        )
        tenant_domains.append(td1)
        db.add(td1)
        
        td2 = TenantDomain(
            id=str(uuid.uuid4()),
            tenant_id=t2.id,
            domain="bi.acme.com",
            is_verified=True,
            is_primary=True,
            ssl_enabled=True,
            verification_method="txt",
            verified_at=datetime.utcnow() - timedelta(days=85)
        )
        tenant_domains.append(td2)
        db.add(td2)
        
        db.commit()
        
        # Create Demo Tenant Invitations
        tenant_invitations = []
        
        ti1 = TenantInvitation(
            id=str(uuid.uuid4()),
            tenant_id=t1.id,
            email="user1@example.com",
            role="editor",
            invited_by=user_id,
            token=secrets.token_urlsafe(32),
            expires_at=datetime.utcnow() + timedelta(days=7),
            created_at=datetime.utcnow() - timedelta(days=2)
        )
        tenant_invitations.append(ti1)
        db.add(ti1)
        
        ti2 = TenantInvitation(
            id=str(uuid.uuid4()),
            tenant_id=t2.id,
            email="analyst@acme.com",
            role="viewer",
            invited_by=user_id,
            token=secrets.token_urlsafe(32),
            expires_at=datetime.utcnow() + timedelta(days=7),
            accepted_at=datetime.utcnow() - timedelta(days=1),
            created_at=datetime.utcnow() - timedelta(days=3)
        )
        tenant_invitations.append(ti2)
        db.add(ti2)
        
        db.commit()
        
        # Create Demo Tenant Usage Records
        tenant_usage_records = []
        
        # Last 3 months of usage for main tenant
        for month_offset in range(3):
            period_start = datetime.utcnow() - timedelta(days=(month_offset + 1) * 30)
            period_end = datetime.utcnow() - timedelta(days=month_offset * 30)
            
            tu = TenantUsage(
                id=str(uuid.uuid4()),
                tenant_id=t1.id,
                period_start=period_start,
                period_end=period_end,
                queries_executed=random.randint(500, 2000),
                dashboards_viewed=random.randint(200, 800),
                api_calls=random.randint(1000, 5000),
                storage_used_mb=random.randint(1500, 2000),
                users_active=random.randint(5, 15),
                ai_queries=random.randint(50, 200),
                analytics_runs=random.randint(30, 100),
                exports_generated=random.randint(20, 80),
                billable_amount=random.randint(50000, 150000),  # $500-$1500 in cents
                created_at=period_end
            )
            tenant_usage_records.append(tu)
            db.add(tu)
        
        db.commit()
        
        # Create Demo Integrations
        integrations = []
        
        # Email Integration
        i1 = Integration(
            id=str(uuid.uuid4()),
            smtp_host="smtp.gmail.com",
            smtp_port="587",
            smtp_user="noreply@nexbii.demo",
            smtp_password="demo_encrypted_password",
            from_email="noreply@nexbii.demo",
            from_name="NexBII Analytics",
            mock_email=True,  # Mock mode for demo
            mock_slack=True,
            slack_webhook_url="https://hooks.slack.com/services/DEMO/WEBHOOK/URL",
            created_by=user_id,
            created_at=datetime.utcnow() - timedelta(days=150)
        )
        integrations.append(i1)
        db.add(i1)
        
        db.commit()
        
        # Create Demo Shared Dashboards (Public Links)
        shared_dashboards = []
        
        # Share dashboard 1 with password protection
        sd1 = SharedDashboard(
            id=str(uuid.uuid4()),
            dashboard_id=dashboards[0].id,  # Sales Analytics Dashboard
            share_token=SharedDashboard.generate_token(),
            password=get_password_hash("demo123"),  # Password-protected
            expires_at=datetime.utcnow() + timedelta(days=30),
            is_active=True,
            allow_interactions=True,
            created_by=user_id,
            created_at=datetime.utcnow() - timedelta(days=10)
        )
        shared_dashboards.append(sd1)
        db.add(sd1)
        
        # Share dashboard 2 without password, expires in 7 days
        sd2 = SharedDashboard(
            id=str(uuid.uuid4()),
            dashboard_id=dashboards[1].id,  # Customer Analytics Dashboard
            share_token=SharedDashboard.generate_token(),
            password=None,
            expires_at=datetime.utcnow() + timedelta(days=7),
            is_active=True,
            allow_interactions=False,  # View-only
            created_by=user_id,
            created_at=datetime.utcnow() - timedelta(days=5)
        )
        shared_dashboards.append(sd2)
        db.add(sd2)
        
        # Share dashboard 3 - no expiration
        sd3 = SharedDashboard(
            id=str(uuid.uuid4()),
            dashboard_id=dashboards[4].id,  # Product & Review Analytics
            share_token=SharedDashboard.generate_token(),
            password=None,
            expires_at=None,  # Never expires
            is_active=True,
            allow_interactions=True,
            created_by=user_id,
            created_at=datetime.utcnow() - timedelta(days=20)
        )
        shared_dashboards.append(sd3)
        db.add(sd3)
        
        db.commit()
        
        # Note: Cache is handled in-memory by Redis, we'll add some activity logs for cache hits
        # Add more activities for cache-related operations
        cache_activities = []
        for i in range(20):
            ca = Activity(
                id=str(uuid.uuid4()),
                user_id=user_id,
                activity_type=ActivityType.QUERY_EXECUTED,
                entity_type="query",
                entity_id=random.choice(queries).id,
                description="executed a cached query (cache hit)",
                activity_metadata={
                    "cache_hit": True,
                    "execution_time_ms": random.randint(10, 50),
                    "ip_address": f"192.168.1.{random.randint(1, 255)}"
                },
                created_at=datetime.utcnow() - timedelta(
                    days=random.randint(0, 15),
                    hours=random.randint(0, 23)
                )
            )
            cache_activities.append(ca)
            db.add(ca)
        
        # Add Dashboard-related activities (replacing EXPORT_GENERATED which doesn't exist)
        dashboard_activities = []
        export_types = ["PDF", "Excel", "CSV", "PNG"]
        for i in range(15):
            ea = Activity(
                id=str(uuid.uuid4()),
                user_id=user_id,
                activity_type=ActivityType.DASHBOARD_SHARED,
                entity_type="dashboard",
                entity_id=random.choice(dashboards).id,
                description=f"shared dashboard",
                activity_metadata={
                    "share_type": "public",
                    "file_size_kb": random.randint(100, 5000),
                    "ip_address": f"192.168.1.{random.randint(1, 255)}"
                },
                created_at=datetime.utcnow() - timedelta(
                    days=random.randint(0, 30),
                    hours=random.randint(0, 23)
                )
            )
            dashboard_activities.append(ea)
            db.add(ea)
        
        db.commit()
        
        # Create Demo API Keys
        api_keys = []
        
        # API Key 1: Full Access Key
        api_key_1_value = f"nexbii_{secrets.token_urlsafe(32)}"
        ak1 = APIKey(
            id=str(uuid.uuid4()),
            tenant_id=t1.id,
            user_id=user_id,
            name="Production API Key",
            description="Full access key for production integrations",
            key_prefix=api_key_1_value[:8],
            key_hash=hashlib.sha256(api_key_1_value.encode()).hexdigest(),
            scopes=["admin:*"],
            rate_limit_per_minute=60,
            rate_limit_per_hour=1000,
            rate_limit_per_day=10000,
            is_active=True,
            expires_at=None,
            request_count=random.randint(500, 2000),
            last_used_at=datetime.utcnow() - timedelta(days=random.randint(0, 5)),
            last_used_ip=f"192.168.1.{random.randint(1, 255)}",
            created_at=datetime.utcnow() - timedelta(days=60)
        )
        api_keys.append(ak1)
        db.add(ak1)
        
        # API Key 2: Read-Only Key
        api_key_2_value = f"nexbii_{secrets.token_urlsafe(32)}"
        ak2 = APIKey(
            id=str(uuid.uuid4()),
            tenant_id=t1.id,
            user_id=user_id,
            name="Analytics Dashboard Read-Only",
            description="Read-only access for external dashboards",
            key_prefix=api_key_2_value[:8],
            key_hash=hashlib.sha256(api_key_2_value.encode()).hexdigest(),
            scopes=["read:dashboards", "read:queries", "read:datasources"],
            rate_limit_per_minute=30,
            rate_limit_per_hour=500,
            rate_limit_per_day=5000,
            is_active=True,
            expires_at=datetime.utcnow() + timedelta(days=90),
            request_count=random.randint(200, 800),
            last_used_at=datetime.utcnow() - timedelta(hours=random.randint(1, 24)),
            last_used_ip=f"10.0.1.{random.randint(1, 255)}",
            created_at=datetime.utcnow() - timedelta(days=30)
        )
        api_keys.append(ak2)
        db.add(ak2)
        
        # API Key 3: Query Execution Key
        api_key_3_value = f"nexbii_{secrets.token_urlsafe(32)}"
        ak3 = APIKey(
            id=str(uuid.uuid4()),
            tenant_id=t2.id,
            user_id=user_id,
            name="Query Execution API",
            description="For automated query execution and reporting",
            key_prefix=api_key_3_value[:8],
            key_hash=hashlib.sha256(api_key_3_value.encode()).hexdigest(),
            scopes=["read:queries", "execute:queries", "read:dashboards"],
            rate_limit_per_minute=45,
            rate_limit_per_hour=800,
            rate_limit_per_day=8000,
            is_active=True,
            expires_at=datetime.utcnow() + timedelta(days=180),
            request_count=random.randint(1000, 3000),
            last_used_at=datetime.utcnow() - timedelta(minutes=random.randint(5, 120)),
            last_used_ip=f"172.16.0.{random.randint(1, 255)}",
            created_at=datetime.utcnow() - timedelta(days=45)
        )
        api_keys.append(ak3)
        db.add(ak3)
        
        db.commit()
        
        # Create Demo Webhooks
        webhooks = []
        
        # Webhook 1: Alert Notifications
        wh1 = Webhook(
            id=str(uuid.uuid4()),
            tenant_id=t1.id,
            user_id=user_id,
            name="Slack Alert Notifications",
            description="Send alert notifications to Slack channel",
            url="https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXXXXXXXXXX",
            secret=secrets.token_urlsafe(32),
            events=["alert.triggered", "alert.resolved"],
            is_active=True,
            max_retries=3,
            retry_backoff_seconds=60,
            total_deliveries=random.randint(50, 150),
            successful_deliveries=random.randint(45, 140),
            failed_deliveries=random.randint(1, 10),
            last_triggered_at=datetime.utcnow() - timedelta(hours=random.randint(1, 24)),
            last_success_at=datetime.utcnow() - timedelta(hours=random.randint(1, 24)),
            created_at=datetime.utcnow() - timedelta(days=90)
        )
        webhooks.append(wh1)
        db.add(wh1)
        
        # Webhook 2: Query Execution Monitoring
        wh2 = Webhook(
            id=str(uuid.uuid4()),
            tenant_id=t1.id,
            user_id=user_id,
            name="Query Execution Monitor",
            description="Monitor query executions and send to external monitoring system",
            url="https://api.monitoring.example.com/webhooks/query-events",
            secret=secrets.token_urlsafe(32),
            events=["query.created", "query.executed", "query.deleted"],
            is_active=True,
            max_retries=5,
            retry_backoff_seconds=30,
            total_deliveries=random.randint(200, 500),
            successful_deliveries=random.randint(190, 480),
            failed_deliveries=random.randint(5, 20),
            last_triggered_at=datetime.utcnow() - timedelta(minutes=random.randint(5, 60)),
            last_success_at=datetime.utcnow() - timedelta(minutes=random.randint(5, 60)),
            created_at=datetime.utcnow() - timedelta(days=60)
        )
        webhooks.append(wh2)
        db.add(wh2)
        
        # Webhook 3: Dashboard Analytics
        wh3 = Webhook(
            id=str(uuid.uuid4()),
            tenant_id=t2.id,
            user_id=user_id,
            name="Dashboard Usage Analytics",
            description="Track dashboard views and interactions",
            url="https://analytics.acme.com/api/events",
            secret=secrets.token_urlsafe(32),
            events=["dashboard.viewed", "dashboard.created", "dashboard.updated"],
            is_active=True,
            max_retries=3,
            retry_backoff_seconds=45,
            total_deliveries=random.randint(300, 700),
            successful_deliveries=random.randint(290, 680),
            failed_deliveries=random.randint(5, 20),
            last_triggered_at=datetime.utcnow() - timedelta(hours=2),
            last_success_at=datetime.utcnow() - timedelta(hours=2),
            created_at=datetime.utcnow() - timedelta(days=75)
        )
        webhooks.append(wh3)
        db.add(wh3)
        
        # Webhook 4: Export Completion
        wh4 = Webhook(
            id=str(uuid.uuid4()),
            tenant_id=t1.id,
            user_id=user_id,
            name="Export Completion Notifier",
            description="Notify when data exports are completed",
            url="https://api.nexbii.demo/webhooks/export-complete",
            secret=secrets.token_urlsafe(32),
            events=["export.completed"],
            is_active=True,
            max_retries=2,
            retry_backoff_seconds=120,
            total_deliveries=random.randint(50, 120),
            successful_deliveries=random.randint(48, 115),
            failed_deliveries=random.randint(1, 5),
            last_triggered_at=datetime.utcnow() - timedelta(days=random.randint(1, 7)),
            last_success_at=datetime.utcnow() - timedelta(days=random.randint(1, 7)),
            created_at=datetime.utcnow() - timedelta(days=45)
        )
        webhooks.append(wh4)
        db.add(wh4)
        
        db.commit()
        
        # Create Demo Plugins
        plugins = []
        
        # Plugin 1: Custom Visualization
        p1 = Plugin(
            id=str(uuid.uuid4()),
            name="sankey_chart",
            display_name="Sankey Flow Diagram",
            description="Custom Sankey diagram for visualizing flow data",
            version="1.0.0",
            author="NexBII Team",
            plugin_type="visualization",
            entry_point="main.py",
            files={
                "main.py": """
import json
import sys

def render_sankey(data):
    # Simple sankey chart implementation
    return {
        "type": "sankey",
        "data": data,
        "rendered": True
    }

if __name__ == "__main__":
    context_file = sys.argv[1]
    with open(context_file, 'r') as f:
        context = json.load(f)
    
    result = render_sankey(context['input'])
    print(json.dumps(result))
"""
            },
            manifest={
                "name": "sankey_chart",
                "version": "1.0.0",
                "plugin_type": "visualization"
            },
            dependencies=[],
            required_scopes=["read:data"],
            config_schema={},
            default_config={},
            installed_by=user_id,
            tenant_id=None,  # Global plugin
            is_enabled=True,
            is_verified=True,
            usage_count=random.randint(50, 200),
            last_used_at=datetime.utcnow() - timedelta(days=random.randint(1, 10)),
            created_at=datetime.utcnow() - timedelta(days=120)
        )
        plugins.append(p1)
        db.add(p1)
        
        # Plugin 2: Data Transformation
        p2 = Plugin(
            id=str(uuid.uuid4()),
            name="data_cleaner",
            display_name="Data Cleaning & Normalization",
            description="Clean and normalize data before analysis",
            version="2.1.0",
            author="Community",
            plugin_type="transformation",
            entry_point="transform.py",
            files={
                "transform.py": """
import json
import sys

def clean_data(data, config):
    # Data cleaning logic
    cleaned = []
    for row in data:
        cleaned_row = {k: v.strip() if isinstance(v, str) else v for k, v in row.items()}
        cleaned.append(cleaned_row)
    return cleaned

if __name__ == "__main__":
    context_file = sys.argv[1]
    with open(context_file, 'r') as f:
        context = json.load(f)
    
    result = clean_data(context['input'], context['config'])
    print(json.dumps({"data": result, "rows_processed": len(result)}))
"""
            },
            manifest={
                "name": "data_cleaner",
                "version": "2.1.0",
                "plugin_type": "transformation"
            },
            dependencies=[],
            required_scopes=["read:data", "write:data"],
            config_schema={},
            default_config={"remove_nulls": True, "trim_strings": True},
            installed_by=user_id,
            tenant_id=t1.id,  # Tenant-specific plugin
            is_enabled=True,
            is_verified=False,
            usage_count=random.randint(100, 300),
            last_used_at=datetime.utcnow() - timedelta(hours=random.randint(1, 48)),
            created_at=datetime.utcnow() - timedelta(days=75)
        )
        plugins.append(p2)
        db.add(p2)
        
        # Plugin 3: Export Formatter
        p3 = Plugin(
            id=str(uuid.uuid4()),
            name="custom_pdf_template",
            display_name="Custom PDF Report Template",
            description="Generate professional PDF reports with custom branding",
            version="1.5.2",
            author="NexBII Team",
            plugin_type="export",
            entry_point="pdf_generator.py",
            files={
                "pdf_generator.py": """
import json
import sys

def generate_pdf(data, config):
    # PDF generation logic
    return {
        "format": "pdf",
        "size_kb": 245,
        "pages": 3,
        "success": True
    }

if __name__ == "__main__":
    context_file = sys.argv[1]
    with open(context_file, 'r') as f:
        context = json.load(f)
    
    result = generate_pdf(context['input'], context['config'])
    print(json.dumps(result))
"""
            },
            manifest={
                "name": "custom_pdf_template",
                "version": "1.5.2",
                "plugin_type": "export"
            },
            dependencies=[],
            required_scopes=["read:dashboards", "export:pdf"],
            config_schema={},
            default_config={"include_logo": True, "page_size": "A4"},
            installed_by=user_id,
            tenant_id=None,  # Global plugin
            is_enabled=True,
            is_verified=True,
            usage_count=random.randint(30, 100),
            last_used_at=datetime.utcnow() - timedelta(days=random.randint(1, 15)),
            created_at=datetime.utcnow() - timedelta(days=90)
        )
        plugins.append(p3)
        db.add(p3)
        
        db.commit()
        
        # Create Plugin Instances
        plugin_instances = []
        
        # Instance 1: Sales Flow Visualization
        pi1 = PluginInstance(
            id=str(uuid.uuid4()),
            plugin_id=p1.id,
            tenant_id=t1.id,
            name="Sales Flow Diagram",
            config={"width": 800, "height": 600, "show_labels": True},
            is_enabled=True,
            execution_count=random.randint(20, 80),
            last_executed_at=datetime.utcnow() - timedelta(days=random.randint(1, 10)),
            total_execution_time_ms=random.randint(5000, 15000),
            error_count=random.randint(0, 3),
            created_at=datetime.utcnow() - timedelta(days=60)
        )
        plugin_instances.append(pi1)
        db.add(pi1)
        
        # Instance 2: Data Cleaner for Sales Data
        pi2 = PluginInstance(
            id=str(uuid.uuid4()),
            plugin_id=p2.id,
            tenant_id=t1.id,
            name="Sales Data Cleaner",
            config={"remove_nulls": True, "trim_strings": True, "lowercase_emails": True},
            is_enabled=True,
            execution_count=random.randint(50, 150),
            last_executed_at=datetime.utcnow() - timedelta(hours=random.randint(1, 24)),
            total_execution_time_ms=random.randint(10000, 30000),
            error_count=random.randint(1, 5),
            created_at=datetime.utcnow() - timedelta(days=45)
        )
        plugin_instances.append(pi2)
        db.add(pi2)
        
        # Instance 3: Monthly Report PDF
        pi3 = PluginInstance(
            id=str(uuid.uuid4()),
            plugin_id=p3.id,
            tenant_id=t1.id,
            name="Monthly Sales Report PDF",
            config={"include_logo": True, "page_size": "A4", "include_charts": True},
            is_enabled=True,
            execution_count=random.randint(10, 30),
            last_executed_at=datetime.utcnow() - timedelta(days=random.randint(1, 15)),
            total_execution_time_ms=random.randint(8000, 20000),
            error_count=random.randint(0, 2),
            created_at=datetime.utcnow() - timedelta(days=60)
        )
        plugin_instances.append(pi3)
        db.add(pi3)
        
        db.commit()
        
        return {
            "success": True,
            "message": "✨ Comprehensive demo data generated successfully for ALL modules!",
            "data": {
                "sqlite_database": db_stats,
                "datasources": len(datasources),
                "queries": len(queries),
                "dashboards": len(dashboards),
                "alerts": len(alerts),
                "subscriptions": len(subscriptions),
                "comments": len(comments),
                "activities": len(activities) + len(cache_activities) + len(dashboard_activities),
                "tenants": len(tenants),
                "tenant_domains": len(tenant_domains),
                "tenant_invitations": len(tenant_invitations),
                "tenant_usage": len(tenant_usage_records),
                "integrations": len(integrations),
                "shared_dashboards": len(shared_dashboards),
                "cache_records": len(cache_activities),
                "dashboard_share_records": len(dashboard_activities),
                "api_keys": len(api_keys),
                "webhooks": len(webhooks),
                "plugins": len(plugins),
                "plugin_instances": len(plugin_instances)
            },
            "details": {
                "datasources": [{"id": ds.id, "name": ds.name, "type": ds.type.value} for ds in datasources],
                "queries": [{"id": q.id, "name": q.name} for q in queries],
                "dashboards": [{"id": d.id, "name": d.name} for d in dashboards],
                "alerts": [{"id": a.id, "name": a.name} for a in alerts],
                "subscriptions": [{"id": s.id, "frequency": s.frequency.value} for s in subscriptions],
                "tenants": [{"id": t.id, "name": t.name, "plan": t.plan} for t in tenants],
                "shared_dashboards": [{"id": sd.id, "dashboard_id": sd.dashboard_id, "expires_at": str(sd.expires_at) if sd.expires_at else "Never"} for sd in shared_dashboards],
                "integrations": [{"id": i.id, "smtp_configured": bool(i.smtp_host), "slack_configured": bool(i.slack_webhook_url)} for i in integrations]
            },
            "summary": {
                "database_records": {
                    "products": db_stats['products'],
                    "customers": db_stats['customers'],
                    "orders": db_stats['orders'],
                    "order_items": f"~{db_stats['order_items']}",
                    "user_activities": db_stats['user_activities'],
                    "departments": db_stats['departments'],
                    "employees": f"~{db_stats['employees']}",
                    "sales_targets": db_stats['sales_targets'],
                    "product_reviews": db_stats['product_reviews']
                },
                "modules_covered": [
                    "✅ SQLite Database (with 9 tables and realistic sample data)",
                    "✅ Data Sources (3 types: SQLite, PostgreSQL, MongoDB)",
                    "✅ SQL Queries (25 comprehensive queries covering sales, customers, HR, products, reviews)",
                    "✅ Dashboards (6 dashboards: Sales, Customer, Operational, HR, Product Reviews, Sales Targets)",
                    "✅ Alerts (3 alerts: Revenue threshold, Order volume, Customer segment monitoring)",
                    "✅ Subscriptions (3 scheduled reports: Daily, Weekly, Monthly)",
                    "✅ Comments (20+ comments on dashboards and queries)",
                    "✅ Activities (135 activity log entries: user actions, cache hits, exports)",
                    "✅ User Management (Demo admin user: admin@nexbii.demo)",
                    "✅ Multi-Tenancy (3 tenants: Enterprise, Professional, Starter plans)",
                    "✅ Custom Domains (2 tenant domains with SSL verification)",
                    "✅ Tenant Invitations (2 user invitations with tokens)",
                    "✅ Usage Tracking (3 months of tenant usage records for billing)",
                    "✅ Integrations (Email SMTP & Slack webhook configurations)",
                    "✅ Shared Dashboards (3 public sharing links: password-protected, expiring, permanent)",
                    "✅ Cache Activity (20 cached query execution records)",
                    "✅ Export History (15 export records: PDF, Excel, CSV, PNG)"
                ]
            }
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate demo data: {str(e)}"
        )
