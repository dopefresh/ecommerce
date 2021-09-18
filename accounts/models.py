from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from .managers import CustomUserManager
from shop.models import Company


def company_logo_directory(instance, filename):
    return f'{instance.name}/logos/{filename}'


class City(models.Model):
    name = models.CharField(
        _('City name'),
        max_length=40,
        default='Астрахань'
    )
    days_delivery = models.IntegerField(
        _('Delivery days'),
        default=0
    )

    class Meta:
        db_table = 'city'
        verbose_name = _('City available for delivery')
        verbose_name_plural = _("Cities available for delivery")

    def __str__(self):
        return f'{self.name}'


class User(AbstractUser):
    USER_ROLES = (
        ('user', 'user'),
        ('employee', 'employee'),
    )
    role = models.CharField(
        _('User role'),
        choices=USER_ROLES,
        max_length=10
    )
    username = None
    email = models.EmailField(_('email address'), unique=True)
    city = models.ForeignKey(
        City,
        on_delete=models.SET_NULL,
        related_name='users',
        blank=True, null=True
    )
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    objects = CustomUserManager()

    class Meta:
        verbose_name = _('User')
        verbose_name_plural = _('Users')

    def __str__(self):
        return f"{self.username} {self.city}"


class Employee(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    company = models.ForeignKey(
        Company,
        on_delete=models.SET_NULL,
        blank=True, null=True,
        related_name='employees'
    )
    phone_number = models.CharField(
        _('phone number'),
        max_length=25,
        blank=True, null=True
    )
    photo = models.ImageField(
        _('photo'),
        upload_to=company_logo_directory,
        blank=True, null=True
    )

    class Meta:
        db_table = 'employee'
        verbose_name_plural = _('Company employees')
        verbose_name = _("Company employee")

    def __str__(self):
        return f'{self.user}\n{self.company}\n{self.phone_number}'
