from django.contrib import admin

from . import models


@admin.register(models.Plan)
class PlanAdmin(admin.ModelAdmin):
    readonly_fields = ('price_id', 'product_id')
    list_display = ('title', 'price_id', 'product_id', 'price')
