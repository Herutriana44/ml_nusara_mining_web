"""Streamlit dashboard for NUSARA Mining Inference API."""

from __future__ import annotations

import json

import pandas as pd
import plotly.graph_objects as go
import requests
import streamlit as st
from requests.exceptions import RequestException

API_BASE_URL = "https://herutriana44-ai-nusara-mining-api.hf.space"

st.set_page_config(
    page_title="NUSARA Mining Dashboard",
    page_icon="⛏️",
    layout="wide",
)

st.markdown("""
<style>
.main-header {
    font-size: 2.2rem;
    font-weight: bold;
    color: #1f77b4;
    text-align: center;
    margin-bottom: 0.5rem;
}
.sub-header {
    font-size: 1.1rem;
    color: #555;
    text-align: center;
    margin-bottom: 1.5rem;
}
.metric-card {
    background-color: #f0f2f6;
    padding: 1.5rem;
    border-radius: 0.5rem;
    margin: 0.5rem 0;
}
</style>
""", unsafe_allow_html=True)


# ── API helpers ────────────────────────────────────────────────────────────

@st.cache_data(ttl=300)
def _get(path: str, timeout: int = 10) -> dict | None:
    """GET request to NUSARA API."""
    try:
        r = requests.get(f"{API_BASE_URL}{path}", timeout=timeout)
        return r.json() if r.ok else None
    except RequestException:
        return None


def _post(path: str, data: dict | None = None, timeout: int = 30) -> dict | None:
    """POST request to NUSARA API (not cached so results are always fresh)."""
    try:
        r = requests.post(
            f"{API_BASE_URL}{path}",
            json=data,
            timeout=timeout,
        )
        return r.json() if r.ok else None
    except RequestException:
        return None


def get_health() -> dict | None:
    return _get("/health")


def get_equipment_failure(data: dict | None = None) -> dict | None:
    return _post("/predict/equipment-failure", data)


def get_maintenance_priority(data: dict | None = None) -> dict | None:
    return _post("/predict/maintenance-priority", data)


def get_cost_anomaly(data: dict | None = None) -> dict | None:
    return _post("/predict/cost-anomaly", data)


def get_what_if(data: dict | None = None) -> dict | None:
    return _post("/predict/what-if", data)


def get_full_pipeline(data: dict | None = None) -> dict | None:
    return _post("/predict/full-pipeline", data)


# ── Sidebar ────────────────────────────────────────────────────────────────

with st.sidebar:
    st.header("⚙️ Configuration")

    if st.button("🔍 Check API Health", use_container_width=True):
        with st.spinner("Checking..."):
            health = get_health()
        if health:
            st.session_state.health = health
        else:
            st.session_state.pop("health", None)
            st.error("Cannot connect to API")

    if "health" in st.session_state:
        h = st.session_state.health
        status = h.get("status", "unknown")
        if status == "ok":
            st.success(f"✅ API: {status.upper()}")
        else:
            st.warning(f"⚠️ API: {status.upper()}")
        models = h.get("models_loaded", 0)
        st.caption(f"Models Loaded: {models}")

    st.divider()
    api_key = st.text_input("API Key (optional)", type="password")
    if api_key:
        st.session_state.api_key = api_key

    page = st.selectbox(
        "📄 Navigate",
        [
            "📊 Overview",
            "🔧 Equipment Failure",
            "🛠️ Maintenance Priority",
            "💰 Cost Anomaly",
            "🎯 What-If Simulation",
            "📈 Full Pipeline",
            "✏️ Custom Input",
        ],
    )

    st.divider()
    st.caption(f"API: `{API_BASE_URL}`")
    st.caption("NUSARA Mining Dashboard v1.0")


# ── Header ─────────────────────────────────────────────────────────────────

st.markdown(
    '<div class="main-header">⛏️ NUSARA Mining ML Dashboard</div>',
    unsafe_allow_html=True,
)
st.markdown(
    '<div class="sub-header">AI-powered predictions for equipment, maintenance, and cost analysis</div>',
    unsafe_allow_html=True,
)


# ── Page 1: Overview ───────────────────────────────────────────────────────

