Weather App
============


Requirements
-------------

1. Python 3.7
2. Postgres 9.4 >



Installation
------------

1. Create Postgres database `e_commerce_db` with user `postgres` and password `password`

2. Create a virtual environment
    `pip install virtualenv`
    `virtualenv -p python3 venv`
2. Install all python dependencies `pip install -r requirements`
3. Run database migrations: `python manage.py migrate`
4. Start web server: `python manage.py runserver`