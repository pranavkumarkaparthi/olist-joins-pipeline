# Olist Multi-Table Joins Pipeline — One Wide Analytics Table

ETL pipeline that stitches four Olist tables (orders, order items, payments, customers) into one wide analytics table, orders_wide: one row per order carrying item totals, payment totals, and customer location. Each source table is profiled before joining; finer-grained tables (items, payments) are aggregated to one row per order with groupby before merging, and every merge is a LEFT join onto the orders spine so no order is ever lost or duplicated.

## Pipeline

1. Extract — load the four CSVs (99,441 orders, 112,650 items, 103,886 payments, 99,441 customers).
2. Transform — aggregate items per order (item_count, items_price, freight_total) and payments per order (payment_total, payment_count, max_installments); LEFT merge items, payments, then customers onto orders.
3. Validate — assert the row count survived the merges unchanged, order_id has no duplicates, and key columns are never null.
4. Load — wide table (99,441 rows x 18 columns) to the orders_wide table in PostgreSQL (olist_ecommerce database).

Profiling facts the build was verified against: 775 orders have no items (mostly unavailable/canceled), exactly 1 order has no payment record — both appear in orders_wide with honestly empty columns.

## Run

    python3 pipeline.py

## Schedule

Airflow DAG olist_joins_pipeline (@daily).

## Stack

Python, pandas, SQLAlchemy, PostgreSQL, Airflow.
