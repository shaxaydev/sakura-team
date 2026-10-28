#!/usr/bin/env bash
set -euo pipefail
root=/opt/sakura-team
if [[ ! ${SSH_ORIGINAL_COMMAND:-} =~ ^deploy\ ([0-9a-f]{40})$ ]]; then
    echo 'Only deploy <40-character commit SHA> is allowed.' >&2
    exit 64
fi
sha=${BASH_REMATCH[1]}
for attempt in $(seq 1 180); do
    [[ ! -f $root/bootstrap.in-progress ]] && break
    if [[ $attempt == 180 ]]; then echo 'Initial setup is still running.' >&2; exit 75; fi
    sleep 5
done
read -r registry_token
export DOCKER_CONFIG="$root/.docker"
mkdir -p "$DOCKER_CONFIG"
chmod 700 "$DOCKER_CONFIG"
printf '%s' "$registry_token" | docker login ghcr.io -u shaxaydev --password-stdin > /dev/null
unset registry_token
exec "$root/bin/deploy.sh" "$sha"
