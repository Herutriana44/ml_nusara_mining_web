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
</style>
""", unsafe_allow_html=True)


# ── API helpers ────────────────────────────────────────────────────────────

@st.cache_data(ttl=300)
def _get(path: str, timeout: int = 15) -> dict | None:
    try:
        r = requests.get(f"{API_BASE_URL}{path}", timeout=timeout)
        return r.json() if r.ok else None
    except RequestException:
        return None


def _post(path: str, data: dict | None = None, timeout: int = 90) -> dict | None:
    try:
        r = requests.post(f"{API_BASE_URL}{path}", json={"records": data}, timeout=timeout)
        return r.json() if r.ok else {"status": "error", "message": f"HTTP {r.status_code}"}
    except RequestException as exc:
        return {"status": "error", "message": str(exc)}


def get_health() -> dict | None:
    return _get("/health")


def predict(model: str, records: list | None = None) -> dict | None:
    return _post(f"/predict/{model}", records)


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
        models = h.get("models_loaded", [])
        st.caption(f"Models Loaded: {h.get('model_count', len(models))}")
        if isinstance(models, list) and models:
            for m in models:
                st.caption(f"• {m}")

    page = st.selectbox(
        "📄 Navigate",
        [
            "📊 Overview",
            "🔧 Equipment Failure",
            "🛠️ Maintenance Priority",
            "💰 Cost Anomaly",
            "🎯 What-If Simulation",
            "🚚 Fleet Optimization",
            "📈 Full Pipeline",
            "✏️ Custom Input",
        ],
    )

    st.divider()
    st.caption(f"API: `{API_BASE_URL}`")
    st.caption("NUSARA Mining Dashboard v2.0")


# ── Header ─────────────────────────────────────────────────────────────────

st.markdown('<div class="main-header">⛏️ NUSARA Mining ML Dashboard</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">AI-powered mining operations analytics</div>', unsafe_allow_html=True)


def api_error(result: dict | None) -> bool:
    """Render an error message if the result is missing or not ok. Return True if error."""
    if not result:
        st.error("❌ Cannot connect to API. Check API health in sidebar.")
        return True
    if result.get("status") != "ok":
        st.error(f"API Error: {result.get('message', 'Unknown error')}")
        return True
    return False


# ── Page 1: Overview ───────────────────────────────────────────────────────

if page == "📊 Overview":
    st.header("Dashboard Overview")

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("📋 Available Models")
        for name, desc in [
            ("Equipment Failure", "Failure probability & risk level per unit"),
            ("Maintenance Priority", "IMMEDIATE / MONITOR action per equipment"),
            ("Cost Anomaly", "Budget vs actual variance anomalies"),
            ("What-If Simulation", "Production scenario projections"),
            ("Fleet Optimization", "Equipment clustering & utilization"),
            ("Full Pipeline", "All models + executive summary"),
        ]:
            st.write(f"**{name}**: {desc}")

    with col2:
        st.subheader("📚 Input Data Format")
        st.write("""
        **Equipment/Fleet:** date, site_name, equipment_name, equipment_type,
        operating_hours, downtime_hours, fuel_consumption, maintenance_cost

        **Financial:** date, site_name, project_name, budgeted_cost, actual_cost

        **Production:** date, site_name, material_name, produced_volume, unit_cost

        Send `records: null` to use the API's bundled sample datasets, or use
        the *Custom Input* page for your own records.
        """)


# ── Page 2: Equipment Failure ──────────────────────────────────────────────

elif page == "🔧 Equipment Failure":
    st.header("🔧 Equipment Failure Prediction")

    if st.button("▶️ Run Prediction", type="primary", use_container_width=True):
        with st.spinner("Predicting equipment failures..."):
            result = predict("equipment-failure")

        if not api_error(result):
            preds = result.get("predictions", [])
            high   = sum(1 for p in preds if p.get("risk_level") == "HIGH")
            medium = sum(1 for p in preds if p.get("risk_level") == "MEDIUM")
            low    = sum(1 for p in preds if p.get("risk_level") == "LOW")

            c1, c2, c3 = st.columns(3)
            c1.metric("🔴 High Risk",   high)
            c2.metric("🟠 Medium Risk", medium)
            c3.metric("🟢 Low Risk",    low)
            st.divider()

            if preds:
                fig = go.Figure(data=[go.Bar(
                    x=["HIGH", "MEDIUM", "LOW"], y=[high, medium, low],
                    marker_color=["#d62728", "#ff7f0e", "#2ca02c"],
                )])
                fig.update_layout(title="Risk Level Distribution", yaxis_title="Count")
                st.plotly_chart(fig, use_container_width=True)

                st.subheader("Top 10 by Failure Probability")
                df = pd.DataFrame(preds)
                if "failure_probability" in df.columns:
                    df = df.sort_values("failure_probability", ascending=False)
                st.dataframe(df.head(10), use_container_width=True)

            with st.expander("🔍 Raw JSON Response"):
                st.json(result)


# ── Page 3: Maintenance Priority ───────────────────────────────────────────

elif page == "🛠️ Maintenance Priority":
    st.header("🛠️ Maintenance Priority Analysis")

    if st.button("▶️ Run Analysis", type="primary", use_container_width=True):
        with st.spinner("Analyzing maintenance priorities..."):
            result = predict("maintenance-priority")

        if not api_error(result):
            preds = result.get("predictions", [])
            immediate = sum(1 for p in preds if p.get("action") == "IMMEDIATE")
            monitor   = sum(1 for p in preds if p.get("action") == "MONITOR")

            c1, c2, c3 = st.columns(3)
            c1.metric("🔴 Immediate", immediate)
            c2.metric("🟢 Monitor",   monitor)
            c3.metric("📋 Total",      len(preds))
            st.divider()

            if preds:
                fig = go.Figure(data=[go.Pie(
                    labels=["Immediate", "Monitor"], values=[immediate, monitor],
                    marker_colors=["#d62728", "#2ca02c"],
                )])
                fig.update_layout(title="Maintenance Action Distribution")
                st.plotly_chart(fig, use_container_width=True)

                st.subheader("Tasks (sorted by priority)")
                df = pd.DataFrame(preds)
                if "maintenance_priority" in df.columns:
                    df = df.sort_values("maintenance_priority", ascending=False)
                st.dataframe(df, use_container_width=True)

            with st.expander("🔍 Raw JSON Response"):
                st.json(result)


# ── Page 4: Cost Anomaly ──────────────────────────────────────────────────

elif page == "💰 Cost Anomaly":
    st.header("💰 Cost Anomaly Detection")

    if st.button("▶️ Run Detection", type="primary", use_container_width=True):
        with st.spinner("Detecting cost anomalies..."):
            result = predict("cost-anomaly")

        if not api_error(result):
            anomalies = result.get("anomalies", [])

            c1, c2 = st.columns(2)
            c1.metric("⚠️ Anomalies Detected", len(anomalies))
            if anomalies:
                avg_var = sum(abs(a.get("variance_pct", 0)) for a in anomalies) / len(anomalies)
                c2.metric("📊 Avg |Variance %|", f"{avg_var:.1f}%")
            st.divider()

            if anomalies:
                df = pd.DataFrame(anomalies)
                if "variance_pct" in df.columns:
                    df = df.sort_values("variance_pct", key=lambda s: s.abs(), ascending=False)

                    fig = go.Figure(data=[go.Histogram(x=df["variance_pct"], nbinsx=30, marker_color="#1f77b4")])
                    fig.update_layout(title="Variance % Distribution", xaxis_title="Variance %", yaxis_title="Frequency")
                    st.plotly_chart(fig, use_container_width=True)

                st.subheader("Detected Anomalies")
                st.dataframe(df, use_container_width=True)
            else:
                st.info("✅ No anomalies detected.")

            with st.expander("🔍 Raw JSON Response"):
                st.json(result)


# ── Page 5: What-If Simulation ────────────────────────────────────────────

elif page == "🎯 What-If Simulation":
    st.header("🎯 What-If Production Simulation")

    if st.button("▶️ Run Simulation", type="primary", use_container_width=True):
        with st.spinner("Running simulation..."):
            result = predict("whatif-simulation")

        if not api_error(result):
            scenarios = result.get("scenarios", {})
            correlations = result.get("correlations", [])

            if scenarios:
                baseline = scenarios.get("baseline_daily_volume", 0)
                combined = scenarios.get("combined_improvement", 0)

                c1, c2, c3 = st.columns(3)
                c1.metric("Baseline Daily Volume", f"{baseline:.1f}")
                c2.metric("Combined Improvement", f"{combined:.1f}", delta=f"{combined - baseline:+.1f}")
                c3.metric("Method", scenarios.get("method", "N/A"))
                st.divider()

                # Scenario comparison
                scen_keys = [
                    ("baseline_daily_volume", "Baseline"),
                    ("increase_ops_20pct", "Ops +20%"),
                    ("reduce_downtime_30pct", "Downtime -30%"),
                    ("combined_improvement", "Combined"),
                ]
                labels = [lbl for k, lbl in scen_keys if k in scenarios]
                values = [scenarios[k] for k, _ in scen_keys if k in scenarios]
                if values:
                    fig = go.Figure(data=[go.Bar(x=labels, y=values, marker_color="#1f77b4")])
                    fig.update_layout(title="Daily Volume by Scenario", yaxis_title="Volume")
                    st.plotly_chart(fig, use_container_width=True)

                m1, m2 = st.columns(2)
                m1.metric("Est. Monthly (Baseline)", f"{scenarios.get('estimated_monthly_baseline', 0):,.0f}")
                m2.metric("Est. Monthly (Optimized)", f"{scenarios.get('estimated_monthly_optimized', 0):,.0f}")

            if correlations:
                st.divider()
                st.subheader("📊 Correlations")
                st.dataframe(pd.DataFrame(correlations), use_container_width=True)

            with st.expander("🔍 Raw JSON Response"):
                st.json(result)


# ── Page 6: Fleet Optimization ────────────────────────────────────────────

elif page == "🚚 Fleet Optimization":
    st.header("🚚 Fleet Optimization")

    if st.button("▶️ Run Optimization", type="primary", use_container_width=True):
        with st.spinner("Clustering fleet..."):
            result = predict("fleet-optimization")

        if not api_error(result):
            clusters = result.get("clusters", [])

            if clusters:
                df = pd.DataFrame(clusters)

                c1, c2, c3 = st.columns(3)
                c1.metric("🚜 Equipment", len(df))
                c2.metric("🔢 Clusters", df["cluster"].nunique() if "cluster" in df.columns else 0)
                if "utilization_rate" in df.columns:
                    c3.metric("📈 Avg Utilization", f"{df['utilization_rate'].mean():.1f}%")
                st.divider()

                # Cluster sizes
                if "cluster" in df.columns:
                    counts = df["cluster"].value_counts().sort_index()
                    fig = go.Figure(data=[go.Bar(x=[f"Cluster {i}" for i in counts.index], y=counts.values, marker_color="#1f77b4")])
                    fig.update_layout(title="Equipment per Cluster", yaxis_title="Count")
                    st.plotly_chart(fig, use_container_width=True)

                # Utilization vs cost scatter
                if {"utilization_rate", "cost_per_hour", "cluster"}.issubset(df.columns):
                    fig2 = go.Figure(data=[go.Scatter(
                        x=df["utilization_rate"], y=df["cost_per_hour"],
                        mode="markers", marker=dict(color=df["cluster"], colorscale="Viridis", showscale=True),
                        text=df["equipment_name"],
                    )])
                    fig2.update_layout(title="Utilization vs Cost per Hour", xaxis_title="Utilization %", yaxis_title="Cost/Hour")
                    st.plotly_chart(fig2, use_container_width=True)

                st.subheader("Fleet Details")
                st.dataframe(df, use_container_width=True)
            else:
                st.info("No cluster data returned.")

            with st.expander("🔍 Raw JSON Response"):
                st.json(result)


# ── Page 7: Full Pipeline ─────────────────────────────────────────────────

elif page == "📈 Full Pipeline":
    st.header("📈 Full ML Pipeline")
    st.info("Runs all models and returns an executive summary.")

    if st.button("▶️ Run Full Pipeline", type="primary", use_container_width=True):
        with st.spinner("Running all models — this may take a moment..."):
            result = predict("all")

        if not result or result.get("status") == "error":
            st.error(f"API Error: {(result or {}).get('message', 'Cannot connect to API')}")
        else:
            summary = result.get("executive_summary", {})
            if summary:
                st.subheader("📊 Executive Summary")
                c1, c2, c3, c4 = st.columns(4)
                c1.metric("High Risk Equip.", summary.get("high_risk_equipment", 0))
                c2.metric("Assessed", summary.get("total_equipment_assessed", 0))
                c3.metric("Urgent Maint.", summary.get("urgent_maintenance_actions", 0))
                c4.metric("Cost Anomalies", summary.get("cost_anomalies_detected", 0))

                c5, c6, c7, c8 = st.columns(4)
                c5.metric("Monthly Baseline", f"{summary.get('estimated_monthly_volume_baseline', 0):,.0f}")
                c6.metric("Monthly Optimized", f"{summary.get('estimated_monthly_volume_optimized', 0):,.0f}")
                c7.metric("Fleet Clusters", summary.get("fleet_clusters", 0))
                c8.metric("Fleet High Prio.", summary.get("fleet_high_priority_count", 0))

                recs = summary.get("recommendations", [])
                if recs:
                    st.subheader("📋 Recommendations")
                    for i, rec in enumerate(recs, 1):
                        st.write(f"{i}. {rec}")

            st.divider()
            models = result.get("models", {})
            if models:
                tabs = st.tabs([f"🔹 {k}" for k in models])
                for tab, (name, mdata) in zip(tabs, models.items()):
                    with tab:
                        st.json(mdata)

            st.caption(f"Version: {result.get('version', '?')} | DB: {result.get('database', '?')} | {result.get('timestamp', '')}")

            with st.expander("🔍 Full Raw JSON"):
                st.json(result)


# ── Page 8: Custom Input ──────────────────────────────────────────────────

elif page == "✏️ Custom Input":
    st.header("✏️ Custom Data Input & Testing")

    model_target = st.selectbox(
        "Prediction Target",
        [
            "equipment-failure", "maintenance-priority", "cost-anomaly",
            "whatif-simulation", "fleet-optimization",
        ],
    )

    examples = {
        "equipment-failure": {"records": [{
            "date": "2025-05-01", "site_name": "Tambang Nikel E",
            "equipment_name": "Bulldozer BD-002", "equipment_type": "Bulldozer",
            "operating_hours": 286.0, "downtime_hours": 23.0,
            "fuel_consumption": 1667.0, "maintenance_cost": 849403.0,
        }]},
        "cost-anomaly": {"records": [{
            "date": "2022-01-02", "site_name": "Area Tambang C",
            "project_name": "Project Alpha",
            "budgeted_cost": 171870.0, "actual_cost": 127873.0,
        }]},
        "whatif-simulation": {"records": [{
            "date": "2025-05-02", "site_name": "Area Tambang C",
            "material_name": "Iron", "produced_volume": 56.0, "unit_cost": 161.0,
        }]},
    }
    example = examples.get(model_target, examples["equipment-failure"])

    st.caption("Enter records as JSON (or leave empty to use API sample data):")
    st.code(json.dumps(example, indent=2), language="json")

    json_input = st.text_area("JSON payload", height=280, placeholder='{"records": [...]}')

    if st.button("▶️ Run Prediction", type="primary", use_container_width=True):
        records = None
        if json_input.strip():
            try:
                parsed = json.loads(json_input)
                records = parsed.get("records", parsed) if isinstance(parsed, dict) else parsed
            except json.JSONDecodeError as exc:
                st.error(f"Invalid JSON: {exc}")
                st.stop()

        with st.spinner("Predicting..."):
            result = predict(model_target, records)

        if result and result.get("status") == "ok":
            st.success("✅ Prediction complete!")
        st.json(result)


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
