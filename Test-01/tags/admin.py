from django.contrib import admin

from . import models

# Register your models here.

class TagAdmin(admin.ModelAdmin):
    search_fields = ['label']

    list_per_page = 10

admin.site.register(models.Tag, TagAdmin)
