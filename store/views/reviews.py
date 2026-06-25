"""
ReviewListCreateView
    GET  → list all reviews for a product
    POST → create a review for a product

ReviewDetailView
    GET    → single review
    DELETE → delete a review
"""

"""
list all view :
  steps :
    need product id 
"""
from store.models.product import User
import logging
import uuid

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from store.selectors.product import get_product_by_id
from store.selectors.reviews import get_reviews_for_product
from store.serializers.reviews import ReviewSerializer, ReviewCreateSerializer
from store.services.reviews import create_review
from core.responses import ApiResponse


class ReviewListCreateView(APIView):

    def get(self, product_id):
        # call selector method for getting all reviews for a product
        product_reviews = get_reviews_for_product(product_id=product_id)

        serializer = ReviewSerializer(product_reviews, many=True)

        return ApiResponse.success(
            data=serializer.data,
            message="all reviews for product",
            code="Reviews _Fetced",
        )

    def post(self, request, product):
        product = get_product_by_id()
        user = User.objects.first()

        serializer = ReviewCreateSerializer(data=request.data)

        serializer.is_valid(raise_exception=True)

        review = create_review(
            product_id=product.id,
            user=user,
            date=serializer.validated_data,
        )

        return ApiResponse.success(
            data=ReviewSerializer(review).data,
            message="review added successfully",
            status_code=status.HTTP_201_CREATED,
        )
