# =============================================================================
# EXECUTIVE DASHBOARD — Indonesian Chili Price Forecasting
# Chili Price Intelligence Platform
# =============================================================================

import streamlit as st
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

from utils import (
    P, inject_css, render_sidebar, page_header, footer, DATA_PATH
)

st.set_page_config(
    page_title="Indonesian Chili Price Forecasting — Project Overview",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded",
)
inject_css()
commodity_sel = render_sidebar(DATA_PATH)

st.markdown("<div style='height:20px;'></div>", unsafe_allow_html=True)

# ── OVERVIEW CONTENT ─────────────────────────────────────────────────────────
icon_flame = "<svg xmlns='http://www.w3.org/2000/svg' width='24' height='24' viewBox='0 0 24 24' fill='none' stroke='currentColor' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'><path d='M8.5 14.5A2.5 2.5 0 0 0 11 12c0-1.38-.5-2-1-3-1.072-2.143-.224-4.054 2-6 .5 2.5 2 4.9 4 6.5 2 1.6 3 3.5 3 5.5a7 7 0 1 1-14 0c0-1.153.433-2.294 1-3a2.5 2.5 0 0 0 2.5 2.5z'/></svg>"
icon_map = "<svg xmlns='http://www.w3.org/2000/svg' width='32' height='32' viewBox='0 0 24 24' fill='none' stroke='currentColor' stroke-width='1.5' stroke-linecap='round' stroke-linejoin='round'><polygon points='3 6 9 3 15 6 21 3 21 18 15 21 9 18 3 21'/><line x1='9' x2='9' y1='3' y2='18'/><line x1='15' x2='15' y1='6' y2='21'/></svg>"
icon_chart = "<svg xmlns='http://www.w3.org/2000/svg' width='32' height='32' viewBox='0 0 24 24' fill='none' stroke='currentColor' stroke-width='1.5' stroke-linecap='round' stroke-linejoin='round'><polyline points='3 3 3 21 21 21'/><polyline points='3 15 9 8 15 12 21 3'/></svg>"
icon_cpu = "<svg xmlns='http://www.w3.org/2000/svg' width='32' height='32' viewBox='0 0 24 24' fill='none' stroke='currentColor' stroke-width='1.5' stroke-linecap='round' stroke-linejoin='round'><rect width='16' height='16' x='4' y='4' rx='2'/><rect width='6' height='6' x='9' y='9' rx='1'/><path d='M15 2v2'/><path d='M15 20v2'/><path d='M2 15h2'/><path d='M2 9h2'/><path d='M20 15h2'/><path d='M20 9h2'/><path d='M9 2v2'/><path d='M9 20v2'/></svg>"

st.markdown(
    f"""
<div style='background:linear-gradient(135deg, {P['card']}, {P['bg']}); border:1px solid {P['border']}; border-radius:12px; padding:32px; margin-bottom:32px; position:relative; overflow:hidden;'>
<div style='position:absolute; top:-50px; right:-50px; width:200px; height:200px; background:radial-gradient(circle, {P['primary_a']}, transparent 70%); border-radius:50%; pointer-events:none;'></div>
<div style='display:flex; align-items:center; gap:16px; margin-bottom:20px;'>
<div style='background:{P['primary']}; width:48px; height:48px; border-radius:12px; display:flex; align-items:center; justify-content:center; color:#fff; box-shadow:0 4px 12px {P['primary_a']};'>
{icon_flame}
</div>
<h2 style='font-family:Outfit,sans-serif; font-size:28px; font-weight:800; color:{P['cream']}; margin:0;'>Indonesian Chili Price Forecasting</h2>
</div>
<p style='font-family:Outfit,sans-serif; font-size:16px; color:{P['cream']}; line-height:1.7; margin-bottom:0; max-width:900px; position:relative; z-index:1;'>
Platform prediksi harga berbasis data yang dirancang khusus untuk menganalisis dan memproyeksikan pergerakan harga cabai di Indonesia. Dashboard ini memberikan wawasan strategis mengenai tren historis, ketimpangan spasial, dan peringatan dini volatilitas pasokan.
</p>
</div>
    """,
    unsafe_allow_html=True
)

