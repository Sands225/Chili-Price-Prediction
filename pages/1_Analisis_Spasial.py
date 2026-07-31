# =============================================================================
# ANALISIS SPASIAL — Chili Price Intelligence Dashboard
# Pemetaan harga, disparitas wilayah, korelasi antar provinsi, audit pasar
# =============================================================================

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from utils import (
    P, DATA_PATH, COMMODITY_LABELS,
    inject_css, render_sidebar, page_header, section_header, footer, insight_card,
    get_chili_wfp, get_national_monthly, blayout,
)

st.set_page_config(
    page_title="Analisis Spasial — Chili Price Intelligence",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded",
)
inject_css()
commodity_sel = render_sidebar(DATA_PATH)

# ── DATA ──────────────────────────────────────────────────────────────────────
with st.spinner("Memuat data spasial..."):
    chili_raw = get_chili_wfp(DATA_PATH, commodity_sel)

df_clean  = chili_raw.dropna(subset=["market", "price"])
mkt_stats = df_clean.groupby(["admin1","market"])["price"].agg(["mean","max","min"]).reset_index()
exp_mkt   = mkt_stats.loc[mkt_stats["mean"].idxmax()]
chp_mkt   = mkt_stats.loc[mkt_stats["mean"].idxmin()]

# ── HEADER ────────────────────────────────────────────────────────────────────
page_header(
    supra="WFP INDONESIA — 34 PROVINSI — 215 PASAR ECERAN",
    title="Analisis Spasial & Disparitas Harga Wilayah",
    desc=(
        f"Pemetaan harga eceran {COMMODITY_LABELS[commodity_sel]} pada 215 lokasi pasar di 34 provinsi "
        f"untuk mengidentifikasi pola disparitas geografis dan integrasi logistik antar-wilayah."
    )
)

# ── PETA + RANKING PROVINSI ───────────────────────────────────────────────────
section_header(
    "Distribusi Harga & Peta Lokasi Pasar",
    "Setiap titik merepresentasikan satu pasar eceran. Warna menunjukkan rata-rata harga historis."
)

c_map, c_bars = st.columns([1.65, 1])

with c_map:
    df_coords = chili_raw.dropna(subset=["latitude","longitude","price"])
    if not df_coords.empty:
        mkt_geo = df_coords.groupby(["admin1","admin2","market"]).agg(
            lat=("latitude","first"), lon=("longitude","first"),
            avg_price=("price","mean"), max_price=("price","max"), count=("price","count")
        ).reset_index()

        hover_txt = [
            f"<b>{r['market']}</b><br>"
            f"Kab/Kota: {r['admin2']}<br>"
            f"Provinsi: {r['admin1']}<br>"
            f"Rata-rata: Rp {r['avg_price']:,.0f}/kg<br>"
            f"Harga Tertinggi: Rp {r['max_price']:,.0f}/kg<br>"
            f"Jumlah Catatan: {r['count']:,}"
            for _, r in mkt_geo.iterrows()
        ]

        fig_map = go.Figure(go.Scattermapbox(
            lat=mkt_geo["lat"], lon=mkt_geo["lon"], mode="markers",
            marker=go.scattermapbox.Marker(
                size=9,
                color=mkt_geo["avg_price"],
                colorscale=[[0.0, P["emerald"]], [0.5, P["amber"]], [1.0, P["crimson"]]],
                showscale=True,
                colorbar=dict(
                    tickfont=dict(color=P["muted"], size=9),
                    title=dict(text="Rp/kg", font=dict(color=P["muted"], size=10)),
                    thickness=10, tickformat=",.0f", outlinecolor="rgba(0,0,0,0)"
                ),
                opacity=0.88
            ),
            text=hover_txt, hoverinfo="text"
        ))
        fig_map.update_layout(
            mapbox=dict(style="carto-darkmatter", center=dict(lat=-2.2, lon=118.0), zoom=3.8),
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=0, r=0, t=0, b=0), height=430,
            hoverlabel=dict(bgcolor=P["surface"], font=dict(color=P["cream"], size=11), bordercolor=P["border"])
        )
        st.plotly_chart(fig_map, use_container_width=True, config={"displayModeBar": False})

