from ..models.product import Product
from ..exceptions import ProductAlreadyExists, ProductNotFound
from typing import Optional

"""
get_product_by_id(product_id)
    → fetch single product
    → raise ProductNotFound if doesn't exist

get_all_products(filters=None)
    → return Product.objects.active() by default
    → if filters has 'status', apply it
    → if filters has 'in_stock', apply it

search_products(query)
    → filter by name__icontains=query
"""


def get_product_by_id(product_id: int):
    try:
        return Product.objects.get(id=product_id)
    except:
        raise ProductNotFound()


def get_all_products(filters : Optional[dict]  = None ):
    try:
        return Product.objects.all()

    except:
        raise ProductNotFound()


def search_products(): 
