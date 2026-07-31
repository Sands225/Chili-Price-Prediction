# =============================================================================
# TREN HISTORIS & POLA MUSIMAN — Chili Price Intelligence Dashboard
# Analisis tren 17 tahun, volatilitas, seasonality, dan STL decomposition
# =============================================================================

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from utils import (
    P, DATA_PATH, COMMODITY_LABELS, MONTH_ID, MONTH_ABB,
    inject_css, render_sidebar, page_header, section_header, footer, insight_card,
    get_national_monthly, blayout,
)

st.set_page_config(
    page_title="Tren & Musiman — Chili Price Intelligence",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded",
)
inject_css()
commodity_sel = render_sidebar(DATA_PATH)

# ── DATA ──────────────────────────────────────────────────────────────────────
with st.spinner("Memuat data tren historis..."):
    mdf = get_national_monthly(DATA_PATH, commodity_sel)

# ── HEADER ────────────────────────────────────────────────────────────────────
page_header(
    supra="ANALISIS TEMPORAL — 17 TAHUN DATA HISTORIS",
    title="Tren Historis & Pola Musiman",
    desc=(
        f"Dekomposisi tren jangka panjang, volatilitas siklus, dan pola musiman "
        f"harga {COMMODITY_LABELS[commodity_sel]} nasional (Januari 2007 – Mei 2024)."
    )
)

# ── TREN HISTORIS + MA12 ──────────────────────────────────────────────────────
section_header(
    "Pergerakan Harga Nasional 17 Tahun",
    "Harga bulanan nasional beserta tren rata-rata bergerak 12 bulan (MA12) sebagai indikator tren jangka menengah."
)

mdf_hist        = mdf.copy()
mdf_hist["MA12"] = mdf_hist["Price"].rolling(12, min_periods=1).mean()
mdf_hist["MA3"]  = mdf_hist["Price"].rolling(3,  min_periods=1).mean()

fig_hist = go.Figure()
fig_hist.add_trace(go.Scatter(
    x=mdf_hist["Date"], y=mdf_hist["Price"],
    mode="lines", name="Harga Bulanan",
    line=dict(color=P["crimson"], width=1.5),
    fill="tozeroy", fillcolor=P["crim_a"],
    hovertemplate="<b>%{x|%b %Y}</b><br>Harga: Rp %{y:,.0f}/kg<extra></extra>"
))
fig_hist.add_trace(go.Scatter(
    x=mdf_hist["Date"], y=mdf_hist["MA12"],
    mode="lines", name="MA-12 (Tren Tahunan)",
    line=dict(color=P["amber"], width=2.5, dash="dash"),
    hovertemplate="<b>%{x|%b %Y}</b><br>MA-12: Rp %{y:,.0f}/kg<extra></extra>"
))
fig_hist.add_trace(go.Scatter(
    x=mdf_hist["Date"], y=mdf_hist["MA3"],
    mode="lines", name="MA-3 (Tren Kuartalan)",
    line=dict(color=P["indigo"], width=1.5, dash="dot"),
    hovertemplate="<b>%{x|%b %Y}</b><br>MA-3: Rp %{y:,.0f}/kg<extra></extra>"
))
fig_hist.update_layout(**blayout("Harga Nasional Bulanan + Moving Average (2007 – 2024)", h=340))
st.plotly_chart(fig_hist, use_container_width=True, config={"displayModeBar": False})

st.markdown("---")

# ── ROLLING VOLATILITY ────────────────────────────────────────────────────────
section_header(
    "Volatilitas Harga (Rolling 12 Bulan)",
    "Coefficient of Variation (CV) = standar deviasi / rata-rata rolling 12 bulan. Mengidentifikasi periode krisis harga secara kuantitatif."
)

mdf_vol = mdf.copy()
mdf_vol["roll12_std"]  = mdf_vol["Price"].rolling(12).std()
mdf_vol["roll12_mean"] = mdf_vol["Price"].rolling(12).mean()
mdf_vol["cv_12"]       = mdf_vol["roll12_std"] / mdf_vol["roll12_mean"] * 100
mdf_vol = mdf_vol.dropna(subset=["cv_12"])

fig_vol = go.Figure()
fig_vol.add_trace(go.Scatter(
    x=mdf_vol["Date"], y=mdf_vol["cv_12"],
    mode="lines", fill="tozeroy",
    fillcolor=P["crim_a"],
    line=dict(color=P["crimson"], width=2),
    name="CV Rolling 12 Bulan (%)",
    hovertemplate="<b>%{x|%b %Y}</b><br>CV: %{y:.1f}%<extra></extra>"
))
# Threshold lines
fig_vol.add_hline(
    y=25, line=dict(color=P["crimson"], width=1.2, dash="dot"),
    annotation=dict(text="Volatilitas Tinggi (25%)", font=dict(color=P["crimson"], size=10), xanchor="left")
)
fig_vol.add_hline(
    y=15, line=dict(color=P["amber"], width=1.2, dash="dot"),
    annotation=dict(text="Volatilitas Moderat (15%)", font=dict(color=P["amber"], size=10), xanchor="left")
)

