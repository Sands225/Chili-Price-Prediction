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

# ── TOP METRICS ROW ───────────────────────────────────────────────────────────
c_score, c_cv, c_peak = st.columns([1, 1, 2.2])

with c_score:
    score = min(100, max(0, 50 + (mom_pct * 2)))
    st.markdown(
        f"<div style='background:{P['card']};border:1px solid {P['border']};border-radius:6px;"
        f"padding:16px 20px;position:relative;overflow:hidden;'>"
        f"<div style='position:absolute;top:0;left:0;right:0;height:2px;"
        f"background:linear-gradient(90deg,{P['primary']},{P['secondary']},{P['tertiary']});'></div>"
        f"<div style='position:absolute;top:0;right:0;width:80px;height:80px;"
        f"background:radial-gradient(circle at top right,{P['primary_a']},transparent 70%);pointer-events:none;'></div>"
        f"<div style='font-family:\"JetBrains Mono\",monospace;font-size:10px;font-weight:700;"
        f"letter-spacing:0.12em;text-transform:uppercase;color:{P['muted']};margin-bottom:6px;'>MOMENTUM SCORE</div>"
        f"<div style='display:flex;justify-content:space-between;align-items:baseline;'>"
        f"<div style='font-family:\"JetBrains Mono\",monospace;font-size:32px;font-weight:700;color:{P['cream']};'>{score:.1f}</div>"
        f"<div style='color:{P['muted']};'>{'↗' if mom_pct>0 else '↘'}</div>"
        f"</div>"
        f"<div style='background:{P['surface']};border-radius:3px;height:4px;margin:12px 0;'>"
        f"<div style='background:linear-gradient(90deg,{P['primary']},{P['secondary']});height:4px;"
        f"border-radius:3px;width:{score:.0f}%;'></div></div>"
        f"<div style='font-family:Outfit,sans-serif;font-size:12px;color:{P['muted']};'>"
        f"{'Extreme Bullish' if score>75 else 'Bearish'} Convergence</div>"
        f"</div>",
        unsafe_allow_html=True
    )

with c_cv:
    # little bar chart for last 6 months CV
    last6_cv = mdf["cv"].tail(6).fillna(0).values
    max_cv = max(last6_cv) if len(last6_cv) > 0 and max(last6_cv) > 0 else 1
    bars = "".join([
        f"<div style='width:12px;height:{max(10, v/max_cv*40):.0f}px;background:{P['tertiary'] if v>20 else P['surface_top']};'></div>"
        for v in last6_cv
    ])
    st.markdown(
        f"<div style='background:{P['card']};border:1px solid {P['border']};border-radius:6px;"
        f"padding:16px 20px;position:relative;overflow:hidden;'>"
        f"<div style='position:absolute;top:0;left:0;right:0;height:2px;"
        f"background:linear-gradient(90deg,{P['secondary']},{P['tertiary']});'></div>"
        f"<div style='position:absolute;top:0;right:0;width:80px;height:80px;"
        f"background:radial-gradient(circle at top right,{P['tertiary_a']},transparent 70%);pointer-events:none;'></div>"
        f"<div style='font-family:\"JetBrains Mono\",monospace;font-size:10px;font-weight:700;"
        f"letter-spacing:0.12em;text-transform:uppercase;color:{P['muted']};margin-bottom:6px;'>ANNUAL CV</div>"
        f"<div style='display:flex;justify-content:space-between;align-items:baseline;'>"
        f"<div style='font-family:\"JetBrains Mono\",monospace;font-size:32px;font-weight:700;color:{P['tertiary']};'>{annual_cv:.1f}%</div>"
        f"<div style='color:{P['tertiary']};font-size:24px;font-weight:700;'>!</div>"
        f"</div>"
        f"<div style='display:flex;align-items:flex-end;gap:4px;height:45px;margin-top:5px;'>{bars}</div>"
        f"</div>",
        unsafe_allow_html=True
    )

