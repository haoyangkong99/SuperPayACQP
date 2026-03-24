"""
Goods Catalog Items Model
"""
import uuid
from django.db import models


class GoodsCatalogItem(models.Model):
    """
    Goods Catalog Item model for SuperPayACQP
    """
    goodsId = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    goodsName = models.TextField()
    goodsCategory = models.TextField()
    goodsBrand = models.TextField()
    goodsUnitAmountValue = models.IntegerField()
    goodsUnitAmountCurrency = models.TextField(default='MYR')
    stockQuantity = models.IntegerField(default=0)
    taxRate = models.DecimalField(max_digits=5, decimal_places=2, default=None)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'goods_catalog_items'
        verbose_name = 'Goods Catalog Item'
        verbose_name_plural = 'Goods Catalog Items'

    def __str__(self):
        return f"{self.goodsName} ({self.goodsId})"
