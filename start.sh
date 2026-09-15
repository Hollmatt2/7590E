#!/usr/bin/env bash
# How the deployed site starts. Railway runs this (see Procfile and docs/deployment-runbook.md).
set -e
export PYTHONUNBUFFERED=1  # print log lines immediately, so Railway's logs show progress as it happens

python manage.py migrate --noinput        # apply any database changes
python manage.py collectstatic --noinput  # gather the admin screens' CSS and JavaScript
python manage.py seed_demo                # demo logins, the playbook, sample agreements (safe to repeat)

# The reading step and the website run side by side in this one service, so both can reach the
# uploaded files on the service's volume.
python manage.py process_agreements --watch &
gunicorn config.wsgi --bind "0.0.0.0:${PORT:-8000}" &

# If either one stops, stop the whole service so Railway restarts it.
wait -n
exit $?
