"""
Product Managers Module

This module contains custom managers and querysets for the Product model.
It provides chainable query methods for common product filtering operations
and business logic queries.

Usage Examples:
    # Basic filtering
    Product.objects.active()
    Product.objects.in_stock()
    Product.objects.on_sale()

    # Chaining
    Product.objects.active().in_stock().price_between(10, 50)

    # Business logic
    Product.objects.best_sellers(limit=10)
    Product.objects.trending(days=7)
    Product.objects.recommended_for_user(user)
"""

from django.db import models
from django.db.models import Q, Sum, Avg, Count, Min, Max
from django.utils import timezone
from datetime import timedelta
from ..models.product import Product


# ============================================================================
# ProductQuerySet - Chainable Query Methods
# ============================================================================
class ProductQuerySet(models.QuerySet):

    def price_between(self, min_price, max_price):
        return self.filter(price__gte=min_price, pric__lte=max_price)


class ProductQuerySet(models.QuerySet):
    """
    Custom QuerySet for Product model with chainable query methods.

    All methods in this class return QuerySet objects, allowing method chaining:
    Product.objects.active().in_stock().on_sale()

    Each method is documented with its purpose, business logic, and usage.
    """

    # ------------------------------------------------------------------------
    # Status & Availability Filters
    # ------------------------------------------------------------------------

    def active(self):
        """
        Filter products that are available for purchase.

        Business Rules:
        - Status must be 'active' (published and visible)
        - Stock must be greater than 0 (available for purchase)
        - Not soft-deleted (is_deleted=False)

        Returns:
            QuerySet: Active Product instances

        Usage:
            active_products = Product.objects.active()
        """
        return self.filter(status=Product.Status.ACTIVE, stock__gt=0, is_deleted=False)

    def in_stock(self):
        """
        Filter products with stock available.

        Does NOT filter by status, so includes active and inactive products.
        Useful for inventory management and restocking reports.

        Returns:
            QuerySet: Products with stock > 0

        Usage:
            all_in_stock = Product.objects.in_stock()
            active_in_stock = Product.objects.active().in_stock()
        """
        return self.filter(stock__gt=0)

    def out_of_stock(self):
        """
        Filter products with zero stock.

        Returns:
            QuerySet: Products with stock = 0

        Usage:
            out_of_stock_products = Product.objects.out_of_stock()
        """
        return self.filter(stock=0)

    def low_stock(self, threshold=5):
        """
        Filter products with stock below a threshold.

        Args:
            threshold (int): Stock threshold (default: 5)

        Returns:
            QuerySet: Products with 0 < stock < threshold

        Usage:
            low_stock_products = Product.objects.low_stock(threshold=3)
        """
        return self.filter(stock__lt=threshold, stock__gt=0)

    def draft(self):
        """
        Filter products in draft status.

        Returns:
            QuerySet: Draft Product instances

        Usage:
            draft_products = Product.objects.draft()
        """
        return self.filter(status=Product.Status.DRAFT)

    def inactive(self):
        """
        Filter products in inactive status.

        Returns:
            QuerySet: Inactive Product instances

        Usage:
            inactive_products = Product.objects.inactive()
        """
        return self.filter(status=Product.Status.INACTIVE)

    # ------------------------------------------------------------------------
    # Pricing & Discount Filters
    # ------------------------------------------------------------------------

    def price_between(self, min_price, max_price):
        """
        Filter products within a price range.

        Args:
            min_price (Decimal): Minimum price (inclusive)
            max_price (Decimal): Maximum price (inclusive)

        Returns:
            QuerySet: Products with min_price <= price <= max_price

        Usage:
            mid_range = Product.objects.price_between(50, 100)
        """
        return self.filter(price__gte=min_price, price__lte=max_price)

    def price_less_than(self, max_price):
        """Filter products with price less than or equal to max_price."""
        return self.filter(price__lte=max_price)

    def price_greater_than(self, min_price):
        """Filter products with price greater than or equal to min_price."""
        return self.filter(price__gte=min_price)

    def on_sale(self):
        """
        Filter products with any discount.

        Returns:
            QuerySet: Products with discount_percentage > 0

        Usage:
            sale_products = Product.objects.on_sale()
        """
        return self.filter(discount_percentage__gt=0)

    def heavily_discounted(self, min_discount=30):
        """
        Filter products with significant discount.

        Args:
            min_discount (int): Minimum discount percentage (default: 30)

        Returns:
            QuerySet: Products with discount_percentage >= min_discount

        Usage:
            clearance = Product.objects.heavily_discounted(50)
        """
        return self.filter(discount_percentage__gte=min_discount)

    def final_price_less_than(self, max_final_price):
        """
        Filter products by final price after discount.

        Args:
            max_final_price (Decimal): Maximum final price

        Returns:
            QuerySet: Products where price * (1 - discount/100) <= max_final_price

        Usage:
            affordable = Product.objects.final_price_less_than(30)
        """
        # Note: This uses a SQL expression for calculated fields
        from django.db.models import F, ExpressionWrapper, fields
        from django.db.models.functions import Round

        final_price = ExpressionWrapper(
            F("price") * (1 - F("discount_percentage") / 100),
            output_field=fields.DecimalField(),
        )

        return self.annotate(final_price=Round(final_price, 2)).filter(
            final_price__lte=max_final_price
        )

    # ------------------------------------------------------------------------
    # Category & Relationship Filters
    # ------------------------------------------------------------------------

    def by_category(self, category_slug):
        """
        Filter products by category slug.

        Args:
            category_slug (str): Category slug

        Returns:
            QuerySet: Products in the specified category

        Usage:
            electronics = Product.objects.by_category('electronics')
        """
        return self.filter(category__slug=category_slug)

    def by_brand(self, brand_slug):
        """
        Filter products by brand slug.

        Args:
            brand_slug (str): Brand slug

        Returns:
            QuerySet: Products in the specified brand

        Usage:
            nike_products = Product.objects.by_brand('nike')
        """
        return self.filter(brand__slug=brand_slug)

    def by_category_and_active(self, category_slug):
        """
        Filter active products by category slug.

        Combines active() and by_category() for convenience.

        Args:
            category_slug (str): Category slug

        Returns:
            QuerySet: Active products in the specified category

        Usage:
            active_electronics = Product.objects.by_category_and_active('electronics')
        """
        return self.active().by_category(category_slug)

    def with_images(self):
        """
        Filter products that have at least one image.

        Returns:
            QuerySet: Products with images

        Usage:
            products_with_images = Product.objects.with_images()
        """
        return self.annotate(image_count=Count("images")).filter(image_count__gt=0)

    def with_reviews(self):
        """
        Filter products that have at least one review.

        Returns:
            QuerySet: Products with reviews

        Usage:
            reviewed_products = Product.objects.with_reviews()
        """
        return self.annotate(review_count=Count("reviews")).filter(review_count__gt=0)

    # ------------------------------------------------------------------------
    # Search & Discovery Filters
    # ------------------------------------------------------------------------

    def search(self, query):
        """
        Advanced product search with relevance scoring.

        Searches in:
        - Product name (highest weight: 3)
        - Product description (medium weight: 1)
        - Category name (medium weight: 1)
        - Brand name (medium weight: 1)

        Only returns active products.

        Args:
            query (str): Search query

        Returns:
            QuerySet: Search results ordered by relevance

        Usage:
            results = Product.objects.search('laptop')
        """
        if not query or len(query.strip()) < 2:
            return self.none()

        words = query.strip().split()
        q_objects = Q()

        for word in words:
            q_objects |= (
                Q(name__icontains=word)
                | Q(description__icontains=word)
                | Q(category__name__icontains=word)
                | Q(brand__name__icontains=word)
            )

        # Annotate with relevance score
        return (
            self.active()
            .filter(q_objects)
            .annotate(
                relevance=(
                    Q(name__icontains=query) * 3
                    + Q(description__icontains=query) * 1
                    + Q(category__name__icontains=query) * 1
                    + Q(brand__name__icontains=query) * 1
                )
            )
            .distinct()
            .order_by("-relevance")
        )

    def related_to(self, product, limit=4):
        """
        Find products related to a given product.

        Prioritizes:
        1. Same category (weight: 2)
        2. Same brand (weight: 1)

        Args:
            product (Product): The reference product
            limit (int): Number of related products to return

        Returns:
            QuerySet: Related products excluding the reference product

        Usage:
            related = Product.objects.related_to(product)
        """
        return (
            self.active()
            .exclude(id=product.id)
            .filter(Q(category=product.category) | Q(brand=product.brand))
            .annotate(
                match_score=(
                    Q(category=product.category) * 2 + Q(brand=product.brand) * 1
                )
            )
            .order_by("-match_score", "-created_at")[:limit]
        )

    def recommended_for_user(self, user, limit=6):
        """
        Get personalized product recommendations for a user.

        Algorithm:
        1. Find categories user has purchased from
        2. Find products user has already bought
        3. Recommend active products from those categories
        4. Exclude already purchased products
        5. Order by popularity

        Args:
            user (User): The user to recommend for
            limit (int): Number of recommendations

        Returns:
            QuerySet: Recommended products

        Usage:
            recommendations = Product.objects.recommended_for_user(request.user)
        """
        # Get categories user has purchased from
        purchased_categories = (
            user.orders.filter(status="delivered")
            .values_list("items__product__category", flat=True)
            .distinct()
        )

        # Get products user has already bought
        purchased_product_ids = user.orders.filter(status="delivered").values_list(
            "items__product__id", flat=True
        )

        if not purchased_categories:
            # Fallback: Return popular products
            return self.popular_by_sales(limit)

        return (
            self.active()
            .filter(category__in=purchased_categories)
            .exclude(id__in=purchased_product_ids)
            .annotate(popularity=Count("order_items"))
            .order_by("-popularity")[:limit]
        )

    # ------------------------------------------------------------------------
    # Analytics & Popularity Filters
    # ------------------------------------------------------------------------

    def popular_by_sales(self, limit=10):
        """
        Get most popular products by total sales.

        Args:
            limit (int): Number of products to return

        Returns:
            QuerySet: Top selling products

        Usage:
            best_sellers = Product.objects.popular_by_sales(limit=5)
        """
        return (
            self.active()
            .annotate(total_sold=Sum("order_items__quantity"))
            .order_by("-total_sold")[:limit]
        )

    def popular_by_views(self, limit=10):
        """
        Get most viewed products.

        Args:
            limit (int): Number of products to return

        Returns:
            QuerySet: Most viewed products

        Usage:
            trending_products = Product.objects.popular_by_views()
        """
        return self.active().order_by("-view_count")[:limit]

    def popular_by_rating(self, min_reviews=5, limit=10):
        """
        Get highest rated products.

        Args:
            min_reviews (int): Minimum number of reviews required
            limit (int): Number of products to return

        Returns:
            QuerySet: Highest rated products

        Usage:
            top_rated = Product.objects.popular_by_rating()
        """
        return (
            self.active()
            .annotate(avg_rating=Avg("reviews__rating"), review_count=Count("reviews"))
            .filter(review_count__gte=min_reviews)
            .order_by("-avg_rating")[:limit]
        )

    def trending(self, days=7, limit=10):
        """
        Get trending products from the last N days.

        Trending is determined by:
        - Recent sales volume
        - Number of unique buyers

        Args:
            days (int): Number of days to look back
            limit (int): Number of products to return

        Returns:
            QuerySet: Trending products

        Usage:
            trending_now = Product.objects.trending(days=3)
        """
        cutoff = timezone.now() - timedelta(days=days)

        return (
            self.active()
            .filter(order_items__created_at__gte=cutoff)
            .annotate(
                recent_sales=Sum("order_items__quantity"),
                unique_buyers=Count("order_items__order__user", distinct=True),
            )
            .filter(recent_sales__gt=0)
            .order_by("-recent_sales", "-unique_buyers")[:limit]
        )

    def flash_sale_eligible(self):
        """
        Get products eligible for flash sale.

        Criteria:
        - Active products
        - Stock > 20
        - Price <= 499

        Returns:
            QuerySet: Flash sale eligible products

        Usage:
            flash_sale = Product.objects.flash_sale_eligible()
        """
        return self.active().filter(stock__gt=20, price__lte=499).order_by("price")

    # ------------------------------------------------------------------------
    # Admin & Dashboard Queries
    # ------------------------------------------------------------------------

    def get_stats(self):
        """
        Get comprehensive product statistics for admin dashboard.

        Returns:
            dict: Dictionary containing all product statistics

        Usage:
            stats = Product.objects.get_stats()
        """
        from django.db.models import Sum, Avg, Min, Max

        return {
            "total": self.count(),
            "active": self.active().count(),
            "draft": self.draft().count(),
            "inactive": self.inactive().count(),
            "in_stock": self.in_stock().count(),
            "out_of_stock": self.out_of_stock().count(),
            "low_stock": self.low_stock(threshold=5).count(),
            "on_sale": self.on_sale().count(),
            "total_stock": self.aggregate(total=Sum("stock"))["total"] or 0,
            "average_price": self.aggregate(avg=Avg("price"))["avg"] or 0,
            "total_value": self.aggregate(total=Sum("price"))["total"] or 0,
            "price_range": {
                "min": self.aggregate(min=Min("price"))["min"] or 0,
                "max": self.aggregate(max=Max("price"))["max"] or 0,
            },
            "by_status": self.values("status").annotate(
                count=Count("id"), avg_price=Avg("price"), total_stock=Sum("stock")
            ),
            "top_categories": self.values("category__name")
            .annotate(product_count=Count("id"))
            .order_by("-product_count")[:5],
        }