# ── MODUL UTAMA DASHBOARD ──────────────────────────────────────────────────────
st.markdown(
    f"<h2 style='font-family:Outfit,sans-serif;font-size:20px;font-weight:700;color:{P['cream']};margin-bottom:20px;'>Modul Utama Dashboard</h2>",
    unsafe_allow_html=True
)

c1, c2, c3 = st.columns(3)

with c1:
    st.markdown(
        f"""
<div style='background:{P['card']};border:1px solid {P['border']};border-radius:12px;padding:24px;height:240px;position:relative;overflow:hidden;'>
<div style='position:absolute;top:0;left:0;right:0;height:4px;background:linear-gradient(90deg, {P['primary']}, transparent);'></div>
<div style='color:{P['primary']};margin-bottom:16px;'>{icon_map}</div>
<b style='color:{P['cream']};font-size:18px;font-family:Outfit,sans-serif;display:block;margin-bottom:12px;'>Analisis Spasial</b>
<p style='margin:0;font-size:14px;color:{P['muted']};font-family:Outfit,sans-serif;line-height:1.6;'>
Memetakan tingkat ketimpangan harga cabai di berbagai provinsi di Indonesia dan membandingkannya dengan rata-rata nasional.
</p>
</div>
        """,
        unsafe_allow_html=True
    )

with c2:
    st.markdown(
        f"""
<div style='background:{P['card']};border:1px solid {P['border']};border-radius:12px;padding:24px;height:240px;position:relative;overflow:hidden;'>
<div style='position:absolute;top:0;left:0;right:0;height:4px;background:linear-gradient(90deg, {P['secondary']}, transparent);'></div>
<div style='color:{P['secondary']};margin-bottom:16px;'>{icon_chart}</div>
<b style='color:{P['cream']};font-size:18px;font-family:Outfit,sans-serif;display:block;margin-bottom:12px;'>Tren Musiman</b>
<p style='margin:0;font-size:14px;color:{P['muted']};font-family:Outfit,sans-serif;line-height:1.6;'>
Melacak pergerakan historis harga dalam 4 tahun terakhir untuk mengidentifikasi siklus panen raya dan fase volatilitas.
</p>
</div>
        """,
        unsafe_allow_html=True
    )

with c3:
    st.markdown(
        f"""
<div style='background:{P['card']};border:1px solid {P['border']};border-radius:12px;padding:24px;height:240px;position:relative;overflow:hidden;'>
<div style='position:absolute;top:0;left:0;right:0;height:4px;background:linear-gradient(90deg, {P['tertiary']}, transparent);'></div>
<div style='color:{P['tertiary']};margin-bottom:16px;'>{icon_cpu}</div>
<b style='color:{P['cream']};font-size:18px;font-family:Outfit,sans-serif;display:block;margin-bottom:12px;'>Model Proyeksi</b>
<p style='margin:0;font-size:14px;color:{P['muted']};font-family:Outfit,sans-serif;line-height:1.6;'>
Memanfaatkan kombinasi <i>Machine Learning</i> (Random Forest) dan model musiman (Holt-Winters) untuk memproyeksikan tren hingga 12 bulan ke depan.
</p>
</div>
        """,
        unsafe_allow_html=True
    )

st.markdown("<div style='height:32px;'></div>", unsafe_allow_html=True)

# ── TEKNOLOGI & DATA ──────────────────────────────────────────────────────────
def tech_pill(icon_svg, name, color):
    parts = name.split()
    first = parts[0]
    rest = " ".join(parts[1:]) if len(parts) > 1 else ""
    return f"""
<div style='display:flex;align-items:center;gap:8px;background:{P['surface']};border:1px solid {P['border']};
padding:8px 16px;border-radius:30px;font-family:\"JetBrains Mono\",monospace;font-size:12px;color:{P['cream']};'>
<span style='color:{color};display:flex;'>{icon_svg}</span> 
<span><span style='color:{color};font-weight:700;'>{first}</span> {rest}</span>
</div>
    """

