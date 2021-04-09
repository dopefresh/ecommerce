from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, View
from django.utils import timezone
from django.db.models import F
from allauth.account.views import LoginView, LogoutView, SignupView

import easypost

from .forms import CheckoutForm
from .models import Item, OrderItem, Order, ShippingAddress

import os
from dotenv import load_dotenv


dotenv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

easypost.api_key = os.environ['EASY_POST_API_KEY'] 


class HomeView(ListView):
    model = Item
    template_name = 'shop/home.html'
    paginate_by = 10


class CheckoutView(LoginRequiredMixin, View):

    def get(self, *args, **kwargs):
        form = CheckoutForm()
        order = Order.objects.get(user=self.request.user, ordered=False)
        context = {
            'form': form,
            'object': order
        }
        return render(self.request, "shop/checkout.html", context)
    
    def post(self, *args, **kwargs):
        form = CheckoutForm(self.request.POST or None) 
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            if form.is_valid():
                fromAddress = easypost.Address.create(
                    company='EasyPost',
                    street1='417 Montgomery Street',
                    street2='5th Floor',
                    city='San Francisco',
                    state='CA',
                    zip='94104',
                    phone='415-528-7555'
                )
                
                toAddress = easypost.Address.create(
                    verify=['delivery'],
                    name=form.cleaned_data.get('name'),
                    street1=form.cleaned_data.get('street1'),
                    street2=form.cleaned_data.get('street2'),
                    city=form.cleaned_data.get('city'),
                    zip=form.cleaned_data.get('zip'),
                    country=form.cleaned_data.get('country'),
                    email=form.cleaned_data.get('email')
                )
                if toAddress.verifications.delivery.success:
                    shipping_address = ShippingAddress(
                        name=form.cleaned_data.get('name'),
                        street1=form.cleaned_data.get('street1'),
                        street2=form.cleaned_data.get('street2'),
                        city=form.cleaned_data.get('city'),
                        zip=form.cleaned_data.get('zip'),
                        country=form.cleaned_data.get('country'),
                        email=form.cleaned_data.get('email')
                    )
                    shipping_address.save()
                    order.shipping_address=shipping_address
                    order.save()
                else:
                    messages.warning(self.request, toAddress.verifications.delivery.errors) 
            else: 
                messages.warning(self.request, "Invalid form") 
            return redirect('shop:checkout')
        
        except ObjectDoesNotExist:
            messages.error(request, "You do not have an active order")
            return redirect('shop:cart')        


class PaymentView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        return render(self.request, 'shop/payment.html')


class ProductView(DetailView):
    model = Item
    template_name = 'shop/product.html'


class CartView(LoginRequiredMixin, View):
    
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            context = {
                'object': order
            }
            return render(self.request, 'shop/cart.html', context)
        except ObjectDoesNotExist:
            messages.error(self.request, "You do not have an active order")
            return redirect('/')


@login_required
def add_to_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_item, created = OrderItem.objects.get_or_create(
        item=item,
        user=request.user,
        ordered=False
    )
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        if order.order_items.filter(item__pk=item.pk).exists():
            order_item.quantity = F('quantity') + 1
            order_item.save()
            messages.info(request, f"This item quantity was updated to {order_item.quantity}")
        else:
            order.order_items.add(order_item)
            messages.info(request, "This item was added to the cart")
    else:
        order = Order.objects.create(user=request.user, ordered_date=timezone.now())
        order.order_items.add(order_item)
        messages.info(request, "This item was added to your cart")
    return redirect('shop:cart')


@login_required
def remove_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_item = get_object_or_404(OrderItem, item__slug=slug)
    order_qs = Order.objects.filter(
        user=request.user,
        ordered=False
    ) 
    if order_qs.exists():
        order = order_qs[0]
        if order.order_items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(
                item=item,
                user=request.user,
                ordered=False
            )[0]
            order.order_items.remove(order_item)
            order_item.delete()
            messages.info(request, "This item was removed from your cart")
        else:
            messages.info(request, "This item isn't in your cart")
    else:
        messages.info(request, "You don't have an active order")

    return redirect('shop:cart')


@login_required
def remove_single_item_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_item = get_object_or_404(OrderItem, item__slug=slug)
    order_qs = Order.objects.filter(
        user=request.user,
        ordered=False
    ) 
    if order_qs.exists():
        order = order_qs[0]
        if order.order_items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(
                item=item,
                user=request.user,
                ordered=False
            )[0]
            if order_item.quantity > 1: 
                order_item.quantity = F('quantity') - 1
                order_item.save()
                messages.info(request, "This item quantity was updated")
            else:
                order.order_items.remove(order_item)
                order_item.delete()
                messages.info(request, "This item was removed from your cart")
        else:
            messages.info(request, "This item isn't in your cart")
    else:
        messages.info(request, "You don't have an active order")

    return redirect('shop:cart')


