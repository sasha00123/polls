# Polls app

### Run app

Running with docker-compose

```
cp .env.example .env # edit with your configuration
docker-compose up
```

### Documentation

Generated `openapi-schema.yml`

### Development

```
virtualenv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env # edit with your configuration
python manage.py migrate
python manage.py runserver
```

### BDD Tests

```
python manage.py behave
```