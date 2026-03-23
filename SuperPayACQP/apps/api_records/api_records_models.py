"""
API Record Model
"""
from django.db import models


class ApiRecord(models.Model):
    """
    API Record model for logging all API calls
    """
    id = models.AutoField(primary_key=True)
    api_url = models.TextField()
    http_method= models.TextField()
    request_body = models.TextField()
    response_body = models.TextField()
    message_type = models.TextField()  # INBOUND or OUTBOUND
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'api_records'
        verbose_name = 'API Record'
        verbose_name_plural = 'API Records'

    def __str__(self):
        return f"{self.api_url} - {self.message_type}"
