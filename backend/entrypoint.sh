#!/bin/sh
set -e

mkdir -p /data/media /data/staticfiles

python manage.py migrate --noinput
python manage.py collectstatic --noinput

exec "$@"
