from django.contrib import admin

from . import models


@admin.register(models.Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display = ('title', 'price_id', 'product_id', 'price')

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = ['price_id', 'product_id']

        if obj and obj.id:
            readonly_fields += ['price', 'recurring_interval']

        return readonly_fields
