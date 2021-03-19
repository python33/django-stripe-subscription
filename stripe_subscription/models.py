from django.db import models
from django.db import transaction
from django.conf import settings
from django.dispatch import receiver
from django.db.models.signals import pre_save
from django.contrib.auth.models import User

from . import utils

import stripe
stripe.api_key = settings.STRIPE_SECRET_KEY


class PlanManager(models.Manager):
    def list_published(self):
        return self.filter(published=True)


class Plan(models.Model):
    RECURRING_INTERVALS = (
        ('week', 'Week'),
        ('month', 'Month'),
        ('year', 'Year')
    )

    # General
    title = models.CharField(max_length=255)
    published = models.BooleanField(default=True)

    # Payment details
    price = models.DecimalField(max_digits=10, decimal_places=2, unique=True)
    recurring_interval = models.CharField(
            choices=RECURRING_INTERVALS,
            max_length=255)
    product_id = models.CharField(max_length=255, null=True, blank=True)
    price_id = models.CharField(max_length=255, null=True, blank=True)

    # Deeplink
    deep_link = models.URLField(max_length=500, null=True, blank=True)

    objects = PlanManager()

    def __str__(self):
        return "<Plan: {}>".format(self.title)


class Subscription(models.Model):
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE)

    # Stripe details
    customer_id = models.CharField(max_length=255, null=True, blank=True)
    subscription_id = models.CharField(max_length=255, null=True, blank=True)

    # Aditional parameters for deep link
    quiz = models.TextField(null=True, blank=True)

    class Meta:
        unique_together = [('user', 'plan')]

    @classmethod
    def create_from_token(cls, token, plan, user, quiz=None):
        """
        Creates new subscription from given token with plan for given user.
        :param token: Paymnet source (starts with pm_)
                      or payment token (starts with tok_)
        :param plan: Selected plan (Plan object)
        :param user: Subscriber
        :param quiz: URL encoded quiz data (user selected options for depp link)
        """

        try:
            obj = cls.objects.get(user=user, plan=plan)
        except cls.DoesNotExist:
            obj = cls(user=user, plan=plan)

        with transaction.atomic():
            if not obj.customer_id:
                customer = stripe.Customer.create(
                        email=user.email,
                        description="User #{}".format(user.id))

                obj.customer_id = customer.id

            kwargs = dict(
                    customer=obj.customer_id,
                    items=[
                        {"price": plan.price_id}
                    ],
                    trial_end=utils.get_trial_end())

            if token.startswith('tok_'):
                token = stripe.Token.retrieve(token)

                source = stripe.Source.create(
                    type=token.type,
                    token=token.id)

                stripe.Customer.create_source(
                    obj.customer_id,
                    source=source.id)
            elif token.startswith('pm_'):
                pm = stripe.PaymentMethod.retrieve(token)
                stripe.PaymentMethod.attach(pm.id, customer=obj.customer_id)
                kwargs['default_payment_method'] = pm.id

            sub = stripe.Subscription.create(**kwargs)
            obj.subscription_id = sub.id

            if quiz:
                obj.quiz = quiz

            obj.save()

        return obj

    @property
    def deep_link(self):
        """
        Returns application deep link (user quiz data will be appended to plan.deep_link).
        """
        plan = self.plan

        if not plan.deep_link:
            return None

        parts = [plan.deep_link]

        if self.quiz:
            parts.append(self.quiz)

        glue = '?'

        if glue in plan.deep_link:
            glue = '&'

        return glue.join(parts)

    def __str__(self):
        return "<Subscription: {}>".format(self.subscription_id)


@receiver(pre_save, sender=Plan)
def plan_pre_save(sender, instance, **kwargs):
    if not instance.price_id:
        utils.create_price_on_stripe(instance)
    else:
        utils.update_price_on_stripe(instance)
