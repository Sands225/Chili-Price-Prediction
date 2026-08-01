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

# ── DATA & MODEL ──────────────────────────────────────────────────────────────
with st.spinner("Melatih model prediksi..."):
    mdf       = get_national_monthly(DATA_PATH, commodity_sel)
    res_model = train_wfp_model(DATA_PATH, commodity_sel)
    fcast_df  = forecast_months_ahead(res_model, n=7)

current_price = mdf["Price"].iloc[-1]

# ── HEADER ────────────────────────────────────────────────────────────────────
right_badge = (
    f"<div style='border:1px solid {P['border']};border-radius:6px;padding:6px 12px;"
    f"display:flex;align-items:center;gap:10px;background:{P['card']};'>"
    f"<div style='width:24px;height:4px;background:{P['primary']};border-radius:2px;'></div>"
    f"<div style='font-family:\"JetBrains Mono\",monospace;font-size:10px;color:{P['cream']};letter-spacing:0.05em;'>LIVE FORECASTING ON</div>"
    f"</div>"
)
page_header(
    supra="PROJECTION ENGINE V2.4",
    title="Model Proyeksi",
    right_widget=right_badge
)

# ── PERFORMANCE CARDS ─────────────────────────────────────────────────────────
mae  = res_model["mae"]
mape = res_model["mape"]
r2   = res_model["r2"]

c1, c2, c3, c4 = st.columns([1.5, 1, 1, 1])

with c1:
    st.markdown(
        f"<div style='background:{P['card']};border:1px solid {P['border']};border-radius:8px;padding:16px 20px;height:120px;position:relative;'>"
        f"<div style='position:absolute;top:0;left:0;right:0;height:2px;background:linear-gradient(90deg,{P['primary']},{P['secondary']});'></div>"
        f"<div style='font-family:\"JetBrains Mono\",monospace;font-size:11px;color:{P['muted']};text-transform:uppercase;margin-bottom:4px;'>MODEL STATUS ⚙</div>"
        f"<div style='font-family:Outfit,sans-serif;font-size:14px;color:{P['cream']};margin-bottom:16px;'>Random Forest Regressor</div>"
        f"<div style='font-family:\"JetBrains Mono\",monospace;font-size:11px;color:{P['primary']};'>Ready & Fitted</div>"
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

with c4:
    st.markdown(
        f"<div style='background:{P['card']};border:1px solid {P['border']};border-radius:8px;padding:16px 20px;height:120px;position:relative;'>"
        f"<div style='position:absolute;top:0;left:0;right:0;height:2px;background:linear-gradient(90deg,{P['primary']},transparent);'></div>"
        f"<div style='font-family:\"JetBrains Mono\",monospace;font-size:11px;color:{P['muted']};margin-bottom:12px;'>CONFIDENCE BOUNDS</div>"
        f"<div style='font-family:\"JetBrains Mono\",monospace;font-size:14px;color:{P['cream']};margin-bottom:12px;'>Dynamically Expanded</div>"
        f"<div style='display:flex;align-items:center;gap:8px;'><span style='width:10px;height:10px;border-radius:50%;border:2px solid {P['muted']};'></span><span style='font-family:Outfit,sans-serif;font-size:12px;color:{P['muted']};'>Based on Forecast Horizon</span></div>"
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
        f"<div style='font-family:Outfit,sans-serif;font-size:16px;font-weight:700;color:{P['cream']};'>7-Month Recursive Forecast</div>"
        f"<div style='font-family:Outfit,sans-serif;font-size:12px;color:{P['muted']};'>Projected market volatility based on current supply-chain signals</div>"
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
    fi = pd.Series(res_model["rf"].feature_importances_, index=FEAT_COLS).sort_values(ascending=False).head(5)
    fi_labels = {
        "lag_1": "HISTORICAL LAGS",
        "lag_2": "HISTORICAL LAGS",
        "month_sin": "SEASONALITY (MONSOON DEP)",
        "roll3_mean": "MOMENTUM INDEX",
        "pct_1m": "VOLATILITY METRIC",
        "quarter": "MACRO CYCLE"
    }

    bars_html = ""
    for k, v in fi.items():
        lbl = fi_labels.get(k, k.upper())
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
        f"<div style='background:{P['card']};border:1px solid {P['border']};border-radius:8px;padding:20px;height:470px;'>"
        f"<div style='font-family:Outfit,sans-serif;font-size:14px;font-weight:700;color:{P['cream']};margin-bottom:24px;'>Feature Importance</div>"
        f"{bars_html}"
        f"</div>",
        unsafe_allow_html=True
    )

st.markdown("<div style='height:24px;'></div>", unsafe_allow_html=True)

# ── MONTHLY PROJECTION INDEX ──────────────────────────────────────────────────
st.markdown(
    f"<div style='display:flex;align-items:center;gap:16px;margin-bottom:16px;'>"
    f"<div style='font-family:Outfit,sans-serif;font-size:14px;font-weight:700;color:{P['cream']};'>Monthly Price Projection Index</div>"
    f"<div style='flex:1;height:1px;background:{P['border']};'></div>"
    f"<div style='font-family:\"JetBrains Mono\",monospace;font-size:11px;color:{P['muted']};'>IDR / KILOGRAM</div>"
    f"</div>",
    unsafe_allow_html=True
)

m_cols = st.columns(4)
for i, (_, row) in enumerate(fcast_df.head(4).iterrows()):
    pct = (row["Forecast"] - current_price) / current_price * 100
    if pct > 8:
        stat_lbl, stat_clr = "BULLISH", P["secondary"]
    elif pct < -5:
        stat_lbl, stat_clr = "VOLATILE", P["primary"]
    elif abs(pct) <= 2:
        stat_lbl, stat_clr = "NEUTRAL", P["muted"]
    else:
        stat_lbl, stat_clr = "STABLE", P["primary"] # the reference uses a reddish orange for STABLE

    arrow = "↗" if pct > 0 else "↘"
    arrow_clr = P["tertiary"] if pct > 0 else P["cream"]

    with m_cols[i]:
        st.markdown(
            f"<div style='background:{P['card']};border:1px solid {P['border']};border-radius:6px;padding:20px;'>"
            f"<div style='display:flex;justify-content:space-between;align-items:center;margin-bottom:16px;'>"
            f"<div style='font-family:\"JetBrains Mono\",monospace;font-size:11px;color:{P['muted']};text-transform:uppercase;'>{pd.Timestamp(row['Date']).strftime('%B %Y')}</div>"
            f"<div style='background:{stat_clr};color:#000;font-family:\"JetBrains Mono\",monospace;font-size:9px;font-weight:700;padding:2px 6px;border-radius:4px;'>{stat_lbl}</div>"
            f"</div>"
            f"<div style='font-family:\"JetBrains Mono\",monospace;font-size:20px;font-weight:700;color:{P['cream']};margin-bottom:12px;'>Rp {row['Forecast']:,.0f}</div>"
            f"<div style='font-family:\"JetBrains Mono\",monospace;font-size:12px;color:{arrow_clr};'>{arrow} {pct:+.1f}% vs Prev</div>"
            f"</div>",
            unsafe_allow_html=True
        )

footer()
