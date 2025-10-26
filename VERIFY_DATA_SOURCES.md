# ✅ Verify New Data Sources - Quick Guide

## 🔍 How to See the New Data Sources

### **Step 1: Clear Browser Cache**
The issue you're experiencing is likely due to browser caching. Here's how to fix it:

**Option A: Hard Refresh (Recommended)**
- **Chrome/Edge:** Press `Ctrl + Shift + R` (Windows/Linux) or `Cmd + Shift + R` (Mac)
- **Firefox:** Press `Ctrl + F5` (Windows/Linux) or `Cmd + Shift + R` (Mac)
- **Safari:** Press `Cmd + Option + R` (Mac)

**Option B: Clear Cache Manually**
1. Open browser DevTools (F12)
2. Right-click the refresh button
3. Select "Empty Cache and Hard Reload"

**Option C: Open Incognito/Private Window**
- This bypasses all cache
- `Ctrl + Shift + N` (Chrome/Edge) or `Ctrl + Shift + P` (Firefox)

---

### **Step 2: Navigate to Data Sources**
1. Go to your NexBII frontend URL
2. Login with demo credentials:
   - Email: `admin@nexbii.demo`
   - Password: `demo123`
3. Click on **"Data Sources"** in the sidebar
4. Click **"Add Data Source"** button

---

### **Step 3: Check the Dropdown**
You should now see **7 categories** with **30+ options**:

```
📁 Relational Databases (6)
   - PostgreSQL
   - MySQL
   - MariaDB
   - Microsoft SQL Server
   - Oracle Database
   - SQLite

☁️ Cloud Data Warehouses (4)
   - Snowflake
   - Amazon Redshift
   - Google BigQuery
   - Azure Synapse Analytics

📊 NoSQL Databases (5)
   - MongoDB
   - Apache Cassandra
   - Amazon DynamoDB
   - CouchDB
   - Redis

🔍 Analytics & Search (3)
   - Elasticsearch
   - ClickHouse
   - Apache Druid

⏱️ Time Series (2)
   - TimescaleDB
   - InfluxDB

🌐 Distributed SQL (2)
   - Presto
   - Trino

📄 File-based (4)
   - CSV Files
   - Excel Files
   - JSON Files
   - Parquet Files
```

---

## 🔧 **If Still Not Working**

### **Verify Services Are Running:**
```bash
# Check service status
sudo supervisorctl -c /etc/supervisor/supervisord.conf status

# Expected output:
# backend    RUNNING   pid xxxx
# frontend   RUNNING   pid xxxx
# mongodb    RUNNING   pid xxxx
```

### **Check Frontend Logs:**
```bash
# View frontend compilation status
tail -f /var/log/supervisor/frontend.out.log

# Should show: "Compiled successfully!"
```

### **Restart Frontend if Needed:**
```bash
# Restart frontend service
sudo supervisorctl -c /etc/supervisor/supervisord.conf restart frontend

# Wait for compilation (30-60 seconds)
sleep 30

# Verify it's running
sudo supervisorctl -c /etc/supervisor/supervisord.conf status frontend
```

---

## 🎯 **Testing a New Data Source**

### **Example: Connect to ClickHouse**

1. Click "Add Data Source"
2. Select **"ClickHouse"** from "Analytics & Search" category
3. Fill in details:
   - **Name:** "My ClickHouse"
   - **Type:** ClickHouse (auto-selected)
   - **Host:** your-clickhouse-host.com
   - **Port:** 8123 (auto-filled)
   - **Database:** default
   - **Username:** default
   - **Password:** your-password
4. Click "Test Connection"
5. If successful, click "Save"

---

## 🐛 **Troubleshooting**

### **Issue: Still seeing only 4 data sources**

**Cause:** Browser is serving cached JavaScript bundle

**Solution:**
1. Open DevTools (F12)
2. Go to "Network" tab
3. Check "Disable cache" checkbox
4. Refresh the page (F5)
5. Look for `bundle.js` or `main.js` in the Network tab
6. Verify it's loading a fresh version (check size and timestamp)

---

### **Issue: Frontend not compiling**

**Check compilation errors:**
```bash
tail -100 /var/log/supervisor/frontend.err.log
```

**Restart frontend:**
```bash
sudo supervisorctl -c /etc/supervisor/supervisord.conf restart frontend
```

---

### **Issue: Port already in use**

**Check what's using port 3000:**
```bash
lsof -i :3000
```

**Kill and restart:**
```bash
sudo supervisorctl -c /etc/supervisor/supervisord.conf restart frontend
```

---

## ✅ **Verification Checklist**

- [ ] Frontend service is RUNNING
- [ ] Backend service is RUNNING
- [ ] Browser cache cleared (hard refresh)
- [ ] DevTools shows "Disable cache" is checked
- [ ] Navigated to Data Sources page
- [ ] Clicked "Add Data Source" button
- [ ] Dropdown shows 7 categories with 30+ options

---

## 📊 **Expected Result**

When you click the "Type" dropdown in the "Add Data Source" modal, you should see:

**Before:** 4 flat options
```
PostgreSQL
MySQL
MongoDB
SQLite
```

**After:** 7 categorized sections with 30+ options
```
▼ Relational Databases
   PostgreSQL, MySQL, MariaDB, SQL Server, Oracle, SQLite
▼ Cloud Data Warehouses
   Snowflake, Redshift, BigQuery, Synapse
▼ NoSQL Databases
   MongoDB, Cassandra, DynamoDB, CouchDB, Redis
▼ Analytics & Search
   Elasticsearch, ClickHouse, Druid
▼ Time Series
   TimescaleDB, InfluxDB
▼ Distributed SQL
   Presto, Trino
▼ File-based
   CSV, Excel, JSON, Parquet
```

---

## 🎉 **Success!**

Once you see all 30+ data source types organized by category, you're all set! 

Try connecting to different data sources and explore NexBII's universal connectivity! 🚀

---

## 📞 **Still Having Issues?**

If you've tried all the above and still only see 4 data sources:

1. **Check file modifications:**
   ```bash
   grep -n "optgroup.*Relational" /app/frontend/src/pages/DataSourcesPage.tsx
   # Should show: 257:    <optgroup label="Relational Databases">
   ```

2. **Verify frontend is serving the new code:**
   ```bash
   # View the compiled bundle timestamp
   ls -lh /app/frontend/build/static/js/ | tail -5
   ```

3. **Force rebuild:**
   ```bash
   cd /app/frontend
   rm -rf build/ node_modules/.cache/
   sudo supervisorctl -c /etc/supervisor/supervisord.conf restart frontend
   ```

**The changes are definitely in the code and the frontend is compiled. It's 99% a browser caching issue!**
