# Stock Tracking DC - InvenTree-Style Modernization Progress

**Started**: December 24, 2025
**Architecture**: Multi-container Docker setup with React frontend + Django REST API backend
**Inspiration**: InvenTree inventory management system

---

## 🎯 Project Goals

1. **Dockerize Application** - Multi-container setup (db, redis, backend, worker, frontend)
2. **Modern Frontend** - React 19 + Vite + Mantine UI (replacing Django templates)
3. **API-First Backend** - Django REST Framework with OpenAPI documentation
4. **Phased Migration** - Focus on Stock Management → Purchase Orders → Other features

---

## 📊 Overall Progress: 15% Complete

### ✅ Phase 1: Infrastructure & Foundation (Week 1-2) - 50% COMPLETE

#### ✅ 1.1 Docker Compose Architecture - DONE
- [x] Create `docker-compose.yml` - Production config with 5 services
- [x] Create `docker-compose.dev.yml` - Development overrides
- [x] Create `docker/backend/Dockerfile` - Multi-stage Python build
- [x] Create `docker/backend/gunicorn.conf.py` - Gunicorn production config
- [x] Create `docker/frontend/Dockerfile` - Multi-stage Node/React build
- [x] Create `docker/frontend/nginx.conf` - Frontend reverse proxy
- [x] Create `.dockerignore` - Build optimization
- [x] Create `.env.example` - Environment variables template

**Files Created**:
- `/docker-compose.yml`
- `/docker-compose.dev.yml`
- `/docker/backend/Dockerfile`
- `/docker/backend/gunicorn.conf.py`
- `/docker/frontend/Dockerfile`
- `/docker/frontend/nginx.conf`
- `/.dockerignore`
- `/.env.example`

#### 🔄 1.2 Project Restructuring - IN PROGRESS
- [ ] Create `src/backend/` directory structure
- [ ] Move existing Django app to `src/backend/`
  - [ ] Move `stock/` app
  - [ ] Move `stockmgtr/` settings
  - [ ] Move `manage.py`
  - [ ] Move `requirements.txt`
- [ ] Create `src/frontend/` directory
- [ ] Initialize React + Vite project
- [ ] Update import paths in Django code
- [ ] Test that existing app still runs

**Target Structure**:
```
Stock-Tracking-DC/
├── docker/                    ✅ DONE
│   ├── backend/
│   │   ├── Dockerfile
│   │   └── gunicorn.conf.py
│   └── frontend/
│       ├── Dockerfile
│       └── nginx.conf
├── src/
│   ├── backend/              ⏳ TODO
│   │   ├── stock/
│   │   ├── stockmgtr/
│   │   ├── manage.py
│   │   └── requirements.txt
│   └── frontend/             ⏳ TODO
│       ├── src/
│       ├── public/
│       ├── package.json
│       └── vite.config.ts
├── docker-compose.yml         ✅ DONE
├── docker-compose.dev.yml     ✅ DONE
├── .env.example              ✅ DONE
└── plan.md                   ✅ DONE
```

---

### ⏳ Phase 2: Backend API Modernization (Week 2-3) - NOT STARTED

#### 2.1 Install Django REST Framework
- [ ] Add DRF dependencies to requirements.txt
  - `djangorestframework==3.14.0`
  - `drf-spectacular==0.27.0` (OpenAPI)
  - `django-filter==23.5`
  - `djangorestframework-simplejwt==5.3.1`
- [ ] Update `settings.py` with DRF configuration
- [ ] Configure CORS for frontend communication

#### 2.2 Create API Layer Structure
- [ ] Create `src/backend/api/` Django app
- [ ] Create `api/serializers/` directory
- [ ] Create `api/views/` directory
- [ ] Create `api/permissions.py`
- [ ] Create `api/pagination.py`
- [ ] Create `api/filters.py`
- [ ] Create `api/urls.py` with DRF router

#### 2.3 Migrate Stock API (Core Feature #1)
- [ ] Create `api/serializers/stock.py`
  - StockSerializer
  - CategorySerializer
  - StockLocationSerializer
- [ ] Create `api/views/stock.py`
  - StockViewSet (list, retrieve, create, update, delete)
  - Custom actions: issue(), receive()
- [ ] Add API routes to `api/urls.py`
- [ ] Keep legacy views in `stock/views.py` for backward compatibility

#### 2.4 Authentication & Permissions
- [ ] Set up JWT token authentication
- [ ] Create `api/permissions.py` using existing UserRole model
- [ ] Map 9 existing roles to DRF permissions
- [ ] Test permission system

**API Endpoints (Stock)**:
```
GET    /api/v1/stock/                 - List all stock
POST   /api/v1/stock/                 - Create stock item
GET    /api/v1/stock/{id}/            - Get stock detail
PUT    /api/v1/stock/{id}/            - Update stock
DELETE /api/v1/stock/{id}/            - Delete stock
POST   /api/v1/stock/{id}/issue/      - Issue stock
POST   /api/v1/stock/{id}/receive/    - Receive stock
GET    /api/v1/categories/            - List categories
```

---

### ⏳ Phase 3: React Frontend Setup (Week 3-4) - NOT STARTED

#### 3.1 Initialize React + Vite
- [ ] Run `npm create vite@latest frontend -- --template react-ts`
- [ ] Install core dependencies:
  - `@mantine/core` `@mantine/hooks` `@mantine/notifications`
  - `zustand` `@tanstack/react-query` `axios`
  - `react-hook-form` `@hookform/resolvers` `zod`
  - `react-router-dom`
  - `@tabler/icons-react`

#### 3.2 Configure Vite
- [ ] Create `vite.config.ts` with:
  - Build output to `../backend/static/frontend`
  - API proxy to `http://localhost:8000`
  - Code splitting for vendor, ui, state

