#!/usr/bin/env bash
echo "=== VERIFICANDO CONEXIÓN ==="
echo "DATABASE_URL: $DATABASE_URL"
python manage.py shell -c "
from django.conf import settings
print('BD REAL:', settings.DATABASES['default']['NAME'])
"
echo "============================="

python manage.py migrate
python manage.py collectstatic --noinput
set -o errexit

pip install -r requirements.txt
python manage.py collectstatic --noinput

# SOLO ejecutar migrate sin especificar app
python manage.py migrate
