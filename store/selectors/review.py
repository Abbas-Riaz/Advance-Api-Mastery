"""
get_reviews_for_product(product_id)
    → fetch product first (reuse get_product_by_id)
    → return Review.objects.filter(product=product)
               .select_related('user')
               .order_by('-created_at')

get_review_by_id(review_id)
    → fetch single review
    → raise ReviewNotFound if missing
"""

from .product import get_product_by_id
from store.models.product import Review
import uuid
from store.exceptions import ReviewNotFound


def get_reviews_for_product(product_id: uuid.UUID):
    # fetching the product using selectors
    product = get_product_by_id(id=product_id)
    # for getting product reviews and user associated with eachp product
    product_reviews = (
        Review.objects.filter(product=product)
        .select_related("user")
        .order_by("-created_at")
    )

    return product_reviews


def get_review_by_id(review_id: uuid.UUID):
    try:
        return Review.objects.get(id=review_id)
    except Review.DoesNotExist:
        raise ReviewNotFound()
