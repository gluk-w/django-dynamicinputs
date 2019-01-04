import pytest
from django.conf import settings


def pytest_configure():
    # For Django 1.8+
    TEMPLATES = [
        {
            'BACKEND': 'django.template.backends.django.DjangoTemplates',
            'DIRS': [],
            'APP_DIRS': True,
        }
    ]

    settings.configure(INSTALLED_APPS=(
        'dynamicinputs',
        'dictionaryfield',
    ), TEMPLATES = TEMPLATES)
