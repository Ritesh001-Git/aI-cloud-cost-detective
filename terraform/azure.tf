terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.0"
    }
  }
}

provider "azurerm" {
  features {}
}

# --- Base Infrastructure ---
resource "azurerm_resource_group" "rg" {
  name     = "rg-finops-detector-test"
  location = "East US"
}

resource "azurerm_virtual_network" "vnet" {
  name                = "vnet-test-core"
  address_space       = ["10.0.0.0/16"]
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name
}


# =========================================================================
# 🔥 DELIBERATE COST LEAKS (Your tool should flag these)
# =========================================================================

# Leak 1: Detached Managed Disk (Orphaned persistent disk)
resource "azurerm_managed_disk" "orphaned_disk" {
  name                 = "disk-stale-data-store"
  location             = azurerm_resource_group.rg.location
  resource_group_name  = azurerm_resource_group.rg.name
  storage_account_type = "Standard_LRS"
  create_option        = "Empty"
  disk_size_gb         = 32
}

# Leak 2: Unassociated Public IP (Idle reserved address billing hourly)
resource "azurerm_public_ip" "unused_ip" {
  name                = "pip-abandoned-service"
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name
  allocation_method   = "Static"
  sku                 = "Standard"
}

# Leak 3: Over-provisioned Storage Account (Premium SKU selected for testing workloads)
resource "azurerm_storage_account" "overprovisioned_storage" {
  name                     = "stfinopspremiumleak001" # Must be globally unique
  resource_group_name      = azurerm_resource_group.rg.name
  location                 = azurerm_resource_group.rg.location
  account_tier             = "Premium" # Right-sizing opportunity: downgrade to "Standard"
  account_kind             = "BlockBlobStorage"
  account_replication_type = "ZRS"
}