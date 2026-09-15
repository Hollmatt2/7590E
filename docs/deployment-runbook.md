# Deployment runbook (Railway)

The site runs as one Railway service, with a Postgres database and a volume for uploaded files.
`start.sh` starts it: it applies database changes, gathers static files, loads the demo data, and then
runs the website (gunicorn) and the reading step (`process_agreements --watch`) side by side. Both need
the uploaded files, and a Railway volume attaches to only one service, so they share one service.

## First deployment

1. Push the repository to the project GitHub account.
2. In Railway (project account): New Project, then Deploy from GitHub repo, and choose the repository.
3. Add the database: New, then Database, then PostgreSQL. In the web service's Variables, add
   `DATABASE_URL` as a reference to the Postgres service's `DATABASE_URL`.
4. Add a volume to the web service, mounted at `/data`.
5. Set the web service's variables:
   - `DJANGO_SECRET_KEY`: a long random string, for example from
     `python -c "import secrets; print(secrets.token_urlsafe(50))"`
   - `DJANGO_DEBUG` = `0`
   - `MEDIA_ROOT` = `/data/media`
   - `DEMO_PASSWORD`: the password for the four demo logins
   - `ANTHROPIC_API_KEY`: the Anthropic key for the AI step. Without it, the site still works and the
     provisions the AI looks for wait for a person.
6. In the service's Settings, under Networking, generate a public domain. Railway passes the address to
   the app as `RAILWAY_PUBLIC_DOMAIN`, which the app adds to its allowed hosts. If it does not, set
   `DJANGO_ALLOWED_HOSTS` to the address.
7. Deploy. The start command comes from `Procfile` (`bash start.sh`).

## Check after every deployment

- The home page loads over https at the public address.
- Each demo role can log in.
- The work queue shows the sample agreements, and within a minute of starting they move from
  "Not read yet" to "Waiting for identification".
- A small PDF submitted as `requester` is read within about 10 seconds.
- `/admin/` works for `admin` and is styled (static files are served).

## Updating

Push to the main branch, and Railway redeploys. `start.sh` applies database changes (migrations).

## Problems

| What you see | Likely cause |
|---|---|
| "Set DJANGO_SECRET_KEY before running with DEBUG off" | The variable is missing. |
| 400 Bad Request | The address is not an allowed host. Set `DJANGO_ALLOWED_HOSTS`. |
| 403 when submitting a form | The https address is not trusted for forms; it comes from the allowed hosts. |
| Agreements stay "Not read yet" | The reading step stopped. The service restarts when either process stops; read the logs. |
| Build fails on Python 3.14 | Change `.python-version` to `3.13`. |

Logs are in the service's Deployments tab.

## Rolling back

In the Deployments tab, pick an earlier deployment and choose Redeploy. Database changes are not undone.

## Secrets

Keys live only in Railway variables, never in the repository (brief, section 9). If one is ever committed,
rotate it immediately and record the incident in `docs/risk-log.md`.