with c_bars:
    prov_series = df_clean.groupby("admin1")["price"].mean().sort_values().tail(14)
    n = len(prov_series)
    colors = [
        P["crimson"] if i >= n-2 else (P["amber"] if i >= n-5 else P["surface"])
        for i in range(n)
    ]
    fig_prov = go.Figure(go.Bar(
        x=prov_series.values, y=prov_series.index, orientation="h",
        marker_color=colors,
        text=[f" Rp {v:,.0f}" for v in prov_series.values],
        textposition="outside", textfont=dict(size=9.5, color=P["muted"]),
        hovertemplate="<b>%{y}</b><br>Rata-rata: Rp %{x:,.0f}/kg<extra></extra>"
    ))
    lo_pv = blayout("Top 14 Provinsi — Rata-Rata Harga Tertinggi", h=430, legend=False)
    lo_pv["margin"]["r"] = 85
    fig_prov.update_layout(**lo_pv)
    st.plotly_chart(fig_prov, use_container_width=True, config={"displayModeBar": False})

# ── TOP 5 TERMAHAL & TERMURAH ─────────────────────────────────────────────────
c_exp, c_chp = st.columns(2)

with c_exp:
    top_exp = mkt_stats.sort_values("mean", ascending=False).head(5).iloc[::-1]
    fig_exp = go.Figure(go.Bar(
        x=top_exp["mean"], y=top_exp["market"], orientation="h",
        marker_color=P["crimson"],
        text=[f" Rp {v:,.0f}" for v in top_exp["mean"]], textposition="outside",
        textfont=dict(size=9.5, color=P["muted"]),
        customdata=top_exp["admin1"].values,
        hovertemplate="<b>%{y}</b> (%{customdata})<br>Rata-rata: Rp %{x:,.0f}/kg<extra></extra>"
    ))
    lo_e = blayout("Top 5 Pasar Eceran Termahal", h=240, legend=False)
    lo_e["margin"]["r"] = 85
    fig_exp.update_layout(**lo_e)
    st.plotly_chart(fig_exp, use_container_width=True, config={"displayModeBar": False})

with c_chp:
    top_chp = mkt_stats.sort_values("mean", ascending=True).head(5).iloc[::-1]
    fig_chp = go.Figure(go.Bar(
        x=top_chp["mean"], y=top_chp["market"], orientation="h",
        marker_color=P["emerald"],
        text=[f" Rp {v:,.0f}" for v in top_chp["mean"]], textposition="outside",
        textfont=dict(size=9.5, color=P["muted"]),
        customdata=top_chp["admin1"].values,
        hovertemplate="<b>%{y}</b> (%{customdata})<br>Rata-rata: Rp %{x:,.0f}/kg<extra></extra>"
    ))
    lo_c = blayout("Top 5 Pasar Eceran Termurah", h=240, legend=False)
    lo_c["margin"]["r"] = 85
    fig_chp.update_layout(**lo_c)
    st.plotly_chart(fig_chp, use_container_width=True, config={"displayModeBar": False})

st.markdown(insight_card(
    "ANALISIS INTEGRASI LOGISTIK SPASIAL",
    f"Selisih harga antara pasar termahal di <b>{exp_mkt['admin1']}</b> dan termurah di "
    f"<b>{chp_mkt['admin1']}</b> mencapai <b>Rp {(exp_mkt['mean'] - chp_mkt['mean']):,.0f}/kg</b> "
    f"({((exp_mkt['mean']-chp_mkt['mean'])/chp_mkt['mean']*100):.0f}%). "
    f"Disparitas ini merupakan refleksi dari beban biaya transportasi antar-pulau, jarak dari sentra produksi utama "
    f"(Jawa Timur & Jawa Tengah), dan kerentanan fisik komoditas (perishability) dalam rantai distribusi jarak jauh.",
    P["amber"]
), unsafe_allow_html=True)

st.markdown("---")

# ── KORELASI HARGA ANTAR PROVINSI ────────────────────────────────────────────
section_header(
    "Korelasi Pergerakan Harga Antar Provinsi",
    "Matriks korelasi Pearson dari rata-rata harga bulanan per provinsi. Nilai tinggi menunjukkan pergerakan harga yang sinkron (integrasi pasar kuat)."
)

