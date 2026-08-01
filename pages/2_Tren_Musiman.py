# =============================================================================
# TREN & MUSIMAN — Heat & Spice Spatial Intelligence
# Chili Price Intelligence Platform
# =============================================================================

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from utils import (
    P, DATA_PATH, COMMODITY_LABELS, MONTH_ABB,
    inject_css, render_sidebar, page_header, section_header, footer,
    stat_card, status_chip, get_chili_wfp, get_national_monthly,
    get_provincial_monthly, blayout,
)

st.set_page_config(
    page_title="Heat & Spice — Trends & Seasonality",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded",
)
inject_css()
commodity_sel = render_sidebar(DATA_PATH)

# ── DATA ──────────────────────────────────────────────────────────────────────
with st.spinner("Memuat data tren historis..."):
    chili_raw = get_chili_wfp(DATA_PATH, commodity_sel)
    natl_mdf = get_national_monthly(DATA_PATH, commodity_sel)
    prov_list = ["NASIONAL"] + sorted(chili_raw["admin1"].dropna().unique().tolist())

# ── HEADER & REGIONAL FILTER ──────────────────────────────────────────────────
# Build custom header widgets (region selector rendered inline via a narrow column
# so it sits in the same row as the title, matching the reference layout, instead
# of appearing as a separate full-width row above the header)
right_widgets = ""

col_title, col_region = st.columns([3.4, 1])
with col_title:
    page_header(
        supra="ANALYTIC INTENSITY",
        title="Tren Musiman",
        right_widget=right_widgets
    )
with col_region:
    idx_prov = prov_list.index("Jawa Timur") if "Jawa Timur" in prov_list else 0
    sel_prov = st.selectbox(
        "PILIH REGION",
        prov_list, index=idx_prov, key="trend_prov_sel",
        label_visibility="collapsed"
    )

# Load data based on selection
if sel_prov == "NASIONAL":
    mdf = natl_mdf.copy()
else:
    mdf = get_provincial_monthly(DATA_PATH, commodity_sel, sel_prov)

if mdf.empty:
    st.warning(f"Data tidak tersedia untuk region: {sel_prov}")
    st.stop()

# Prepare derived data
mdf["MA12"] = mdf["Price"].rolling(12, min_periods=1).mean()
mdf["MA3"]  = mdf["Price"].rolling(3, min_periods=1).mean()
current_p   = mdf["Price"].iloc[-1]
prev_p      = mdf["Price"].iloc[-2] if len(mdf) > 1 else current_p
mom_pct     = (current_p - prev_p) / prev_p * 100 if prev_p > 0 else 0

mdf["roll12_std"]  = mdf["Price"].rolling(12).std()
mdf["cv"] = mdf["roll12_std"] / mdf["MA12"] * 100
annual_cv = mdf["cv"].iloc[-1] if not pd.isna(mdf["cv"].iloc[-1]) else 0



# ── REGIONAL PRICE CYCLE ANALYSIS (Smooth line) ──────────────────────────────
mdf_recent = mdf[mdf["Date"] >= "2020-01-01"].copy()
natl_recent = natl_mdf[natl_mdf["Date"].isin(mdf_recent["Date"])].copy()

