"""
Goods Catalog Views
Upsert and Query endpoints for GoodsCatalogItems
Using DTO pattern for request/response handling
"""
import logging
import uuid
from decimal import Decimal
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from pydantic import ValidationError

from apps.goods.goods_catalog_item_models import GoodsCatalogItem
from dtos.request import GoodsCatalogItemRequestDTO
from dtos.response import (
    GoodsCatalogUpsertResponseDTO,
    GoodsCatalogListResponseDTO,
    GoodsCatalogDetailResponseDTO,
    GoodsCatalogItemDTO
)
from utils.constants import Result, ResultStatus

logger = logging.getLogger(__name__)


class GoodsCatalogUpsertView(APIView):
    """
    POST /api/goods/upsert
    Create or update a GoodsCatalogItem
    
    Request body (using DTO):
    {
        "goodsId": "uuid (optional, for update)",
        "goodsName": "string (required)",
        "goodsCategory": "string (optional)",
        "goodsBrand": "string (optional)",
        "goodsUnitAmountValue": integer (required),
        "goodsUnitAmountCurrency": "string (optional, default: MYR)",
        "stockQuantity": integer (optional, default: 0),
        "taxRate": decimal (optional, default: 0.00)
    }
    """
    
    def post(self, request):
        try:
            # Parse and validate request using DTO
            try:
                request_dto = GoodsCatalogItemRequestDTO(**request.data)
            except ValidationError as e:
                result = Result(
                    resultStatus=ResultStatus.FAILURE,
                    resultMessage='Validation error: ' + str(e.errors()[0]['msg']) if e.errors() else 'Validation error',
                    resultCode='PARAM_ILLEGAL'
                )
                return Response({
                    'result': result.model_dump(),
                    'errors': e.errors()
                }, status=status.HTTP_400_BAD_REQUEST)
            
            goods_id = request_dto.goodsId
            goods_name = request_dto.goodsName
            goods_category = request_dto.goodsCategory or ''
            goods_brand = request_dto.goodsBrand or ''
            goods_unit_amount_value = request_dto.goodsUnitAmountValue
            goods_unit_amount_currency = request_dto.goodsUnitAmountCurrency or 'MYR'
            stock_quantity = request_dto.stockQuantity if request_dto.stockQuantity is not None else 0
            tax_rate = Decimal(str(request_dto.taxRate)) if request_dto.taxRate is not None else Decimal('0.00')
            
            # If goodsId is provided, try to update existing item
            if goods_id:
                try:
                    goods_uuid = uuid.UUID(goods_id)
                    item = GoodsCatalogItem.objects.filter(goodsId=goods_uuid).first()
                    
                    if item:
                        # Update existing item
                        item.goodsName = goods_name
                        item.goodsCategory = goods_category
                        item.goodsBrand = goods_brand
                        item.goodsUnitAmountValue = goods_unit_amount_value
                        item.goodsUnitAmountCurrency = goods_unit_amount_currency
                        item.stockQuantity = stock_quantity
                        item.taxRate = tax_rate 
                        item.save()
                        
                        # Build response DTO
                        response_dto = GoodsCatalogUpsertResponseDTO(
                            result=Result.returnSuccess(),
                            goodsId=str(item.goodsId),
                            action='updated'
                        )
                        return Response(response_dto.model_dump(), status=status.HTTP_200_OK)
                    else:
                        # Create new item with provided goodsId
                        item = GoodsCatalogItem.objects.create(
                            goodsId=goods_uuid,
                            goodsName=goods_name,
                            goodsCategory=goods_category,
                            goodsBrand=goods_brand,
                            goodsUnitAmountValue=goods_unit_amount_value,
                            goodsUnitAmountCurrency=goods_unit_amount_currency,
                            stockQuantity=stock_quantity,
                            taxRate=tax_rate
                        )
                        
                        # Build response DTO
                        response_dto = GoodsCatalogUpsertResponseDTO(
                            result=Result.returnSuccess(),
                            goodsId=str(item.goodsId),
                            action='created'
                        )
                        return Response(response_dto.model_dump(), status=status.HTTP_201_CREATED)
                        
                except ValueError:
                    result = Result(
                        resultStatus=ResultStatus.FAILURE,
                        resultMessage='Invalid goodsId format',
                        resultCode='PARAM_ILLEGAL'
                    )
                    return Response({
                        'result': result.model_dump()
                    }, status=status.HTTP_400_BAD_REQUEST)
            else:
                # Create new item with auto-generated UUID
                item = GoodsCatalogItem.objects.create(
                    goodsName=goods_name,
                    goodsCategory=goods_category,
                    goodsBrand=goods_brand,
                    goodsUnitAmountValue=goods_unit_amount_value,
                    goodsUnitAmountCurrency=goods_unit_amount_currency,
                    stockQuantity=stock_quantity,
                    taxRate=tax_rate
                )
                
                # Build response DTO
                response_dto = GoodsCatalogUpsertResponseDTO(
                    result=Result.returnSuccess(),
                    goodsId=str(item.goodsId),
                    action='created'
                )
                return Response(response_dto.model_dump(), status=status.HTTP_201_CREATED)
                
        except Exception as e:
            logger.error(f"Error upserting goods catalog item: {e}")
            result = Result(
                resultStatus=ResultStatus.FAILURE,
                resultMessage=str(e),
                resultCode='PROCESS_FAIL'
            )
            return Response({
                'result': result.model_dump()
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class GoodsCatalogListView(APIView):
    """
    GET /api/goods
    Returns all GoodsCatalogItems
    """
    
    def get(self, request):
        try:
            items = GoodsCatalogItem.objects.all().order_by('-created_at')
            
            # Build list of GoodsCatalogItemDTO
            goods_list = []
            for item in items:
                item_dto = GoodsCatalogItemDTO(
                    goodsId=str(item.goodsId),
                    goodsName=item.goodsName,
                    goodsCategory=item.goodsCategory,
                    goodsBrand=item.goodsBrand,
                    goodsUnitAmountValue=item.goodsUnitAmountValue,
                    goodsUnitAmountCurrency=item.goodsUnitAmountCurrency,
                    stockQuantity=item.stockQuantity,
                    taxRate=float(item.taxRate),
                    created_at=item.created_at.isoformat() if item.created_at else None,
                    updated_at=item.updated_at.isoformat() if item.updated_at else None
                )
                goods_list.append(item_dto)
            
            # Build response DTO
            response_dto = GoodsCatalogListResponseDTO(
                result=Result.returnSuccess(),
                count=len(goods_list),
                goods=goods_list
            )
            
            return Response(response_dto.model_dump(), status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error listing goods catalog items: {e}")
            result = Result(
                resultStatus=ResultStatus.FAILURE,
                resultMessage=str(e),
                resultCode='PROCESS_FAIL'
            )
            return Response({
                'result': result.model_dump()
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class GoodsCatalogDetailView(APIView):
    """
    GET /api/goods/<goodsId>
    Returns a specific GoodsCatalogItem by goodsId
    """
    
    def get(self, request, goods_id):
        try:
            try:
                goods_uuid = uuid.UUID(goods_id)
            except ValueError:
                result = Result(
                    resultStatus=ResultStatus.FAILURE,
                    resultMessage='Invalid goodsId format',
                    resultCode='PARAM_ILLEGAL'
                )
                return Response({
                    'result': result.model_dump()
                }, status=status.HTTP_404_NOT_FOUND)
            
            item = GoodsCatalogItem.objects.filter(goodsId=goods_uuid).first()
            
            if not item:
                result = Result(
                    resultStatus=ResultStatus.FAILURE,
                    resultMessage='Goods catalog item not found',
                    resultCode='ORDER_NOT_EXIST'
                )
                return Response({
                    'result': result.model_dump()
                }, status=status.HTTP_404_NOT_FOUND)
            
            # Build response DTO
            response_dto = GoodsCatalogDetailResponseDTO(
                result=Result.returnSuccess(),
                goodsId=str(item.goodsId),
                goodsName=item.goodsName,
                goodsCategory=item.goodsCategory,
                goodsBrand=item.goodsBrand,
                goodsUnitAmountValue=item.goodsUnitAmountValue,
                goodsUnitAmountCurrency=item.goodsUnitAmountCurrency,
                stockQuantity=item.stockQuantity,
                taxRate=float(item.taxRate),
                created_at=item.created_at.isoformat() if item.created_at else None,
                updated_at=item.updated_at.isoformat() if item.updated_at else None
            )
            
            return Response(response_dto.model_dump(), status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error getting goods catalog item: {e}")
            result = Result(
                resultStatus=ResultStatus.FAILURE,
                resultMessage=str(e),
                resultCode='PROCESS_FAIL'
            )
            return Response({
                'result': result.model_dump()
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class GoodsCatalogDeleteView(APIView):
    """
    DELETE /api/goods/<goodsId>/delete
    Delete a GoodsCatalogItem by goodsId
    """
    
    def delete(self, request, goods_id):
        try:
            try:
                goods_uuid = uuid.UUID(goods_id)
            except ValueError:
                result = Result(
                    resultStatus=ResultStatus.FAILURE,
                    resultMessage='Invalid goodsId format',
                    resultCode='PARAM_ILLEGAL'
                )
                return Response({
                    'result': result.model_dump()
                }, status=status.HTTP_400_BAD_REQUEST)
            
            item = GoodsCatalogItem.objects.filter(goodsId=goods_uuid).first()
            
            if not item:
                result = Result(
                    resultStatus=ResultStatus.FAILURE,
                    resultMessage='Goods catalog item not found',
                    resultCode='ORDER_NOT_EXIST'
                )
                return Response({
                    'result': result.model_dump()
                }, status=status.HTTP_404_NOT_FOUND)
            
            # Delete the item
            item_name = item.goodsName
            item.delete()
            
            # Build response
            result = Result(
                resultStatus=ResultStatus.SUCCESS,
                resultMessage=f'Goods catalog item "{item_name}" deleted successfully',
                resultCode='SUCCESS'
            )
            return Response({
                'result': result.model_dump(),
                'goodsId': goods_id,
                'action': 'deleted'
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error deleting goods catalog item: {e}")
            result = Result(
                resultStatus=ResultStatus.FAILURE,
                resultMessage=str(e),
                resultCode='PROCESS_FAIL'
            )
            return Response({
                'result': result.model_dump()
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
