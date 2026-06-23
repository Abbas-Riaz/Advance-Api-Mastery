"""
store/views/product.py
======================
HTTP layer for the Product domain.

This module contains ONLY request/response handling.
No business logic, no ORM queries, no domain rules live here.

RESPONSIBILITIES
----------------
- Parse incoming HTTP requests
- Delegate validation to serializers
- Delegate business logic to services and selectors
- Return consistent HTTP responses via ApiResponse

WHAT DOES NOT BELONG HERE
--------------------------
- ORM queries          → selectors/product.py
- Business rules       → services/product.py
- Data validation      → serializers/product.py

URL PATTERNS
------------
    GET    /products/           → ProductListCreateView.get()
    POST   /products/           → ProductListCreateView.post()
    GET    /products/<uuid:pk>/ → ProductDetailView.get()
    PATCH  /products/<uuid:pk>/ → ProductDetailView.patch()
    DELETE /products/<uuid:pk>/ → ProductDetailView.delete()
"""

import logging
import uuid

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from core.responses import ApiResponse
from store.selectors.product import get_all_products, get_product_by_id
from store.serializers.product import (
    ProductCreateSerializer,
    ProductSerializer,
    ProductUpdateSerializer,
)
from store.services.product import create_product, delete_product, update_product

# Module-level logger — logs will show as "store.views.product" in output
# making it easy to trace which view triggered a log entry
logger = logging.getLogger(__name__)


class ProductListCreateView(APIView):
    """
    Handles collection-level operations on Product.

    Endpoints:
        GET  /products/ — list all active products
        POST /products/ — create a new product
    """

    # Require valid JWT token for all methods in this view
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Return a list of all active products.

        No filters applied by default — get_all_products() returns
        active products only via the custom manager.

        Returns:
            200: List of serialized products.
        """
        logger.info(f"Product list requested | user: {request.user.id}")

        # Fetch via selector — never query ORM directly in views
        products = get_all_products()

        # many=True tells serializer to handle a queryset, not a single object
        serializer = ProductSerializer(products, many=True)

        return ApiResponse.success(
            data=serializer.data, message="Products fetched successfully."
        )

    def post(self, request):
        """
        Create a new product.

        Validates input via ProductCreateSerializer, then delegates
        creation to the service layer which enforces business rules.

        Returns:
            201: Serialized newly created product.
            400: Validation errors from serializer.
            409: Duplicate product name (raised by service).
        """
        logger.info(f"Product creation requested | user: {request.user.id}")

        # Step 1 — validate incoming data
        # raise_exception=True means ValidationError is raised immediately
        # on invalid data — global handler formats it into our error shape
        serializer = ProductCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Step 2 — delegate to service
        # service handles duplicate checking, logging, and DB write
        # keyword arg (data=) required because service uses keyword-only args (*)
        product = create_product(data=serializer.validated_data)

        # Step 3 — serialize the created instance for output
        # use read serializer (ProductSerializer) not the write one
        return ApiResponse.success(
            data=ProductSerializer(product).data,
            message="Product created successfully.",
            status_code=status.HTTP_201_CREATED,
        )


class ProductDetailView(APIView):
    """
    Handles single-instance operations on Product.

    Endpoints:
        GET    /products/<uuid:pk>/ — retrieve a product
        PATCH  /products/<uuid:pk>/ — partially update a product
        DELETE /products/<uuid:pk>/ — permanently delete a product
    """

    # Require valid JWT token for all methods in this view
    permission_classes = [IsAuthenticated]

    def get(self, request, pk: uuid.UUID):
        """
        Retrieve a single product by ID.

        Returns:
            200: Serialized product.
            404: Product not found (raised by selector).
        """
        logger.info(
            f"Product detail requested | product_id: {pk} | user: {request.user.id}"
        )

        # Selector raises ProductNotFound automatically if missing —
        # no try/except needed here, global handler catches it
        product = get_product_by_id(product_id=pk)

        return ApiResponse.success(
            data=ProductSerializer(product).data,
            message="Product fetched successfully.",
        )

    def patch(self, request, pk: uuid.UUID):
        """
        Partially update a product.

        Only fields present in request.data are updated.
        Fields not included remain unchanged.

        Returns:
            200: Serialized updated product.
            400: Validation errors.
            404: Product not found.
        """
        logger.info(
            f"Product update requested | product_id: {pk} | user: {request.user.id}"
        )

        # Validate only the fields provided — all fields are optional
        # in ProductUpdateSerializer via extra_kwargs required=False
        serializer = ProductUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Service fetches product internally via selector,
        # applies changes, and saves — returns updated instance
        product = update_product(product_id=pk, data=serializer.validated_data)

        return ApiResponse.success(
            data=ProductSerializer(product).data,
            message="Product updated successfully.",
        )

    def delete(self, request, pk: uuid.UUID):
        """
        Permanently delete a product.

        Hard delete — no soft delete implemented at this stage.
        Returns 204 No Content on success (no body needed).

        Returns:
            204: Product deleted successfully.
            404: Product not found.
        """
        logger.info(
            f"Product deletion requested | product_id: {pk} | user: {request.user.id}"
        )

        # Service handles fetch + delete internally
        delete_product(product_id=pk)

        # 204 No Content — no data to return after deletion
        return ApiResponse.success(
            message="Product deleted successfully.",
            status_code=status.HTTP_204_NO_CONTENT,
        )
