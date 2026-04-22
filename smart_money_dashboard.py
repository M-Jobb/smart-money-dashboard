# =============================================================================
# SMART MONEY DASHBOARD — Streamlit-app
# Kombinerer Modul 1 (Sektor RS), Modul 2 (VSA/Whale Tracker) og
# Modul 3 (Wyckoff-fase) i ett interaktivt dashboard
#
# INSTALLASJON:
#   pip install streamlit yfinance pandas pandas_ta plotly scipy tqdm
#
# KJØRING:
#   streamlit run smart_money_dashboard.py
# =============================================================================

import streamlit as st
import yfinance as yf
import pandas as pd
import pandas_ta as ta
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from scipy.signal import argrelextrema
from datetime import datetime, timedelta
from dataclasses import dataclass
from typing import Optional
import warnings
warnings.filterwarnings('ignore')

# =============================================================================
# SIDE-KONFIGURASJON
# =============================================================================

st.set_page_config(
    page_title="Smart Money Dashboard",
    page_icon="🐋",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Mørkt tema via custom CSS
st.markdown("""
<style>
    /* Generell bakgrunn og typografi */
    .stApp { background-color: #0d1117; color: #c9d1d9; }
    .stApp header { background-color: #0d1117; }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #161b22;
        border-right: 1px solid #30363d;
    }
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] .stMarkdown p { color: #8b949e; font-size: 13px; }
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 { color: #c9d1d9; }

    /* Metric-kort */
    [data-testid="metric-container"] {
        background: #161b22;
        border: 1px solid #30363d;
        border-radius: 8px;
        padding: 14px 16px;
    }
    [data-testid="metric-container"] label { color: #8b949e !important; font-size: 12px !important; }
    [data-testid="metric-container"] [data-testid="stMetricValue"] {
        color: #c9d1d9 !important;
        font-size: 22px !important;
        font-weight: 500 !important;
    }

    /* Tabeller */
    .dataframe { background-color: #161b22 !important; color: #c9d1d9 !important; }
    .dataframe th { background-color: #21262d !important; color: #8b949e !important; font-size: 12px !important; }
    .dataframe td { font-size: 13px !important; }

    /* Faner */
    .stTabs [data-baseweb="tab-list"] { background: #161b22; border-radius: 8px; padding: 4px; }
    .stTabs [data-baseweb="tab"] { color: #8b949e; border-radius: 6px; }
    .stTabs [aria-selected="true"] { background: #21262d !important; color: #c9d1d9 !important; }

    /* Seksjonstittler */
    h1 { color: #e6edf3 !important; font-size: 24px !important; font-weight: 500 !important; }
    h2 { color: #c9d1d9 !important; font-size: 18px !important; font-weight: 500 !important; }
    h3 { color: #8b949e !important; font-size: 14px !important; font-weight: 500 !important; }

    /* Divider */
    hr { border-color: #30363d; }

    /* Score-badge i tabell */
    .score-high { color: #3fb950; font-weight: 500; }
    .score-mid  { color: #d29922; font-weight: 500; }
    .score-low  { color: #f85149; font-weight: 500; }
</style>
""", unsafe_allow_html=True)

# =============================================================================
# KONSTANTER
# =============================================================================

SEKTORER = {
    'XLK':  ('Teknologi',              ['NVDA','MSFT','AAPL','AVGO','AMD','CRM','ORCL','QCOM','TXN','INTC','AMAT','MU','LRCX','KLAC','ADI','MRVL','PANW','CRWD','SNPS','CDNS']),
    'XLF':  ('Finans',                 ['BRK-B','JPM','V','MA','BAC','WFC','GS','MS','BLK','SPGI','AXP','CB','CME','ICE','PGR','TRV','MET','PRU','AFL','AIG']),
    'XLE':  ('Energi',                 ['XOM','CVX','COP','EOG','SLB','MPC','PXD','VLO','PSX','OXY','HES','DVN','BKR','FANG','HAL','APA','EQT','MRO','CTRA','OVV']),
    'XLV':  ('Helse',                  ['LLY','UNH','JNJ','ABBV','MRK','TMO','ABT','DHR','PFE','AMGN','MDT','ISRG','GILD','CVS','CI','HCA','ZTS','ELV','SYK','BSX']),
    'XLI':  ('Industri',               ['GE','RTX','HON','UNP','BA','DE','ETN','LMT','NOC','GD','MMM','ITW','EMR','CMI','PH','FDX','UPS','CSX','NSC','WM']),
    'XLY':  ('Forbruksdiskresjonær',   ['AMZN','TSLA','HD','MCD','NKE','SBUX','LOW','BKNG','TJX','CMG','F','GM','ABNB','DHI','LEN','NVR','PHM','MAR','HLT','YUM']),
    'XLP':  ('Forbruksstabeltre',      ['PG','COST','KO','PEP','WMT','PM','MO','MDLZ','CL','EL','STZ','KHC','GIS','HSY','K','SJM','MKC','CAG','CPB','HRL']),
    'XLU':  ('Utilities',              ['NEE','SO','DUK','AEP','SRE','EXC','XEL','PEG','ED','AWK','PPL','ES','FE','NI','CMS','CNP','LNT','OGE','PNW','WEC']),
    'XLB':  ('Materialer',             ['LIN','APD','SHW','FCX','NEM','NUE','VMC','MLM','ALB','CE','IFF','PPG','IP','CF','MOS','FMC','SEE','PKG','WRK','BALL']),
    'XLRE': ('Eiendom',                ['PLD','AMT','CCI','EQIX','SPG','O','PSA','WELL','DLR','AVB','EQR','SBA','SBAC','WPC','EXR','HST','ARE','BXP','UDR','NNN']),
    'XLC':  ('Kommunikasjonstjenester',['META','GOOGL','GOOG','NFLX','T','VZ','DIS','CMCSA','TMUS','CHTR','EA','WBD','PARA','OMC','IPG','NWSA','FOX','LYV','ZM','MTCH']),
}

BENCHMARK = 'SPY'

PERIODE_VALG = {
    '1 måned':   30,
    '3 måneder': 90,
    '6 måneder': 180,
    '1 år':      365,
}

WYCKOFF_FASE_FARGE = {
    'spring':         '#3fb950',
    'markup':         '#388bfd',
    'akkumulering_B': '#a371f7',
    'akkumulering_A': '#6e7681',
    'distribusjon':   '#d29922',
    'markdown':       '#f85149',
}

# =============================================================================
# CACHING — viktig for ytelse i Streamlit
# =============================================================================

@st.cache_data(ttl=1800, show_spinner=False)  # Cache i 30 min
def hent_data(tickers: tuple, dager: int) -> pd.DataFrame:
    """Henter OHLCV-data for en liste tickers. Cached."""
    start = (datetime.today() - timedelta(days=dager + 10)).strftime('%Y-%m-%d')
    raw = yf.download(list(tickers), start=start, progress=False, auto_adjust=True)
    if isinstance(raw.columns, pd.MultiIndex):
        return raw
    # Enkelt-ticker: pakk inn i MultiIndex-format
    raw.columns = pd.MultiIndex.from_product([raw.columns, tickers])
    return raw

@st.cache_data(ttl=1800, show_spinner=False)
def hent_enkelt(ticker: str, dager: int) -> pd.DataFrame:
    """Henter OHLCV for én ticker. Cached."""
    start = (datetime.today() - timedelta(days=dager + 10)).strftime('%Y-%m-%d')
    raw = yf.download(ticker, start=start, progress=False, auto_adjust=True)
    df = pd.DataFrame({
        'Open':   raw['Open'].squeeze(),
        'High':   raw['High'].squeeze(),
        'Low':    raw['Low'].squeeze(),
        'Close':  raw['Close'].squeeze(),
        'Volume': raw['Volume'].squeeze(),
    }).dropna()
    return df.tail(dager)

# =============================================================================
# ANALYSE-FUNKSJONER
# =============================================================================

def beregn_relativ_styrke(closes: pd.Series, benchmark: pd.Series, dager: int) -> float:
    """RS = avkastning aksje - avkastning benchmark over N dager."""
    s = closes.dropna().tail(dager)
    b = benchmark.dropna().tail(dager)
    if len(s) < 2 or len(b) < 2:
        return 0.0
    return round(
        (s.iloc[-1]/s.iloc[0] - 1 - (b.iloc[-1]/b.iloc[0] - 1)) * 100, 2
    )

def vpa_analyse(df: pd.DataFrame) -> dict:
    """
    Volum-Pris-Analyse: teller og scorer VSA-signaler.
    Returnerer en dict med signal-tellere og samlet VSA-score.
    """
    df = df.copy().dropna()
    vol_sma = df['Volume'].rolling(20).mean()
    vol_ratio = df['Volume'] / vol_sma
    chg = df['Close'].pct_change() * 100
    close_pct = (df['Close'] - df['Low']) / (df['High'] - df['Low'] + 1e-9)

    absorpsjon = int(((vol_ratio >= 1.8) & (chg.abs() <= 0.8)).sum())
    thrust      = int(((vol_ratio >= 1.5) & (chg >= 0.8) & (close_pct >= 0.65)).sum())
    shakeout    = int(((vol_ratio >= 2.5) & (chg < -0.5) & (close_pct >= 0.45)).sum())

    # OBV-trend
    obv = ta.obv(df['Close'], df['Volume'])
    obv_slope = (obv.iloc[-1] - obv.iloc[-min(20, len(obv))]) if len(obv) > 5 else 0

    # VSA-score (0-100)
    score = min(100, absorpsjon * 8 + thrust * 10 + shakeout * 6 +
                (15 if obv_slope > 0 else 0))

    return {
        'absorpsjon':  absorpsjon,
        'sos_thrust':  thrust,
        'shakeout':    shakeout,
        'obv_stigende': obv_slope > 0,
        'vsa_score':   round(score, 1),
    }

def wyckoff_fase_enkel(df: pd.DataFrame, rs: float) -> tuple[str, float]:
    """
    Forenklet Wyckoff-fase for rask scanning.
    Returnerer (fase, confidence_score).
    """
    if len(df) < 30:
        return 'ukjent', 0.0

    closes  = df['Close'].values
    highs   = df['High'].values
    lows    = df['Low'].values
    vol     = df['Volume'].values
    vol_sma = pd.Series(vol).rolling(20).mean().values

    # Swing-nivåer
    hi_idx = argrelextrema(highs, np.greater, order=8)[0]
    lo_idx = argrelextrema(lows,  np.less,    order=8)[0]
    resist = float(np.median(highs[hi_idx])) if len(hi_idx) else highs.max()
    support = float(np.median(lows[lo_idx]))  if len(lo_idx) else lows.min()

    kurs = closes[-1]
    range_h = resist - support

    # OBV
    obv = ta.obv(df['Close'], df['Volume'])
    obv_trend = obv.iloc[-1] > obv.iloc[-min(20, len(obv))]

    # VSA
    vpa = vpa_analyse(df)

    # Spring-sjekk
    spring = False
    for i in range(-10, 0):
        try:
            if df['Low'].iloc[i] < support * 0.99 and df['Close'].iloc[i] > support:
                spring = True
                break
        except IndexError:
            break

    score = 50
    if obv_trend:            score += 12
    if spring:               score += 18
    if rs > 2:               score += 10
    if vpa['absorpsjon'] >= 2: score += 10
    if vpa['sos_thrust'] >= 1: score += 8
    if not obv_trend:        score -= 15
    if rs < -3:              score -= 10

    markup  = kurs > resist * 1.01 and vpa['sos_thrust'] >= 1
    dist    = kurs > support + range_h * 0.65 and not obv_trend
    mdown   = kurs < support * 0.97 and not obv_trend and rs < -3

    if mdown:   return 'markdown',       max(5,  min(score, 35))
    if dist:    return 'distribusjon',   max(20, min(score, 50))
    if markup:  return 'markup',         max(65, min(score, 92))
    if spring:  return 'spring',         max(72, min(score, 98))
    if vpa['absorpsjon'] >= 2 or vpa['obv_stigende']:
                return 'akkumulering_B', max(55, min(score, 82))
    return      'akkumulering_A',        max(35, min(score, 68))

def beregn_smart_money_score(rs: float, vsa_score: float,
                              cm_score: float, obv_opp: bool) -> float:
    """
    Sammensatt Smart Money Score (0–100).
    Vekting: RS 25% | VSA 30% | Wyckoff 30% | OBV 15%
    """
    rs_n   = min(100, max(0, (rs + 15) / 30 * 100)) * 0.25
    vsa_n  = min(100, vsa_score)                     * 0.30
    cm_n   = min(100, cm_score)                      * 0.30
    obv_n  = (100 if obv_opp else 0)                 * 0.15
    return round(rs_n + vsa_n + cm_n + obv_n, 1)

# =============================================================================
# SEKTOR-SCREENING (Modul 1 — rask versjon)
# =============================================================================

@st.cache_data(ttl=1800, show_spinner=False)
def sektor_screening(periode_dager: int) -> pd.DataFrame:
    """Beregner relativ styrke for alle 11 sektorer mot SPY."""
    alle = list(SEKTORER.keys()) + [BENCHMARK]
    raw = hent_data(tuple(alle), periode_dager)
    benchmark_serie = raw['Close'][BENCHMARK].dropna()

    rader = []
    for etf, (navn, _) in SEKTORER.items():
        if etf not in raw['Close'].columns:
            continue
        close = raw['Close'][etf].dropna()
        rs_1m  = beregn_relativ_styrke(close, benchmark_serie, 21)
        rs_3m  = beregn_relativ_styrke(close, benchmark_serie, 63)
        rs_6m  = beregn_relativ_styrke(close, benchmark_serie, 126)
        rader.append({'ETF': etf, 'Sektor': navn,
                      'RS 1M': rs_1m, 'RS 3M': rs_3m, 'RS 6M': rs_6m,
                      'Score': round(rs_1m * 0.3 + rs_3m * 0.45 + rs_6m * 0.25, 2)})

    return pd.DataFrame(rader).sort_values('Score', ascending=False).reset_index(drop=True)

# =============================================================================
# DRILL-DOWN SCANNER (Modul 2+3 kombinert)
# =============================================================================

@st.cache_data(ttl=1800, show_spinner=False)
def drill_down_scanner(sektor_etf: str, periode_dager: int) -> pd.DataFrame:
    """
    Henter de 20 største komponentene i valgt sektor og kjører full analyse.
    Sjekker: Relativ styrke, VPA og Wyckoff-fase.
    Returnerer tabell sortert etter Smart Money Score.
    """
    _, tickers = SEKTORER[sektor_etf]
    tickers_20 = tickers[:20]

    # Hent all data i én batch
    alle = list(set(tickers_20 + [sektor_etf, BENCHMARK]))
    raw = hent_data(tuple(alle), max(periode_dager, 120) + 20)

    if 'Close' not in raw.columns.get_level_values(0):
        return pd.DataFrame()

    benchmark_serie = raw['Close'][BENCHMARK].dropna()
    sektor_serie    = raw['Close'][sektor_etf].dropna()

    rader = []
    for ticker in tickers_20:
        if ticker not in raw['Close'].columns:
            continue

        close = raw['Close'][ticker].dropna()
        if len(close) < 30:
            continue

        # Bygg OHLCV
        try:
            df_ticker = pd.DataFrame({
                'Open':   raw['Open'][ticker],
                'High':   raw['High'][ticker],
                'Low':    raw['Low'][ticker],
                'Close':  raw['Close'][ticker],
                'Volume': raw['Volume'][ticker],
            }).dropna().tail(max(periode_dager, 120))
        except KeyError:
            continue

        # Beregninger
        rs_vs_spy    = beregn_relativ_styrke(close, benchmark_serie, periode_dager)
        rs_vs_sektor = beregn_relativ_styrke(close, sektor_serie, periode_dager)
        vpa          = vpa_analyse(df_ticker)
        fase, cm_sc  = wyckoff_fase_enkel(df_ticker, rs_vs_spy)
        sms          = beregn_smart_money_score(rs_vs_spy, vpa['vsa_score'],
                                                cm_sc, vpa['obv_stigende'])

        kurs = float(close.iloc[-1])
        chg_1d = float((close.iloc[-1] / close.iloc[-2] - 1) * 100) if len(close) > 1 else 0

        rader.append({
            'Ticker':        ticker,
            'Kurs':          round(kurs, 2),
            '1d %':          round(chg_1d, 2),
            'RS vs SPY':     rs_vs_spy,
            'RS vs Sektor':  rs_vs_sektor,
            'Absorpsjon':    vpa['absorpsjon'],
            'Vol-thrust':    vpa['sos_thrust'],
            'VSA Score':     vpa['vsa_score'],
            'Wyckoff Fase':  fase,
            'CM Score':      round(cm_sc, 1),
            'OBV Opp':       vpa['obv_stigende'],
            'Smart Money':   sms,
        })

    df = pd.DataFrame(rader).sort_values('Smart Money', ascending=False).reset_index(drop=True)
    df.index += 1
    return df

# =============================================================================
# PLOT-FUNKSJONER
# =============================================================================

def plot_sektor_heatmap(df: pd.DataFrame) -> go.Figure:
    """Interaktivt varmekart: sektorer × tidsperioder."""
    z = df[['RS 1M', 'RS 3M', 'RS 6M']].values
    tekst = [[f"{v:+.1f}%" for v in row] for row in z]

    fig = go.Figure(go.Heatmap(
        z=z,
        x=['1 måned', '3 måneder', '6 måneder'],
        y=df['ETF'] + ' — ' + df['Sektor'],
        text=tekst,
        texttemplate='%{text}',
        textfont={'size': 12, 'color': 'white'},
        colorscale=[
            [0.0,  '#7f1d1d'], [0.25, '#b91c1c'],
            [0.40, '#c2410c'], [0.50, '#374151'],
            [0.60, '#166534'], [0.75, '#15803d'],
            [1.0,  '#14532d'],
        ],
        zmid=0,
        showscale=True,
        colorbar=dict(
            title=dict(
                text='RS vs SPY (%)',
                font=dict(color='#8b949e')
            ),
            tickfont=dict(color='#8b949e'),
            bgcolor='#0d1117',
        ),
    ))
    fig.update_layout(
        paper_bgcolor='#0d1117', plot_bgcolor='#0d1117',
        height=420,
        margin=dict(l=10, r=20, t=20, b=10),
        xaxis=dict(side='top', tickfont=dict(color='#8b949e', size=12)),
        yaxis=dict(tickfont=dict(color='#c9d1d9', size=11), autorange='reversed'),
        font=dict(family='monospace'),
    )

    return fig

def plot_rs_boble(df: pd.DataFrame) -> go.Figure:
    """
    Bobel-diagram: X = Smart Money Score, Y = RS vs SPY.
    Størrelse = Absorpsjons-dager, Farge = Wyckoff-fase.
    """
    fase_hex = {
        'spring': '#3fb950', 'markup': '#388bfd',
        'akkumulering_B': '#a371f7', 'akkumulering_A': '#6e7681',
        'distribusjon': '#d29922', 'markdown': '#f85149',
    }
    df = df.copy()
    df['Farge'] = df['Wyckoff Fase'].map(fase_hex).fillna('#6e7681')
    df['Størrelse'] = (df['Absorpsjon'] * 12 + 40).clip(40, 200)

    fig = go.Figure()

    for fase, farge in fase_hex.items():
        subset = df[df['Wyckoff Fase'] == fase]
        if subset.empty:
            continue
        fig.add_trace(go.Scatter(
            x=subset['Smart Money'],
            y=subset['RS vs SPY'],
            mode='markers+text',
            name=fase.replace('_', ' ').title(),
            text=subset['Ticker'],
            textposition='middle center',
            textfont=dict(size=10, color='white'),
            marker=dict(
                size=subset['Størrelse'] / 5,
                color=farge,
                opacity=0.85,
                line=dict(width=1, color='rgba(255,255,255,0.3)'),
            ),
            hovertemplate=(
                '<b>%{text}</b><br>'
                'Smart Money: %{x:.1f}<br>'
                'RS vs SPY: %{y:+.1f}%<br>'
                f'Fase: {fase}<extra></extra>'
            ),
        ))

    fig.add_hline(y=0, line=dict(color='#30363d', width=1, dash='dot'))
    fig.add_vline(x=65, line=dict(color='#30363d', width=1, dash='dot'))

    fig.update_layout(
    paper_bgcolor='#0d1117',
    plot_bgcolor='#161b22',
    xaxis=dict(
        title=dict(
            text="X-Axis Label",
            font=dict(family="Arial", size=14, color="white")
        ),
        tickfont=dict(color='gray')
    ),
    yaxis=dict(
        title=dict(
            text="Y-Axis Label",
            font=dict(family="Arial", size=14, color="white")
        )
    ),
)
    return fig

def plot_candlestick_vsa(ticker: str, dager: int) -> go.Figure:
    """
    Candlestick-chart med volum og VSA-markering.
    Fargede søyler for absorpsjon, thrust og shakeout.
    """
    df = hent_enkelt(ticker, dager)
    if df.empty:
        return go.Figure()

    vol_sma = df['Volume'].rolling(20).mean()
    vol_ratio = df['Volume'] / vol_sma
    chg = df['Close'].pct_change() * 100
    close_pct = (df['Close'] - df['Low']) / (df['High'] - df['Low'] + 1e-9)

    absorpsjon_mask = (vol_ratio >= 1.8) & (chg.abs() <= 0.8)
    thrust_mask     = (vol_ratio >= 1.5) & (chg >= 0.8) & (close_pct >= 0.65)
    shakeout_mask   = (vol_ratio >= 2.5) & (chg < -0.5) & (close_pct >= 0.45)

    vol_farger = []
    for i in df.index:
        if absorpsjon_mask.get(i, False): vol_farger.append('#3fb95099')
        elif thrust_mask.get(i, False):   vol_farger.append('#388bfd99')
        elif shakeout_mask.get(i, False): vol_farger.append('#d2992299')
        elif df.loc[i,'Close'] >= df.loc[i,'Open']: vol_farger.append('#3fb95044')
        else:                              vol_farger.append('#f8514944')

    obv = ta.obv(df['Close'], df['Volume'])

    fig = make_subplots(
        rows=3, cols=1,
        shared_xaxes=True,
        row_heights=[0.60, 0.22, 0.18],
        vertical_spacing=0.02,
    )

    # Panel 1: Candlestick
    fig.add_trace(go.Candlestick(
        x=df.index, open=df['Open'], high=df['High'],
        low=df['Low'], close=df['Close'],
        increasing_line_color='#3fb950', decreasing_line_color='#f85149',
        increasing_fillcolor='#3fb950', decreasing_fillcolor='#f85149',
        name='Kurs', showlegend=False,
    ), row=1, col=1)

    # Absorpsjon-markering på chart
    for i in df.index:
        if absorpsjon_mask.get(i, False):
            fig.add_annotation(
                x=i, y=df.loc[i,'Low'] * 0.993, text='▲',
                showarrow=False, font=dict(color='#3fb950', size=10),
                row=1, col=1,
            )
        elif shakeout_mask.get(i, False):
            fig.add_annotation(
                x=i, y=df.loc[i,'High'] * 1.005, text='◆',
                showarrow=False, font=dict(color='#d29922', size=9),
                row=1, col=1,
            )

    # Panel 2: Volum
    fig.add_trace(go.Bar(
    x=df.index, 
    y=df['Volume'],
    marker_color='#3fb950', # Standard hex
    opacity=0.3             # Sets transparency for the whole trace
))

    # Panel 3: OBV
    fig.add_trace(go.Scatter(
        x=df.index, y=obv,
        line=dict(color='#a371f7', width=1.5),
        fill='tozeroy', fillcolor='rgba(163,113,247,0.08)',
        name='OBV', showlegend=False,
    ), row=3, col=1)

    # Legende manuelt
    for navn, farge, symbol in [
        ('Absorpsjon', '#3fb950', '▲'),
        ('Vol-thrust', '#388bfd', '●'),
        ('Shakeout',   '#d29922', '◆'),
    ]:
        fig.add_trace(go.Scatter(
            x=[None], y=[None], mode='markers',
            marker=dict(color=farge, size=8, symbol='circle'),
            name=f'{symbol} {navn}', showlegend=True,
        ), row=1, col=1)

    panel_stil = dict(
        gridcolor='#21262d', zeroline=False,
        tickfont=dict(color='#8b949e', size=10),
    )

    fig.update_layout(
        paper_bgcolor='#0d1117', plot_bgcolor='#161b22',
        height=600,
        margin=dict(l=10, r=10, t=40, b=10),
        title=dict(text=f'<b>{ticker}</b> — Volume Spread Analysis',
                   font=dict(color='#c9d1d9', size=14), x=0.01),
        xaxis=dict(**panel_stil, rangeslider_visible=False),
        xaxis2=dict(**panel_stil),
        xaxis3=dict(**panel_stil),
        yaxis=dict(**panel_stil, title=dict(text='Kurs', font=dict(color='#8b949e', size=10))),
        yaxis2=dict(**panel_stil, title=dict(text='Volum', font=dict(color='#8b949e', size=10))),
        yaxis3=dict(**panel_stil, title=dict(text='OBV', font=dict(color='#8b949e', size=10))),
        legend=dict(
            orientation='h', x=0, y=1.06,
            bgcolor='rgba(0,0,0,0)', font=dict(color='#8b949e', size=11),
        ),
        hovermode='x unified',
    )
    return fig

def plot_rs_tidslinje(tickers: list, sektor_etf: str, dager: int) -> go.Figure:
    """Relativ styrke-tidslinje: alle top-aksjer mot sektor-ETF."""
    topp_5 = tickers[:5]
    alle   = list(set(topp_5 + [sektor_etf, BENCHMARK]))
    raw    = hent_data(tuple(alle), dager + 10)

    if 'Close' not in raw.columns.get_level_values(0):
        return go.Figure()

    benchmark = raw['Close'][BENCHMARK].dropna()
    farger = ['#3fb950', '#388bfd', '#a371f7', '#d29922', '#f85149', '#8b949e']

    fig = go.Figure()

    for i, t in enumerate(topp_5):
        if t not in raw['Close'].columns:
            continue
        serie = raw['Close'][t].dropna().tail(dager)
        rs_ts = ((serie / serie.iloc[0]) - (benchmark.tail(dager) / benchmark.tail(dager).iloc[0])) * 100
        fig.add_trace(go.Scatter(
            x=rs_ts.index, y=rs_ts.round(2),
            name=t,
            line=dict(color=farger[i % len(farger)], width=1.8),
            hovertemplate=f'<b>{t}</b>: %{{y:+.1f}}%<extra></extra>',
        ))

    # Sektor-ETF som referanse
    sektor_s = raw['Close'][sektor_etf].dropna().tail(dager)
    rs_sektor = ((sektor_s / sektor_s.iloc[0]) - (benchmark.tail(dager) / benchmark.tail(dager).iloc[0])) * 100
    fig.add_trace(go.Scatter(
        x=rs_sektor.index, y=rs_sektor.round(2),
        name=f'{sektor_etf} (sektor)',
        line=dict(color='#30363d', width=2, dash='dot'),
        hovertemplate=f'<b>{sektor_etf}</b>: %{{y:+.1f}}%<extra></extra>',
    ))

    fig.add_hline(y=0, line=dict(color='#30363d', width=1))

    fig.update_layout(
        paper_bgcolor='#0d1117', plot_bgcolor='#161b22',
        height=380,
        margin=dict(l=10, r=10, t=30, b=10),
        xaxis=dict(gridcolor='#21262d', tickfont=dict(color='#8b949e')),
        yaxis=dict(gridcolor='#21262d', tickfont=dict(color='#8b949e'),
                   title=dict(text='RS vs SPY (%)', font=dict(color='#8b949e'))),
        legend=dict(bgcolor='#161b22', bordercolor='#30363d', borderwidth=1,
                    font=dict(color='#8b949e', size=11)),
        hovermode='x unified',
        font=dict(color='#c9d1d9'),
    )
    return fig

# =============================================================================
# TABELL-FORMATERING
# =============================================================================

def formater_tabell(df: pd.DataFrame) -> pd.DataFrame:
    """Formaterer kolonner for visning i st.dataframe."""
    vis = df.copy()

    def farge_score(v):
        if v >= 70:   return '🟢 ' + str(v)
        elif v >= 50: return '🟡 ' + str(v)
        else:         return '🔴 ' + str(v)

    def farge_rs(v):
        return f'+{v:.1f}%' if v >= 0 else f'{v:.1f}%'

    def farge_fase(f):
        ikoner = {
            'spring': '🌱 Spring',
            'markup': '📈 Mark-up',
            'akkumulering_B': '🔵 Akk. B',
            'akkumulering_A': '⚪ Akk. A',
            'distribusjon': '⚠️ Dist.',
            'markdown': '📉 Mark-down',
        }
        return ikoner.get(f, f)

    vis['Smart Money'] = vis['Smart Money'].apply(farge_score)
    vis['RS vs SPY']   = vis['RS vs SPY'].apply(farge_rs)
    vis['RS vs Sektor']= vis['RS vs Sektor'].apply(farge_rs)
    vis['Wyckoff Fase']= vis['Wyckoff Fase'].apply(farge_fase)
    vis['OBV Opp']     = vis['OBV Opp'].apply(lambda x: '✓' if x else '—')
    vis['1d %']        = vis['1d %'].apply(lambda v: f'+{v:.2f}%' if v >= 0 else f'{v:.2f}%')
    vis['Kurs']        = vis['Kurs'].apply(lambda v: f'${v:,.2f}')

    return vis[[
        'Ticker','Kurs','1d %','RS vs SPY','RS vs Sektor',
        'Absorpsjon','Vol-thrust','VSA Score',
        'Wyckoff Fase','CM Score','OBV Opp','Smart Money'
    ]]

# =============================================================================
# STREAMLIT APP — LAYOUT
# =============================================================================

def main():

    # ── SIDEBAR ──────────────────────────────────────────────────────────────
    with st.sidebar:
        st.markdown("## 🐋 Smart Money")
        st.markdown("---")

        st.markdown("### Tidsperiode")
        periode_navn = st.selectbox(
            "Analysehorisont",
            list(PERIODE_VALG.keys()),
            index=1,
            label_visibility='collapsed',
        )
        periode_dager = PERIODE_VALG[periode_navn]

        st.markdown("### Sektor")
        sektor_valg = st.selectbox(
            "Velg sektor for drill-down",
            list(SEKTORER.keys()),
            format_func=lambda x: f"{x} — {SEKTORER[x][0]}",
            label_visibility='collapsed',
        )

        st.markdown("### Drill-down aksje")
        _, tickers_sektor = SEKTORER[sektor_valg]
        chart_ticker = st.selectbox(
            "Vis VSA-chart for",
            tickers_sektor[:20],
            label_visibility='collapsed',
        )

        st.markdown("---")
        kjør_scan = st.button("⟳  Oppdater analyse", use_container_width=True)
        st.markdown("""
        <div style='font-size:11px;color:#6e7681;margin-top:12px;line-height:1.6;'>
        Data: Yahoo Finance<br>
        Cache: 30 min<br>
        Wyckoff + VSA analyse<br>
        Ikke finansiell rådgivning
        </div>
        """, unsafe_allow_html=True)

    # ── HEADER ───────────────────────────────────────────────────────────────
    col_t, col_d = st.columns([3, 1])
    with col_t:
        st.markdown(f"# Smart Money Dashboard")
        st.markdown(f"<span style='color:#8b949e;font-size:13px;'>"
                    f"Sektor: <b style='color:#c9d1d9'>{sektor_valg} — {SEKTORER[sektor_valg][0]}</b>"
                    f" &nbsp;|&nbsp; Periode: <b style='color:#c9d1d9'>{periode_navn}</b>"
                    f" &nbsp;|&nbsp; {datetime.today().strftime('%d.%m.%Y %H:%M')}"
                    f"</span>", unsafe_allow_html=True)
    with col_d:
        st.markdown("<div style='height:32px'></div>", unsafe_allow_html=True)
        if st.button("⟳ Tøm cache", use_container_width=True):
            st.cache_data.clear()
            st.rerun()

    st.markdown("---")

    # ── LAST DATA ─────────────────────────────────────────────────────────────
    with st.spinner("Henter sektor-data fra Yahoo Finance..."):
        sektor_df = sektor_screening(periode_dager)

    with st.spinner(f"Skanner {sektor_valg}-komponenter..."):
        scan_df = drill_down_scanner(sektor_valg, periode_dager)

    # ── METRIC-KORT ───────────────────────────────────────────────────────────
    if not scan_df.empty:
        topp = scan_df.iloc[0]
        ant_grønn = int((scan_df['Smart Money'] >= 65).sum())
        ant_spring = int((scan_df['Wyckoff Fase'] == 'spring').sum())

        m1, m2, m3, m4, m5 = st.columns(5)
        m1.metric("Topp-kandidat",  topp['Ticker'],
                  f"SMS: {topp['Smart Money']:.0f}/100")
        m2.metric("Beste fase",     topp['Wyckoff Fase'].replace('_',' ').title(),
                  f"RS: {topp['RS vs SPY']:+.1f}%")
        m3.metric("Spring/LPS",     f"{ant_spring} aksjer",
                  "Beste entry-soner")
        m4.metric("Høy SMS (≥65)",  f"{ant_grønn}/{len(scan_df)}",
                  "Institusjonell interesse")
        m5.metric("Sektor RS 3M",
                  f"{sektor_df[sektor_df['ETF']==sektor_valg]['RS 3M'].values[0]:+.1f}%"
                  if not sektor_df[sektor_df['ETF']==sektor_valg].empty else "—",
                  "vs SPY")

    st.markdown("---")

    # ── FANER ────────────────────────────────────────────────────────────────
    tab1, tab2, tab3, tab4 = st.tabs([
        "🗺  Sektor-varmekart",
        "🔬  Drill-down scanner",
        "📊  VSA-chart",
        "📈  RS-tidslinje",
    ])

    # ── TAB 1: SEKTOR-VARMEKART ───────────────────────────────────────────────
    with tab1:
        st.markdown("### Relativ styrke vs SPY — alle 11 sektorer")
        st.markdown(
            "<span style='color:#8b949e;font-size:12px;'>"
            "Grønt = kapital strømmer inn · Rødt = kapital strømmer ut · "
            "Klikk en celle for detaljer</span>",
            unsafe_allow_html=True,
        )
        st.plotly_chart(plot_sektor_heatmap(sektor_df),
                        use_container_width=True, config={'displayModeBar': False})

        st.markdown("##### Sektor-rangering")
        vis_sektor = sektor_df.copy()
        for kol in ['RS 1M','RS 3M','RS 6M','Score']:
            vis_sektor[kol] = vis_sektor[kol].apply(
                lambda v: f'+{v:.1f}%' if v >= 0 else f'{v:.1f}%'
            )
        st.dataframe(vis_sektor, use_container_width=True, hide_index=True)

    # ── TAB 2: DRILL-DOWN ────────────────────────────────────────────────────
    with tab2:
        if scan_df.empty:
            st.warning("Ingen data tilgjengelig. Prøv å tømme cache.")
        else:
            col_a, col_b = st.columns([3, 2], gap='large')

            with col_a:
                st.markdown(f"### Boble-diagram — {sektor_valg}")
                st.markdown(
                    "<span style='color:#8b949e;font-size:12px;'>"
                    "X = Smart Money Score · Y = RS vs SPY · "
                    "Størrelse = absorpsjons-dager · Farge = Wyckoff-fase</span>",
                    unsafe_allow_html=True,
                )
                st.plotly_chart(plot_rs_boble(scan_df),
                                use_container_width=True,
                                config={'displayModeBar': False})

            with col_b:
                st.markdown("### Topp 5 kandidater")
                for _, row in scan_df.head(5).iterrows():
                    farge = WYCKOFF_FASE_FARGE.get(row['Wyckoff Fase'], '#6e7681')
                    sms   = row['Smart Money']
                    bar_w = int(sms)
                    st.markdown(f"""
                    <div style='background:#161b22;border:1px solid #30363d;border-radius:8px;
                                padding:10px 14px;margin-bottom:8px;'>
                      <div style='display:flex;justify-content:space-between;align-items:center;'>
                        <span style='font-size:15px;font-weight:500;color:#e6edf3;'>{row['Ticker']}</span>
                        <span style='font-size:11px;background:{farge}22;color:{farge};
                                     border:1px solid {farge}44;border-radius:4px;padding:2px 8px;'>
                          {row['Wyckoff Fase'].replace('_',' ').title()}
                        </span>
                      </div>
                      <div style='margin:6px 0 4px;background:#21262d;border-radius:3px;height:5px;'>
                        <div style='width:{bar_w}%;background:{farge};border-radius:3px;height:5px;'></div>
                      </div>
                      <div style='display:flex;gap:14px;font-size:12px;color:#8b949e;'>
                        <span>SMS: <b style='color:#c9d1d9;'>{sms:.0f}</b></span>
                        <span>RS: <b style='color:{"#3fb950" if row["RS vs SPY"]>=0 else "#f85149"};'>
                          {row["RS vs SPY"]:+.1f}%</b></span>
                        <span>Abs: <b style='color:#c9d1d9;'>{row["Absorpsjon"]}</b></span>
                        <span>OBV: <b style='color:#c9d1d9;'>{"↑" if row["OBV Opp"] else "↓"}</b></span>
                      </div>
                    </div>
                    """, unsafe_allow_html=True)

            st.markdown("### Smart Money Scanner — full tabell")
            st.markdown(
                "<span style='color:#8b949e;font-size:12px;'>"
                "Klikk kolonneoverskrift for å sortere · "
                "🟢 SMS ≥ 70 · 🟡 50–70 · 🔴 under 50</span>",
                unsafe_allow_html=True,
            )
            st.dataframe(
                formater_tabell(scan_df),
                use_container_width=True,
                height=480,
            )

            csv = scan_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                "⬇  Last ned CSV",
                data=csv,
                file_name=f"smart_money_{sektor_valg}_{datetime.today().strftime('%Y%m%d')}.csv",
                mime='text/csv',
            )

    # ── TAB 3: VSA-CHART ─────────────────────────────────────────────────────
    with tab3:
        st.markdown(f"### {chart_ticker} — Volume Spread Analysis")
        st.markdown(
            "<span style='color:#8b949e;font-size:12px;'>"
            "▲ Absorpsjon (grønn) · ◆ Shakeout (gul) · OBV i bunn-panel</span>",
            unsafe_allow_html=True,
        )
        with st.spinner(f"Henter {chart_ticker}..."):
            fig_vsa = plot_candlestick_vsa(chart_ticker, min(periode_dager, 90))
        st.plotly_chart(fig_vsa, use_container_width=True,
                        config={'displayModeBar': True, 'scrollZoom': True})

        # Mini-stats
        if not scan_df.empty and chart_ticker in scan_df['Ticker'].values:
            rad = scan_df[scan_df['Ticker'] == chart_ticker].iloc[0]
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Smart Money Score", f"{rad['Smart Money']:.0f}/100")
            c2.metric("Wyckoff Fase",      rad['Wyckoff Fase'].replace('_',' ').title())
            c3.metric("Absorpsjonsdager",  rad['Absorpsjon'])
            c4.metric("OBV-trend",         "Stigende ↑" if rad['OBV Opp'] else "Fallende ↓")

    # ── TAB 4: RS-TIDSLINJE ───────────────────────────────────────────────────
    with tab4:
        st.markdown(f"### Relativ styrke over tid — topp 5 i {sektor_valg}")
        st.markdown(
            "<span style='color:#8b949e;font-size:12px;'>"
            "Kumulativ RS vs SPY · Stiplet = sektor-ETF som referanse</span>",
            unsafe_allow_html=True,
        )
        topp5_tickers = scan_df.head(5)['Ticker'].tolist() if not scan_df.empty else []
        if topp5_tickers:
            with st.spinner("Bygger RS-tidslinje..."):
                fig_rs = plot_rs_tidslinje(topp5_tickers, sektor_valg, periode_dager)
            st.plotly_chart(fig_rs, use_container_width=True,
                            config={'displayModeBar': False})
        else:
            st.info("Kjør scanner for å se RS-tidslinje.")

# =============================================================================
# ENTRY POINT
# =============================================================================

if __name__ == '__main__':
    main()