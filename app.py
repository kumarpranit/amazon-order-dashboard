import traceback
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import Dash, dcc, html, Input, Output, State
import dash_bootstrap_components as dbc
from pathlib import Path

BASE = Path(__file__).parent / "data"

# ── Load raw data ───────────────────────────────────────────────────────────────
customers   = pd.read_csv(BASE / "Copy of df_Customers.csv")
order_items = pd.read_csv(BASE / "Copy of df_OrderItems.csv")
payments    = pd.read_csv(BASE / "Copy of df_Payments.csv")
products    = pd.read_csv(BASE / "Copy of df_Products.csv")
orders      = pd.read_csv(BASE / "Copy of orders_rev_df.csv", parse_dates=[
    "order_purchase_timestamp", "order_delivered_timestamp", "order_estimated_delivery_date"
])

# ── Build master table ──────────────────────────────────────────────────────────
pay_agg = payments.groupby("order_id").agg(
    payment_value=("payment_value", "sum"),
    payment_type=("payment_type", "first"),
    payment_installments=("payment_installments", "max"),
).reset_index()

items_agg = order_items.groupby("order_id").agg(
    item_price=("price", "sum"),
    shipping=("shipping_charges", "sum"),
    n_items=("product_id", "count"),
).reset_index()

master = (
    orders
    .merge(customers, on="customer_id", how="left")
    .merge(pay_agg,   on="order_id",    how="left")
    .merge(items_agg, on="order_id",    how="left")
)
master["order_month"] = master["order_purchase_timestamp"].dt.to_period("M").dt.to_timestamp()
master["is_sao_paulo"] = master["customer_city"].str.strip().str.lower() == "sao paulo"

items_cat = order_items.merge(
    products[["product_id", "product_category_name"]], on="product_id", how="left"
).merge(
    master[["order_id", "customer_state", "customer_city", "order_status",
            "payment_type", "order_purchase_timestamp", "order_month", "is_sao_paulo"]],
    on="order_id", how="left"
)

# ── Filter options ──────────────────────────────────────────────────────────────
ALL_STATES   = sorted(master["customer_state"].dropna().unique())
ALL_STATUSES = sorted(master["order_status"].dropna().unique())
ALL_PAYMENTS = sorted(pay_agg["payment_type"].dropna().unique())
ALL_CATS     = sorted(items_cat["product_category_name"].dropna().unique())
DATE_MIN     = master["order_purchase_timestamp"].min().date()
DATE_MAX     = master["order_purchase_timestamp"].max().date()
T_REV        = master["payment_value"].sum()
T_ORD        = master["order_id"].nunique()

# ── Colours ─────────────────────────────────────────────────────────────────────
AMAZON_ORANGE = "#FF9900"
AMAZON_DARK   = "#131921"
AMAZON_BLUE   = "#146EB4"
CARD_BG       = "#1E2A38"
FILTER_BG     = "#1A2332"
TEXT          = "#FFFFFF"
GREEN         = "#00C49F"

PLOT_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font_color=TEXT,
    margin=dict(l=10, r=10, t=40, b=10),
    legend=dict(bgcolor="rgba(0,0,0,0)"),
)
DD_STYLE         = {"background": "#0F1923", "color": TEXT, "border": "1px solid #2E4057"}
TAB_STYLE        = {"backgroundColor": AMAZON_DARK, "color": "#888", "border": "none", "padding": "10px 20px"}
TAB_SELECTED     = {"backgroundColor": CARD_BG, "color": AMAZON_ORANGE, "border": "none",
                    "borderTop": f"3px solid {AMAZON_ORANGE}", "padding": "10px 20px", "fontWeight": "600"}

# ── Helpers ─────────────────────────────────────────────────────────────────────
def apply_filters(df, start_date, end_date, states, statuses, payments_sel):
    d = df.copy()
    if start_date:
        d = d[d["order_purchase_timestamp"] >= pd.Timestamp(start_date)]
    if end_date:
        d = d[d["order_purchase_timestamp"] <= pd.Timestamp(end_date)]
    if states:
        d = d[d["customer_state"].isin(states)]
    if statuses:
        d = d[d["order_status"].isin(statuses)]
    if payments_sel:
        d = d[d["payment_type"].isin(payments_sel)]
    return d


