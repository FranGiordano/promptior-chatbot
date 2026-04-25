#!/bin/bash
set -e

# Install Docker
dnf update -y
dnf install -y docker git
systemctl enable docker
systemctl start docker

# Install Docker Compose plugin
dnf install -y docker-compose-plugin

# Clone repo
git clone https://github.com/FranGiordano/promptior-chatbot.git /app
cd /app

# Set env vars
cat > /app/.env <<ENV
CLOUDFLARE_TUNNEL_TOKEN=${cloudflare_tunnel_token}
OPENROUTER_API_KEY=${openrouter_api_key}
ENV

# Run
docker compose up -d
