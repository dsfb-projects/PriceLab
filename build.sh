#!/usr/bin/env bash
# Build do Render — instala dependências, coleta estáticos e roda migrations
set -o errexit

pip install -r requirements.txt

cd backend
python manage.py collectstatic --noinput
python manage.py migrate
