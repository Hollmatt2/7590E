# Hosting on the Lightsail box

Since 2026-11-03 the site runs on Matt's Lightsail server at https://calder.100-59-211-221.nip.io
(Railway's project was gone on 10/25).

- `Dockerfile` builds the website: Python 3.14, the packages in requirements.txt, then `start.sh`
  (migrate, collectstatic, seed_demo, the reading step and gunicorn) as an ordinary user.
- `docker-compose.yml` runs it next to its own Postgres database. Uploaded PDFs are kept in the
  `media` volume, the database in the `pgdata` volume.
- HTTPS: the Caddy server already on the box (from the Miniflux setup) has a
  `calder.100-59-211-221.nip.io` block that forwards to `calder-web:8000`. Caddy gets the
  certificate itself. nip.io turns the name into the box's IP address.
- Secrets (DJANGO_SECRET_KEY, DEMO_PASSWORD, ANTHROPIC_API_KEY, DB_PASSWORD, DJANGO_DEBUG=0,
  DJANGO_ALLOWED_HOSTS) are in `/opt/calder/.env` on the box, readable only by the ubuntu user.
- Deploy a change: `bash deploy/lightsail/deploy.sh` from the laptop. Pushing to GitHub does not
  deploy.
- Logs: `ssh -i ~/.ssh/lightsail-bgcraft.pem ubuntu@100.59.211.221 docker logs --tail 50 calder-web-1`
