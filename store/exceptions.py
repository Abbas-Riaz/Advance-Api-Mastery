# store/exceptions.py

from rest_framework.exceptions import APIException
from rest_framework import status


class ProductNotFound(APIException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = "Product not found."
    default_code = "product_not_found"


class InsufficientStock(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Not enough stock available."
    default_code = "insufficient_stock"


class ProductAlreadyExists(APIException):
    status_code = status.HTTP_409_CONFLICT
    default_detail = "A product with this name already exists."
    default_code = "product_already_exists"


class ReviewNotFound(APIException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = "review not found."
    default_code = "review_not_found"
