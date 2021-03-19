from django.contrib import admin

from . import models


@admin.register(models.Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display = ('title', 'price_id', 'product_id', 'price', 'published')
    list_filter = ('published',)

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = ['price_id', 'product_id']

        if obj and obj.id:
            readonly_fields += ['price', 'recurring_interval']

        return readonly_fields


@admin.register(models.Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    readonly_fields = (
            'created_at', 'updated_at', 'user',
            'plan', 'customer_id', 'subscription_id', 'quiz')
    list_display = ('user', 'created_at', 'updated_at',
                    'customer_id', 'subscription_id', 'is_active')
    list_filter = ('is_active', 'created_at')
    fieldsets = (
        (None, {
            "fields": ('user', 'is_active', 'created_at', 'updated_at')
        }),
        ('Stripe', {
            "fields": ('plan', 'customer_id', 'subscription_id')
        }),
        ('Quiz', {
            "fields": ('quiz',)
        })
    )

