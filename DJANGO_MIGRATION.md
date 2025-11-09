# Django Migration Guide

The backend has been converted from Flask to Django. Follow these steps to set up:

## 1. Install Dependencies

```bash
uv sync
```

## 2. Create Django Migrations

```bash
cd backend
uv run python manage.py makemigrations
```

## 3. Migrate Database

**IMPORTANT**: The existing SQLite database will be preserved, but Django will create its own migration history.

```bash
uv run python manage.py migrate
```

## 4. Run the Server

From the project root:
```bash
python start.py
```

Or directly:
```bash
cd backend
uv run python manage.py runserver 0.0.0.0:8001
```

## API Endpoints

All endpoints remain the same:
- `GET /api/contacts` - List contacts
- `POST /api/contacts` - Create contact
- `PUT /api/contacts/<id>` - Update contact
- `DELETE /api/contacts/<id>` - Delete contact

Same for templates, campaigns, etc.

## Notes

- The database file (`followupper.db`) is shared between Flask and Django
- Django models use the same table names as Flask (via `db_table` in Meta)
- All existing data will be preserved
- The frontend doesn't need any changes - API endpoints are identical

