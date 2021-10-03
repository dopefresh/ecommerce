from django.conf import settings
from django.db import models
from django.db.models.signals import post_save, pre_save
from django.dispatch.dispatcher import receiver
from django.utils.text import slugify
from django.utils.translation import ugettext_lazy as _
from PIL import Image

from shop import tasks

import uuid
from loguru import logger


def company_logo_directory(instance, filename):
    return f'logos/{filename}'


def company_product_directory(instance, filename):
    return f'products/{filename}'


def category_directory(instance, filename):
    return f'categories/{filename}'


def subcategory_directory(instance, filename):
    return f'subcategories/{filename}'


class Company(models.Model):
    name = models.CharField(
        _('Company name'),
        max_length=500, unique=True
    )
    location = models.CharField(
        _('Company location'),
        max_length=500)
    phone_number = models.CharField(
        _('Company phone number'),
        max_length=30, blank=False, null=False)
    logo = models.ImageField(
        _('Company logo'),
        upload_to=company_logo_directory,
        blank=True,
        null=True)

    class Meta:
        db_table = 'company'
        verbose_name = _('Company')
        verbose_name_plural = _('Companies')

    def __str__(self):
        return f'Company name: {self.name}\n{self.phone_number}\n{self.location}'

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        tasks.save_company_image.delay(self.pk)


class Employee(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    company = models.ForeignKey(
        'Company',
        on_delete=models.SET_NULL,
        blank=True, null=True,
        related_name='employees',
        verbose_name=_('company'),
        db_index=True
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


class Category(models.Model):
    """
    Category of Product in ecommerce site
    """
    slug = models.SlugField(blank=True)
    title = models.CharField(
        _('Category name'),
        max_length=100, unique=True)
    image = models.ImageField(
        _('Category image'),
        upload_to=category_directory,
        blank=True,
        null=True)

    class Meta:
        db_table = 'category'
        verbose_name = _('Category')
        verbose_name_plural = _("Categories")

    def __str__(self) -> str:
        return self.title

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        super().save(*args, **kwargs)
        tasks.save_category_image.delay(self.pk)


class Subcategory(models.Model):
    """
    Subcategory of Product in ecommerce site
    """
    slug = models.SlugField(blank=True)
    title = models.CharField(
        _('Subcategory name'),
        max_length=100, unique=True)
    category = models.ForeignKey('Category',
                                 on_delete=models.CASCADE,
                                 related_name='subcategories',
                                 verbose_name=_('category'),
                                 db_index=True)
    image = models.ImageField(
        _('Subcategory image'),
        upload_to=subcategory_directory,
        blank=True,
        null=True)

    class Meta:
        db_table = 'subcategory'
        verbose_name = _('Subcategory')
        verbose_name_plural = _('Subcategories')

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        super().save(*args, **kwargs)
        tasks.save_subcategory_image.delay(self.pk)


class Item(models.Model):
    """
    Product in ecommerce site
    """
    title = models.CharField(
        _('Product title'),
        max_length=255,
        blank=False, null=False,
        unique=True)
    description = models.TextField(
        _('Product description'),
        blank=True, null=True)
    price = models.IntegerField(
        _('Product price'),
        blank=False, null=False)
    image_href = models.CharField(
        _('Product image href'),
        blank=True, null=True,
        max_length=500
    )
    slug = models.SlugField(blank=True, max_length=255)
    subcategory = models.ForeignKey(
        'Subcategory',
        on_delete=models.SET_NULL,
        null=True,
        related_name='items',
        verbose_name=_('subcategory'),
        db_index=True
    )
    company = models.ForeignKey(
        'Company',
        on_delete=models.SET_NULL,
        null=True,
        verbose_name=_('company'),
        db_index=True
    )

    class Meta:
        db_table = 'item'
        verbose_name = _('Product')
        verbose_name_plural = _('Products')

    def __str__(self):
        return f'{self.title} {self.price}'

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        super().save(*args, **kwargs)
        tasks.save_item_image.delay(self.pk)


class OrderItem(models.Model):
    """
    User's items in his order
    """
    quantity = models.IntegerField(
        _('Quantity of item in order'),
        default=1)
    item = models.ForeignKey(
        'Item', on_delete=models.CASCADE,
        verbose_name=_('item'),
        db_index=True
    )
    order = models.ForeignKey('Order',
                              related_name='order_items',
                              on_delete=models.CASCADE,
                              verbose_name=_('order'),
                              db_index=True)

    class Meta:
        db_table = 'order_item'
        verbose_name = _("Item in user order")
        verbose_name_plural = _("Items in user order")
        unique_together = (
            'item',
            'order',
        )
        ordering = ('item__title',)

    def __str__(self):
        return f"{self.item}: {self.quantity}"


class Order(models.Model):
    """
    User's order object
    """
    ordered = models.BooleanField(
        _('Is it ordered by user'),
        default=False)
    shipped = models.BooleanField(
        _('Is order shipped'),
        default=False)
    ordered_date = models.DateField(
        _("Date when ordered"),
        blank=True, null=True)

    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    amount = models.IntegerField(blank=True, null=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE,
                             related_name='orders',
                             verbose_name=_('user'),
                             db_index=True)

    class Meta:
        db_table = 'order'
        verbose_name = _("User's cart")
        verbose_name_plural = _("User's Carts")

    def __str__(self):
        return str(self.user)

    def get_total_price(self):
        return sum([
            order_item.quantity * order_item.item.price
            for order_item in self.order_items.all()
        ])


class Step(models.Model):
    """
    Steps, that's order is taking before getting to user
    1. Payment
    2. Packaging
    3. Transportation
    4. Delivery in user's city
    """
    name_step = models.CharField(
        _('Step name'),
        max_length=50, default='Оплата'
    )

    class Meta:
        verbose_name = _("Step")
        verbose_name_plural = _("Steps")

    def __str__(self):
        return self.name_step


class OrderStep(models.Model):
    step = models.ForeignKey(
        'Step', on_delete=models.CASCADE,
        verbose_name=_('step'),
        db_index=True
    )
    order = models.ForeignKey(
        'Order',
        on_delete=models.CASCADE,
        verbose_name=_('order'),
        related_name='order_steps',
        db_index=True
    )
    date_step_begin = models.DateTimeField(
        _('Date step began'),
        null=True
    )
    date_step_end = models.DateTimeField(
        _('Date step ended'),
        null=True)

    class Meta:
        verbose_name = _("Order's Step")
        verbose_name_plural = _("Order's Steps")