def delta_badge(filtered_val, total_val):
    if total_val == 0:
        return ""
    pct = (filtered_val / total_val) * 100
    color = AMAZON_ORANGE if pct < 100 else GREEN
    return html.Span(
        f"{pct:.0f}% of total",
        style={"fontSize": "0.68rem", "color": color, "marginLeft": "6px",
               "background": f"{color}22", "padding": "2px 7px", "borderRadius": "4px"},
    )


def make_kpi_card(card_id, icon, title, color=AMAZON_ORANGE):
    return dbc.Card([
        dbc.CardBody([
            html.Div([
                html.Span(icon, style={"fontSize": "1.8rem"}),
                html.Div([
                    html.P(title, className="mb-0",
                           style={"fontSize": "0.68rem", "color": "#aaa",
                                  "textTransform": "uppercase", "letterSpacing": "0.06em"}),
                    html.H4(id=f"kpi-{card_id}-value", children="—", className="mb-0",
                            style={"color": color, "fontWeight": "700", "fontSize": "1.35rem"}),
                    html.Div(id=f"kpi-{card_id}-delta", style={"minHeight": "18px"}),
                ], style={"marginLeft": "12px"}),
            ], style={"display": "flex", "alignItems": "center"}),
        ])
    ], style={"background": CARD_BG, "border": f"1px solid {color}33",
              "borderRadius": "12px", "height": "100%"})


def chart_card(graph_id, height=320):
    return dbc.Card(
        dbc.CardBody(dcc.Graph(id=graph_id, config={"displayModeBar": False},
                               style={"height": f"{height}px"})),
        style={"background": CARD_BG, "border": "none", "borderRadius": "12px"},
    )


def empty_fig(msg="No data for selected filters"):
    fig = go.Figure()
    fig.update_layout(
        **PLOT_LAYOUT,
        annotations=[dict(text=msg, x=0.5, y=0.5, showarrow=False,
                          font=dict(size=14, color="#555"))],
    )
    return fig


# ── Shared filter → dataframes ───────────────────────────────────────────────────
def _filtered_dfs(start_date, end_date, states, statuses, payments_sel, categories):
    df = apply_filters(master, start_date, end_date, states, statuses, payments_sel)
    df_cats = items_cat.copy()
    if start_date:
        df_cats = df_cats[df_cats["order_purchase_timestamp"] >= pd.Timestamp(start_date)]
    if end_date:
        df_cats = df_cats[df_cats["order_purchase_timestamp"] <= pd.Timestamp(end_date)]
    if states:
        df_cats = df_cats[df_cats["customer_state"].isin(states)]
    if statuses:
        df_cats = df_cats[df_cats["order_status"].isin(statuses)]
    if payments_sel:
        df_cats = df_cats[df_cats["payment_type"].isin(payments_sel)]
    if categories:
        df_cats = df_cats[df_cats["product_category_name"].isin(categories)]
        df = df[df["order_id"].isin(df_cats["order_id"])]
    return df, df_cats


