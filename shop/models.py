from django.db import models
from django.conf import settings
from django.shortcuts import reverse
from django_countries.fields import CountryField


CATEGORY_CHOICES = (
    ('S', 'Shirt'),
    ('SW', 'Sport wear'),
    ('OW', 'Outwear'),
    ('CPU', 'CPU'),
)

LABEL_CHOICES = (
    ('P', 'primary'),
    ('S', 'secondary'),
    ('D', 'danger')
)


class Item(models.Model):
    image = models.ImageField(upload_to='product_images/') 
    title = models.CharField(max_length=100)
    price = models.FloatField()
    discount_price = models.FloatField(blank=True, null=True) 
    description = models.TextField(default="")
    category = models.CharField(choices=CATEGORY_CHOICES, max_length=10) 
    label = models.CharField(choices=LABEL_CHOICES, max_length=10)
    slug = models.SlugField()

    def __str__(self):
        return f"{self.title} {self.price} руб."
    
    def get_absolute_url(self):
        return reverse('shop:product', kwargs={
            'slug': self.slug
        })
    
    def get_add_to_cart_url(self):
        return reverse('shop:add_to_cart', kwargs={
            'slug': self.slug
        })
    
    def get_remove_from_cart_url(self):
        return reverse('shop:remove_from_cart', kwargs={
            'slug': self.slug
        })

    def get_price(self):
        return self.discount_price if self.discount_price else self.price

class OrderItem(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE)  
    quantity = models.IntegerField(default=1)  
    ordered = models.BooleanField(default=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE,
                             blank=True, null=True) 
    quantity = models.IntegerField(default=1)

    def __str__(self):
        return f"{self.item.title} amount={self.quantity}"
    

class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    order_items = models.ManyToManyField(OrderItem)
    start_date = models.DateTimeField(auto_now_add=True)
    ordered_date = models.DateTimeField()
    ordered = models.BooleanField(default=False)
    billing_address = models.ForeignKey('BillingAddress', on_delete=models.SET_NULL, blank=True, null=True) 

    def __str__(self):
        return self.user.username

    def get_total_price(self):
        total = 0
        for order_item in self.order_items.all():
            if order_item.item.discount_price:
                total += order_item.item.discount_price * order_item.quantity
            else:
                total += order_item.item.price * order_item.quantity
        return total


class BillingAddress(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    street_address = models.CharField(max_length=255)
    apartment_address = models.CharField(max_length=100) 
    country = CountryField(multiple=False) 
    zip = models.CharField(max_length=100) 
    
    def __str__(self):
        return self.user.username








