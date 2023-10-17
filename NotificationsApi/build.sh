#!/usr/bin/env bash
# exit on error
set -o errexit
python -m pip install --upgrade pip
pip install -r ../requirements.txt
mkdir staticfiles
python manage.py collectstatic --no-input
python manage.py migrate

python manage.py crontab add
