"""
Refund Models
"""
from django.db import models


class RefundRecord(models.Model):
    """
    Refund Record model for SuperPayACQP
    """
    refundRequestId = models.TextField(primary_key=True)
    paymentRequestId = models.TextField()  # FK to PaymentRequest
    paymentId = models.TextField(blank=True)
    refundAmountValue = models.IntegerField()
    refundAmountCurrency = models.TextField()
    refundReason = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'refund_records'
        verbose_name = 'Refund Record'
        verbose_name_plural = 'Refund Records'

    def __str__(self):
        return self.refundRequestId
