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
