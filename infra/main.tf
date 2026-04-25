terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    tls = {
      source  = "hashicorp/tls"
      version = "~> 4.0"
    }
    local = {
      source  = "hashicorp/local"
      version = "~> 2.0"
    }
  }
}

provider "aws" {
  region     = var.aws_region
  access_key = var.aws_access_key_id
  secret_key = var.aws_secret_access_key
}

resource "tls_private_key" "app" {
  algorithm = "RSA"
  rsa_bits  = 4096
}

resource "aws_key_pair" "app" {
  key_name   = var.key_name
  public_key = tls_private_key.app.public_key_openssh
}

resource "local_file" "private_key" {
  content         = tls_private_key.app.private_key_pem
  filename        = "${path.module}/${var.key_name}.pem"
  file_permission = "0400"
}

data "aws_ami" "amazon_linux" {
  most_recent = true
  owners      = ["amazon"]

  filter {
    name   = "name"
    values = ["al2023-ami-*-x86_64"]
  }
}

resource "aws_security_group" "ec2" {
  name = "promptior-ec2-sg"

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_instance" "app" {
  ami                    = data.aws_ami.amazon_linux.id
  instance_type          = var.instance_type
  key_name               = aws_key_pair.app.key_name
  vpc_security_group_ids = [aws_security_group.ec2.id]

  user_data = <<-EOF
    #!/bin/bash
    set -e

    # Install Docker
    dnf update -y
    dnf install -y docker git
    systemctl enable docker
    systemctl start docker

    # Install Docker Compose
    curl -SL https://github.com/docker/compose/releases/latest/download/docker-compose-linux-x86_64 -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose

    # Clone repo
    git clone https://github.com/FranGiordano/promptior-chatbot.git /app
    cd /app

    # Set env vars
    cat > /app/.env <<ENV
CLOUDFLARE_TUNNEL_TOKEN=${var.cloudflare_tunnel_token}
OPENROUTER_API_KEY=${var.openrouter_api_key}
ENV

    # Run
    docker-compose up -d
  EOF

  tags = {
    Name = "promptior-chatbot"
  }
}

output "public_ip" {
  value = aws_instance.app.public_ip
}
