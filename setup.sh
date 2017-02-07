#!/bin/sh

set -e

python3 -m venv venv
. venv/bin/activate
pip install -r requirements.txt
python3 manage.py migrate
