from ecommerce.celery import app
from shop.models import Order, OrderStep

import datetime
from pytz import timezone
from loguru import logger


@app.task(name='update_orders')
def update_orders():
    logger.info('Updating orders')
    orders = Order.objects.filter(
        ordered=True, shipped=False
    ).prefetch_related('order_steps')

    for order in orders:
        packaging_step = order.order_steps.get(
            step__name_step='упаковка'
        )
        transport_step = order.order_steps.get(
            step__name_step='доставка в город'
        )
        delivery_step = order.order_steps.get(
            step__name_step='доставка по городу'
        )

        now = datetime.datetime.now(tz=timezone('Europe/Moscow'))
        time_diff = now - packaging_step.date_step_begin

        if packaging_step.date_step_end is None and time_diff.seconds >= 120:
            packaging_step.date_step_end = now
            transport_step.date_step_begin = now
            packaging_step.save()
            transport_step.save()
            continue
        
        if transport_step.date_step_begin is None:
            continue

        timediff = now - transport_step.date_step_begin
        if transport_step.date_step_end is None and timediff.seconds >= 120:
            transport_step.date_step_end = now
            delivery_step.date_step_begin = now
            transport_step.save()
            delivery_step.save()
            continue
        
        if delivery_step.date_step_begin is None:
            continue

        timediff = now - delivery_step.date_step_begin
        if delivery_step.date_step_end is None and timediff.seconds >= 120:
            delivery_step.date_step_end = now
            delivery_step.save()
            order.shipped = True
            order.save()
