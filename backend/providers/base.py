import json
import subprocess
from abc import ABC, abstractmethod
from typing import Any


class ScannerError(Exception):
    def __init__(self, message: str, status_code: int = 500) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code


class BaseScanner(ABC):
    provider: str
    cli_name: str

    @abstractmethod
    def list_scopes(self) -> list[dict[str, Any]]:
        """Return the account or grouping boundaries available to scan."""

    @abstractmethod
    def scan_resources(self, target_scope: str) -> list[dict[str, Any]]:
        """Return normalized resources within the requested scope."""

    def _run_json(self, command: list[str]) -> Any:
        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                check=True,
            )
        except FileNotFoundError as exc:
            raise ScannerError(
                f"{self.cli_name} CLI is not installed or is not available on PATH.",
                status_code=500,
            ) from exc
        except subprocess.CalledProcessError as exc:
            details = (exc.stderr or exc.stdout or "").strip()
            message = (
                f"{self.provider.upper()} CLI command failed. Check that you are logged in "
                "and that the requested scope is valid."
            )
            if details:
                message = f"{message} CLI output: {details}"
            raise ScannerError(message, status_code=400) from exc

        try:
            return json.loads(result.stdout or "[]")
        except json.JSONDecodeError as exc:
            raise ScannerError(
                f"{self.provider.upper()} CLI returned invalid JSON.",
                status_code=500,
            ) from exc

    def _resource(
        self,
        *,
        resource_type: str,
        name: str,
        resource_id: str,
        location: str | None = None,
        sku_or_size: str | None = None,
        tags: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        return {
            "provider": self.provider,
            "type": resource_type,
            "name": name,
            "id": resource_id,
            "location": location,
            "sku_or_size": sku_or_size,
            "tags": tags or {},
        }
