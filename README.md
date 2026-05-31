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