lo_vol = blayout("Volatilitas Harga — Coefficient of Variation Rolling 12 Bulan", h=280, legend=False)
lo_vol["yaxis"]["ticksuffix"] = "%"
lo_vol["yaxis"]["tickformat"]  = ".0f"
fig_vol.update_layout(**lo_vol)
st.plotly_chart(fig_vol, use_container_width=True, config={"displayModeBar": False})

st.markdown("---")

# ── HEATMAP + SEASONAL BAR ────────────────────────────────────────────────────
section_header(
    "Pola Musiman: Intensitas Harga Per Bulan",
    "Dua cara membaca pola musiman: heatmap matriks (tahun × bulan) dan rata-rata per bulan lintas tahun."
)

ct1, ct2 = st.columns(2)

with ct1:
    mdf_h          = mdf.copy()
    mdf_h["year"]  = mdf_h["Date"].dt.year
    mdf_h["month"] = mdf_h["Date"].dt.month
    piv  = mdf_h.pivot_table(index="year", columns="month", values="Price", aggfunc="mean")
    z    = piv.values
    zt   = np.where(np.isnan(z), None, np.round(z / 1000, 1))
    text_arr = [[f"{v:.0f}k" if v is not None else "" for v in row] for row in zt]

    fig_hm = go.Figure(go.Heatmap(
        z=z, x=MONTH_ABB[:piv.shape[1]], y=[str(int(y)) for y in piv.index],
        colorscale=[[0.0, "#0F1420"], [0.3, P["emerald"]], [0.6, P["amber"]], [1.0, P["crimson"]]],
        text=text_arr, texttemplate="%{text}",
        textfont=dict(size=8.5, color="rgba(255,255,255,0.75)"),
        hovertemplate="<b>%{y} — %{x}</b><br>Rata-rata: Rp %{z:,.0f}/kg<extra></extra>",
        showscale=False
    ))
    lo_hm = blayout("Heatmap Intensitas Harga (Tahun × Bulan)", h=350, legend=False)
    lo_hm["yaxis"]["autorange"] = "reversed"
    fig_hm.update_layout(**lo_hm)
    st.plotly_chart(fig_hm, use_container_width=True, config={"displayModeBar": False})

with ct2:
    mdf_s          = mdf.copy()
    mdf_s["month"] = mdf_s["Date"].dt.month
    mon_avg = mdf_s.groupby("month")["Price"].mean()
    mon_std = mdf_s.groupby("month")["Price"].std()
    q75     = mon_avg.quantile(0.75)
    q50     = mon_avg.quantile(0.50)
    bar_colors = [
        P["crimson"] if v >= q75 else (P["amber"] if v >= q50 else P["surface"])
        for v in mon_avg.values
    ]

    fig_sea = go.Figure()
    fig_sea.add_trace(go.Bar(
        x=MONTH_ID, y=mon_avg.values,
        marker_color=bar_colors,
        error_y=dict(
            type="data", array=mon_std.values, visible=True,
            color=P["muted"], thickness=1.5, width=4
        ),
        hovertemplate="<b>%{x}</b><br>Rata-rata: Rp %{y:,.0f}/kg<extra></extra>"
    ))
    # Mark highest month
    peak_idx = mon_avg.values.argmax()
    fig_sea.add_annotation(
        x=MONTH_ID[peak_idx], y=mon_avg.values[peak_idx] + mon_std.values[peak_idx] + 1500,
        text="Puncak", showarrow=True, arrowhead=2,
        font=dict(color=P["crimson"], size=10), arrowcolor=P["crimson"]
    )
    lo_sea = blayout("Rata-Rata Harga Per Bulan — Seluruh Tahun (2007–2024)", h=350, legend=False)
    fig_sea.update_layout(**lo_sea)
    st.plotly_chart(fig_sea, use_container_width=True, config={"displayModeBar": False})

st.markdown(insight_card(
    "DOKTRIN MUSIMAN KONTRAKSI PASOKAN",
    "Data 17 tahun mengonfirmasi dua jendela waktu dengan risiko lonjakan harga tertinggi:<br>"
    "<b>1. Musim Hujan & Akhir Tahun (Desember – Februari):</b> Intensitas curah hujan tinggi memicu penyakit "
    "busuk buah (Antraknosa) pada tanaman, mengganggu panen, dan bersamaan dengan lonjakan permintaan libur akhir tahun.<br>"
    "<b>2. Jendela Hari Besar Keagamaan (Maret – Mei):</b> Peningkatan permintaan grosir menjelang Ramadan dan "
    "Idul Fitri menekan stok pasar secara agregat, mendorong harga di atas rata-rata historis.",
    P["crimson"]
), unsafe_allow_html=True)

st.markdown("---")

