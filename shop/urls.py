from django.urls import path

from . import views

app_name='shop'

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('checkout/', views.CheckoutView.as_view(), name='checkout'),
    path('product/<slug>/', views.ProductView.as_view(), name='product'),
    path('cart/', views.CartView.as_view(), name='cart'),
    path('add_to_cart/<slug>/', views.add_to_cart, name='add_to_cart'),
    path('remove_from_cart/<slug>/', views.remove_from_cart, name='remove_from_cart'),
    path('remove_single_item_from_cart/<slug>', views.remove_single_item_from_cart,name='remove_single_item_from_cart'),
    path('payment/<payment_option>/', views.PaymentView.as_view(), name='payment'),
]










