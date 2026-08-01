# =============================================================================
# ANALISIS SPASIAL — Heat & Spice Spatial Intelligence
# Chili Price Intelligence Platform
# =============================================================================

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from utils import (
    P, DATA_PATH, COMMODITY_LABELS,
    inject_css, render_sidebar, page_header, section_header, footer,
    insight_card, stat_card, status_chip,
    get_chili_wfp, blayout,
)

st.set_page_config(
    page_title="Heat & Spice — Spatial Analysis",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded",
)
inject_css()
commodity_sel = render_sidebar(DATA_PATH)

# ── DATA ──────────────────────────────────────────────────────────────────────
with st.spinner("Memuat data spasial..."):
    chili_raw = get_chili_wfp(DATA_PATH, commodity_sel)

df_clean  = chili_raw.dropna(subset=["market","price"])
mkt_stats = df_clean.groupby(["admin1","market"])["price"].agg(["mean","max","min"]).reset_index()
exp_mkt   = mkt_stats.loc[mkt_stats["mean"].idxmax()]
chp_mkt   = mkt_stats.loc[mkt_stats["mean"].idxmin()]
prov_list = sorted(df_clean["admin1"].unique().tolist())

# ── HEADER + TOGGLE NASIONAL/PROVINSI ─────────────────────────────────────────
page_header(
    supra="WFP INDONESIA — 34 PROVINSI — 215 PASAR ECERAN",
    title="Analisis Spasial",
)

# Stack views vertically instead of tabs
view_tab1 = st.container()
view_tab2 = st.container()