# ── Executive figure builder ────────────────────────────────────────────────────
def build_exec_figures(df, df_cats):
    figs = {}

    mrev = df.groupby("order_month")["payment_value"].sum().reset_index().sort_values("order_month")
    if mrev.empty:
        figs["revenue"] = empty_fig()
    else:
        fig = px.area(mrev, x="order_month", y="payment_value", title="Monthly Revenue",
                      color_discrete_sequence=[AMAZON_ORANGE],
                      labels={"order_month": "", "payment_value": "Revenue (BRL)"})
        fig.update_layout(**PLOT_LAYOUT)
        fig.update_traces(line_color=AMAZON_ORANGE, fillcolor="rgba(255,153,0,0.12)")
        figs["revenue"] = fig

    sc = df["order_status"].value_counts().reset_index()
    sc.columns = ["status", "count"]
    if sc.empty:
        figs["status"] = empty_fig()
    else:
        fig = px.bar(sc, x="status", y="count", title="Orders by Status",
                     color="count", color_continuous_scale=[[0, AMAZON_BLUE], [1, AMAZON_ORANGE]],
                     labels={"status": "", "count": "Orders"})
        fig.update_layout(**PLOT_LAYOUT, coloraxis_showscale=False)
        figs["status"] = fig

    pt = df["payment_type"].value_counts().reset_index()
    pt.columns = ["type", "count"]
    if pt.empty:
        figs["payment"] = empty_fig()
    else:
        fig = px.pie(pt, names="type", values="count", title="Payment Types",
                     color_discrete_sequence=px.colors.sequential.Oranges_r, hole=0.45)
        fig.update_layout(**PLOT_LAYOUT)
        figs["payment"] = fig

    cat_rev = (df_cats.groupby("product_category_name")["price"]
               .sum().reset_index().sort_values("price", ascending=False).head(10))
    cat_rev.columns = ["category", "revenue"]
    if cat_rev.empty:
        figs["categories"] = empty_fig()
    else:
        fig = px.bar(cat_rev.sort_values("revenue"), x="revenue", y="category",
                     orientation="h", title="Top 10 Categories by Revenue",
                     color="revenue", color_continuous_scale=[[0, AMAZON_BLUE], [1, AMAZON_ORANGE]],
                     labels={"revenue": "Revenue (BRL)", "category": ""})
        fig.update_layout(**PLOT_LAYOUT, coloraxis_showscale=False)
        figs["categories"] = fig

    so = df.groupby("customer_state")["order_id"].count().reset_index()
    so.columns = ["state", "orders"]
    so = so.sort_values("orders", ascending=False).head(15)
    if so.empty:
        figs["states"] = empty_fig()
    else:
        fig = px.bar(so, x="state", y="orders", title="Orders by State (Top 15)",
                     color="orders", color_continuous_scale=[[0, AMAZON_BLUE], [1, AMAZON_ORANGE]],
                     labels={"state": "", "orders": "Orders"})
        fig.update_layout(**PLOT_LAYOUT, coloraxis_showscale=False)
        figs["states"] = fig

    deliv = df[df["order_status"] == "delivered"].copy()
    deliv["delivery_days"] = (deliv["order_delivered_timestamp"] -
                               deliv["order_purchase_timestamp"]).dt.days
    md = deliv.groupby("order_month")["delivery_days"].mean().reset_index().sort_values("order_month")
    if md.empty:
        figs["delivery"] = empty_fig()
    else:
        fig = px.line(md, x="order_month", y="delivery_days", title="Avg Delivery Days per Month",
                      color_discrete_sequence=[AMAZON_ORANGE],
                      labels={"order_month": "", "delivery_days": "Days"}, markers=True)
        fig.update_layout(**PLOT_LAYOUT)
        figs["delivery"] = fig

    return figs


