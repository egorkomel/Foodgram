#!/bin/bash

python3 manage.py makemigrations api
python3 manage.py makemigrations users
python3 manage.py migrate
python3 manage.py collectstatic --no-input
python3 manage.py import_ingredients --write_json
python3 manage.py import_ingredients --read
