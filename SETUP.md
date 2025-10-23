# Followupper Setup Instructions

## Prerequisites

- Python 3.13 or higher
- `uv` package manager (recommended) or `pip`

## Installation

### Using uv (Recommended)

1. Install dependencies:
```bash
uv sync
```

2. Run the application:
```bash
uv run python main.py
```

### Using pip

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the application:
```bash
python main.py
```

## Database Setup

The application will automatically:
- Create the SQLite database file (`followupper.db`)
- Run database migrations using Alembic
- Set up all necessary tables

## First Run

1. The application will start with a GUI interface
2. Navigate through the tabs:
   - **Contacts**: Manage your client contacts
   - **Schedule**: View scheduled follow-ups
   - **Templates**: Create message templates
   - **Settings**: Configure platform credentials

## Development

### Running Migrations

To create a new migration:
```bash
alembic revision --autogenerate -m "Description of changes"
```

To apply migrations:
```bash
alembic upgrade head
```

### Project Structure

```
followupper/
├── src/
│   ├── models/          # Database models
│   ├── gui/             # GUI components
│   └── app.py           # Main application
├── migrations/          # Database migrations
├── main.py              # Entry point
├── pyproject.toml       # Project configuration
└── requirements.txt     # Dependencies
```

## Next Steps

1. Configure your Gmail credentials in Settings
2. Add your first contact
3. Create message templates
4. Set up automated follow-up schedules

## Troubleshooting

- If the database doesn't exist, the app will create it automatically
- Check the console for any error messages
- Ensure all dependencies are installed correctly