if page == "📊 Overview":
    st.header("Dashboard Overview")

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("📋 Available Endpoints")
        for name, desc in [
            ("Equipment Failure", "Predict risk level of equipment breakdown"),
            ("Maintenance Priority", "Prioritize maintenance tasks across sites"),
            ("Cost Anomaly", "Detect cost anomalies using Isolation Forest"),
            ("What-If Simulation", "Simulate production scenarios"),
            ("Full Pipeline", "Run all models at once with executive summary"),
        ]:
            st.write(f"**{name}**: {desc}")

    with col2:
        st.subheader("📚 Input Data Format")
        st.write("""
        **Equipment Data:** date, site_name, equipment_name, operating_hours,
        downtime_hours, fuel_consumption, maintenance_cost

        **Financial Data:** date, site_name, project_name, budgeted_cost,
        actual_cost

        **Production Data:** date, site_name, material_name, produced_volume,
        unit_cost

        **Tips:** Use *Custom Input* page to test with your own data.
        """)


# ── Page 2: Equipment Failure ──────────────────────────────────────────────

elif page == "🔧 Equipment Failure":
    st.header("🔧 Equipment Failure Prediction")

    if st.button("▶️ Run Equipment Failure Prediction", type="primary", use_container_width=True):
        with st.spinner("Predicting equipment failures..."):
            result = get_equipment_failure()

        if not result:
            st.error("❌ Cannot connect to API. Check API health in sidebar.")
        elif result.get("status") != "ok":
            st.error(f"API Error: {result.get('message', 'Unknown error')}")
        else:
            data = result.get("data", {})
            predictions = data.get("predictions", [])

            # Summary metrics
            high_risk   = sum(1 for p in predictions if p.get("risk_level") == "high")
            medium_risk = sum(1 for p in predictions if p.get("risk_level") == "medium")
            low_risk    = sum(1 for p in predictions if p.get("risk_level") == "low")

            c1, c2, c3 = st.columns(3)
            c1.metric("🔴 High Risk",   high_risk)
            c2.metric("🟠 Medium Risk", medium_risk)
            c3.metric("🟢 Low Risk",    low_risk)

            st.divider()

            # Risk distribution bar chart
            if predictions:
                fig = go.Figure(data=[go.Bar(
                    x=["High", "Medium", "Low"],
                    y=[high_risk, medium_risk, low_risk],
                    marker_color=["#d62728", "#ff7f0e", "#2ca02c"],
                )])
                fig.update_layout(
                    title="Risk Level Distribution",
                    xaxis_title="Risk Level",
                    yaxis_title="Count",
                )
                st.plotly_chart(fig, use_container_width=True)

                # Top 10 by risk score
                st.subheader("Top 10 Highest Risk Equipment")
                df = pd.DataFrame(predictions)
                if "risk_score" in df.columns:
                    df = df.sort_values("risk_score", ascending=False)
                st.dataframe(df.head(10), use_container_width=True)

            with st.expander("🔍 Raw JSON Response"):
                st.json(result)


# ── Page 3: Maintenance Priority ───────────────────────────────────────────

elif page == "🛠️ Maintenance Priority":
    st.header("🛠️ Maintenance Priority Analysis")

    if st.button("▶️ Run Maintenance Priority", type="primary", use_container_width=True):
        with st.spinner("Analyzing maintenance priorities..."):
            result = get_maintenance_priority()

        if not result:
            st.error("❌ Cannot connect to API. Check API health in sidebar.")
        elif result.get("status") != "ok":
            st.error(f"API Error: {result.get('message', 'Unknown error')}")
        else:
            data = result.get("data", {})
            predictions = data.get("predictions", [])

            urgent = sum(1 for p in predictions if p.get("priority") == "urgent")
            high   = sum(1 for p in predictions if p.get("priority") == "high")
            medium = sum(1 for p in predictions if p.get("priority") == "medium")
            low    = sum(1 for p in predictions if p.get("priority") == "low")

            c1, c2, c3, c4 = st.columns(4)
            c1.metric("🔴 Urgent", urgent)
            c2.metric("🟠 High",   high)
            c3.metric("🟡 Medium", medium)
            c4.metric("🟢 Low",    low)

            st.divider()

            # Pie chart
            if predictions:
                fig = go.Figure(data=[go.Pie(
                    labels=["Urgent", "High", "Medium", "Low"],
                    values=[urgent, high, medium, low],
                    marker_colors=["#d62728", "#ff7f0e", "#ffd700", "#2ca02c"],
                )])
                fig.update_layout(title="Maintenance Priority Distribution")
                st.plotly_chart(fig, use_container_width=True)

                st.subheader("Maintenance Tasks (sorted by priority)")
                df = pd.DataFrame(predictions)
                if "priority_score" in df.columns:
                    df = df.sort_values("priority_score", ascending=False)
                st.dataframe(df, use_container_width=True)

            with st.expander("🔍 Raw JSON Response"):
                st.json(result)


