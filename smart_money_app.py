# =============================================================================
# SMART MONEY DASHBOARD — Komplett enkeltfil for Streamlit Cloud
# Inkluderer: Guide/Forside + Dashboard i én fil via session_state-navigasjon
#
# KJØRING:  streamlit run smart_money_app.py
# DEPLOY:   Pek Streamlit Cloud til denne filen (main file path)
# =============================================================================

import streamlit as st
import yfinance as yf
import pandas as pd
import pandas_ta as ta
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from scipy.signal import argrelextrema
from datetime import datetime, timedelta
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

# =============================================================================
# GLOBALT TEMA
# =============================================================================

st.markdown("""
<style>
    .stApp { background-color: #0d1117; color: #c9d1d9; }
    .stApp header { background-color: #0d1117; }
    section[data-testid="stSidebar"] {
        background-color: #161b22;
        border-right: 1px solid #30363d;
    }
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] .stMarkdown p { color: #8b949e; font-size: 13px; }
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3 { color: #c9d1d9; }
    [data-testid="metric-container"] {
        background: #161b22;
        border: 1px solid #30363d;
        border-radius: 8px;
        padding: 14px 16px;
    }
    [data-testid="metric-container"] label { color: #8b949e !important; font-size: 12px !important; }
    [data-testid="metric-container"] [data-testid="stMetricValue"] {
        color: #c9d1d9 !important; font-size: 22px !important; font-weight: 500 !important;
    }
    .dataframe { background-color: #161b22 !important; color: #c9d1d9 !important; }
    .dataframe th { background-color: #21262d !important; color: #8b949e !important; font-size: 12px !important; }
    .dataframe td { font-size: 13px !important; }
    .stTabs [data-baseweb="tab-list"] { background: #161b22; border-radius: 8px; padding: 4px; }
    .stTabs [data-baseweb="tab"] { color: #8b949e; border-radius: 6px; }
    .stTabs [aria-selected="true"] { background: #21262d !important; color: #c9d1d9 !important; }
    h1 { color: #e6edf3 !important; font-size: 24px !important; font-weight: 500 !important; }
    h2 { color: #c9d1d9 !important; font-size: 18px !important; font-weight: 500 !important; }
    h3 { color: #8b949e !important; font-size: 14px !important; font-weight: 500 !important; }
    hr { border-color: #30363d; }
    .concept-card {
        background: #161b22; border: 1px solid #30363d; border-radius: 10px;
        padding: 16px 18px; margin-bottom: 10px;
    }
    .concept-card h4 { color: #e6edf3 !important; font-size: 14px !important;
        margin: 0 0 5px 0; font-weight: 500 !important; }
    .concept-card p { color: #8b949e; font-size: 13px; line-height: 1.65; margin: 0; }
    .callout { background: #161b22; border-left: 3px solid #388bfd; border-radius: 0 8px 8px 0;
        padding: 11px 15px; margin: 10px 0; font-size: 13px; color: #8b949e; line-height: 1.65; }
    .callout.green  { border-left-color: #3fb950; }
    .callout.yellow { border-left-color: #d29922; }
    .callout.red    { border-left-color: #f85149; }
    .nav-btn { cursor: pointer; }
</style>
""", unsafe_allow_html=True)

# =============================================================================
# KONSTANTER
# =============================================================================

