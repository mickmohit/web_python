# Basic Flask Application

A simple Flask web application with a basic API endpoint.

## Setup

1. Create a virtual environment (recommended):
   ```
   python -m venv venv
   .\venv\Scripts\activate  # On Windows
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

## Running the Application

```
python main.py
```

The application will be available at http://localhost:5000

## Endpoints

- `GET /`: Home page with a welcome message
- `GET /api/health`: Health check endpoint that returns JSON
