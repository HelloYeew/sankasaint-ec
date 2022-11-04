# Sankasaint Election Committee
 EC app for election in Software project subject to select James Brucker as a next president powered by [ayaka framework](https://github.com/HelloYeew/ayaka).

## Setup

```bash
pip install virtualenv
virtualenv venv
source venv/bin/activate # Windows : venv\Scripts\activate
pip install -r requirements.txt
```

Copy `.env.example` to `.env` and continue on database migration

```bash
python manage.py migrate
python manage.py loaddata seed/apps.json
python manage.py createsuperuser
# Follow the instruction
```

Now to run the server

```bash
python manage.py runserver
```

## Dump database data

```bash
python manage.py dumpdata apps > seed/apps.json --indent 4
```

## Load database data

```bash
python manage.py loaddata seed/apps.json
```

## Import legacy data to new database tables

1. Run `load database data` section
2. Get in utility page `/utils` and run `Import legacy data` button

Note : If you are not loading the data from the dump file, the migration will fail and you need to reset the database and do it again.

## Run tests

```bash
python manage.py test
```