SEKTORER = {
    'XLK':  ('Teknologi',               ['NVDA','MSFT','AAPL','AVGO','AMD','CRM','ORCL','QCOM','TXN','INTC','AMAT','MU','LRCX','KLAC','ADI','MRVL','PANW','CRWD','SNPS','CDNS']),
    'XLF':  ('Finans',                  ['BRK-B','JPM','V','MA','BAC','WFC','GS','MS','BLK','SPGI','AXP','CB','CME','ICE','PGR','TRV','MET','PRU','AFL','AIG']),
    'XLE':  ('Energi',                  ['XOM','CVX','COP','EOG','SLB','MPC','PXD','VLO','PSX','OXY','HES','DVN','BKR','FANG','HAL','APA','EQT','MRO','CTRA','OVV']),
    'XLV':  ('Helse',                   ['LLY','UNH','JNJ','ABBV','MRK','TMO','ABT','DHR','PFE','AMGN','MDT','ISRG','GILD','CVS','CI','HCA','ZTS','ELV','SYK','BSX']),
    'XLI':  ('Industri',                ['GE','RTX','HON','UNP','BA','DE','ETN','LMT','NOC','GD','MMM','ITW','EMR','CMI','PH','FDX','UPS','CSX','NSC','WM']),
    'XLY':  ('Forbruksdiskresjonær',    ['AMZN','TSLA','HD','MCD','NKE','SBUX','LOW','BKNG','TJX','CMG','F','GM','ABNB','DHI','LEN','NVR','PHM','MAR','HLT','YUM']),
    'XLP':  ('Forbruksstabeltre',       ['PG','COST','KO','PEP','WMT','PM','MO','MDLZ','CL','EL','STZ','KHC','GIS','HSY','K','SJM','MKC','CAG','CPB','HRL']),
    'XLU':  ('Utilities',               ['NEE','SO','DUK','AEP','SRE','EXC','XEL','PEG','ED','AWK','PPL','ES','FE','NI','CMS','CNP','LNT','OGE','PNW','WEC']),
    'XLB':  ('Materialer',              ['LIN','APD','SHW','FCX','NEM','NUE','VMC','MLM','ALB','CE','IFF','PPG','IP','CF','MOS','FMC','SEE','PKG','WRK','BALL']),
    'XLRE': ('Eiendom',                 ['PLD','AMT','CCI','EQIX','SPG','O','PSA','WELL','DLR','AVB','EQR','SBA','SBAC','WPC','EXR','HST','ARE','BXP','UDR','NNN']),
    'XLC':  ('Kommunikasjonstjenester', ['META','GOOGL','GOOG','NFLX','T','VZ','DIS','CMCSA','TMUS','CHTR','EA','WBD','PARA','OMC','IPG','NWSA','FOX','LYV','ZM','MTCH']),
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

DARK    = '#0d1117'
SURFACE = '#161b22'
GRID    = '#21262d'
MUTED   = '#8b949e'
TEXT    = '#c9d1d9'

# =============================================================================
# SESSION STATE — navigasjon + widget-tracking
# =============================================================================

if 'side' not in st.session_state:
    st.session_state.side = 'guide'

# Spor forrige sektor for å nullstille chart-valg ved sektorbytte
if '_prev_sektor' not in st.session_state:
    st.session_state._prev_sektor = 'XLK'

# =============================================================================
# SIDEBAR
# =============================================================================

with st.sidebar:
    st.markdown("## 🐋 Smart Money")
    st.markdown("---")

    # Navigasjon
    if st.button("📖  Guide & Metodikk",
                 use_container_width=True,
                 type="secondary" if st.session_state.side == 'dashboard' else "primary"):
        st.session_state.side = 'guide'
        st.rerun()

    if st.button("📊  Dashboard",
                 use_container_width=True,
                 type="primary" if st.session_state.side == 'dashboard' else "secondary"):
        st.session_state.side = 'dashboard'
        st.rerun()

    st.markdown("---")

    if st.session_state.side == 'dashboard':
        st.markdown("### Tidsperiode")
        st.selectbox(
            "Analysehorisont", list(PERIODE_VALG.keys()), index=1,
            label_visibility='collapsed',
            key='sb_periode',
        )

        st.markdown("### Sektor")
        st.selectbox(
            "Velg sektor", list(SEKTORER.keys()),
            format_func=lambda x: f"{x} — {SEKTORER[x][0]}",
            label_visibility='collapsed',
            key='sb_sektor',
        )

        # Nullstill chart-valg når sektoren endres
        aktuell_sektor = st.session_state.get('sb_sektor', 'XLK')
        if aktuell_sektor != st.session_state._prev_sektor:
            st.session_state._prev_sektor = aktuell_sektor
            if 'tab3_chart' in st.session_state:
                del st.session_state['tab3_chart']

        st.markdown("---")
        if st.button("⟳  Oppdater analyse", use_container_width=True):
            st.cache_data.clear()
            st.rerun()

    st.markdown("""
    <div style='font-size:11px;color:#6e7681;margin-top:12px;line-height:1.7;'>
    Data: Yahoo Finance · Cache: 30 min<br>
    Ikke finansiell rådgivning
    </div>
    """, unsafe_allow_html=True)

# =============================================================================
# CACHING
# =============================================================================

@st.cache_data(ttl=1800, show_spinner=False)
def hent_data(tickers: tuple, dager: int) -> pd.DataFrame:
    start = (datetime.today() - timedelta(days=dager + 10)).strftime('%Y-%m-%d')
    raw = yf.download(list(tickers), start=start, progress=False, auto_adjust=True)
    if isinstance(raw.columns, pd.MultiIndex):
        return raw
    raw.columns = pd.MultiIndex.from_product([raw.columns, tickers])
    return raw


def hent_enkelt(ticker: str, dager: int) -> pd.DataFrame:
    """Henter OHLCV for én ticker. Ingen cache — sikrer at ticker-bytte alltid gir riktig data."""
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

def beregn_relativ_styrke(closes, benchmark, dager):
    s = closes.dropna().tail(dager)
    b = benchmark.dropna().tail(dager)
    if len(s) < 2 or len(b) < 2:
        return 0.0
    return round((s.iloc[-1]/s.iloc[0] - 1 - (b.iloc[-1]/b.iloc[0] - 1)) * 100, 2)

def vpa_analyse(df):
    df = df.copy().dropna()
    vol_sma   = df['Volume'].rolling(20).mean()
    vol_ratio = df['Volume'] / vol_sma
    chg       = df['Close'].pct_change() * 100
    close_pct = (df['Close'] - df['Low']) / (df['High'] - df['Low'] + 1e-9)

    absorpsjon = int(((vol_ratio >= 1.8) & (chg.abs() <= 0.8)).sum())
    thrust     = int(((vol_ratio >= 1.5) & (chg >= 0.8) & (close_pct >= 0.65)).sum())
    shakeout   = int(((vol_ratio >= 2.5) & (chg < -0.5) & (close_pct >= 0.45)).sum())

    obv       = ta.obv(df['Close'], df['Volume'])
    obv_slope = (obv.iloc[-1] - obv.iloc[-min(20, len(obv))]) if len(obv) > 5 else 0
    score     = min(100, absorpsjon*8 + thrust*10 + shakeout*6 + (15 if obv_slope > 0 else 0))

    return {'absorpsjon': absorpsjon, 'sos_thrust': thrust, 'shakeout': shakeout,
            'obv_stigende': obv_slope > 0, 'vsa_score': round(score, 1)}

def wyckoff_fase_enkel(df, rs):
    if len(df) < 30:
        return 'ukjent', 0.0
    closes = df['Close'].values
    highs  = df['High'].values
    lows   = df['Low'].values
    vol    = df['Volume'].values

    hi_idx  = argrelextrema(highs, np.greater, order=8)[0]
    lo_idx  = argrelextrema(lows,  np.less,    order=8)[0]
    resist  = float(np.median(highs[hi_idx])) if len(hi_idx) else highs.max()
    support = float(np.median(lows[lo_idx]))  if len(lo_idx) else lows.min()
    kurs    = closes[-1]
    range_h = resist - support

    obv       = ta.obv(df['Close'], df['Volume'])
    obv_trend = obv.iloc[-1] > obv.iloc[-min(20, len(obv))]
    vpa       = vpa_analyse(df)

    spring = False
    for i in range(-10, 0):
        try:
            if df['Low'].iloc[i] < support * 0.99 and df['Close'].iloc[i] > support:
                spring = True; break
        except IndexError:
            break

    score = 50
    if obv_trend:              score += 12
    if spring:                 score += 18
    if rs > 2:                 score += 10
    if vpa['absorpsjon'] >= 2: score += 10
    if vpa['sos_thrust'] >= 1: score += 8
    if not obv_trend:          score -= 15
    if rs < -3:                score -= 10

    markup = kurs > resist * 1.01 and vpa['sos_thrust'] >= 1
    dist   = kurs > support + range_h * 0.65 and not obv_trend
    mdown  = kurs < support * 0.97 and not obv_trend and rs < -3

    if mdown:  return 'markdown',       max(5,  min(score, 35))
    if dist:   return 'distribusjon',   max(20, min(score, 50))
    if markup: return 'markup',         max(65, min(score, 92))
    if spring: return 'spring',         max(72, min(score, 98))
    if vpa['absorpsjon'] >= 2 or vpa['obv_stigende']:
               return 'akkumulering_B', max(55, min(score, 82))
    return     'akkumulering_A',        max(35, min(score, 68))

def beregn_smart_money_score(rs, vsa_score, cm_score, obv_opp):
    rs_n  = min(100, max(0, (rs + 15) / 30 * 100)) * 0.25
    vsa_n = min(100, vsa_score) * 0.30
    cm_n  = min(100, cm_score)  * 0.30
    obv_n = (100 if obv_opp else 0) * 0.15
    return round(rs_n + vsa_n + cm_n + obv_n, 1)

@st.cache_data(ttl=1800, show_spinner=False)
def sektor_screening(periode_dager):
    alle = list(SEKTORER.keys()) + [BENCHMARK]
    raw  = hent_data(tuple(alle), periode_dager)
    bench = raw['Close'][BENCHMARK].dropna()
    rader = []
    for etf, (navn, _) in SEKTORER.items():
        if etf not in raw['Close'].columns:
            continue
        close = raw['Close'][etf].dropna()
        rs_1m = beregn_relativ_styrke(close, bench, 21)
        rs_3m = beregn_relativ_styrke(close, bench, 63)
        rs_6m = beregn_relativ_styrke(close, bench, 126)
        rader.append({'ETF': etf, 'Sektor': navn,
                      'RS 1M': rs_1m, 'RS 3M': rs_3m, 'RS 6M': rs_6m,
                      'Score': round(rs_1m*0.3 + rs_3m*0.45 + rs_6m*0.25, 2)})
    return pd.DataFrame(rader).sort_values('Score', ascending=False).reset_index(drop=True)

@st.cache_data(ttl=1800, show_spinner=False)
def drill_down_scanner(sektor_etf, periode_dager):
    _, tickers = SEKTORER[sektor_etf]
    tickers_20 = tickers[:20]
    alle = list(set(tickers_20 + [sektor_etf, BENCHMARK]))
    raw  = hent_data(tuple(alle), max(periode_dager, 120) + 20)
    if 'Close' not in raw.columns.get_level_values(0):
        return pd.DataFrame()

    bench_s  = raw['Close'][BENCHMARK].dropna()
    sektor_s = raw['Close'][sektor_etf].dropna()
    rader = []

    for ticker in tickers_20:
        if ticker not in raw['Close'].columns:
            continue
        close = raw['Close'][ticker].dropna()
        if len(close) < 30:
            continue
        try:
            df_t = pd.DataFrame({
                'Open':   raw['Open'][ticker],
                'High':   raw['High'][ticker],
                'Low':    raw['Low'][ticker],
                'Close':  raw['Close'][ticker],
                'Volume': raw['Volume'][ticker],
            }).dropna().tail(max(periode_dager, 120))
        except KeyError:
            continue

        rs_spy    = beregn_relativ_styrke(close, bench_s,  periode_dager)
        rs_sek    = beregn_relativ_styrke(close, sektor_s, periode_dager)
        vpa       = vpa_analyse(df_t)
        fase, cm  = wyckoff_fase_enkel(df_t, rs_spy)
        sms       = beregn_smart_money_score(rs_spy, vpa['vsa_score'], cm, vpa['obv_stigende'])
        kurs      = float(close.iloc[-1])
        chg_1d    = float((close.iloc[-1]/close.iloc[-2] - 1)*100) if len(close) > 1 else 0

        rader.append({
            'Ticker': ticker, 'Kurs': round(kurs, 2), '1d %': round(chg_1d, 2),
            'RS vs SPY': rs_spy, 'RS vs Sektor': rs_sek,
            'Absorpsjon': vpa['absorpsjon'], 'Vol-thrust': vpa['sos_thrust'],
            'VSA Score': vpa['vsa_score'], 'Wyckoff Fase': fase,
            'CM Score': round(cm, 1), 'OBV Opp': vpa['obv_stigende'], 'Smart Money': sms,
        })

    df = pd.DataFrame(rader).sort_values('Smart Money', ascending=False).reset_index(drop=True)
    df.index += 1
    return df

# =============================================================================
# PLOT-HJELPERE
# =============================================================================

def _base(fig, h=340):
    fig.update_layout(
        paper_bgcolor=DARK, plot_bgcolor=SURFACE, height=h,
        margin=dict(l=10, r=10, t=20, b=10),
        font=dict(color=TEXT, size=11), hovermode='x unified',
        legend=dict(bgcolor='rgba(0,0,0,0)', font=dict(color=MUTED, size=11)),
        xaxis=dict(gridcolor=GRID, zeroline=False, tickfont=dict(color=MUTED, size=10)),
        yaxis=dict(gridcolor=GRID, zeroline=False, tickfont=dict(color=MUTED, size=10)),
    )
    return fig

# =============================================================================
# PLOT-FUNKSJONER — DASHBOARD
# =============================================================================

def plot_sektor_heatmap(df):
    z    = df[['RS 1M','RS 3M','RS 6M']].values
    tekst = [[f"{v:+.1f}%" for v in row] for row in z]
    fig  = go.Figure(go.Heatmap(
        z=z, x=['1 måned','3 måneder','6 måneder'],
        y=df['ETF'] + ' — ' + df['Sektor'],
        text=tekst, texttemplate='%{text}',
        textfont={'size': 12, 'color': 'white'},
        colorscale=[[0,'#7f1d1d'],[0.25,'#b91c1c'],[0.4,'#c2410c'],
                    [0.5,'#374151'],[0.6,'#166534'],[0.75,'#15803d'],[1,'#14532d']],
        zmid=0, showscale=True,
        colorbar=dict(title=dict(text='RS vs SPY (%)', font=dict(color=MUTED)),
                      tickfont=dict(color=MUTED)),
    ))
    fig.update_layout(
        paper_bgcolor=DARK, plot_bgcolor=DARK, height=420,
        margin=dict(l=10, r=20, t=20, b=10),
        xaxis=dict(side='top', tickfont=dict(color=MUTED, size=12)),
        yaxis=dict(tickfont=dict(color=TEXT, size=11), autorange='reversed'),
        font=dict(family='monospace'),
    )
    return fig

def plot_rs_boble(df):
    fase_hex = {'spring':'#3fb950','markup':'#388bfd','akkumulering_B':'#a371f7',
                'akkumulering_A':'#6e7681','distribusjon':'#d29922','markdown':'#f85149'}
    df = df.copy()
    df['Farge']    = df['Wyckoff Fase'].map(fase_hex).fillna('#6e7681')
    df['Størrelse'] = (df['Absorpsjon'] * 12 + 40).clip(40, 200)
    fig = go.Figure()
    for fase, farge in fase_hex.items():
        sub = df[df['Wyckoff Fase'] == fase]
        if sub.empty: continue
        fig.add_trace(go.Scatter(
            x=sub['Smart Money'], y=sub['RS vs SPY'],
            mode='markers+text', name=fase.replace('_',' ').title(),
            text=sub['Ticker'], textposition='middle center',
            textfont=dict(size=10, color='white'),
            marker=dict(size=sub['Størrelse']/5, color=farge, opacity=0.85,
                        line=dict(width=1, color='rgba(255,255,255,0.3)')),
            hovertemplate=f'<b>%{{text}}</b><br>SMS: %{{x:.1f}}<br>RS: %{{y:+.1f}}%<extra>{fase}</extra>',
        ))
    fig.add_hline(y=0, line=dict(color='#30363d', width=1, dash='dot'))
    fig.add_vline(x=65, line=dict(color='#30363d', width=1, dash='dot'))
    fig.update_layout(
        paper_bgcolor=DARK, plot_bgcolor=SURFACE, height=440,
        margin=dict(l=10, r=10, t=30, b=40),
        xaxis=dict(title=dict(text='Smart Money Score', font=dict(color=MUTED)),
                   gridcolor=GRID, tickfont=dict(color=MUTED)),
        yaxis=dict(title=dict(text='RS vs SPY (%)', font=dict(color=MUTED)),
                   gridcolor=GRID, tickfont=dict(color=MUTED)),
        legend=dict(bgcolor=SURFACE, bordercolor='#30363d', borderwidth=1,
                    font=dict(color=MUTED, size=11)),
        font=dict(color=TEXT),
    )
    return fig

def plot_candlestick_vsa(ticker, dager):
    df = hent_enkelt(ticker, dager)
    if df.empty: return go.Figure()

    vol_sma       = df['Volume'].rolling(20).mean()
    vol_ratio     = df['Volume'] / vol_sma
    chg           = df['Close'].pct_change() * 100
    close_pct     = (df['Close'] - df['Low']) / (df['High'] - df['Low'] + 1e-9)
    absorpsjon_m  = (vol_ratio >= 1.8) & (chg.abs() <= 0.8)
    thrust_m      = (vol_ratio >= 1.5) & (chg >= 0.8) & (close_pct >= 0.65)
    shakeout_m    = (vol_ratio >= 2.5) & (chg < -0.5) & (close_pct >= 0.45)

    vol_farger = []
    for i in df.index:
        if absorpsjon_m.get(i, False):  vol_farger.append('rgba(63,185,80,0.6)')
        elif thrust_m.get(i, False):    vol_farger.append('rgba(56,139,253,0.6)')
        elif shakeout_m.get(i, False):  vol_farger.append('rgba(210,153,34,0.6)')
        elif df.loc[i,'Close'] >= df.loc[i,'Open']: vol_farger.append('rgba(63,185,80,0.26)')
        else:                           vol_farger.append('rgba(248,81,73,0.26)')

    obv = ta.obv(df['Close'], df['Volume'])

    fig = make_subplots(rows=3, cols=1, shared_xaxes=True,
                        row_heights=[0.60, 0.22, 0.18], vertical_spacing=0.02)

    fig.add_trace(go.Candlestick(
        x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'],
        increasing_line_color='#3fb950', decreasing_line_color='#f85149',
        increasing_fillcolor='#3fb950',  decreasing_fillcolor='#f85149',
        name='Kurs', showlegend=False,
    ), row=1, col=1)

    for i in df.index:
        if absorpsjon_m.get(i, False):
            fig.add_annotation(x=i, y=df.loc[i,'Low']*0.993, text='▲',
                showarrow=False, font=dict(color='#3fb950', size=10),
                xref='x', yref='y')
        elif shakeout_m.get(i, False):
            fig.add_annotation(x=i, y=df.loc[i,'High']*1.005, text='◆',
                showarrow=False, font=dict(color='#d29922', size=9),
                xref='x', yref='y')

    fig.add_trace(go.Bar(x=df.index, y=df['Volume'],
                         marker_color=vol_farger, name='Volum', showlegend=False),
                  row=2, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=vol_sma,
                             line=dict(color=MUTED, width=1, dash='dot'),
                             name='Vol SMA(20)', showlegend=False),
                  row=2, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=obv,
                             line=dict(color='#a371f7', width=1.5),
                             fill='tozeroy', fillcolor='rgba(163,113,247,0.08)',
                             name='OBV', showlegend=False),
                  row=3, col=1)

    for navn, farge, sym in [('Absorpsjon','#3fb950','▲'),
                               ('Vol-thrust','#388bfd','●'),
                               ('Shakeout',  '#d29922','◆')]:
        fig.add_trace(go.Scatter(x=[None], y=[None], mode='markers',
                                 marker=dict(color=farge, size=8),
                                 name=f'{sym} {navn}', showlegend=True), row=1, col=1)

    ax = dict(gridcolor=GRID, zeroline=False, tickfont=dict(color=MUTED, size=10))
    fig.update_layout(
        paper_bgcolor=DARK, plot_bgcolor=SURFACE, height=600,
        margin=dict(l=10, r=10, t=40, b=10),
        title=dict(text=f'<b>{ticker}</b> — Volume Spread Analysis',
                   font=dict(color=TEXT, size=14), x=0.01),
        xaxis=dict(**ax, rangeslider_visible=False),
        xaxis2=dict(**ax), xaxis3=dict(**ax),
        yaxis=dict(**ax, title=dict(text='Kurs',  font=dict(color=MUTED, size=10))),
        yaxis2=dict(**ax, title=dict(text='Volum', font=dict(color=MUTED, size=10))),
        yaxis3=dict(**ax, title=dict(text='OBV',   font=dict(color=MUTED, size=10))),
        legend=dict(orientation='h', x=0, y=1.06,
                    bgcolor='rgba(0,0,0,0)', font=dict(color=MUTED, size=11)),
        hovermode='x unified',
    )
    return fig

