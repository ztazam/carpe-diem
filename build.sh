#!/usr/bin/env bash
set -o errexit

pip install -r requirements.txt
python manage.py collectstatic --noinput

# SOLO ejecutar migrate sin especificar app
python manage.py migrate
