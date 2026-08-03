# =============================================================================
# SHARED UTILITIES — Chili Price Intelligence / Heat & Spice
# Seleksi Internal Satria Data 2026
# =============================================================================

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import csv
import io
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error
import warnings
warnings.filterwarnings("ignore")

# =============================================================================
# DESIGN TOKENS — Heat & Spice "Thermal Spectrum"
# =============================================================================

P = {
    # ── Surfaces
    "bg":          "#051424",
    "card":        "#0D1C2D",
    "surface":     "#122131",
    "surface_hi":  "#1C2B3C",
    "surface_top": "#273647",
    # ── Borders
    "border":      "#1C2B3C",
    "border_d":    "#0D1C2D",
    "outline":     "#5C4039",
    # ── Thermal Accents
    "primary":     "#FF5625",   # Chili Red — forecast line, CTA, critical alerts
    "primary_a":   "rgba(255,86,37,0.12)",
    "secondary":   "#F97316",   # Orange — confidence intervals, secondary trends
    "secondary_a": "rgba(249,115,22,0.12)",
    "tertiary":    "#FBBF24",   # Amber — peak indicators, warnings, highlights
    "tertiary_a":  "rgba(251,191,36,0.12)",
    # ── Text
    "cream":       "#D4E4FA",
    "on_surface":  "#D4E4FA",
    "muted":       "#94A3B8",
    "dim":         "#5C7A99",
    # ── Semantic
    "emerald":     "#22C55E",
    "emerald_a":   "rgba(34,197,94,0.12)",
    "red":         "#EF4444",
    "red_a":       "rgba(239,68,68,0.12)",
    # ── Aliases for legacy compat
    "crimson":     "#FF5625",
    "crim_a":      "rgba(255,86,37,0.12)",
    "amber":       "#F97316",
    "amber_a":     "rgba(249,115,22,0.12)",
    "indigo":      "#FBBF24",
    "indigo_a":    "rgba(251,191,36,0.12)",
    "amber_mid":   "#E86010",
    "crim_mid":    "#CC3A14",
}

MONTH_ABB  = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
MONTH_ID   = ["Jan","Feb","Mar","Apr","Mei","Jun","Jul","Agu","Sep","Okt","Nov","Des"]
MONTH_FULL = ["Januari","Februari","Maret","April","Mei","Juni",
              "Juli","Agustus","September","Oktober","November","Desember"]

DATA_PATH = "dataset/wfp_food_prices_idn.csv"

FEAT_COLS = [
    "month_sin","month_cos","quarter","year",
    "lag_1","lag_2","lag_3","lag_6","lag_12",
    "roll3_mean","roll6_mean","roll3_std","roll6_std",
    "pct_1m","pct_3m",
]

COMMODITY_LABELS = {
    "birds_eye": "Cabai Rawit (Bird's Eye)",
    "red":       "Cabai Merah (Red Chili)",
    "all":       "Semua Jenis Cabai",
}

# =============================================================================
# CSS INJECTION — Heat & Spice "Dark Lab"
# =============================================================================

def inject_css():
    st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600;700&display=swap');

html, body, .stApp, [data-testid="stAppViewContainer"] {{
    background-color: {P['bg']} !important;
    font-family: 'Outfit', -apple-system, sans-serif !important;
    color: {P['cream']} !important;
}}
[data-testid="block-container"] {{
    padding: 1.4rem 2.8rem 3rem !important;
    max-width: 1560px;
}}

/* ── SIDEBAR ── */
[data-testid="stSidebar"] {{
    background-color: {P['card']} !important;
    border-right: 1px solid {P['border']} !important;
    position: relative;
}}
[data-testid="stSidebar"]::after {{
    content: '';
    position: absolute;
    top: 0; right: 0; bottom: 0;
    width: 2px;
    background: linear-gradient(to bottom, {P['primary']}, {P['secondary']});
    opacity: 0.7;
}}
[data-testid="stSidebarContent"] {{
    padding-top: 1rem !important;
}}

