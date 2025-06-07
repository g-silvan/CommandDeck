#!/bin/bash

# Port aus der .env Datei auslesen
WEB_PORT=$(grep -E '^WEB_PORT=' .env | cut -d '=' -f2)

# Gunicorn starten
venv/bin/gunicorn --workers 10 --timeout 120 --bind 0.0.0.0:$WEB_PORT main:app