# ── Page 4: Cost Anomaly ──────────────────────────────────────────────────

elif page == "💰 Cost Anomaly":
    st.header("💰 Cost Anomaly Detection")

    if st.button("▶️ Run Cost Anomaly Detection", type="primary", use_container_width=True):
        with st.spinner("Detecting cost anomalies..."):
            result = get_cost_anomaly()

        if not result:
            st.error("❌ Cannot connect to API. Check API health in sidebar.")
        elif result.get("status") != "ok":
            st.error(f"API Error: {result.get('message', 'Unknown error')}")
        else:
            data = result.get("data", {})
            predictions = data.get("predictions", [])

            total     = len(predictions)
            anomalies = sum(1 for p in predictions if p.get("is_anomaly"))
            normal    = total - anomalies

            c1, c2, c3 = st.columns(3)
            c1.metric("📋 Total Records",      total)
            c2.metric("⚠️ Anomalies Detected", anomalies)
            c3.metric("✅ Normal Records",      normal)

            st.divider()

            if predictions:
                # Status bar chart
                fig = go.Figure(data=[go.Bar(
                    x=["Normal", "Anomaly"],
                    y=[normal, anomalies],
                    marker_color=["#2ca02c", "#d62728"],
                )])
                fig.update_layout(title="Cost Records Status", xaxis_title="Status", yaxis_title="Count")
                st.plotly_chart(fig, use_container_width=True)

                # Variance distribution
                variance_vals = [p.get("variance_score", 0) for p in predictions if "variance_score" in p]
                if variance_vals:
                    fig2 = go.Figure(data=[go.Histogram(x=variance_vals, nbinsx=30, marker_color="#1f77b4")])
                    fig2.update_layout(title="Variance Score Distribution", xaxis_title="Variance Score", yaxis_title="Frequency")
                    st.plotly_chart(fig2, use_container_width=True)

                # Anomaly table
                st.subheader("Detected Anomalies")
                anomaly_df = pd.DataFrame([p for p in predictions if p.get("is_anomaly")])
                if not anomaly_df.empty:
                    st.dataframe(anomaly_df, use_container_width=True)
                else:
                    st.info("✅ No anomalies detected in this dataset.")

            with st.expander("🔍 Raw JSON Response"):
                st.json(result)


# ── Page 5: What-If Simulation ────────────────────────────────────────────

elif page == "🎯 What-If Simulation":
    st.header("🎯 What-If Production Simulation")

    if st.button("▶️ Run What-If Simulation", type="primary", use_container_width=True):
        with st.spinner("Running simulation..."):
            result = get_what_if()

        if not result:
            st.error("❌ Cannot connect to API. Check API health in sidebar.")
        elif result.get("status") != "ok":
            st.error(f"API Error: {result.get('message', 'Unknown error')}")
        else:
            data     = result.get("data", {})
            baseline = data.get("baseline", {})
            scenario = data.get("scenario", {})

            c1, c2, c3 = st.columns(3)
            c1.metric("Current Production",   baseline.get("total_production", 0))
            c2.metric("Simulated Production", scenario.get("total_production", 0))
            change = scenario.get("total_production", 0) - baseline.get("total_production", 0)
            c3.metric("Difference", f"{change:+.2f}")

            st.divider()

            # Comparison chart
            if baseline and scenario:
                shared_keys = [k for k in baseline if k in scenario]
                if shared_keys:
                    fig = go.Figure()
                    fig.add_trace(go.Bar(name="Current",   x=shared_keys, y=[baseline[k] for k in shared_keys]))
                    fig.add_trace(go.Bar(name="Simulated", x=shared_keys, y=[scenario[k] for k in shared_keys]))
                    fig.update_layout(title="Baseline vs Scenario Comparison", barmode="group")
                    st.plotly_chart(fig, use_container_width=True)

            # Recommendations
            recs = data.get("recommendations", [])
            if recs:
                st.subheader("📋 Recommendations")
                for i, rec in enumerate(recs, 1):
                    st.write(f"{i}. {rec}")

            with st.expander("🔍 Raw JSON Response"):
                st.json(result)


