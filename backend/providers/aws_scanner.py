from typing import Any

from .base import BaseScanner


class AWSScanner(BaseScanner):
    provider = "aws"
    cli_name = "AWS"

    def list_scopes(self) -> list[dict[str, Any]]:
        payload = self._run_json(
            ["aws", "ec2", "describe-regions", "--output", "json"]
        )
        return [
            {
                "id": region["RegionName"],
                "name": region["RegionName"],
                "endpoint": region.get("Endpoint"),
            }
            for region in payload.get("Regions", [])
        ]

    def scan_resources(self, target_scope: str) -> list[dict[str, Any]]:
        payload = self._run_json(
            [
                "aws",
                "resourcegroupstaggingapi",
                "get-resources",
                "--region",
                target_scope,
                "--output",
                "json",
            ]
        )
        return [
            self._normalize(resource, target_scope)
            for resource in payload.get("ResourceTagMappingList", [])
        ]

    def _normalize(
        self, resource: dict[str, Any], region: str
    ) -> dict[str, Any]:
        arn = resource.get("ResourceARN", "")
        return self._resource(
            resource_type=self._resource_type(arn),
            name=self._resource_name(arn),
            resource_id=arn,
            location=region,
            tags={
                tag["Key"]: tag.get("Value", "")
                for tag in resource.get("Tags", [])
                if "Key" in tag
            },
        )

    @staticmethod
    def _resource_name(arn: str) -> str:
        return arn.rsplit("/", 1)[-1].rsplit(":", 1)[-1]

    @staticmethod
    def _resource_type(arn: str) -> str:
        parts = arn.split(":")
        service = parts[2] if len(parts) > 2 else ""
        if service == "ec2":
            return "virtual_machine"
        if service == "s3":
            return "object_storage"
        if service in {"rds", "dynamodb"}:
            return "database"
        return service or "unknown"
