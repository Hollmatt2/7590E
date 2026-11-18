#!/usr/bin/env bash
# Copy the code to the Lightsail box and rebuild the website there. Run from the laptop:
#   bash deploy/lightsail/deploy.sh
set -euo pipefail
cd "$(dirname "$0")/../.."
BOX=ubuntu@100.59.211.221
KEY=~/.ssh/lightsail-bgcraft.pem
rsync -az --delete -e "ssh -i $KEY" \
  --exclude .git --exclude .venv --exclude __pycache__ --exclude data/ --exclude media/ \
  --exclude staticfiles/ --exclude db.sqlite3 --exclude .env \
  ./ "$BOX:/opt/calder/app/"
ssh -i "$KEY" "$BOX" 'cd /opt/calder/app/deploy/lightsail && docker compose --env-file /opt/calder/.env up -d --build && docker image prune -f >/dev/null'
echo "Deployed: https://calder.100-59-211-221.nip.io"