def plot_rs_tidslinje(tickers, sektor_etf, dager):
    alle  = list(set(tickers[:5] + [sektor_etf, BENCHMARK]))
    raw   = hent_data(tuple(alle), dager + 10)
    if 'Close' not in raw.columns.get_level_values(0):
        return go.Figure()
    bench  = raw['Close'][BENCHMARK].dropna()
    farger = ['#3fb950','#388bfd','#a371f7','#d29922','#f85149']
    fig    = go.Figure()
    for i, t in enumerate(tickers[:5]):
        if t not in raw['Close'].columns: continue
        s  = raw['Close'][t].dropna().tail(dager)
        rs = ((s/s.iloc[0]) - (bench.tail(dager)/bench.tail(dager).iloc[0])) * 100
        fig.add_trace(go.Scatter(x=rs.index, y=rs.round(2), name=t,
                                 line=dict(color=farger[i], width=1.8),
                                 hovertemplate=f'<b>{t}</b>: %{{y:+.1f}}%<extra></extra>'))
    ss  = raw['Close'][sektor_etf].dropna().tail(dager)
    rs_s = ((ss/ss.iloc[0]) - (bench.tail(dager)/bench.tail(dager).iloc[0])) * 100
    fig.add_trace(go.Scatter(x=rs_s.index, y=rs_s.round(2),
                             name=f'{sektor_etf} (sektor)',
                             line=dict(color='#30363d', width=2, dash='dot'),
                             hovertemplate=f'<b>{sektor_etf}</b>: %{{y:+.1f}}%<extra></extra>'))
    fig.add_hline(y=0, line=dict(color='#30363d', width=1))
    fig.update_layout(
        paper_bgcolor=DARK, plot_bgcolor=SURFACE, height=380,
        margin=dict(l=10, r=10, t=30, b=10),
        xaxis=dict(gridcolor=GRID, tickfont=dict(color=MUTED)),
        yaxis=dict(gridcolor=GRID, tickfont=dict(color=MUTED),
                   title=dict(text='RS vs SPY (%)', font=dict(color=MUTED))),
        legend=dict(bgcolor=SURFACE, bordercolor='#30363d', borderwidth=1,
                    font=dict(color=MUTED, size=11)),
        hovermode='x unified', font=dict(color=TEXT),
    )
    return fig

