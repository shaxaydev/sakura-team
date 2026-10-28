#!/usr/bin/env bash
set -euo pipefail
umask 077
root=/opt/sakura-team
stamp=$(date -u +%Y%m%dT%H%M%SZ)
dest="$root/backups/$stamp"
mkdir -p "$dest"
docker compose --project-name sakura-team --env-file "$root/.env" --env-file "$root/images.env" -f "$root/current/team/deploy/compose.json" exec -T sakura-db pg_dump -U plane plane | gzip > "$dest/database.sql.gz"
gzip -t "$dest/database.sql.gz"
docker run --rm -v sakura-team_uploads:/source:ro -v "$dest:/backup" alpine:3.22 tar -czf /backup/uploads.tar.gz -C /source .
tar -tzf "$dest/uploads.tar.gz" > /dev/null
echo "Sakura backup created: $dest"
