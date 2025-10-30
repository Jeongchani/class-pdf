#!/usr/bin/env bash
set -euo pipefail

APP_DIR="/srv/class-pdf/app"          # git clone한 위치
SITE_DIR="/srv/class-pdf/site"
NGINX_CONF="/etc/nginx/conf.d/class-pdf.conf"

echo "[0/4] 준비: rsync 확인"
if ! command -v rsync >/dev/null 2>&1; then
  sudo apt update && sudo apt install -y rsync
fi

echo "[1/4] 사이트 파일 동기화"
sudo rsync -a --delete "$APP_DIR/site/" "$SITE_DIR/"

echo "[2/4] 인덱스 스크립트 갱신"
sudo install -m 755 "$APP_DIR/scripts/build_index.py" /srv/class-pdf/build_index.py

echo "[3/4] Flask 코드 갱신 (admin)"
sudo install -m 644 "$APP_DIR/admin/admin.py" /srv/class-pdf/admin/admin.py
sudo systemctl restart class-pdf-admin || true

echo "[4/4] Nginx 설정(템플릿) 적용"
sudo install -m 644 "$APP_DIR/nginx/class-pdf.conf" "$NGINX_CONF"
sudo nginx -t && sudo systemctl reload nginx

echo "DONE"