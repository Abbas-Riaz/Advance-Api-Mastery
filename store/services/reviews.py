"""
create_review(*, product_id, user, data) -> Review
    → fetch product (selector)
    → check user hasn't already reviewed this product
      (raise ReviewAlreadyExists if they have)
    → Review.objects.create(product=product, user=user, **data)
    → log it

delete_review(*, review_id, user) -> None
    → fetch review (selector)
    → check review belongs to this user (raise PermissionDenied if not)
    → review.delete()
    → log it
"""

import uuid
from store.models import Review
import logging

from rest_framework.exceptions import PermissionDenied

from store.selectors.product import get_product_by_id
from store.exceptions import ReviewAlreadyExists

logger = logging.getLogger(__name__)

from store.selectors.reviews import get_review_by_id

"""
create view :
  -every review should be assiciated with user so we need a user 
  -for creating review we need : rating , user , product
"""


def create_review(*, product_id, user, data) -> Review:

    product = get_product_by_id(product_id=product_id)

    # check the uniqueness of each review each user can have only one review

    if Review.objects.filter(product=product, user=user).exists():
        logger.warning(
            f"review already exist for this user {user.id} for this product {product.name}"
        )
        raise ReviewAlreadyExists()
    review = Review.objects.create(product=product, user=user, **data)
    logger.info("review created successfully ")
    return review


def delete_review(*, review_id: uuid.UUID, user) -> None:

    review = get_review_by_id(
        review_id=review_id,
    )

    if review.user != user:
        raise PermissionDenied()
    review.delete()

    logger.info(f"{review_id} has been deleted")
