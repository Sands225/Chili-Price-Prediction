# =============================================================================
# SHARED UTILITIES — Chili Price Intelligence Dashboard
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
# DESIGN TOKENS
# =============================================================================

P = {
    "bg":        "#080B11",
    "card":      "#0F1420",
    "surface":   "#171F30",
    "border":    "#212B3E",
    "border_d":  "#141B29",
    "crimson":   "#F43F5E",
    "crim_a":    "rgba(244, 63, 94, 0.12)",
    "emerald":   "#10B981",
    "emerald_a": "rgba(16, 185, 129, 0.12)",
    "amber":     "#F59E0B",
    "amber_a":   "rgba(245, 158, 11, 0.12)",
    "indigo":    "#6366F1",
    "indigo_a":  "rgba(99, 102, 241, 0.12)",
    "cream":     "#F8FAFC",
    "muted":     "#94A3B8",
    "dim":       "#475569",
    "crim_mid":  "#BE123C",
    "amber_mid": "#B45309",
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
# CSS INJECTION
# =============================================================================

def inject_css():
    st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap');

html, body, .stApp, [data-testid="stAppViewContainer"] {{
    background-color: {P['bg']} !important;
    font-family: 'Inter', -apple-system, sans-serif !important;
    color: {P['cream']} !important;
}}
[data-testid="block-container"] {{
    padding: 1.8rem 3.2rem 3rem !important;
    max-width: 1480px;
}}
[data-testid="stSidebar"] {{
    background-color: {P['card']} !important;
    border-right: 1px solid {P['border']} !important;
}}
[data-testid="stSidebarContent"] {{
    padding-top: 1rem !important;
}}
[data-testid="metric-container"] {{
    background: {P['card']} !important;
    border: 1px solid {P['border']} !important;
    border-radius: 8px !important;
    padding: 1.1rem 1.3rem !important;
    position: relative;
    overflow: hidden;
    box-shadow: 0 4px 12px rgba(0,0,0,0.2);
}}
[data-testid="metric-container"]::after {{
    content: '';
    position: absolute;
    bottom: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, {P['crimson']}, {P['amber']}, {P['emerald']});
}}
[data-testid="stMetricLabel"] p {{
    font-size: 10.5px !important;
    font-weight: 700 !important;
    letter-spacing: 0.1em !important;
    text-transform: uppercase !important;
    color: {P['muted']} !important;
    margin: 0 !important;
}}
[data-testid="stMetricValue"] {{
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 21px !important;
    font-weight: 600 !important;
    color: {P['cream']} !important;
    line-height: 1.3 !important;
}}
[data-testid="stMetricDelta"] span {{
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 11px !important;
}}
h1, h2, h3, h4 {{ color: {P['cream']} !important; font-weight: 700 !important; letter-spacing: -0.02em; }}
hr {{ border: none !important; border-top: 1px solid {P['border_d']} !important; margin: 1.8rem 0 !important; }}
[data-baseweb="select"] > div {{
    background-color: {P['surface']} !important;
    border-color: {P['border']} !important;
    color: {P['cream']} !important;
    border-radius: 6px !important;
}}
[data-baseweb="select"] svg {{ fill: {P['muted']} !important; }}
[data-baseweb="popover"] ul {{ background: {P['surface']} !important; border-color: {P['border']} !important; }}
[data-baseweb="popover"] li {{ color: {P['cream']} !important; }}
[data-baseweb="popover"] li:hover {{ background: {P['border']} !important; }}
div[data-baseweb="input"] > div {{
    background-color: {P['surface']} !important;
    border-color: {P['border']} !important;
    color: {P['cream']} !important;
    border-radius: 6px !important;
}}
[data-testid="stDataFrame"] {{ background: {P['card']} !important; border-radius: 8px !important; }}
::-webkit-scrollbar {{ width: 6px; height: 6px; }}
::-webkit-scrollbar-track {{ background: {P['bg']}; }}
::-webkit-scrollbar-thumb {{ background: {P['border']}; border-radius: 4px; }}
::-webkit-scrollbar-thumb:hover {{ background: {P['crimson']}; }}
#MainMenu, footer {{ visibility: hidden !important; }}
[data-testid="stToolbar"] {{ display: none !important; }}
[data-testid="stDecoration"] {{ display: none !important; }}
[data-testid="stSidebarNavItems"] a {{
    color: {P['muted']} !important;
    border-radius: 6px !important;
    font-size: 13px !important;
    padding: 6px 10px !important;
}}
[data-testid="stSidebarNavItems"] a:hover {{
    background: {P['surface']} !important;
    color: {P['cream']} !important;
}}
[data-testid="stSidebarNavItems"] a[aria-current="page"] {{
    background: {P['surface']} !important;
    color: {P['emerald']} !important;
    font-weight: 600 !important;
}}
</style>
""", unsafe_allow_html=True)


# =============================================================================
# DATA PIPELINE
# =============================================================================

@st.cache_data(show_spinner=False)
def load_wfp_raw(path: str) -> pd.DataFrame:
    """Load and parse WFP food prices CSV dataset."""
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
    """Filter dataset by chili variety."""
    df = load_wfp_raw(path)
    ch = (df[df["commodity"].str.contains("Chili|chili", na=False, regex=True)]
          .dropna(subset=["date", "price"]).copy())
    if commodity_type == "birds_eye":
        ch = ch[ch["commodity"].str.lower().str.contains("bird", na=False)]
    elif commodity_type == "red":
        ch = ch[ch["commodity"].str.lower().str.contains("red", na=False)]
    return ch.sort_values("date").reset_index(drop=True)


@st.cache_data(show_spinner=False)
def get_national_monthly(path: str, commodity_type: str = "birds_eye") -> pd.DataFrame:
    """Compute monthly national average prices."""
    ch = get_chili_wfp(path, commodity_type)
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
    """Engineer time-series features for Random Forest model."""
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
    """Train Random Forest model and return results dict."""
    mdf  = get_national_monthly(path, commodity_type)
    feat = make_features(mdf)
    sp   = int(len(feat) * 0.82)
    tr, te = feat.iloc[:sp], feat.iloc[sp:]

    rf = RandomForestRegressor(
        n_estimators=400, max_depth=7,
        min_samples_leaf=2, random_state=42, n_jobs=-1
    )
    rf.fit(tr[FEAT_COLS], tr["Price"])
    pred = rf.predict(te[FEAT_COLS])
    y    = te["Price"].values

    mae  = float(mean_absolute_error(y, pred))
    rmse = float(np.sqrt(mean_squared_error(y, pred)))
    mape = float(np.mean(np.abs((y - pred) / np.where(y != 0, y, 1))) * 100)
    r2   = float(1 - np.sum((y - pred) ** 2) / np.sum((y - y.mean()) ** 2))

    return dict(
        rf=rf, feat=feat, tr=tr, te=te,
        pred=pred, y=y,
        mae=mae, rmse=rmse, mape=mape, r2=r2,
        mdf=mdf
    )


def forecast_months_ahead(res: dict, n: int = 7) -> pd.DataFrame:
    """Recursive multi-step forecast using trained RF model."""
    rf   = res["rf"]
    feat = res["feat"].copy()
    rows = []
    for step in range(n):
        p  = feat["Price"]
        nd = pd.Timestamp(feat["Date"].iloc[-1]) + pd.DateOffset(months=1)
        lag12 = p.iloc[-12] if len(p) >= 12 else p.iloc[0]
        lag4  = p.iloc[-4]  if len(p) >= 4  else p.iloc[0]
        row = {
            "month_sin":  np.sin(2 * np.pi * nd.month / 12),
            "month_cos":  np.cos(2 * np.pi * nd.month / 12),
            "quarter":    (nd.month - 1) // 3 + 1,
            "year":       nd.year,
            "lag_1":  p.iloc[-1], "lag_2": p.iloc[-2],
            "lag_3":  p.iloc[-3], "lag_6": p.iloc[-6] if len(p) >= 6 else p.iloc[0],
            "lag_12": lag12,
            "roll3_mean": p.iloc[-3:].mean(),
            "roll6_mean": p.iloc[-6:].mean() if len(p) >= 6 else p.mean(),
            "roll3_std":  float(p.iloc[-3:].std(ddof=0)),
            "roll6_std":  float(p.iloc[-6:].std(ddof=0)) if len(p) >= 6 else 0.0,
            "pct_1m": (p.iloc[-1] - p.iloc[-2]) / p.iloc[-2] if p.iloc[-2] else 0,
            "pct_3m": (p.iloc[-1] - lag4) / lag4 if lag4 else 0,
        }
        X    = pd.DataFrame([row])[FEAT_COLS]
        fval = float(rf.predict(X)[0])
        # CI widens with horizon (accumulated uncertainty)
        base_ci = float(np.array([t.predict(X)[0] for t in rf.estimators_]).std())
        ci = base_ci * (1.4 + step * 0.15)  # CI grows with forecast horizon
        rows.append({
            "Date": nd, "Forecast": fval,
            "Lower": max(0.0, fval - ci), "Upper": fval + ci,
            "step": step + 1
        })
        new_row = pd.DataFrame([{"Date": nd, "Price": fval, **row}])
        feat = pd.concat([feat, new_row], ignore_index=True)
    return pd.DataFrame(rows)


# =============================================================================
# PLOTLY LAYOUT HELPER
# =============================================================================

def blayout(title: str = "", h: int = 380, legend: bool = True,
            y_sfx: str = "", y_fmt: str = ",.0f") -> dict:
    return dict(
        title=dict(
            text=f"<b style='color:{P['cream']};font-size:12px;font-family:Inter,sans-serif;letter-spacing:0.04em;'>{title}</b>",
            x=0, xanchor="left", pad=dict(l=4, b=12),
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, sans-serif", color=P["muted"], size=11),
        height=h,
        margin=dict(l=10, r=10, t=42, b=10),
        xaxis=dict(
            gridcolor=P["border_d"], linecolor=P["border"],
            tickcolor="rgba(0,0,0,0)",
            tickfont=dict(size=10, color=P["muted"]),
            zeroline=False,
        ),
        yaxis=dict(
            gridcolor=P["border_d"], linecolor="rgba(0,0,0,0)",
            tickcolor="rgba(0,0,0,0)",
            tickfont=dict(size=10, color=P["muted"]),
            tickformat=y_fmt, ticksuffix=y_sfx,
            zeroline=False,
        ),
        legend=(dict(
            bgcolor="rgba(0,0,0,0)",
            font=dict(size=10, color=P["cream"]),
            orientation="h", y=1.08, x=1, xanchor="right"
        ) if legend else dict(visible=False)),
        hovermode="x unified",
        hoverlabel=dict(
            bgcolor=P["surface"],
            font=dict(color=P["cream"], size=11),
            bordercolor=P["border"],
        ),
    )


# =============================================================================
# HTML COMPONENT HELPERS
# =============================================================================

def insight_card(title: str, body: str, accent: str = None) -> str:
    a = accent or P["crimson"]
    return (
        f"<div style='background:{P['card']};border:1px solid {P['border']};"
        f"border-left:4px solid {a};border-radius:8px;"
        f"padding:16px 20px;margin-bottom:18px;'>"
        f"<div style='font-size:10px;font-weight:800;letter-spacing:0.14em;"
        f"text-transform:uppercase;color:{a};margin-bottom:6px;'>{title}</div>"
        f"<div style='font-size:12.5px;color:{P['cream']};line-height:1.65;"
        f"font-weight:400;'>{body}</div></div>"
    )


def section_header(title: str, subtitle: str = "") -> None:
    """Renders a standardized section header."""
    st.markdown(
        f"<h3 style='margin-bottom:4px;'>{title}</h3>"
        + (f"<p style='font-size:12px;color:{P['muted']};margin-bottom:16px;'>{subtitle}</p>" if subtitle else ""),
        unsafe_allow_html=True
    )


def page_header(supra: str, title: str, desc: str = "") -> None:
    """Renders the standard top-of-page header block."""
    st.markdown(
        f"<div style='padding:8px 0 4px;'>"
        f"<div style='font-size:9px;font-weight:800;letter-spacing:0.2em;"
        f"text-transform:uppercase;color:{P['emerald']};margin-bottom:4px;'>{supra}</div>"
        f"<div style='font-size:26px;font-weight:800;letter-spacing:-0.03em;"
        f"color:{P['cream']};line-height:1.1;'>{title}</div>"
        + (f"<div style='margin-top:6px;font-size:12px;color:{P['muted']};'>{desc}</div>" if desc else "")
        + "</div>",
        unsafe_allow_html=True
    )
    st.markdown("<br>", unsafe_allow_html=True)


def footer() -> None:
    st.markdown("---")
    st.markdown(
        f"<div style='text-align:center;padding:10px 0 4px;font-size:11px;color:{P['dim']};'>"
        f"Chili Price Intelligence Platform &nbsp;&middot;&nbsp; "
        f"Data: WFP Food Prices Indonesia &nbsp;&middot;&nbsp; Seleksi Internal Satria Data 2026"
        f"</div>",
        unsafe_allow_html=True
    )


# =============================================================================
# SIDEBAR RENDERER (shared across all pages)
# =============================================================================

def render_sidebar(path: str) -> str:
    """Render commodity selector + dataset summary in sidebar. Returns selected commodity key."""
    with st.sidebar:
        st.markdown(
            f"<div style='padding:6px 0 10px;'>"
            f"<div style='font-size:9px;font-weight:800;letter-spacing:0.18em;"
            f"text-transform:uppercase;color:{P['emerald']};margin-bottom:4px;'>"
            f"WFP FOOD PRICES — INDONESIA</div>"
            f"<div style='font-size:17px;font-weight:800;color:{P['cream']};line-height:1.2;margin-bottom:14px;'>"
            f"Chili Price Intelligence</div>"
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

        chili_preview = get_chili_wfp(path, commodity_sel)
        avg_p = chili_preview["price"].mean() if not chili_preview.empty else 0
        min_p = chili_preview["price"].min()  if not chili_preview.empty else 0
        max_p = chili_preview["price"].max()  if not chili_preview.empty else 0
        n_obs = len(chili_preview)

        st.markdown(
            f"<div style='background:{P['surface']};border:1px solid {P['border']};"
            f"border-radius:8px;padding:14px;margin:10px 0;'>"
            f"<div style='font-size:9px;font-weight:800;letter-spacing:0.12em;"
            f"text-transform:uppercase;color:{P['amber']};margin-bottom:8px;'>RINGKASAN DATASET</div>"
            f"<div style='font-size:11px;color:{P['muted']};line-height:1.9;'>"
            f"&bull; Total Observasi: <b style='color:{P['cream']};'>{n_obs:,}</b><br>"
            f"&bull; Rata-rata: <b style='color:{P['emerald']};'>Rp {avg_p:,.0f}/kg</b><br>"
            f"&bull; Terendah: <b style='color:{P['cream']};'>Rp {min_p:,.0f}/kg</b><br>"
            f"&bull; Tertinggi: <b style='color:{P['cream']};'>Rp {max_p:,.0f}/kg</b>"
            f"</div></div>",
            unsafe_allow_html=True
        )

        st.markdown(
            f"<div style='margin-top:8px;'>"
            f"<div style='font-size:9px;font-weight:800;letter-spacing:0.12em;"
            f"text-transform:uppercase;color:{P['dim']};margin-bottom:8px;'>MODUL ANALISIS</div>"
            f"<div style='font-size:11px;color:{P['dim']};line-height:2.1;'>"
            f"&#9632;&nbsp; Overview Eksekutif<br>"
            f"&#9632;&nbsp; Analisis Spasial<br>"
            f"&#9632;&nbsp; Tren &amp; Musiman<br>"
            f"&#9632;&nbsp; Model Proyeksi"
            f"</div></div>",
            unsafe_allow_html=True
        )

    return commodity_sel
