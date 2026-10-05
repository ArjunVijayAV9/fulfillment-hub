import streamlit as st
import pandas as pd
from pathlib import Path

# ============================================================
# PAGE CONFIG
# ============================================================
st.set_page_config(
    page_title="Fulfillment Hub",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded",
)

DATA_DIR = Path(__file__).parent / "data"
DEMO_NOW = pd.Timestamp("2026-09-29 09:30")

# ============================================================
# DATA
# ============================================================
@st.cache_data
def load_data():
    orders = pd.read_csv(
        DATA_DIR / "orders.csv",
        parse_dates=["order_time", "deadline"]
    )
    products = pd.read_csv(DATA_DIR / "products.csv")
    inventory = pd.read_csv(DATA_DIR / "inventory.csv")
    shipments = pd.read_csv(DATA_DIR / "shipments.csv")
    return orders, products, inventory, shipments


orders, products, inventory, shipments = load_data()

if "orders_live" not in st.session_state:
    st.session_state.orders_live = orders.copy()

if "inventory_live" not in st.session_state:
    st.session_state.inventory_live = inventory.copy()

orders = st.session_state.orders_live.copy()
inventory = st.session_state.inventory_live.copy()


# ============================================================
# RISK LOGIC
# ============================================================
def risk_details(row):
    if row["status"] == "Shipped":
        return "On Track", "Already shipped"

    if row["stock_status"] == "Stock Issue":
        return "Critical", "Main-warehouse stock unavailable"

    hours = (row["deadline"] - DEMO_NOW).total_seconds() / 3600

    if row["priority"] == "High" and hours <= 3:
        return "Critical", f"High priority • {max(hours, 0):.1f}h to deadline"

    if hours <= 3:
        return "At Risk", f"{max(hours, 0):.1f}h to deadline"

    if row["priority"] == "High" and hours <= 5:
        return "At Risk", f"High priority • {hours:.1f}h to deadline"

    return "On Track", f"{hours:.1f}h to deadline"


risk_values = orders.apply(risk_details, axis=1, result_type="expand")
orders["risk"] = risk_values[0]
orders["risk_reason"] = risk_values[1]
orders["hours_to_deadline"] = (
    (orders["deadline"] - DEMO_NOW).dt.total_seconds() / 3600
).round(1)


def risk_icon(value):
    return {
        "Critical": "🔴",
        "At Risk": "🟠",
        "On Track": "🟢"
    }.get(value, "⚪")