# ============================================================================
# ProductManager - Entry Point for Queries
# ============================================================================


class ProductManager(models.Manager):
    """
    Custom Manager for Product model.

    This manager serves as the entry point for all Product queries.
    It forwards all methods to the custom ProductQuerySet for chainability.

    Usage:
        Product.objects.active()
        Product.objects.in_stock()
        Product.objects.best_sellers(limit=5)
    """

    def get_queryset(self):
        """
        Override get_queryset to use custom ProductQuerySet.

        Returns:
            ProductQuerySet: Custom QuerySet with all chainable methods

        This is the key to making custom methods chainable.
        """
        return ProductQuerySet(self.model, using=self._db)

    # ------------------------------------------------------------------------
    # Status & Availability
    # ------------------------------------------------------------------------

    def active(self):
        """Get active products available for purchase."""
        return self.get_queryset().active()

    def in_stock(self):
        """Get products with stock available."""
        return self.get_queryset().in_stock()

    def out_of_stock(self):
        """Get products with zero stock."""
        return self.get_queryset().out_of_stock()

    def low_stock(self, threshold=5):
        """Get products with stock below threshold."""
        return self.get_queryset().low_stock(threshold)

    def draft(self):
        """Get products in draft status."""
        return self.get_queryset().draft()

    def inactive(self):
        """Get products in inactive status."""
        return self.get_queryset().inactive()

    # ------------------------------------------------------------------------
    # Pricing & Discount
    # ------------------------------------------------------------------------

    def price_between(self, min_price, max_price):
        """Get products within a price range."""
        return self.get_queryset().price_between(min_price, max_price)

    def price_less_than(self, max_price):
        """Get products with price less than or equal to max_price."""
        return self.get_queryset().price_less_than(max_price)

    def price_greater_than(self, min_price):
        """Get products with price greater than or equal to min_price."""
        return self.get_queryset().price_greater_than(min_price)

    def on_sale(self):
        """Get products with any discount."""
        return self.get_queryset().on_sale()

    def heavily_discounted(self, min_discount=30):
        """Get products with significant discount."""
        return self.get_queryset().heavily_discounted(min_discount)

    def final_price_less_than(self, max_final_price):
        """Get products by final price after discount."""
        return self.get_queryset().final_price_less_than(max_final_price)

    # ------------------------------------------------------------------------
    # Category & Relationships
    # ------------------------------------------------------------------------

    def by_category(self, category_slug):
        """Get products by category slug."""
        return self.get_queryset().by_category(category_slug)

    def by_brand(self, brand_slug):
        """Get products by brand slug."""
        return self.get_queryset().by_brand(brand_slug)

    def by_category_and_active(self, category_slug):
        """Get active products by category slug."""
        return self.get_queryset().by_category_and_active(category_slug)

    def with_images(self):
        """Get products that have at least one image."""
        return self.get_queryset().with_images()

    def with_reviews(self):
        """Get products that have at least one review."""
        return self.get_queryset().with_reviews()

    # ------------------------------------------------------------------------
    # Search & Discovery
    # ------------------------------------------------------------------------

    def search(self, query):
        """Advanced product search with relevance scoring."""
        return self.get_queryset().search(query)

    def related_to(self, product, limit=4):
        """Find products related to a given product."""
        return self.get_queryset().related_to(product, limit)

    def recommended_for_user(self, user, limit=6):
        """Get personalized product recommendations."""
        return self.get_queryset().recommended_for_user(user, limit)

    # ------------------------------------------------------------------------
    # Analytics & Popularity
    # ------------------------------------------------------------------------

    def best_sellers(self, limit=10):
        """Get most popular products by total sales."""
        return self.get_queryset().popular_by_sales(limit)

    def most_viewed(self, limit=10):
        """Get most viewed products."""
        return self.get_queryset().popular_by_views(limit)

    def top_rated(self, min_reviews=5, limit=10):
        """Get highest rated products."""
        return self.get_queryset().popular_by_rating(min_reviews, limit)

    def trending(self, days=7, limit=10):
        """Get trending products from the last N days."""
        return self.get_queryset().trending(days, limit)

    def flash_sale_eligible(self):
        """Get products eligible for flash sale."""
        return self.get_queryset().flash_sale_eligible()

    # ------------------------------------------------------------------------
    # Admin & Dashboard
    # ------------------------------------------------------------------------

    def get_stats(self):
        """Get comprehensive product statistics for admin dashboard."""
        return self.get_queryset().get_stats()
