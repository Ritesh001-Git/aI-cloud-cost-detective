terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
}

provider "google" {
  project = "your-gcp-project-id" # Replace with your target testing project ID
  region  = "us-central1"
  zone    = "us-central1-a"
}

# --- Base Infrastructure ---
resource "google_compute_network" "vpc" {
  name                    = "finops-test-network"
  auto_create_subnetworks = true
}


# =========================================================================
# 🔥 DELIBERATE COST LEAKS (Your tool should flag these)
# =========================================================================

# Leak 1: Orphaned Compute Disk (Standalone persistent block storage)
resource "google_compute_disk" "orphaned_disk" {
  name = "disk-abandoned-db-replica"
  type = "pd-standard"
  size = 50
  zone = "us-central1-a"
}

# Leak 2: Unassigned Static External IP (Accumulates idle reservation fees)
resource "google_compute_address" "unused_static_ip" {
  name         = "ip-stale-legacy-lb"
  address_type = "EXTERNAL"
  region       = "us-central1"
}

# Leak 3: Over-provisioned Cloud SQL Database (High-Availability + Enterprise Tier for testing)
resource "google_sql_database_instance" "overprovisioned_db" {
  name             = "sql-overprovisioned-test-db"
  database_version = "POSTGRES_15"
  region           = "us-central1"
  
  deletion_protection = false # Crucial for simple automated cleanups via your workflow

  settings {
    # Right-sizing opportunity: High availability (REGIONAL) and large tiers 
    # are significant cost multipliers. For testing, it should be ZONAL and db-f1-micro.
    tier              = "db-custom-4-15360" # 4 vCPU, 15GB RAM
    availability_type = "REGIONAL"          # Dual-zone redundant configuration doubling base tier costs
  }
}