from django.db import models
from ..models import Product
from rest_framework import serializers

from ..services.product import create_product

"""
ProductSerializer:
    ✅ ModelSerializer
    ✅ expose: id, name, description, price, stock,
               status, is_in_stock, created_at, updated_at
    ✅ all fields read_only (output only)
    ✅ is_in_stock → SerializerMethodField or BooleanField(read_only=True)

ProductCreateSerializer:
    ✅ ModelSerializer
    ✅ fields: name, description, price, stock, status
    ✅ validate_price → raise error if price <= 0
    ✅ validate_name  → strip whitespace, check not empty

ProductUpdateSerializer:
    ✅ ModelSerializer
    ✅ same fields as create
    ✅ ALL fields optional (partial update)
    ✅ same validators


"""

from rest_framework import serializers
from store.models.product import Product


class ProductSerializer(serializers.ModelSerializer):
    # @property on model — must be declared explicitly
    is_in_stock = serializers.BooleanField(read_only=True)

    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "description",
            "price",
            "stock",
            "status",
            "is_in_stock",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields


class ProductCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ["name", "description", "price", "stock", "status"]

    def validate_price(self, value):
        if value <= 0:
            raise serializers.ValidationError("Price must be greater than zero.")
        return value  # always return value

    def validate_name(self, value):
        if not value.strip():
            raise serializers.ValidationError("Name cannot be empty or whitespace.")
        return value.strip()


class ProductUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ["name", "description", "price", "stock", "status"]
        # all fields optional — partial update pattern
        extra_kwargs = {
            field: {"required": False}
            for field in ["name", "description", "price", "stock", "status"]
        }

    def validate_price(self, value):
        if value <= 0:
            raise serializers.ValidationError("Price must be greater than zero.")
        return value
