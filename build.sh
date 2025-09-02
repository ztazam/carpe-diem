#!/usr/bin/env bash
set -o errexit

# Instalar dependencias
pip install -r requirements.txt

# Colectar archivos estáticos
python manage.py collectstatic --noinput

# Aplicar migraciones de la base de datos
python manage.py migrate