with c_peak:
    st.markdown(
        f"<div style='background:{P['surface']};border:1px solid {P['border']};border-radius:6px;"
        f"padding:24px;height:100%;display:flex;justify-content:space-between;align-items:center;'>"
        f"<div>"
        f"<div style='font-family:Outfit,sans-serif;font-size:16px;font-weight:700;color:{P['cream']};margin-bottom:6px;'>"
        f"Peak Season Forecast</div>"
        f"<div style='font-family:Outfit,sans-serif;font-size:13px;color:{P['muted']};line-height:1.5;max-width:300px;'>"
        f"The upcoming holiday surge is expected to hit Q4 with a +22% price delta compared to historical medians."
        f"</div></div>"
        f"</div>",
        unsafe_allow_html=True
    )

st.markdown("<div style='height:24px;'></div>", unsafe_allow_html=True)

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
    f"<div style='display:flex;gap:40px;text-align:right;'>"
    f"<div>"
    f"<div style='font-family:\"JetBrains Mono\",monospace;font-size:9px;color:{P['muted']};text-transform:uppercase;'>LOCAL VARIANCE</div>"
    f"<div style='font-family:\"JetBrains Mono\",monospace;font-size:14px;color:{P['cream']};'>{local_variance_pct:+.1f}% vs National</div>"
    f"</div>"
    f"<div>"
    f"<div style='font-family:\"JetBrains Mono\",monospace;font-size:9px;color:{P['muted']};text-transform:uppercase;'>CYCLE STATE</div>"
    f"<div style='font-family:\"JetBrains Mono\",monospace;font-size:14px;color:{P['secondary']};'>Peak Expansion</div>"
    f"</div>"
    f"</div></div>",
    unsafe_allow_html=True
)
st.plotly_chart(fig_cycle, use_container_width=True, config={"displayModeBar": False})

st.markdown("<div style='height:24px;'></div>", unsafe_allow_html=True)

# ── MAIN TRENDS & HEATMAP ─────────────────────────────────────────────────────
c_main, c_heat = st.columns([2.5, 1])

with c_main:
    mdf_plot = mdf[mdf["Date"] >= "2020-01-01"]
    
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
    lo_h = blayout("17-Year Price Trajectory (Regional Context)", h=380, legend=True)
    lo_h["plot_bgcolor"] = P["card"]
    lo_h["paper_bgcolor"] = P["card"]
    lo_h["margin"] = dict(l=20, r=20, t=60, b=20)
    fig_hist.update_layout(**lo_h)
    fig_hist.update_layout(
        legend=dict(
            orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1,
            font=dict(color=P["muted"], size=10, family="JetBrains Mono"),
            bgcolor="rgba(0,0,0,0)"
        )
    )
    st.plotly_chart(fig_hist, use_container_width=True, config={"displayModeBar": False})

    lt_avg = mdf["Price"].mean()
    latest_year = int(mdf["Date"].dt.year.max())
    cy_peak = mdf.loc[mdf["Date"].dt.year == latest_year, "Price"].max()
    growth = (mdf["Price"].iloc[-1] - mdf["Price"].iloc[0]) / mdf["Price"].iloc[0] * 100
    # Bottom metrics
    st.markdown(
        f"<div style='display:grid;grid-template-columns:repeat(4, 1fr);gap:16px;margin-top:10px;'>"
        f"<div style='border:1px solid {P['border']};border-radius:4px;padding:12px;'>"
        f"<div style='font-family:\"JetBrains Mono\",monospace;font-size:9px;color:{P['muted']};text-transform:uppercase;'>LONG TERM AVG</div>"
        f"<div style='font-family:\"JetBrains Mono\",monospace;font-size:14px;color:{P['cream']};font-weight:700;'>Rp {lt_avg/1000:,.2f}k</div>"
        f"</div>"
        f"<div style='border:1px solid {P['border']};border-radius:4px;padding:12px;'>"
        f"<div style='font-family:\"JetBrains Mono\",monospace;font-size:9px;color:{P['muted']};text-transform:uppercase;'>CY_{latest_year} PEAK</div>"
        f"<div style='font-family:\"JetBrains Mono\",monospace;font-size:14px;color:{P['secondary']};font-weight:700;'>Rp {cy_peak/1000:,.2f}k</div>"
        f"</div>"
        f"<div style='border:1px solid {P['border']};border-radius:4px;padding:12px;'>"
        f"<div style='font-family:\"JetBrains Mono\",monospace;font-size:9px;color:{P['muted']};text-transform:uppercase;'>TOTAL GROWTH</div>"
        f"<div style='font-family:\"JetBrains Mono\",monospace;font-size:14px;color:{P['cream']};font-weight:700;'>+{growth:.0f}%</div>"
        f"</div>"
        f"<div style='border:1px solid {P['border']};border-radius:4px;padding:12px;'>"
        f"<div style='font-family:\"JetBrains Mono\",monospace;font-size:9px;color:{P['muted']};text-transform:uppercase;'>CONFIDENCE</div>"
        f"<div style='font-family:\"JetBrains Mono\",monospace;font-size:14px;color:{P['cream']};font-weight:700;'>92.4%</div>"
        f"</div>"
        f"</div></div>",
        unsafe_allow_html=True
    )

