import subprocess
import unittest
from unittest.mock import patch

from providers.aws_scanner import AWSScanner
from providers.azure_scanner import AzureScanner
from providers.base import ScannerError
from providers.gcp_scanner import GCPScanner


class ScannerTests(unittest.TestCase):
    @patch("providers.base.subprocess.run")
    def test_azure_resource_is_normalized(self, run):
        run.return_value.stdout = """
        [{
          "id": "/subscriptions/1/resourceGroups/demo/providers/Microsoft.Compute/virtualMachines/vm-1",
          "name": "vm-1",
          "type": "Microsoft.Compute/virtualMachines",
          "location": "westus",
          "sku": {"name": "Standard_D2s_v3"},
          "tags": {"team": "platform"}
        }]
        """

        resources = AzureScanner().scan_resources("demo")

        self.assertEqual(resources[0]["type"], "virtual_machine")
        self.assertEqual(resources[0]["sku_or_size"], "Standard_D2s_v3")
        self.assertEqual(resources[0]["tags"], {"team": "platform"})

    @patch("providers.base.subprocess.run")
    def test_aws_resource_is_normalized(self, run):
        run.return_value.stdout = """
        {"ResourceTagMappingList": [{
          "ResourceARN": "arn:aws:rds:us-east-1:123456789012:db:orders",
          "Tags": [{"Key": "env", "Value": "prod"}]
        }]}
        """

        resources = AWSScanner().scan_resources("us-east-1")

        self.assertEqual(resources[0]["type"], "database")
        self.assertEqual(resources[0]["name"], "orders")
        self.assertEqual(resources[0]["location"], "us-east-1")

    @patch("providers.base.subprocess.run")
    def test_gcp_resource_is_normalized(self, run):
        run.return_value.stdout = """
        [{
          "assetType": "compute.googleapis.com/Instance",
          "displayName": "worker-1",
          "name": "//compute.googleapis.com/projects/demo/zones/us-central1-a/instances/worker-1",
          "location": "us-central1-a",
          "additionalAttributes": {"machineType": "e2-medium"},
          "labels": {"team": "platform"}
        }]
        """

        resources = GCPScanner().scan_resources("demo")

        self.assertEqual(resources[0]["type"], "virtual_machine")
        self.assertEqual(resources[0]["sku_or_size"], "e2-medium")

    @patch("providers.base.subprocess.run", side_effect=FileNotFoundError)
    def test_missing_cli_has_readable_error(self, run):
        with self.assertRaisesRegex(ScannerError, "not installed"):
            AWSScanner().list_scopes()

    @patch("providers.base.subprocess.run")
    def test_cli_failure_is_a_bad_request(self, run):
        run.side_effect = subprocess.CalledProcessError(
            returncode=1,
            cmd=["az"],
            stderr="Please run 'az login'",
        )

        with self.assertRaises(ScannerError) as context:
            AzureScanner().list_scopes()

        self.assertEqual(context.exception.status_code, 400)
        self.assertIn("az login", context.exception.message)


if __name__ == "__main__":
    unittest.main()
