from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.utils.translation import ugettext_lazy as _
from allauth.account.forms import SignupForm

from .models import User, City

from loguru import logger


class CustomUserCreationForm(SignupForm):
    city = forms.ModelChoiceField(
        queryset=City.objects.all(), label=_('city'),
        widget=forms.Select, empty_label=None,
    )

    class Meta:
        model = User
        fields = ('email', 'password1', 'password2', 'city')

    def save(self, request):
        user = super().save(request)
        return user


class CustomUserChangeForm(UserChangeForm):
    city = forms.ModelChoiceField(
        queryset=City.objects.all(), label='city',
        widget=forms.Select, empty_label=None
    )

    class Meta:
        model = User
        fields = ('email', 'city',)
