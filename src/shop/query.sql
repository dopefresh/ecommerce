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


WITH ItemCTE AS (
    SELECT shop_item.id AS item_id
    FROM shop_item
    WHERE slug = 'intel-core-i5-10400f-oem-lga-1200-6-x-2900-l2-15-l3-12-2ddr4-2666-tdp-65'
)
INSERT INTO shop_orderitem(quantity, item_id, order_id)
SELECT 1, ItemCTE.item_id, 9
FROM ItemCTE
ON CONFLICT(item_id, order_id) DO NOTHING;


WITH ItemCTE AS (
    SELECT shop_item.id AS item_id
    FROM shop_item
    WHERE slug = 'intel-core-i5-10400f-oem-lga-1200-6-x-2900-l2-15-l3-12-2ddr4-2666-tdp-65'
), OrderCTE AS (
    SELECT shop_order.id AS order_id
    FROM shop_order
    WHERE shop_order.ordered = FALSE AND shop_order.shipped = FALSE AND shop_order.user_id = 1
)
DELETE FROM shop_orderitem
WHERE item_id = (
    SELECT item_id FROM ItemCTE
) AND order_id = (
    SELECT order_id FROM OrderCTE
);


WITH ItemCTE AS (
    SELECT shop_item.id AS item_id
    FROM shop_item
    WHERE slug = 'intel-core-i5-10400f-oem-lga-1200-6-x-2900-l2-15-l3-12-2ddr4-2666-tdp-65'
), OrderCTE AS (
    SELECT shop_order.id AS order_id
    FROM shop_order
    WHERE shop_order.ordered = FALSE AND shop_order.shipped = FALSE AND shop_order.user_id = 1
)
UPDATE shop_orderitem
SET quantity = shop_orderitem.quantity + 1
WHERE item_id = (
    SELECT item_id FROM ItemCTE
) AND order_id = (
    SELECT order_id FROM OrderCTE
);
