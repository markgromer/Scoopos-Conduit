#!/usr/bin/env bash
# Render build script - installs Python deps + builds the React frontend
# then copies the built static files so FastAPI can serve them.
set -o errexit

echo "==> Installing Python dependencies..."
pip install -r requirements.txt

echo "==> Installing Node.js + building frontend..."
# Render provides Node via nix, but we install deps ourselves
cd frontend
npm install
npm run build
cd ..

echo "==> Copying frontend build to backend static dir..."
rm -rf backend/static
cp -r frontend/dist backend/static

echo "==> Running database migrations..."
python -m alembic upgrade head || echo "Alembic migration skipped (run manually if first deploy)"

echo "==> Build complete."
