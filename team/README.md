# Sakura team workspace

Personal fork of Plane Community v1.4.2, commit `5f7d92784c403f76284f0f16718f320221dc7fec`.

- Production: https://team.borili.uz
- Workspace: Sushi bar Sakura; time zone: Asia/Tashkent.
- Source: https://github.com/shaxaydev/sakura-team
- Upstream licensing and copyright notices are retained. `apps/api/plane/utils/email.py` has a commercial header in this upstream release; this inconsistency is recorded for clarification before custom distribution.

## Update flow

1. Branch from `main`, make a change, open a pull request.
2. CI validates deployment files and builds all five application images.
3. Merge to `main`: images are pushed to GHCR with immutable commit-SHA tags.
4. The production job uses a dedicated restricted SSH key, backs up the tracker database, applies migrations and updates only the `sakura-team` Compose project.
5. Health checks cover Sakura plus the existing Borili and ERP endpoints. On failure, the previous runtime release is restored when available. Database schema rollback is manual using the retained dump.

GitHub Environment `production`: `VPS_SSH_KEY`, `VPS_KNOWN_HOSTS`. GHCR uses the job's short-lived `GITHUB_TOKEN`. Production environment values stay in `/opt/sakura-team/.env` (mode 600), never in GitHub or source control.

## Server layout

- `/opt/sakura-team/releases/<commit>/team/deploy/`: deployment configuration for each release.
- `/opt/sakura-team/current`: last healthy release.
- `/opt/sakura-team/images.env`: image namespace and commit tag.
- `/opt/sakura-team/bin/`: deployment entry point; CI key only accepts `deploy <SHA>`.
- `/opt/sakura-team/backups/`: database backups before deployment.
- Shared Caddy handles TLS and routing. No host ports are published by this Compose project.
- Service names all start with `sakura-` to avoid collisions with ERP service DNS names on the shared Docker network.
- Password login, closed registration, no SMTP configuration. Initial admin credentials are stored outside Git.

The upstream workflows are preserved in `.github/upstream-workflows/`; `.github/workflows/sakura.yml` is the active team pipeline.

## Backups and rollback

Create a database and upload snapshot:

```sh
bash /opt/sakura-team/current/team/deploy/backup.sh
```

The script checks gzip/tar integrity. A full restore rehearsal is a separate operation. Copy backups off the VPS regularly. Never run `down -v` or a global Docker prune on this shared server.

Runtime rollback: restore `images.previous.env` as `images.env` and start the previous release's Compose file under project name `sakura-team`. A migration can change the schema; runtime rollback does not undo migrations. Database restore requires stopping only Sakura writers, selecting the matching dump, and then starting the matching release. Preserve current data before restoring.
