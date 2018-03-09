#!/bin/sh
cd /portal
#cp msmtprc /etc
sleep 1 # Hopefully enough for the database to start accepting connections
python manage.py makemigrations
python manage.py migrate
python manage.py runserver 0.0.0.0:8000