icon_db = "<svg xmlns='http://www.w3.org/2000/svg' width='18' height='18' viewBox='0 0 24 24' fill='none' stroke='currentColor' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'><ellipse cx='12' cy='5' rx='9' ry='3'/><path d='M3 5V19A9 3 0 0 0 21 19V5'/><path d='M3 12A9 3 0 0 0 21 12'/></svg>"
icon_bolt = "<svg xmlns='http://www.w3.org/2000/svg' width='18' height='18' viewBox='0 0 24 24' fill='none' stroke='currentColor' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'><polygon points='13 2 3 14 12 14 11 22 21 10 12 10 13 2'/></svg>"

icon_code = "<svg xmlns='http://www.w3.org/2000/svg' width='16' height='16' viewBox='0 0 24 24' fill='none' stroke='currentColor' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'><polyline points='16 18 22 12 16 6'/><polyline points='8 6 2 12 8 18'/></svg>"
icon_table = "<svg xmlns='http://www.w3.org/2000/svg' width='16' height='16' viewBox='0 0 24 24' fill='none' stroke='currentColor' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'><rect width='18' height='18' x='3' y='3' rx='2'/><path d='M3 9h18'/><path d='M9 21V9'/></svg>"
icon_pie = "<svg xmlns='http://www.w3.org/2000/svg' width='16' height='16' viewBox='0 0 24 24' fill='none' stroke='currentColor' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'><path d='M21.21 15.89A10 10 0 1 1 8 2.83'/><path d='M22 12A10 10 0 0 0 12 2v10z'/></svg>"
icon_net = "<svg xmlns='http://www.w3.org/2000/svg' width='16' height='16' viewBox='0 0 24 24' fill='none' stroke='currentColor' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'><rect width='6' height='6' x='2' y='9' rx='1'/><rect width='6' height='6' x='16' y='2' rx='1'/><rect width='6' height='6' x='16' y='16' rx='1'/><path d='M8 12h8'/><path d='M12 12V5h4'/><path d='M12 12v7h4'/></svg>"

tech_html = f"""
<div style='background:{P['card']};border:1px solid {P['border']};border-radius:12px;padding:32px;'>
<div style='display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:32px;'>

<!-- Data Source -->
<div style='flex:1;min-width:300px;'>
<div style='display:flex;align-items:center;gap:12px;margin-bottom:16px;'>
<div style='width:36px;height:36px;border-radius:8px;background:{P['surface']};display:flex;align-items:center;justify-content:center;color:{P['tertiary']};border:1px solid {P['border']};'>
{icon_db}
</div>
<h3 style='font-family:Outfit,sans-serif;font-size:18px;font-weight:700;color:{P['cream']};margin:0;'>Data Foundation</h3>
</div>
<div style='background:{P['surface']};border-left:3px solid {P['tertiary']};padding:16px;border-radius:6px;border:1px solid {P['border']};border-left-width:3px;border-left-color:{P['tertiary']};'>
<b style='font-family:Outfit,sans-serif;font-size:15px;color:{P['cream']};'>WFP - Indonesia Food Prices</b>
<p style='font-family:Outfit,sans-serif;font-size:13px;color:{P['muted']};margin:6px 0 0 0;line-height:1.5;'>
Dataset pergerakan harga pangan Indonesia dengan fokus analisis panel 2020–2024 pada 34 provinsi.
</p>
</div>
</div>

<!-- Tech Stack -->
<div style='flex:1.5;min-width:400px;'>
<div style='display:flex;align-items:center;gap:12px;margin-bottom:16px;'>
<div style='width:36px;height:36px;border-radius:8px;background:{P['surface']};display:flex;align-items:center;justify-content:center;color:{P['primary']};border:1px solid {P['border']};'>
{icon_bolt}
</div>
<h3 style='font-family:Outfit,sans-serif;font-size:18px;font-weight:700;color:{P['cream']};margin:0;'>Technology Stack</h3>
</div>

<div style='display:flex;flex-wrap:wrap;gap:12px;'>
{tech_pill(icon_code, "Streamlit UI", P['primary'])}
{tech_pill(icon_table, "Pandas & NumPy", P['emerald'])}
{tech_pill(icon_pie, "Plotly Graphs", P['secondary'])}
{tech_pill(icon_net, "Scikit-Learn & Statsmodels", P['tertiary'])}
</div>
</div>

</div>
</div>
"""

st.markdown(tech_html, unsafe_allow_html=True)

st.markdown("<div style='height:40px;'></div>", unsafe_allow_html=True)
footer()