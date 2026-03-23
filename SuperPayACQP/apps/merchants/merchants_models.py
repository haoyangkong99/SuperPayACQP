"""
Merchant Model
"""
from django.db import models


class Merchant(models.Model):
    """
    Merchant model for SuperPayACQP
    """
    merchantId = models.TextField(primary_key=True)
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
    productCodes=models.JSONField(null=True, blank=True)
    registrationNotifyUrl = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'merchants'
        verbose_name = 'Merchant'
        verbose_name_plural = 'Merchants'

    def __str__(self):
        return self.merchantName
    

class Registration(models.Model):

    registrationRequestId = models.TextField(primary_key=True)
    productCodes = models.JSONField(null=True, blank=True)
    referenceMerchantId = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'registration_records'


class EntryCode(models.Model):
    """
    Entry Code model for SuperPayACQP
    """
    codeId = models.TextField(primary_key=True)
    merchantId = models.TextField()  # FK to Merchant
    codeStartTime = models.DateTimeField()
    codeExpireTime = models.DateTimeField()
    status = models.TextField(default='Active')  # Active or Inactive
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'entry_codes'
        verbose_name = 'Entry Code'
        verbose_name_plural = 'Entry Codes'

    def __str__(self):
        return f"{self.codeId} - {self.merchantId}"
