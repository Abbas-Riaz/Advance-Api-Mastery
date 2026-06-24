"""
store/models/product.py
=======================
Product is the core entity of the store domain.

This model represents a sellable item in the system.
It is the parent in the following relationships:
    - Product → Review     (One to Many)  — Phase 3
    - Product → Tag        (Many to Many) — Phase 4
    - Product → OrderItem  (One to Many)  — Phase 5

DESIGN DECISIONS
----------------
- UUID primary key   : prevents sequential ID scraping
- Status TextChoices : type-safe, admin-friendly, no raw strings scattered
- Custom manager     : all queryset logic centralised in managers/product.py
- DB indexes         : status and name are the most filtered/searched fields
- no null=True on    : TextField — one empty state (empty string) is enough,
  description          two empty states (null + empty string) cause bugs

DO NOT put business logic here.
Business logic belongs in services/product.py.
"""

import uuid
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator

from store.managers.product import ProductManager
from django.conf import settings

# class Product(models.Model):
#     """
#     Represents a single product in the store.

#     Lifecycle:
#         DRAFT → ACTIVE → INACTIVE

#     A product starts as DRAFT, gets published as ACTIVE,
#     and is soft-disabled as INACTIVE (never hard deleted).
#     """

#     class Status(models.TextChoices):
#         """
#         Defines the visibility/availability state of a product.

#         DRAFT    — created but not yet visible to customers
#         ACTIVE   — live and visible to customers
#         INACTIVE — hidden from customers, kept for records
#         """

#         ACTIVE = "active", "Active"
#         INACTIVE = "inactive", "Inactive"
#         DRAFT = "draft", "Draft"

#     # ------------------------------------------------------------------
#     # Identity
#     # ------------------------------------------------------------------

#     # UUID prevents sequential ID scraping (/products/1, /products/2 etc)
#     id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

#     # unique=True enforced at DB level — serializer validation is second layer
#     name = models.CharField(max_length=255, unique=True)

#     # blank=True — empty string allowed, no null=True — avoids dual empty states
#     description = models.TextField(blank=True)

#     # ------------------------------------------------------------------
#     # Pricing & Inventory
#     # ------------------------------------------------------------------

#     # max_digits=10, decimal_places=2 supports up to 99,999,999.99
#     price = models.DecimalField(max_digits=10, decimal_places=2)

#     # PositiveIntegerField — DB-level constraint, stock can never go negative
#     stock = models.PositiveIntegerField(default=0)

#     # ------------------------------------------------------------------
#     # State
#     # ------------------------------------------------------------------

#     status = models.CharField(
#         max_length=20,
#         choices=Status.choices,
#         default=Status.DRAFT,  # always starts as draft — never auto-published
#     )

#     # ------------------------------------------------------------------
#     # Timestamps — never set manually, Django handles both
#     # ------------------------------------------------------------------

#     # auto_now_add — written once on INSERT, never touched again
#     created_at = models.DateTimeField(auto_now_add=True)

#     # auto_now — updated on every .save() call automatically
#     updated_at = models.DateTimeField(auto_now=True)

# # ------------------------------------------------------------------
# # Manager
# # ------------------------------------------------------------------

# # Replaces default manager — enables Product.objects.active(), .in_stock()
# objects = ProductManager()

#     class Meta:
#         # Newest products first on every query — no need to add order_by() anywhere
#         ordering = ["-created_at"]

#         indexes = [
#             # Index on status — most list views filter by status='active'
#             models.Index(fields=["status"]),
#             # Index on name — search queries hit this field most
#             models.Index(fields=["name"]),
#         ]

#     def __str__(self):
#         # Used in Django admin and shell — makes debugging readable
#         return f"{self.name} ({self.status})"

#     # ------------------------------------------------------------------
#     # Properties — computed fields, no DB hit
#     # ------------------------------------------------------------------

#     @property
#     def is_in_stock(self):
#         """
#         Returns True if stock is available.

#         Used by serializers and business logic to check availability
#         without scattering stock > 0 checks everywhere in the codebase.
#         """
#         return self.stock > 0


"""

this file is for designign models for prduct info storing and related data 

"""


class Product(models.Model):

    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        ACTIVE = "active", "Active"
        INACTIVE = "inactive", "Inactive"

    """uuid field avoid scraping from your website and it remain unique globally and it is difficult to guess and send data from front end """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True)
    price = models.DecimalField(
        decimal_places=2, max_digits=10
    )  # user decimal field for prices to avoid float error and keep value shorten
    stock = models.PositiveBigIntegerField(default=0)  # stock can not be negative

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT,  # always starts as draft — never auto-published
    )

    # ------------------------------------------------------------------
    # Timestamps — never set manually, Django handles both
    # ------------------------------------------------------------------

    # auto_now_add — written once on INSERT, never touched again
    created_at = models.DateTimeField(auto_now_add=True)

    # auto_now — updated on every .save() call automatically
    updated_at = models.DateTimeField(auto_now=True)

    # ------------------------------------------------------------------
    # Manager
    # ------------------------------------------------------------------

    # Replaces default manager — enables Product.objects.active(), .in_stock()
    objects = ProductManager()

    def __str__(self):
        # Used in Django admin and shell — makes debugging readable
        return f"{self.name} ({self.status})"

    @property
    def is_in_stock(self):
        return self.stock > 0


class Review(models.Model):
    """
    this model will be used to store reviews data and related things
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    # rating must be assiciated with user no rating should be there when no user
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE
    )  # rating is for product so there must be a product against rating

    # validation for rating should be consider rating should be in between 1 and 5 and each rating should be unique for a product by users
    rating = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(1, "Rating must be between 1 and 5"),
            MaxValueValidator(5, "Rating must be between 1 and 5"),
        ]
    )
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["created_at"]
        unique_together = [["user", "product"]]

        indexes = [
            models.Index(fields=["user"]),
            models.Index(fields=["product"]),
        ]

    def __str__(self):
        return f"{self.user} , {self.rating}"