# ── VP Revenue figure builder ───────────────────────────────────────────────────
def build_vp_figures(df, df_cats):
    figs = {}

    # Sales by month
    mrev = df.groupby("order_month")["payment_value"].sum().reset_index().sort_values("order_month")
    if mrev.empty:
        figs["vp_sales"] = empty_fig()
    else:
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=mrev["order_month"], y=mrev["payment_value"],
            mode="lines+markers", name="Revenue",
            line=dict(color=AMAZON_ORANGE, width=3),
            marker=dict(size=7, color=AMAZON_ORANGE),
            fill="tozeroy", fillcolor="rgba(255,153,0,0.1)",
        ))
        fig.update_layout(**PLOT_LAYOUT, title="Sales by Month (BRL)",
                          xaxis_title="", yaxis_title="Revenue (BRL)", yaxis_tickformat=",.0f")
        figs["vp_sales"] = fig

    # Order volume by month
    mvol = df.groupby("order_month")["order_id"].nunique().reset_index().sort_values("order_month")
    mvol.columns = ["order_month", "order_count"]
    if mvol.empty:
        figs["vp_volume"] = empty_fig()
    else:
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=mvol["order_month"], y=mvol["order_count"], name="Orders",
            marker=dict(color=AMAZON_BLUE),
        ))
        fig.add_trace(go.Scatter(
            x=mvol["order_month"], y=mvol["order_count"],
            mode="lines", name="Trend",
            line=dict(color=AMAZON_ORANGE, width=2, dash="dot"),
        ))
        fig.update_layout(**PLOT_LAYOUT, title="Order Volume by Month",
                          xaxis_title="", yaxis_title="# Orders", barmode="overlay")
        figs["vp_volume"] = fig

    # Top 10 most purchased categories
    top_prod = (df_cats.groupby("product_category_name")["order_id"]
                .count().reset_index().sort_values("order_id", ascending=False).head(10))
    top_prod.columns = ["category", "purchases"]
    top_prod["category"] = top_prod["category"].str.replace("_", " ").str.title()
    if top_prod.empty:
        figs["vp_products"] = empty_fig()
    else:
        fig = px.bar(
            top_prod.sort_values("purchases"), x="purchases", y="category",
            orientation="h", title="Top 10 Most Purchased Product Categories",
            color="purchases",
            color_continuous_scale=[[0, "#1a4a6e"], [0.5, AMAZON_BLUE], [1, AMAZON_ORANGE]],
            labels={"purchases": "# of Purchases", "category": ""},
            text="purchases",
        )
        fig.update_traces(textposition="outside", textfont_color=TEXT)
        fig.update_layout(**PLOT_LAYOUT, coloraxis_showscale=False)
        figs["vp_products"] = fig

    # % of orders from São Paulo city — by month
    sp_tmp = df[["order_month", "is_sao_paulo"]].copy()
    sp = (sp_tmp.groupby("order_month")["is_sao_paulo"]
          .apply(lambda x: x.sum() / max(len(x), 1) * 100)
          .reset_index())
    sp.columns = ["order_month", "sp_pct"]
    sp = sp.sort_values("order_month")
    if sp.empty:
        figs["vp_saopaulo"] = empty_fig()
    else:
        avg_sp = sp["sp_pct"].mean()
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=sp["order_month"], y=sp["sp_pct"],
            mode="lines+markers", name="São Paulo %",
            line=dict(color=GREEN, width=3),
            marker=dict(size=7, color=GREEN),
            fill="tozeroy", fillcolor="rgba(0,196,159,0.1)",
        ))
        fig.add_hline(y=avg_sp, line_dash="dot", line_color=AMAZON_ORANGE,
                      annotation_text=f"Avg {avg_sp:.1f}%",
                      annotation_font_color=AMAZON_ORANGE)
        fig.update_layout(**PLOT_LAYOUT,
                          title="% of Orders from São Paulo City — by Month",
                          xaxis_title="", yaxis_title="% of Orders", yaxis_ticksuffix="%")
        figs["vp_saopaulo"] = fig

    return figs


# ── Design rationale card (static) ──────────────────────────────────────────────
def design_rationale_card():
    bullet  = lambda t: html.Li(t, style={"marginBottom": "4px", "color": "#ccc", "fontSize": "0.87rem"})
    section = lambda title, items: html.Div([
        html.P(title, style={"color": AMAZON_ORANGE, "fontWeight": "700",
                             "marginBottom": "6px", "fontSize": "0.88rem",
                             "textTransform": "uppercase", "letterSpacing": "0.05em"}),
        html.Ul([bullet(i) for i in items], style={"paddingLeft": "18px", "marginBottom": "0"}),
    ], style={"marginBottom": "16px"})

    return dbc.Card(dbc.CardBody([
        html.Div([
            html.Span("📋", style={"fontSize": "1.4rem"}),
            html.H5("VP Revenue Brief — Dashboard Design Rationale",
                    style={"color": TEXT, "marginLeft": "10px", "marginBottom": "0"}),
        ], style={"display": "flex", "alignItems": "center", "marginBottom": "16px"}),
        dbc.Row([
            dbc.Col(section("What the dashboard shows", [
                "Sales by Month — revenue trend line to spot seasonal peaks.",
                "Order Volume by Month — bars + trend line to separate count from revenue growth.",
                "Top 10 Product Categories by Purchase Frequency — ranked by item count, not revenue.",
                "% Orders from São Paulo City — monthly line with average reference; SP is Brazil's largest commerce hub.",
            ]), md=4),
            dbc.Col(section("How the layout is designed", [
                "Time-series charts side-by-side on top row — VP sees trend and scale at a glance.",
                "Product ranking and SP% below — tactical detail beneath strategic trends.",
                "All charts respect the shared filter bar so the VP can slice any view instantly.",
                "Colour language: orange = revenue/volume, green = São Paulo %, blue = bar fills.",
            ]), md=4),
            dbc.Col(section("Additional metrics to consider", [
                "AOV trend line — shows if growth comes from more orders or higher basket size.",
                "Customer Retention Rate — % of customers placing a second order within 90 days.",
                "Cancellation Rate by Month — flags fulfilment issues that erode revenue.",
                "Seller Concentration — top 10 sellers by GMV; high concentration = supply-chain risk.",
                "Brazil state-level geo heat-map for regional expansion opportunities.",
                "3-month moving average forecast ribbon on the Sales chart.",
            ]), md=4),
        ]),
    ]), style={"background": "#0D1B2A", "border": f"1px solid {AMAZON_ORANGE}44",
               "borderRadius": "12px", "marginBottom": "20px"})


