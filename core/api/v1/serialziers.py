from django.core.exceptions import ValidationError
from django_restql.mixins import DynamicFieldsMixin
from rest_framework import serializers

from core.models import Product, Order


class ProductSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = [
            'id',
            'name',
            'price',
            'inventory',
        ]


class OrderSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = [
            'id',
            'user',
            'product',
            'quantity',
            'total_amount',
            'created_at',
        ]
        extra_kwargs = {
            'user': {'read_only': True, },
        }

    def create(self, validated_data):
        user = self.context.get('request').user
        validated_data['user'] = user
        try:
            return super(OrderSerializer, self).create(validated_data)
        except ValidationError as errors:
            raise serializers.ValidationError(dict(errors))

    def to_representation(self, order):
        data = super(OrderSerializer, self).to_representation(order)
        from users.api.v1.serializers import UserSerializer
        data['user'] = UserSerializer(
            order.user,
            context=self.context,
        ).data
        data['product'] = ProductSerializer(
            order.product,
            context=self.context,
        ).data
        return data
