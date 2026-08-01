# =============================================================================
# MODEL PROYEKSI — Heat & Spice Spatial Intelligence
# Chili Price Intelligence Platform
# =============================================================================

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from utils import (
    P, DATA_PATH, COMMODITY_LABELS, FEAT_COLS,
    inject_css, render_sidebar, page_header, section_header, footer,
    stat_card, status_chip, get_national_monthly, train_wfp_model,
    forecast_months_ahead, blayout,
)

st.set_page_config(
    page_title="Heat & Spice — Projection Engine",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded",
)
inject_css()
commodity_sel = render_sidebar(DATA_PATH)

with st.spinner("Melatih model prediksi..."):
    mdf       = get_national_monthly(DATA_PATH, commodity_sel)
    res_model = train_wfp_model(DATA_PATH, commodity_sel)
    fcast_df  = forecast_months_ahead(res_model, n=12)

current_price = mdf["Price"].iloc[-1]

# ── HEADER ────────────────────────────────────────────────────────────────────
page_header(
    supra="PROJECTION ENGINE V2.4",
    title="Model Proyeksi",
)

# ── PERFORMANCE CARDS ─────────────────────────────────────────────────────────
mae  = res_model["mae"]
mape = res_model["mape"]
r2   = res_model["r2"]

c1, c2, c3 = st.columns([1.5, 1, 1])

with c1:
    st.markdown(
        f"<div style='background:{P['card']};border:1px solid {P['border']};border-radius:8px;padding:16px 20px;height:120px;position:relative;'>"
        f"<div style='position:absolute;top:0;left:0;right:0;height:2px;background:linear-gradient(90deg,{P['primary']},{P['secondary']});'></div>"
        f"<div style='font-family:\"JetBrains Mono\",monospace;font-size:11px;color:{P['muted']};text-transform:uppercase;margin-bottom:4px;'>MODEL STATUS ⚙</div>"
        f"<div style='font-family:Outfit,sans-serif;font-size:14px;color:{P['cream']};margin-bottom:16px;'>Holt-Winters Seasonal + RF Engine</div>"
        f"<div style='font-family:\"JetBrains Mono\",monospace;font-size:11px;color:{P['primary']};'>(2020–2024 Base)</div>"
        f"</div>",
        unsafe_allow_html=True
    )

with c2:
    st.markdown(
        f"<div style='background:{P['card']};border:1px solid {P['border']};border-radius:8px;padding:16px 20px;height:120px;position:relative;'>"
        f"<div style='position:absolute;top:0;left:0;right:0;height:2px;background:linear-gradient(90deg,{P['tertiary']},transparent);'></div>"
        f"<div style='font-family:\"JetBrains Mono\",monospace;font-size:11px;color:{P['muted']};margin-bottom:12px;'>R² SCORE</div>"
        f"<div style='font-family:\"JetBrains Mono\",monospace;font-size:22px;color:{P['cream']};font-weight:700;'>{r2:.3f}</div>"
        f"</div>",
        unsafe_allow_html=True
    )

with c3:
    st.markdown(
        f"<div style='background:{P['card']};border:1px solid {P['border']};border-radius:8px;padding:16px 20px;height:120px;position:relative;'>"
        f"<div style='position:absolute;top:0;left:0;right:0;height:2px;background:linear-gradient(90deg,{P['secondary']},transparent);'></div>"
        f"<div style='font-family:\"JetBrains Mono\",monospace;font-size:11px;color:{P['muted']};margin-bottom:4px;'>MAPE (ERROR)</div>"
        f"<div style='font-family:\"JetBrains Mono\",monospace;font-size:22px;color:{P['cream']};font-weight:700;'>{mape:.2f}%</div>"
        f"</div>",
        unsafe_allow_html=True
    )


st.markdown("<div style='height:24px;'></div>", unsafe_allow_html=True)

# ── FORECAST CHART & FEATURE IMPORTANCE ───────────────────────────────────────
c_chart, c_feat = st.columns([2.5, 1])

