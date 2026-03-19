"""
Payment Models
"""
from django.db import models


class PaymentRequest(models.Model):
    """
    Payment Request model for SuperPayACQP
    """
    paymentRequestId = models.TextField(primary_key=True)
    acquirerId = models.TextField(blank=True)
    paymentAmountValue = models.IntegerField()
    paymentAmountCurrency = models.TextField()
    paymentMethodType = models.TextField(blank=True)
    paymentMethodId = models.TextField(blank=True)
    customerId = models.TextField(blank=True)
    paymentMethodMetaData = models.JSONField(null=True, blank=True)
    isInStorePayment = models.BooleanField(default=False)
    isCashierPayment = models.BooleanField(default=False)
    inStorePaymentScenario = models.TextField(blank=True)
    paymentExpiryTime = models.DateTimeField(null=True, blank=True)
    paymentNotifyUrl = models.TextField(blank=True)
    paymentRedirectUrl = models.TextField(blank=True)
    splitSettlementId = models.TextField(blank=True)
    settlementStrategy = models.JSONField(null=True, blank=True)
    paymentId = models.TextField(blank=True)
    paymentTime = models.DateTimeField(null=True, blank=True)
    pspId = models.TextField(blank=True)
    walletBrandName = models.TextField(blank=True)
    mppPaymentId = models.TextField(blank=True)
    customsDeclarationAmountValue = models.IntegerField(null=True)
    customsDeclarationAmountCurrency = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'payment_requests'
        verbose_name = 'Payment Request'
        verbose_name_plural = 'Payment Requests'

    def __str__(self):
        return self.paymentRequestId


class PaymentRequestResult(models.Model):
    """
    Payment Request Result model for SuperPayACQP
    """
    id = models.AutoField(primary_key=True)
    paymentRequestId = models.TextField()  # FK to PaymentRequest
    isFinalStatus = models.BooleanField(default=False)
    resultStatus = models.TextField()
    resultCode = models.TextField()
    resultMessage = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'payment_requests_result'
        verbose_name = 'Payment Request Result'
        verbose_name_plural = 'Payment Request Results'

    def __str__(self):
        return f"{self.paymentRequestId} - {self.resultCode}"


class Settlement(models.Model):
    """
    Settlement model for SuperPayACQP
    """
    settlementId = models.TextField(primary_key=True)
    paymentRequestId = models.TextField()  # FK to PaymentRequest
    settlementAmount = models.IntegerField()
    settlementCurrency = models.TextField()
    quoteId = models.TextField(blank=True)
    quotePrice = models.DecimalField(max_digits=20, decimal_places=10, null=True)
    quoteCurrencyPair = models.TextField(blank=True)
    quoteStartTime = models.DateTimeField(null=True, blank=True)
    quoteExpiryTime = models.DateTimeField(null=True, blank=True)
    quoteUnit = models.TextField(blank=True)
    baseCurrency = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'settlements'
        verbose_name = 'Settlement'
        verbose_name_plural = 'Settlements'

    def __str__(self):
        return self.settlementId
