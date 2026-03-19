"""
API Records App Configuration
"""
from django.apps import AppConfig


class ApiRecordsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.api_records'
    verbose_name = 'API Records'
