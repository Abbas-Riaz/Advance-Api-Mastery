"""
store/selectors/product.py
===========================
Read-only data access for Product. No create/update/delete logic here.
"""

import logging
import uuid
from typing import Optional

from django.db import models

from store.models.product import Product
from store.exceptions import ProductNotFound

logger = logging.getLogger(__name__)


def get_product_by_id(product_id: uuid.UUID) -> Product:
    """Fetch a single product by ID. Raises ProductNotFound if missing."""
    try:
        return Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        logger.warning(f"Product not found: {product_id}")
        raise ProductNotFound()

        # def all_products (filters : Optional[dict] = None) -> models.QuerySet[Product] :

        #     queryset = Product.objects.all()
        #     if not filters :
        #         return queryset.active()

        #     status = filters.get('status')

        #     if status :

        #         queryset = queryset.filter(status = status)
        #     else :
        #         queryset = queryset.active()

        #     if filters.get('in_stock') :
        queryset = queryset.instock()


def get_all_products(filters: Optional[dict] = None) -> models.QuerySet[Product]:
    """Fetch products, optionally narrowed by status and in_stock filters."""
    queryset = Product.objects.all()

    if not filters:
        return queryset.active()

    status = filters.get("status")
    if status:
        queryset = queryset.filter(status=status)
    else:
        queryset = queryset.active()

    if filters.get("in_stock"):
        queryset = queryset.in_stock()

    return queryset


def search_products(query: str) -> models.QuerySet[Product]:
    """Search active products by name (case-insensitive partial match)."""
    logger.info(f"Product search: '{query}'")
    return Product.objects.active().filter(name__icontains=query)
