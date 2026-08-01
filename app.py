# =============================================================================
# EXECUTIVE DASHBOARD — Heat & Spice
# Chili Price Intelligence Platform
# =============================================================================

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

from utils import (
    P, DATA_PATH, COMMODITY_LABELS, MONTH_FULL,
    inject_css, render_sidebar, page_header, footer, insight_card,
    stat_card, status_chip, section_header,
    get_chili_wfp, get_national_monthly, train_wfp_model,
    forecast_months_ahead, blayout,
)

st.set_page_config(
    page_title="Heat & Spice — Executive Dashboard",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded",
)
inject_css()
commodity_sel = render_sidebar(DATA_PATH)

# ── DATA ─────────────────────────────────────────────────────────────────────
with st.spinner("Memuat data..."):
    mdf       = get_national_monthly(DATA_PATH, commodity_sel)
    chili_raw = get_chili_wfp(DATA_PATH, commodity_sel)
    res_model = train_wfp_model(DATA_PATH, commodity_sel)
    fcast_df  = forecast_months_ahead(res_model, n=7)

current_price = mdf["Price"].iloc[-1]
prev_price    = mdf["Price"].iloc[-2] if len(mdf) >= 2 else current_price
mom_change    = (current_price - prev_price) / prev_price * 100 if prev_price else 0.0

recent_cv = mdf["Price"].tail(12).std() / mdf["Price"].tail(12).mean()

df_clean  = chili_raw.dropna(subset=["market","price"])
mkt_stats = df_clean.groupby(["admin1","market"])["price"].agg(["mean","max","min"]).reset_index()
exp_mkt   = mkt_stats.loc[mkt_stats["mean"].idxmax()]
chp_mkt   = mkt_stats.loc[mkt_stats["mean"].idxmin()]
next_fc   = fcast_df["Forecast"].iloc[0]
fc_diff   = (next_fc - current_price) / current_price * 100

# YoY
yoy_prices        = mdf.copy()
yoy_prices["yr"]  = yoy_prices["Date"].dt.year
yoy_avg           = yoy_prices.groupby("yr")["Price"].mean()
yoy_change        = ((yoy_avg.iloc[-1] - yoy_avg.iloc[-2]) / yoy_avg.iloc[-2] * 100) if len(yoy_avg) >= 2 else 0

mdf_s           = mdf.copy()
mdf_s["month"]  = mdf_s["Date"].dt.month
peak_month_num  = mdf_s.groupby("month")["Price"].mean().idxmax()
peak_month_name = MONTH_FULL[peak_month_num - 1]

disparity_pct   = (exp_mkt["mean"] - chp_mkt["mean"]) / chp_mkt["mean"] * 100
direction       = "meningkat" if mom_change > 0 else "menurun"
yoy_dir         = "tumbuh" if yoy_change > 0 else "terkoreksi"

# ── STATUS ────────────────────────────────────────────────────────────────────
if recent_cv > 0.25 or abs(mom_change) > 12:
    status_bg   = P["primary"]
    status_text = "Status: Potensi Krisis Tinggi"
    status_desc = f"Pasokan regional berpotensi turun akibat tekanan musiman. Volatilitas {recent_cv*100:.1f}% — segera aktifkan protokol substitusi distribusi."
    status_icon = "⚠"
elif recent_cv > 0.15 or abs(mom_change) > 5:
    status_bg   = P["secondary"]
    status_text = "Status: Waspada Siklus Moderat"
    status_desc = f"Pergerakan harga berada dalam fase penyesuaian musiman. CV 12 bulan: {recent_cv*100:.1f}%. Pemantauan pasokan diperlukan."
    status_icon = "◈"
else:
    status_bg   = P["emerald"]
    status_text = "Status: Pasokan & Harga Terkendali"
    status_desc = f"Kondisi pasar relatif seimbang. CV 12 bulan: {recent_cv*100:.1f}%. Tidak ada sinyal krisis yang terdeteksi."
    status_icon = "◉"

