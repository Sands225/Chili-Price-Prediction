# =============================================================================
# MODEL PROYEKSI — Chili Price Intelligence Dashboard
# Evaluasi model ML, feature importance, actual vs predicted, dan forecast
# =============================================================================

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from utils import (
    P, DATA_PATH, COMMODITY_LABELS, FEAT_COLS,
    inject_css, render_sidebar, page_header, section_header, footer, insight_card,
    get_national_monthly, train_wfp_model, forecast_months_ahead, blayout,
)

st.set_page_config(
    page_title="Model Proyeksi — Chili Price Intelligence",
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
page_header(
    supra="MACHINE LEARNING — RANDOM FOREST REGRESSOR",
    title="Model Proyeksi Harga",
    desc=(
        f"Evaluasi performa dan horizon proyeksi model prediksi harga "
        f"{COMMODITY_LABELS[commodity_sel]} menggunakan Random Forest dengan rekayasa fitur time-series."
    )
)

# ── MODEL PERFORMANCE CARDS ───────────────────────────────────────────────────
section_header(
    "Evaluasi Performa Model",
    "Dihitung pada data test (18% data terbaru yang tidak digunakan saat pelatihan)."
)

mae  = res_model["mae"]
rmse = res_model["rmse"]
mape = res_model["mape"]
r2   = res_model["r2"]

r2_clr   = P["emerald"] if r2   > 0.85 else (P["amber"] if r2   > 0.70 else P["crimson"])
mape_clr = P["emerald"] if mape < 10   else (P["amber"] if mape < 20   else P["crimson"])

m1, m2, m3, m4 = st.columns(4)
with m1:
    st.metric("MAE (Mean Abs. Error)", f"Rp {mae:,.0f}", "Rata-rata selisih absolut prediksi vs aktual")
with m2:
    st.metric("RMSE", f"Rp {rmse:,.0f}", "Penalti lebih besar untuk error besar")
with m3:
    st.metric("MAPE (%)", f"{mape:.2f}%", "Error relatif terhadap harga aktual")
with m4:
    st.metric("R² Score", f"{r2:.4f}", "Proporsi variansi yang dapat dijelaskan model")

# Qualitative interpretation
if r2 > 0.85 and mape < 15:
    interp_color = P["emerald"]
    interp_text  = "Model berkinerja BAIK — cocok untuk digunakan sebagai referensi proyeksi jangka pendek."
elif r2 > 0.65:
    interp_color = P["amber"]
    interp_text  = "Model berkinerja MODERAT — proyeksi dapat dijadikan indikasi arah, namun perlu validasi tambahan."
else:
    interp_color = P["crimson"]
    interp_text  = "Model berkinerja LEMAH — tingginya volatilitas data membatasi kemampuan prediksi. Pertimbangkan model alternatif."

st.markdown(
    f"<div style='background:{P['card']};border:1px solid {P['border']};"
    f"border-left:4px solid {interp_color};border-radius:8px;"
    f"padding:12px 18px;margin-bottom:6px;'>"
    f"<div style='font-size:9px;font-weight:800;letter-spacing:0.12em;"
    f"color:{interp_color};text-transform:uppercase;margin-bottom:4px;'>INTERPRETASI KINERJA MODEL</div>"
    f"<div style='font-size:12.5px;color:{P['cream']};'>{interp_text}</div>"
    f"</div>",
    unsafe_allow_html=True
)

st.markdown("---")

# ── FEATURE IMPORTANCE + ACTUAL VS PREDICTED ─────────────────────────────────
section_header(
    "Analisis Model: Feature Importance & Aktual vs Prediksi",
    "Kiri: Faktor dominan pembentuk harga. Kanan: Kualitas prediksi pada data uji (titik mendekati garis diagonal = prediksi akurat)."
)

cf1, cf2 = st.columns(2)

with cf1:
    fi = pd.Series(res_model["rf"].feature_importances_, index=FEAT_COLS).sort_values(ascending=True)
    fi_labels = {
        "month_sin": "Sin Bulan", "month_cos": "Cos Bulan",
        "quarter": "Kuartal", "year": "Tahun",
        "lag_1": "Harga -1 Bln", "lag_2": "Harga -2 Bln",
        "lag_3": "Harga -3 Bln", "lag_6": "Harga -6 Bln",
        "lag_12": "Harga -12 Bln",
        "roll3_mean": "MA-3 Harga", "roll6_mean": "MA-6 Harga",
        "roll3_std": "Volatilitas-3", "roll6_std": "Volatilitas-6",
        "pct_1m": "Perubahan 1 Bln", "pct_3m": "Perubahan 3 Bln",
    }
    fi_clean = fi.rename(index=fi_labels)
    max_fi = fi_clean.max()
    fi_colors = [
        P["crimson"] if v >= max_fi * 0.70 else
        (P["amber"]  if v >= max_fi * 0.40 else P["surface"])
        for v in fi_clean.values
    ]

    fig_fi = go.Figure(go.Bar(
        x=fi_clean.values * 100,
        y=fi_clean.index,
        orientation="h",
        marker_color=fi_colors,
        text=[f" {v*100:.1f}%" for v in fi_clean.values],
        textposition="outside",
        textfont=dict(size=9, color=P["muted"]),
        hovertemplate="<b>%{y}</b><br>Importance: %{x:.2f}%<extra></extra>"
    ))
    lo_fi = blayout("Feature Importance — Kontribusi Variabel (%)", h=400, legend=False)
    lo_fi["xaxis"]["ticksuffix"] = "%"
    lo_fi["xaxis"]["tickformat"] = ".0f"
    lo_fi["margin"]["r"] = 55
    fig_fi.update_layout(**lo_fi)
    st.plotly_chart(fig_fi, use_container_width=True, config={"displayModeBar": False})

with cf2:
    y_true = res_model["y"]
    y_pred = res_model["pred"]
    mn_val = min(y_true.min(), y_pred.min()) * 0.95
    mx_val = max(y_true.max(), y_pred.max()) * 1.05

    fig_scat = go.Figure()
    fig_scat.add_trace(go.Scatter(
        x=[mn_val, mx_val], y=[mn_val, mx_val],
        mode="lines", name="Prediksi Sempurna",
        line=dict(color=P["emerald"], width=1.5, dash="dash"),
        hoverinfo="skip"
    ))
    fig_scat.add_trace(go.Scatter(
        x=y_true, y=y_pred,
        mode="markers", name="Data Uji",
        marker=dict(color=P["indigo"], size=8, opacity=0.75,
                    line=dict(color=P["cream"], width=0.5)),
        hovertemplate="Aktual: Rp %{x:,.0f}<br>Prediksi: Rp %{y:,.0f}<extra></extra>"
    ))
    lo_sc = blayout("Aktual vs Prediksi — Data Uji (18% Akhir)", h=400)
    lo_sc["xaxis"]["title"] = dict(text="Harga Aktual (Rp/kg)", font=dict(size=10, color=P["muted"]))
    lo_sc["yaxis"]["title"] = dict(text="Harga Prediksi (Rp/kg)", font=dict(size=10, color=P["muted"]))
    fig_scat.update_layout(**lo_sc)
    st.plotly_chart(fig_scat, use_container_width=True, config={"displayModeBar": False})

st.markdown(insight_card(
    "FAKTOR DOMINAN PEMBENTUK HARGA",
    "Feature importance mengonfirmasi bahwa <b>harga bulan sebelumnya (Lag-1, Lag-2)</b> merupakan prediktor terkuat, "
    "mencerminkan autokorelasi kuat pada deret waktu harga komoditas. "
    "<b>MA-3 dan MA-6</b> mengindikasikan tren jangka menengah sebagai sinyal yang relevan. "
    "<b>Komponen musiman (sin/cos bulan, kuartal)</b> memiliki kontribusi signifikan terhadap prediksi, "
    "selaras dengan temuan pola musiman pada analisis tren historis.",
    P["indigo"]
), unsafe_allow_html=True)

st.markdown("---")

# ── FORECAST CHART ────────────────────────────────────────────────────────────
section_header(
    "Proyeksi Harga 7 Bulan Ke Depan",
    "Hasil recursive forecasting dengan interval ketidakpastian yang melebar seiring bertambahnya horizon proyeksi."
)

tr_plot = res_model["tr"].tail(36)
te_plot = res_model["te"]

fig_fc = go.Figure()
fig_fc.add_trace(go.Scatter(
    x=tr_plot["Date"], y=tr_plot["Price"],
    mode="lines", name="Histori Pelatihan",
    line=dict(color="rgba(255,255,255,0.25)", width=1.5)
))
fig_fc.add_trace(go.Scatter(
    x=te_plot["Date"], y=te_plot["Price"],
    mode="lines", name="Data Aktual Pengujian",
    line=dict(color=P["cream"], width=2)
))
fig_fc.add_trace(go.Scatter(
    x=pd.concat([fcast_df["Date"], fcast_df["Date"][::-1]]),
    y=pd.concat([fcast_df["Upper"], fcast_df["Lower"][::-1]]),
    fill="toself", fillcolor=P["amber_a"],
    line=dict(color="rgba(0,0,0,0)"),
    showlegend=False, hoverinfo="skip",
    name="Interval Ketidakpastian"
))
fig_fc.add_trace(go.Scatter(
    x=fcast_df["Date"], y=fcast_df["Forecast"],
    mode="lines+markers", name="Proyeksi 7 Bulan",
    line=dict(color=P["amber"], width=2.5),
    marker=dict(size=9, symbol="diamond", color=P["amber"],
                line=dict(color=P["cream"], width=1)),
    hovertemplate="<b>%{x|%b %Y}</b><br>Proyeksi: Rp %{y:,.0f}/kg<extra></extra>"
))
lo_fc = blayout("Grafik Proyeksi Harga — Training | Testing | Forecast Horizon", h=360)
fig_fc.update_layout(**lo_fc)
st.plotly_chart(fig_fc, use_container_width=True, config={"displayModeBar": False})

# ── PROJECTION CARDS ─────────────────────────────────────────────────────────
st.markdown(
    f"<div style='font-size:10px;font-weight:800;letter-spacing:0.12em;"
    f"color:{P['muted']};margin-bottom:12px;text-transform:uppercase;'>DETAIL PROYEKSI PER BULAN</div>",
    unsafe_allow_html=True
)

card_cols = st.columns(7)
for i, (_, row) in enumerate(fcast_df.iterrows()):
    pct = (row["Forecast"] - current_price) / current_price * 100
    clr = P["crimson"] if pct >= 5 else (P["amber"] if pct >= 0 else P["emerald"])
    ci_width = row["Upper"] - row["Lower"]
    with card_cols[i]:
        st.markdown(
            f"<div style='background:{P['card']};border:1px solid {P['border']};"
            f"border-top:3px solid {clr};border-radius:6px;padding:10px 10px;text-align:center;'>"
            f"<div style='font-size:9px;font-weight:700;color:{P['muted']};'>"
            f"M+{row['step']}</div>"
            f"<div style='font-size:9px;color:{P['muted']};margin-bottom:4px;'>"
            f"{pd.Timestamp(row['Date']).strftime('%b %Y')}</div>"
            f"<div style='font-family:JetBrains Mono,monospace;font-size:13px;"
            f"font-weight:700;color:{P['cream']};'>"
            f"Rp {row['Forecast']:,.0f}</div>"
            f"<div style='font-size:10px;color:{clr};font-weight:600;margin-top:2px;'>"
            f"{pct:+.1f}%</div>"
            f"<div style='font-size:8.5px;color:{P['dim']};margin-top:4px;'>"
            f"CI ±{ci_width/2:,.0f}</div>"
            f"</div>",
            unsafe_allow_html=True
        )

st.markdown("<br>", unsafe_allow_html=True)

# ── DISCLAIMER ────────────────────────────────────────────────────────────────
st.markdown(
    f"<div style='background:{P['surface']};border:1px solid {P['border_d']};"
    f"border-radius:8px;padding:14px 18px;margin-top:8px;'>"
    f"<div style='font-size:9px;font-weight:800;letter-spacing:0.12em;"
    f"color:{P['dim']};text-transform:uppercase;margin-bottom:6px;'>DISCLAIMER METODOLOGIS</div>"
    f"<div style='font-size:11px;color:{P['dim']};line-height:1.8;'>"
    f"&bull; Model menggunakan <b>recursive multi-step forecasting</b>: prediksi setiap bulan digunakan sebagai "
    f"input lag untuk bulan berikutnya, sehingga akurasi menurun pada horizon &gt; 3 bulan.<br>"
    f"&bull; <b>Interval ketidakpastian</b> diperoleh dari dispersi prediksi antar-pohon dalam Random Forest "
    f"dan melebar secara progresif seiring bertambahnya horizon (bukan 95% CI statistik formal).<br>"
    f"&bull; Model dilatih pada data bulanan WFP (2007–2024) tanpa informasi eksternal "
    f"(cuaca, kebijakan impor, harga BBM). Perubahan struktural di luar pola historis tidak dapat diantisipasi.<br>"
    f"&bull; Proyeksi bersifat <b>indikatif</b> dan dimaksudkan sebagai referensi awal, bukan satu-satunya dasar pengambilan keputusan."
    f"</div></div>",
    unsafe_allow_html=True
)

footer()
