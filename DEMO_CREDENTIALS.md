# 🎯 NexBII Demo Credentials

## Quick Login

For testing and validation purposes, a demo admin account has been pre-configured in the system.

### Demo Admin Account

| Field | Value |
|-------|-------|
| **Email** | `admin@nexbii.demo` |
| **Password** | `demo123` |
| **Role** | Admin (Full Access) |
| **Permissions** | All features and management capabilities |

---

## 🚀 How to Use

### Method 1: Auto-Fill Button (Recommended)
1. Navigate to the login page
2. Click the **"Fill Demo Credentials"** button in the amber banner
3. Credentials will be automatically filled
4. Click **"Sign In"**

### Method 2: Manual Entry
1. Navigate to the login page
2. Enter email: `admin@nexbii.demo`
3. Enter password: `demo123`
4. Click **"Sign In"**

---

## ✅ What You Can Do with Demo Account

As an admin user, you have access to all features:

### ✅ Data Management
- ✅ Create, edit, and delete data sources
- ✅ Connect to PostgreSQL, MySQL, MongoDB, SQLite databases
- ✅ Test database connections
- ✅ View database schemas

### ✅ Query Management
- ✅ Write and execute SQL queries
- ✅ Save queries for reuse
- ✅ View query execution results
- ✅ View query execution time

### ✅ Dashboard Management
- ✅ Create new dashboards
- ✅ List all dashboards
- ✅ Edit dashboard details
- ✅ Delete dashboards

### ✅ User Management
- ✅ View user profile
- ✅ Access all admin features

---

## 🔐 Security Notes

### For Development/Testing
- ✅ This demo account is meant for testing and validation
- ✅ Perfect for demonstrations and evaluations
- ✅ Safe to use in development environments

### For Production
- ⚠️ **DO NOT** use demo credentials in production
- ⚠️ Delete or disable the demo account before production deployment
- ⚠️ Create strong, unique admin accounts for production use

---

## 🔧 How to Disable Demo Account (Production)

If deploying to production, disable the demo account:

```bash
cd /app/backend
python3 << 'EOF'
from app.core.database import SessionLocal
from app.models.user import User

db = SessionLocal()
demo_user = db.query(User).filter(User.email == "admin@nexbii.demo").first()
if demo_user:
    demo_user.is_active = False
    db.commit()
    print("✅ Demo account disabled")
db.close()
EOF
```

---

## 🎨 Login Page Features

### Auto-Fill Banner
The login page now includes a prominent amber-colored banner with:
- **Lightning icon** for quick identification
- **"Try Demo Account"** heading
- **Description** explaining the demo feature
- **"Fill Demo Credentials"** button for one-click auto-fill

### Visual Design
- Gradient amber background (from-amber-50 to-orange-50)
- Amber border for clear visibility
- Lightning bolt icon for "quick demo" association
- Hover effects on the button

---

## 📊 Test Scenarios

Use the demo account to test these scenarios:

### 1. Data Source Connection
```
1. Login with demo credentials
2. Navigate to "Data Sources"
3. Click "Add Data Source"
4. Try connecting to a test database
```

### 2. Query Execution
```
1. Login with demo credentials
2. Navigate to "Queries"
3. Click "Create Query"
4. Write a SQL query
5. Execute and view results
```

### 3. Dashboard Creation
```
1. Login with demo credentials
2. Navigate to "Dashboards"
3. Click "Create Dashboard"
4. Add name and description
5. Save dashboard
```

---

## 🆘 Troubleshooting

### Can't Login with Demo Credentials?

**Problem:** Login fails with demo credentials

**Solutions:**
1. Check that backend is running: `sudo supervisorctl status backend`
2. Verify database is accessible: `pg_isready`
3. Recreate demo user:
   ```bash
   cd /app/backend
   python3 << 'EOF'
   from app.core.database import SessionLocal
   from app.models.user import User, UserRole
   from app.core.security import get_password_hash
   
   db = SessionLocal()
   existing = db.query(User).filter(User.email == "admin@nexbii.demo").first()
   
   if existing:
       existing.hashed_password = get_password_hash("demo123")
       existing.is_active = True
   else:
       demo = User(
           email="admin@nexbii.demo",
           hashed_password=get_password_hash("demo123"),
           full_name="Demo Admin",
           role=UserRole.ADMIN,
           is_active=True
       )
       db.add(demo)
   
   db.commit()
   print("✅ Demo account ready")
   db.close()
   EOF
   ```

### Auto-Fill Button Not Working?

**Problem:** Button doesn't fill credentials

**Solution:**
- Refresh the browser page (Ctrl+R or Cmd+R)
- Clear browser cache
- Check that frontend is running: `sudo supervisorctl status frontend`

---

## 📚 Additional Resources

- **API Documentation:** http://localhost:8001/docs
- **Health Check:** http://localhost:8001/api/health
- **Frontend:** http://localhost:3000
- **Backend:** http://localhost:8001

---

**Happy Testing! 🎉**

For questions or issues, check the main README.md or PHASE1_AUDIT.md files.