def formater_tabell(df):
    vis = df.copy()
    vis['Smart Money']  = vis['Smart Money'].apply(
        lambda v: f'🟢 {v:.0f}' if v >= 70 else (f'🟡 {v:.0f}' if v >= 50 else f'🔴 {v:.0f}'))
    vis['RS vs SPY']    = vis['RS vs SPY'].apply(lambda v: f'+{v:.1f}%' if v >= 0 else f'{v:.1f}%')
    vis['RS vs Sektor'] = vis['RS vs Sektor'].apply(lambda v: f'+{v:.1f}%' if v >= 0 else f'{v:.1f}%')
    vis['Wyckoff Fase'] = vis['Wyckoff Fase'].map({
        'spring':'🌱 Spring','markup':'📈 Mark-up','akkumulering_B':'🔵 Akk. B',
        'akkumulering_A':'⚪ Akk. A','distribusjon':'⚠️ Dist.','markdown':'📉 Mark-down',
    }).fillna(vis['Wyckoff Fase'])
    vis['OBV Opp'] = vis['OBV Opp'].apply(lambda x: '✓' if x else '—')
    vis['1d %']    = vis['1d %'].apply(lambda v: f'+{v:.2f}%' if v >= 0 else f'{v:.2f}%')
    vis['Kurs']    = vis['Kurs'].apply(lambda v: f'${v:,.2f}')
    return vis[['Ticker','Kurs','1d %','RS vs SPY','RS vs Sektor',
                'Absorpsjon','Vol-thrust','VSA Score','Wyckoff Fase','CM Score','OBV Opp','Smart Money']]

# =============================================================================
# PLOT-FUNKSJONER — GUIDE
# =============================================================================

def plot_wyckoff_syklus():
    np.random.seed(42)
    def s(a, b, n, noise=0): return np.linspace(a, b, n) + np.random.randn(n)*noise

    pris = np.concatenate([
        s(100,62,20,1.8), s(62,80,12,1.2), s(80,65,10,1.0),   # Fase A
        s(65,78,18,2.0),  s(78,63,12,1.5), s(63,76,14,1.8), s(76,67,10,1.2),  # Fase B
        s(67,58,8,1.0),   s(58,74,10,0.8),                   # Fase C
        s(74,88,14,1.2),  s(88,82,8,0.8),  s(82,96,12,1.0),  # Fase D
        s(96,118,20,1.5), s(118,110,8,1.0),s(110,138,18,2.0),s(138,130,6,1.0),s(130,155,16,1.8), # Mark-up
        s(155,162,10,2.0),s(162,148,8,1.5),s(148,158,10,2.0),s(158,145,12,1.5),
        s(145,152,8,1.5), s(152,135,10,2.0),                  # Distribusjon
        s(135,115,14,2.0),s(115,120,6,1.0),s(120,95,12,1.5),  # Mark-down
    ])
    x = np.arange(len(pris))
    lA=42; lB=lA+54; lC=lB+18; lD=lC+34; lE=lD+68; lDst=lE+58

    segmenter = [(0,lA,'#6e7681','Fase A'),(lA,lB,'#a371f7','Fase B'),
                 (lB,lC,'#3fb950','Fase C'),(lC,lD,'#388bfd','Fase D'),
                 (lD,lE,'#388bfd','Mark-up'),(lE,lDst,'#d29922','Distribusjon'),
                 (lDst,len(pris),'#f85149','Mark-down')]
    fig = go.Figure()
    shown = set()
    for start, end, col, navn in segmenter:
        end = min(end, len(pris)-1)
        fig.add_trace(go.Scatter(x=x[start:end+1], y=pris[start:end+1],
                                 mode='lines', line=dict(color=col, width=2.2),
                                 name=navn, showlegend=(navn not in shown),
                                 hoverinfo='skip'))
        shown.add(navn)

    fig.add_shape(type='line', x0=lA, x1=lC+5, y0=66, y1=66,
                  line=dict(color='rgba(63,185,80,0.33)', width=1, dash='dot'))
    fig.add_shape(type='line', x0=lA, x1=lC+5, y0=80, y1=80,
                  line=dict(color='rgba(248,81,73,0.33)', width=1, dash='dot'))

    for a in [(lA//2,56,'SC','#6e7681'),(lA-5,83,'AR','#6e7681'),
              (lB-8,57,'ST','#a371f7'),(lB+8,51,'Spring','#3fb950'),
              (lC+8,79,'SOS','#388bfd'),(lD-5,79,'LPS','#388bfd'),
              (lE+10,168,'UTAD','#d29922'),(lDst+8,122,'SOW','#f85149')]:
        fig.add_annotation(x=a[0], y=a[1], text=f'<b>{a[2]}</b>', showarrow=False,
                           font=dict(color=a[3], size=10), bgcolor='rgba(13,17,23,0.53)')

    for start, end, col in [
        (0,    lA,       'rgba(110,118,129,0.03)'),
        (lA,   lB,       'rgba(163,113,247,0.03)'),
        (lB,   lC,       'rgba(63,185,80,0.03)'),
        (lC,   lD,       'rgba(56,139,253,0.03)'),
        (lD,   lE,       'rgba(56,139,253,0.04)'),
        (lE,   lDst,     'rgba(210,153,34,0.03)'),
        (lDst, len(pris),'rgba(248,81,73,0.03)'),
    ]:
        fig.add_vrect(x0=start, x1=min(end,len(pris)-1), fillcolor=col, line_width=0)

    fig.update_layout(paper_bgcolor=DARK, plot_bgcolor=SURFACE, height=360,
                      margin=dict(l=10,r=10,t=10,b=10), hovermode=False,
                      xaxis=dict(showticklabels=False, gridcolor=GRID, zeroline=False),
                      yaxis=dict(gridcolor=GRID, zeroline=False, tickfont=dict(color=MUTED, size=10),
                                 title=dict(text='Pris', font=dict(color=MUTED, size=10))),
                      legend=dict(orientation='h', x=0, y=1.04,
                                  bgcolor='rgba(0,0,0,0)', font=dict(color=MUTED, size=10)))
    return fig

def plot_absorpsjon():
    fig = make_subplots(rows=1, cols=2,
                        subplot_titles=['Volum (× snitt)', 'Prisendring (%)'],
                        horizontal_spacing=0.12)
    kat  = ['Normal', 'Vol-thrust', 'Absorpsjon', 'Distribusjon']
    vol  = [1.0, 2.4, 2.8, 2.1]
    pris = [0.8, 2.1, 0.2, -1.6]
    vcol = ['#6e7681','#388bfd','#3fb950','#f85149']
    pcol = ['#6e7681','#3fb950','#3fb950','#f85149']
    fig.add_trace(go.Bar(x=kat, y=vol, marker_color=vcol, showlegend=False,
                         text=[f'{v:.1f}×' for v in vol], textposition='outside',
                         textfont=dict(color=TEXT, size=11)), row=1, col=1)
    fig.add_trace(go.Bar(x=kat, y=pris, marker_color=pcol, showlegend=False,
                         text=[f'{v:+.1f}%' for v in pris], textposition='outside',
                         textfont=dict(color=TEXT, size=11)), row=1, col=2)
    fig.update_layout(paper_bgcolor=DARK, plot_bgcolor=SURFACE, height=290,
                      margin=dict(l=10,r=10,t=40,b=10), font=dict(color=TEXT, size=11))
    for ax in ['xaxis','xaxis2']:
        fig.update_layout(**{ax: dict(gridcolor=GRID, tickfont=dict(color=MUTED, size=10))})
    for ax in ['yaxis','yaxis2']:
        fig.update_layout(**{ax: dict(gridcolor=GRID, zeroline=True,
                                      zerolinecolor='#30363d', tickfont=dict(color=MUTED, size=10))})
    for ann in fig.layout.annotations:
        ann.font.color = MUTED; ann.font.size = 12
    return fig

def plot_obv_divergens():
    np.random.seed(7)
    n = 60; x = np.arange(n)
    pris = 100 + np.cumsum(np.random.randn(n)*0.4)
    pris[30:] += np.linspace(0, -3, 30)
    obv  = np.cumsum(np.random.randn(n)*200)
    obv[20:] += np.linspace(0, 4000, 40)

    fig = make_subplots(rows=2, cols=1, shared_xaxes=True,
                        row_heights=[0.55, 0.45], vertical_spacing=0.04)
    fig.add_trace(go.Scatter(x=x, y=pris, line=dict(color=TEXT, width=2),
                             name='Pris', hovertemplate='Pris: %{y:.1f}<extra></extra>'),
                  row=1, col=1)
    fig.add_shape(type='line', x0=28, x1=59, y0=pris[28], y1=pris[-1],
                  line=dict(color='rgba(248,81,73,0.47)', width=1.5, dash='dot'))
    fig.add_trace(go.Scatter(x=x, y=obv, line=dict(color='#a371f7', width=2),
                             fill='tozeroy', fillcolor='rgba(163,113,247,0.07)',
                             name='OBV', hovertemplate='OBV: %{y:,.0f}<extra></extra>'),
                  row=2, col=1)
    fig.add_shape(type='line', x0=20, x1=59, y0=obv[20], y1=obv[-1],
                  line=dict(color='rgba(63,185,80,0.47)', width=1.5, dash='dot'))
    fig.add_annotation(x=52, y=pris[-1]+1.5, text='Pris svak', showarrow=False,
                       font=dict(color='#f85149', size=10))
    fig.update_layout(paper_bgcolor=DARK, plot_bgcolor=SURFACE, height=310,
                      margin=dict(l=10,r=10,t=14,b=10), hovermode='x unified',
                      legend=dict(bgcolor='rgba(0,0,0,0)', font=dict(color=MUTED, size=11)),
                      font=dict(color=TEXT, size=11))
    for ax in ['xaxis','xaxis2']:
        fig.update_layout(**{ax: dict(gridcolor=GRID, zeroline=False,
                                      showticklabels=False, tickfont=dict(color=MUTED))})
    for ax in ['yaxis','yaxis2']:
        fig.update_layout(**{ax: dict(gridcolor=GRID, zeroline=False, tickfont=dict(color=MUTED, size=10))})
    return fig

def plot_rs_illustrasjon():
    np.random.seed(21); n = 90; x = np.arange(n)
    spy  = 100 + np.cumsum(np.random.randn(n)*0.5)
    sterk = (spy + np.linspace(0,18,n) + np.cumsum(np.random.randn(n)*0.3))
    svak  = (spy - np.linspace(0,12,n) + np.cumsum(np.random.randn(n)*0.3))
    sterk = sterk/sterk[0]*100; svak = svak/svak[0]*100; spy_n = spy/spy[0]*100
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=x, y=sterk, name='Sterk aksje',
                             line=dict(color='#3fb950', width=2)))
    fig.add_trace(go.Scatter(x=x, y=spy_n, name='SPY',
                             line=dict(color=MUTED, width=1.5, dash='dot')))
    fig.add_trace(go.Scatter(x=x, y=svak, name='Svak aksje',
                             line=dict(color='#f85149', width=2)))
    fig.add_annotation(x=88, y=sterk[-1]+2,
                       text=f'+{sterk[-1]-100:.0f}%', showarrow=False,
                       font=dict(color='#3fb950', size=11))
    fig.add_annotation(x=88, y=svak[-1]-3,
                       text=f'{svak[-1]-100:.0f}%', showarrow=False,
                       font=dict(color='#f85149', size=11))
    return _base(fig, h=290)

