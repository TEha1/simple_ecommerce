from decimal import Decimal
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import Sum, F, DecimalField
from django.utils.translation import gettext_lazy as _

from utilities.models import BaseModel


class User(AbstractUser):
    ADMIN = 1
    CUSTOMER = 2

    ROLE_CHOICES = (
        (ADMIN, "admin"),
        (CUSTOMER, "customer"),
    )

    username = models.CharField(
        max_length=100,
        unique=True,
        error_messages={
            'unique': _("This user already registered."),
        },
        verbose_name=_('username'),
    )
    email = models.EmailField(
        blank=True,
        null=True,
        verbose_name=_('email address')
    )
    role = models.PositiveSmallIntegerField(
        choices=ROLE_CHOICES,
        default=CUSTOMER,
        verbose_name=_("role")
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("created at")
    )
    modified_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_("modified at")
    )

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["email", ]

    def save(self, *args, **kwargs):
        if self.pk is None:
            if self.is_superuser or self.is_staff:
                self.role = self.ADMIN
        return super(User, self).save()

    @property
    def last_order_date(self):
        order = self.user_orders.last()
        return order.created_at if order else None

    @property
    def first_order_date(self):
        order = self.user_orders.first()
        return order.created_at if order else None

    @property
    def average_order_value(self):
        orders = self.user_orders.all()
        total = orders.aggregate(
            total=Sum((F('quantity') * F('product__price')), output_field=DecimalField())
        )['total']
        return Decimal(total / orders.count()) if total else None

    @property
    def wish_list_count(self):
        return self.user_wish_lists.count()


class WishList(BaseModel):
    product = models.ForeignKey(
        "core.Product",
        on_delete=models.CASCADE,
        related_name="product_wish_lists",
        verbose_name=_("product")
    )
    user = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
        related_name="user_wish_lists",
        verbose_name=_("customer")
    )

    class Meta:
        verbose_name = _("Wish List")
        verbose_name_plural = _("Wish Lists")

    def __str__(self):
        return f'{self.user} - {self.product}'