# ────────────────────────────────────────────────────────────────────────────
with view_tab1:
    # MAP + TOP 14 RANKING ─────────────────────────────────────────────────────
    c_map, c_rank = st.columns([1.65, 1])

    with c_map:
        df_coords = chili_raw.dropna(subset=["latitude","longitude","price"])
        if not df_coords.empty:
            mkt_geo = df_coords.groupby(["admin1","admin2","market"]).agg(
                lat=("latitude","first"), lon=("longitude","first"),
                avg_price=("price","mean"), max_price=("price","max"), count=("price","count")
            ).reset_index()
            mkt_geo["cv"] = (
                df_coords.groupby(["admin1","admin2","market"])["price"].std()
                .div(df_coords.groupby(["admin1","admin2","market"])["price"].mean())
                .reindex(mkt_geo.set_index(["admin1","admin2","market"]).index).values
            ) * 100
            hotspot = mkt_geo.loc[mkt_geo["cv"].idxmax()] if mkt_geo["cv"].notna().any() else None

            hover_txt = [
                f"<b>{r['market']}</b><br>"
                f"Kab/Kota: {r['admin2']}<br>"
                f"Provinsi: {r['admin1']}<br>"
                f"Rata-rata: Rp {r['avg_price']:,.0f}/kg<br>"
                f"Max: Rp {r['max_price']:,.0f}/kg"
                for _, r in mkt_geo.iterrows()
            ]

            fig_map = go.Figure(go.Scattermapbox(
                lat=mkt_geo["lat"], lon=mkt_geo["lon"], mode="markers",
                marker=go.scattermapbox.Marker(
                    size=9,
                    color=mkt_geo["avg_price"],
                    colorscale=[
                        [0.0, P["emerald"]], [0.4, P["tertiary"]],
                        [0.7, P["secondary"]], [1.0, P["primary"]]
                    ],
                    showscale=True,
                    colorbar=dict(
                        title=dict(text="Harga (Rp/kg)", font=dict(color=P["cream"], size=10, family="JetBrains Mono"), side="top"),
                        tickfont=dict(color=P["muted"], size=9, family="JetBrains Mono"),
                        thickness=10, tickformat=",.0f", outlinecolor="rgba(0,0,0,0)",
                        y=0.45, len=0.85
                    ),
                    opacity=0.88
                ),
                text=hover_txt, hoverinfo="text", showlegend=False
            ))
            if hotspot is not None:
                fig_map.add_trace(go.Scattermapbox(
                    lat=[hotspot["lat"]], lon=[hotspot["lon"]],
                    mode="markers+text", text=["🔥"], textfont=dict(size=18),
                    marker=go.scattermapbox.Marker(size=1),
                    hovertext=[f"<b>{hotspot['market']}</b><br>Volatilitas tertinggi (CV {hotspot['cv']:.1f}%)"],
                    hoverinfo="text", showlegend=False
                ))
            fig_map.update_layout(
                mapbox=dict(style="carto-darkmatter", center=dict(lat=-2.2, lon=118.0), zoom=3.8),
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                margin=dict(l=0, r=0, t=0, b=0), height=400,
                hoverlabel=dict(bgcolor=P["surface"], font=dict(color=P["cream"], size=11, family="Outfit"), bordercolor=P["border"])
            )
            # Heat intensity legend overlay + Download button
            st.markdown(
                f"<div style='position:relative;'>"
                f"<div style='position:absolute;top:10px;left:10px;z-index:999;"
                f"background:{P['card']}CC;border:1px solid {P['border']};border-radius:4px;padding:8px 12px;'>"
                f"<div style='font-family:\"JetBrains Mono\",monospace;font-size:9px;font-weight:700;"
                f"letter-spacing:0.1em;color:{P['muted']};margin-bottom:6px;'>HEAT INTENSITY</div>"
                f"<div style='display:flex;gap:10px;align-items:center;'>"
                f"<div style='display:flex;align-items:center;gap:4px;'>"
                f"<span style='width:7px;height:7px;border-radius:50%;background:{P['emerald']};display:inline-block;'></span>"
                f"<span style='font-family:\"JetBrains Mono\",monospace;font-size:9px;color:{P['emerald']};'>LOW</span></div>"
                f"<div style='display:flex;align-items:center;gap:4px;'>"
                f"<span style='width:7px;height:7px;border-radius:50%;background:{P['tertiary']};display:inline-block;'></span>"
                f"<span style='font-family:\"JetBrains Mono\",monospace;font-size:9px;color:{P['tertiary']};'>MODERATE</span></div>"
                f"<div style='display:flex;align-items:center;gap:4px;'>"
                f"<span style='width:7px;height:7px;border-radius:50%;background:{P['primary']};display:inline-block;'></span>"
                f"<span style='font-family:\"JetBrains Mono\",monospace;font-size:9px;color:{P['primary']};'>CRITICAL</span></div>"
                f"</div></div></div>",
                unsafe_allow_html=True
            )
            st.plotly_chart(fig_map, use_container_width=True, config={"scrollZoom": True, "displayModeBar": False})

        # Caption + Download button
        st.markdown(
            f"<div style='display:flex;justify-content:space-between;align-items:center;margin-top:-8px;'>"
            f"<div>"
            f"<div style='font-family:Outfit,sans-serif;font-size:13px;font-weight:600;color:{P['cream']};'>Geographic Spice Distribution</div>"
            f"<div style='font-family:Outfit,sans-serif;font-size:11px;color:{P['muted']};'>Real-time volatility tracking across primary trade routes</div>"
            f"</div>"
            f"</div>",
            unsafe_allow_html=True
        )

    with c_rank:
        # Rankings panel styled like reference
        prov_series = df_clean.groupby("admin1")["price"].mean().sort_values(ascending=False).head(14)
        max_val = prov_series.iloc[0]
        items_html = ""
        for i, (prov, val) in enumerate(prov_series.items()):
            clr = P["primary"] if i < 2 else (P["secondary"] if i < 5 else P["tertiary"])
            bar_w = val / max_val * 100
            items_html += (
                f"<div style='display:flex;align-items:center;gap:10px;padding:7px 0;"
                f"border-bottom:1px solid {P['border_d']};'>"
                f"<span style='font-family:\"JetBrains Mono\",monospace;font-size:10px;"
                f"color:{P['dim']};width:18px;text-align:right;'>{i+1:02d}</span>"
                f"<div style='flex:1;min-width:0;'>"
                f"<div style='font-family:Outfit,sans-serif;font-size:12px;color:{P['cream']};white-space:nowrap;overflow:hidden;text-overflow:ellipsis;'>{prov}</div>"
                f"<div style='background:{P['surface']};border-radius:2px;height:3px;margin-top:3px;'>"
                f"<div style='background:{clr};height:3px;border-radius:2px;width:{bar_w:.0f}%;'></div></div>"
                f"</div>"
                f"<span style='font-family:\"JetBrains Mono\",monospace;font-size:11px;"
                f"font-weight:700;color:{clr};white-space:nowrap;'>{val/1000:.1f}k</span>"
                f"</div>"
            )

        st.markdown(
            f"<div style='background:{P['card']};border:1px solid {P['border']};border-radius:6px;"
            f"padding:14px 16px;height:448px;overflow-y:auto;'>"
            f"<div style='display:flex;justify-content:space-between;align-items:center;margin-bottom:10px;'>"
            f"<div style='font-family:Outfit,sans-serif;font-size:14px;font-weight:700;color:{P['cream']};'>RANKINGS</div>"
            f"</div>"
            f"<div style='font-family:Outfit,sans-serif;font-size:12px;font-weight:600;color:{P['secondary']};margin-bottom:8px;'>Top 14 Provinces</div>"
            f"{items_html}"
            f"</div>",
            unsafe_allow_html=True
        )

    st.markdown("<div style='height:16px;'></div>", unsafe_allow_html=True)



    # TOP 5 TERMAHAL & TERMURAH ─────────────────────────────────────────────────
    section_header("Extremes Analysis", "Markets with the highest and lowest average prices")
    c_exp, c_chp = st.columns([1, 1])

    with c_exp:
        top_exp = mkt_stats.sort_values("mean", ascending=False).head(5)
        rows_exp = ""
        for i, (_, r) in enumerate(top_exp.iterrows()):
            clr = P["primary"] if i == 0 else (P["secondary"] if i == 1 else P["muted"])
            rows_exp += (
                f"<div style='display:flex;justify-content:space-between;align-items:center;"
                f"padding:8px 0;border-bottom:1px solid {P['border_d']};'>"
                f"<div>"
                f"<div style='font-family:Outfit,sans-serif;font-size:12px;font-weight:600;color:{P['cream']};'>{r['market']}</div>"
                f"<div style='font-family:Outfit,sans-serif;font-size:10px;color:{P['muted']};'>{r['admin1']}</div>"
                f"</div>"
                f"<span style='font-family:\"JetBrains Mono\",monospace;font-size:13px;font-weight:700;color:{clr};'>"
                f"Rp {r['mean']/1000:.0f}k</span>"
                f"</div>"
            )
        st.markdown(
            f"<div style='background:{P['card']};border:1px solid {P['border']};border-top:3px solid {P['primary']};"
            f"border-radius:6px;padding:14px 16px;'>"
            f"<div style='display:flex;align-items:center;gap:6px;margin-bottom:10px;'>"
            f"<span style='color:{P['primary']};'>↑</span>"
            f"<span style='font-family:Outfit,sans-serif;font-size:13px;font-weight:700;color:{P['cream']};'>Top 5 Expensive</span>"
            f"</div>{rows_exp}</div>",
            unsafe_allow_html=True
        )

    with c_chp:
        top_chp = mkt_stats.sort_values("mean", ascending=True).head(5)
        rows_chp = ""
        for i, (_, r) in enumerate(top_chp.iterrows()):
            clr = P["emerald"] if i < 2 else P["muted"]
            rows_chp += (
                f"<div style='display:flex;justify-content:space-between;align-items:center;"
                f"padding:8px 0;border-bottom:1px solid {P['border_d']};'>"
                f"<div>"
                f"<div style='font-family:Outfit,sans-serif;font-size:12px;font-weight:600;color:{P['cream']};'>{r['market']}</div>"
                f"<div style='font-family:Outfit,sans-serif;font-size:10px;color:{P['muted']};'>{r['admin1']}</div>"
                f"</div>"
                f"<span style='font-family:\"JetBrains Mono\",monospace;font-size:13px;font-weight:700;color:{clr};'>"
                f"Rp {r['mean']/1000:.0f}k</span>"
                f"</div>"
            )
        st.markdown(
            f"<div style='background:{P['card']};border:1px solid {P['border']};border-top:3px solid {P['emerald']};"
            f"border-radius:6px;padding:14px 16px;'>"
            f"<div style='display:flex;align-items:center;gap:6px;margin-bottom:10px;'>"
            f"<span style='color:{P['emerald']};'>↓</span>"
            f"<span style='font-family:Outfit,sans-serif;font-size:13px;font-weight:700;color:{P['cream']};'>Top 5 Cheapest</span>"
            f"</div>{rows_chp}</div>",
            unsafe_allow_html=True
        )



