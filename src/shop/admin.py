from django.contrib import admin

from .models import (
    Company,
    Category,
    Subcategory,
    Item,
    OrderItem,
    Order,
    OrderStep,
    Step,
    Employee
)

admin.site.register(Company)
admin.site.register(Category)
admin.site.register(Subcategory)
admin.site.register(Item)
admin.site.register(OrderItem)
admin.site.register(Order)
admin.site.register(OrderStep)
admin.site.register(Step)
admin.site.register(Employee)
