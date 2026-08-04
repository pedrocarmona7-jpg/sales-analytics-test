from pathlib import Path
from sqlite3 import Connection
import pandas as pd
import logging

from .config import DATA_DIR

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_all_data(conn: Connection) -> None:
    n_customers = load_customers(conn)
    n_orders = load_orders(conn)
    n_items = load_order_items(conn)

    logger.info(
        "Loaded %d customers, %d orders, %d order_items",
        n_customers, n_orders, n_items,
    )

def load_customers(conn: Connection) -> None:
    df = pd.read_csv(Path(DATA_DIR) / "customers.csv")

    df.to_sql("customers", conn, if_exists="replace", index=False)
    return len(df)

def load_orders(conn: Connection) -> None:
    df = pd.read_csv(Path(DATA_DIR) / "orders.csv")
    
    missing_amount = df["total_amount"].isna().sum()
    if missing_amount:
        logger.warning("%d orders had missing total_amount; defaulting to 0.0", missing_amount)
    df["total_amount"] = df["total_amount"].fillna(0.0)

    missing_customer = ~df["customer_id"].isin(
        pd.read_sql_query("SELECT customer_id FROM customers", conn)["customer_id"]
    )
    if missing_customer.any():
        logger.warning("%d orders reference unknown customer_id", missing_customer.sum())

    df.to_sql("orders", conn, if_exists="replace", index=False)
    return len(df)

def load_order_items(conn: Connection) -> None:
    df = pd.read_csv(Path(DATA_DIR) / "order_items.csv")


    negative_qty = df["quantity"] < 0
    if negative_qty.any():
        logger.warning("%d order_items have negative quantity", negative_qty.sum())

    df.to_sql("order_items", conn, if_exists="replace", index=False)
    return len(df)
