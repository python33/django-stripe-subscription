import re

from django import forms
from django.core.exceptions import ValidationError

from .models import Plan


class SubscribeForm(forms.Form):
    stripe_token = forms.CharField(max_length=255)
    plan = forms.ModelChoiceField(queryset=Plan.objects.list_published())

    def clean_stripe_token(self):
        data = self.cleaned_data['stripe_token']

        if not re.match('tok_[0-9a-zA-Z]+', data):
            raise ValidationError('Token format validation failed')

        return data
