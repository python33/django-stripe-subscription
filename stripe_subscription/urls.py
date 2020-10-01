from django.urls import path

from . import views


app_name = 'stripe-subscription'

urlpatterns = [
    path('session/', views.session),
    path('subscribe/', views.subscribe)
]
