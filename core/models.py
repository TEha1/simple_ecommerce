from decimal import Decimal
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models, transaction
from django.utils.translation import gettext_lazy as _

from users.models import WishList
from utilities.models import BaseModel


class Product(BaseModel):
    name = models.CharField(
        max_length=500,
        verbose_name=_("name")
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0.0), ],
        verbose_name=_("price")
    )
    inventory = models.PositiveIntegerField(
        help_text=_("the currently available quantity of the product in the store."),
        verbose_name=_("inventory")
    )

    class Meta:
        verbose_name = _("product")
        verbose_name_plural = _("products")
        ordering = ['-created_at', ]
        indexes = [
            models.Index(fields=['name', ]),
        ]

    def __str__(self):
        return f'{self.name}'

    def wish_dislike(self, user_id):
        likes = WishList.objects.filter(product_id=self.id, user_id=user_id)
        if likes.exists():
            likes.delete()
            return False
        else:
            WishList.objects.create(product_id=self.id, user_id=user_id)
            return True


class Order(BaseModel):
    user = models.ForeignKey(
        "users.User",
        on_delete=models.PROTECT,
        related_name="user_orders",
        verbose_name=_("user")
    )
    product = models.ForeignKey(
        "core.Product",
        on_delete=models.PROTECT,
        related_name="product_orders",
        verbose_name=_("product")
    )
    quantity = models.PositiveIntegerField(
        validators=[MinValueValidator(1), ],
        verbose_name=_("quantity")
    )

    class Meta:
        verbose_name = _("order")
        verbose_name_plural = _("orders")

    def __str__(self):
        return f'{self.product} - {self.quantity}'

    def clean(self):
        total_amount = Decimal(self.quantity * self.product.price)
        if total_amount > 1000:
            raise ValidationError({'quantity': _("Sorry, the maximum amount for one order is 1,000 USD.")})
        if self.quantity > self.product.inventory:
            raise ValidationError({
                'quantity': _('sorry, the remaining quantity of that product only %(inventory)s.') % {
                    'inventory': self.product.inventory, }
            })

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        self.full_clean()
        if self.pk is None:
            self.deduct_product_availability()
        return super(Order, self).save(force_insert=force_insert, force_update=force_update, using=using,
                                       update_fields=update_fields)

    def deduct_product_availability(self):
        product = Product.objects.select_for_update().filter(pk=self.product.pk).first()
        with transaction.atomic():
            product.inventory -= self.quantity
            product.save()

    @property
    def total_amount(self):
        return Decimal(self.product.price * self.quantity)
