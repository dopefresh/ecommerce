from django.urls import path
from django.conf import settings

from . import views

app_name = 'shop'

urlpatterns = [
    path('', views.CategoryView.as_view(), name='category'),
    path('category/<str:slug>/', views.SubCategoryView.as_view(), name='subcategory'),
    path('checkout/', views.CheckoutView.as_view(), name='checkout'),
    path('cart/', views.CartView.as_view(), name='cart'),
    path('search/', views.search_view, name='search'),
    path('subcategory/<str:slug>/', views.ProductsView.as_view(), name='products'),
    path('product/<slug>/', views.ProductView.as_view(), name='product'),
]
