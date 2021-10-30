from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import F, Q
from django.db import transaction, connections, IntegrityError
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render, reverse
from django.utils.translation import ugettext_lazy as _
from django.views.generic import DetailView, ListView, View

from .models import Category, Subcategory, Item, Order, Step, OrderStep, OrderItem

import json
import logging


class CategoryView(ListView):
    model = Category
    template_name = 'shop/category.html'
    paginate_by = 10
    ordering = ('title',)


class SubcategoryView(ListView):
    model = Subcategory
    template_name = 'shop/subcategory.html'
    context_object_name = 'subcategories'
    paginate_by = 20
    ordering = ('title',)

    def get_queryset(self):
        subcategories = Subcategory.objects.filter(
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
        if len(self.kwargs) == 1:
            items = Item.objects.filter(
                subcategory__slug=self.kwargs.get('slug'),
            ).order_by('price', 'title')
            return items
        return Item.objects.all()


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
            messages.error(self.request, _("You do not have an active order"))
            return redirect('shop:category')


class ProductView(DetailView):
    model = Item
    template_name = 'shop/item.html'
    context_object_name = 'item'

    def get_queryset(self):
        return Item.objects.filter(slug=self.kwargs.get('slug'))


def create_order_steps(user_id: int) -> int:
    with connections['default'].cursor() as cursor:
        insert_query = '''
            WITH OrderCTE AS (
                SELECT shop_order.id
                FROM shop_order
                WHERE shop_order.ordered = FALSE AND shop_order.shipped = FALSE AND shop_order.user_id = 1
            ), OrderStepJoinedCTE AS (
                SELECT OrderCTE.id AS order_id, shop_step.id AS step_id
                FROM OrderCTE, shop_step
            )
            INSERT INTO shop_orderstep(order_id, step_id)
            SELECT OrderStepJoinedCTE.order_id, OrderStepJoinedCTE.step_id
            FROM OrderStepJoinedCTE
            RETURNING order_id;
        '''
        cursor.execute(insert_query, [user_id])
        row = cursor.fetchone()
        return row[0]


class CartView(LoginRequiredMixin, View):
    @transaction.atomic
    def get(self, *args, **kwargs):
        try:
            user = self.request.user
            order_id = create_order_steps(user.id)
            order = Order.objects.prefetch_related('order_items').get(id=order_id)
            context = {'object': order}
            return render(self.request, 'shop/cart.html', context)
        except ObjectDoesNotExist:
            transaction.rollback()
            messages.error(self.request, "You do not have an active order")
            return redirect(reverse('shop:category'))
        except IntegrityError as e:
            transaction.rollback()
            # 4 Order Steps were already present
            if 'unique constraint' in e.message:
                order = Order.objects.prefetch_related('order_items').get(
                    user=user, ordered=False,
                    shipped=False
                )
                context = {'object': order}
                return render(self.request, 'shop/cart.html', context)
            # Unexpected Integrity Error
            logger = logging.getLogger(__name__)
            logger.exception('Integrity error')
            return redirect(reverse('shop:category'))
        except Exception:
            transaction.rollback()
            logger = logging.getLogger(__name__)
            logger.exception('Rolling back transaction')
            return redirect(reverse('shop:category'))


def search_view(request):
    if request.method == 'POST':
        search_query = request.POST.get('search')
        items = Item.objects.filter(title__icontains=search_query)
        return render(request, 'shop/search.html', {'items': items})
    return redirect(request.path_info)


def add_to_cart(order_id: int, item_slug) -> bool:
    with connections['default'].cursor() as cursor:
        insert_query = ''' 
            WITH ItemCTE AS (
                SELECT shop_item.id AS item_id
                FROM shop_item
                WHERE slug = %s
            )
            INSERT INTO shop_orderitem(quantity, item_id, order_id)
            SELECT 1, ItemCTE.item_id, %s
            FROM ItemCTE
            ON CONFLICT(item_id, order_id) DO NOTHING;
        '''
        cursor.execute(insert_query, [item_slug, order_id])


@login_required
@transaction.atomic
def ajax_add_to_cart(request):
    data = json.loads(request.body)
    try:
        order, order_created = Order.objects.get_or_create(
            user=request.user, ordered=False, shipped=False
        )
        item_slug = data.get('slug')
        add_to_cart(order.id, item_slug)
    except Exception:
        transaction.rollback()
        logger = logging.getLogger(__name__)
        logger.exception('Unexpected error')
        return JsonResponse({}, status=405)
    else:
        return JsonResponse({}, status=201)


# Did check all this raw queries only in postgres
def remove_from_cart(item_slug: str, user_id: int):
    with connections['default'].cursor() as cursor:
        delete_query = '''
            WITH ItemCTE AS (
                SELECT shop_item.id AS item_id
                FROM shop_item
                WHERE slug = %s
            ), OrderCTE AS (
                SELECT shop_order.id AS order_id
                FROM shop_order
                WHERE shop_order.ordered = FALSE AND shop_order.shipped = FALSE AND shop_order.user_id = %s
            )
            DELETE FROM shop_orderitem
            WHERE item_id = (
                SELECT item_id FROM ItemCTE
            ) AND order_id = (
                SELECT order_id FROM OrderCTE
            )
        '''
        cursor.execute(delete_query, [item_slug, user_id])


@login_required
@transaction.atomic
def ajax_remove_from_cart(request):
    event_json = json.loads(request.body)
    item_slug = event_json.get('slug')
    user_id = request.user.id
    try:
        remove_from_cart(
            item_slug=item_slug,
            user_id=user_id
        )
    except IntegrityError:
        transaction.rollback()
        logger = logging.getLogger(__name__)
        logger.exception('Integrity error')
        return JsonResponse({
            'error': _("This item doesn't exist or user doesn't have order")
        }, status=400)
    else:
        return JsonResponse({}, status=202)


def edit_cart(item_slug: str, user_id: int, quantity: int):
    with connections['default'].cursor() as cursor:
        update_query = '''
            WITH ItemCTE AS (
                SELECT shop_item.id AS item_id
                FROM shop_item
                WHERE slug = %s
            ), OrderCTE AS (
                SELECT shop_order.id AS order_id
                FROM shop_order
                WHERE shop_order.ordered = FALSE AND shop_order.shipped = FALSE AND shop_order.user_id = %s
            )
            UPDATE shop_orderitem
            SET quantity = %s
            WHERE item_id = (
                SELECT item_id FROM ItemCTE
            ) AND order_id = (
                SELECT order_id FROM OrderCTE
            );
        '''
        cursor.execute(update_query, [item_slug, user_id, quantity])


@login_required
@transaction.atomic
def ajax_edit_cart(request):
    logger = logging.getLogger(__name__)
    posted_data = json.loads(request.body)
    item_slug = posted_data.get('slug')
    user_id = request.user.id
    quantity = posted_data.get('quantity')
    try:
        edit_cart(
            item_slug=item_slug,
            user_id=user_id,
            quantity=quantity
        )
    except IntegrityError:
        transaction.rollback()
        logger.exception('Integrity error')
        return JsonResponse({}, status=500)
    except Exception:
        transaction.rollback()
        logger.exception('Error')
        return JsonResponse({}, status=500)
    else:
        return JsonResponse({}, status=202)
