# psychologist-robot

## INSTALLATION

### 1. Clone the repository

```git clone repo_url```

### 2. Setup the virtual environment

```python3 -m venv venv```

### 3. Activate the virtual environment

```source venv/bin/activate```

### 4. Install the requirements

```pip install -r requirements/develop.txt```

### 5. Create .env file and Copy from .env.example, then edit the .env file with your credentials
```cp .env.example .env```

### 6. Run the migrations

```python manage.py migrate```

### 7. Run the server

```python manage.py runserver```

``````