# DSA Software Development Capstone Project

## Tech Stack Used

backend - Python/Django
frontend - React + Tailwindcss
database - sqlite3

## To get started

To run the server on your local machine, assuming you have python and pip installed, after you clone this repo, run:

```bash
pip install -r requirements.txt
python manage.py runserver
```

## Directory Structure

If you are new to python and Django:

backend/ - Server settings, application and configuration
backend/urls.py - Main URL config

core/ - Main server code
core/urls.py - Application URL config
core/views.py - Backend views for data processing, API endpoints
core/models.py - Database config
core/serializers.py - JSON serializers or parsers for APIs
core/tests.py - Test coverage

static/ - CSS, JavaScript and Images
static/dist/assets - Built react files
static/logo.jpg - Application logo

templates/ - HTML files properly linked to the built react files