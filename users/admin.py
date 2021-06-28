from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from users.models import WishList
from utilities.admin import BaseAdmin

User = get_user_model()


@admin.register(User)
class UserAdmin(BaseAdmin, UserAdmin):
    list_display = [
        'username',
        'email',
        'is_superuser',
        'is_staff',
        'is_active',
        'role',
        'last_order_date',
        'first_order_date',
        'average_order_value',
        'manage_buttons',
    ]
    search_fields = [
        'username',
        'first_name',
        'last_name',
        'email',
    ]

    def get_list_filter(self, obj):
        list_filter = list(super(UserAdmin, self).get_list_filter(obj))
        list_filter.append('role')
        return list_filter

    fieldsets = (
        (_('Personal info'), {'fields': (
            'username', 'password', 'email', 'first_name', 'last_name', 'role',)}),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = ((None, {
        'classes': ('wide',),
        'fields': (
            'username', 'password', 'email', 'first_name', 'last_name', 'role',
        ),
    }),)


@admin.register(WishList)
class WishListAdmin(BaseAdmin):
    list_display = [
        'user',
        'product',
    ]
    search_fields = [
        'user__username',
        'product__name',
    ]
