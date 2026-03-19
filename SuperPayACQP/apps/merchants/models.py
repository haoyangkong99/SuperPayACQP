"""
Merchant Model
"""
from django.db import models


class Merchant(models.Model):
    """
    Merchant model for SuperPayACQP
    """
    merchantId = models.TextField(primary_key=True)
    referenceMerchantId = models.TextField(blank=True)
    merchantName = models.TextField()
    merchantDisplayName = models.TextField()
    merchantRegisterDate = models.DateTimeField(null=True, blank=True)
    merchantMCC = models.TextField(blank=True)
    merchantAddress = models.JSONField(null=True, blank=True)
    store = models.JSONField(null=True, blank=True)
    registrationDetailLegalName = models.TextField(blank=True)
    registrationDetailRegistrationType = models.TextField(blank=True)
    registrationDetailRegistrationNo = models.TextField(blank=True)
    registrationDetailRegistrationAddress = models.JSONField(null=True, blank=True)
    registrationDetailBusinessType = models.TextField(blank=True)
    websites = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'merchants'
        verbose_name = 'Merchant'
        verbose_name_plural = 'Merchants'

    def __str__(self):
        return self.merchantName