#### 3.3 Core Frontend Structure
- [ ] Create `src/states/userState.ts` (Zustand)
- [ ] Create `src/states/notificationState.ts`
- [ ] Create `src/api/client.ts` (Axios with auth interceptor)
- [ ] Create `src/router.tsx` (React Router)
- [ ] Create `src/components/Layout.tsx`
- [ ] Create `src/components/ProtectedRoute.tsx`

#### 3.4 Authentication UI
- [ ] Create `src/pages/Login.tsx`
- [ ] Create `src/pages/Dashboard.tsx`
- [ ] Implement JWT token storage
- [ ] Implement login/logout flow

---

### ⏳ Phase 4: Migrate Stock Management UI (Week 4-5) - NOT STARTED

#### 4.1 Stock List Page
- [ ] Create `src/pages/stock/StockList.tsx`
- [ ] Create `src/components/stock/StockTable.tsx` (Mantine DataTable)
- [ ] Create `src/components/stock/StockFilters.tsx`
- [ ] Implement search functionality
- [ ] Implement filtering (category, location, condition)
- [ ] Connect to `/api/v1/stock/` endpoint

#### 4.2 Stock Detail Page
- [ ] Create `src/pages/stock/StockDetail.tsx`
- [ ] Display stock information
- [ ] Show stock history
- [ ] Show location information
- [ ] Add Issue/Receive buttons

#### 4.3 Stock Forms
- [ ] Create `src/components/stock/StockForm.tsx`
- [ ] Create `src/pages/stock/CreateStock.tsx`
- [ ] Create `src/pages/stock/EditStock.tsx`
- [ ] Implement React Hook Form with Zod validation
- [ ] Connect to API endpoints

---

### ⏳ Phase 5: Migrate Purchase Orders (Week 6-7) - NOT STARTED

#### 5.1 PurchaseOrder API
- [ ] Create `api/serializers/purchase_order.py`
- [ ] Create `api/views/purchase_order.py`
- [ ] Add custom actions: submit(), receive_items()

#### 5.2 Frontend PO Management
- [ ] Create `src/pages/po/PurchaseOrderList.tsx`
- [ ] Create `src/pages/po/PurchaseOrderDetail.tsx`
- [ ] Create `src/pages/po/CreatePurchaseOrder.tsx`
- [ ] Create `src/pages/po/ReceiveItems.tsx`

---

### ⏳ Phase 6: Additional Features (Week 8+) - NOT STARTED

- [ ] Stock Transfers API + UI
- [ ] Inventory Audits API + UI
- [ ] Real-time Notifications (WebSockets)
- [ ] Dashboard with Charts (Recharts)
- [ ] Reports & Analytics

---

## 🔧 Current Working Directory

```
/home/vboxuser/Documents/Stock-Tracking-DC/
```

---

## 📝 Recent Changes

### December 24, 2025 - Session 1
- Created Docker infrastructure (docker-compose, Dockerfiles, configs)
- Set up multi-container architecture (db, redis, backend, worker, frontend)
- Created environment template (.env.example)
- Created .dockerignore for build optimization
- Created this plan.md file for tracking progress

---

## 🚀 Next Steps

1. **Restructure Project** (Phase 1.2):
   - Move existing Django code to `src/backend/`
   - Initialize React app in `src/frontend/`

2. **Test Docker Setup**:
   - Copy `.env.example` to `.env` and configure
   - Run `docker-compose -f docker-compose.dev.yml up`
   - Verify all containers start successfully

3. **Begin Phase 2** (Backend API):
   - Install Django REST Framework
   - Create API layer structure
   - Start migrating Stock endpoints

---

## 📚 Technical Stack

### Backend
- **Framework**: Django 5.2.5
- **API**: Django REST Framework 3.14
- **Database**: MySQL 8.0
- **Cache**: Redis 7
- **Task Queue**: Celery 5.3.4
- **Server**: Gunicorn (production)
- **Documentation**: drf-spectacular (OpenAPI)

### Frontend
- **Framework**: React 19
- **Build Tool**: Vite 7
- **UI Library**: Mantine 8
- **State**: Zustand
- **Data Fetching**: TanStack Query
- **Forms**: React Hook Form + Zod
- **Routing**: React Router 6
- **HTTP**: Axios
- **Icons**: Tabler Icons

### DevOps
- **Containerization**: Docker + Docker Compose
- **Web Server**: nginx (production frontend)
- **Reverse Proxy**: nginx
- **Deployment**: Railway

---

## 📖 References

- **InvenTree Source**: `/home/vboxuser/Documents/project/InvenTree`
- **Detailed Plan**: `/home/vboxuser/.claude/plans/replicated-cooking-zephyr.md`
- **Current Code**: `/home/vboxuser/Documents/Stock-Tracking-DC/`

---

## ⚠️ Important Notes

1. **Backward Compatibility**: Keep existing Django views during migration
2. **Database**: No schema changes required - models stay the same
3. **Permissions**: Map existing 9 roles to DRF permissions
4. **Zero Downtime**: Deploy each phase incrementally
5. **Testing**: Test each phase before moving to next

---

## 🎯 Success Criteria

- [ ] All containers start successfully with docker-compose
- [ ] Frontend communicates with backend API
- [ ] Stock management works in new React UI
- [ ] Purchase orders work in new React UI
- [ ] All 9 user roles work correctly
- [ ] Performance: API response < 200ms (p95)
- [ ] Performance: Frontend bundle < 500KB (gzipped)
- [ ] Mobile responsive design
- [ ] OpenAPI documentation accessible

---

**Last Updated**: December 24, 2025
**Status**: Phase 1.1 Complete (Docker Infrastructure) ✅
**Next**: Phase 1.2 (Project Restructuring) ⏳