# ── Page 6: Full Pipeline ─────────────────────────────────────────────────

elif page == "📈 Full Pipeline":
    st.header("📈 Full ML Pipeline Analysis")
    st.info("Runs all prediction models at once and provides an executive summary.")

    if st.button("▶️ Run Full Pipeline", type="primary", use_container_width=True):
        with st.spinner("Running all models — this may take a moment..."):
            result = get_full_pipeline()

        if not result:
            st.error("❌ Cannot connect to API. Check API health in sidebar.")
        elif result.get("status") != "ok":
            st.error(f"API Error: {result.get('message', 'Unknown error')}")
        else:
            data = result.get("data", {})

            # Executive summary
            summary = data.get("summary")
            if summary:
                st.subheader("📊 Executive Summary")
                if isinstance(summary, str):
                    st.write(summary)
                else:
                    st.json(summary)

            st.divider()

            tab1, tab2, tab3, tab4 = st.tabs([
                "🔧 Equipment", "🛠️ Maintenance", "💰 Cost", "🎯 What-If"
            ])

            with tab1:
                ef = data.get("equipment_failure", {}).get("data", {})
                preds = ef.get("predictions", [])
                if preds:
                    st.dataframe(pd.DataFrame(preds).head(10), use_container_width=True)
                else:
                    st.info("No equipment failure data in pipeline result.")

            with tab2:
                mp = data.get("maintenance_priority", {}).get("data", {})
                preds = mp.get("predictions", [])
                if preds:
                    st.dataframe(pd.DataFrame(preds).head(10), use_container_width=True)
                else:
                    st.info("No maintenance priority data in pipeline result.")

            with tab3:
                ca = data.get("cost_anomaly", {}).get("data", {})
                preds = ca.get("predictions", [])
                if preds:
                    anomaly_df = pd.DataFrame([p for p in preds if p.get("is_anomaly")])
                    if not anomaly_df.empty:
                        st.dataframe(anomaly_df.head(10), use_container_width=True)
                    else:
                        st.info("No cost anomalies detected.")

            with tab4:
                wi = data.get("what_if", {}).get("data", {})
                if wi:
                    st.json(wi)
                else:
                    st.info("No what-if simulation data in pipeline result.")

            st.divider()
            with st.expander("🔍 Full Raw JSON Response"):
                st.json(result)


# ── Page 7: Custom Input ──────────────────────────────────────────────────

