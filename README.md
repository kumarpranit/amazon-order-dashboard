<div align="center">

<img src="https://upload.wikimedia.org/wikipedia/commons/a/a9/Amazon_logo.svg" width="200px" alt="Amazon Logo"/>

# 📦 Amazon Order & Delivery Dashboard

**An interactive, real-time e-commerce analytics dashboard built with Plotly Dash**

[![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Dash](https://img.shields.io/badge/Dash-4.1.0-008DE4?style=for-the-badge&logo=plotly&logoColor=white)](https://dash.plotly.com)
[![Plotly](https://img.shields.io/badge/Plotly-5.24.1-3F4F75?style=for-the-badge&logo=plotly&logoColor=white)](https://plotly.com)
[![Pandas](https://img.shields.io/badge/Pandas-2.2.3-150458?style=for-the-badge&logo=pandas&logoColor=white)](https://pandas.pydata.org)
[![Render](https://img.shields.io/badge/Hosted_on-Render-46E3B7?style=for-the-badge&logo=render&logoColor=white)](https://render.com)

[![GitHub stars](https://img.shields.io/github/stars/kumarpranit/amazon-order-dashboard?style=social)](https://github.com/kumarpranit/amazon-order-dashboard/stargazers)
[![GitHub forks](https://img.shields.io/github/forks/kumarpranit/amazon-order-dashboard?style=social)](https://github.com/kumarpranit/amazon-order-dashboard/network)

<br/>

[🚀 Live Demo](#-live-demo) · [✨ Features](#-features) · [📊 Dashboard Views](#-dashboard-views) · [🛠 Tech Stack](#-tech-stack) · [⚡ Quick Start](#-quick-start) · [☁️ Deploy](#️-deployment)

</div>

---

## 🚀 Live Demo

> 🌐 **[amazon-order-dashboard.onrender.com](https://amazon-order-dashboard.onrender.com)** *(add URL after deploy)*

> ⚠️ Free tier may take ~30 seconds to wake from sleep on first visit.

---

## ✨ Features

<table>
<tr>
<td width="50%">

### 🎛 Interactive Filters
- 📅 **Date Range Picker** — slice any time window
- 🗺 **State** — multi-select Brazilian states
- 📋 **Order Status** — delivered, cancelled, shipped & more
- 💳 **Payment Type** — credit card, boleto, voucher, debit
- 🏷 **Category** — filter by product category
- 🔄 **Reset Button** — clear all filters in one click

</td>
<td width="50%">

### ⚡ Cross-Filtering
- Click a **state bar** → filters the whole dashboard to that state
- Click a **payment pie slice** → filters by payment type
- Click a **status bar** → filters by order status
- Click a **category bar** → filters by product category
- Every chart and KPI updates **instantly**

</td>
</tr>
</table>

---

## 📊 Dashboard Views

### 🏢 Tab 1 — Executive Overview

| KPI Card | Description |
|---|---|
| 💰 **Total Revenue** | Sum of all payment values in BRL |
| 📦 **Total Orders** | Unique order count |
| 🛒 **Avg Order Value** | Mean payment value per order |
| 🚚 **On-Time Delivery** | % of delivered orders within estimated window |

> Each KPI card shows a **"% of total" badge** so you always know how much of the full dataset your filters are covering.

**Charts included:**

```
┌─────────────────────────────┬──────────────────┐
│  📈 Monthly Revenue (area)  │  Orders by Status │
├──────────────┬──────────────┴──────────────────-┤
│ 💳 Payment   │  🏷 Top 10 Categories by Revenue  │
│    Types     │     (horizontal bar)              │
│   (donut)    │                                   │
├──────────────┴────────────────────┬─────────────┤
│  🗺 Orders by State (Top 15)      │ 🚚 Avg Days │
│                                   │   Delivery  │
└───────────────────────────────────┴─────────────┘
```

---

### 📋 Tab 2 — VP Revenue Report

> *Built to answer a direct brief from the VP of Revenue.*

| Chart | Insight |
|---|---|
| 📈 **Sales by Month** | Revenue trend line — spot seasonal peaks and growth trajectory |
| 📊 **Order Volume by Month** | Bar chart + dotted trend overlay — separate volume from revenue growth |
| 🏆 **Top 10 Most Purchased Categories** | Ranked by **frequency** (not revenue) — what customers actually buy most |
| 🏙 **% Orders from São Paulo** | Monthly % with average reference line — São Paulo is Brazil's #1 commerce hub |

**Also included on this tab:**

> 💡 A **Design Rationale card** answers the 3 key questions:
> - *What kind of dashboard did we build and why?*
> - *How is the layout designed?*
> - *What additional metrics should the VP consider?*

---

## 🗂 Dataset Overview

Five CSV files (~89,000 rows each) sourced from a Brazilian e-commerce platform:

| File | Key Columns | Rows |
|---|---|---|
| `df_Customers.csv` | customer_id, city, state | ~89k |
| `df_OrderItems.csv` | order_id, product_id, price, shipping | ~89k |
| `df_Payments.csv` | order_id, payment_type, payment_value | ~89k |
| `df_Products.csv` | product_id, product_category_name | ~89k |
| `orders_rev_df.csv` | order_id, status, timestamps | ~89k |

> 📅 **Date Range:** September 2016 — September 2018

---

## 🛠 Tech Stack

| Layer | Technology | Version |
|---|---|---|
| 🖼 App Framework | [Plotly Dash](https://dash.plotly.com/) | 4.1.0 |
| 🎨 UI Components | [Dash Bootstrap Components](https://dash-bootstrap-components.opensource.faculty.ai/) | 2.0.4 |
| 📊 Charts | [Plotly](https://plotly.com/python/) | 5.24.1 |
| 🔢 Data Processing | [pandas](https://pandas.pydata.org/) | 2.2.3 |
| 🚀 Production Server | [gunicorn](https://gunicorn.org/) | 23.0.0 |
| ☁️ Hosting | [Render](https://render.com) | — |

---

## ⚡ Quick Start

```bash
# 1. Clone the repository
git clone https://github.com/kumarpranit/amazon-order-dashboard.git
cd amazon-order-dashboard

# 2. (Optional) Create a virtual environment
python -m venv venv && source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the app
python app.py
```

Open **[http://localhost:8050](http://localhost:8050)** in your browser. 🎉

---

## ☁️ Deployment

This repo includes a `render.yaml` blueprint for **one-click deployment** on Render.

### Deploy to Render (Free)

```
1. Go to render.com → sign in with GitHub
2. New + → Web Service → Connect a repository
3. Select  kumarpranit/amazon-order-dashboard
4. Render auto-reads render.yaml → click Create Web Service
5. Live in ~3 minutes 🚀
```

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy)

> **Free tier note:** App sleeps after 15 min of inactivity. Upgrade to Starter ($7/mo) for always-on hosting.

---

## 📁 Project Structure

```
amazon-order-dashboard/
│
├── 📄 app.py                      # Main Dash application
├── 📄 requirements.txt            # Python dependencies
├── 📄 Procfile                    # gunicorn start command
├── 📄 render.yaml                 # Render deployment blueprint
├── 📄 README.md                   # You are here
│
└── 📂 data/
    ├── Copy of df_Customers.csv
    ├── Copy of df_OrderItems.csv
    ├── Copy of df_Payments.csv
    ├── Copy of df_Products.csv
    └── Copy of orders_rev_df.csv
```

---

## 👤 Author

**Pranit Kumar**
[![LinkedIn](https://img.shields.io/badge/LinkedIn-0077B5?style=flat&logo=linkedin&logoColor=white)](https://linkedin.com/in/kumarpranit)
[![GitHub](https://img.shields.io/badge/GitHub-100000?style=flat&logo=github&logoColor=white)](https://github.com/kumarpranit)

---

<div align="center">

**Built for the UCLA Industry Seminar — Amazon Case Study · Spring 2026**

⭐ If you found this useful, give the repo a star!

</div>
