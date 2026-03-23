"""
Payment Models
"""
from django.db import models


class PaymentRequest(models.Model):
    """
    Payment Request model for SuperPayACQP
    """
    paymentRequestId = models.TextField(primary_key=True)
    acquirerId = models.TextField(blank=True, null=True)
    paymentAmountValue = models.IntegerField()
    paymentAmountCurrency = models.TextField()
    paymentMethodType = models.TextField(blank=True, null=True)
    paymentMethodId = models.TextField(blank=True, null=True)
    customerId = models.TextField(blank=True, null=True)
    paymentMethodMetaData = models.JSONField(null=True, blank=True)
    isInStorePayment = models.BooleanField(default=False)
    isCashierPayment = models.BooleanField(default=False)
    inStorePaymentScenario = models.TextField(blank=True, null=True)
    paymentExpiryTime = models.DateTimeField(null=True, blank=True)
    paymentNotifyUrl = models.TextField(blank=True, null=True)
    paymentRedirectUrl = models.TextField(blank=True, null=True)
    splitSettlementId = models.TextField(blank=True, null=True)
    settlementStrategy = models.JSONField(null=True, blank=True)
    paymentId = models.TextField(blank=True, null=True)
    paymentTime = models.DateTimeField(null=True, blank=True)
    pspId = models.TextField(blank=True, null=True)
    walletBrandName = models.TextField(blank=True, null=True)
    mppPaymentId = models.TextField(blank=True, null=True)
    customsDeclarationAmountValue = models.IntegerField(null=True)
    customsDeclarationAmountCurrency = models.TextField(blank=True, null=True)
    resultStatus = models.TextField(blank=True, null=True)
    resultCode = models.TextField(blank=True, null=True)
    resultMessage = models.TextField(blank=True, null=True)
    paymentStatus = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'payment_requests'
        verbose_name = 'Payment Request'
        verbose_name_plural = 'Payment Requests'

    def __str__(self):
        return self.paymentRequestId


class Settlement(models.Model):
    """
    Settlement model for SuperPayACQP
    """
    settlementId = models.TextField(primary_key=True)
    paymentRequestId = models.TextField()  # FK to PaymentRequest
    settlementAmountValue = models.IntegerField()
    settlementCurrency = models.TextField()
    quoteId = models.TextField(blank=True, null=True)
    quotePrice = models.DecimalField(max_digits=20, decimal_places=10, null=True)
    quoteCurrencyPair = models.TextField(blank=True, null=True)
    quoteStartTime = models.DateTimeField(null=True, blank=True)
    quoteExpiryTime = models.DateTimeField(null=True, blank=True)
    quoteUnit = models.TextField(blank=True, null=True)
    baseCurrency = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'settlements'
        verbose_name = 'Settlement'
        verbose_name_plural = 'Settlements'

    def __str__(self):
        return self.settlementId