def plot_sms_donut():
    fig = go.Figure(go.Pie(
        labels=['RS (25%)', 'VSA (30%)', 'Wyckoff (30%)', 'OBV (15%)'],
        values=[25, 30, 30, 15], hole=0.60,
        marker=dict(colors=['#388bfd','#3fb950','#a371f7','#d29922'],
                    line=dict(color=DARK, width=2)),
        textfont=dict(color=TEXT, size=11), textposition='outside',
        hovertemplate='%{label}: %{value}%<extra></extra>',
    ))
    fig.add_annotation(text='<b>SMS</b><br>0–100', x=0.5, y=0.5,
                       showarrow=False, font=dict(color=TEXT, size=13))
    fig.update_layout(paper_bgcolor=DARK, height=270,
                      margin=dict(l=10,r=10,t=10,b=10),
                      legend=dict(bgcolor='rgba(0,0,0,0)', font=dict(color=MUTED, size=11)))
    return fig

# =============================================================================
# SIDE: GUIDE
# =============================================================================

def vis_guide():
    st.markdown("""
    <div style='padding: 2rem 0 1rem;'>
      <div style='display:flex; align-items:center; gap:12px; margin-bottom:8px;'>
        <span style='font-size:32px;'>🐋</span>
        <span style='font-size:26px; font-weight:500; color:#e6edf3;'>Smart Money Dashboard</span>
      </div>
      <p style='color:#8b949e; font-size:14px; max-width:680px; line-height:1.75; margin:0;'>
        Et forskningsverktøy for å identifisere institusjonell aktivitet i aksjemarkedet —
        inspirert av <b style='color:#c9d1d9;'>Wyckoff-teori</b> og
        <b style='color:#c9d1d9;'>Volume Spread Analysis (VSA)</b>.
      </p>
    </div>
    """, unsafe_allow_html=True)

    if st.button("➜  Gå til dashboardet", type="primary"):
        st.session_state.side = 'dashboard'
        st.rerun()

    st.markdown("---")

    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "🧭 Kom i gang", "📐 Wyckoff", "📊 VSA", "📈 Relativ styrke",
        "🎯 Smart Money Score", "🖥 Brukerveiledning",
    ])

    # ── TAB 1 ────────────────────────────────────────────────────────────────
    with tab1:
        c1, c2 = st.columns([3, 2], gap='large')
        with c1:
            st.markdown("## Hva er Smart Money?")
            st.markdown("""
            <p style='color:#8b949e;font-size:14px;line-height:1.75;'>
            «Smart Money» er institusjonelle aktører — pensjonsfond, hedgefond,
            forsikringsselskaper og market makers — som forvalter så store summer at de
            etterlater seg <b style='color:#c9d1d9;'>spor i pris og volum</b> før store
            prisbevegelser. Dette dashboardet identifiserer disse sporene systematisk.
            </p>""", unsafe_allow_html=True)

            st.markdown("### Trelagsanalysen")
            for modul, tittel, beskr, farge in [
                ("Modul 1","Sektor","Hvilke sektorer leder? Kapital strømmer inn her.","#388bfd"),
                ("Modul 2","Aksje", "Hvilke aksjer viser absorpsjonssignaler?","#a371f7"),
                ("Modul 3","Fase",  "Wyckoff-fase og konkrete entry-nivåer.","#3fb950"),
            ]:
                st.markdown(f"""
                <div style='display:flex;gap:12px;padding:10px 0;border-bottom:1px solid #21262d;'>
                  <div style='min-width:76px;padding:3px 8px;border-radius:20px;background:{farge}18;
                               border:1px solid {farge}44;text-align:center;font-size:11px;
                               color:{farge};font-weight:500;margin-top:2px;'>{modul}</div>
                  <div>
                    <div style='font-size:13px;font-weight:500;color:#c9d1d9;margin-bottom:2px;'>{tittel}</div>
                    <div style='font-size:12px;color:#8b949e;'>{beskr}</div>
                  </div>
                </div>""", unsafe_allow_html=True)

        with c2:
            st.markdown("### Arbeidsflyt")
            for i, (t, b, f) in enumerate([
                ("Les sektor-varmekartet","Finn grønneste sektorer over 1M/3M/6M","#388bfd"),
                ("Velg vinner-sektor","Sett i sidebaren og kjør analyse","#a371f7"),
                ("Sorter på Smart Money","Høyest score = sterkest signal","#3fb950"),
                ("Filtrer Spring/LPS","Beste entry-soner — Wyckoff Fase C","#3fb950"),
                ("Bekreft med VSA-chart","Se absorpsjon-piler og OBV-trend","#388bfd"),
                ("Sett stop under support","Trading range low minus 1× ATR","#d29922"),
            ], 1):
                st.markdown(f"""
                <div style='display:flex;gap:10px;padding:8px 0;border-bottom:1px solid #21262d;'>
                  <div style='min-width:22px;height:22px;border-radius:50%;background:#21262d;
                               border:1px solid {f}55;display:flex;align-items:center;
                               justify-content:center;color:{f};font-size:11px;
                               font-weight:500;flex-shrink:0;margin-top:1px;'>{i}</div>
                  <div>
                    <div style='font-size:12px;font-weight:500;color:#c9d1d9;margin-bottom:1px;'>{t}</div>
                    <div style='font-size:11px;color:#8b949e;'>{b}</div>
                  </div>
                </div>""", unsafe_allow_html=True)

        st.markdown("---")
        st.markdown("""
        <div style='background:#161b22;border:1px solid #d2992244;border-radius:8px;padding:12px 16px;'>
          <span style='color:#d29922;font-size:12px;font-weight:500;'>⚠ Ansvarsfraskrivelse</span><br>
          <span style='color:#8b949e;font-size:12px;line-height:1.65;'>
          Dette er et <b style='color:#c9d1d9;'>forsknings- og opplæringsverktøy</b>, ikke finansiell
          rådgivning. All handel innebærer risiko. Data fra Yahoo Finance kan ha forsinkelser og mangler.
          Gjør alltid din egen analyse og konsulter en lisensiert finansrådgiver.
          </span>
        </div>""", unsafe_allow_html=True)

    # ── TAB 2: WYCKOFF ───────────────────────────────────────────────────────
    with tab2:
        st.markdown("## Wyckoff-metoden")
        st.markdown("""<p style='color:#8b949e;font-size:14px;line-height:1.75;max-width:760px;'>
        Richard D. Wyckoff (1873–1934) hevdet at markedet kontrolleres av én tenkt aktør —
        <b style='color:#c9d1d9;'>Composite Man (CM)</b> — som representerer summen av alle
        institusjonelle beslutninger. Han opererer i en forutsigbar syklus:</p>""",
        unsafe_allow_html=True)

        st.plotly_chart(plot_wyckoff_syklus(), use_container_width=True,
                        config={'displayModeBar': False})

        st.markdown("### Akkumuleringens fem faser")
        for fase, tittel, tekst, farge in [
            ("Fase A","Stopp av nedturen",
             "Selling Climax (SC): massivt salgsvolum stopper nedgangen brått. Automatic Rally (AR): "
             "prisen spretter opp. Secondary Test (ST): retur mot SC-nivå på lavere volum — "
             "bekrefter at supply er avtagende.","#6e7681"),
            ("Fase B","Bygger årsaken",
             "CM akkumulerer stille over uker/måneder. Prisen oscillerer mellom support og resistance. "
             "Volum-karakteren endres: høyt på oppturene, lavt på nedturene. "
             "Retail-investorer frustreres og selger.","#a371f7"),
            ("Fase C","Spring / Shakeout",
             "CM tester siste rest av supply ved å dytte prisen UNDER support kortvarig. "
             "Trigger stop-losses og lokker shorts. Men prisen snapper tilbake raskt. "
             "Dette er den BESTE entry-muligheten i hele syklusen.","#3fb950"),
            ("Fase D","Bekreftelse",
             "Sign of Strength (SOS): prisen bryter resistance på høyt volum. "
             "Last Point of Support (LPS): siste pullback til gammel resistance (nå support). "
             "Sekundær entry for de som gikk glipp av Spring.","#388bfd"),
            ("Fase E","Mark-up",
             "CM holder posisjon mens prisen stiger fritt. Media begynner å omtale aksjen positivt. "
             "Syklusen avsluttes med distribusjon på toppen der CM selger til entusiastiske retail-kjøpere.","#388bfd"),
        ]:
            with st.expander(f"**{fase}** — {tittel}", expanded=(fase in ['Fase C','Fase D'])):
                st.markdown(f"""
                <div style='display:flex;gap:12px;'>
                  <div style='width:3px;background:{farge};border-radius:3px;flex-shrink:0;margin:2px 0;'></div>
                  <p style='color:#8b949e;font-size:13px;line-height:1.75;margin:0;'>{tekst}</p>
                </div>""", unsafe_allow_html=True)

        st.markdown("### Nøkkelbegreper")
        begreper = [
            ("SC","Selling Climax","Enormt salgsvolum stopper nedgangen. Pris lukker langt fra dagslav."),
            ("AR","Automatic Rally","Kjapt hopp etter SC. Definerer øvre grense for trading range."),
            ("ST","Secondary Test","Test av SC-nivå på lavere volum. Bekrefter at supply er tømt."),
            ("SOS","Sign of Strength","Breakout av trading range på høyt volum. Demand dominerer."),
            ("LPS","Last Point of Support","Siste pullback etter SOS. Gammel resistance er ny support."),
            ("UTAD","Upthrust After Dist.","Falsk breakout over topp på høyt volum, lukker under."),
            ("SOW","Sign of Weakness","Distribusjon bekreftet: breakdown av support på høyt volum."),
            ("BUTC","Back-Up to the Creek","Pullback til brutt resistance. Sekundær entry-mulighet."),
        ]
        c1, c2 = st.columns(2)
        for i, (fk, nm, fork) in enumerate(begreper):
            col = c1 if i % 2 == 0 else c2
            col.markdown(f"""
            <div class='concept-card'>
              <h4><span style='color:#388bfd;font-family:monospace;'>{fk}</span> — {nm}</h4>
              <p>{fork}</p>
            </div>""", unsafe_allow_html=True)

    # ── TAB 3: VSA ───────────────────────────────────────────────────────────
    with tab3:
        st.markdown("## Volume Spread Analysis (VSA)")
        st.markdown("""<p style='color:#8b949e;font-size:14px;line-height:1.75;max-width:760px;'>
        Kjerneprinsippet: <b style='color:#c9d1d9;'>sammenhengen mellom volum og prisspread
        avslører hvem som kontrollerer markedet</b>. Høyt volum betyr at store aktører er
        involvert — spørsmålet er om de kjøper eller selger.</p>""", unsafe_allow_html=True)

        st.markdown("### Effort vs. Result")
        st.plotly_chart(plot_absorpsjon(), use_container_width=True,
                        config={'displayModeBar': False})

        for cls, bold_col, bold_txt, rest in [
            ("green","#3fb950","Absorpsjon (viktigste signal):","Høyt volum + liten prisreaksjon. CM kjøper ALT som tilbys uten å la prisen falle. Prisen «klistrer» fordi en stor kjøper absorberer supply."),
            ("","#388bfd","Volume Thrust:","Høyt volum + stor prisoppgang + lukker i øvre del av range. Institusjoner kjøper aggressivt — åpen demand som overvelder supply."),
            ("yellow","#d29922","Shakeout / Spring:","Enormt volum + pris faller intradag MEN lukker i midten. CM dytter ned for å utløse stop-losses og kjøper alt de får. Neste dag returnerer prisen."),
        ]:
            st.markdown(f"""<div class='callout {cls}'>
              <b style='color:{bold_col};'>{bold_txt}</b> {rest}</div>""",
            unsafe_allow_html=True)

        st.markdown("### OBV — den skjulte indikatoren")
        co1, co2 = st.columns([3, 2], gap='large')
        with co1:
            st.plotly_chart(plot_obv_divergens(), use_container_width=True,
                            config={'displayModeBar': False})
        with co2:
            st.markdown("""<p style='color:#8b949e;font-size:13px;line-height:1.75;margin-top:0.8rem;'>
            OBV legger til volum på opp-dager og trekker fra på ned-dager. Resultatet er et
            kumulativt mål på hvem som netto akkumulerer.<br><br>
            <b style='color:#3fb950;'>Bullish divergens:</b> OBV stiger mens prisen er flat
            eller svakt ned — CM kan ikke skjule nettokjøpene sine i OBV.<br><br>
            <b style='color:#f85149;'>Bearish divergens:</b> OBV faller mens prisen holder seg oppe.
            Distribusjons-signal.</p>""", unsafe_allow_html=True)

        st.markdown("### Slik leses VSA-chartet")
        for sym, farge, navn, forklaring in [
            ("▲ Grønn pil (under candle)","#3fb950","Absorpsjonsdag",
             "Vol > 1.8× snitt, prisendring < 0.8%. Se etter serier av disse dagene."),
            ("◆ Gul diamant (over candle)","#d29922","Shakeout",
             "Vol > 2.5× snitt, pris faller men lukker i midten. Bekreft med neste dag."),
            ("Blå volumsøyle","#388bfd","Volume Thrust",
             "Vol > 1.5× snitt, pris +0.8%+, lukker i øvre 35% av range."),
            ("Lilla OBV-kurve (bunn-panel)","#a371f7","On-Balance Volume",
             "Stigende OBV med flat pris = skjult akkumulering."),
        ]:
            st.markdown(f"""
            <div style='display:flex;gap:12px;padding:9px 0;border-bottom:1px solid #21262d;'>
              <div style='min-width:170px;font-family:monospace;font-size:11px;
                           color:{farge};padding-top:2px;'>{sym}</div>
              <div>
                <div style='font-size:13px;font-weight:500;color:#c9d1d9;margin-bottom:2px;'>{navn}</div>
                <div style='font-size:12px;color:#8b949e;'>{forklaring}</div>
              </div>
            </div>""", unsafe_allow_html=True)

    # ── TAB 4: RS ────────────────────────────────────────────────────────────
    with tab4:
        st.markdown("## Relativ styrke — kapitalflyt-signalet")
        co1, co2 = st.columns([3, 2], gap='large')
        with co1:
            st.plotly_chart(plot_rs_illustrasjon(), use_container_width=True,
                            config={'displayModeBar': False})
        with co2:
            st.markdown("""<div style='margin-top:0.5rem;'>
            <div class='callout green'><b style='color:#3fb950;'>Positiv RS</b>
             — aksjen stiger mer enn SPY. Kapital strømmer inn.</div>
            <div class='callout red'><b style='color:#f85149;'>Negativ RS</b>
             — kapital strømmer ut. Unngå long-posisjoner.</div>
            <p style='color:#8b949e;font-size:13px;line-height:1.75;margin-top:10px;'>
            <b style='color:#c9d1d9;'>Cross-timeframe-regel:</b> Sterk på 1M, 3M og 6M
            er langt sterkere enn kun sterk denne uken.
            Vedvarende styrke = institusjonell overbevisning.</p></div>""",
            unsafe_allow_html=True)

        st.markdown("### Sektorrotasjon")
        co1, co2, co3 = st.columns(3)
        for col, (fase, sekt, farge, beskr) in zip([co1, co2, co3], [
            ("Tidlig bull",["XLY — Forbruk","XLK — Teknologi","XLF — Finans"],"#3fb950","Risiko-on, vekst-sektorer leder."),
            ("Mid bull",   ["XLI — Industri","XLB — Materialer","XLE — Energi"],"#388bfd","Sykliske sektorer tar over."),
            ("Sen bull",   ["XLV — Helse","XLP — Dagligvare","XLU — Utilities"],"#d29922","Defensive sektorer styrkes."),
        ]):
            col.markdown(f"""
            <div style='background:#161b22;border:1px solid #30363d;border-radius:8px;
                         padding:14px;min-height:160px;'>
              <div style='font-size:12px;color:{farge};font-weight:500;margin-bottom:8px;'>{fase}</div>
              {''.join(f"<div style='font-size:12px;color:#c9d1d9;margin-bottom:4px;'>→ {s}</div>" for s in sekt)}
              <div style='font-size:11px;color:#6e7681;margin-top:8px;'>{beskr}</div>
            </div>""", unsafe_allow_html=True)

    # ── TAB 5: SMS ───────────────────────────────────────────────────────────
    with tab5:
        st.markdown("## Smart Money Score (SMS)")
        co1, co2 = st.columns([2, 3], gap='large')
        with co1:
            st.plotly_chart(plot_sms_donut(), use_container_width=True,
                            config={'displayModeBar': False})
        with co2:
            for navn, vekt, farge, beskr in [
                ("Relativ styrke","25%","#388bfd","Aksje vs SPY. Normalisert 0–100."),
                ("VSA Score",     "30%","#3fb950","Absorpsjon × 8 + Thrust × 10 + Shakeout × 6 + OBV-bonus."),
                ("Wyckoff CM",    "30%","#a371f7","Composite Man confidence. Spring = høyest mulig."),
                ("OBV Trend",     "15%","#d29922","Binær: stiger OBV over 20 dager? +15 poeng."),
            ]:
                st.markdown(f"""
                <div style='display:flex;gap:12px;padding:10px 0;border-bottom:1px solid #21262d;'>
                  <div style='min-width:46px;font-size:15px;font-weight:500;color:{farge};
                               font-family:monospace;flex-shrink:0;'>{vekt}</div>
                  <div>
                    <div style='font-size:13px;font-weight:500;color:#c9d1d9;margin-bottom:2px;'>{navn}</div>
                    <div style='font-size:12px;color:#8b949e;'>{beskr}</div>
                  </div>
                </div>""", unsafe_allow_html=True)

        st.markdown("### Tolkningstabel")
        for score, label, farge, tekst in [
            ("70–100","🟢 Sterk institusjonell interesse","#3fb950",
             "Alle fire dimensjoner peker riktig. Sjekk VSA-chart for timing."),
            ("50–69", "🟡 Moderat — avvent bekreftelse","#d29922",
             "Signaler er der, men ikke fullt bekreftet. Legg på watch-list."),
            ("0–49",  "🔴 Svak eller negativ","#f85149",
             "Unngå long-posisjoner. Kan være i distribusjon eller mark-down."),
        ]:
            st.markdown(f"""
            <div style='display:flex;gap:14px;padding:11px 0;border-bottom:1px solid #21262d;'>
              <div style='min-width:80px;font-family:monospace;font-size:13px;
                           color:{farge};font-weight:500;padding-top:2px;'>{score}</div>
              <div>
                <div style='font-size:13px;font-weight:500;color:#c9d1d9;margin-bottom:2px;'>{label}</div>
                <div style='font-size:12px;color:#8b949e;'>{tekst}</div>
              </div>
            </div>""", unsafe_allow_html=True)

        st.markdown("""<div class='callout yellow' style='margin-top:1rem;'>
        <b style='color:#d29922;'>Viktig:</b> SMS er et <i>screening</i>-verktøy, ikke et
        handelssignal. Høy score betyr at aksjen fortjener grundigere analyse — ikke et automatisk kjøp.
        </div>""", unsafe_allow_html=True)

    # ── TAB 6: BRUKERVEILEDNING ───────────────────────────────────────────────
    with tab6:
        st.markdown("## Brukerveiledning")
        st.markdown("### Sidepanel")
        for felt, beskr in [
            ("📖 Guide / 📊 Dashboard","Bytter mellom forsiden og dashboardet."),
            ("Tidsperiode","1M = kortsiktig. 3–6M = swing-trading. 1Y = langsiktig."),
            ("Velg sektor","Velg sektor for drill-down basert på varmekartet."),
            ("VSA-chart for","Velg enkeltaksje for candlestick-analyse."),
            ("Oppdater analyse","Tømmer cache og henter fersk data fra Yahoo Finance."),
        ]:
            st.markdown(f"""
            <div class='concept-card' style='margin-bottom:7px;'>
              <h4>{felt}</h4><p>{beskr}</p>
            </div>""", unsafe_allow_html=True)

        st.markdown("### Fanene i dashboardet")
        for fane, beskr in [
            ("🗺 Sektor-varmekart","Heatmap over 11 sektorer mot SPY. Les alle tre kolonner — konsistent grønn = sterkest signal."),
            ("🔬 Drill-down scanner","Boble-diagram + tabell over topp 20 i valgt sektor. Klikk kolonneoverskrift for sortering."),
            ("📊 VSA-chart","Candlestick med volum og OBV. ▲ = absorpsjon, ◆ = shakeout. Scroll for zoom."),
            ("📈 RS-tidslinje","Kumulativ RS for topp 5 aksjer. Stiplet = sektor-ETF som referanse."),
        ]:
            st.markdown(f"""
            <div style='display:flex;gap:12px;padding:10px 0;border-bottom:1px solid #21262d;'>
              <div style='font-size:13px;font-weight:500;color:#c9d1d9;min-width:180px;flex-shrink:0;'>{fane}</div>
              <div style='font-size:13px;color:#8b949e;'>{beskr}</div>
            </div>""", unsafe_allow_html=True)

        st.markdown("### Kolonneoversikt i tabellen")
        co1, co2 = st.columns(2)
        for i, (kol, beskr) in enumerate([
            ("Smart Money","Sammensatt score 0–100. Primær sorteringskolonne."),
            ("Wyckoff Fase","🌱 Spring = beste entry · 📈 Mark-up = bekreftelse."),
            ("RS vs SPY","Vil ha > 0 (helst > +3%) for long."),
            ("RS vs Sektor","Outperformer aksjen sin sektor?"),
            ("Absorpsjon","Antall absorpsjonsdager (30d). Høyere = bedre."),
            ("OBV Opp","✓ = OBV stigende. Kritisk bekreftelse."),
        ]):
            col = co1 if i % 2 == 0 else co2
            col.markdown(f"""
            <div style='padding:7px 0;border-bottom:1px solid #21262d;'>
              <span style='font-family:monospace;font-size:12px;color:#388bfd;'>{kol}</span>
              <span style='font-size:12px;color:#8b949e;margin-left:6px;'>{beskr}</span>
            </div>""", unsafe_allow_html=True)

