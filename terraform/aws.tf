terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = "us-east-1"
}

# --- Base Infrastructure ---
resource "aws_vpc" "main" {
  cidr_block = "10.0.0.0/16"
  tags       = { Name = "finops-test-vpc" }
}

resource "aws_subnet" "public" {
  vpc_id            = aws_vpc.main.id
  cidr_block        = "10.0.1.0/24"
  availability_zone = "us-east-1a"
}

resource "aws_internet_gateway" "gw" {
  vpc_id = aws_vpc.main.id
}

# Necessary Compute
resource "aws_instance" "active_node" {
  ami           = "ami-0c7217cdde317cfec" # Ubuntu 22.04 LTS (Update AMI ID for your region if needed)
  instance_type = "t3.micro"
  subnet_id     = aws_subnet.public.id
  tags          = { Name = "active-prod-node" }
}


# =========================================================================
# 🔥 DELIBERATE COST LEAKS (Your tool should flag these)
# =========================================================================

# Leak 1: Orphaned EBS Volume (Created but never attached to an EC2 instance)
resource "aws_ebs_volume" "orphaned_volume" {
  availability_zone = "us-east-1a"
  size              = 20
  type              = "gp3"
  tags              = { Name = "abandoned-backup-vol" }
}

# Leak 2: Unassociated Elastic IP (Allocated to the account but empty)
resource "aws_eip" "unused_eip" {
  domain = "vpc"
  tags   = { Name = "stale-marketing-ip" }
}

# Leak 3: Idle NAT Gateway (Charges an hourly baseline without processing traffic)
resource "aws_eip" "nat_eip" {
  domain = "vpc"
}

resource "aws_nat_gateway" "idle_nat" {
  allocation_id = aws_eip.nat_eip.id
  subnet_id     = aws_subnet.public.id
  tags          = { Name = "forgotten-private-nat" }
  
  depends_on = [aws_internet_gateway.gw]
}