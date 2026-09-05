CREATE OR REPLACE VIEW supply_chain_kpi AS

SELECT

    (SELECT COUNT(*)
     FROM fact_orders)
        AS total_orders,

    (SELECT ROUND(SUM(total_amount), 2)
     FROM fact_orders)
        AS total_sales,

    (SELECT COUNT(*)
     FROM fact_inventory
     WHERE low_stock_flag = TRUE)
        AS low_stock_products,

    (SELECT COUNT(*)
     FROM fact_shipments)
        AS total_shipments,

    (SELECT COUNT(*)
     FROM fact_shipments
     WHERE delivery_status = 'ON_TIME')
        AS on_time_shipments,

    (SELECT COUNT(*)
     FROM fact_shipments
     WHERE delivery_status = 'DELAYED')
        AS delayed_shipments,

    (SELECT ROUND(
        100.0 *
        COUNT(*) FILTER (
            WHERE delivery_status = 'ON_TIME'
        )
        / NULLIF(COUNT(*), 0),
        2
    )
     FROM fact_shipments)
        AS on_time_delivery_percentage,

    (SELECT ROUND(SUM(shipping_cost), 2)
     FROM fact_shipments)
        AS total_shipping_cost,

    (SELECT COUNT(*)
     FROM fact_purchase_orders)
        AS total_purchase_orders,

    (SELECT ROUND(
        SUM(purchase_order_value),
        2
    )
     FROM fact_purchase_orders)
        AS total_purchase_order_value;