# ── PROVINSI TAB ─────────────────────────────────────────────────────────────
with view_tab2:
    st.markdown(f"<div style='height:16px;'></div>", unsafe_allow_html=True)
    section_header("Provincial Drill-Down", "Detailed insights and local market rankings for the selected region")
    st.markdown(f"<div style='height:8px;'></div>", unsafe_allow_html=True)

    col_sel, col_info = st.columns([1, 2])
    with col_sel:
        idx_bali = prov_list.index("BALI") if "BALI" in prov_list else 0
        sel_prov = st.selectbox(
            "PILIH PROVINSI",
            prov_list, index=idx_bali, key="prov_tab_sel",
            help="Pilih provinsi untuk melihat analisis mendalam"
        )

    with col_info:
        prov_df     = df_clean[df_clean["admin1"] == sel_prov]
        prov_avg    = prov_df["price"].mean()  if not prov_df.empty else 0
        prov_max    = prov_df["price"].max()   if not prov_df.empty else 0
        prov_min    = prov_df["price"].min()   if not prov_df.empty else 0
        prov_n_mkt  = prov_df["market"].nunique()
        natl_avg    = df_clean["price"].mean()
        vs_natl     = (prov_avg - natl_avg) / natl_avg * 100 if natl_avg > 0 else 0
        clr_vn      = P["primary"] if vs_natl > 5 else (P["emerald"] if vs_natl < -2 else P["muted"])

        mi1, mi2, mi3, mi4 = st.columns(4)
        with mi1: st.metric("Rata-rata Harga", f"Rp {prov_avg:,.0f}")
        with mi2: st.metric("vs Nasional", f"{vs_natl:+.1f}%")
        with mi3: st.metric("Harga Tertinggi", f"Rp {prov_max:,.0f}")
        with mi4: st.metric("Pasar Aktif", f"{prov_n_mkt}")

    st.markdown("<div style='height:12px;'></div>", unsafe_allow_html=True)

    # Map + Bar chart for selected province
    pc1, pc2 = st.columns([1.7, 1])
    with pc1:
        df_prov_geo = chili_raw[
            (chili_raw["admin1"] == sel_prov) &
            chili_raw["latitude"].notna() & chili_raw["longitude"].notna() & chili_raw["price"].notna()
        ]
        if not df_prov_geo.empty:
            pg = df_prov_geo.groupby("market").agg(
                lat=("latitude","first"), lon=("longitude","first"),
                avg_price=("price","mean"), count=("price","count")
            ).reset_index()
            center_lat = pg["lat"].mean()
            center_lon = pg["lon"].mean()
            fig_pm = go.Figure(go.Scattermapbox(
                lat=pg["lat"], lon=pg["lon"], mode="markers",
                marker=go.scattermapbox.Marker(
                    size=12, color=pg["avg_price"],
                    colorscale=[[0.0, P["emerald"]], [0.5, P["secondary"]], [1.0, P["primary"]]],
                    showscale=True,
                    colorbar=dict(
                        title=dict(text="Harga (Rp/kg)", font=dict(color=P["cream"], size=10, family="JetBrains Mono"), side="top"),
                        tickfont=dict(color=P["muted"], size=9), thickness=10, tickformat=",.0f", outlinecolor="rgba(0,0,0,0)",
                        y=0.45, len=0.85
                    )
                ),
                text=[f"<b>{r['market']}</b><br>Rp {r['avg_price']:,.0f}/kg" for _, r in pg.iterrows()],
                hoverinfo="text", showlegend=False
            ))
            fig_pm.update_layout(
                mapbox=dict(style="carto-darkmatter", center=dict(lat=center_lat, lon=center_lon), zoom=6),
                paper_bgcolor="rgba(0,0,0,0)", margin=dict(l=0,r=0,t=0,b=0), height=360,
                hoverlabel=dict(bgcolor=P["surface"], font=dict(color=P["cream"], size=11), bordercolor=P["border"])
            )
            st.plotly_chart(fig_pm, use_container_width=True, config={"scrollZoom": True, "displayModeBar": False})
        else:
            st.info(f"Data koordinat tidak tersedia untuk {sel_prov}.")

    with pc2:
        mkt_local = prov_df.groupby("market")["price"].mean().sort_values(ascending=False).head(10)
        if not mkt_local.empty:
            max_mkt_val = mkt_local.max()
            fig_local = go.Figure(go.Bar(
                x=mkt_local.values, y=mkt_local.index, orientation="h",
                marker_color=[P["primary"] if i < 2 else (P["secondary"] if i < 4 else P["surface"]) for i in range(len(mkt_local))],
                text=[f" Rp {v:,.0f}" for v in mkt_local.values], textposition="outside",
                textfont=dict(size=9, color=P["cream"], family="JetBrains Mono"),
                hovertemplate="<b>%{y}</b><br>Rp %{x:,.0f}/kg<extra></extra>"
            ))
            lo = blayout(f"Top Pasar — {sel_prov}", h=360, legend=False)
            lo["margin"] = dict(l=150, r=140, t=40, b=20)
            lo["xaxis"]["range"] = [0, max_mkt_val * 1.35]
            fig_local.update_layout(**lo)
            st.plotly_chart(fig_local, use_container_width=True, config={"displayModeBar": False})



footer()
