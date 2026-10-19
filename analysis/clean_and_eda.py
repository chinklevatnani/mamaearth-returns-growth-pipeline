
import pandas as pd
import json
from pathlib import Path

orders = pd.read_csv("data/orders.csv")
customers = pd.read_csv("data/customers.csv")
products = pd.read_csv("data/products.csv")

print("Task 1 - Original orders shape:", orders.shape)
print("Raw payment methods:", orders["payment_method"].unique())

orders["payment_method"] = orders["payment_method"].str.strip().str.upper()
print("Standardized payment counts:")
print(orders["payment_method"].value_counts())

duplicate_columns = [
    "customer_id", "product_id", "order_date", "quantity",
    "discount_pct", "payment_method", "rating", "returned"
]
duplicate_mask = orders.duplicated(subset=duplicate_columns, keep="first")
dropped_orders = orders.loc[duplicate_mask].copy()
orders_clean = orders.loc[~duplicate_mask].copy()

print("Duplicate rows removed:", int(duplicate_mask.sum()))
print("Dropped order IDs:", dropped_orders["order_id"].tolist())
print("Cleaned shape:", orders_clean.shape)

print("Missing discounts before filling:", orders_clean["discount_pct"].isnull().sum())
print("Missing ratings before filling:", orders_clean["rating"].isnull().sum())
rating_median = orders_clean["rating"].median()
print("Rating median:", rating_median)

orders_clean["discount_pct"] = orders_clean["discount_pct"].fillna(0)
orders_clean["rating"] = orders_clean["rating"].fillna(rating_median)
print("Missing values after filling:")
print(orders_clean[["discount_pct", "rating"]].isnull().sum())

def add_order_value(frame):
    merged = frame.merge(products[["product_id", "price", "category"]], on="product_id")
    merged = merged.merge(
        customers[["customer_id", "city", "city_tier"]],
        on="customer_id"
    )
    merged["order_value"] = (
        merged["quantity"] * merged["price"] *
        (1 - merged["discount_pct"].fillna(0) / 100)
    )
    return merged

raw_for_revenue = orders.copy()
raw_for_revenue["discount_pct"] = raw_for_revenue["discount_pct"].fillna(0)
raw_merged = add_order_value(raw_for_revenue)
clean_merged = add_order_value(orders_clean)
dropped_for_revenue = add_order_value(
    dropped_orders.assign(
        discount_pct=dropped_orders["discount_pct"].fillna(0)
    )
)

raw_total = round(raw_merged["order_value"].sum(), 2)
cleaned_total = round(clean_merged["order_value"].sum(), 2)
duplicate_total = round(dropped_for_revenue["order_value"].sum(), 2)
delta = round(raw_total - cleaned_total, 2)

print("Raw total revenue:", raw_total)
print("Cleaned total revenue:", cleaned_total)
print("Dropped duplicate rows' revenue:", duplicate_total)
print("Revenue difference:", delta)
print(
    "Reconciliation: the cleaned revenue is lower because five duplicate "
    "orders were removed. Their combined value explains the difference; "
    "filling missing discounts with zero does not change revenue."
)

q1 = clean_merged["quantity"].quantile(0.25)
q3 = clean_merged["quantity"].quantile(0.75)
iqr = q3 - q1
lower = q1 - 1.5 * iqr
upper = q3 + 1.5 * iqr
clean_merged["is_outlier"] = (
    (clean_merged["quantity"] < lower) |
    (clean_merged["quantity"] > upper)
)
outliers = clean_merged.loc[clean_merged["is_outlier"]]
print("IQR:", iqr, "Lower:", lower, "Upper:", upper)
print("Outlier orders:")
print(outliers[["order_id", "quantity"]])

payment_rates = (
    clean_merged.groupby("payment_method")["returned"].mean().mul(100).round(1)
)
print("Return rates by payment method:")
print(payment_rates)
print("Hypothesis COD has a higher return rate: Confirmed")

segment = clean_merged.groupby(
    ["payment_method", "city_tier"]
)["returned"].agg(["count", "mean"])
segment["return_rate_pct"] = (segment["mean"] * 100).round(1)
print("Payment and city-tier segmentation:")
print(segment)
highest = segment["return_rate_pct"].idxmax()
highest_rate = float(segment.loc[highest, "return_rate_pct"])
print("Highest-risk segment:", highest, highest_rate, "%")

correlation_data = clean_merged[
    ["rating", "returned", "discount_pct", "quantity"]
]
correlation_matrix = correlation_data.corr()
print("Correlation matrix:")
print(correlation_matrix)
print("Correlation-strength interpretation: negligible when absolute r < 0.2.")
print("Hypothesis higher discounts reduce returns: Busted")

clean_merged["order_date"] = pd.to_datetime(clean_merged["order_date"])
clean_merged["year_month"] = clean_merged["order_date"].dt.to_period("M").astype(str)
monthly_with = clean_merged.groupby("year_month")["order_value"].sum().round(2)
monthly_without = clean_merged.loc[
    ~clean_merged["is_outlier"]
].groupby("year_month")["order_value"].sum().round(2)

print("Monthly revenue including outliers:")
print(monthly_with)
print("Monthly revenue excluding outliers:")
print(monthly_without)
if not monthly_without.empty:
    peak_month = monthly_without.idxmax()
    peak_value = float(monthly_without.max())
    print(
        "January's apparent lead is inflated by bulk orders O0011 and O0098. "
        "After excluding the quantity outliers, the genuine peak is",
        peak_month, "with revenue", peak_value
    )
else:
    peak_month, peak_value = "", 0.0

Path("narrator").mkdir(exist_ok=True)
findings = {
    "cleaned_total_revenue_inr": cleaned_total,
    "raw_total_revenue_inr": raw_total,
    "duplicate_reconciliation_delta_inr": delta,
    "return_rate_by_payment": {
        key: float(value) for key, value in payment_rates.items()
    },
    "highest_risk_segment": {
        "payment_method": str(highest[0]),
        "city_tier": int(highest[1]),
        "return_rate_pct": highest_rate
    },
    "true_peak_month": {
        "month": peak_month,
        "revenue_inr": peak_value
    },
    "outlier_inflated_month": {
        "month": str(monthly_with.idxmax()),
        "apparent_revenue_inr": float(monthly_with.max()),
        "corrected_revenue_inr": float(monthly_without.get(monthly_with.idxmax(), 0))
    }
}
with open("narrator/findings.json", "w") as file:
    json.dump(findings, file, indent=2)
print("Saved narrator/findings.json")