# ── STL DECOMPOSITION ─────────────────────────────────────────────────────────
section_header(
    "Dekomposisi Deret Waktu (Trend + Seasonal + Residual)",
    "Menggunakan STL (Seasonal-Trend Decomposition via LOESS) untuk memisahkan komponen struktural harga."
)

try:
    from statsmodels.tsa.seasonal import STL

    ts = mdf.set_index("Date")["Price"].asfreq("MS")
    stl_result = STL(ts, period=12, robust=True).fit()

    fig_stl = make_subplots(
        rows=3, cols=1, shared_xaxes=True,
        row_heights=[0.45, 0.3, 0.25],
        vertical_spacing=0.05,
        subplot_titles=["Komponen Tren Jangka Panjang", "Komponen Musiman", "Komponen Residual"]
    )
    # Trend
    fig_stl.add_trace(go.Scatter(
        x=ts.index, y=stl_result.trend,
        mode="lines", name="Tren",
        line=dict(color=P["amber"], width=2.5),
        hovertemplate="Tren: Rp %{y:,.0f}/kg<extra></extra>"
    ), row=1, col=1)
    # Seasonal
    fig_stl.add_trace(go.Scatter(
        x=ts.index, y=stl_result.seasonal,
        mode="lines", name="Musiman",
        line=dict(color=P["emerald"], width=1.5),
        fill="tozeroy", fillcolor=P["emerald_a"],
        hovertemplate="Musiman: Rp %{y:,.0f}/kg<extra></extra>"
    ), row=2, col=1)
    # Residual
    resid_colors = [P["crimson"] if v > 0 else P["indigo"] for v in stl_result.resid]
    fig_stl.add_trace(go.Bar(
        x=ts.index, y=stl_result.resid,
        name="Residual", marker_color=resid_colors,
        hovertemplate="Residual: Rp %{y:,.0f}/kg<extra></extra>"
    ), row=3, col=1)

    fig_stl.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, sans-serif", color=P["muted"], size=11),
        height=520, showlegend=False,
        margin=dict(l=10, r=10, t=30, b=10),
        hoverlabel=dict(bgcolor=P["surface"], font=dict(color=P["cream"], size=11), bordercolor=P["border"]),
    )
    for i in range(1, 4):
        fig_stl.update_xaxes(
            gridcolor=P["border_d"], linecolor=P["border"],
            tickcolor="rgba(0,0,0,0)", tickfont=dict(size=10, color=P["muted"]),
            zeroline=False, row=i, col=1
        )
        fig_stl.update_yaxes(
            gridcolor=P["border_d"], linecolor="rgba(0,0,0,0)",
            tickcolor="rgba(0,0,0,0)", tickfont=dict(size=10, color=P["muted"]),
            tickformat=",.0f", zeroline=False, row=i, col=1
        )
    for ann in fig_stl.layout.annotations:
        ann.font.color = P["cream"]
        ann.font.size  = 11

    st.plotly_chart(fig_stl, use_container_width=True, config={"displayModeBar": False})

    # STL metrics
    seasonal_strength = max(0, 1 - np.var(stl_result.resid) / np.var(stl_result.seasonal + stl_result.resid))
    trend_strength    = max(0, 1 - np.var(stl_result.resid) / np.var(stl_result.trend + stl_result.resid))
    avg_seasonal_amp  = stl_result.seasonal.max() - stl_result.seasonal.min()

    m1, m2, m3 = st.columns(3)
    with m1:
        st.metric("Kekuatan Tren (STL)", f"{trend_strength:.3f}", "Mendekati 1 = tren dominan")
    with m2:
        st.metric("Kekuatan Musiman (STL)", f"{seasonal_strength:.3f}", "Mendekati 1 = musiman kuat")
    with m3:
        st.metric("Amplitudo Musiman", f"Rp {avg_seasonal_amp:,.0f}/kg", "Rentang fluktuasi per siklus tahunan")

except ImportError:
    st.info("Statsmodels tidak tersedia. Jalankan: pip install statsmodels")
    # Fallback: simple trend dari rolling mean
    mdf_fb = mdf.copy()
    mdf_fb["Tren"]   = mdf_fb["Price"].rolling(12, center=True, min_periods=1).mean()
    mdf_fb["Resid"]  = mdf_fb["Price"] - mdf_fb["Tren"]
    fig_fb = go.Figure()
    fig_fb.add_trace(go.Scatter(x=mdf_fb["Date"], y=mdf_fb["Tren"], mode="lines",
                                line=dict(color=P["amber"], width=2), name="Tren (MA-12)"))
    fig_fb.add_trace(go.Scatter(x=mdf_fb["Date"], y=mdf_fb["Resid"], mode="lines",
                                line=dict(color=P["indigo"], width=1.5), name="Residual"))
    fig_fb.update_layout(**blayout("Tren & Residual (MA-12 Fallback)", h=320))
    st.plotly_chart(fig_fb, use_container_width=True, config={"displayModeBar": False})

footer()
