from django.urls import path
from store.views.product import ProductListCreateView, ProductDetailView

urlpatterns = [
    path("products/", ProductListCreateView.as_view()),
    path("product/<uuid:pk>/", ProductListCreateView.as_view()),
]
