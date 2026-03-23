"""
Order Models
"""
from django.db import models


class Order(models.Model):
    """
    Order model for SuperPayACQP
    """
    orderId = models.TextField(primary_key=True)
    referenceOrderId = models.TextField(blank=True, null=True)
    orderDescription = models.TextField(blank=True, null=True)
    orderAmountValue = models.IntegerField(null=True)
    orderAmountCurrency = models.TextField(blank=True, null=True)
    merchantId = models.TextField(blank=True, null=True)  # FK to Merchant
    shippingName = models.JSONField(null=True, blank=True)
    shippingPhoneNo = models.TextField(blank=True, null=True)
    shippingAddress = models.JSONField(null=True, blank=True)
    shippingCarrier = models.TextField(blank=True, null=True)
    referenceBuyerId = models.TextField(blank=True, null=True)
    buyerName = models.JSONField(null=True, blank=True)
    buyerPhoneNo = models.TextField(blank=True, null=True)
    buyerEmail = models.TextField(blank=True, null=True)
    env = models.JSONField(null=True, blank=True)
    indirectAcquirer = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'orders'
        verbose_name = 'Order'
        verbose_name_plural = 'Orders'

    def __str__(self):
        return self.orderId


class OrderGoods(models.Model):
    """
    Order Goods model for SuperPayACQP
    """
    id = models.AutoField(primary_key=True)
    orderId = models.TextField(blank=True, null=True)  # FK to Order
    referenceGoodsId = models.TextField(blank=True, null=True)
    goodsName = models.TextField(blank=True, null=True)
    goodsCategory = models.TextField(blank=True, null=True)
    goodsBrand = models.TextField(blank=True, null=True)
    goodsUnitAmountValue = models.IntegerField(null=True)
    goodsUnitAmountCurrency = models.TextField(blank=True, null=True)
    goodsQuantity = models.IntegerField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'order_goods'
        verbose_name = 'Order Goods'
        verbose_name_plural = 'Order Goods'

    def __str__(self):
        return f"{self.goodsName} - {self.orderId}"