fig_cycle = go.Figure()
# National baseline
fig_cycle.add_trace(go.Scatter(
    x=natl_recent["Date"], y=natl_recent["Price"],
    mode="lines", line=dict(color=P["surface_top"], width=2),
    name="National Average", hoverinfo="skip"
))
# Regional line (smooth spline-like using shape)
fig_cycle.add_trace(go.Scatter(
    x=mdf_recent["Date"], y=mdf_recent["Price"],
    mode="lines", line=dict(color=P["cream"], width=2, shape="spline"),
    name=sel_prov,
    hovertemplate="%{x|%b %Y}<br>Rp %{y:,.0f}/kg<extra></extra>"
))
fig_cycle.add_annotation(
    x=mdf_recent["Date"].iloc[len(mdf_recent)//2],
    y=mdf_recent["Price"].mean(),
    text="REGIONAL CYCLE VISUALIZATION",
    showarrow=False, font=dict(color=P["surface_top"], size=10, family="JetBrains Mono"),
    opacity=0.5
)

# Local variance: regional average vs national average over the same recent window
# (previously this reused mom_pct — the region's own month-over-month change — which
# is not a comparison against the national figure at all)
natl_recent_avg = natl_recent["Price"].mean()
local_avg = mdf_recent["Price"].mean()
local_variance_pct = (
    (local_avg - natl_recent_avg) / natl_recent_avg * 100 if natl_recent_avg > 0 else 0
)

lo_cyc = blayout("", h=250, legend=True)
lo_cyc["xaxis"]["showgrid"] = False
lo_cyc["yaxis"]["showgrid"] = True
lo_cyc["plot_bgcolor"] = P["card"]
lo_cyc["paper_bgcolor"] = P["card"]
lo_cyc["margin"] = dict(l=20, r=20, t=10, b=20)
fig_cycle.update_layout(**lo_cyc)
fig_cycle.update_layout(
    legend=dict(
        orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1,
        font=dict(color=P["muted"], size=10, family="JetBrains Mono"),
        bgcolor="rgba(0,0,0,0)"
    )
)

st.markdown(
    f"<div style='background:{P['card']};border:1px solid {P['border']};border-radius:8px;padding:20px;'>"
    f"<div style='display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:10px;'>"
    f"<div>"
    f"<div style='font-family:Outfit,sans-serif;font-size:18px;font-weight:700;color:{P['cream']};'>Regional Price Cycle Analysis</div>"
    f"<div style='font-family:Outfit,sans-serif;font-size:12px;color:{P['muted']};'>Isolasi Tren & Siklus Harga Daerah: {sel_prov}</div>"
    f"</div>"
    f"<div style='text-align:right;'>"
    f"<div style='font-family:\"JetBrains Mono\",monospace;font-size:9px;color:{P['muted']};text-transform:uppercase;'>LOCAL VARIANCE</div>"
    f"<div style='font-family:\"JetBrains Mono\",monospace;font-size:14px;color:{P['cream']};'>{local_variance_pct:+.1f}% vs National</div>"
    f"</div></div>",
    unsafe_allow_html=True
)
st.plotly_chart(fig_cycle, use_container_width=True, config={"displayModeBar": False})

st.markdown("<div style='height:24px;'></div>", unsafe_allow_html=True)

# ── MAIN TRENDS ───────────────────────────────────────────────────────────────
c_main = st.container()

with c_main:
    mdf_plot = mdf[mdf["Date"] >= "2020-01-01"]
    min_yr = int(mdf_plot["Date"].dt.year.min())
    max_yr = int(mdf_plot["Date"].dt.year.max())
    lt_avg = mdf["Price"].mean()
    latest_year = int(mdf["Date"].dt.year.max())
    cy_peak = mdf.loc[mdf["Date"].dt.year == latest_year, "Price"].max()
    growth = (mdf["Price"].iloc[-1] - mdf["Price"].iloc[0]) / mdf["Price"].iloc[0] * 100

    st.markdown(
        f"<div style='background:{P['card']};border:1px solid {P['border']};border-radius:8px;padding:20px;'>"
        f"<div style='display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:10px;'>"
        f"<div>"
        f"<div style='font-family:Outfit,sans-serif;font-size:18px;font-weight:700;color:{P['cream']};'>Price Trajectory ({min_yr} – {max_yr})</div>"
        f"<div style='font-family:Outfit,sans-serif;font-size:12px;color:{P['muted']};'>Pergerakan Harga Historis & Rata-rata Bergerak (MA3 & MA12)</div>"
        f"</div>"
        f"<div style='display:flex;gap:32px;text-align:right;'>"
        f"<div>"
        f"<div style='font-family:\"JetBrains Mono\",monospace;font-size:9px;color:{P['muted']};text-transform:uppercase;'>LONG TERM AVG</div>"
        f"<div style='font-family:\"JetBrains Mono\",monospace;font-size:14px;color:{P['cream']};font-weight:700;'>Rp {lt_avg:,.0f}</div>"
        f"</div>"
        f"<div>"
        f"<div style='font-family:\"JetBrains Mono\",monospace;font-size:9px;color:{P['muted']};text-transform:uppercase;'>CY_{latest_year} PEAK</div>"
        f"<div style='font-family:\"JetBrains Mono\",monospace;font-size:14px;color:{P['secondary']};font-weight:700;'>Rp {cy_peak:,.0f}</div>"
        f"</div>"
        f"<div>"
        f"<div style='font-family:\"JetBrains Mono\",monospace;font-size:9px;color:{P['muted']};text-transform:uppercase;'>TOTAL GROWTH</div>"
        f"<div style='font-family:\"JetBrains Mono\",monospace;font-size:14px;color:{P['cream']};font-weight:700;'>{growth:+.1f}%</div>"
        f"</div>"
        f"</div></div>",
        unsafe_allow_html=True
    )
    
    fig_hist = go.Figure()
    fig_hist.add_trace(go.Scatter(
        x=mdf_plot["Date"], y=mdf_plot["Price"],
        mode="lines", name="Price",
        line=dict(color=P["cream"], width=1.5),
        hovertemplate="<b>%{x|%b %Y}</b><br>Rp %{y:,.0f}/kg<extra></extra>"
    ))
    fig_hist.add_trace(go.Scatter(
        x=mdf_plot["Date"], y=mdf_plot["MA12"],
        mode="lines", name="MA12",
        line=dict(color=P["primary"], width=2.5, dash="dash"),
    ))
    fig_hist.add_trace(go.Scatter(
        x=mdf_plot["Date"], y=mdf_plot["MA3"],
        mode="lines", name="MA3",
        line=dict(color=P["secondary"], width=1.5),
    ))
    lo_h = blayout("", h=320, legend=True)
    lo_h["plot_bgcolor"] = P["card"]
    lo_h["paper_bgcolor"] = P["card"]
    lo_h["margin"] = dict(l=20, r=20, t=10, b=20)
    fig_hist.update_layout(**lo_h)
    fig_hist.update_layout(
        legend=dict(
            orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1,
            font=dict(color=P["muted"], size=10, family="JetBrains Mono"),
            bgcolor="rgba(0,0,0,0)"
        )
    )
    st.plotly_chart(fig_hist, use_container_width=True, config={"displayModeBar": False})


st.markdown("<div style='height:24px;'></div>", unsafe_allow_html=True)



footer()
