import argparse
from pathlib import Path
import pandas as pd
from sqlite3 import Connection
from .db import create_in_memory_db
from .loaders import load_all_data
from .config import DEFAULT_REPORTS_DIR

import logging

logger = logging.getLogger(__name__)

def compute_revenue_per_customer_month(conn, from_date=None, to_date=None):
    query = """
            SELECT
                c.customer_id,
                c.name,
                c.country,
                strftime('%Y-%m', o.order_date) AS year_month,
                SUM(o.total_amount) AS revenue
            FROM orders o
            JOIN customers c
                ON c.customer_id = o.customer_id
            WHERE o.total_amount >= 0
            """
    params = []

    if from_date:
        query += " AND o.order_date >= ?"
        params.append(from_date)

    if to_date:
        query += " AND o.order_date <= ?"
        params.append(to_date)
    query += """
            GROUP BY
                c.customer_id,
                c.name,
                c.country,
                year_month
            ORDER BY
                year_month ASC,
                revenue DESC
            """
    df = pd.read_sql_query(query, conn, params=params)
    df["revenue"] = df["revenue"].round(2)
    return df




def compute_top_products(
    conn: Connection,
    limit: int = 5,
    from_date=None,
    to_date=None
) -> pd.DataFrame:
    # TODO: Write your SQL query here to generate the top products report here.
    #
    query = """
        SELECT
            oi.product_name,
            SUM(oi.quantity * oi.unit_price) AS total_revenue
        FROM order_items oi
        JOIN orders o
            ON oi.order_id = o.order_id
        WHERE 1=1
    """
    params = []

    if from_date:
        query += " AND o.order_date >= ?"
        params.append(from_date)

    if to_date:
        query += " AND o.order_date <= ?"
        params.append(to_date)

    query += """
        GROUP BY oi.product_name
        ORDER BY total_revenue DESC
        LIMIT ?
        """

    params.append(limit)
    df = pd.read_sql_query(
    query,
    conn,
    params=params
    )
    df["total_revenue"] = df["total_revenue"].round(2)
    return df


def generate_reports(
    conn: Connection,
    output_dir,
    from_date=None,
    to_date=None
) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)

    df_rev = compute_revenue_per_customer_month(conn, from_date=from_date, to_date=to_date)
    df_rev.to_csv(output_dir / "revenue_per_customer_per_month.csv", index=False)
    logger.info("Generated revenue report with %d rows", len(df_rev))

    df_top = compute_top_products(conn, limit=5, from_date=from_date, to_date=to_date)
    df_top.to_csv(output_dir / "top_products.csv", index=False)
    logger.info("Generated top products report with %d rows", len(df_top))