# ── App ─────────────────────────────────────────────────────────────────────────
app  = Dash(__name__, external_stylesheets=[dbc.themes.CYBORG])
server = app.server   # exposed for gunicorn
app.title = "Amazon Order & Delivery Dashboard"

# ── Filter bar ──────────────────────────────────────────────────────────────────
filter_bar = dbc.Card(dbc.CardBody([
    dbc.Row([
        dbc.Col([
            html.Label("Date Range", style={"color": "#aaa", "fontSize": "0.7rem",
                                            "textTransform": "uppercase", "letterSpacing": "0.05em"}),
            dcc.DatePickerRange(
                id="filter-date", min_date_allowed=DATE_MIN, max_date_allowed=DATE_MAX,
                start_date=DATE_MIN, end_date=DATE_MAX, display_format="MMM YYYY",
            ),
        ], md=3),
        dbc.Col([
            html.Label("State", style={"color": "#aaa", "fontSize": "0.7rem",
                                       "textTransform": "uppercase", "letterSpacing": "0.05em"}),
            dcc.Dropdown(id="filter-state",
                         options=[{"label": s, "value": s} for s in ALL_STATES],
                         multi=True, placeholder="All States", style=DD_STYLE),
        ], md=2),
        dbc.Col([
            html.Label("Order Status", style={"color": "#aaa", "fontSize": "0.7rem",
                                              "textTransform": "uppercase", "letterSpacing": "0.05em"}),
            dcc.Dropdown(id="filter-status",
                         options=[{"label": s.title(), "value": s} for s in ALL_STATUSES],
                         multi=True, placeholder="All Statuses", style=DD_STYLE),
        ], md=2),
        dbc.Col([
            html.Label("Payment Type", style={"color": "#aaa", "fontSize": "0.7rem",
                                              "textTransform": "uppercase", "letterSpacing": "0.05em"}),
            dcc.Dropdown(id="filter-payment",
                         options=[{"label": p.replace("_", " ").title(), "value": p} for p in ALL_PAYMENTS],
                         multi=True, placeholder="All Types", style=DD_STYLE),
        ], md=2),
        dbc.Col([
            html.Label("Category", style={"color": "#aaa", "fontSize": "0.7rem",
                                          "textTransform": "uppercase", "letterSpacing": "0.05em"}),
            dcc.Dropdown(id="filter-category",
                         options=[{"label": c.replace("_", " ").title(), "value": c} for c in ALL_CATS],
                         multi=True, placeholder="All Categories", style=DD_STYLE),
        ], md=2),
        dbc.Col([
            html.Label("\u00a0", style={"display": "block"}),
            dbc.Button("Reset", id="btn-reset", color="warning", outline=True,
                       size="sm", className="w-100"),
        ], md=1),
    ], className="g-2"),
]), style={"background": FILTER_BG, "border": "1px solid #2E4057",
           "borderRadius": "12px", "marginBottom": "14px"})

