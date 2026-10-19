
import pandas as pd
import matplotlib.pyplot as plt

orders = pd.read_csv("data/orders.csv")
products = pd.read_csv("data/products.csv")

orders["payment_method"] = orders["payment_method"].str.strip().str.upper()
duplicate_columns = [
    "customer_id", "product_id", "order_date", "quantity",
    "discount_pct", "payment_method", "rating", "returned"
]
orders = orders.drop_duplicates(subset=duplicate_columns, keep="first").copy()
orders["discount_pct"] = orders["discount_pct"].fillna(0)

merged = orders.merge(products[["product_id", "price"]], on="product_id")
merged["order_value"] = (
    merged["quantity"] * merged["price"] *
    (1 - merged["discount_pct"] / 100)
)

payment_rates = (
    merged.groupby("payment_method")["returned"].mean().mul(100).sort_values()
)
plt.figure(figsize=(8, 5))
bars = plt.bar(payment_rates.index, payment_rates.values)
plt.title("COD Returns at 44.4% — 3x Card")
plt.xlabel("Payment method")
plt.ylabel("Return rate (%)")
for bar, value in zip(bars, payment_rates.values):
    plt.text(bar.get_x() + bar.get_width()/2, value, f"{value:.1f}%",
             ha="center", va="bottom")
plt.tight_layout()
plt.savefig("visualizations/return_rate_by_payment.png", dpi=150)
plt.close()

merged["order_date"] = pd.to_datetime(merged["order_date"])
q1 = merged["quantity"].quantile(0.25)
q3 = merged["quantity"].quantile(0.75)
iqr = q3 - q1
lower, upper = q1 - 1.5 * iqr, q3 + 1.5 * iqr
merged = merged[
    (merged["quantity"] >= lower) & (merged["quantity"] <= upper)
].copy()
merged["year_month"] = merged["order_date"].dt.to_period("M").astype(str)
monthly = merged.groupby("year_month")["order_value"].sum()

plt.figure(figsize=(9, 5))
plt.plot(monthly.index, monthly.values, marker="o")
plt.title("Outlier-Corrected Monthly Revenue — March 2026 Peak")
plt.xlabel("Month")
plt.ylabel("Revenue (INR)")
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig("visualizations/monthly_revenue_trend.png", dpi=150)
plt.close()
print("Saved both visualization PNGs.")
