## AI Cloud Cost Detective - Request Flow

```
①  User ─·─·─► React Frontend ─·─·─► FastAPI Middleware ─·─·─► Custom JWT Auth Verification (Azure PostgreSQL)
                                                                       │
②  User selects Provider (AWS/Azure/GCP) & Target Scope ◄───[Hydrates Scopes via API]
         │
         ▼
③  FastAPI Backend ─·─·─► Multi-Cloud Registry Module
                                 │
                                 ├───► (AWS)   ─► Boto3 SDK ──────────┐
                                 ├───► (Azure) ─► Azure CLI (`az`) ───┼─► Ingests Raw Infrastructure State
                                 └───► (GCP)   ─► Google Client API ──┘
                                                                       │
④  FastAPI WebSocket Channel ◄─·─·─·─·─·─ [Emits Stage Milestones] ───┘
         │
         ▼ [Pushes Live State Packets]
    React ProgressTracker (Timeline Stepper Visualization)
                                                                       │
⑤  Normalized Resource Payload ─·─·─► Gemini 2.5 Flash API ────────────┘
                                        │ (Enforced Pydantic Schema: extra="forbid")
                                        ▼
⑥  Structured AI Insights ─·─·─► Azure PostgreSQL ─·─·─► Stores Comprehensive Run Ledger (JSONB)
                                        │
                                        ▼ [Resolves Background Task Promise]
⑦  React Report Dashboard ◄·─·─·─·─·─·──┘ (Renders Color-Coded Severity Badges & Copyable CLI Remediation Fixes)
```
