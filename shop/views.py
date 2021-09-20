from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import F, Q
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render, reverse
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django.views.generic import DetailView, ListView, View
from django.conf import settings

from .models import Category, SubCategory, Item, Order, OrderItem

from loguru import logger
import json


class CategoryView(ListView):
    model = Category
    template_name = 'shop/category.html'
    paginate_by = 10
    ordering = ('title',)


class SubCategoryView(ListView):
    model = SubCategory
    template_name = 'shop/subcategory.html'
    context_object_name = 'subcategories'
    paginate_by = 20
    ordering = ('title',)

    def get_queryset(self):
        subcategories = SubCategory.objects.filter(
            category__slug=self.kwargs.get('slug')
        ).order_by('title')
        return subcategories


class ProductsView(ListView):
    model = Item
    template_name = 'shop/items.html'
    context_object_name = 'items'
    paginate_by = 20
    ordering = ('price', 'title',)

    def get_queryset(self):
        items = Item.objects.filter(
            sub_category__slug=self.kwargs.get('slug'),
        ).order_by('price', 'title')
        return items


class CheckoutView(LoginRequiredMixin, View):
    model = Order

    def get(self, *args, **kwargs):
        try:
            order = Order.objects.prefetch_related('order_items').get(
                user=self.request.user, ordered=False, shipped=False
            )
            context = {'object': order}
            return render(self.request, "shop/checkout.html", context)
        except Exception as e:
            logger.info(str(e))
            messages.error(self.request, _("You do not have an active order"))
            return redirect('shop:category')


class ProductView(DetailView):
    model = Item
    template_name = 'shop/item.html'
    context_object_name = 'item'

    def get_queryset(self):
        return Item.objects.filter(slug=self.kwargs.get('slug'))


class CartView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.prefetch_related('order_items').get(
                user=self.request.user, ordered=False, shipped=False
            )
            context = {'object': order}
            return render(self.request, 'shop/cart.html', context)
        except ObjectDoesNotExist:
            messages.error(self.request, "You do not have an active order")
            return redirect('/')


def search_view(request):
    if request.method == 'POST':
        search_query = request.POST.get('search')
        items = Item.objects.filter(title__icontains=search_query)
        return render(request, 'shop/search.html', {'items': items})
    return redirect(request.path_info)


@login_required
def ajax_add_to_cart(request):
    event_json = json.loads(request.body)
    try:
        item = Item.objects.get(slug=event_json.get('slug'))
    except:
        return JsonResponse({'error': _("This item doesn't exist")}, status=400)
    order, order_created = Order.objects.get_or_create(
        user=request.user, ordered=False, shipped=False
    )
    order_item, order_item_created = OrderItem.objects.get_or_create(
        order=order, item=item
    )
    return JsonResponse({}, status=201)


@login_required
def ajax_remove_from_cart(request):
    event_json = json.loads(request.body)
    slug = event_json.get('slug')
    try:
        item = Item.objects.get(slug=slug)
    except Item.objects.DoesNotExist:
        return JsonResponse({'error': _("This item doesn't exist")}, status=400)

    try:
        order = Order.objects.get(
            user=request.user, ordered=False, shipped=False
        )
    except Order.DoesNotExist:
        return JsonResponse({'error': 'You do not have an active order'}, status=400)

    try:
        order_item = OrderItem.objects.get(
            order=order, item=item
        )
    except OrderItem.DoesNotExist:
        return JsonResponse({'error': 'No such item in your cart'}, status=400)

    order_item.delete()
    return JsonResponse({}, status=202)


@login_required
def ajax_edit_cart(request):
    logger.info('Function begin')
    posted_data = json.loads(request.body)
    logger.info('Parsed request body')
    slug = posted_data.get('slug')
    quantity = posted_data.get('quantity')
    try:
        item = Item.objects.get(slug=slug)
    except Item.DoesNotExist:
        return JsonResponse({'error': 'This item does not exist'}, status=400)

    try:
        order = Order.objects.get(
            user=request.user,
            ordered=False,
            shipped=False
        )
    except Order.DoesNotExist:
        return JsonResponse({'error': 'You do not have an active order'}, status=400)

    try:
        order_item = OrderItem.objects.get(
            item=item,
            order=order
        )
    except OrderItem.DoesNotExist:
        return JsonResponse({'error': 'No such item in your cart'}, status=400)

    order_item.quantity = quantity
    order_item.save()
    return JsonResponse({}, status=200)
