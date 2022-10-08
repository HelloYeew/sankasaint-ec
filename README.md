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

## Run tests

```bash
python manage.py test
```
