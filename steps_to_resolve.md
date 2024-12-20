To resolve the "no such table: pharmacy_app_shop" error, follow these steps:

1. Create the migrations directory:
```bash
mkdir pharmacy_app/migrations
touch pharmacy_app/migrations/__init__.py
```

2. Create initial migrations:
```bash
python manage.py makemigrations pharmacy_app
```

3. Apply the migrations:
```bash
python manage.py migrate
```

This will create all necessary database tables for your models including the Shop model.