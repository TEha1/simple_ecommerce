from django.urls import path, include
from rest_framework.routers import DefaultRouter

from core.api.v1.views import ProductResource, OrderResource

app_name = 'core'

router = DefaultRouter()
router.register(r'products', ProductResource, basename='products')
router.register(r'orders', OrderResource, basename='orders')

urlpatterns = [
    path('', include(router.urls)),
]
