# mamaearth-returns-growth-pipeline

## Project Overview
This project analyzes Mamaearth order data to understand revenue, returns, payment methods, customer segments, quantity outliers, and monthly revenue trends. It includes SQL reporting, Python data cleaning and exploratory data analysis (EDA), visualizations, and an SCR (Situation–Complication–Resolution) narrative.

## Project Structure
- `data/` — Customer, product, and order CSV files.
- `analysis/` — Python cleaning, EDA, and visualization scripts.
- `sql/` — Database schema, seed data, and SQL reports.
- `visualizations/` — Generated charts.
- `narrator/` — Findings JSON, narrative generator, and sample output.

## Key Findings
- Raw revenue: ₹99,860.20.
- Cleaned revenue: ₹97,358.30 after removing five duplicate rows.
- COD orders have the highest return rate at 44.4%.
- The highest-risk segment is COD customers in Tier-2 cities, with a 54.5% return rate.
- March 2026 is the genuine peak month after correcting for quantity outliers.

## How to Run
1. Run `sql/schema.sql`, `sql/seed_data.sql`, and `sql/reports.sql` in MySQL Workbench.
2. Run `analysis/clean_and_eda.py`.
3. Run `analysis/visualize.py`.
4. Run `narrator/generate_narrative.py` to generate the narrative.

Install the required Python packages before running the scripts. Configure any Gemini API key securely; never commit API keys or secrets to the repository.

## Outputs
See `narrator/findings.json` for the numeric findings, `narrator/sample_output.txt` for the sample narrative, and `visualizations/` for the generated charts.
