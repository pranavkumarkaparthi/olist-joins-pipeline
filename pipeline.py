import logging
import pandas as pd
from sqlalchemy import create_engine

logging.basicConfig(

    level=logging.INFO,
    format = "%(asctime)s [%(levelname)s] %(message)s ",
    handlers= [ logging.FileHandler("pipeline.log"), logging.StreamHandler(),
     ],

)

logger= logging.getLogger(__name__)

### Extract


orders = pd.read_csv("data/raw/olist_orders_dataset.csv", parse_dates= ["order_purchase_timestamp"])
items = pd.read_csv("data/raw/olist_order_items_dataset.csv")
payments = pd.read_csv("data/raw/olist_order_payments_dataset.csv")
customers = pd.read_csv("data/raw/olist_customers_dataset.csv")
logger.info(f"Extracted {len(orders)} orders, {len(items)} items, {len(payments)} payments, {len(customers)} customers")


################## Transform#########################

items_by_order = items.groupby("order_id").agg(item_count=("order_item_id", "count"), items_price = ("price","sum"), freight_total = ("freight_value","sum")).reset_index()
payments_by_order = payments.groupby("order_id").agg(payment_total=("payment_value","sum"), payment_count=("payment_sequential", "count"), max_installements = ("payment_installments", "max")).reset_index()

wide = orders.merge(items_by_order, on="order_id", how="left")
wide = wide.merge(payments_by_order,  on="order_id", how ="left")
wide= wide.merge(customers, on ="customer_id", how= "left")
logger.info(f"Build_wide_Table: {len(wide)}rows, {len(wide.columns)}columns")

###################----- Validate -------###########

assert len(wide)== len(orders), "Row count changed during merges"
assert wide.duplicated(subset=["order_id"]).sum()==0, "Duplicate order_id in wide table"
assert wide["order_id"].notnull().all(), "Null values found in order_id column"
assert wide["customer_id"].notnull().all(), "Null values found in customer_id column"
logger.info("Validation Passed")

######################---- LOAD ------#############

engine= create_engine("postgresql://pranavkumarkaparthi@localhost:5432/olist_ecommerce")
wide.to_sql("orders_wide", engine, if_exists= "replace", index=False)
logger.info(f"Loaded {len(wide)}rows into order wide")