# ── HEADER ────────────────────────────────────────────────────────────────────
right_badge = (
    f"<div style='background:{P['card']};border:1px solid {P['primary']};"
    f"border-radius:4px;padding:8px 14px;text-align:right;'>"
    f"<div style='font-family:\"JetBrains Mono\",monospace;font-size:9px;color:{P['muted']};'>VARIETAS AKTIF</div>"
    f"<div style='font-family:Outfit,sans-serif;font-size:13px;font-weight:700;color:{P['cream']};'>"
    f"{COMMODITY_LABELS[commodity_sel]}</div>"
    f"</div>"
)
page_header(
    supra="FORECASTING VOLATILITY: BIRD'S EYE VIEW",
    title="Overview",
    right_widget=right_badge
)

# ── ALERT BANNER ──────────────────────────────────────────────────────────────
st.markdown(
    f"<div style='background:{status_bg}22;border:1px solid {status_bg};border-radius:6px;"
    f"padding:14px 20px;margin-bottom:20px;"
    f"display:flex;justify-content:space-between;align-items:center;'>"
    f"<div style='display:flex;align-items:center;gap:14px;'>"
    f"<span style='font-size:20px;color:{status_bg};'>{status_icon}</span>"
    f"<div>"
    f"<div style='font-family:Outfit,sans-serif;font-size:15px;font-weight:700;color:{status_bg};'>{status_text}</div>"
    f"<div style='font-family:Outfit,sans-serif;font-size:12px;color:{P['cream']};opacity:0.85;margin-top:2px;'>{status_desc}</div>"
    f"</div></div>"
    f"</div>",
    unsafe_allow_html=True
)

# ── KPI CARDS ─────────────────────────────────────────────────────────────────
k1, k2, k3, k4 = st.columns(4)
with k1:
    mom_clr = P["primary"] if mom_change > 5 else (P["emerald"] if mom_change < -2 else P["tertiary"])

    # Mini bar sparkline — last 7 months, normalized to card height
    spark_vals = mdf["Price"].tail(7).tolist()
    spark_max  = max(spark_vals) if spark_vals else 1
    spark_min  = min(spark_vals) if spark_vals else 0
    spark_rng  = (spark_max - spark_min) or 1
    bars_html  = ""
    for i, v in enumerate(spark_vals):
        h_pct = 25 + (v - spark_min) / spark_rng * 75  # keep a visible min height
        is_last = i == len(spark_vals) - 1
        bar_clr = P["primary"] if is_last else P["surface_hi"]
        bars_html += (
            f"<div style='flex:1;height:{h_pct:.0f}%;background:{bar_clr};"
            f"border-radius:1px;'></div>"
        )

    st.markdown(
        f"<div style='background:{P['card']};border:1px solid {P['border']};border-radius:6px;"
        f"padding:16px 18px;position:relative;overflow:hidden;'>"
        f"<div style='position:absolute;top:0;left:0;right:0;height:2px;"
        f"background:linear-gradient(90deg,{P['primary']},{P['secondary']},{P['tertiary']});'></div>"
        f"<div style='font-family:\"JetBrains Mono\",monospace;font-size:10px;font-weight:700;"
        f"letter-spacing:0.12em;text-transform:uppercase;color:{P['muted']};margin-bottom:4px;'>AVG PRICE (NATL)</div>"
        f"<div style='display:flex;justify-content:space-between;align-items:flex-end;gap:10px;'>"
        f"<div>"
        f"<div style='font-family:\"JetBrains Mono\",monospace;font-size:22px;font-weight:700;color:{P['cream']};'>"
        f"Rp {current_price:,.0f}<span style='font-size:12px;color:{P['muted']};'>/kg</span></div>"
        f"<div style='font-family:\"JetBrains Mono\",monospace;font-size:11px;color:{mom_clr};margin-top:4px;'>"
        f"{'↑' if mom_change>0 else '↓'} {abs(mom_change):.1f}% MoM</div>"
        f"</div>"
        f"<div style='display:flex;align-items:flex-end;gap:3px;height:36px;width:80px;flex-shrink:0;'>{bars_html}</div>"
        f"</div>"
        f"</div>",
        unsafe_allow_html=True
    )

