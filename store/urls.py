from django.urls import path
from store.views.product import ProductListCreateView, ProductDetailView

# store/urls.py

from store.views.reviews import ReviewListCreateView, ReviewDetailView

urlpatterns = [
    # Product endpoints
    path("products/", ProductListCreateView.as_view(), name="product-list-create"),
    path("products/<uuid:pk>/", ProductDetailView.as_view(), name="product-detail"),
    # Review endpoints — nested under product
    path(
        "products/<uuid:product_pk>/reviews/",
        ReviewListCreateView.as_view(),
        name="review-list-create",
    ),
    path(
        "products/<uuid:product_pk>/reviews/<uuid:pk>/",
        ReviewDetailView.as_view(),
        name="review-detail",
    ),
]
