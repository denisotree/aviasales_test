#!/usr/bin/env bash
gunicorn --reload wsgi:app -c ./gunicorn.py -b 0.0.0.0:8000