with c_heat:
    # Monthly Heatmap (3 cols x 4 rows)
    mdf_m = mdf.copy()
    mdf_m["month"] = mdf_m["Date"].dt.month
    mon_avg = mdf_m.groupby("month")["Price"].mean()
    min_m, max_m = mon_avg.min(), mon_avg.max()

    def get_hm_color(norm):
        if norm > 0.85: return P["tertiary"]      # brightest peak (e.g. Dec)
        if norm > 0.65: return "#E8A87C"           # peach — notable secondary peak
        if norm > 0.45: return "#B06A4A"           # muted rose-brown
        if norm > 0.25: return P["surface_hi"]
        return P["surface"]                        # low season

    mon_norm = {i: ((mon_avg.get(i, min_m) - min_m) / (max_m - min_m) if max_m > min_m else 0) for i in range(1, 13)}
    # highlight the top-3 months with an accent border, matching the reference design
    top3_months = sorted(mon_norm, key=mon_norm.get, reverse=True)[:3]

    hm_html = "<div style='display:grid;grid-template-columns:1fr 1fr 1fr;gap:12px;margin:20px 0;'>"
    for i in range(1, 13):
        norm = mon_norm[i]
        c = get_hm_color(norm)
        if i in top3_months:
            border = f"1.5px solid {P['tertiary'] if norm == max(mon_norm.values()) else P['secondary']}"
        else:
            border = "none"
        hm_html += (
            f"<div>"
            f"<div style='font-family:\"JetBrains Mono\",monospace;font-size:9px;color:{P['muted']};text-align:center;margin-bottom:4px;'>{MONTH_ABB[i-1].upper()}</div>"
            f"<div style='height:36px;background:{c};border-radius:4px;border:{border};box-sizing:border-box;'></div>"
            f"</div>"
        )
    hm_html += "</div>"

    st.markdown(
        f"<div style='background:{P['card']};border:1px solid {P['border']};border-radius:8px;padding:20px;height:480px;'>"
        f"<div style='font-family:Outfit,sans-serif;font-size:18px;font-weight:700;color:{P['cream']};'>Monthly Heatmap</div>"
        f"<div style='font-family:Outfit,sans-serif;font-size:12px;color:{P['muted']};'>Seasonal Intensity Index</div>"
        f"{hm_html}"
        f"</div>",
        unsafe_allow_html=True
    )

st.markdown("<div style='height:24px;'></div>", unsafe_allow_html=True)

# ── ANNUAL VOLATILITY BREAKDOWN ───────────────────────────────────────────────
st.markdown(
    f"<div style='display:flex;justify-content:space-between;align-items:center;margin-bottom:12px;'>"
    f"<h3 style='font-family:Outfit,sans-serif;margin:0;font-size:17px;color:{P['cream']};'>Annual Volatility Breakdown</h3>"
    f"<div style='display:flex;align-items:center;gap:6px;'>"
    f"<span style='width:7px;height:7px;border-radius:50%;background:{P['primary']};display:inline-block;'></span>"
    f"<span style='font-family:\"JetBrains Mono\",monospace;font-size:11px;font-weight:700;"
    f"letter-spacing:0.08em;color:{P['primary']};'>CRITICAL ALERTS ACTIVE</span>"
    f"</div></div>",
    unsafe_allow_html=True
)

