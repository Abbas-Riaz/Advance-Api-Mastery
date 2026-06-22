"""
store/services/product.py
=========================
Write operations for the Product domain.

This module handles all state-changing operations (CREATE, UPDATE, DELETE).
It is the ONLY place in the codebase that should mutate Product data.

RESPONSIBILITIES
----------------
- Business rule validation before any DB mutation
- Calling selectors for object retrieval (never raw ORM queries here)
- Raising domain exceptions on rule violations
- Logging every mutation for auditability

WHAT DOES NOT BELONG HERE
--------------------------
- Read-only queries         → selectors/product.py
- HTTP request/response     → views/product.py
- Serialization/validation  → serializers/product.py

DEPENDENCY FLOW
---------------
views → services → selectors → models
         ↕
      exceptions
"""

import logging
import uuid
from typing import Optional

from store.exceptions import ProductAlreadyExists, ProductNotFound
from store.models.product import Product
from store.selectors.product import get_product_by_id

# Module-level logger — always use __name__ so logs show exact file path
# Log output example: "store.services.product — Product created: abc-123"
logger = logging.getLogger(__name__)


def create_product(*, data: dict) -> Product:
    """
    Create a new product after validating business rules.

    This is the single entry point for product creation in the entire system.
    No other layer (view, task, signal) should call Product.objects.create() directly.

    Business Rules:
        - Product name must be unique (enforced at DB level AND here for clean error)
        - Price must be greater than zero (enforced at serializer level before reaching here)

    Args:
        data (dict): Validated field data from ProductCreateSerializer.
                     Expected keys: name, description, price, stock, status
                     Caller must pass keyword argument: create_product(data={...})

    Returns:
        Product: Newly created Product instance.

    Raises:
        ProductAlreadyExists: If a product with the same name already exists.

    Usage:
        product = create_product(data=serializer.validated_data)
    """
    # Check uniqueness at service level before hitting the DB with an insert.
    # Although the DB has a unique constraint on name, catching it here gives
    # us a clean domain exception (ProductAlreadyExists) instead of a raw
    # IntegrityError that would fall through to a 500 response.
    if Product.objects.filter(name=data["name"]).exists():
        logger.warning(f"Product creation blocked — duplicate name: '{data['name']}'")
        raise ProductAlreadyExists()

    # Create the product — all fields come from validated serializer data,
    # so no manual field-level validation is needed here.
    product = Product.objects.create(**data)

    logger.info(f"Product created — id: {product.id} | name: '{product.name}'")

    return product


def update_product(*, product_id: uuid.UUID, data: dict) -> Product:
    """
    Update an existing product's fields.

    Only updates the fields present in `data` — partial update pattern.
    Uses setattr() loop instead of Product.objects.filter().update() to:
        1. Trigger model-level signals (pre_save, post_save) if added later
        2. Properly update the `updated_at` auto_now timestamp
        3. Allow per-field hooks in the future without changing this function

    Note: Product.objects.filter().update() bypasses .save() entirely,
    which means auto_now fields do NOT update. Always prefer .save() for
    single object updates.

    Args:
        product_id (uuid.UUID): The UUID of the product to update.
        data (dict):            Fields to update with their new values.
                                Only provided fields are touched — others unchanged.

    Returns:
        Product: Updated Product instance with refreshed field values.

    Raises:
        ProductNotFound: If no product with the given ID exists.

    Usage:
        updated = update_product(product_id=pk, data=serializer.validated_data)
    """
    # Reuse selector — never write raw ORM get() calls in services.
    # If product doesn't exist, ProductNotFound is raised here automatically.
    product = get_product_by_id(product_id)

    # Partial update — iterate only over what was provided.
    # setattr(product, 'price', 99.99) is equivalent to product.price = 99.99
    # This pattern supports both full and partial updates without separate logic.
    for field, value in data.items():
        setattr(product, field, value)

    # Save to DB — triggers auto_now on updated_at automatically.
    # Only pass update_fields for performance if this becomes a bottleneck.
    product.save()

    logger.info(
        f"Product updated — id: {product.id} | fields changed: {list(data.keys())}"
    )

    return product


def delete_product(*, product_id: uuid.UUID) -> None:
    """
    Permanently delete a product by ID.

    WARNING: This is a hard delete. The record is permanently removed from the DB.
    If soft delete is needed in the future (is_deleted flag), implement it here
    without changing the function signature — callers won't need to change.

    Args:
        product_id (uuid.UUID): The UUID of the product to delete.

    Returns:
        None: Callers (views) should return 204 No Content after calling this.

    Raises:
        ProductNotFound: If no product with the given ID exists.

    Usage:
        delete_product(product_id=pk)
    """
    # Fetch first — ensures ProductNotFound is raised cleanly if missing,
    # rather than silently deleting zero rows (which ORM filter().delete() would do).
    product = get_product_by_id(product_id)

    # Store name before deletion for the log — after .delete() the object still
    # exists in memory but referencing it can cause unexpected behaviour in
    # some signal/cache setups, so we capture what we need beforehand.
    product_name = product.name

    product.delete()

    logger.info(f"Product deleted — id: {product_id} | name: '{product_name}'")