/* ── METRIC CARDS — Heat & Spice style ── */
[data-testid="metric-container"] {{
    background: {P['card']} !important;
    border: 1px solid {P['border']} !important;
    border-radius: 6px !important;
    padding: 1rem 1.2rem !important;
    position: relative;
    overflow: hidden;
}}
[data-testid="metric-container"]::before {{
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, {P['primary']}, {P['secondary']}, {P['tertiary']});
}}
[data-testid="metric-container"]::after {{
    content: '';
    position: absolute;
    top: 0; right: 0;
    width: 80px; height: 80px;
    background: radial-gradient(circle at top right, {P['primary_a']}, transparent 70%);
    pointer-events: none;
}}
[data-testid="stMetricLabel"] p {{
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 10px !important;
    font-weight: 700 !important;
    letter-spacing: 0.12em !important;
    text-transform: uppercase !important;
    color: {P['muted']} !important;
    margin: 0 !important;
}}
[data-testid="stMetricValue"] {{
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 22px !important;
    font-weight: 700 !important;
    color: {P['cream']} !important;
    line-height: 1.2 !important;
}}
[data-testid="stMetricDelta"] span {{
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 11px !important;
}}

/* ── TYPOGRAPHY ── */
h1, h2, h3, h4 {{
    font-family: 'Outfit', sans-serif !important;
    color: {P['cream']} !important;
    font-weight: 700 !important;
    letter-spacing: -0.02em;
}}
hr {{
    border: none !important;
    border-top: 1px solid {P['border_d']} !important;
    margin: 1.6rem 0 !important;
}}

/* ── INPUTS & SELECTS ── */
[data-baseweb="select"] > div {{
    background-color: {P['surface']} !important;
    border-color: {P['border']} !important;
    color: {P['cream']} !important;
    border-radius: 4px !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 12px !important;
}}
[data-baseweb="select"] svg {{ fill: {P['muted']} !important; }}
[data-baseweb="popover"] ul {{ background: {P['surface']} !important; border-color: {P['border']} !important; }}
[data-baseweb="popover"] li {{ color: {P['cream']} !important; font-family: 'Outfit', sans-serif !important; font-size: 13px !important; }}
[data-baseweb="popover"] li:hover {{ background: {P['surface_hi']} !important; }}
div[data-baseweb="input"] > div {{
    background-color: {P['surface']} !important;
    border-color: {P['border']} !important;
    color: {P['cream']} !important;
    border-radius: 4px !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 12px !important;
}}
div[data-baseweb="input"] > div:focus-within {{
    border-color: {P['secondary']} !important;
    box-shadow: 0 0 0 2px {P['secondary_a']} !important;
}}

/* ── DATAFRAME ── */
[data-testid="stDataFrame"] {{
    background: {P['card']} !important;
    border-radius: 6px !important;
    border: 1px solid {P['border']} !important;
}}

/* ── TABS ── */
[data-baseweb="tab-list"] {{
    background: transparent !important;
    border-bottom: 1px solid {P['border']} !important;
    gap: 4px !important;
}}
[data-baseweb="tab"] {{
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 11px !important;
    font-weight: 600 !important;
    letter-spacing: 0.08em !important;
    text-transform: uppercase !important;
    color: {P['dim']} !important;
    background: transparent !important;
    border: 1px solid {P['border']} !important;
    border-bottom: none !important;
    border-radius: 4px 4px 0 0 !important;
    padding: 6px 16px !important;
}}
[aria-selected="true"][data-baseweb="tab"] {{
    color: {P['primary']} !important;
    background: {P['card']} !important;
    border-color: {P['primary']} !important;
}}

/* ── SCROLLBAR ── */
::-webkit-scrollbar {{ width: 5px; height: 5px; }}
::-webkit-scrollbar-track {{ background: {P['bg']}; }}
::-webkit-scrollbar-thumb {{ background: {P['border']}; border-radius: 3px; }}
::-webkit-scrollbar-thumb:hover {{ background: {P['primary']}; }}

