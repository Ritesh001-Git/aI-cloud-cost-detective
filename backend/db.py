import json
import os
from typing import Any
from uuid import UUID, uuid4

import asyncpg
from dotenv import load_dotenv

load_dotenv()

_pool: asyncpg.Pool | None = None


class DatabaseError(Exception):
    pass


def _database_url() -> str:
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise DatabaseError(
            "DATABASE_URL is not configured. Add the managed PostgreSQL connection URL "
            "to the backend environment."
        )
    return database_url.replace("postgresql+asyncpg://", "postgresql://", 1)


async def connect() -> None:
    global _pool
    if _pool is not None:
        return
    try:
        _pool = await asyncpg.create_pool(dsn=_database_url(), min_size=1, max_size=10)
        await initialize_schema()
    except (asyncpg.PostgresError, OSError, ValueError) as exc:
        _pool = None
        raise DatabaseError(
            "Unable to connect to managed PostgreSQL. Check DATABASE_URL, network access, "
            "and SSL settings."
        ) from exc


async def close() -> None:
    global _pool
    if _pool is not None:
        await _pool.close()
        _pool = None


def _get_pool() -> asyncpg.Pool:
    if _pool is None:
        raise DatabaseError("Database pool is not initialized.")
    return _pool


async def initialize_schema() -> None:
    async with _get_pool().acquire() as connection:
        await connection.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id UUID PRIMARY KEY,
                email VARCHAR(320) UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
            );

            CREATE TABLE IF NOT EXISTS analyses (
                id UUID PRIMARY KEY,
                user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                provider VARCHAR(16) NOT NULL CHECK (provider IN ('aws', 'azure', 'gcp')),
                target_scope VARCHAR(512) NOT NULL,
                resources_scanned INT NOT NULL,
                issues_found INT NOT NULL,
                estimated_savings NUMERIC(14, 2) NOT NULL,
                analysis_result JSONB NOT NULL,
                status VARCHAR(32) NOT NULL,
                created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
            );

            CREATE INDEX IF NOT EXISTS analyses_user_created_at_idx
                ON analyses (user_id, created_at DESC);
            """
        )


async def save_completed_analysis(
    *,
    analysis_id: UUID,
    user_id: UUID,
    provider: str,
    target_scope: str,
    resources_scanned: int,
    analysis_result: dict[str, Any],
) -> None:
    try:
        await _get_pool().execute(
            """
            INSERT INTO analyses (
                id, user_id, provider, target_scope, resources_scanned, issues_found,
                estimated_savings, analysis_result, status
            )
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8::jsonb, 'completed')
            """,
            analysis_id,
            user_id,
            provider,
            target_scope,
            resources_scanned,
            len(analysis_result["issues"]),
            analysis_result["total_estimated_monthly_savings"],
            json.dumps(analysis_result),
        )
    except asyncpg.ForeignKeyViolationError as exc:
        raise DatabaseError(
            "The authenticated user does not exist in the users table."
        ) from exc
    except asyncpg.PostgresError as exc:
        raise DatabaseError("Unable to persist the completed analysis.") from exc


async def create_user(email: str, password_hash: str) -> UUID:
    user_id = uuid4()
    try:
        await _get_pool().execute(
            """
            INSERT INTO users (id, email, password_hash)
            VALUES ($1, $2, $3)
            """,
            user_id,
            email,
            password_hash,
        )
    except asyncpg.UniqueViolationError as exc:
        raise DatabaseError("A user with that email already exists.") from exc
    except asyncpg.PostgresError as exc:
        raise DatabaseError("Unable to create the user.") from exc
    return user_id


async def get_user_by_email(email: str) -> dict[str, Any] | None:
    try:
        record = await _get_pool().fetchrow(
            """
            SELECT id, email, password_hash, created_at
            FROM users
            WHERE email = $1
            """,
            email,
        )
    except asyncpg.PostgresError as exc:
        raise DatabaseError("Unable to load the user account.") from exc
    return dict(record) if record else None


async def get_analysis_history(user_id: UUID) -> list[dict[str, Any]]:
    try:
        records = await _get_pool().fetch(
            """
            SELECT id, provider, target_scope, resources_scanned, issues_found,
                   estimated_savings, analysis_result, status, created_at
            FROM analyses
            WHERE user_id = $1
            ORDER BY created_at DESC
            """,
            user_id,
        )
    except asyncpg.PostgresError as exc:
        raise DatabaseError("Unable to load analysis history.") from exc
    history = []
    for record in records:
        item = dict(record)
        if isinstance(item["analysis_result"], str):
            item["analysis_result"] = json.loads(item["analysis_result"])
        history.append(item)
    return history
