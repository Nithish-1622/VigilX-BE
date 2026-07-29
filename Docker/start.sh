#!/bin/bash
# =============================================================================
# VigilX Enterprise Backend Startup Script
# Deployed via Zoho Catalyst AppSail (Docker source)
# =============================================================================

# Exit on error, but we handle individual failures manually below
set -e

echo "==========================================="
echo "  Starting VigilX Enterprise Backend"
echo "==========================================="

# Zoho Catalyst injects X_ZOHO_CATALYST_LISTEN_PORT at runtime.
# Default to 9000 for local Docker testing.
export X_ZOHO_CATALYST_LISTEN_PORT=${X_ZOHO_CATALYST_LISTEN_PORT:-9000}
echo "[INFO] Catalyst Listen Port: $X_ZOHO_CATALYST_LISTEN_PORT"

# --- Guard: Crash early if critical env vars are missing ---
if [ -z "$DATABASE_URL" ]; then
  echo "[WARNING] DATABASE_URL is not set. Migrations will be skipped."
fi

# =============================================================================
# 1. Django REST API Setup (Gunicorn on port 8000)
# =============================================================================
cd /app/backend/django-api

if [ -n "$DATABASE_URL" ]; then
  echo "[INFO] Running Django database migrations..."
  python manage.py migrate --noinput || echo "[WARNING] Migrations failed. Check DATABASE_URL."
  
  echo "[INFO] Collecting Django static files..."
  python manage.py collectstatic --noinput || echo "[WARNING] Collectstatic failed."
else
  echo "[SKIP] Skipping migrations and collectstatic (no DATABASE_URL configured)."
fi

echo "[INFO] Starting Django REST API (Gunicorn) on 127.0.0.1:8000..."
gunicorn config.wsgi:application \
  --bind 127.0.0.1:8000 \
  --workers 2 \
  --timeout 120 \
  --daemon \
  --log-file /tmp/gunicorn.log \
  --access-logfile /tmp/gunicorn-access.log

echo "[OK] Gunicorn started."

# =============================================================================
# 2. FastAPI AI Engine Setup (Uvicorn on port 8001)
# =============================================================================
cd /app/backend/ai-engine

echo "[INFO] Starting FastAPI AI Engine (Uvicorn) on 127.0.0.1:8001..."
uvicorn main:app \
  --host 127.0.0.1 \
  --port 8001 \
  --workers 1 \
  --log-level info \
  --access-log &

UVICORN_PID=$!
echo "[OK] Uvicorn started (PID: $UVICORN_PID)."

# Give Uvicorn a moment to initialize before nginx starts forwarding
sleep 3

# =============================================================================
# 3. Nginx Reverse Proxy
# =============================================================================
echo "[INFO] Configuring Nginx Reverse Proxy..."
envsubst '${X_ZOHO_CATALYST_LISTEN_PORT}' < /etc/nginx/nginx.conf.template > /etc/nginx/nginx.conf

echo "[INFO] Testing Nginx config..."
nginx -t && echo "[OK] Nginx config is valid."

echo "[INFO] Starting Nginx on port $X_ZOHO_CATALYST_LISTEN_PORT..."
# Nginx in the foreground keeps the container alive
exec nginx -g "daemon off;"
