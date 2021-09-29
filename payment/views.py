from django.views.generic import DetailView, ListView, View
from django.shortcuts import HttpResponse, render, redirect, reverse, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required

from shop.models import Order, OrderStep, Step

from decouple import config
import uuid
from yookassa.domain.notification import WebhookNotification
from yookassa import Configuration, Payment
import json
import datetime
from pytz import timezone


@login_required
def order_status_view(request):
    order = get_object_or_404(
        Order, user=request.user,
        ordered=True, shipped=False
    )
    steps = order.order_steps
    current_step = 'оплата'
    for step in steps:
        if step.date_step_end is None:
            current_step = step.step.name_step
            break
    return render(request, 'payment/order_status.html', {'status': current_step})


@login_required
def get_shipped_orders_view(request):
    orders = Order.objects.filter(shipped=True, user=request.user)
    return render(request, 'payment/orders.html', {'orders': orders})


@login_required
def order_view(request, uuid):
    order = get_object_or_404(Order, uuid=uuid, user=request.user)
    return render(request, 'payment/order.html', {'order': order})


@login_required
def pay_view(request):
    if request.method == 'POST':
        order = get_object_or_404(Order, user=request.user,
                                  ordered=False, shipped=False)
        payment_step = order.order_steps.get(step__name_step='оплата')
        payment_step.date_step_begin = datetime.datetime.now(
            tz=timezone('Europe/Moscow')
        )
        payment_step.save()

        Configuration.account_id = config('YOOKASSA_SHOP_ID')
        Configuration.secret_key = config('YOOKASSA_SECRET_KEY')
        amount = order.get_total_price()
        payment = Payment.create(
            {
                'amount': {
                    'value': amount,
                    'currency': 'RUB'
                },
                'confirmation': {
                    'type': 'redirect',
                    'return_url': reverse('shop:category')
                },
                'capture': True,
                'description': f'{request.user}-{amount}',
            }, order.uuid
        )
        redirect_url = payment.confirmation.confirmation_url
        return redirect(redirect_url)
    return redirect('shop:checkout')


@csrf_exempt
def webhook_handler(request):
    event_json = json.loads(request.body)
    notification_object = WebhookNotification(event_json)

    payment = notification_object.object
    if payment.paid:
        order = Order.objects.get(
            uuid=payment.id
        )
        order.ordered = True
        today_date = datetime.datetime.now(tz=pytz.timezone('Europe/Moscow'))
        order.ordered_date = today_date.date()
        order.save()

        now = datetime.datetime.now(tz=timezone('Europe/Moscow'))
        payment_step = order.order_steps.get(step__name_step='оплата')
        packaging_step = order.order_steps.get(step__name_step='упаковка')
        payment_step.date_step_end = now
        packaging_step.date_step_end = now
        payment_step.save()
        packaging_step.save()

    return HttpResponse(status=200)
