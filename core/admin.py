from django.contrib import admin
from core.models import Product, Order
from utilities.admin import BaseAdmin


@admin.register(Product)
class ProductAdmin(BaseAdmin):
    list_display = [
        'name',
        'price',
        'inventory',
        'created_at',
        'modified_at',
        'manage_buttons',
    ]
    search_fields = [
        'name',
    ]


@admin.register(Order)
class OrderAdmin(BaseAdmin):
    list_display = [
        'user',
        'product',
        'quantity',
        'total_amount',
    ]

    search_fields = [
        'user__username',
        'product__name',
    ]