prov_monthly = (
    df_clean
    .groupby(["admin1", pd.Grouper(key="date", freq="MS")])["price"]
    .mean().unstack("admin1")
)
# Pilih 18 provinsi dengan data terbanyak
top_provs = prov_monthly.count().sort_values(ascending=False).head(18).index.tolist()
corr_m = prov_monthly[top_provs].corr()

# Shorten long province names for display
def shorten(name):
    replacements = {
        "Kalimantan": "Kal.",
        "Sulawesi": "Sul.",
        "Sumatera": "Sum.",
        "DKI Jakarta": "DKI",
        "Jawa Barat": "Jabar",
        "Jawa Tengah": "Jateng",
        "Jawa Timur": "Jatim",
        "DI Yogyakarta": "DIY",
        "Nusa Tenggara": "NTB/NTT",
    }
    for k, v in replacements.items():
        name = name.replace(k, v)
    return name

labels_short = [shorten(p) for p in top_provs]
z_corr = np.round(corr_m.values, 2)
text_corr = [[f"{v:.2f}" for v in row] for row in z_corr]

fig_corr = go.Figure(go.Heatmap(
    z=z_corr, x=labels_short, y=labels_short,
    colorscale=[
        [0.0, "#141B29"], [0.3, P["indigo"]], [0.6, P["amber"]], [1.0, P["crimson"]]
    ],
    text=text_corr, texttemplate="%{text}",
    textfont=dict(size=8, color="rgba(255,255,255,0.8)"),
    hovertemplate="<b>%{y}</b> × <b>%{x}</b><br>Korelasi: %{z:.2f}<extra></extra>",
    zmin=-1, zmax=1, showscale=True,
    colorbar=dict(
        tickfont=dict(color=P["muted"], size=9),
        thickness=10, outlinecolor="rgba(0,0,0,0)"
    )
))
lo_cr = blayout("Matriks Korelasi Harga Antar Provinsi (18 Provinsi Terpadat)", h=480, legend=False)
lo_cr["xaxis"]["tickangle"] = -35
lo_cr["xaxis"]["tickfont"]["size"] = 9
lo_cr["yaxis"]["tickfont"]["size"] = 9
lo_cr["margin"] = dict(l=80, r=30, t=52, b=80)
fig_corr.update_layout(**lo_cr)
st.plotly_chart(fig_corr, use_container_width=True, config={"displayModeBar": False})

st.markdown(insight_card(
    "INTERPRETASI KORELASI HARGA",
    "Korelasi tinggi (>0.85) antar provinsi mengindikasikan integrasi pasar yang kuat — pergerakan harga di satu wilayah "
    "secara cepat ditransmisikan ke wilayah lain melalui rantai perdagangan. "
    "Sebaliknya, korelasi rendah (<0.50) menunjukkan pasar yang lebih terisolir secara logistik, "
    "umumnya terjadi pada provinsi kepulauan di luar Jawa yang mengandalkan jalur laut sebagai koneksi utama.",
    P["indigo"]
), unsafe_allow_html=True)

st.markdown("---")

# ── PEMBANDING 2 PROVINSI ─────────────────────────────────────────────────────
section_header(
    "Komparasi Pergerakan Harga Antar Provinsi",
    "Bandingkan tren harga bulanan dua provinsi secara langsung untuk mengidentifikasi margin dan divergensi."
)

prov_list = sorted(df_clean["admin1"].unique())
idx_p1 = prov_list.index("DKI Jakarta") if "DKI Jakarta" in prov_list else 0
idx_p2 = prov_list.index("Jawa Timur")  if "Jawa Timur"  in prov_list else min(1, len(prov_list)-1)

cp1, cp2 = st.columns(2)
with cp1:
    prov1 = st.selectbox("Provinsi A", prov_list, index=idx_p1, key="prov1_sel")
with cp2:
    prov2 = st.selectbox("Provinsi B", prov_list, index=idx_p2, key="prov2_sel")

df_p1 = df_clean[df_clean["admin1"]==prov1].groupby(pd.Grouper(key="date", freq="MS"))["price"].mean().reset_index()
df_p2 = df_clean[df_clean["admin1"]==prov2].groupby(pd.Grouper(key="date", freq="MS"))["price"].mean().reset_index()

