"""
store/serializers/review.py
============================
Serializers for the Review domain.

ReviewSerializer        — read/output, used in all responses
ReviewCreateSerializer  — write/input, used on POST only
"""

from rest_framework import serializers
from store.models.product import Review


class ReviewSerializer(serializers.ModelSerializer):
    """
    Output serializer for Review.
    Exposes human-readable user and product fields instead of raw IDs.
    """

    # Return username string — avoids exposing full User object
    user = serializers.SerializerMethodField()

    # Return product name string — avoids exposing full Product object
    product = serializers.SerializerMethodField()

    class Meta:
        model = Review
        fields = ["id", "product", "user", "rating", "comment", "created_at"]
        read_only_fields = ["id", "product", "user", "rating", "comment", "created_at"]

    def get_user(self, obj):
        return obj.user.username

    def get_product(self, obj):
        return obj.product.name


class ReviewCreateSerializer(serializers.ModelSerializer):
    """
    Input serializer for creating a Review.
    product and user are NOT here — they come from URL and request.user.
    """

    class Meta:
        model = Review
        fields = ["rating", "comment"]
        extra_kwargs = {
            "comment": {"required": False, "allow_blank": True},
        }

    def validate_rating(self, value):
        if not (1 <= value <= 5):
            raise serializers.ValidationError("Rating must be between 1 and 5.")
        return value