with k2:
    mkt_count   = df_clean["market"].nunique()
    mkt_cv      = (
        df_clean.groupby(["admin1","market"])["price"].agg(["mean","std"])
        .assign(cv=lambda d: d["std"] / d["mean"] * 100)
        .dropna()
    )
    volatile_hub_count = int((mkt_cv["cv"] > mkt_cv["cv"].median()).sum())
    st.markdown(
        f"<div style='background:{P['card']};border:1px solid {P['border']};border-radius:6px;"
        f"padding:16px 18px;position:relative;overflow:hidden;'>"
        f"<div style='position:absolute;top:0;left:0;right:0;height:2px;"
        f"background:linear-gradient(90deg,{P['primary']},{P['secondary']},{P['tertiary']});'></div>"
        f"<div style='font-family:\"JetBrains Mono\",monospace;font-size:10px;font-weight:700;"
        f"letter-spacing:0.12em;text-transform:uppercase;color:{P['muted']};margin-bottom:4px;'>ACTIVE MARKET HUBS</div>"
        f"<div style='font-family:\"JetBrains Mono\",monospace;font-size:22px;font-weight:700;color:{P['cream']};'>"
        f"{mkt_count} <span style='font-size:12px;color:{P['muted']};font-weight:400;'>Markets</span></div>"
        f"<div style='font-family:Outfit,sans-serif;font-size:11px;color:{P['muted']};margin-top:4px;'>"
        f"{volatile_hub_count} Hubs reporting volatility</div>"
        f"</div>",
        unsafe_allow_html=True
    )

with k3:
    conf_pct = min(99, res_model["r2"] * 100)
    fc_clr   = P["primary"] if fc_diff > 5 else (P["secondary"] if fc_diff > 0 else P["emerald"])
    st.markdown(
        f"<div style='background:{P['card']};border:1px solid {P['border']};border-radius:6px;"
        f"padding:16px 18px;position:relative;overflow:hidden;'>"
        f"<div style='position:absolute;top:0;left:0;right:0;height:2px;"
        f"background:linear-gradient(90deg,{P['primary']},{P['secondary']},{P['tertiary']});'></div>"
        f"<div style='font-family:\"JetBrains Mono\",monospace;font-size:10px;font-weight:700;"
        f"letter-spacing:0.12em;text-transform:uppercase;color:{P['muted']};margin-bottom:4px;'>"
        f"30D PROJECTION {status_chip('HIGH CONFIDENCE' if conf_pct>80 else 'MODERATE', P['tertiary'] if conf_pct>80 else P['secondary'])}</div>"
        f"<div style='font-family:\"JetBrains Mono\",monospace;font-size:22px;font-weight:700;color:{P['cream']};'>"
        f"Rp {next_fc:,.0f}</div>"
        f"<div style='display:flex;align-items:center;gap:8px;margin-top:6px;'>"
        f"<div style='flex:1;background:{P['surface']};border-radius:3px;height:3px;'>"
        f"<div style='background:{fc_clr};height:3px;border-radius:3px;width:{conf_pct:.0f}%;'></div></div>"
        f"<span style='font-family:\"JetBrains Mono\",monospace;font-size:10px;color:{P['muted']};'>{conf_pct:.0f}%</span>"
        f"</div>"
        f"<div style='font-family:\"JetBrains Mono\",monospace;font-size:10px;color:{fc_clr};margin-top:3px;'>{fc_diff:+.1f}% est.</div>"
        f"</div>",
        unsafe_allow_html=True
    )

