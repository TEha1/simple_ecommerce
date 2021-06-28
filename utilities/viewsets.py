from django_filters.rest_framework import FilterSet, BooleanFilter
from drf_yasg import openapi

from core.models import Product
from users.models import WishList


class ProductFilterClass(FilterSet):
    wishlist = BooleanFilter(method='filter_wishlist')

    class Meta:
        model = Product
        fields = []

    def filter_wishlist(self, queryset, name, value):
        if value:
            if self.request.user.is_authenticated:
                queryset = queryset.filter(
                    pk__in=WishList.objects.filter(user=self.request.user).values_list('product_id', flat=True)
                )
        return queryset


product_field_expand = [
    openapi.Parameter('wishlist', in_=openapi.IN_QUERY,
                      description="Filter the returned products list with the authentication user wishes.",
                      type=openapi.TYPE_BOOLEAN),
    openapi.Parameter('ordering', in_=openapi.IN_QUERY, enum=['created_at', '-created_at', ],
                      description="Ordering the returned products list.",
                      type=openapi.TYPE_STRING),
    openapi.Parameter('page_size', in_=openapi.IN_QUERY, required=True, default=20,
                      description="Number of results to return per page.",
                      type=openapi.TYPE_INTEGER),
]
