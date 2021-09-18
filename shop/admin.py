from django.contrib import admin

from .models import Company, Category, SubCategory, Item, OrderItem, Order

admin.site.register(Company)
admin.site.register(Category)
admin.site.register(SubCategory)
admin.site.register(Item)
admin.site.register(OrderItem)
admin.site.register(Order)
