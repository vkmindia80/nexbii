# NexBII - Advanced Business Intelligence & Analytics Platform

🚀 A comprehensive, enterprise-grade business intelligence platform built with FastAPI and React.

## 📋 Project Overview

NexBII is an advanced BI platform that rivals Metabase, providing intuitive data exploration, visualization, and reporting tools for both technical and non-technical users.

**Phase 1 MVP Status:** ✅ **COMPLETE** (95%)

## 🗺️ Development Roadmap

See [ROADMAP.md](./ROADMAP.md) for the complete development plan, current status, and Phase 2 features.

## 🏗️ Architecture

- **Backend:** FastAPI (Python) - High-performance async API
- **Frontend:** React + TypeScript - Modern component-based UI
- **Database:** PostgreSQL (metadata) + MongoDB (optional)
- **Charts:** Apache ECharts - 20+ chart types
- **Authentication:** JWT-based with role-based access control

## 📦 Tech Stack

### Backend
- FastAPI 0.104+
- SQLAlchemy (PostgreSQL ORM)
- PyMongo (MongoDB)
- JWT Authentication
- Pandas for data processing

### Frontend
- React 18
- TypeScript
- Tailwind CSS
- Apache ECharts
- Axios for API calls
- React Router for navigation

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- Node.js 18+
- PostgreSQL 14+
- MongoDB (optional)

### Installation

1. **Install Backend Dependencies:**
```bash
cd /app/backend
pip install -r requirements.txt
```

2. **Install Frontend Dependencies:**
```bash
cd /app/frontend
yarn install
```

3. **Configure Environment:**

Backend `.env` file is located at `/app/backend/.env`
Frontend `.env` file is located at `/app/frontend/.env`

Update database URLs and other settings as needed.

4. **Start Services:**

```bash
# Start both services with supervisor
sudo supervisorctl start all

# Or start individually:
sudo supervisorctl start backend
sudo supervisorctl start frontend
```

5. **Access the Application:**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8001
- API Docs: http://localhost:8001/docs

### 🎯 Demo Credentials

For quick testing and validation, use the demo admin account:

**Email:** `admin@nexbii.demo`  
**Password:** `demo123`  
**Role:** Admin (full access)

> 💡 **Tip:** Click the "Fill Demo Credentials" button on the login page to auto-fill these credentials!

## 📊 Current Features (Phase 1 MVP)

### ✅ Completed
- User authentication (register/login)
- JWT-based security
- Data source management (PostgreSQL, MySQL, MongoDB, SQLite)
- Connection testing
- SQL query editor with execution
- Query management (save, list, delete)
- Dashboard CRUD operations
- Modern, responsive UI
- Role-based access control

### 🚧 In Development
- Visual query builder
- Chart visualizations (10 types)
- Dashboard builder with widgets
- Data source schema introspection
- Query result caching

## 🎯 Phase 1 Goals (Months 1-3)

Week 1-2: ✅ **Authentication & Project Setup**
- User registration and login
- JWT authentication
- Basic user management

Week 3-4: ✅ **Data Source Connectivity**
- PostgreSQL, MySQL, MongoDB, SQLite support
- Connection testing and validation
- Secure credential storage

Week 5-6: 🚧 **Visual Query Builder** (Next)
- Drag-and-drop interface
- Filter operations
- Join operations
- Aggregations

Week 7-8: **SQL Editor Enhancement**
- Syntax highlighting
- Query execution
- Result grid view
- Query history

Week 9-10: **Visualization Engine**
- 10 essential chart types
- Interactive charts
- Chart configuration UI

Week 11-12: **Dashboard System**
- Grid-based dashboard builder
- Widget management
- Dashboard sharing

## 📁 Project Structure

```
/app/
├── backend/              # FastAPI backend
│   ├── app/
│   │   ├── api/         # API endpoints
│   │   ├── core/        # Core config & security
│   │   ├── models/      # Database models
│   │   ├── schemas/     # Pydantic schemas
│   │   └── services/    # Business logic
│   ├── server.py        # Main FastAPI app
│   └── requirements.txt # Python dependencies
│
├── frontend/            # React frontend
│   ├── src/
│   │   ├── components/  # React components
│   │   ├── pages/       # Page components
│   │   ├── services/    # API services
│   │   └── types/       # TypeScript types
│   ├── package.json     # Node dependencies
│   └── tailwind.config.js
│
├── ROADMAP.md          # Complete development roadmap
└── README.md           # This file
```

## 🔒 Security Features

- JWT-based authentication
- Password hashing with bcrypt
- Role-based access control (Admin, Editor, Viewer)
- Secure database credential storage
- CORS protection
- SQL injection prevention

## 📝 API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - User login
- `GET /api/auth/me` - Get current user

### Data Sources
- `POST /api/datasources/` - Create data source
- `GET /api/datasources/` - List data sources
- `GET /api/datasources/{id}` - Get data source
- `POST /api/datasources/test` - Test connection
- `GET /api/datasources/{id}/schema` - Get schema
- `DELETE /api/datasources/{id}` - Delete data source

### Queries
- `POST /api/queries/` - Create query
- `GET /api/queries/` - List queries
- `GET /api/queries/{id}` - Get query
- `POST /api/queries/execute` - Execute query
- `DELETE /api/queries/{id}` - Delete query

### Dashboards
- `POST /api/dashboards/` - Create dashboard
- `GET /api/dashboards/` - List dashboards
- `GET /api/dashboards/{id}` - Get dashboard
- `PUT /api/dashboards/{id}` - Update dashboard
- `DELETE /api/dashboards/{id}` - Delete dashboard

## 🧪 Testing

```bash
# Backend tests (coming soon)
cd /app/backend
pytest

# Frontend tests (coming soon)
cd /app/frontend
yarn test
```

## 📈 Monitoring

Check service logs:
```bash
# Backend logs
tail -f /var/log/supervisor/backend.out.log
tail -f /var/log/supervisor/backend.err.log

# Frontend logs
tail -f /var/log/supervisor/frontend.out.log
```

Service status:
```bash
sudo supervisorctl status
```

## 🤝 Contributing

This is an active development project following a 12-month roadmap. See ROADMAP.md for planned features.

## 📄 License

MIT License

## 🎉 Acknowledgments

Built with modern technologies to provide an enterprise-grade BI solution that's both powerful and user-friendly.
