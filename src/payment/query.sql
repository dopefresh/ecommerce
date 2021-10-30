--Webhook query
--1. Get order,
--2. Update fields: ordered, ordered_date
--3. Get payment and packaging step, update payment step date_step_end, and packaging step date_stepbegin

WITH OrderCTE AS (
    UPDATE shop_order
    SET ordered_date = NOW(),
        ordered = TRUE
    WHERE shop_order.ordered = FALSE AND shop_order.shipped = FALSE AND shop_order.user_id = 1
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
        THEN NOW()
        ELSE NULL
    END
), date_step_begin = (
    CASE
        WHEN shop_orderstep.step_id = (
            SELECT step_id FROM StepCTE WHERE name_step = 'упаковка'
        )
        THEN NOW()
        ELSE NULL
    END
)
WHERE shop_orderstep.order_id = (
    SELECT order_id FROM OrderCTE
)


WITH OrderCTE AS (
    SELECT shop_order.id AS order_id
    FROM shop_order
    WHERE ordered = FALSE AND shipped = FALSE AND user_id = 1
), StepCTE AS (
    SELECT shop_step.id AS step_id, shop_step.name_step
    FROM shop_step
)
UPDATE shop_orderstep
SET date_step_begin = (
    CASE
        WHEN shop_orderstep.step_id = (
            SELECT step_id FROM StepCTE WHERE name_step = 'оплата'
        )
        THEN NOW()
        ELSE NULL
    END
)
WHERE shop_orderstep.order_id = (
    SELECT order_id FROM OrderCTE
)
