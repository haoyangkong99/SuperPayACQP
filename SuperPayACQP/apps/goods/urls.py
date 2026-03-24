"""
Goods API URLs
"""
from django.urls import path
from apps.goods.goods_catalog_item_views import (
    GoodsCatalogUpsertView,
    GoodsCatalogListView,
    GoodsCatalogDetailView,
    GoodsCatalogDeleteView
)

urlpatterns = [
    # POST /api/goods/upsert - Create or update goods catalog item
    path('upsert', GoodsCatalogUpsertView.as_view(), name='goods-upsert'),
    
    # GET /api/goods - List all goods catalog items
    path('', GoodsCatalogListView.as_view(), name='goods-list'),
    
    # DELETE /api/goods/<goodsId>/delete - Delete goods catalog item
    path('<str:goods_id>/delete', GoodsCatalogDeleteView.as_view(), name='goods-delete'),
    
    # GET /api/goods/<goodsId> - Get specific goods catalog item
    path('<str:goods_id>', GoodsCatalogDetailView.as_view(), name='goods-detail'),
]
