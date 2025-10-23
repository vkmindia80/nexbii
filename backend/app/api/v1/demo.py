from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import uuid
from ...core.database import get_db
from ...models.datasource import DataSource, DataSourceType
from ...models.query import Query
from ...models.dashboard import Dashboard
from ...models.user import User

router = APIRouter()

@router.post("/generate")
async def generate_demo_data(db: Session = Depends(get_db)):
    """
    Generate demo data for all modules:
    - Data sources (3 demo sources)
    - Queries (5 demo queries)
    - Dashboards (2 demo dashboards)
    """
    try:
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
    AVG(order_value) as avg_order_value,
    SUM(order_value) as total_revenue
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
            "message": "Comprehensive demo data generated successfully for all modules",
            "data": {
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
                    "products": 25,
                    "customers": 200,
                    "orders": 1500,
                    "order_items": "~3750",
                    "user_activities": 5000
                },
                "modules_covered": [
                    "Data Sources (3 types: SQLite, PostgreSQL, MongoDB)",
                    "SQL Queries (14 comprehensive queries)",
                    "Dashboards (3 dashboards: Sales, Customer, Operations)",
                    "User Management (Demo admin user)"
                ]
            }
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate demo data: {str(e)}"
        )
