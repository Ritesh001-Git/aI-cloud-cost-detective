from typing import Any

from .base import BaseScanner


class GCPScanner(BaseScanner):
    provider = "gcp"
    cli_name = "Google Cloud"

    def list_scopes(self) -> list[dict[str, Any]]:
        projects = self._run_json(
            [
                "gcloud",
                "projects",
                "list",
                "--filter=lifecycleState:ACTIVE",
                "--format=json",
            ]
        )
        return [
            {
                "id": project["projectId"],
                "name": project.get("name", project["projectId"]),
                "project_number": project.get("projectNumber"),
            }
            for project in projects
        ]

    def scan_resources(self, target_scope: str) -> list[dict[str, Any]]:
        resources = self._run_json(
            [
                "gcloud",
                "asset",
                "search-all-resources",
                f"--scope=projects/{target_scope}",
                "--format=json",
            ]
        )
        return [self._normalize(resource) for resource in resources]

    def _normalize(self, resource: dict[str, Any]) -> dict[str, Any]:
        attributes = resource.get("additionalAttributes") or {}
        return self._resource(
            resource_type=self._resource_type(resource.get("assetType", "")),
            name=resource.get("displayName") or resource.get("name", ""),
            resource_id=resource.get("name", ""),
            location=resource.get("location"),
            sku_or_size=(
                attributes.get("machineType")
                or attributes.get("tier")
                or attributes.get("storageClass")
            ),
            tags=resource.get("labels") or attributes.get("labels"),
        )

    @staticmethod
    def _resource_type(asset_type: str) -> str:
        asset_type = asset_type.lower()
        if "instance" in asset_type:
            return "virtual_machine"
        if "bucket" in asset_type:
            return "object_storage"
        if "database" in asset_type or "sql" in asset_type:
            return "database"
        return asset_type or "unknown"
