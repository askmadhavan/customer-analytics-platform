"""Rebuild mart_daily_sales from the Olist CSV files for the web dashboard.

Joins orders with order items (all statuses), sums item price by purchase
date, and adds per-state and per-category breakdowns. Writes
api/app/static/sales.json.

Run from the repository root:  python ml/src/build_web_sales.py data/raw
"""
import json
import sys

import pandas as pd

OUT_PATH = "api/app/static/sales.json"


def main(raw_dir):
    orders = pd.read_csv(f"{raw_dir}/olist_orders_dataset.csv")
    items = pd.read_csv(f"{raw_dir}/olist_order_items_dataset.csv")
    products = pd.read_csv(f"{raw_dir}/olist_products_dataset.csv")
    customers = pd.read_csv(f"{raw_dir}/olist_customers_dataset.csv")
    names = pd.read_csv(f"{raw_dir}/product_category_name_translation.csv")

    orders["sales_date"] = pd.to_datetime(orders.order_purchase_timestamp).dt.date.astype(str)
    j = (
        orders.merge(items, on="order_id")
        .merge(customers[["customer_id", "customer_state"]], on="customer_id", how="left")
        .merge(products[["product_id", "product_category_name"]], on="product_id", how="left")
        .merge(names, on="product_category_name", how="left")
    )
    j["cat"] = j.product_category_name_english.fillna(j.product_category_name).fillna("(Blank)")
    print("revenue", round(j.price.sum(), 2), "orders", j.order_id.nunique())

    daily = j.groupby("sales_date").agg(revenue=("price", "sum"), orders=("order_id", "nunique")).reset_index()
    calendar = pd.DataFrame(
        {"sales_date": pd.date_range(daily.sales_date.min(), daily.sales_date.max()).date.astype(str)}
    )
    daily = calendar.merge(daily, how="left").fillna(0)

    j["month"] = j.sales_date.str[:7]
    months = sorted(j.month.unique())
    by_cat = j.groupby("cat").price.sum().sort_values(ascending=False)
    cat_month = j.pivot_table(index="cat", columns="month", values="price", aggfunc="sum", fill_value=0)
    cat_month = cat_month.reindex(columns=months, fill_value=0)
    state_rev = j.pivot_table(index="customer_state", columns="sales_date", values="price", aggfunc="sum", fill_value=0)
    state_rev = state_rev.reindex(columns=daily.sales_date, fill_value=0)
    state_ord = j.groupby(["customer_state", "sales_date"]).order_id.nunique().unstack(fill_value=0)
    state_ord = state_ord.reindex(columns=daily.sales_date, fill_value=0)

    out = {
        "start": daily.sales_date.iloc[0],
        "dates_n": len(daily),
        "revenue": [round(v, 2) for v in daily.revenue],
        "orders": [int(v) for v in daily.orders],
        "states": {
            s: {"r": [round(v, 2) for v in state_rev.loc[s]], "o": [int(v) for v in state_ord.loc[s]]}
            for s in state_rev.index
        },
        "months": months,
        "cat_month": {k: [round(v, 2) for v in cat_month.loc[k]] for k in by_cat.index},
    }
    with open(OUT_PATH, "w") as f:
        json.dump(out, f, separators=(",", ":"))
    print("wrote", OUT_PATH)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "data/raw")
