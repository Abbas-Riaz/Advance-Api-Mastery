# """
# ReviewListCreateView
#     GET  → list all reviews for a product
#     POST → create a review for a product

# ReviewDetailView
#     GET    → single review
#     DELETE → delete a review
# """

# """
# list all view :
#   steps :
#     need product id
# """
# from store.models.product import User
# import logging
# import uuid

# from rest_framework import status
# from rest_framework.permissions import IsAuthenticated
# from rest_framework.views import APIView
# from store.selectors.product import get_product_by_id
# from store.selectors.reviews import get_reviews_for_product
# from store.serializers.reviews import ReviewSerializer, ReviewCreateSerializer
# from store.services.reviews import create_review, get_review_by_id
# from core.responses import ApiResponse
# from store.services.reviews import delete_review


# class ReviewListCreateView(APIView):

#     def get(self, product_id):
#         # call selector method for getting all reviews for a product
#         product_reviews = get_reviews_for_product(product_id=product_id)

#         serializer = ReviewSerializer(product_reviews, many=True)

#         return ApiResponse.success(
#             data=serializer.data,
#             message="all reviews for product",
#             code="Reviews _Fetced",
#         )

#     def post(self, request, product):
#         product = get_product_by_id()
#         user = User.objects.first()

#         serializer = ReviewCreateSerializer(data=request.data)

#         serializer.is_valid(raise_exception=True)

#         review = create_review(
#             product_id=product.id,
#             user=user,
#             date=serializer.validated_data,
#         )

#         return ApiResponse.success(
#             data=ReviewSerializer(review).data,
#             message="review added successfully",
#             status_code=status.HTTP_201_CREATED,
#         )


# class ReviewDetailView(APIView):

#     permission_classes = [IsAuthenticated]

#     def get(self, request, pk):

#         review = get_review_by_id(product_id=pk)
#         serializer = ReviewSerializer(review)

#         serializer.is_valid(Exception=True)

#         return ApiResponse.success(data=serializer.validated_data)

#     def delete(self, request, pk):

#         deleted_review = delete_review(review_id=pk)

#         return ApiResponse.success(message=f"deleted successfully {deleted_review.id} ")

"""
store/views/review.py
=====================
HTTP layer for the Review domain.

Thin views only — no business logic, no ORM queries.
All logic delegated to selectors and services.

URL Patterns:
    GET    /products/<uuid:product_pk>/reviews/          → list reviews
    POST   /products/<uuid:product_pk>/reviews/          → create review
    GET    /products/<uuid:product_pk>/reviews/<uuid:pk>/ → single review
    DELETE /products/<uuid:product_pk>/reviews/<uuid:pk>/ → delete review
"""

import logging
import uuid

from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.views import APIView

from core.responses import ApiResponse
from store.selectors.reviews import get_reviews_for_product, get_review_by_id
from store.serializers.reviews import ReviewSerializer, ReviewCreateSerializer
from store.services.reviews import create_review, delete_review

logger = logging.getLogger(__name__)


class ReviewListCreateView(APIView):
    """
    GET  /products/<uuid:product_pk>/reviews/ — list all reviews for a product
    POST /products/<uuid:product_pk>/reviews/ — create a review
    """

    def get(self, request, product_pk: uuid.UUID):
        """
        Return all reviews for a specific product.
        select_related('user') handled inside selector — no N+1.
        """
        logger.info(f"Reviews list requested | product: {product_pk}")

        reviews = get_reviews_for_product(product_id=product_pk)
        serializer = ReviewSerializer(reviews, many=True)

        return ApiResponse.success(
            data=serializer.data, message="Reviews fetched successfully."
        )

    def post(self, request, product_pk: uuid.UUID):
        """
        Create a review for a product.
        User comes from request — not from body (security).
        product_id comes from URL — not from body.
        """
        logger.info(f"Review creation requested | product: {product_pk}")

        # Temporary until JWT auth is set up
        user = User.objects.first()

        serializer = ReviewCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        review = create_review(
            product_id=product_pk, user=user, data=serializer.validated_data
        )

        return ApiResponse.success(
            data=ReviewSerializer(review).data,
            message="Review created successfully.",
            status_code=status.HTTP_201_CREATED,
        )


class ReviewDetailView(APIView):
    """
    GET    /products/<uuid:product_pk>/reviews/<uuid:pk>/ — single review
    DELETE /products/<uuid:product_pk>/reviews/<uuid:pk>/ — delete review
    """

    def get(self, request, product_pk: uuid.UUID, pk: uuid.UUID):
        """Return a single review by ID."""
        logger.info(f"Review detail requested | review: {pk}")

        review = get_review_by_id(review_id=pk)

        return ApiResponse.success(
            data=ReviewSerializer(review).data, message="Review fetched successfully."
        )

    def delete(self, request, product_pk: uuid.UUID, pk: uuid.UUID):
        """
        Delete a review.
        Service checks ownership — only the review author can delete.
        """
        logger.info(f"Review deletion requested | review: {pk}")

        # Temporary until JWT auth is set up
        user = User.objects.first()

        delete_review(review_id=pk, user=user)

        return ApiResponse.success(
            message="Review deleted successfully.",
            status_code=status.HTTP_204_NO_CONTENT,
        )
