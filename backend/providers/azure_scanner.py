from typing import Any

from .base import BaseScanner


class AzureScanner(BaseScanner):
    provider = "azure"
    cli_name = "Azure"

    def list_scopes(self) -> list[dict[str, Any]]:
        groups = self._run_json(["az", "group", "list", "--output", "json"])
        return [
            {
                "id": group["name"],
                "name": group["name"],
                "location": group.get("location"),
            }
            for group in groups
        ]

    def scan_resources(self, target_scope: str) -> list[dict[str, Any]]:
        resources = self._run_json(
            [
                "az",
                "resource",
                "list",
                "--resource-group",
                target_scope,
                "--output",
                "json",
            ]
        )
        return [self._normalize(resource) for resource in resources]

    def _normalize(self, resource: dict[str, Any]) -> dict[str, Any]:
        sku = resource.get("sku") or {}
        return self._resource(
            resource_type=self._resource_type(resource.get("type", "")),
            name=resource.get("name", ""),
            resource_id=resource.get("id", ""),
            location=resource.get("location"),
            sku_or_size=sku.get("name") or resource.get("kind"),
            tags=resource.get("tags"),
        )

    @staticmethod
    def _resource_type(native_type: str) -> str:
        native_type = native_type.lower()
        if "virtualmachines" in native_type:
            return "virtual_machine"
        if "storageaccounts" in native_type:
            return "object_storage"
        if "database" in native_type or "servers" in native_type:
            return "database"
        return native_type or "unknown"
