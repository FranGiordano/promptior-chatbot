#!/bin/bash
set -e

# Install Docker
dnf update -y
dnf install -y docker git
systemctl enable docker
systemctl start docker

# Install Docker CLI plugins (buildx + compose)
mkdir -p /usr/local/lib/docker/cli-plugins
curl -SL https://github.com/docker/buildx/releases/latest/download/buildx-linux-amd64 -o /usr/local/lib/docker/cli-plugins/docker-buildx
curl -SL https://github.com/docker/compose/releases/latest/download/docker-compose-linux-x86_64 -o /usr/local/lib/docker/cli-plugins/docker-compose
chmod +x /usr/local/lib/docker/cli-plugins/docker-buildx /usr/local/lib/docker/cli-plugins/docker-compose

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