# =============================================================================
# SIDE: DASHBOARD
# =============================================================================

def vis_dashboard():
    # Les widget-verdier direkte fra eksplisitte session_state-nøkler
    periode_dager = PERIODE_VALG.get(
        st.session_state.get('sb_periode', '3 måneder'), 90)
    sektor_valg  = st.session_state.get('sb_sektor', 'XLK')
    # chart_ticker leses direkte i tab3 via eigen selectbox — ikke her

    # Header
    col_t, col_d = st.columns([3, 1])
    with col_t:
        st.markdown("# Smart Money Dashboard")
        st.markdown(
            f"<span style='color:#8b949e;font-size:13px;'>"
            f"Sektor: <b style='color:#c9d1d9;'>{sektor_valg} — {SEKTORER[sektor_valg][0]}</b>"
            f" &nbsp;|&nbsp; {datetime.today().strftime('%d.%m.%Y %H:%M')}"
            f"</span>", unsafe_allow_html=True)
    with col_d:
        st.markdown("<div style='height:30px'></div>", unsafe_allow_html=True)
        if st.button("⟳ Tøm cache", use_container_width=True):
            st.cache_data.clear()
            st.rerun()
    st.markdown("---")

    with st.spinner("Henter sektor-data..."):
        sektor_df = sektor_screening(periode_dager)
    with st.spinner(f"Skanner {sektor_valg}..."):
        scan_df = drill_down_scanner(sektor_valg, periode_dager)

    if not scan_df.empty:
        topp       = scan_df.iloc[0]
        ant_grønn  = int((scan_df['Smart Money'] >= 65).sum())
        ant_spring = int((scan_df['Wyckoff Fase'] == 'spring').sum())
        m1, m2, m3, m4, m5 = st.columns(5)
        m1.metric("Topp-kandidat",  topp['Ticker'],        f"SMS: {topp['Smart Money']:.0f}/100")
        m2.metric("Beste fase",     topp['Wyckoff Fase'].replace('_',' ').title(),
                  f"RS: {topp['RS vs SPY']:+.1f}%")
        m3.metric("Spring/LPS",     f"{ant_spring} aksjer","Beste entry-soner")
        m4.metric("Høy SMS (≥65)",  f"{ant_grønn}/{len(scan_df)}", "Institusjonell interesse")
        rs_rad = sektor_df[sektor_df['ETF'] == sektor_valg]
        m5.metric("Sektor RS 3M",
                  f"{rs_rad['RS 3M'].values[0]:+.1f}%" if not rs_rad.empty else "—",
                  "vs SPY")
    st.markdown("---")

    tab1, tab2, tab3, tab4 = st.tabs([
        "🗺  Sektor-varmekart","🔬  Drill-down scanner","📊  VSA-chart","📈  RS-tidslinje",
    ])

    with tab1:
        st.markdown("### Relativ styrke vs SPY — alle 11 sektorer")
        st.caption("Grønt = kapital strømmer inn · Rødt = kapital strømmer ut")
        st.plotly_chart(plot_sektor_heatmap(sektor_df),
                        use_container_width=True, config={'displayModeBar': False})
        vis_s = sektor_df.copy()
        for kol in ['RS 1M','RS 3M','RS 6M','Score']:
            vis_s[kol] = vis_s[kol].apply(lambda v: f'+{v:.1f}%' if v >= 0 else f'{v:.1f}%')
        st.dataframe(vis_s, use_container_width=True, hide_index=True)

    with tab2:
        if scan_df.empty:
            st.warning("Ingen data. Prøv å tømme cache.")
        else:
            ca, cb = st.columns([3, 2], gap='large')
            with ca:
                st.markdown(f"### Boble-diagram — {sektor_valg}")
                st.caption("X = Smart Money Score · Y = RS vs SPY · Størrelse = absorpsjons-dager")
                st.plotly_chart(plot_rs_boble(scan_df), use_container_width=True,
                                config={'displayModeBar': False})
            with cb:
                st.markdown("### Topp 5")
                for _, row in scan_df.head(5).iterrows():
                    farge = WYCKOFF_FASE_FARGE.get(row['Wyckoff Fase'], '#6e7681')
                    sms   = row['Smart Money']
                    st.markdown(f"""
                    <div style='background:#161b22;border:1px solid #30363d;border-radius:8px;
                                padding:10px 14px;margin-bottom:8px;'>
                      <div style='display:flex;justify-content:space-between;align-items:center;'>
                        <span style='font-size:15px;font-weight:500;color:#e6edf3;'>{row['Ticker']}</span>
                        <span style='font-size:11px;background:{farge}22;color:{farge};
                                     border:1px solid {farge}44;border-radius:4px;padding:2px 8px;'>
                          {row['Wyckoff Fase'].replace('_',' ').title()}</span>
                      </div>
                      <div style='margin:6px 0 4px;background:#21262d;border-radius:3px;height:5px;'>
                        <div style='width:{int(sms)}%;background:{farge};border-radius:3px;height:5px;'></div>
                      </div>
                      <div style='display:flex;gap:14px;font-size:12px;color:#8b949e;'>
                        <span>SMS: <b style='color:#c9d1d9;'>{sms:.0f}</b></span>
                        <span>RS: <b style='color:{"#3fb950" if row["RS vs SPY"]>=0 else "#f85149"};'>
                          {row["RS vs SPY"]:+.1f}%</b></span>
                        <span>Abs: <b style='color:#c9d1d9;'>{row["Absorpsjon"]}</b></span>
                        <span>OBV: <b style='color:#c9d1d9;'>{"↑" if row["OBV Opp"] else "↓"}</b></span>
                      </div>
                    </div>""", unsafe_allow_html=True)

            st.markdown("### Smart Money Scanner")
            st.caption("🟢 SMS ≥ 70 · 🟡 50–70 · 🔴 under 50 · Klikk kolonneoverskrift for sortering")
            st.dataframe(formater_tabell(scan_df), use_container_width=True, height=480)
            csv = scan_df.to_csv(index=False).encode('utf-8')
            st.download_button("⬇  Last ned CSV", data=csv,
                               file_name=f"smart_money_{sektor_valg}_{datetime.today().strftime('%Y%m%d')}.csv",
                               mime='text/csv')

    with tab3:
        # Selectbox direkte i fanen — garantert korrekt rekkefølge
        _, tickers_tab3 = SEKTORER[sektor_valg]
        chart_ticker = st.selectbox(
            "Velg aksje for VSA-analyse",
            tickers_tab3[:20],
            key='tab3_chart',
        )
        st.caption("▲ Absorpsjon (grønn) · ◆ Shakeout (gul) · OBV i bunn-panel · Scroll for zoom")
        with st.spinner(f"Laster {chart_ticker}..."):
            fig_vsa = plot_candlestick_vsa(chart_ticker, min(periode_dager, 90))
        st.plotly_chart(fig_vsa, use_container_width=True,
                        config={'displayModeBar': True, 'scrollZoom': True})
        if not scan_df.empty and chart_ticker in scan_df['Ticker'].values:
            r = scan_df[scan_df['Ticker'] == chart_ticker].iloc[0]
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Smart Money Score", f"{r['Smart Money']:.0f}/100")
            c2.metric("Wyckoff Fase",      r['Wyckoff Fase'].replace('_',' ').title())
            c3.metric("Absorpsjonsdager",  r['Absorpsjon'])
            c4.metric("OBV-trend",         "Stigende ↑" if r['OBV Opp'] else "Fallende ↓")

    with tab4:
        st.markdown(f"### Relativ styrke over tid — topp 5 i {sektor_valg}")
        st.caption("Kumulativ RS vs SPY · Stiplet = sektor-ETF som referanse")
        topp5 = scan_df.head(5)['Ticker'].tolist() if not scan_df.empty else []
        if topp5:
            with st.spinner("Bygger RS-tidslinje..."):
                fig_rs = plot_rs_tidslinje(topp5, sektor_valg, periode_dager)
            st.plotly_chart(fig_rs, use_container_width=True, config={'displayModeBar': False})
        else:
            st.info("Kjør scanner for å se RS-tidslinje.")

# =============================================================================
# ROUTER — velg side basert på session_state
# =============================================================================

if st.session_state.side == 'guide':
    vis_guide()
else:
    vis_dashboard()