# ── Layout ───────────────────────────────────────────────────────────────────────
app.layout = dbc.Container([

    dbc.Row(dbc.Col(html.Div([
        html.Img(src="https://upload.wikimedia.org/wikipedia/commons/a/a9/Amazon_logo.svg",
                 style={"height": "34px", "filter": "brightness(0) invert(1)"}),
        html.H4("Order & Delivery Dashboard",
                style={"color": TEXT, "marginLeft": "16px", "marginBottom": "0"}),
    ], style={"display": "flex", "alignItems": "center", "padding": "16px 0"})), className="mb-1"),

    filter_bar,

    dbc.Row([
        dbc.Col(make_kpi_card("revenue", "💰", "Total Revenue",    AMAZON_ORANGE), md=3),
        dbc.Col(make_kpi_card("orders",  "📦", "Total Orders",     AMAZON_ORANGE), md=3),
        dbc.Col(make_kpi_card("avg",     "🛒", "Avg Order Value",  AMAZON_BLUE),   md=3),
        dbc.Col(make_kpi_card("ontime",  "🚚", "On-Time Delivery", GREEN),         md=3),
    ], className="mb-3 g-3"),

    dcc.Tabs(id="main-tabs", value="exec", children=[

        dcc.Tab(label="Executive Overview", value="exec",
                style=TAB_STYLE, selected_style=TAB_SELECTED, children=[
            html.Div([
                dbc.Row([
                    dbc.Col(chart_card("chart-revenue"), md=8),
                    dbc.Col(chart_card("chart-status"),  md=4),
                ], className="mb-3 g-3 mt-3"),
                dbc.Row([
                    dbc.Col(chart_card("chart-payment"),    md=4),
                    dbc.Col(chart_card("chart-categories"), md=8),
                ], className="mb-3 g-3"),
                dbc.Row([
                    dbc.Col(chart_card("chart-states"),   md=8),
                    dbc.Col(chart_card("chart-delivery"), md=4),
                ], className="mb-3 g-3"),
                html.P("Click any bar or pie slice to cross-filter · Built with Plotly Dash",
                       style={"color": "#444", "fontSize": "0.72rem",
                              "textAlign": "center", "paddingBottom": "8px"}),
            ]),
        ]),

        dcc.Tab(label="VP Revenue Report", value="vp",
                style=TAB_STYLE, selected_style=TAB_SELECTED, children=[
            html.Div([
                html.Div(style={"height": "16px"}),
                design_rationale_card(),
                dbc.Row([
                    dbc.Col(chart_card("vp-sales",  360), md=6),
                    dbc.Col(chart_card("vp-volume", 360), md=6),
                ], className="mb-3 g-3"),
                dbc.Row([
                    dbc.Col(chart_card("vp-products", 380), md=6),
                    dbc.Col(chart_card("vp-saopaulo", 380), md=6),
                ], className="mb-3 g-3"),
                html.P("All charts respond to the shared filter bar above · Built with Plotly Dash",
                       style={"color": "#444", "fontSize": "0.72rem",
                              "textAlign": "center", "paddingBottom": "8px"}),
            ]),
        ]),
    ], style={"borderBottom": f"2px solid {AMAZON_ORANGE}33"}),

], fluid=True, style={"background": AMAZON_DARK, "minHeight": "100vh", "padding": "0 24px"})


# ── Cross-filter callbacks ───────────────────────────────────────────────────────
@app.callback(
    Output("filter-state", "value"),
    Input("chart-states", "clickData"),
    State("filter-state", "value"),
    prevent_initial_call=True,
)
def click_state(click_data, current):
    if not click_data:
        return current
    clicked = click_data["points"][0]["x"]
    current = list(current or [])
    return [s for s in current if s != clicked] if clicked in current else current + [clicked]


@app.callback(
    Output("filter-payment", "value"),
    Input("chart-payment", "clickData"),
    State("filter-payment", "value"),
    prevent_initial_call=True,
)
def click_payment(click_data, current):
    if not click_data:
        return current
    clicked = click_data["points"][0]["label"]
    current = list(current or [])
    return [p for p in current if p != clicked] if clicked in current else current + [clicked]


@app.callback(
    Output("filter-status", "value"),
    Input("chart-status", "clickData"),
    State("filter-status", "value"),
    prevent_initial_call=True,
)
def click_status(click_data, current):
    if not click_data:
        return current
    clicked = click_data["points"][0]["x"]
    current = list(current or [])
    return [s for s in current if s != clicked] if clicked in current else current + [clicked]


