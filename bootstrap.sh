#!/bin/sh
export FLASK_APP=./api/index.py
export FLASK_ENV=development
flask run --host=0.0.0.0

