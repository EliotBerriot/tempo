#!/bin/sh
python manage.py migrate
python manage.py runserver_plus 0.0.0.0:8000
#./tempo/static/node_modules/gulp/bin/gulp.js watch
