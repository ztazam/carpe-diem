#!/usr/bin/env bash
set -o errexit

# Instalar dependencias
pip install -r requirements.txt

# Colectar archivos estáticos
python manage.py collectstatic --noinput

# Aplicar TODAS las migraciones (incluyendo las apps de Django)
python manage.py migrate

# Migración ESPECÍFICA para tu app core (por si acaso)
python manage.py migrate core

# Crear superusuario por defecto (opcional)
# echo "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.create_superuser('admin', 'admin@example.com', 'password') if not User.objects.filter(username='admin').exists() else None" | python manage.py shell#!/usr/bin/env bash
set -o errexit

# Instalar dependencias
pip install -r requirements.txt

# Colectar archivos estáticos
python manage.py collectstatic --noinput

# Aplicar migraciones de la base de datos
python manage.py migrate
