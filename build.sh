#!/usr/bin/env bash
set -o errexit

sh build_frontend.sh

# build backend
pip install -r requirements.txt

python manage.py collectstatic --no-input
python manage.py migrate
