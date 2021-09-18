from django.urls import path
from django.conf import settings

from . import views

app_name = 'shop'

urlpatterns = [
    path('', views.CategoryView.as_view(), name='category'),
    path('category/<str:slug>/', views.SubCategoryView.as_view(), name='subcategory'),
    path('subcategory/<str:slug>/', views.ProductsView.as_view(), name='products'),
    path('checkout/', views.CheckoutView.as_view(), name='checkout'),
    path('product/<slug>/', views.ProductView.as_view(), name='product'),
    path('cart/', views.CartView.as_view(), name='cart'),
    path('ajax_add_to_cart/',
         views.ajax_add_to_cart, name='ajax_add_to_cart'),
    path('ajax_edit_cart/', views.ajax_edit_cart, name='ajax_edit_cart'),
    path('ajax_remove_from_cart/',
         views.ajax_remove_from_cart,
         name='ajax_remove_from_cart'),
    path('search/', views.search_view, name='search'),
]
