from datetime import datetime, timedelta

from django.conf import settings

import stripe
stripe.api_key = settings.STRIPE_SECRET_KEY


def get_product(plan):
    """
    Returns stripe product id for given plan.
    :param plan: billing.models.Plan
    """

    if not plan.product_id:
        product = stripe.Product.create(
                name=plan.title)
        plan.product_id = product.id

    return plan.product_id


def create_price_on_stripe(plan):
    """
    Creates stripe.Price object via SDK.
    :param plan: billing.models.Plan
    """

    price = stripe.Price.create(
        unit_amount=int(plan.price * 100),
        currency="usd",
        product=get_product(plan),
        recurring={"interval": plan.recurring_interval})

    plan.price_id = price.id


def update_price_on_stripe(plan):
    """
    Removes stripe.Price object via SDK.
    :param plan: billing.models.Plan
    """
    stripe.Price.modify(
        plan.price_id,
        unit_amount=int(plan.price * 100),
        recurring={"interval": plan.recurring_interval})


def get_trial_end(days=3):
    """
    Returns trial end timestamp.
    :param days: Trial period
    :returns int: Trial end timestamp
    """
    trial_end = datetime.now() + timedelta(days=days)
    return int(trial_end.timestamp())
