from django.http import JsonResponse
from django.middleware.csrf import get_token
from django.contrib.auth.decorators import login_required

from .models import Plan, Subscription
from .forms import SubscribeForm


def session(request):
    """
    Returns current user session.
    """

    if request.user and request.user.is_authenticated:
        qs = Plan.objects.list_published()

        return JsonResponse({
            "status": "ok",
            "session": {
                "csrf_token": get_token(request),
                "user": request.user.email,
                "plans": [
                    {'id': p.id, 'title': p.title, 'price': p.price}
                    for p in qs
                ]
            }
        })

    return JsonResponse({"status": "error"}, status=400)


@login_required
def subscribe(request):
    """
    Creates new subscription for current user with payment token and plan.
    """

    if request.method == "POST":
        form = SubscribeForm(request.POST)

        if form.is_valid():
            token = form.cleaned_data['stripe_token']
            plan = form.cleaned_data['plan']

            sub = Subscription.create_from_token(
                    token,
                    plan,
                    request.user)

            if sub:
                return JsonResponse({"status": "ok"})
        else:
            return JsonResponse(
                    {"status": "error", "errors": form.errors},
                    status=400)

    return JsonResponse({"status": "error"}, status=400)