with c_chart:
    st.markdown(
        f"<div style='display:flex;justify-content:space-between;align-items:center;margin-bottom:16px;'>"
        f"<div>"
        f"<div style='font-family:Outfit,sans-serif;font-size:16px;font-weight:700;color:{P['cream']};'>12-Month Seasonal Forecast</div>"
        f"<div style='font-family:Outfit,sans-serif;font-size:12px;color:{P['muted']};'>Proyeksi musiman dinamis 12-bulan ke depan (Juni 2024 – Mei 2025)</div>"
        f"</div>"
        f"</div>",
        unsafe_allow_html=True
    )

    tr_plot = res_model["tr"].tail(36)
    te_plot = res_model["te"]

    fig_fc = go.Figure()
    # Historical / Test line (dimmed)
    hist_concat = pd.concat([tr_plot, te_plot])
    fig_fc.add_trace(go.Scatter(
        x=hist_concat["Date"], y=hist_concat["Price"],
        mode="lines", name="Historical",
        line=dict(color=P["muted"], width=1.5, dash="dot"),
        hoverinfo="skip"
    ))
    # Confidence Interval
    fig_fc.add_trace(go.Scatter(
        x=pd.concat([fcast_df["Date"], fcast_df["Date"][::-1]]),
        y=pd.concat([fcast_df["Upper"], fcast_df["Lower"][::-1]]),
        fill="toself", fillcolor=P["secondary_a"],
        line=dict(color="rgba(0,0,0,0)"),
        showlegend=False, hoverinfo="skip"
    ))
    # Forecast line
    fig_fc.add_trace(go.Scatter(
        x=fcast_df["Date"], y=fcast_df["Forecast"],
        mode="lines+markers", name="Forecast",
        line=dict(color=P["primary"], width=2),
        marker=dict(size=6, color=P["primary"]),
        hovertemplate="<b>%{x|%b %y}</b><br>Rp %{y:,.0f}<extra></extra>"
    ))
    # Connecting point
    fig_fc.add_trace(go.Scatter(
        x=[hist_concat["Date"].iloc[-1], fcast_df["Date"].iloc[0]],
        y=[hist_concat["Price"].iloc[-1], fcast_df["Forecast"].iloc[0]],
        mode="lines", line=dict(color=P["primary"], width=2), showlegend=False, hoverinfo="skip"
    ))

    lo_fc = blayout("", h=380, legend=False)
    lo_fc["plot_bgcolor"] = P["card"]
    lo_fc["paper_bgcolor"] = P["card"]
    lo_fc["margin"] = dict(l=10, r=10, t=10, b=10)
    lo_fc["xaxis"]["tickformat"] = "%b %y"
    fig_fc.update_layout(**lo_fc)

    st.markdown(f"<div style='background:{P['card']};border:1px solid {P['border']};border-radius:8px;padding:20px;'>", unsafe_allow_html=True)
    st.plotly_chart(fig_fc, use_container_width=True, config={"displayModeBar": False})
    st.markdown("</div>", unsafe_allow_html=True)

with c_feat:
    fi = pd.Series(res_model["rf"].feature_importances_, index=FEAT_COLS).sort_values(ascending=False).head(8)
    bars_html = ""
    for k, v in fi.items():
        lbl = k.upper()
        pct = v * 100
        bars_html += (
            f"<div style='margin-bottom:16px;'>"
            f"<div style='display:flex;justify-content:space-between;font-family:\"JetBrains Mono\",monospace;font-size:10px;color:{P['muted']};margin-bottom:6px;'>"
            f"<span>{lbl}</span><span>{pct:.0f}%</span></div>"
            f"<div style='background:{P['surface_hi']};height:8px;border-radius:2px;'>"
            f"<div style='background:{P['primary']};height:8px;border-radius:2px;width:{pct}%;'></div></div>"
            f"</div>"
        )

    st.markdown(
        f"<div style='background:{P['card']};border:1px solid {P['border']};border-radius:8px;padding:20px;height:470px;overflow-y:auto;'>"
        f"<div style='font-family:Outfit,sans-serif;font-size:14px;font-weight:700;color:{P['cream']};margin-bottom:24px;'>Feature Importance</div>"
        f"{bars_html}"
        f"</div>",
        unsafe_allow_html=True
    )

st.markdown("<div style='height:24px;'></div>", unsafe_allow_html=True)

# ── MONTHLY PROJECTION INDEX ──────────────────────────────────────────────────
st.markdown(
    f"<div style='display:flex;align-items:center;gap:16px;margin-bottom:16px;'>"
    f"<div style='font-family:Outfit,sans-serif;font-size:14px;font-weight:700;color:{P['cream']};'>Monthly Price Projection Index (12-Month Horizon)</div>"
    f"<div style='flex:1;height:1px;background:{P['border']};'></div>"
    f"<div style='font-family:\"JetBrains Mono\",monospace;font-size:11px;color:{P['muted']};'>IDR / KILOGRAM</div>"
    f"</div>",
    unsafe_allow_html=True
)

# Render 12 months in 2 rows of 6 columns
for row_idx in [0, 6]:
    m_cols = st.columns(6)
    for col_idx in range(6):
        idx = row_idx + col_idx
        if idx >= len(fcast_df):
            break
        row = fcast_df.iloc[idx]
        prev_p = fcast_df.iloc[idx - 1]["Forecast"] if idx > 0 else current_price
        pct = (row["Forecast"] - prev_p) / prev_p * 100

        arrow = "↗" if pct >= 0 else "↘"
        arrow_clr = P["primary"] if pct >= 0 else P["emerald"]

        with m_cols[col_idx]:
            st.markdown(
                f"<div style='background:{P['card']};border:1px solid {P['border']};border-radius:6px;padding:14px;margin-bottom:12px;'>"
                f"<div style='font-family:\"JetBrains Mono\",monospace;font-size:11px;color:{P['muted']};text-transform:uppercase;margin-bottom:8px;'>{pd.Timestamp(row['Date']).strftime('%b %Y')}</div>"
                f"<div style='font-family:\"JetBrains Mono\",monospace;font-size:16px;font-weight:700;color:{P['cream']};margin-bottom:8px;'>Rp {row['Forecast']:,.0f}</div>"
                f"<div style='font-family:\"JetBrains Mono\",monospace;font-size:10px;color:{arrow_clr};'>{arrow} {pct:+.1f}% vs Prev</div>"
                f"</div>",
                unsafe_allow_html=True
            )

footer()