with k4:
    stability   = "CRITICAL" if recent_cv > 0.25 else ("MODERATE" if recent_cv > 0.15 else "STABLE")
    stab_clr    = P["primary"] if recent_cv > 0.25 else (P["tertiary"] if recent_cv > 0.15 else P["emerald"])
    trend_arrow = "↓" if mom_change < 0 else "↑"
    st.markdown(
        f"<div style='background:{P['card']};border:1px solid {P['border']};border-radius:6px;"
        f"padding:16px 18px;position:relative;overflow:hidden;'>"
        f"<div style='position:absolute;top:0;left:0;right:0;height:2px;"
        f"background:linear-gradient(90deg,{P['primary']},{P['secondary']},{P['tertiary']});'></div>"
        f"<div style='display:flex;justify-content:space-between;align-items:flex-start;'>"
        f"<div style='font-family:\"JetBrains Mono\",monospace;font-size:10px;font-weight:700;"
        f"letter-spacing:0.12em;text-transform:uppercase;color:{P['muted']};margin-bottom:4px;'>SUPPLY STABILITY</div>"
        f"<span style='color:{stab_clr};font-size:13px;'>{trend_arrow}</span>"
        f"</div>"
        f"<div style='font-family:Outfit,sans-serif;font-size:22px;font-weight:800;color:{stab_clr};'>{stability}</div>"
        f"<div style='font-family:Outfit,sans-serif;font-size:11px;color:{P['muted']};margin-top:3px;'>"
        f"CV 12-bln: {recent_cv*100:.1f}% · Puncak: {peak_month_name}</div>"
        f"</div>",
        unsafe_allow_html=True
    )

st.markdown("<div style='height:16px;'></div>", unsafe_allow_html=True)

# ── TREND SYNTHESIS + VOLATILITY ALERTS ──────────────────────────────────────
col_main, col_side = st.columns([2, 1])

with col_main:
    # Trend Synthesis box
    narrative = (
        f"Per <b>{mdf['Date'].max().strftime('%B %Y')}</b>, harga {COMMODITY_LABELS[commodity_sel]} nasional "
        f"tercatat di <b style='color:{P['secondary']};'>Rp {current_price:,.0f}/kg</b> — {direction} "
        f"<b>{abs(mom_change):.1f}%</b> dibandingkan bulan sebelumnya. "
        f"Secara tahunan, rata-rata harga {yoy_dir} <b>{abs(yoy_change):.1f}%</b>. "
        f"Disparitas harga antar-wilayah mencapai <b style='color:{P['tertiary']};'>Rp {(exp_mkt['mean']-chp_mkt['mean']):,.0f}/kg</b> "
        f"({disparity_pct:.0f}%) antara <b>{exp_mkt['admin1']}</b> dan <b>{chp_mkt['admin1']}</b>. "
        f"Data historis 17 tahun menunjukkan <b>{peak_month_name}</b> sebagai bulan puncak yang konsisten."
    )
    st.markdown(
        f"<div style='background:{P['card']};border:1px solid {P['border']};border-radius:6px;padding:20px;'>"
        f"<div style='display:flex;justify-content:space-between;align-items:center;margin-bottom:12px;'>"
        f"<div style='display:flex;align-items:center;gap:8px;'>"
        f"<span style='color:{P['secondary']};font-size:14px;'>✦</span>"
        f"<span style='font-family:Outfit,sans-serif;font-size:15px;font-weight:700;color:{P['cream']};'>Trend Synthesis</span>"
        f"</div>"
        f"</div>"
        f"<div style='font-family:Outfit,sans-serif;font-size:13px;color:{P['cream']};line-height:1.75;'>"
        f"{narrative}</div>"
        f"</div>",
        unsafe_allow_html=True
    )

    st.markdown("<div style='height:14px;'></div>", unsafe_allow_html=True)

    # Price Volatility sparkline (last 24 months) + historic reference line
    last24 = mdf.tail(24).copy()
    last24["Historic"] = last24["Price"].rolling(6, min_periods=1).mean()

    fig_spark = go.Figure()
    fig_spark.add_trace(go.Scatter(
        x=last24["Date"], y=last24["Price"],
        mode="lines", name="Current",
        line=dict(color=P["primary"], width=2),
        fill="tozeroy", fillcolor=P["primary_a"],
        hovertemplate="<b>%{x|%b %Y}</b><br>Rp %{y:,.0f}/kg<extra></extra>"
    ))
    fig_spark.add_trace(go.Scatter(
        x=last24["Date"], y=last24["Historic"],
        mode="lines", name="Historic",
        line=dict(color=P["secondary"], width=1.5, dash="dot"),
        hovertemplate="<b>%{x|%b %Y}</b><br>Historic avg: Rp %{y:,.0f}/kg<extra></extra>"
    ))
    # Mark current peak
    peak_row = last24.loc[last24["Price"].idxmax()]
    fig_spark.add_annotation(
        x=peak_row["Date"], y=peak_row["Price"],
        text="CURRENT PEAK REACHED",
        showarrow=True, arrowhead=2, arrowcolor=P["tertiary"],
        font=dict(color=P["tertiary"], size=9, family="JetBrains Mono"),
        ax=0, ay=-35
    )
    lo = blayout("PRICE VOLATILITY FORECAST (30D)", h=220, legend=True)
    fig_spark.update_layout(**lo)
    fig_spark.update_layout(
        legend=dict(
            orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1,
            font=dict(color=P["muted"], size=9, family="JetBrains Mono"),
            bgcolor="rgba(0,0,0,0)"
        )
    )
    st.plotly_chart(fig_spark, use_container_width=True, config={"displayModeBar": False})

