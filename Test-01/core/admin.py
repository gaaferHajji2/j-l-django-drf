from django.contrib import admin

from django.contrib.contenttypes.admin import GenericTabularInline

from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from core.models import User
from store.admin import ProductAdmin

from store.models import Product

from tags.models import TaggedItem

class UserAdmin(BaseUserAdmin):
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("username", "usable_password", "password1", "password2", "email", "first_name", "last_name"),
            },
        ),
    )

# Register your models here.
class TagInline(GenericTabularInline):
    model = TaggedItem

    min_num = 1

    max_num = 10

    extra = 0

    autocomplete_fields = ['tag']

class CustomProductAdmin(ProductAdmin):
    inlines = [ TagInline ]

admin.site.unregister(Product)

admin.site.register(Product, CustomProductAdmin)

admin.site.register(User, UserAdmin)