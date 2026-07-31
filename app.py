# =============================================================================
# OVERVIEW EKSEKUTIF — Chili Price Intelligence Dashboard
# Halaman Utama: Ringkasan kondisi pasar, KPI, narrative, highlights
# =============================================================================

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

from utils import (
    P, DATA_PATH, COMMODITY_LABELS, MONTH_FULL,
    inject_css, render_sidebar, page_header, footer,
    get_chili_wfp, get_national_monthly, train_wfp_model,
    forecast_months_ahead, blayout, insight_card,
)

st.set_page_config(
    page_title="Overview — Chili Price Intelligence",
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
if recent_cv > 0.25 or abs(mom_change) > 12:
    status_bg   = P["crimson"]
    status_text = "VOLATILITAS TINGGI — RISIKO PASOKAN TINGGI"
    status_desc = "Fluktuasi harga signifikan di tingkat eceran nasional berpotensi memicu lonjakan inflasi pangan."
elif recent_cv > 0.15 or abs(mom_change) > 5:
    status_bg   = P["amber"]
    status_text = "MODERAT — PERLU WASPADA SIKLUS"
    status_desc = "Pergerakan harga berada dalam fase penyesuaian musiman yang memerlukan pemantauan pasokan."
else:
    status_bg   = P["emerald"]
    status_text = "STABIL — PASOKAN & HARGA TERKENDALI"
    status_desc = "Kondisi pasokan komoditas di tingkat eceran relatif seimbang dengan tingkat permintaan."

df_clean  = chili_raw.dropna(subset=["market","price"])
mkt_stats = df_clean.groupby(["admin1","market"])["price"].agg(["mean","max","min"]).reset_index()
exp_mkt   = mkt_stats.loc[mkt_stats["mean"].idxmax()]
chp_mkt   = mkt_stats.loc[mkt_stats["mean"].idxmin()]
next_fc   = fcast_df["Forecast"].iloc[0]
fc_diff   = (next_fc - current_price) / current_price * 100

# ── HEADER ────────────────────────────────────────────────────────────────────
page_header(
    supra="SISTEM INTELIJEN PASAR PANGAN NASIONAL — WFP INDONESIA",
    title="Overview Eksekutif",
    desc=(
        f"Ringkasan kondisi pasar {COMMODITY_LABELS[commodity_sel]} nasional &nbsp;&middot;&nbsp; "
        f"<span style='font-family:JetBrains Mono,monospace;color:{P['amber']};font-size:11px;'>"
        f"Januari 2007 – Mei 2024</span>"
        f" &nbsp;&middot;&nbsp; 34 Provinsi &nbsp;&middot;&nbsp; 215 Pasar Eceran"
    )
)

# ── STATUS BANNER ─────────────────────────────────────────────────────────────
st.markdown(
    f"<div style='background:{P['card']};border:1px solid {P['border']};border-left:5px solid {status_bg};"
    f"border-radius:8px;padding:14px 22px;margin-bottom:18px;"
    f"display:flex;justify-content:space-between;align-items:center;'>"
    f"<div>"
    f"<div style='font-size:9px;font-weight:800;letter-spacing:0.16em;"
    f"color:{status_bg};text-transform:uppercase;'>INDIKATOR VOLATILITAS PASAR NASIONAL</div>"
    f"<div style='font-size:15px;font-weight:700;color:{P['cream']};margin-top:3px;'>{status_text}</div>"
    f"<div style='font-size:11.5px;color:{P['muted']};margin-top:2px;'>{status_desc}</div>"
    f"</div>"
    f"<div style='text-align:right;font-family:JetBrains Mono,monospace;flex-shrink:0;margin-left:20px;'>"
    f"<span style='font-size:9px;color:{P['muted']};'>PERIODE DATA TERAKHIR</span><br>"
    f"<span style='font-size:15px;font-weight:600;color:{P['amber']};'>"
    f"{mdf['Date'].max().strftime('%B %Y')}</span>"
    f"</div></div>",
    unsafe_allow_html=True
)

# ── KPI CARDS ─────────────────────────────────────────────────────────────────
k1, k2, k3, k4 = st.columns(4)
with k1:
    st.metric("Rata-Rata Harga Nasional", f"Rp {current_price:,.0f}", f"{mom_change:+.1f}% MoM")
with k2:
    st.metric("Pasar Termahal", f"Rp {exp_mkt['mean']:,.0f}",
              f"{exp_mkt['market']} — {exp_mkt['admin1']}", delta_color="off")
with k3:
    st.metric("Pasar Termurah", f"Rp {chp_mkt['mean']:,.0f}",
              f"{chp_mkt['market']} — {chp_mkt['admin1']}", delta_color="off")
with k4:
    st.metric("Proyeksi Bulan Depan", f"Rp {next_fc:,.0f}", f"{fc_diff:+.1f}% Estimasi")

st.markdown("---")

# ── AUTO-GENERATED NARRATIVE ──────────────────────────────────────────────────
yoy_prices        = mdf.copy()
yoy_prices["yr"]  = yoy_prices["Date"].dt.year
yoy_avg           = yoy_prices.groupby("yr")["Price"].mean()
yoy_change        = ((yoy_avg.iloc[-1] - yoy_avg.iloc[-2]) / yoy_avg.iloc[-2] * 100) if len(yoy_avg) >= 2 else 0

mdf_s             = mdf.copy()
mdf_s["month"]    = mdf_s["Date"].dt.month
peak_month_num    = mdf_s.groupby("month")["Price"].mean().idxmax()
peak_month_name   = MONTH_FULL[peak_month_num - 1]
disparity_pct     = (exp_mkt["mean"] - chp_mkt["mean"]) / chp_mkt["mean"] * 100
direction         = "meningkat" if mom_change > 0 else "menurun"
yoy_dir           = "tumbuh" if yoy_change > 0 else "terkoreksi"

narrative = (
    f"Per <b>{mdf['Date'].max().strftime('%B %Y')}</b>, harga {COMMODITY_LABELS[commodity_sel]} nasional "
    f"tercatat di <b>Rp {current_price:,.0f}/kg</b> — {direction} <b>{abs(mom_change):.1f}%</b> "
    f"dibandingkan bulan sebelumnya. Secara tahunan, rata-rata harga {yoy_dir} <b>{abs(yoy_change):.1f}%</b> "
    f"dari tahun sebelumnya. Disparitas harga antar-wilayah mencapai "
    f"<b>Rp {(exp_mkt['mean'] - chp_mkt['mean']):,.0f}/kg ({disparity_pct:.0f}%)</b> antara "
    f"<b>{exp_mkt['admin1']}</b> (tertinggi) dan <b>{chp_mkt['admin1']}</b> (terendah). "
    f"Data historis 17 tahun menunjukkan <b>{peak_month_name}</b> sebagai bulan dengan rata-rata harga tertinggi secara konsisten, "
    f"didorong oleh kombinasi musim hujan dan peningkatan permintaan libur nasional."
)

st.markdown(
    f"<div style='background:{P['card']};border:1px solid {P['border']};border-radius:8px;"
    f"padding:18px 24px;margin-bottom:20px;'>"
    f"<div style='font-size:9px;font-weight:800;letter-spacing:0.14em;"
    f"text-transform:uppercase;color:{P['indigo']};margin-bottom:8px;'>RINGKASAN EKSEKUTIF</div>"
    f"<div style='font-size:13px;color:{P['cream']};line-height:1.8;'>{narrative}</div>"
    f"</div>",
    unsafe_allow_html=True
)

# ── SPARKLINE + HIGHLIGHT FINDINGS ───────────────────────────────────────────
col_spark, col_findings = st.columns([2, 1])

with col_spark:
    last24 = mdf.tail(24).copy()
    fig_spark = go.Figure()
    fig_spark.add_trace(go.Scatter(
        x=last24["Date"], y=last24["Price"],
        mode="lines+markers",
        line=dict(color=P["crimson"], width=2.5),
        marker=dict(size=5, color=P["crimson"]),
        fill="tozeroy", fillcolor=P["crim_a"],
        hovertemplate="<b>%{x|%b %Y}</b><br>Rp %{y:,.0f}/kg<extra></extra>"
    ))
    lo_sp = blayout("Pergerakan Harga 24 Bulan Terakhir", h=240, legend=False)
    fig_spark.update_layout(**lo_sp)
    st.plotly_chart(fig_spark, use_container_width=True, config={"displayModeBar": False})

with col_findings:
    cv_pct  = recent_cv * 100
    r2_val  = res_model["r2"]
    f1_clr  = P["amber"]
    f2_clr  = P["emerald"] if r2_val > 0.80 else P["amber"]
    f3_clr  = P["crimson"] if recent_cv > 0.25 else (P["amber"] if recent_cv > 0.15 else P["emerald"])

    st.markdown(
        f"<div style='height:240px;display:flex;flex-direction:column;gap:10px;'>"

        f"<div style='background:{P['card']};border:1px solid {P['border']};"
        f"border-left:3px solid {f1_clr};border-radius:6px;padding:10px 14px;flex:1;'>"
        f"<div style='font-size:9px;font-weight:800;letter-spacing:0.1em;"
        f"color:{f1_clr};text-transform:uppercase;'>Disparitas Spasial</div>"
        f"<div style='font-size:15px;font-weight:700;color:{P['cream']};margin-top:2px;font-family:JetBrains Mono,monospace;'>"
        f"Rp {(exp_mkt['mean']-chp_mkt['mean']):,.0f}/kg</div>"
        f"<div style='font-size:10px;color:{P['muted']};margin-top:1px;'>"
        f"{exp_mkt['admin1']} vs {chp_mkt['admin1']}</div>"
        f"</div>"

        f"<div style='background:{P['card']};border:1px solid {P['border']};"
        f"border-left:3px solid {f2_clr};border-radius:6px;padding:10px 14px;flex:1;'>"
        f"<div style='font-size:9px;font-weight:800;letter-spacing:0.1em;"
        f"color:{f2_clr};text-transform:uppercase;'>Akurasi Model ML</div>"
        f"<div style='font-size:15px;font-weight:700;color:{P['cream']};margin-top:2px;font-family:JetBrains Mono,monospace;'>"
        f"R&sup2; = {r2_val:.3f}</div>"
        f"<div style='font-size:10px;color:{P['muted']};margin-top:1px;'>"
        f"MAPE {res_model['mape']:.1f}% &nbsp;&middot;&nbsp; RMSE Rp {res_model['rmse']:,.0f}</div>"
        f"</div>"

        f"<div style='background:{P['card']};border:1px solid {P['border']};"
        f"border-left:3px solid {f3_clr};border-radius:6px;padding:10px 14px;flex:1;'>"
        f"<div style='font-size:9px;font-weight:800;letter-spacing:0.1em;"
        f"color:{f3_clr};text-transform:uppercase;'>Volatilitas 12 Bulan</div>"
        f"<div style='font-size:15px;font-weight:700;color:{P['cream']};margin-top:2px;font-family:JetBrains Mono,monospace;'>"
        f"CV = {cv_pct:.1f}%</div>"
        f"<div style='font-size:10px;color:{P['muted']};margin-top:1px;'>"
        f"{'Tinggi' if recent_cv>0.25 else ('Moderat' if recent_cv>0.15 else 'Rendah')} — "
        f"Bulan Puncak: {peak_month_name}</div>"
        f"</div>"

        f"</div>",
        unsafe_allow_html=True
    )

st.markdown("---")

# ── DATA COVERAGE STATS ───────────────────────────────────────────────────────
total_obs = len(chili_raw)
stats = [
    ("17", "Tahun Data", P["cream"]),
    ("34", "Provinsi", P["emerald"]),
    ("215", "Pasar Eceran", P["amber"]),
    ("2", "Varietas Cabai", P["indigo"]),
    (f"{total_obs:,}", "Total Observasi", P["crimson"]),
]
cols = st.columns(5)
for col, (val, label, clr) in zip(cols, stats):
    with col:
        st.markdown(
            f"<div style='text-align:center;padding:14px 10px;"
            f"background:{P['card']};border:1px solid {P['border']};border-radius:8px;'>"
            f"<div style='font-size:22px;font-weight:800;color:{clr};"
            f"font-family:JetBrains Mono,monospace;'>{val}</div>"
            f"<div style='font-size:10px;color:{P['muted']};text-transform:uppercase;"
            f"letter-spacing:0.1em;margin-top:4px;'>{label}</div>"
            f"</div>",
            unsafe_allow_html=True
        )

footer()