with col_side:
    # Volatility Alerts panel
    # Detect the date column defensively — raw market data may use different casing
    date_col = next((c for c in ("date", "Date", "DATE") if c in df_clean.columns), None)
    if date_col is not None:
        recent_df = df_clean[df_clean[date_col] >= df_clean[date_col].max() - pd.DateOffset(months=3)]
    else:
        recent_df = df_clean  # fall back to full history if no date column is available

    vol_mkts = (
        recent_df.groupby(["admin1","market"])["price"]
        .agg(["mean","std"]).reset_index()
        .dropna()
    )
    vol_mkts["cv"] = vol_mkts["std"] / vol_mkts["mean"] * 100
    vol_mkts = vol_mkts.sort_values("cv", ascending=False).reset_index(drop=True)
    total_alerts = len(vol_mkts)
    top_mkts = vol_mkts.head(3)

    alerts_html = ""
    for i, row in top_mkts.iterrows():
        clr = P["primary"] if row["cv"] > 20 else (P["secondary"] if row["cv"] > 10 else P["tertiary"])
        alerts_html += (
            f"<div style='display:flex;justify-content:space-between;align-items:center;"
            f"padding:10px 12px;border-bottom:1px solid {P['border_d']};'>"
            f"<div>"
            f"<div style='font-family:Outfit,sans-serif;font-size:12px;font-weight:600;color:{P['cream']};'>"
            f"{row['market']}, {row['admin1']}</div>"
            f"</div>"
            f"<div style='display:flex;align-items:center;gap:8px;'>"
            f"<span style='font-family:\"JetBrains Mono\",monospace;font-size:13px;font-weight:700;color:{clr};'>"
            f"+{row['cv']:.1f}%</span>"
            f"<span style='color:{P['muted']};font-size:12px;'>›</span>"
            f"</div></div>"
        )

    # mini map thumbnail placeholder
    st.markdown(
        f"<div style='background:{P['card']};border:1px solid {P['border']};border-radius:6px;overflow:hidden;'>"
        f"<div style='padding:14px 16px;display:flex;justify-content:space-between;align-items:center;'>"
        f"<span style='font-family:Outfit,sans-serif;font-size:14px;font-weight:700;color:{P['cream']};'>Volatility Alerts</span>"
        f"</div>"
        f"{alerts_html}"
        f"</div>",
        unsafe_allow_html=True
    )



footer()