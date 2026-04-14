Here's a **complete, practical example** of how to set up professional logging in a Django project (console + file logging).

### 1. Project Structure
```
myproject/
├── manage.py
├── myproject/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
├── myapp/
│   ├── __init__.py
│   ├── models.py
│   ├── views.py
│   ├── apps.py
│   └── ...
├── logs/
│   └── django.log          # will be created automatically
└── requirements.txt
```

### 2. `settings.py` – Logging Configuration (Recommended)

Add this at the bottom of your `settings.py`:

```python
import os
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).resolve().parent.parent

# ====================== LOGGING CONFIGURATION ======================
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,

    # Formatters
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
        'detailed': {
            'format': '{asctime} | {levelname} | {name} | {module}:{lineno} | {message}',
            'style': '{',
        },
    },

    # Handlers
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'detailed',
        },
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(BASE_DIR, 'logs/django.log'),
            'maxBytes': 10 * 1024 * 1024,      # 10 MB
            'backupCount': 5,                  # Keep 5 backup files
            'formatter': 'detailed',
            'encoding': 'utf-8',
        },
        'error_file': {
            'level': 'ERROR',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(BASE_DIR, 'logs/django_errors.log'),
            'maxBytes': 10 * 1024 * 1024,
            'backupCount': 5,
            'formatter': 'detailed',
            'encoding': 'utf-8',
        },
    },

    # Loggers
    'loggers': {
        # Root logger
        '': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
        },
        # Django core loggers
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
        'django.request': {
            'handlers': ['console', 'error_file'],
            'level': 'ERROR',
            'propagate': False,
        },
        'django.security': {
            'handlers': ['console', 'error_file'],
            'level': 'WARNING',
            'propagate': False,
        },
        # Your custom app logger
        'myapp': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}
```

### 3. Create the logs directory

Run this once:
```bash
mkdir -p logs
```

### 4. Using Logging in Your Code

#### In `myapp/views.py`:
```python
import logging
from django.http import HttpResponse
from django.views.generic import View

# Get logger for this app
logger = logging.getLogger(__name__)   # Recommended: __name__ gives 'myapp.views'

class MyView(View):
    def get(self, request):
        logger.debug("Debug message: This will only show in DEBUG mode")
        logger.info("Info: User %s accessed the homepage", request.user.username)
        logger.warning("Warning: Something suspicious happened")
        
        try:
            # Simulate an error
            1 / 0
        except Exception as e:
            logger.error("Error occurred in MyView.get()", exc_info=True)
            logger.exception("This also logs the full traceback")  # Same as above but cleaner

        return HttpResponse("Hello, logging world!")
```

#### In `myapp/models.py`:
```python
import logging
from django.db import models

logger = logging.getLogger(__name__)

class MyModel(models.Model):
    name = models.CharField(max_length=100)

    def save(self, *args, **kwargs):
        logger.info("Saving MyModel instance: %s", self.name)
        super().save(*args, **kwargs)
        
        if self.name == "bad":
            logger.error("Invalid name detected: %s", self.name)
```

### 5. Bonus: Different Log Levels in Development vs Production

You can make it environment-aware:

```python
# In settings.py
LOG_LEVEL = 'DEBUG' if DEBUG else 'INFO'

LOGGING = {
    ...
    'loggers': {
        '': {
            'handlers': ['console', 'file'],
            'level': LOG_LEVEL,
        },
        ...
    }
}
```

### 6. Common Logger Names You Might Want

```python
logger = logging.getLogger('django.db.backends')        # SQL queries
logger = logging.getLogger('django.security')           # Security events
logger = logging.getLogger('myapp.tasks')               # Celery tasks
logger = logging.getLogger('myapp.utils')               # Utilities
```

### 7. Testing Your Logging

Run the development server and visit a page that triggers logs:

```bash
python manage.py runserver
```

You should see colored output in the terminal (console) and logs being written to:
- `logs/django.log`
- `logs/django_errors.log`

### 8. Production Tips (using Gunicorn / uWSGI)

In production, it's common to use:

```python
# settings.py for production
LOGGING['handlers']['console']['formatter'] = 'verbose'

# Or use WatchedFileHandler for Docker/Kubernetes
'class': 'logging.handlers.WatchedFileHandler',
```

Would you like me to also show:
- How to add JSON structured logging?
- Integration with Sentry?
- Logging Celery tasks?
- Using `django-logging` or `structlog`?

Just let me know!