avg_p1  = df_p1["price"].mean() if not df_p1.empty else 0
avg_p2  = df_p2["price"].mean() if not df_p2.empty else 0
gap_val = abs(avg_p1 - avg_p2)
pct_ratio = (avg_p1 / avg_p2 * 100) if avg_p2 > 0 else 100
cheaper   = prov1 if avg_p1 < avg_p2 else prov2

fig_comp = go.Figure()
if not df_p1.empty:
    fig_comp.add_trace(go.Scatter(
        x=df_p1["date"], y=df_p1["price"], mode="lines", name=prov1,
        line=dict(color=P["crimson"], width=2)
    ))
if not df_p2.empty:
    fig_comp.add_trace(go.Scatter(
        x=df_p2["date"], y=df_p2["price"], mode="lines", name=prov2,
        line=dict(color=P["emerald"], width=2)
    ))
fig_comp.update_layout(**blayout(f"Perbandingan Harga: {prov1} vs {prov2}", h=300))

cc_chart, cc_side = st.columns([2.2, 1])
with cc_chart:
    st.plotly_chart(fig_comp, use_container_width=True, config={"displayModeBar": False})
with cc_side:
    st.markdown(
        f"<div style='background:{P['card']};border:1px solid {P['border']};"
        f"border-radius:8px;padding:20px;height:300px;"
        f"display:flex;flex-direction:column;justify-content:center;gap:8px;'>"
        f"<div style='font-size:9px;font-weight:800;letter-spacing:0.12em;"
        f"color:{P['muted']};text-transform:uppercase;'>METRIK SELISIH HARGA</div>"
        f"<div style='font-size:24px;font-weight:700;color:{P['cream']};"
        f"font-family:JetBrains Mono,monospace;'>Rp {gap_val:,.0f}/kg</div>"
        f"<div style='font-size:11px;color:{P['amber']};'>Rata-rata Margin Antar-Wilayah</div>"
        f"<hr style='margin:8px 0 !important;'>"
        f"<div style='font-size:12px;color:{P['cream']};line-height:1.8;'>"
        f"&bull; {prov1}: <b>Rp {avg_p1:,.0f}/kg</b><br>"
        f"&bull; {prov2}: <b>Rp {avg_p2:,.0f}/kg</b><br>"
        f"&bull; Rasio: <b>{pct_ratio:.1f}%</b><br>"
        f"&bull; Lebih murah: <b>{cheaper}</b>"
        f"</div></div>",
        unsafe_allow_html=True
    )

st.markdown("---")

# ── AUDIT PASAR ECERAN ────────────────────────────────────────────────────────
section_header(
    "Audit & Pencarian Pasar Eceran",
    "Eksplorasi data historis harga untuk semua pasar eceran berdasarkan nama pasar, kota, atau provinsi."
)

search_q = st.text_input(
    "Cari Pasar, Kota, atau Provinsi:",
    placeholder="Contoh: Senen, Surabaya, Jawa Tengah..."
)

mkt_full = df_clean.groupby(["admin1","admin2","market"]).agg(
    Harga_Rata_Rata=("price","mean"),
    Harga_Tertinggi=("price","max"),
    Harga_Terendah=("price","min"),
    Jumlah_Catatan=("price","count"),
).reset_index().rename(columns={
    "admin1":"Provinsi", "admin2":"Kab/Kota", "market":"Nama Pasar"
})

if search_q:
    mkt_filtered = mkt_full[
        mkt_full["Nama Pasar"].str.contains(search_q, case=False, na=False) |
        mkt_full["Kab/Kota"].str.contains(search_q, case=False, na=False) |
        mkt_full["Provinsi"].str.contains(search_q, case=False, na=False)
    ]
else:
    mkt_filtered = mkt_full.copy()

mkt_display = mkt_filtered.copy()
for col in ["Harga_Rata_Rata","Harga_Tertinggi","Harga_Terendah"]:
    mkt_display[col] = mkt_display[col].map("Rp {:,.0f}".format)

st.markdown(
    f"<div style='font-size:11px;color:{P['muted']};margin-bottom:8px;'>"
    f"Menampilkan <b style='color:{P['cream']};'>{len(mkt_filtered):,}</b> pasar dari total <b>{len(mkt_full):,}</b></div>",
    unsafe_allow_html=True
)
st.dataframe(mkt_display, use_container_width=True, height=300)

footer()