elif page == "✏️ Custom Input":
    st.header("✏️ Custom Data Input & Testing")

    model_target = st.selectbox(
        "Prediction Target",
        ["Equipment Failure", "Maintenance Priority", "Cost Anomaly", "What-If Simulation"],
    )

    input_method = st.radio("Input Method", ["Form", "JSON"])

    if input_method == "Form":
        records: list[dict] = []

        if model_target == "Equipment Failure":
            c1, c2 = st.columns(2)
            with c1:
                date          = st.date_input("Date")
                site_name     = st.text_input("Site Name")
                eq_name       = st.text_input("Equipment Name")
                eq_type       = st.text_input("Equipment Type")
            with c2:
                op_hours      = st.number_input("Operating Hours",  min_value=0.0)
                down_hours    = st.number_input("Downtime Hours",    min_value=0.0)
                fuel          = st.number_input("Fuel Consumption",  min_value=0.0)
                maint_cost    = st.number_input("Maintenance Cost",  min_value=0.0)

            records = [{
                "date": str(date), "site_name": site_name,
                "equipment_name": eq_name, "equipment_type": eq_type,
                "operating_hours": op_hours, "downtime_hours": down_hours,
                "fuel_consumption": fuel, "maintenance_cost": maint_cost,
            }]
            endpoint_fn = get_equipment_failure

        elif model_target == "Maintenance Priority":
            c1, c2 = st.columns(2)
            with c1:
                date       = st.date_input("Date")
                site_name  = st.text_input("Site Name")
                eq_name    = st.text_input("Equipment Name")
            with c2:
                op_hours   = st.number_input("Operating Hours",  min_value=0.0)
                down_hours = st.number_input("Downtime Hours",    min_value=0.0)
                maint_cost = st.number_input("Maintenance Cost",  min_value=0.0)

            records = [{
                "date": str(date), "site_name": site_name,
                "equipment_name": eq_name, "operating_hours": op_hours,
                "downtime_hours": down_hours, "maintenance_cost": maint_cost,
            }]
            endpoint_fn = get_maintenance_priority

        elif model_target == "Cost Anomaly":
            c1, c2 = st.columns(2)
            with c1:
                date          = st.date_input("Date")
                site_name     = st.text_input("Site Name")
                project_name  = st.text_input("Project Name")
            with c2:
                budgeted      = st.number_input("Budgeted Cost",  min_value=0.0)
                actual        = st.number_input("Actual Cost",    min_value=0.0)

            records = [{
                "date": str(date), "site_name": site_name,
                "project_name": project_name,
                "budgeted_cost": budgeted, "actual_cost": actual,
            }]
            endpoint_fn = get_cost_anomaly

        else:  # What-If
            c1, c2 = st.columns(2)
            with c1:
                date            = st.date_input("Date")
                site_name       = st.text_input("Site Name")
                material_name   = st.text_input("Material Name")
            with c2:
                produced_volume = st.number_input("Produced Volume",  min_value=0.0)
                unit_cost       = st.number_input("Unit Cost",        min_value=0.0)

            records = [{
                "date": str(date), "site_name": site_name,
                "material_name": material_name,
                "produced_volume": produced_volume, "unit_cost": unit_cost,
            }]
            endpoint_fn = get_what_if

        if st.button("▶️ Run Prediction", type="primary", use_container_width=True):
            payload = {"records": records}
            with st.spinner("Predicting..."):
                result = endpoint_fn(payload)
            if result:
                st.success("✅ Prediction complete!")
                st.json(result)
            else:
                st.error("❌ Prediction failed — check API connection.")

    else:  # JSON input
        st.caption("Enter records as JSON. Example for Equipment Failure:")
        st.code(json.dumps({
            "records": [{
                "date": "2025-05-01",
                "site_name": "Tambang Nikel E",
                "equipment_name": "Bulldozer BD-002",
                "equipment_type": "Bulldozer",
                "operating_hours": 286.0,
                "downtime_hours": 23.0,
                "fuel_consumption": 1667.0,
                "maintenance_cost": 849403.0,
            }]
        }, indent=2), language="json")

        json_input = st.text_area("Enter JSON payload", height=300)

        if st.button("▶️ Run Prediction", type="primary", use_container_width=True):
            fn_map = {
                "Equipment Failure":   get_equipment_failure,
                "Maintenance Priority": get_maintenance_priority,
                "Cost Anomaly":        get_cost_anomaly,
                "What-If Simulation":  get_what_if,
            }
            try:
                payload = json.loads(json_input)
                with st.spinner("Predicting..."):
                    result = fn_map[model_target](payload)
                if result:
                    st.success("✅ Prediction complete!")
                    st.json(result)
                else:
                    st.error("❌ Prediction failed — check API connection.")
            except json.JSONDecodeError as exc:
                st.error(f"Invalid JSON: {exc}")


# ── Footer ─────────────────────────────────────────────────────────────────

st.divider()
st.markdown(
    f"""
    <div style='text-align:center;color:#888;padding:1rem'>
    ⛏️ NUSARA Mining ML Dashboard &nbsp;|&nbsp; API: <code>{API_BASE_URL}</code><br>
    <small>© 2025 NUSARA AI. Powered by Streamlit.</small>
    </div>
    """,
    unsafe_allow_html=True,
)
