from django.views.generic import DetailView, ListView, View
from django.shortcuts import HttpResponse, render, redirect, reverse, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.db import transaction, connections, IntegrityError

from shop.models import Order, OrderStep, Step

from decouple import config
import uuid
from yookassa.domain.notification import WebhookNotification
from yookassa import Configuration, Payment
import json
import datetime
from pytz import timezone
from loguru import logger


@login_required
def order_status_view(request):
    try:
        order = Order.objects.prefetch_related('order_steps').get(
            user=request.user, ordered=False, shipped=False
        )
        steps = order.order_steps.all()
        current_step = 'оплата'
        for step in steps:
            if step.date_step_end is None:
                current_step = step.step.name_step
                break
        return render(request, 'payment/order_status.html', {'status': current_step})
    except Exception as e:
        logger.error(str(e))
        return HttpResponse('У вас ещё нет заказа', status=404)


@login_required
def get_shipped_orders_view(request):
    orders = Order.objects.filter(shipped=True, user=request.user)
    return render(request, 'payment/orders.html', {'orders': orders})


@login_required
def order_view(request, uuid):
    order = get_object_or_404(Order, uuid=uuid)
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
                    'return_url': 'https://ecommerce-by-popov-vasilii-app.ru.com/'
                },
                'capture': True,
                'description': f'{request.user}-{amount}',
                'metadata': {
                    "order_uuid": str(order.uuid)
                },
            }, str(order.uuid))
        redirect_url = payment.confirmation.confirmation_url
        return redirect(redirect_url)
    return redirect('shop:checkout')


# TODO: check yookassa api again and find out where uuid is created
# works only in postgres didn't test it yet, as I'm busy with another private project
def set_order_as_ordered(uuid, now_time):
    with connections['default'].cursor() as cursor:
        query = '''    
            WITH OrderCTE AS (
                UPDATE shop_order
                SET ordered_date = %s,
                    ordered = TRUE
                WHERE shop_order.uuid = %s
                RETURNING id AS order_id
            ), StepCTE AS (
                SELECT shop_step.id AS step_id, shop_step.name_step
                FROM shop_step
            )
            UPDATE shop_orderstep
            SET date_step_end = (
                CASE
                    WHEN shop_orderstep.step_id = (
                        SELECT step_id FROM StepCTE WHERE name_step = 'оплата'
                    )
                    THEN %s
                    ELSE NULL
                END
            ), date_step_begin = (
                CASE
                    WHEN shop_orderstep.step_id = (
                        SELECT step_id FROM StepCTE WHERE name_step = 'упаковка'
                    )
                    THEN %s
                    ELSE NULL
                END
            )
            WHERE shop_orderstep.order_id = (
                SELECT order_id FROM OrderCTE
            )
        '''
        cursor.execute(query, [now_time, uuid, now_time, now_time])


@csrf_exempt
def webhook_handler(request):
    logger.info('Webhook triggered')
    event_json = json.loads(request.body)
    notification_object = WebhookNotification(event_json)

    payment = notification_object.object
    if payment.paid:
        with transaction.atomic():
            order_uuid = uuid.UUID(payment.metdata.get('order_uuid'))
            now_time = datetime.datetime.now(tz=timezone('Europe/Moscow'))
            set_order_as_ordered(
                uuid=order_uuid,
                now_time=now_time
            )

    return HttpResponse(status=200)