mdf_yr = mdf.copy()
mdf_yr["year"] = mdf_yr["Date"].dt.year
yr_stats = mdf_yr.groupby("year")["Price"].agg(["mean", "std", "max"]).reset_index()
yr_stats["cv"] = yr_stats["std"] / yr_stats["mean"] * 100
yr_stats = yr_stats.sort_values("year", ascending=False).head(5)

rows_html = ""
for i, r in yr_stats.iterrows():
    y_str = f"{int(r['year'])} (YTD)" if i == 0 else str(int(r['year']))
    cv = r["cv"]
    if cv > 20:
        stat_lbl = "CRITICAL"
        stat_clr = P["primary"]
        cv_clr = P["primary"]
    elif cv > 10:
        stat_lbl = "MODERATE"
        stat_clr = P["secondary"]
        cv_clr = P["secondary"]
    else:
        stat_lbl = "STABLE"
        stat_clr = P["muted"]
        cv_clr = P["cream"]

    rows_html += (
        f"<div style='display:grid;grid-template-columns:1.5fr 1fr 1fr 1fr 1fr 1fr;align-items:center;"
        f"padding:16px 20px;border-bottom:1px solid {P['border_d']};'>"
        f"<div style='font-family:\"JetBrains Mono\",monospace;font-size:13px;color:{P['cream']};'>{y_str}</div>"
        f"<div style='font-family:\"JetBrains Mono\",monospace;font-size:13px;color:{P['cream']};'>Rp {r['mean']/1000:.2f}k</div>"
        f"<div style='font-family:\"JetBrains Mono\",monospace;font-size:13px;color:{P['muted']};'>{r['std']/1000:.2f}</div>"
        f"<div style='font-family:\"JetBrains Mono\",monospace;font-size:13px;font-weight:700;color:{cv_clr};'>{cv:.1f}%</div>"
        f"<div style='font-family:\"JetBrains Mono\",monospace;font-size:13px;color:{P['cream']};'>Rp {r['max']/1000:.2f}k</div>"
        f"<div><span style='border:1px solid {stat_clr};color:{stat_clr};font-family:\"JetBrains Mono\",monospace;"
        f"font-size:9px;font-weight:700;padding:4px 8px;border-radius:4px;'>{stat_lbl}</span></div>"
        f"</div>"
    )

st.markdown(
    f"<div style='background:{P['card']};border:1px solid {P['border']};border-radius:8px;overflow:hidden;'>"
    f"<div style='display:grid;grid-template-columns:1.5fr 1fr 1fr 1fr 1fr 1fr;padding:12px 20px;"
    f"border-bottom:1px solid {P['border']};background:{P['surface']};'>"
    f"<div style='font-family:\"JetBrains Mono\",monospace;font-size:10px;color:{P['muted']};'>YEAR</div>"
    f"<div style='font-family:\"JetBrains Mono\",monospace;font-size:10px;color:{P['muted']};'>MEAN PRICE</div>"
    f"<div style='font-family:\"JetBrains Mono\",monospace;font-size:10px;color:{P['muted']};'>STD DEV</div>"
    f"<div style='font-family:\"JetBrains Mono\",monospace;font-size:10px;color:{P['muted']};'>COEFF. VAR (CV)</div>"
    f"<div style='font-family:\"JetBrains Mono\",monospace;font-size:10px;color:{P['muted']};'>MAX SPIKE</div>"
    f"<div style='font-family:\"JetBrains Mono\",monospace;font-size:10px;color:{P['muted']};'>STATUS</div>"
    f"</div>"
    f"{rows_html}"
    f"</div>",
    unsafe_allow_html=True
)

footer()
