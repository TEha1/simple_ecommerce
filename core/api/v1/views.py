from django.utils.translation import gettext_lazy as _
from django.utils.decorators import method_decorator
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from drf_yasg.utils import swagger_auto_schema
from core.api.v1.serialziers import ProductSerializer, OrderSerializer
from core.models import Product, Order
from utilities.viewsets import product_field_expand, ProductFilterClass


@method_decorator(name='list', decorator=swagger_auto_schema(manual_parameters=product_field_expand))
class ProductResource(ModelViewSet):
    http_method_names = ['get', ]
    serializer_class = ProductSerializer
    queryset = Product.objects.all()
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter, ]
    filterset_fields = [
        'wishlist',
    ]
    filter_class = ProductFilterClass
    search_fields = [
        'name',
    ]
    ordering_fields = [
        'created_at',
    ]

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            self.permission_classes = []
            self.authentication_classes = []
        return super(ProductResource, self).get_permissions()

    @action(methods=['get', ], detail=True, url_path='wish-dislike', url_name='wish_dislike')
    def user_wish_dislike(self, request, pk):
        product = self.get_object()
        wished = product.wish_dislike(user_id=self.request.user.id)

        if wished:
            message = _("product wished")
        else:
            message = _("product disliked")

        return Response(
            {
                "details": message,
            },
            status=status.HTTP_200_OK,
        )


class OrderResource(ModelViewSet):
    http_method_names = ['post', 'get', ]
    serializer_class = OrderSerializer
    filter_backends = [DjangoFilterBackend, ]
    filterset_fields = ['product', ]

    def get_queryset(self):
        return Order.objects.filter(user_id=self.request.user.id).order_by('-created_at')