@app.callback(
    Output("filter-category", "value"),
    Input("chart-categories", "clickData"),
    State("filter-category", "value"),
    prevent_initial_call=True,
)
def click_category(click_data, current):
    if not click_data:
        return current
    clicked = click_data["points"][0]["y"]
    current = list(current or [])
    return [c for c in current if c != clicked] if clicked in current else current + [clicked]


@app.callback(
    Output("filter-date",     "start_date"),
    Output("filter-date",     "end_date"),
    Output("filter-state",    "value", allow_duplicate=True),
    Output("filter-status",   "value", allow_duplicate=True),
    Output("filter-payment",  "value", allow_duplicate=True),
    Output("filter-category", "value", allow_duplicate=True),
    Input("btn-reset", "n_clicks"),
    prevent_initial_call=True,
)
def reset_filters(_):
    return DATE_MIN, DATE_MAX, None, None, None, None


# ── Shared inputs ────────────────────────────────────────────────────────────────
FILTER_INPUTS = [
    Input("filter-date",     "start_date"),
    Input("filter-date",     "end_date"),
    Input("filter-state",    "value"),
    Input("filter-status",   "value"),
    Input("filter-payment",  "value"),
    Input("filter-category", "value"),
]


# ── Callback 1: KPIs + Executive charts ──────────────────────────────────────────
@app.callback(
    Output("kpi-revenue-value", "children"),
    Output("kpi-revenue-delta", "children"),
    Output("kpi-orders-value",  "children"),
    Output("kpi-orders-delta",  "children"),
    Output("kpi-avg-value",     "children"),
    Output("kpi-avg-delta",     "children"),
    Output("kpi-ontime-value",  "children"),
    Output("kpi-ontime-delta",  "children"),
    Output("chart-revenue",    "figure"),
    Output("chart-status",     "figure"),
    Output("chart-payment",    "figure"),
    Output("chart-categories", "figure"),
    Output("chart-states",     "figure"),
    Output("chart-delivery",   "figure"),
    *FILTER_INPUTS,
)
def update_exec(start_date, end_date, states, statuses, payments_sel, categories):
    try:
        df, df_cats = _filtered_dfs(start_date, end_date, states, statuses, payments_sel, categories)

        total_rev = df["payment_value"].sum()
        total_ord = df["order_id"].nunique()
        avg_val   = float(df["payment_value"].mean()) if not df.empty else 0.0

        deliv = df[df["order_status"] == "delivered"].copy()
        if not deliv.empty:
            deliv["delivery_days"]  = (deliv["order_delivered_timestamp"] -
                                        deliv["order_purchase_timestamp"]).dt.days
            deliv["estimated_days"] = (deliv["order_estimated_delivery_date"] -
                                        deliv["order_purchase_timestamp"]).dt.days
            on_time_rate = float((deliv["delivery_days"] <= deliv["estimated_days"]).mean()) * 100
        else:
            on_time_rate = 0.0

        figs = build_exec_figures(df, df_cats)

        return (
            f"BRL {total_rev:,.0f}", delta_badge(total_rev, T_REV),
            f"{total_ord:,}",        delta_badge(total_ord, T_ORD),
            f"BRL {avg_val:,.2f}",   "",
            f"{on_time_rate:.1f}%",  "",
            figs["revenue"], figs["status"], figs["payment"],
            figs["categories"], figs["states"], figs["delivery"],
        )
    except Exception:
        traceback.print_exc()
        raise


# ── Callback 2: VP Revenue charts ────────────────────────────────────────────────
@app.callback(
    Output("vp-sales",    "figure"),
    Output("vp-volume",   "figure"),
    Output("vp-products", "figure"),
    Output("vp-saopaulo", "figure"),
    *FILTER_INPUTS,
)
def update_vp(start_date, end_date, states, statuses, payments_sel, categories):
    try:
        df, df_cats = _filtered_dfs(start_date, end_date, states, statuses, payments_sel, categories)
        figs = build_vp_figures(df, df_cats)
        return figs["vp_sales"], figs["vp_volume"], figs["vp_products"], figs["vp_saopaulo"]
    except Exception:
        traceback.print_exc()
        raise


if __name__ == "__main__":
    app.run(debug=False, port=8050)
