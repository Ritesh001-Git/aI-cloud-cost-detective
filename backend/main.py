import asyncio
from contextlib import asynccontextmanager
from typing import Any, Literal
from uuid import UUID, uuid4

from fastapi import (
    BackgroundTasks,
    Depends,
    FastAPI,
    HTTPException,
    Query,
    Security,
    WebSocket,
    WebSocketDisconnect,
    status,
)
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, Field

import db
from auth import (
    create_access_token,
    decode_access_token,
    hash_password,
    validate_configuration,
    verify_password,
)
from ai_analyzer import AIAnalysisError, AIAnalyzer
from providers import AWSScanner, AzureScanner, BaseScanner, GCPScanner, ScannerError

Provider = Literal["aws", "azure", "gcp"]
bearer_scheme = HTTPBearer(auto_error=False)


@asynccontextmanager
async def lifespan(_: FastAPI):
    validate_configuration()
    await db.connect()
    try:
        yield
    finally:
        await db.close()


app = FastAPI(title="AI Cloud Cost Detective API", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SCANNERS: dict[str, BaseScanner] = {
    "aws": AWSScanner(),
    "azure": AzureScanner(),
    "gcp": GCPScanner(),
}


class AnalyzeRequest(BaseModel):
    provider: Provider
    target_scope: str = Field(min_length=1)


class AuthRequest(BaseModel):
    email: str = Field(min_length=3, max_length=320)
    password: str = Field(min_length=8, max_length=128)


class ConnectionManager:
    def __init__(self) -> None:
        self.connections: dict[UUID, set[WebSocket]] = {}
        self.latest_events: dict[UUID, dict[str, Any]] = {}
        self.owners: dict[UUID, UUID] = {}

    async def connect(self, analysis_id: UUID, websocket: WebSocket) -> None:
        await websocket.accept()
        self.connections.setdefault(analysis_id, set()).add(websocket)
        if event := self.latest_events.get(analysis_id):
            await websocket.send_json(event)

    def disconnect(self, analysis_id: UUID, websocket: WebSocket) -> None:
        sockets = self.connections.get(analysis_id)
        if sockets is None:
            return
        sockets.discard(websocket)
        if not sockets:
            self.connections.pop(analysis_id, None)

    async def broadcast(self, analysis_id: UUID, event: dict[str, Any]) -> None:
        packet = {"analysis_id": str(analysis_id), **event}
        self.latest_events[analysis_id] = packet
        disconnected: list[WebSocket] = []
        for websocket in self.connections.get(analysis_id, set()).copy():
            try:
                await websocket.send_json(packet)
            except (WebSocketDisconnect, RuntimeError):
                disconnected.append(websocket)
        for websocket in disconnected:
            self.disconnect(analysis_id, websocket)


manager = ConnectionManager()


def authenticated_user_id(
    credentials: HTTPAuthorizationCredentials | None = Security(bearer_scheme),
) -> UUID:
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return decode_access_token(credentials.credentials)


async def _progress(
    analysis_id: UUID,
    *,
    provider: Provider,
    target_scope: str,
    progress: int,
    message: str,
    state: str = "running",
    result: dict[str, Any] | None = None,
) -> None:
    await manager.broadcast(
        analysis_id,
        {
            "status": state,
            "progress": progress,
            "provider": provider,
            "target_scope": target_scope,
            "message": message,
            "result": result,
        },
    )


async def run_analysis(
    analysis_id: UUID, user_id: UUID, request: AnalyzeRequest
) -> None:
    provider_label = request.provider.upper()
    try:
        await _progress(
            analysis_id,
            provider=request.provider,
            target_scope=request.target_scope,
            progress=5,
            message=(
                f"Connecting to {provider_label} and validating environment parameters..."
            ),
        )
        await _progress(
            analysis_id,
            provider=request.provider,
            target_scope=request.target_scope,
            progress=20,
            message=(
                "Scanning active infrastructure footprint within target scope "
                f"{request.target_scope}..."
            ),
        )
        resources = await asyncio.to_thread(
            SCANNERS[request.provider].scan_resources, request.target_scope
        )
        await _progress(
            analysis_id,
            provider=request.provider,
            target_scope=request.target_scope,
            progress=45,
            message="Normalizing resource configuration maps...",
        )
        await _progress(
            analysis_id,
            provider=request.provider,
            target_scope=request.target_scope,
            progress=60,
            message="Analyzing target profile costs with Gemini engine...",
        )
        analysis = await asyncio.to_thread(
            AIAnalyzer(request.provider, resources).analyze
        )
        result = {
            **analysis.model_dump(),
            "resources_scanned": len(resources),
            "provider": request.provider,
            "target_scope": request.target_scope,
        }
        await _progress(
            analysis_id,
            provider=request.provider,
            target_scope=request.target_scope,
            progress=85,
            message="Persisting structured analysis recommendations to ledger...",
        )
        await db.save_completed_analysis(
            analysis_id=analysis_id,
            user_id=user_id,
            provider=request.provider,
            target_scope=request.target_scope,
            resources_scanned=len(resources),
            analysis_result=result,
        )
        await _progress(
            analysis_id,
            provider=request.provider,
            target_scope=request.target_scope,
            progress=100,
            message="Analysis complete",
            state="completed",
            result=result,
        )
    except (AIAnalysisError, ScannerError, db.DatabaseError) as exc:
        await _progress(
            analysis_id,
            provider=request.provider,
            target_scope=request.target_scope,
            progress=100,
            message=str(exc),
            state="failed",
        )


@app.get("/api/accounts-or-groups")
async def accounts_or_groups(
    provider: Provider = Query(...),
    _: UUID = Depends(authenticated_user_id),
):
    try:
        scopes = await asyncio.to_thread(SCANNERS[provider].list_scopes)
    except ScannerError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message) from exc
    return {"provider": provider, "scopes": scopes}


@app.post("/api/auth/signup", status_code=status.HTTP_201_CREATED)
async def signup(request: AuthRequest):
    try:
        user_id = await db.create_user(
            request.email.lower().strip(), hash_password(request.password)
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except db.DatabaseError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {
        "access_token": create_access_token(user_id, request.email),
        "token_type": "bearer",
    }


@app.post("/api/auth/login")
async def login(request: AuthRequest):
    try:
        user = await db.get_user_by_email(request.email.lower().strip())
    except db.DatabaseError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    if user is None or not verify_password(request.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid email or password.")
    return {
        "access_token": create_access_token(user["id"], user["email"]),
        "token_type": "bearer",
    }


@app.post("/api/analyze", status_code=status.HTTP_202_ACCEPTED)
async def analyze(
    request: AnalyzeRequest,
    background_tasks: BackgroundTasks,
    user_id: UUID = Depends(authenticated_user_id),
):
    analysis_id = uuid4()
    manager.owners[analysis_id] = user_id
    background_tasks.add_task(run_analysis, analysis_id, user_id, request)
    return {
        "analysis_id": analysis_id,
        "status": "accepted",
        "websocket_url": f"/ws/progress/{analysis_id}",
    }


@app.get("/api/history")
async def history(user_id: UUID = Depends(authenticated_user_id)):
    try:
        return {"analyses": await db.get_analysis_history(user_id)}
    except db.DatabaseError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.websocket("/ws/progress/{analysis_id}")
async def progress(websocket: WebSocket, analysis_id: UUID, token: str = Query(...)):
    try:
        user_id = decode_access_token(token)
    except HTTPException:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return
    if manager.owners.get(analysis_id) != user_id:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return
    await manager.connect(analysis_id, websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(analysis_id, websocket)
