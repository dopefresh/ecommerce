from django.conf import settings
from django.db import models
from django.utils.text import slugify
from django.utils.translation import ugettext_lazy as _
from PIL import Image

from loguru import logger

from shop import tasks


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


class SubCategory(models.Model):
    """
    Subcategory of Product in ecommerce site
    """
    slug = models.SlugField(blank=True)
    title = models.CharField(
        _('Subcategory name'),
        max_length=100, unique=True)
    category = models.ForeignKey('Category',
                                 on_delete=models.CASCADE,
                                 related_name='sub_categories',
                                 verbose_name=_('category'))
    image = models.ImageField(
        _('Subcategory image'),
        upload_to=subcategory_directory,
        blank=True,
        null=True)

    class Meta:
        db_table = 'sub_category'
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
        max_length=100,
        blank=False,
        null=False,
        unique=True)
    description = models.TextField(
        _('Product description'),
        blank=True, null=True)
    price = models.IntegerField(
        _('Product price'),
        blank=False, null=False)
    image = models.ImageField(
        _('Product image'),
        upload_to=company_product_directory,
        blank=True,
        null=True)

    slug = models.SlugField(blank=True)
    sub_category = models.ForeignKey('SubCategory',
                                     on_delete=models.SET_NULL,
                                     null=True,
                                     related_name='items',
                                     verbose_name=_('category'))
    company = models.ForeignKey('Company',
                                on_delete=models.SET_NULL,
                                null=True,
                                verbose_name=_('company'))

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
    User items in his order
    """
    quantity = models.IntegerField(
        _('Quantity of item in order'),
        default=1)
    item = models.ForeignKey(
        'Item', on_delete=models.CASCADE, verbose_name=_('item'))
    order = models.ForeignKey('Order',
                              related_name='order_items',
                              on_delete=models.CASCADE,
                              verbose_name=_('order'))

    class Meta:
        db_table = 'order_item'
        verbose_name = "Item in user order"
        verbose_name_plural = "Items in user order"
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
    ordered_date = models.DateTimeField(
        _("Date when ordered"),
        blank=True, null=True)

    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE,
                             related_name='orders',
                             verbose_name=_('user'))

    class Meta:
        db_table = 'order'
        verbose_name = "User's cart"
        verbose_name_plural = "User's Carts"

    def __str__(self):
        return str(self.user)

    def get_total_price(self):
        return sum([order_item.quantity * order_item.item.price
                    for order_item in self.order_items.all()])


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
    orders = models.ManyToManyField(Order,
                                    related_name='steps',
                                    through='OrderStep')

    class Meta:
        verbose_name = "Step"
        verbose_name_plural = "Steps"


class OrderStep(models.Model):
    step = models.ForeignKey(
        'Step', on_delete=models.CASCADE,
        verbose_name=_('step')
    )
    order = models.ForeignKey(
        'Order', on_delete=models.CASCADE, verbose_name=_('order'))
    date_step_begin = models.DateField(
        _('Date step began'),
        null=True
    )
    date_step_end = models.DateField(
        _('Date step ended'),
        null=True)

    class Meta:
        verbose_name = "Order's Step"
        verbose_name_plural = "Order's Steps"
