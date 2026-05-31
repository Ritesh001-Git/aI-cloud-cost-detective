# AI Cloud Cost Detective 🔍💰

An enterprise-grade, multi-cloud FinOps platform that automates the discovery, analysis, and remediation of infrastructure cost leaks. By combining native cloud APIs with **Gemini 2.5 Flash**, the platform identifies idle resources, over-provisioned tiers, and architectural anomalies across AWS, Azure, and GCP—providing real-time progress updates and one-click remediation CLI commands.

## 🚀 Key Features

- **Multi-Cloud Ingestion Engine:** Unified strategy pattern to dynamically scan infra across **AWS Regions** (via Boto3), **Azure Resource Groups** (via Azure CLI), and **GCP Projects** (via Google Client APIs).
- **Asynchronous Streaming Pipelines:** Live multi-stage orchestration updates pushed from backend to frontend via **FastAPI WebSockets**.
- **Deterministic AI Analysis:** Leverages **Gemini 2.5 Flash** with strict Pydantic schemas (`extra="forbid"`) to guarantee parseable, structured JSON cost optimization insights.
- **Secure Persistence & Auditing:** Complete user session security via custom **JWT authentication** backed by an **Azure PostgreSQL (Flexible Server)** storage ledger utilizing `JSONB` for flexible run records.
- **Production-Ready Operations:** Fully containerized architecture using **Docker**, managed via **Azure Container Apps (ACA)**, automated through **Jenkins CI/CD**, and monitored using **Prometheus & Grafana**.

---

## 🏗️ System Architecture

The application is split into a decoupled decoupled React frontend and a FastAPI backend strategy framework:

```
                                  ┌──────────────┐
                                  │  DEVELOPER   │
                                  └──────┬───────┘
                                         │
                                         ▼ [Jenkins CI/CD Pipeline]
                                  ┌──────────────────────┐
                                  │ AZURE CONTAINER APPS │
                                  │  (Docker Container)  │
                                  └──────────────────────┘
                                             │
=============================================│=============================================
                                             ▼
                                      ┌──────────────┐
                                      │     USER     │
                                      └──────┬───────┘
                                             │
                                             ▼
                                  ┌──────────────────────┐
                                  │    REACT FRONTEND    │
                                  │(Vite + TS + Tailwind)│
                                  └──────────┬───────────┘
                                             │
                                             │ HTTP Rest & WebSockets
                                             ▼
                                  ┌──────────────────────┐      ┌──────────────────────┐
                                  │    PYTHON BACKEND    │◄────►│   AZURE KEY VAULT    │
                                  │      (FastAPI)       │      │  (Secrets Rotation)  │
                                  │                      │      └──────────────────────┘
                                  │ · Custom JWT Auth    │      ┌──────────────────────┐
                                  │ · Registry Pattern   │◄────►│ PROMETHEUS & GRAFANA │
                                  └────┬───┬───┬──────┬──┘      │   (Observability)    │
                                       │   │   │      │         └──────────────────────┘
            ┌──────────────────────────┘   │   │      └──────────────────────────┐
            │                              │   │                                 │
            ▼                              │   ▼ [Async Tasks]                   ▼ [Structured JSON]
┌──────────────────────┐                   │ ┌──────────────────────┐  ┌──────────────────────┐
│ MULTI-CLOUD ENGINES  │                   │ │   FASTAPI WEBSOCKET  │  │  GEMINI 2.5 FLASH    │
│  (CLI/API Wrappers)  │                   │ │  (Progress Channel)  │  │        API           │
├──────────────────────┤                   │ └──────────┬───────────┘  ├──────────────────────┤
│ · AWS SDK (Boto3)    │                   │            │              │ · System Prompt      │
│ · Azure CLI (`az`)   │                   │            │ Live Updates │ · Config:            │
│ · GCP Client APIs    │                   │            ▼              │   response_schema    │
└──────────┬───────────┘                   │ ┌──────────────────────┐  │   extra="forbid"     │
           │                               │ │    REACT FRONTEND    │  └──────────┬───────────┘
           ▼ [Raw Ingestion]               │ │  (ProgressTracker)   │             │
┌──────────────────────┐                   │ └──────────────────────┘             │ Discovered Insights
│ TARGET CLOUD SCOPES  │                   │                                      │ & Fix Commands
├──────────────────────┤                   │                                      │
│ · AWS Regions        │                   └──────────────────┐                   │
│ · Azure Resource Grps│                                      │                   │
│ · GCP Projects       │                                      ▼                   ▼
└──────────────────────┘                             ┌──────────────────────────────────┐
                                                     │         AZURE POSTGRESQL         │
                                                     │         (Flexible Server)        │
                                                     ├──────────────────────────────────┤
                                                     │ · users: Auth metadata           │
                                                     │ · analyses: Multi-Cloud JSONB    │
                                                     └────────────────┬─────────────────┘
                                                                      │
                                                                      │ Hydrates view on mount
                                                                      ▼
                                                     ┌──────────────────────────────────┐
                                                     │          REACT FRONTEND          │
                                                     │ (Interactive Reports, Severity   │
                                                     │  Badges, & Copyable CLI Fixes)   │
                                                     └──────────────────────────────────┘
```