/* ── HIDE STREAMLIT CHROME ── */
#MainMenu, footer {{ visibility: hidden !important; }}
[data-testid="stToolbar"] {{ display: none !important; }}
[data-testid="stDecoration"] {{ display: none !important; }}

/* ── SIDEBAR NAV ── */
[data-testid="stSidebarNav"] {{
    padding-top: 95px !important;
    padding-bottom: 0px !important;
    margin-bottom: -15px !important;
}}
.custom-sidebar-brand {{
    position: fixed !important;
    top: 28px !important;
    left: 28px !important;
    width: 250px !important;
    z-index: 999999 !important;
    pointer-events: none;
}}
[data-testid="stSidebarNavItems"] a {{
    color: {P['muted']} !important;
    border-radius: 6px !important;
    font-family: 'Outfit', sans-serif !important;
    font-size: 14px !important;
    font-weight: 500 !important;
    padding: 8px 16px !important;
    margin: 2px 16px !important;
    transition: all 0.15s ease;
    display: flex !important;
    align-items: center !important;
    text-decoration: none !important;
}}
[data-testid="stSidebarNavItems"] a:hover {{
    background: {P['surface']} !important;
    color: {P['cream']} !important;
}}
[data-testid="stSidebarNavItems"] a[aria-current="page"] {{
    background: {P['secondary']} !important;
    color: #fff !important;
    font-weight: 600 !important;
}}
[data-testid="stSidebarNavItems"] a span {{
    display: none !important;
}}
[data-testid="stSidebarNavItems"] a::before {{
    content: '';
    display: inline-block;
    width: 18px;
    height: 18px;
    margin-right: 12px;
    background-color: currentColor;
    -webkit-mask-size: contain;
    -webkit-mask-repeat: no-repeat;
    -webkit-mask-position: center;
    mask-size: contain;
    mask-repeat: no-repeat;
    mask-position: center;
}}
[data-testid="stSidebarNavItems"] li:nth-child(1) a::before {{
    -webkit-mask-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='currentColor' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Crect x='3' y='3' width='7' height='7'/%3E%3Crect x='14' y='3' width='7' height='7'/%3E%3Crect x='14' y='14' width='7' height='7'/%3E%3Crect x='3' y='14' width='7' height='7'/%3E%3C/svg%3E");
    mask-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='currentColor' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Crect x='3' y='3' width='7' height='7'/%3E%3Crect x='14' y='3' width='7' height='7'/%3E%3Crect x='14' y='14' width='7' height='7'/%3E%3Crect x='3' y='14' width='7' height='7'/%3E%3C/svg%3E");
}}
[data-testid="stSidebarNavItems"] li:nth-child(1) a::after {{
    content: 'Overview';
}}
[data-testid="stSidebarNavItems"] li:nth-child(2) a::before {{
    -webkit-mask-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='currentColor' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpolygon points='3 6 9 3 15 6 21 3 21 18 15 21 9 18 3 21'/%3E%3Cline x1='9' y1='3' x2='9' y2='18'/%3E%3Cline x1='15' y1='6' x2='15' y2='21'/%3E%3C/svg%3E");
    mask-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='currentColor' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpolygon points='3 6 9 3 15 6 21 3 21 18 15 21 9 18 3 21'/%3E%3Cline x1='9' y1='3' x2='9' y2='18'/%3E%3Cline x1='15' y1='6' x2='15' y2='21'/%3E%3C/svg%3E");
}}
[data-testid="stSidebarNavItems"] li:nth-child(2) a::after {{
    content: 'Spatial';
}}
[data-testid="stSidebarNavItems"] li:nth-child(3) a::before {{
    -webkit-mask-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='currentColor' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpolyline points='23 6 13.5 15.5 8.5 10.5 1 18'/%3E%3Cpolyline points='17 6 23 6 23 12'/%3E%3C/svg%3E");
    mask-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='currentColor' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpolyline points='23 6 13.5 15.5 8.5 10.5 1 18'/%3E%3Cpolyline points='17 6 23 6 23 12'/%3E%3C/svg%3E");
}}
[data-testid="stSidebarNavItems"] li:nth-child(3) a::after {{
    content: 'Trends';
}}
[data-testid="stSidebarNavItems"] li:nth-child(4) a::before {{
    -webkit-mask-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='currentColor' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cline x1='18' y1='20' x2='18' y2='10'/%3E%3Cline x1='12' y1='20' x2='12' y2='4'/%3E%3Cline x1='6' y1='20' x2='6' y2='14'/%3E%3C/svg%3E");
    mask-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='currentColor' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cline x1='18' y1='20' x2='18' y2='10'/%3E%3Cline x1='12' y1='20' x2='12' y2='4'/%3E%3Cline x1='6' y1='20' x2='6' y2='14'/%3E%3C/svg%3E");
}}
[data-testid="stSidebarNavItems"] li:nth-child(4) a::after {{
    content: 'Model';
}}