# ============================================================
# PROFESSIONAL UI THEME
# ============================================================
st.markdown(
    """
    <style>
    /* ---------- Global ---------- */
    .stApp {
        background: #F4F7FB;
        color: #172B4D;
    }

    .main .block-container {
        max-width: 1500px;
        padding-top: 2rem;
        padding-bottom: 3rem;
    }

    /* ---------- Sidebar ---------- */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0B1F3A 0%, #102F56 100%);
        border-right: 1px solid #183B67;
    }

    section[data-testid="stSidebar"] * {
        color: #EAF2FF !important;
    }

    section[data-testid="stSidebar"] .stRadio label {
        padding: 7px 10px;
        border-radius: 8px;
    }

    section[data-testid="stSidebar"] .stRadio label:hover {
        background: rgba(255,255,255,0.08);
    }

    .sidebar-brand {
        padding: 10px 4px 20px 4px;
    }

    .sidebar-logo {
        font-size: 2rem;
    }

    .sidebar-title {
        font-size: 1.35rem;
        font-weight: 800;
        margin-top: 3px;
    }

    .sidebar-subtitle {
        font-size: 0.82rem;
        color: #AFC4DF !important;
        margin-top: 3px;
    }

    .sidebar-footer {
        padding: 14px 4px;
        border-top: 1px solid rgba(255,255,255,0.12);
        margin-top: 20px;
    }

    /* ---------- Page Header ---------- */
    .page-eyebrow {
        color: #1677C8;
        font-size: 0.78rem;
        font-weight: 800;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        margin-bottom: 5px;
    }

    .page-title {
        color: #102A43;
        font-size: 2.25rem;
        font-weight: 800;
        line-height: 1.15;
        margin: 0;
    }

    .page-subtitle {
        color: #66788A;
        font-size: 0.98rem;
        margin-top: 7px;
        margin-bottom: 20px;
    }

    /* ---------- KPI Cards ---------- */
    div[data-testid="stMetric"] {
        background: #FFFFFF;
        border: 1px solid #D9E2EC;
        border-radius: 14px;
        padding: 16px 18px;
        box-shadow: 0 3px 12px rgba(16, 42, 67, 0.05);
        min-height: 105px;
    }

    div[data-testid="stMetric"] label {
        color: #66788A !important;
        font-weight: 600;
    }

    div[data-testid="stMetricValue"] {
        color: #102A43 !important;
        font-weight: 800;
    }

    /* ---------- Section Headers ---------- */
    .section-title {
        color: #102A43;
        font-size: 1.25rem;
        font-weight: 800;
        margin: 3px 0 12px 0;
    }

    .section-caption {
        color: #7B8794;
        font-size: 0.88rem;
        margin-bottom: 12px;
    }

    /* ---------- Cards ---------- */
    .panel {
        background: #FFFFFF;
        border: 1px solid #D9E2EC;
        border-radius: 16px;
        padding: 18px;
        box-shadow: 0 4px 14px rgba(16, 42, 67, 0.045);
        height: 100%;
    }

    .demo-panel {
        background: linear-gradient(135deg, #0F355F 0%, #1677C8 100%);
        color: #FFFFFF;
        border-radius: 16px;
        padding: 20px;
        box-shadow: 0 8px 24px rgba(15, 53, 95, 0.20);
    }

    .demo-panel .muted {
        color: #D8E9FA;
    }

    .demo-order {
        font-size: 1.45rem;
        font-weight: 800;
    }

    .demo-label {
        font-size: 0.75rem;
        font-weight: 700;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        color: #B9D9F4;
    }

    .demo-value {
        font-size: 1rem;
        font-weight: 700;
        margin-top: 2px;
    }

    /* ---------- Status Pills ---------- */
    .pill {
        display: inline-block;
        padding: 5px 10px;
        border-radius: 999px;
        font-size: 0.78rem;
        font-weight: 750;
    }

    .pill-critical {
        background: #FEE4E2;
        color: #B42318;
    }

    .pill-risk {
        background: #FFF0D6;
        color: #B54708;
    }

    .pill-track {
        background: #DFF7EA;
        color: #067647;
    }

    .pill-blue {
        background: #E0F2FE;
        color: #026AA2;
    }

    /* ---------- Workflow ---------- */
    .workflow-step {
        background: #FFFFFF;
        border: 1px solid #D9E2EC;
        border-radius: 12px;
        padding: 12px 10px;
        text-align: center;
        min-height: 75px;
    }

    .workflow-number {
        display: inline-flex;
        width: 26px;
        height: 26px;
        align-items: center;
        justify-content: center;
        border-radius: 50%;
        background: #1677C8;
        color: #FFFFFF;
        font-weight: 800;
        font-size: 0.78rem;
        margin-bottom: 5px;
    }

    .workflow-label {
        color: #243B53;
        font-weight: 700;
        font-size: 0.86rem;
    }

    /* ---------- Tables ---------- */
    div[data-testid="stDataFrame"] {
        border-radius: 12px;
        overflow: hidden;
        border: 1px solid #D9E2EC;
    }

    /* ---------- Buttons ---------- */
    .stButton > button {
        border-radius: 9px;
        font-weight: 700;
        border: 1px solid #B8C7D9;
        min-height: 42px;
    }

    .stButton > button[kind="primary"] {
        background: #1677C8;
        border-color: #1677C8;
        color: #FFFFFF;
    }

    .stButton > button[kind="primary"]:hover {
        background: #0F5FA7;
        border-color: #0F5FA7;
    }

    /* ---------- Alerts ---------- */
    .small-note {
        color: #7B8794;
        font-size: 0.82rem;
    }

    .info-strip {
        background: #EAF4FF;
        border-left: 4px solid #1677C8;
        color: #244A68;
        border-radius: 8px;
        padding: 12px 14px;
        margin: 8px 0 14px 0;
    }

    /* ---------- Hide Streamlit chrome ---------- */
    #MainMenu {
        visibility: hidden;
    }

    footer {
        visibility: hidden;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# REUSABLE UI HELPERS
# ============================================================
def page_header(eyebrow, title, subtitle):
    st.markdown(f'<div class="page-eyebrow">{eyebrow}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="page-title">{title}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="page-subtitle">{subtitle}</div>', unsafe_allow_html=True)


def risk_pill(risk):
    cls = {
        "Critical": "pill-critical",
        "At Risk": "pill-risk",
        "On Track": "pill-track",
    }.get(risk, "pill-blue")
    return f'<span class="pill {cls}">{risk}</span>'


# ============================================================
# SIDEBAR
# ============================================================
with st.sidebar:
    st.markdown(
        """
        <div class="sidebar-brand">
            <div class="sidebar-logo">📦</div>
            <div class="sidebar-title">Fulfillment Hub</div>
            <div class="sidebar-subtitle">XYZ Operations Control Center</div>
        </div>
        """,
        unsafe_allow_html=True
    )

    page = st.radio(
        "Navigate",
        ["Dashboard", "Orders", "Inventory", "Shipments", "About"],
        label_visibility="collapsed"
    )

    st.markdown(
        """
        <div class="sidebar-footer">
            <div class="sidebar-subtitle">DEMO ENVIRONMENT</div>
            <div style="font-weight:700;margin-top:4px;">29 Sep 2026</div>
            <div class="sidebar-subtitle" style="margin-top:8px;">
                Synthetic data • No live integrations
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


# ============================================================
# DASHBOARD
# ============================================================
if page == "Dashboard":
    page_header(
        "Operations Control Center",
        "Fulfillment Hub",
        "One place to see what needs attention before an order misses its deadline."
    )

    total = len(orders)
    pending = int((orders["status"] != "Shipped").sum())
    priority = int((orders["priority"] == "High").sum())
    critical = int((orders["risk"] == "Critical").sum())
    at_risk = int((orders["risk"] == "At Risk").sum())
    inventory_issues = int((orders["stock_status"] == "Stock Issue").sum())

    c1, c2, c3, c4, c5, c6 = st.columns(6)
    c1.metric("Total Orders", total)
    c2.metric("Pending", pending)
    c3.metric("Priority", priority)
    c4.metric("Critical", critical)
    c5.metric("At Risk", at_risk)
    c6.metric("Inventory Issues", inventory_issues)

    st.markdown("<br>", unsafe_allow_html=True)

    left, right = st.columns([1.85, 1])

    with left:
        st.markdown('<div class="section-title">🚨 Action Required</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="section-caption">Orders that need attention before the next fulfillment step.</div>',
            unsafe_allow_html=True
        )

        action_df = orders[
            (orders["risk"].isin(["Critical", "At Risk"])) |
            (orders["stock_status"] == "Stock Issue")
        ].sort_values(
            ["risk", "deadline"],
            ascending=[True, True]
        ).head(8)

        display = action_df[
            ["order_id", "priority", "status", "deadline", "stock_status", "risk", "risk_reason"]
        ].copy()

        display["Priority"] = display["priority"]
        display["Deadline"] = display["deadline"].dt.strftime("%d %b • %H:%M")
        display["Risk"] = display["risk"].map(
            lambda x: risk_icon(x) + " " + x
        )

        # Recommended operational action
        def recommended_action(row):
         if row["stock_status"] == "Stock Issue":
          return "Transfer Stock"
         elif row["risk"] == "Critical":
          return "Prioritize"
         elif row["risk"] == "At Risk":
          return "Expedite"
         else:
          return "Continue"
        display["Action"] = action_df.apply(
        recommended_action,
        axis=1
        ) 

        display = display.rename(
            columns={
                "order_id": "Order",
                "status": "Status",
                "stock_status": "Stock",
                "risk_reason": "Why",
            }
        )

        st.dataframe(
            display[
                ["Order", "Priority", "Status", "Deadline", "Stock", "Risk", "Why", "Action"]
            ],
            use_container_width=True,
            hide_index=True,
            height=330
        )

    with right:
        st.markdown('<div class="section-title">📊 Order Status</div>', unsafe_allow_html=True)
        status_counts = orders["status"].value_counts().reindex(
            [
                "Order Received",
                "Order Processed",
                "Picking",
                "Packing",
                "Staging",
                "Shipped"
            ],
            fill_value=0
        )
        st.bar_chart(status_counts, height=200)

        st.markdown('<div class="section-title">⚡ Priority Mix</div>', unsafe_allow_html=True)
        priority_counts = orders["priority"].value_counts().reindex(
            ["High", "Normal"],
            fill_value=0
        )
        st.bar_chart(priority_counts, height=130)

    st.markdown("<br>", unsafe_allow_html=True)

    # Focused interview/demo scenario.
    st.markdown('<div class="section-title">🎯 Recommended Demo Scenario</div>', unsafe_allow_html=True)

    demo = orders[orders["order_id"] == "ORD-1026"]

    if not demo.empty:
        r = demo.iloc[0]

        st.markdown(
            f"""
            <div class="demo-panel">
                <div class="demo-label">End-to-end exception walkthrough</div>
                <div class="demo-order">{r["order_id"]}</div>
                <div class="muted" style="margin-top:4px;">
                    Demonstrates how the system turns an inventory exception into a clear operational action.
                </div>
                <div style="height:16px;"></div>
                <div style="display:flex;gap:42px;flex-wrap:wrap;">
                    <div>
                        <div class="demo-label">Priority</div>
                        <div class="demo-value">{r["priority"]}</div>
                    </div>
                    <div>
                        <div class="demo-label">Current Status</div>
                        <div class="demo-value">{r["status"]}</div>
                    </div>
                    <div>
                        <div class="demo-label">Risk</div>
                        <div class="demo-value">🔴 Critical</div>
                    </div>
                    <div>
                        <div class="demo-label">Exception</div>
                        <div class="demo-value">Main stock unavailable</div>
                    </div>
                </div>
                <div style="height:18px;"></div>
                <div style="background:rgba(255,255,255,0.12);border-radius:10px;padding:12px 14px;">
                    <b>Recommended action:</b>
                    Transfer available SKU stock from the secondary warehouse to the main warehouse,
                    then continue with Pick → Pack → Stage → Ship.
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown('<div class="section-title">🧭 Recommended Workflow</div>', unsafe_allow_html=True)

    workflow = [
        ("1", "Received"),
        ("2", "Processed"),
        ("3", "Picking"),
        ("4", "Packing"),
        ("5", "Staging"),
        ("6", "Shipped"),
    ]

    cols = st.columns(6)
    for col, (num, label) in zip(cols, workflow):
        with col:
            st.markdown(
                f"""
                <div class="workflow-step">
                    <div class="workflow-number">{num}</div>
                    <div class="workflow-label">{label}</div>
                </div>
                """,
                unsafe_allow_html=True
            )

    st.markdown(
        """
        <div class="info-strip">
            <b>Design choice:</b> the dashboard prioritizes exceptions instead of showing every operational detail.
            A warehouse user should be able to open the app and immediately understand what needs action.
        </div>
        """,
        unsafe_allow_html=True
    )


# ============================================================
# ORDERS
# ============================================================
elif page == "Orders":
    page_header(
        "Order Operations",
        "Order Management",
        "Filter orders by priority, status and operational risk."
    )

    c1, c2, c3 = st.columns(3)

    priority_filter = c1.multiselect(
        "Priority",
        ["High", "Normal"],
        default=["High", "Normal"]
    )

    status_options = sorted(orders["status"].unique())
    status_filter = c2.multiselect(
        "Status",
        status_options,
        default=status_options
    )

    risk_filter = c3.multiselect(
        "Risk",
        ["Critical", "At Risk", "On Track"],
        default=["Critical", "At Risk", "On Track"]
    )

    filtered = orders[
        orders["priority"].isin(priority_filter)
        & orders["status"].isin(status_filter)
        & orders["risk"].isin(risk_filter)
    ].copy()

    st.markdown(
        f'<div class="small-note">Showing <b>{len(filtered)}</b> of {len(orders)} orders</div>',
        unsafe_allow_html=True
    )
    st.markdown("<br>", unsafe_allow_html=True)

    table = filtered[
        [
            "order_id",
            "customer",
            "sku",
            "quantity",
            "priority",
            "status",
            "deadline",
            "stock_status",
            "risk",
        ]
    ].copy()

    table["deadline"] = table["deadline"].dt.strftime("%d %b • %H:%M")
    table["risk"] = table["risk"].map(
        lambda x: risk_icon(x) + " " + x
    )

    table = table.rename(
        columns={
            "order_id": "Order",
            "customer": "Customer",
            "sku": "SKU",
            "quantity": "Qty",
            "priority": "Priority",
            "status": "Status",
            "deadline": "Deadline",
            "stock_status": "Stock",
            "risk": "Risk",
        }
    )

    st.dataframe(
        table,
        use_container_width=True,
        hide_index=True,
        height=390
    )

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="section-title">🔎 Order Detail</div>', unsafe_allow_html=True)

    order_options = filtered["order_id"].tolist()

    if not order_options:
        st.warning("No orders match the selected filters.")
    else:
        default_index = (
            order_options.index("ORD-1026")
            if "ORD-1026" in order_options
            else 0
        )

        selected_order = st.selectbox(
            "Select an order",
            order_options,
            index=default_index
        )

        row = orders[orders["order_id"] == selected_order].iloc[0]

        a, b, c, d = st.columns(4)
        a.metric("Order", row["order_id"])
        b.metric("Priority", row["priority"])
        c.metric("Status", row["status"])
        d.metric("Risk", f"{risk_icon(row['risk'])} {row['risk']}")

        st.markdown("<br>", unsafe_allow_html=True)

        if row["stock_status"] == "Stock Issue":
            st.error(
                f"**Why this order is critical:** {row['risk_reason']}. "
                "Check secondary warehouse stock and transfer it before picking."
            )
        elif row["risk"] == "Critical":
            st.warning(f"**Why this order is critical:** {row['risk_reason']}.")
        elif row["risk"] == "At Risk":
            st.warning(f"**Why this order is at risk:** {row['risk_reason']}.")
        else:
            st.success(f"**Why this order is on track:** {row['risk_reason']}.")

        if row["stock_status"] == "Stock Issue":
            next_action = "Resolve inventory / transfer stock before picking."
        elif row["status"] == "Shipped":
            next_action = "No further fulfillment action required."
        else:
            next_action = "Continue through the next fulfillment stage."

        st.markdown(
            f"""
            <div class="panel">
                <b>Next action</b><br>
                <span style="color:#52606D;">{next_action}</span>
            </div>
            """,
            unsafe_allow_html=True
        )

        next_status = {
            "Order Received": "Order Processed",
            "Order Processed": "Picking",
            "Picking": "Packing",
            "Packing": "Staging",
            "Staging": "Shipped",
            "Shipped": "Shipped",
        }[row["status"]]

        if next_status != row["status"]:
            st.markdown("<br>", unsafe_allow_html=True)

            if st.button(
                f"Advance {row['order_id']} → {next_status}",
                type="primary"
            ):
                st.session_state.orders_live.loc[
                    st.session_state.orders_live["order_id"] == selected_order,
                    "status"
                ] = next_status

                st.success(
                    f"{selected_order} moved to {next_status}."
                )
                st.rerun()


# ============================================================
# INVENTORY
# ============================================================
elif page == "Inventory":
    page_header(
        "Warehouse Operations",
        "Inventory Control",
        "Compare main and secondary warehouse stock before an order reaches picking."
    )

    inv = inventory.copy()

    inv["available_total"] = (
        inv["main_warehouse_qty"]
        + inv["secondary_warehouse_qty"]
    )

    inv["status"] = inv.apply(
        lambda r: (
            "Transfer Needed"
            if r["main_warehouse_qty"] == 0
            and r["secondary_warehouse_qty"] > 0
            else "Reorder"
            if r["main_warehouse_qty"] <= r["reorder_level"]
            else "Healthy"
        ),
        axis=1
    )

    c1, c2, c3 = st.columns(3)
    c1.metric("SKUs", len(inv))
    c2.metric(
        "Transfer Needed",
        int((inv["status"] == "Transfer Needed").sum())
    )
    c3.metric(
        "Reorder Alerts",
        int((inv["status"] == "Reorder").sum())
    )

    st.markdown("<br>", unsafe_allow_html=True)

    display = inv.merge(
        products[["sku", "product_name", "variant"]],
        on="sku"
    )

    display = display[
        [
            "sku",
            "product_name",
            "variant",
            "main_warehouse_qty",
            "secondary_warehouse_qty",
            "reorder_level",
            "status",
        ]
    ].rename(
        columns={
            "sku": "SKU",
            "product_name": "Product",
            "variant": "Variant",
            "main_warehouse_qty": "Main",
            "secondary_warehouse_qty": "Secondary",
            "reorder_level": "Reorder Level",
            "status": "Status",
        }
    )

    st.dataframe(
        display,
        use_container_width=True,
        hide_index=True,
        height=330
    )

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="section-title">🔄 Stock Transfer</div>', unsafe_allow_html=True)

    transferable = inv[
        (inv["main_warehouse_qty"] == 0)
        & (inv["secondary_warehouse_qty"] > 0)
    ]

    if transferable.empty:
        st.success("No transfer candidates.")
    else:
        selected_sku = st.selectbox(
            "SKU to transfer",
            transferable["sku"].tolist()
        )

        available = int(
            inv.loc[
                inv["sku"] == selected_sku,
                "secondary_warehouse_qty"
            ].iloc[0]
        )

        transfer_qty = st.number_input(
            "Quantity",
            min_value=1,
            max_value=available,
            value=min(3, available)
        )

        st.markdown(
            f"""
            <div class="info-strip">
                <b>{selected_sku}</b> has <b>0</b> units in Main and
                <b>{available}</b> units in Secondary.
                Orders ship from the Main warehouse, so this is a transfer action.
            </div>
            """,
            unsafe_allow_html=True
        )

        if st.button(
            "Transfer to Main Warehouse",
            type="primary"
        ):
            mask = (
                st.session_state.inventory_live["sku"]
                == selected_sku
            )

            st.session_state.inventory_live.loc[
                mask,
                "secondary_warehouse_qty"
            ] -= transfer_qty

            st.session_state.inventory_live.loc[
                mask,
                "main_warehouse_qty"
            ] += transfer_qty

            st.success(
                f"Transferred {transfer_qty} unit(s) of "
                f"{selected_sku} to the main warehouse."
            )

            st.rerun()


# ============================================================
# SHIPMENTS
# ============================================================
elif page == "Shipments":
    page_header(
        "Dispatch Operations",
        "Staging & Courier Pickup",
        "Make packed boxes visible and reduce missed pickup risk."
    )

    shipment_view = shipments.copy()

    ready = shipment_view[
        shipment_view["pickup_status"] == "Ready for Pickup"
    ]

    c1, c2, c3 = st.columns(3)

    c1.metric("Ready for Pickup", len(ready))
    c2.metric(
        "Collected",
        int(
            (shipment_view["pickup_status"] == "Collected").sum()
        )
    )
    c3.metric(
        "Not Ready",
        int(
            (shipment_view["pickup_status"] == "Not Ready").sum()
        )
    )

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown(
        '<div class="section-title">🚚 Courier Summary</div>',
        unsafe_allow_html=True
    )

    summary = (
        shipment_view
        .groupby(["courier", "pickup_status"])
        .size()
        .unstack(fill_value=0)
    )

    st.dataframe(
        summary,
        use_container_width=True,
        hide_index=False
    )

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown(
        '<div class="section-title">📦 Shipment Queue</div>',
        unsafe_allow_html=True
    )

    shipment_table = shipment_view[
        [
            "order_id",
            "courier",
            "pickup_time",
            "shipping_cost",
            "pickup_status",
        ]
    ].rename(
        columns={
            "order_id": "Order",
            "courier": "Courier",
            "pickup_time": "Pickup",
            "shipping_cost": "Cost",
            "pickup_status": "Pickup Status",
        }
    )

    st.dataframe(
        shipment_table,
        use_container_width=True,
        hide_index=True,
        height=390
    )

    st.markdown(
        """
        <div class="info-strip">
            <b>Production improvement:</b> connect this view to courier pickup confirmation,
            barcode scans and physical staging locations.
        </div>
        """,
        unsafe_allow_html=True
    )


# ============================================================
# ABOUT
# ============================================================
else:
    page_header(
        "Prototype Documentation",
        "About Fulfillment Hub",
        "Scope, assumptions and future production improvements."
    )

    c1, c2 = st.columns(2)

    with c1:
        st.markdown(
            """
            <div class="panel">
                <div class="section-title">Problem Focus</div>
                <ul>
                    <li>Order visibility</li>
                    <li>Priority-order handling</li>
                    <li>Deadline risk</li>
                    <li>Inventory exceptions</li>
                    <li>Secondary-to-main warehouse transfer</li>
                    <li>Courier pickup visibility</li>
                </ul>
            </div>
            """,
            unsafe_allow_html=True
        )

    with c2:
        st.markdown(
            """
            <div class="panel">
                <div class="section-title">Design Principle</div>
                <p>
                    The warehouse team is experienced but not very comfortable with technology.
                    The interface therefore uses a small number of pages, clear statuses and
                    action-oriented exception messages.
                </p>
                <p>
                    The dashboard answers one question first:
                    <b>What needs attention right now?</b>
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown(
        """
        <div class="panel">
            <div class="section-title">Prototype Assumptions</div>
            <ul>
                <li>All operational data is synthetic and used only for demonstration.</li>
                <li>There are no live store, warehouse or courier integrations.</li>
                <li>Risk thresholds are prototype business rules and should be calibrated using real XYZ data.</li>
                <li>Stock transfers are demonstrated through Streamlit session state rather than a production backend.</li>
            </ul>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown(
        """
        <div class="panel">
            <div class="section-title">Future Production Improvements</div>
            <div style="display:grid;grid-template-columns:repeat(2,1fr);gap:10px;">
                <div>📷 Barcode scanning</div>
                <div>🔗 Live marketplace integration</div>
                <div>📦 Real-time inventory synchronization</div>
                <div>🚚 Courier API integration</div>
                <div>🔔 Automated alerts</div>
                <div>🔐 Role-based access</div>
                <div>🧾 Audit trail for stock movements</div>
                <div>📍 Staging-location tracking</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
