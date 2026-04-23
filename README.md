# Amazon Order & Delivery Dashboard

An interactive data dashboard built with **Plotly Dash** that visualises Brazilian e-commerce order and delivery data across two views — an Executive Overview and a VP Revenue Report.

---

## Live Demo

> Deployed on Render: *(add your URL here after deployment)*

---

## Features

### Shared Filter Bar
| Filter | Options |
|---|---|
| Date Range | Any start/end date between Sep 2016 – Sep 2018 |
| State | Any Brazilian state (multi-select) |
| Order Status | delivered, cancelled, shipped, etc. (multi-select) |
| Payment Type | credit card, boleto, voucher, debit (multi-select) |
| Category | Any product category (multi-select) |
| Reset | Clears all filters instantly |

All KPI cards and every chart update in real time when filters change.

### Tab 1 — Executive Overview
- **KPI Cards** — Total Revenue, Total Orders, Avg Order Value, On-Time Delivery % (each shows % of total dataset currently in view)
- **Monthly Revenue** — area chart
- **Orders by Status** — bar chart (click a bar to filter by that status)
- **Payment Types** — donut chart (click a slice to filter by payment type)
- **Top 10 Categories by Revenue** — horizontal bar (click to filter by category)
- **Orders by State** — bar chart (click to filter by state)
- **Avg Delivery Days per Month** — line chart

### Tab 2 — VP Revenue Report
Answers a brief from the VP of Revenue:
- **Sales by Month** — revenue trend line with area fill
- **Order Volume by Month** — bars + dotted trend overlay
- **Top 10 Most Purchased Product Categories** — ranked by purchase frequency (not revenue)
- **% of Orders from São Paulo City** — monthly line with average reference line

A **Design Rationale card** at the top of this tab explains the layout decisions, metric choices, and additional visualisations worth considering.

---

## Datasets

Five CSV files (~89k rows each) stored in `data/`:

| File | Key Columns |
|---|---|
| `df_Customers.csv` | customer_id, customer_city, customer_state |
| `df_OrderItems.csv` | order_id, product_id, price, shipping_charges |
| `df_Payments.csv` | order_id, payment_type, payment_value |
| `df_Products.csv` | product_id, product_category_name |
| `orders_rev_df.csv` | order_id, customer_id, order_status, timestamps |

---

## Running Locally

```bash
# 1. Clone
git clone https://github.com/kumarpranit/amazon-order-dashboard.git
cd amazon-order-dashboard

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run
python app.py
```

Open [http://localhost:8050](http://localhost:8050) in your browser.

---

## Deployment (Render)

The repo includes a `render.yaml` blueprint for one-click deployment.

1. Go to [render.com](https://render.com) and sign in with GitHub
2. Click **New + → Web Service → Connect a repository**
3. Select `amazon-order-dashboard`
4. Render auto-detects the blueprint — confirm and click **Create Web Service**
5. Your app will be live in ~3 minutes at `https://amazon-order-dashboard.onrender.com`

> **Note:** Free tier instances sleep after 15 min of inactivity and take ~30 sec to wake on next visit.

---

## Tech Stack

| Layer | Library |
|---|---|
| App framework | [Plotly Dash](https://dash.plotly.com/) 4.1 |
| UI components | [Dash Bootstrap Components](https://dash-bootstrap-components.opensource.faculty.ai/) |
| Charts | [Plotly](https://plotly.com/python/) 5.24 |
| Data processing | [pandas](https://pandas.pydata.org/) 2.2 |
| Production server | [gunicorn](https://gunicorn.org/) |

---

## Project Structure

```
amazon-order-dashboard/
├── app.py               # Main Dash application
├── requirements.txt     # Python dependencies
├── Procfile             # gunicorn start command
├── render.yaml          # Render deployment blueprint
├── data/
│   ├── Copy of df_Customers.csv
│   ├── Copy of df_OrderItems.csv
│   ├── Copy of df_Payments.csv
│   ├── Copy of df_Products.csv
│   └── Copy of orders_rev_df.csv
└── README.md
```