/* ── BUTTONS ── */
[data-testid="stButton"] button {{
    background: transparent !important;
    border: 1px solid {P['muted']} !important;
    color: {P['cream']} !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 11px !important;
    font-weight: 600 !important;
    letter-spacing: 0.08em !important;
    border-radius: 4px !important;
    transition: all 0.2s ease;
}}
[data-testid="stButton"] button:hover {{
    border-color: {P['secondary']} !important;
    color: {P['secondary']} !important;
    box-shadow: 0 0 8px {P['secondary_a']};
}}

/* ── SPINNER ── */
[data-testid="stSpinner"] {{ color: {P['secondary']} !important; }}

/* ── PROGRESS BAR ── */
[data-testid="stProgress"] > div > div {{
    background: linear-gradient(90deg, {P['primary']}, {P['secondary']}) !important;
}}
</style>
""", unsafe_allow_html=True)


# =============================================================================
# DATA PIPELINE
# =============================================================================

@st.cache_data(show_spinner=False)
def load_wfp_raw(path: str) -> pd.DataFrame:
    rows, header = [], None
    with open(path, encoding="utf-8") as f:
        reader = csv.reader(f)
        for i, row in enumerate(reader):
            if i == 0:
                header = row
                continue
            if len(row) == 1:
                try:
                    row = next(csv.reader(io.StringIO(row[0])))
                except StopIteration:
                    continue
            rows.append(row)
    df = pd.DataFrame(rows, columns=header)
    df["price"]     = pd.to_numeric(df["price"],     errors="coerce")
    df["date"]      = pd.to_datetime(df["date"],     errors="coerce")
    df["latitude"]  = pd.to_numeric(df["latitude"],  errors="coerce")
    df["longitude"] = pd.to_numeric(df["longitude"], errors="coerce")
    return df


@st.cache_data(show_spinner=False)
def get_chili_wfp(path: str, commodity_type: str = "birds_eye") -> pd.DataFrame:
    df = load_wfp_raw(path)
    ch = (df[df["commodity"].str.contains("Chili|chili", na=False, regex=True)]
          .dropna(subset=["date", "price", "admin1"]).copy())
    ch = ch[ch["admin1"].astype(str).str.strip() != ""].copy()
    # Filter: Data dari 2020 sampai 2024 saja
    ch = ch[(ch["date"] >= "2020-01-01") & (ch["date"] <= "2024-05-31")].copy()
    # Clean outlier/errant price entries
    ch = ch[(ch["price"] >= 5000) & (ch["price"] <= 200000)]
    if commodity_type == "birds_eye":
        ch = ch[ch["commodity"].str.lower().str.contains("bird", na=False)]
    elif commodity_type == "red":
        ch = ch[ch["commodity"].str.lower().str.contains("red", na=False)]
    return ch.sort_values("date").reset_index(drop=True)


@st.cache_data(show_spinner=False)
def get_national_monthly(path: str, commodity_type: str = "birds_eye") -> pd.DataFrame:
    ch = get_chili_wfp(path, commodity_type)
    m = (
        ch.groupby(pd.Grouper(key="date", freq="MS"))["price"]
        .mean().reset_index()
        .rename(columns={"date": "Date", "price": "Price"})
    )
    return m.dropna().sort_values("Date").reset_index(drop=True)


@st.cache_data(show_spinner=False)
def get_provincial_monthly(path: str, commodity_type: str = "birds_eye", province: str = None) -> pd.DataFrame:
    """Monthly average prices for a specific province (or national if None)."""
    ch = get_chili_wfp(path, commodity_type)
    if province and province != "NASIONAL":
        ch = ch[ch["admin1"] == province]
    if ch.empty:
        return pd.DataFrame(columns=["Date", "Price"])
    m = (
        ch.groupby(pd.Grouper(key="date", freq="MS"))["price"]
        .mean().reset_index()
        .rename(columns={"date": "Date", "price": "Price"})
    )
    return m.dropna().sort_values("Date").reset_index(drop=True)


# =============================================================================
# FEATURE ENGINEERING & MODELING
# =============================================================================

def make_features(df: pd.DataFrame) -> pd.DataFrame:
    d = df.copy()
    d["year"]      = d["Date"].dt.year
    d["month"]     = d["Date"].dt.month
    d["month_sin"] = np.sin(2 * np.pi * d["month"] / 12)
    d["month_cos"] = np.cos(2 * np.pi * d["month"] / 12)
    d["quarter"]   = d["Date"].dt.quarter
    for lag in [1, 2, 3, 6, 12]:
        d[f"lag_{lag}"] = d["Price"].shift(lag)
    d["roll3_mean"] = d["Price"].shift(1).rolling(3).mean()
    d["roll6_mean"] = d["Price"].shift(1).rolling(6).mean()
    d["roll3_std"]  = d["Price"].shift(1).rolling(3).std()
    d["roll6_std"]  = d["Price"].shift(1).rolling(6).std()
    d["pct_1m"]     = d["Price"].pct_change(1)
    d["pct_3m"]     = d["Price"].pct_change(3)
    return d.dropna().reset_index(drop=True)


@st.cache_data(show_spinner=False)
def train_wfp_model(path: str, commodity_type: str = "birds_eye") -> dict:
    mdf  = get_national_monthly(path, commodity_type)
    feat = make_features(mdf)
    sp   = int(len(feat) * 0.80)
    tr, te = feat.iloc[:sp], feat.iloc[sp:]
    rf = RandomForestRegressor(
        n_estimators=300, max_depth=5,
        min_samples_leaf=2, random_state=42, n_jobs=-1
    )
    rf.fit(tr[FEAT_COLS], tr["Price"])
    pred = rf.predict(te[FEAT_COLS])
    y    = te["Price"].values
    mae  = float(mean_absolute_error(y, pred))
    rmse = float(np.sqrt(mean_squared_error(y, pred)))
    mape = float(np.mean(np.abs((y - pred) / np.where(y != 0, y, 1))) * 100)
    r2   = float(1 - np.sum((y - pred) ** 2) / np.sum((y - y.mean()) ** 2))
    return dict(rf=rf, feat=feat, tr=tr, te=te, pred=pred, y=y,
                mae=mae, rmse=rmse, mape=mape, r2=r2, mdf=mdf)


def forecast_months_ahead(res: dict, n: int = 7) -> pd.DataFrame:
    """
    Multi-step forecasting using Holt-Winters Exponential Smoothing to capture
    dynamic seasonal waves (December-March surge, May-August trough).
    """
    mdf = res["mdf"].copy()
    ts  = mdf.set_index("Date")["Price"]
    ts.index = pd.date_range(ts.index[0], periods=len(ts), freq="MS")
    
    try:
        from statsmodels.tsa.holtwinters import ExponentialSmoothing
        try:
            hw_model = ExponentialSmoothing(ts, seasonal_periods=12, trend="add", seasonal="add", initialization_method="heuristic")
            hw_fit   = hw_model.fit(optimized=True)
            fc_vals  = hw_fit.forecast(n)
        except Exception:
            hw_model = ExponentialSmoothing(ts, seasonal_periods=12, trend="add", seasonal="add", initialization_method="estimated")
            hw_fit   = hw_model.fit()
            fc_vals  = hw_fit.forecast(n)
    except Exception:
        # Fallback: Seasonal additive projection based on historical monthly averages
        mdf_calc = mdf.copy()
        mdf_calc["Month"] = mdf_calc["Date"].dt.month
        monthly_means = mdf_calc.groupby("Month")["Price"].mean()
        overall_mean = mdf_calc["Price"].mean()
        seasonal_diff = monthly_means - overall_mean
        
        last_date = ts.index.max()
        future_dates = pd.date_range(last_date + pd.DateOffset(months=1), periods=n, freq="MS")
        last_val = ts.iloc[-1]
        
        fc_list = []
        for d in future_dates:
            m = d.month
            s_factor = seasonal_diff.get(m, 0.0)
            # Smooth transition from last observed price + seasonal deviation
            pred_val = last_val * 0.4 + (overall_mean + s_factor) * 0.6
            fc_list.append(pred_val)
        fc_vals = pd.Series(fc_list, index=future_dates)
        
    last_date = ts.index.max()
    future_dates = pd.date_range(last_date + pd.DateOffset(months=1), periods=n, freq="MS")
    
    rows = []
    rmse = res.get("rmse", ts.std() * 0.15)
    for step, (d, fval) in enumerate(zip(future_dates, fc_vals)):
        ci = float(rmse * (1.0 + step * 0.12))
        rows.append({
            "Date": d,
            "Forecast": float(fval),
            "Lower": max(0.0, float(fval) - ci),
            "Upper": float(fval) + ci,
            "step": step + 1
        })
    return pd.DataFrame(rows)


# =============================================================================
# PLOTLY LAYOUT HELPER
# =============================================================================

def blayout(title: str = "", h: int = 380, legend: bool = True,
            y_sfx: str = "", y_fmt: str = ",.0f") -> dict:
    return dict(
        title=dict(
            text=f"<b style='color:{P['cream']};font-size:12px;font-family:Outfit,sans-serif;letter-spacing:0.02em;'>{title}</b>",
            x=0, xanchor="left", pad=dict(l=4, b=10),
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Outfit, sans-serif", color=P["muted"], size=11),
        height=h,
        margin=dict(l=10, r=10, t=42, b=10),
        xaxis=dict(
            gridcolor=P["border_d"], linecolor=P["border"],
            tickcolor="rgba(0,0,0,0)",
            tickfont=dict(size=10, color=P["muted"], family="JetBrains Mono, monospace"),
            zeroline=False,
        ),
        yaxis=dict(
            gridcolor=P["border_d"], linecolor="rgba(0,0,0,0)",
            tickcolor="rgba(0,0,0,0)",
            tickfont=dict(size=10, color=P["muted"], family="JetBrains Mono, monospace"),
            tickformat=y_fmt, ticksuffix=y_sfx,
            zeroline=False,
        ),
        legend=(dict(
            bgcolor="rgba(0,0,0,0)",
            font=dict(size=10, color=P["cream"], family="JetBrains Mono, monospace"),
            orientation="h", y=1.08, x=1, xanchor="right"
        ) if legend else dict(visible=False)),
        hovermode="x unified",
        hoverlabel=dict(
            bgcolor=P["surface"],
            font=dict(color=P["cream"], size=11, family="Outfit, sans-serif"),
            bordercolor=P["border"],
        ),
    )


# =============================================================================
# HTML COMPONENT HELPERS
# =============================================================================

def stat_card(label: str, value: str, sub: str = "", accent: str = None, mono_val: bool = True) -> str:
    """Premium stat card with top gradient stripe and radial glow."""
    a = accent or P["primary"]
    val_font = "font-family:'JetBrains Mono',monospace;" if mono_val else "font-family:'Outfit',sans-serif;"
    return (
        f"<div style='background:{P['card']};border:1px solid {P['border']};border-radius:6px;"
        f"padding:16px 18px;position:relative;overflow:hidden;'>"
        f"<div style='position:absolute;top:0;left:0;right:0;height:2px;"
        f"background:linear-gradient(90deg,{P['primary']},{P['secondary']},{P['tertiary']});'></div>"
        f"<div style='position:absolute;top:0;right:0;width:80px;height:80px;"
        f"background:radial-gradient(circle at top right,{a}1A,transparent 70%);pointer-events:none;'></div>"
        f"<div style='font-family:\"JetBrains Mono\",monospace;font-size:10px;font-weight:700;"
        f"letter-spacing:0.12em;text-transform:uppercase;color:{P['muted']};margin-bottom:6px;'>{label}</div>"
        f"<div style='{val_font}font-size:22px;font-weight:700;color:{P['cream']};line-height:1.2;'>{value}</div>"
        + (f"<div style='font-size:11px;color:{P['muted']};margin-top:4px;'>{sub}</div>" if sub else "")
        + "</div>"
    )


def insight_card(title: str, body: str, accent: str = None) -> str:
    a = accent or P["primary"]
    return (
        f"<div style='background:{P['card']};border:1px solid {P['border']};"
        f"border-left:3px solid {a};border-radius:6px;"
        f"padding:14px 18px;margin-bottom:16px;'>"
        f"<div style='font-family:\"JetBrains Mono\",monospace;font-size:10px;font-weight:700;"
        f"letter-spacing:0.14em;text-transform:uppercase;color:{a};margin-bottom:6px;'>{title}</div>"
        f"<div style='font-family:\"Outfit\",sans-serif;font-size:13px;color:{P['cream']};"
        f"line-height:1.65;font-weight:400;'>{body}</div></div>"
    )


def status_chip(label: str, color: str = None) -> str:
    c = color or P["primary"]
    return (
        f"<span style='background:{c};color:#000;font-family:\"JetBrains Mono\",monospace;"
        f"font-size:9px;font-weight:700;letter-spacing:0.1em;text-transform:uppercase;"
        f"border-radius:3px;padding:2px 7px;vertical-align:middle;'>{label}</span>"
    )


def section_header(title: str, subtitle: str = "") -> None:
    st.markdown(
        f"<div style='margin-bottom:12px;'>"
        f"<h3 style='font-family:Outfit,sans-serif;margin-bottom:2px;font-size:17px;'>{title}</h3>"
        + (f"<p style='font-family:Outfit,sans-serif;font-size:12px;color:{P['muted']};margin:0;'>{subtitle}</p>" if subtitle else "")
        + "</div>",
        unsafe_allow_html=True
    )


def page_header(supra: str, title: str, desc: str = "", right_widget: str = "") -> None:
    st.markdown(
        f"<div style='display:flex;justify-content:space-between;align-items:flex-start;"
        f"padding:4px 0 16px;border-bottom:1px solid {P['border']};margin-bottom:20px;'>"
        f"<div>"
        f"<div style='font-family:\"JetBrains Mono\",monospace;font-size:9px;font-weight:700;"
        f"letter-spacing:0.2em;text-transform:uppercase;color:{P['secondary']};margin-bottom:3px;'>{supra}</div>"
        f"<div style='font-family:Outfit,sans-serif;font-size:24px;font-weight:800;"
        f"letter-spacing:-0.03em;color:{P['cream']};line-height:1.1;'>{title}</div>"
        + (f"<div style='font-family:Outfit,sans-serif;margin-top:5px;font-size:12px;color:{P['muted']};'>{desc}</div>" if desc else "")
        + f"</div>{right_widget}</div>",
        unsafe_allow_html=True
    )


def footer() -> None:
    st.markdown("---")
    st.markdown(
        f"<div style='display:flex;justify-content:space-between;align-items:center;"
        f"padding:8px 0 2px;'>"
        f"<div style='font-family:\"JetBrains Mono\",monospace;font-size:10px;color:{P['dim']};'>"
        f"© 2025 SPICE ANALYTICA · ENGINE: HEAT-1 · GPL COMPLIANT</div>"
        f"<div style='display:flex;gap:8px;align-items:center;'>"
        f"<span style='width:7px;height:7px;border-radius:50%;background:{P['emerald']};display:inline-block;'></span>"
        f"<span style='font-family:\"JetBrains Mono\",monospace;font-size:10px;color:{P['dim']};'>SYSTEMS NOMINAL</span>"
        f"</div></div>",
        unsafe_allow_html=True
    )


# =============================================================================
# SIDEBAR RENDERER
# =============================================================================

def render_sidebar(path: str) -> str:
    with st.sidebar:
        # Brand
        st.markdown(
            f"<div class='custom-sidebar-brand'>"
            f"<div style='font-family:Outfit,sans-serif;font-size:18px;font-weight:800;color:{P['cream']};letter-spacing:-0.02em;line-height:1.2;'>"
            f"<span style='color:{P['primary']};'>Indonesian Chili</span><br>Price Forecasting</div>"
            f"</div>",
            unsafe_allow_html=True
        )

        commodity_sel = st.selectbox(
            "VARIETAS CABAI",
            options=["birds_eye", "red", "all"],
            format_func=lambda x: COMMODITY_LABELS[x],
            index=0,
            key="nav_commodity_type"
        )

        # Dataset stats calculation
        chili_preview = get_chili_wfp(path, commodity_sel)

        n_prov = chili_preview["admin1"].nunique() if not chili_preview.empty and "admin1" in chili_preview.columns else 0
        n_kab  = chili_preview["admin2"].nunique() if not chili_preview.empty and "admin2" in chili_preview.columns else 0
        n_mkt  = chili_preview["market"].nunique() if not chili_preview.empty and "market" in chili_preview.columns else 0
        n_obs  = len(chili_preview)

        avg_p = chili_preview["price"].mean() if not chili_preview.empty else 0
        min_p = chili_preview["price"].min()  if not chili_preview.empty else 0
        max_p = chili_preview["price"].max()  if not chili_preview.empty else 0

        if not chili_preview.empty and "date" in chili_preview.columns:
            min_date = chili_preview["date"].min()
            max_date = chili_preview["date"].max()
            period_str = f"{min_date.strftime('%b %Y')} – {max_date.strftime('%b %Y')}"
        else:
            period_str = "Jan 2020 – Mei 2024"

        st.markdown(
            f"<div style='background:{P['surface']};border:1px solid {P['border']};"
            f"border-radius:6px;padding:12px 14px;margin:12px 16px;'>"
            f"<div style='font-family:\"JetBrains Mono\",monospace;font-size:9px;font-weight:700;"
            f"letter-spacing:0.12em;text-transform:uppercase;color:{P['tertiary']};margin-bottom:8px;'>DATASET OVERVIEW</div>"
            f"<div style='font-family:Outfit,sans-serif;font-size:11px;color:{P['muted']};line-height:2.0;'>"
            f"Provinsi &nbsp;<b style='color:{P['cream']};font-family:\"JetBrains Mono\",monospace;'>{n_prov} Provinsi</b><br>"
            f"Cakupan &nbsp;<b style='color:{P['cream']};font-family:\"JetBrains Mono\",monospace;'>{n_kab} Kab/Kota · {n_mkt} Pasar</b><br>"
            f"Periode &nbsp;<b style='color:{P['cream']};font-family:\"JetBrains Mono\",monospace;'>{period_str}</b><br>"
            f"Total Observasi &nbsp;<b style='color:{P['cream']};font-family:\"JetBrains Mono\",monospace;'>{n_obs:,} data</b><br>"
            f"Rata-rata &nbsp;<b style='color:{P['secondary']};font-family:\"JetBrains Mono\",monospace;'>Rp {avg_p:,.0f}/kg</b><br>"
            f"Terendah &nbsp;<b style='color:{P['cream']};font-family:\"JetBrains Mono\",monospace;'>Rp {min_p:,.0f}/kg</b><br>"
            f"Tertinggi &nbsp;<b style='color:{P['cream']};font-family:\"JetBrains Mono\",monospace;'>Rp {max_p:,.0f}/kg</b>"
            f"</div></div>",
            unsafe_allow_html=True
        )

    return commodity_sel
