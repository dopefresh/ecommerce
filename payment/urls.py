from django.urls import path
from django.conf import settings

from . import views

app_name = 'payment'

urlpatterns = [
    path('pay/', views.pay_view, name='pay'),
    path(
        'webhook/Xyx36tQyw8JqkEZLeheWkCD85SzTGguwFvpjNsErUa2pmN2Pm2/',
        views.webhook_handler,
        name='webhook'
    ),
    path('order_status/', views.order_status_view, name='order_status'),
    path('orders/', views.get_shipped_orders_view, name='orders'),
    path('order/<str:uuid>/', views.order_view, name='order'),
]
