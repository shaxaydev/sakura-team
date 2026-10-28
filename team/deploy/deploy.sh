#!/usr/bin/env bash
set -euo pipefail
umask 077
root=/opt/sakura-team
sha=${1:?Commit SHA required}
[[ $sha =~ ^[0-9a-f]{40}$ ]] || exit 64
exec 9>"$root/deploy.lock"
flock -n 9 || { echo 'Another Sakura deployment is running.' >&2; exit 75; }
export DOCKER_CONFIG="$root/.docker"
mkdir -p "$root/releases/$sha" "$root/backups"
release="$root/releases/$sha"
if [[ ! -d $root/source.git ]]; then
    git clone --bare https://github.com/shaxaydev/sakura-team.git "$root/source.git"
fi
git --git-dir="$root/source.git" fetch --depth 1 origin "$sha"
git --git-dir="$root/source.git" archive "$sha" team/deploy | tar -x -C "$release"
compose=(docker compose --project-name sakura-team --env-file "$root/.env" --env-file "$root/images.env" -f "$release/team/deploy/compose.json")
previous=$(readlink -f "$root/current" 2>/dev/null || true)
previous_images="$root/images.previous.env"
if [[ -f $root/images.env ]]; then cp "$root/images.env" "$previous_images"; fi
if [[ -n $previous && -f $previous/team/deploy/compose.json ]]; then
    old=(docker compose --project-name sakura-team --env-file "$root/.env" --env-file "$root/images.env" -f "$previous/team/deploy/compose.json")
    if [[ -n $("${old[@]}" ps -q sakura-db) ]]; then
        "${old[@]}" exec -T sakura-db pg_dump -U plane plane | gzip > "$root/backups/before-$sha.sql.gz"
        gzip -t "$root/backups/before-$sha.sql.gz"
    fi
fi
rollback() {
    status=$?
    trap - ERR
    if [[ -n $previous && -f $previous_images ]]; then
        cp "$previous_images" "$root/images.env"
        docker compose --project-name sakura-team --env-file "$root/.env" --env-file "$root/images.env" -f "$previous/team/deploy/compose.json" up -d sakura-web sakura-admin sakura-space sakura-live sakura-api sakura-worker sakura-beat || true
        echo 'Previous runtime images restored. Database backup retained; schema was not automatically rolled back.' >&2
    fi
    exit "$status"
}
trap rollback ERR
printf 'IMAGE_PREFIX=ghcr.io/shaxaydev/sakura-team\nAPP_TAG=%s\n' "$sha" > "$root/images.env"
"${compose[@]}" config --quiet
"${compose[@]}" pull
"${compose[@]}" up -d sakura-db sakura-redis sakura-mq sakura-storage
"${compose[@]}" run --rm -T sakura-migrator
"${compose[@]}" up -d sakura-web sakura-admin sakura-space sakura-live sakura-api sakura-worker sakura-beat
for attempt in $(seq 1 60); do
    if docker exec rs-erp-proxy-1 wget -q -O /dev/null http://sakura-api:8000/api/instances/ && docker exec rs-erp-proxy-1 wget -q -O /dev/null http://sakura-web:3000/; then break; fi
    if [[ $attempt == 60 ]]; then echo 'Sakura did not become healthy.' >&2; false; fi
    sleep 5
done
curl -fsS https://borili.uz/api/health > /dev/null
curl -fsS https://app.gorillax.uz/api/health > /dev/null
ln -sfn "$release" "$root/current"
echo "Sakura deployed: $sha"