---

## 🔄 End-to-End Request Flow

1. **Authentication:** User updates/registers profile ➔ FastAPI issues signature-verified custom **JWT** ➔ Stored in local user environment context.
2. **Target Scoping:** UI triggers regional baseline fetch paths matching cloud provider registries (`aws`, `azure`, `gcp`).
3. **Ingestion Loop:** Backend executes selected environment module ➔ maps infrastructure topology footprints cleanly to intermediate data object.
4. **WebSocket Streaming:** Concurrent generation steps stream real-time task markers down to the frontend components via standard WebSockets.
5. **AI Evaluation:** Normalized configuration data structures load directly to **Gemini 2.5 Flash** using forced schema layouts to strip unpredictable parsing failures.
6. **Persistence:** Complete run history blocks, target calculations, and native mitigation commands write straight to the database core.
7. **Visualization UI:** React hydrates a clean, dynamic dashboard featuring color-coded priority alerts and copy-to-clipboard automation blocks.

---

## 📁 Repository Structure

```text
ai-cloud-cost-detective/
├── backend/
│   ├── providers/
│   │   ├── __init__.py
│   │   ├── base.py              # Scanner Abstract Base Class
│   │   ├── aws_scanner.py       # AWS Boto3 metric collector
│   │   ├── azure_scanner.py     # Azure CLI JSON mapper
│   │   └── gcp_scanner.py       # Google Cloud Core API processor
│   ├── main.py                  # API endpoints, Lifespan configuration, & WebSocket routers
│   ├── db.py                    # Connection engine, table models, & async queries
│   ├── ai_analyzer.py           # Gemini 2.5 Flash API connector with schema config
│   ├── requirements.txt         # Core Python server libraries
│   └── .env.example             # Backend variables setup block
├── frontend/
│   ├── src/
│   │   ├── context/
│   │   │   └── AuthContext.tsx  # Secure API Client and interceptors
│   │   ├── pages/
│   │   │   ├── Login.tsx
│   │   │   ├── Signup.tsx
│   │   │   ├── Dashboard.tsx    # Multi-Cloud scan command interface
│   │   │   ├── Report.tsx       # Live visualization cards & copy blocks
│   │   │   └── History.tsx      # Historic diagnostics grid view
│   │   ├── components/
│   │   │   ├── ProgressTracker.tsx # WebSocket dynamic state tracker
│   │   │   └── Navbar.tsx
│   │   ├── main.tsx
│   │   └── App.tsx
│   ├── package.json
│   ├── tailwind.config.js
│   ├── vite.config.ts
│   └── .gitignore
└── Dockerfile
```

## 🛠️ Local Development Setup
Prerequisites

-  Python 3.11+
-  Node.js 18+
-  PostgreSQL server (running locally via Homebrew or Docker)
-  Configured Cloud CLIs (aws configure, az login, or gcloud auth login)

### 1. Database Setup
Ensure you have a target database running locally:

`createdb cloud_cost_detective`

### 2. Backend Initialization
```
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```
### 3. Create a .env file in the backend/ folder

```
DATABASE_URL=postgresql+asyncpg://<your_username>@localhost:5432/cloud_cost_detective
JWT_SECRET=your_generated_cryptographic_32_byte_string
GEMINI_API_KEY=your_google_ai_studio_api_key
GEMINI_MODEL=gemini-2.5-flash
```

### 4. Run the API engine:

`uvicorn main:app --reload --port 8000`

### 5. Frontend Initialization
```
cd ../frontend
npm install
npm run dev
```

### 6. Open your browser to http://localhost:5173 to interact with the platform dashboard.

