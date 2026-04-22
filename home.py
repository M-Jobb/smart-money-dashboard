# =============================================================================
# SMART MONEY DASHBOARD — Forside / Dokumentasjon
# Forklarer Wyckoff-teori, VSA og bruken av dashboardet
# =============================================================================

import streamlit as st
import plotly.graph_objects as go
import numpy as np
from plotly.subplots import make_subplots

st.set_page_config(
    page_title="Smart Money — Guide",
    page_icon="🐋",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── GLOBALT TEMA (identisk med dashboard) ────────────────────────────────────
st.markdown("""
<style>
    .stApp { background-color: #0d1117; color: #c9d1d9; }
    .stApp header { background-color: #0d1117; }
    [data-testid="stSidebar"] {
        background-color: #161b22;
        border-right: 1px solid #30363d;
    }
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] .stMarkdown p { color: #8b949e; font-size: 13px; }
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 { color: #c9d1d9; }
    h1 { color: #e6edf3 !important; font-weight: 500 !important; }
    h2 { color: #c9d1d9 !important; font-weight: 500 !important; }
    h3 { color: #8b949e   !important; font-weight: 500 !important; }
    hr { border-color: #30363d; }
    .stTabs [data-baseweb="tab-list"] { background: #161b22; border-radius: 8px; padding: 4px; }
    .stTabs [data-baseweb="tab"] { color: #8b949e; border-radius: 6px; }
    .stTabs [aria-selected="true"] { background: #21262d !important; color: #c9d1d9 !important; }

    /* Egne komponenter */
    .concept-card {
        background: #161b22;
        border: 1px solid #30363d;
        border-radius: 10px;
        padding: 18px 20px;
        margin-bottom: 10px;
    }
    .concept-card h4 {
        color: #e6edf3 !important;
        font-size: 15px !important;
        margin: 0 0 6px 0;
        font-weight: 500 !important;
    }
    .concept-card p {
        color: #8b949e;
        font-size: 13px;
        line-height: 1.65;
        margin: 0;
    }
    .pill {
        display: inline-block;
        padding: 3px 10px;
        border-radius: 20px;
        font-size: 11px;
        font-weight: 500;
        margin: 2px;
    }
    .step-num {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 26px; height: 26px;
        border-radius: 50%;
        background: #21262d;
        border: 1px solid #388bfd44;
        color: #388bfd;
        font-size: 13px;
        font-weight: 500;
        margin-right: 8px;
        flex-shrink: 0;
    }
    .signal-row {
        display: flex;
        align-items: flex-start;
        gap: 12px;
        padding: 10px 0;
        border-bottom: 1px solid #21262d;
    }
    .signal-row:last-child { border-bottom: none; }
    .callout {
        background: #161b22;
        border-left: 3px solid #388bfd;
        border-radius: 0 8px 8px 0;
        padding: 12px 16px;
        margin: 12px 0;
        font-size: 13px;
        color: #8b949e;
        line-height: 1.65;
    }
    .callout.green  { border-left-color: #3fb950; }
    .callout.yellow { border-left-color: #d29922; }
    .callout.red    { border-left-color: #f85149; }
    .score-legend {
        display: flex;
        gap: 8px;
        flex-wrap: wrap;
        margin: 8px 0;
    }
</style>
""", unsafe_allow_html=True)

# =============================================================================
# PLOT-FUNKSJONER — alle bruker #0d1117 bakgrunn
# =============================================================================

DARK = '#0d1117'
SURFACE = '#161b22'
GRID = '#21262d'
MUTED = '#8b949e'
TEXT = '#c9d1d9'

def _base_layout(fig, height=340, title=''):
    fig.update_layout(
        paper_bgcolor=DARK, plot_bgcolor=SURFACE,
        height=height,
        margin=dict(l=10, r=10, t=36 if title else 14, b=10),
        title=dict(text=title, font=dict(color=TEXT, size=13), x=0.01)
            if title else {},
        font=dict(color=TEXT, size=11),
        xaxis=dict(gridcolor=GRID, zeroline=False,
                   tickfont=dict(color=MUTED, size=10)),
        yaxis=dict(gridcolor=GRID, zeroline=False,
                   tickfont=dict(color=MUTED, size=10)),
        hovermode='x unified',
        showlegend=True,
        legend=dict(bgcolor='rgba(0,0,0,0)', font=dict(color=MUTED, size=11)),
    )
    return fig

# ── Wyckoff-syklus-diagram ───────────────────────────────────────────────────
def plot_wyckoff_syklus():
    """Tegner den klassiske Wyckoff-akkumulerings- og distribusjons-kurven."""
    np.random.seed(42)
    n = 280

    # Bygg kurven manuelt for å matche Wyckoff-fasene nøyaktig
    def s(start, end, pts, noise=0.0):
        base = np.linspace(start, end, pts)
        return base + np.random.randn(pts) * noise

    # Fase A: Selling Climax + Automatic Rally (bunn etableres)
    fase_a = np.concatenate([
        s(100, 62, 20, 1.8),   # Sharp decline (SC)
        s(62, 80, 12, 1.2),    # Automatic Rally (AR)
        s(80, 65, 10, 1.0),    # Secondary Test (ST)
    ])
    # Fase B: Trading range, bygger årsak
    fase_b = np.concatenate([
        s(65, 78, 18, 2.0),
        s(78, 63, 12, 1.5),
        s(63, 76, 14, 1.8),
        s(76, 67, 10, 1.2),
    ])
    # Fase C: Spring / Shakeout
    fase_c = np.concatenate([
        s(67, 58, 8, 1.0),     # Spring under support
        s(58, 74, 10, 0.8),    # Snap back
    ])
    # Fase D: Sign of Strength, Last Point of Support
    fase_d = np.concatenate([
        s(74, 88, 14, 1.2),    # SOS
        s(88, 82, 8, 0.8),     # LPS (BUTC)
        s(82, 96, 12, 1.0),    # Continuation
    ])
    # Fase E: Mark-up
    fase_e = np.concatenate([
        s(96, 118, 20, 1.5),
        s(118, 110, 8, 1.0),
        s(110, 138, 18, 2.0),
        s(138, 130, 6, 1.0),
        s(130, 155, 16, 1.8),
    ])
    # Distribusjon (topp)
    dist = np.concatenate([
        s(155, 162, 10, 2.0),
        s(162, 148, 8, 1.5),
        s(148, 158, 10, 2.0),
        s(158, 145, 12, 1.5),
        s(145, 152, 8, 1.5),
        s(152, 135, 10, 2.0),
    ])
    # Mark-down
    mdown = np.concatenate([
        s(135, 115, 14, 2.0),
        s(115, 120, 6, 1.0),
        s(120, 95, 12, 1.5),
    ])

    pris = np.concatenate([fase_a, fase_b, fase_c, fase_d, fase_e, dist, mdown])
    x = np.arange(len(pris))

    # Grensepunkter
    lA = len(fase_a)
    lB = lA + len(fase_b)
    lC = lB + len(fase_c)
    lD = lC + len(fase_d)
    lE = lD + len(fase_e)
    lDist = lE + len(dist)

    fig = go.Figure()

    # Pris-kurve fargelagt per fase
    segmenter = [
        (0,   lA,    '#6e7681',  'Fase A'),
        (lA,  lB,    '#a371f7',  'Fase B'),
        (lB,  lC,    '#3fb950',  'Fase C'),
        (lC,  lD,    '#388bfd',  'Fase D'),
        (lD,  lE,    '#388bfd',  'Mark-up'),
        (lE,  lDist, '#d29922',  'Distribusjon'),
        (lDist, len(pris), '#f85149', 'Mark-down'),
    ]

    for i, (start, end, farge, navn) in enumerate(segmenter):
        seg_x = x[start:end+1]
        seg_y = pris[start:end+1]
        fig.add_trace(go.Scatter(
            x=seg_x, y=seg_y,
            mode='lines',
            line=dict(color=farge, width=2.2),
            name=navn,
            showlegend=(navn not in ['Mark-up']),
            hoverinfo='skip',
        ))

    # Støtte- og motstandslinjer i trading range
    fig.add_shape(type='line', x0=lA, x1=lC+5,
                  y0=66, y1=66,
                  line=dict(color='#3fb95055', width=1, dash='dot'))
    fig.add_shape(type='line', x0=lA, x1=lC+5,
                  y0=80, y1=80,
                  line=dict(color='#f8514955', width=1, dash='dot'))

    # Pile og annotasjoner
    annotasjoner = [
        dict(x=lA//2,      y=58,  text='SC',   color='#6e7681'),
        dict(x=lA-5,       y=83,  text='AR',   color='#6e7681'),
        dict(x=lB-8,       y=57,  text='ST',   color='#a371f7'),
        dict(x=lB+lC//2-5, y=53,  text='Spring ↓', color='#3fb950'),
        dict(x=lC+5,       y=79,  text='SOS',  color='#388bfd'),
        dict(x=lD-5,       y=79,  text='LPS',  color='#388bfd'),
        dict(x=lE+10,      y=168, text='UTAD', color='#d29922'),
        dict(x=lDist+8,    y=125, text='SOW',  color='#f85149'),
    ]
    for a in annotasjoner:
        fig.add_annotation(
            x=a['x'], y=a['y'], text=f"<b>{a['text']}</b>",
            showarrow=False,
            font=dict(color=a['color'], size=10),
            bgcolor='#0d111788',
        )

    # Fargede bakgrunns-rektangler per fase
    fase_bg = [
        (0,    lA,    '#6e767108'),
        (lA,   lB,    '#a371f708'),
        (lB,   lC,    '#3fb95008'),
        (lC,   lD,    '#388bfd08'),
        (lD,   lE,    '#388bfd0a'),
        (lE,   lDist, '#d2992208'),
        (lDist,len(pris),'#f8514908'),
    ]
    for start, end, farge in fase_bg:
        fig.add_vrect(x0=start, x1=end, fillcolor=farge, line_width=0)

    fig.update_layout(
        paper_bgcolor=DARK, plot_bgcolor=SURFACE,
        height=360,
        margin=dict(l=10, r=10, t=10, b=10),
        xaxis=dict(showticklabels=False, gridcolor=GRID, zeroline=False),
        yaxis=dict(gridcolor=GRID, zeroline=False,
                   tickfont=dict(color=MUTED, size=10),
                   title=dict(text='Pris', font=dict(color=MUTED, size=10))),
        legend=dict(
            orientation='h', x=0, y=1.04,
            bgcolor='rgba(0,0,0,0)',
            font=dict(color=MUTED, size=10),
        ),
        hovermode=False,
    )
    return fig

# ── Absorpsjon vs Normal-dag ─────────────────────────────────────────────────
def plot_absorpsjon():
    """Illustrerer Effort vs Result — hjertet i VSA."""
    kategorier = ['Normal dag', 'Vol-thrust (bullish)', 'Absorpsjon', 'Distribution']
    volum      = [1.0,          2.4,                    2.8,          2.1]
    pris_chg   = [0.8,          2.1,                    0.2,         -1.6]
    farger_vol = ['#6e7681',    '#388bfd',              '#3fb950',    '#f85149']
    farger_pris= ['#6e7681',    '#3fb950',              '#3fb950',    '#f85149']

    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=['Volum (× gjennomsnitt)', 'Prisendring (%)'],
        horizontal_spacing=0.12,
    )

    fig.add_trace(go.Bar(
        x=kategorier, y=volum,
        marker_color=farger_vol,
        showlegend=False,
        text=[f'{v:.1f}×' for v in volum],
        textposition='outside',
        textfont=dict(color=TEXT, size=11),
    ), row=1, col=1)

    fig.add_trace(go.Bar(
        x=kategorier, y=pris_chg,
        marker_color=farger_pris,
        showlegend=False,
        text=[f'{v:+.1f}%' for v in pris_chg],
        textposition='outside',
        textfont=dict(color=TEXT, size=11),
    ), row=1, col=2)

    fig.update_layout(
        paper_bgcolor=DARK, plot_bgcolor=SURFACE,
        height=300,
        margin=dict(l=10, r=10, t=40, b=10),
        font=dict(color=TEXT, size=11),
    )
    for ax in ['xaxis','xaxis2']:
        fig.update_layout(**{ax: dict(
            gridcolor=GRID, tickfont=dict(color=MUTED, size=10),
        )})
    for ax in ['yaxis','yaxis2']:
        fig.update_layout(**{ax: dict(
            gridcolor=GRID, zeroline=True, zerolinecolor='#30363d',
            tickfont=dict(color=MUTED, size=10),
        )})
    for ann in fig.layout.annotations:
        ann.font.color = MUTED
        ann.font.size  = 12
    return fig

# ── OBV-divergens ────────────────────────────────────────────────────────────
def plot_obv_divergens():
    """Viser klassisk bullish OBV-divergens: OBV stiger mens pris er flat."""
    np.random.seed(7)
    n = 60
    x = np.arange(n)

    pris_base = 100 + np.cumsum(np.random.randn(n) * 0.4)
    pris_base[30:] += np.linspace(0, -3, 30)    # Pris flater / svak ned

    obv_base = np.cumsum(np.random.randn(n) * 200)
    obv_base[20:] += np.linspace(0, 4000, 40)   # OBV stiger stille

    fig = make_subplots(
        rows=2, cols=1, shared_xaxes=True,
        row_heights=[0.55, 0.45],
        vertical_spacing=0.04,
    )

    fig.add_trace(go.Scatter(
        x=x, y=pris_base,
        line=dict(color='#c9d1d9', width=2),
        name='Pris', showlegend=True,
        hovertemplate='Pris: %{y:.1f}<extra></extra>',
    ), row=1, col=1)

    # Divergens-annotasjon: trend-linje på pris
    fig.add_shape(type='line',
        x0=28, x1=59, y0=pris_base[28], y1=pris_base[-1],
        line=dict(color='#f8514977', width=1.5, dash='dot'), row=1, col=1)

    fig.add_trace(go.Scatter(
        x=x, y=obv_base,
        line=dict(color='#a371f7', width=2),
        fill='tozeroy', fillcolor='rgba(163,113,247,0.07)',
        name='OBV', showlegend=True,
        hovertemplate='OBV: %{y:,.0f}<extra></extra>',
    ), row=2, col=1)

    # OBV stigende trend-linje
    fig.add_shape(type='line',
        x0=20, x1=59, y0=obv_base[20], y1=obv_base[-1],
        line=dict(color='#3fb95077', width=1.5, dash='dot'), row=2, col=1)

    # Divergens-label
    fig.add_annotation(
        x=52, y=pris_base[-1]+1.5,
        text='Pris svak', showarrow=False,
        font=dict(color='#f85149', size=10),
    )
    fig.add_annotation(
        x=52, y=obv_base[-1]-1200,
        text='OBV stiger', showarrow=False,
        font=dict(color='#3fb950', size=10),
        row=2, col=1, xref='x2', yref='y2',
    )

    fig.update_layout(
        paper_bgcolor=DARK, plot_bgcolor=SURFACE,
        height=320,
        margin=dict(l=10, r=10, t=14, b=10),
        legend=dict(bgcolor='rgba(0,0,0,0)', font=dict(color=MUTED, size=11)),
        font=dict(color=TEXT, size=11),
        hovermode='x unified',
    )
    for ax in ['xaxis','xaxis2']:
        fig.update_layout(**{ax: dict(
            gridcolor=GRID, zeroline=False,
            showticklabels=False,
            tickfont=dict(color=MUTED),
        )})
    for ax in ['yaxis','yaxis2']:
        fig.update_layout(**{ax: dict(
            gridcolor=GRID, zeroline=False,
            tickfont=dict(color=MUTED, size=10),
        )})
    return fig

# ── Smart Money Score forklaring ─────────────────────────────────────────────
def plot_sms_radar():
    """Doughnut-chart som viser vektingen i Smart Money Score."""
    komponenter = ['Relativ styrke<br>(25%)', 'VSA Score<br>(30%)',
                   'Wyckoff CM<br>(30%)', 'OBV Trend<br>(15%)']
    verdier = [25, 30, 30, 15]
    farger  = ['#388bfd', '#3fb950', '#a371f7', '#d29922']

    fig = go.Figure(go.Pie(
        labels=komponenter,
        values=verdier,
        hole=0.60,
        marker=dict(colors=farger,
                    line=dict(color=DARK, width=2)),
        textfont=dict(color=TEXT, size=11),
        textposition='outside',
        hovertemplate='%{label}: %{value}%<extra></extra>',
    ))

    fig.add_annotation(
        text='<b>SMS</b><br>0 – 100',
        x=0.5, y=0.5, showarrow=False,
        font=dict(color=TEXT, size=13),
    )

    fig.update_layout(
        paper_bgcolor=DARK,
        height=280,
        margin=dict(l=10, r=10, t=10, b=10),
        legend=dict(bgcolor='rgba(0,0,0,0)', font=dict(color=MUTED, size=11),
                    orientation='v', x=1.0),
        showlegend=True,
    )
    return fig

# ── Relativ styrke illustrasjon ───────────────────────────────────────────────
def plot_rs_illustrasjon():
    """Viser RS-konseptet: to aksjer mot SPY over tid."""
    np.random.seed(21)
    n = 90
    x = np.arange(n)

    spy   = 100 + np.cumsum(np.random.randn(n) * 0.5)
    sterk = spy + np.linspace(0, 18, n) + np.cumsum(np.random.randn(n) * 0.3)
    svak  = spy - np.linspace(0, 12, n) + np.cumsum(np.random.randn(n) * 0.3)

    # Normaliser til 100
    sterk = sterk / sterk[0] * 100
    svak  = svak  / svak[0]  * 100
    spy_n = spy   / spy[0]   * 100

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=x, y=sterk,
        name='Sterk aksje (akkumulering)',
        line=dict(color='#3fb950', width=2),
        hovertemplate='%{y:.1f}<extra></extra>',
    ))
    fig.add_trace(go.Scatter(
        x=x, y=spy_n,
        name='SPY (benchmark)',
        line=dict(color='#6e7681', width=1.5, dash='dot'),
        hovertemplate='SPY: %{y:.1f}<extra></extra>',
    ))
    fig.add_trace(go.Scatter(
        x=x, y=svak,
        name='Svak aksje (distribusjon)',
        line=dict(color='#f85149', width=2),
        hovertemplate='%{y:.1f}<extra></extra>',
    ))

    fig.add_annotation(
        x=88, y=sterk[-1]+2,
        text=f'+{sterk[-1]-100:.0f}%',
        showarrow=False,
        font=dict(color='#3fb950', size=11, family='monospace'),
    )
    fig.add_annotation(
        x=88, y=svak[-1]-3,
        text=f'{svak[-1]-100:.0f}%',
        showarrow=False,
        font=dict(color='#f85149', size=11, family='monospace'),
    )

    return _base_layout(fig, height=300)

# =============================================================================
# LAYOUT — FORSIDE
# =============================================================================

# ── HERO ──────────────────────────────────────────────────────────────────────
st.markdown("""
<div style='padding: 2.5rem 0 1.5rem;'>
  <div style='display:flex; align-items:center; gap:14px; margin-bottom:10px;'>
    <span style='font-size:36px;'>🐋</span>
    <h1 style='margin:0; font-size:30px !important; color:#e6edf3 !important;'>
      Smart Money Dashboard
    </h1>
  </div>
  <p style='color:#8b949e; font-size:15px; max-width:700px; line-height:1.7; margin:0;'>
    Et forskningsverktøy for å identifisere <b style='color:#c9d1d9;'>institusjonell aktivitet</b>
    i aksjemarkedet — inspirert av Wyckoff-teori og Volume Spread Analysis.
    Denne guiden forklarer metodikken og hvordan du tolker resultatene.
  </p>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# ── NAVIGASJONS-TABS ──────────────────────────────────────────────────────────
tab_intro, tab_wyckoff, tab_vsa, tab_rs, tab_sms, tab_bruk = st.tabs([
    "🧭 Kom i gang",
    "📐 Wyckoff-teori",
    "📊 VSA — Volum",
    "📈 Relativ styrke",
    "🎯 Smart Money Score",
    "🖥 Brukerveiledning",
])

# ─────────────────────────────────────────────────────────────────────────────
# TAB 1: KOM I GANG
# ─────────────────────────────────────────────────────────────────────────────
with tab_intro:
    col1, col2 = st.columns([3, 2], gap='large')

    with col1:
        st.markdown("## Hva er Smart Money?")
        st.markdown("""
        <p style='color:#8b949e; font-size:14px; line-height:1.75;'>
        «Smart Money» refererer til institusjonelle aktører — pensjonsfond, hedgefond,
        forsikringsselskaper og market makers — som forvalter så store summer at de
        ikke kan kjøpe og selge uten å etterlate seg spor i markedsdata.
        </p>
        <p style='color:#8b949e; font-size:14px; line-height:1.75;'>
        Dette dashboardet analyserer <b style='color:#c9d1d9;'>pris, volum og relativ
        styrke</b> for å identifisere disse sporene — før retail-investorer (og finansmediene)
        oppdager dem.
        </p>
        """, unsafe_allow_html=True)

        st.markdown("### Trelagsanalysen")
        st.markdown("""
        <p style='color:#8b949e; font-size:13px; margin-bottom:14px;'>
        Dashboardet analyserer markedet i tre lag — fra makro til mikro:
        </p>
        """, unsafe_allow_html=True)

        lag = [
            ("Lag 1 — Sektor",     "Modul 1",
             "Hvilke sektorer leder markedet? Her strømmer kapital inn.",
             "#388bfd"),
            ("Lag 2 — Aksje",      "Modul 2",
             "Hvilke enkeltaksjer i vinner-sektoren viser absorpsjons-signaler?",
             "#a371f7"),
            ("Lag 3 — Fase",       "Modul 3",
             "Hvilken Wyckoff-fase er aksjen i? Finn riktig entry-punkt.",
             "#3fb950"),
        ]
        for tittel, modul, beskr, farge in lag:
            st.markdown(f"""
            <div style='display:flex; gap:14px; align-items:flex-start;
                        padding:12px 0; border-bottom:1px solid #21262d;'>
              <div style='min-width:80px; padding:4px 10px; border-radius:20px;
                           background:{farge}18; border:1px solid {farge}44;
                           text-align:center; font-size:11px; color:{farge};
                           font-weight:500; margin-top:2px;'>
                {modul}
              </div>
              <div>
                <div style='font-size:14px; font-weight:500; color:#c9d1d9;
                             margin-bottom:3px;'>{tittel}</div>
                <div style='font-size:13px; color:#8b949e;'>{beskr}</div>
              </div>
            </div>
            """, unsafe_allow_html=True)

    with col2:
        st.markdown("### Arbeidsflyt")
        steg = [
            ("Åpne dashboardet",
             "Naviger til dashboardet via sidemenyen til venstre.",
             "#388bfd"),
            ("Velg tidsperiode",
             "1M for kortsiktige signaler, 3–6M for swing-trading.",
             "#a371f7"),
            ("Les sektor-varmekartet",
             "Identifiser de grønneste sektorene over alle tre perioder.",
             "#3fb950"),
            ("Kjør drill-down",
             "Velg vinner-sektor i sidebaren og trykk 'Oppdater analyse'.",
             "#d29922"),
            ("Sorter på Smart Money",
             "Høyest score = sterkest institusjonell interesse.",
             "#388bfd"),
            ("Sjekk VSA-chart",
             "Bekreft med candlestick-chart og volum-signaler.",
             "#3fb950"),
        ]
        for i, (tittel, beskr, farge) in enumerate(steg, 1):
            st.markdown(f"""
            <div style='display:flex; gap:12px; align-items:flex-start;
                        padding:10px 0; border-bottom:1px solid #21262d;'>
              <div style='min-width:26px; height:26px; border-radius:50%;
                           background:#21262d; border:1px solid {farge}55;
                           display:flex; align-items:center; justify-content:center;
                           color:{farge}; font-size:12px; font-weight:500;
                           flex-shrink:0; margin-top:1px;'>{i}</div>
              <div>
                <div style='font-size:13px; font-weight:500; color:#c9d1d9;
                             margin-bottom:2px;'>{tittel}</div>
                <div style='font-size:12px; color:#8b949e;'>{beskr}</div>
              </div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("""
    <div style='background:#161b22; border:1px solid #d2992244;
                border-radius:8px; padding:14px 18px;'>
      <span style='color:#d29922; font-size:12px; font-weight:500;'>⚠ VIKTIG ANSVARSFRASKRIVELSE</span><br>
      <span style='color:#8b949e; font-size:12px; line-height:1.65;'>
      Dette dashboardet er et <b style='color:#c9d1d9;'>forsknings- og opplæringsverktøy</b>,
      ikke finansiell rådgivning. All handel innebærer risiko. Data fra Yahoo Finance kan
      ha forsinkelser og mangler. Gjør alltid din egen analyse (DYOR) og konsulter en
      lisensiert finansrådgiver før du tar investeringsbeslutninger.
      </span>
    </div>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# TAB 2: WYCKOFF
# ─────────────────────────────────────────────────────────────────────────────
with tab_wyckoff:
    st.markdown("## Wyckoff-metoden")
    st.markdown("""
    <p style='color:#8b949e; font-size:14px; line-height:1.75; max-width:780px;'>
    Richard D. Wyckoff (1873–1934) var en av de første til å systematisere studiet av
    markedsstruktur. Hans kjerne-innsikt: alle prisbevegelser er resultatet av
    <b style='color:#c9d1d9;'>kampen mellom supply (tilbud) og demand (etterspørsel)</b>,
    og denne kampen etterlater seg avlesbare spor i pris og volum.
    Han personifiserte institusjonene som én aktør — <b style='color:#c9d1d9;'>Composite Man (CM)</b>.
    </p>
    """, unsafe_allow_html=True)

    st.markdown("### Den fullstendige markedssyklusen")
    st.plotly_chart(plot_wyckoff_syklus(), use_container_width=True,
                    config={'displayModeBar': False})

    st.markdown("### Akkumuleringens fem faser")
    faser = [
        ("Fase A", "Stopp av nedturen",
         "Selling Climax (SC): massivt salgsvolum stopper nedgangen brått. "
         "Automatic Rally (AR): prisen spretter opp fra SC. Secondary Test (ST): prisen "
         "returnerer mot SC-nivå på lavere volum — bekrefter at supply er avtagende.",
         "#6e7681"),
        ("Fase B", "Bygger årsaken",
         "Composite Man akkumulerer stille over uker og måneder. Prisen oscillerer "
         "mellom support (SC-nivå) og resistance (AR-nivå). Volum-karakteren endres: "
         "høyt volum på oppturene, lavt på nedturene. Retail-investorer frustreres og selger.",
         "#a371f7"),
        ("Fase C", "Spring / Shakeout",
         "CM tester siste rest av supply ved å dytte prisen kortvarig UNDER support — "
         "trigger stop-losses og overbeviserer shorts. Men prisen snapper tilbake raskt. "
         "Dette er den BESTE entry-muligheten i hele syklusen.",
         "#3fb950"),
        ("Fase D", "Bekreftelse",
         "Sign of Strength (SOS): prisen bryter resistance på høyt volum. "
         "Last Point of Support (LPS) / Back-Up to the Creek (BUTC): siste pullback "
         "til gammel resistance (nå support). Entry nr. 2 for de som gikk glipp av Spring.",
         "#388bfd"),
        ("Fase E", "Mark-up",
         "CM holder posisjon og prisen stiger fritt. Retail-media begynner å omtale aksjen "
         "positivt. Volum er høyt på oppturer, lavt på konsolideringer. Syklusen "
         "avsluttes med en ny distribusjonsfase på toppen.",
         "#388bfd"),
    ]

    for fase, tittel, tekst, farge in faser:
        with st.expander(f"**{fase}** — {tittel}", expanded=(fase in ['Fase C','Fase D'])):
            st.markdown(f"""
            <div style='display:flex; gap:14px;'>
              <div style='width:3px; background:{farge}; border-radius:3px;
                           flex-shrink:0; margin:2px 0;'></div>
              <p style='color:#8b949e; font-size:13px; line-height:1.75; margin:0;'>
                {tekst}
              </p>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("### Nøkkelbegreper i dashboardet")
    begreper = [
        ("SC",   "Selling Climax",         "Enormt salgsvolum stopper nedgangen. Prisen lukker langt fra dagslav."),
        ("AR",   "Automatic Rally",        "Kjapt hopp etter SC. Definerer øvre grense for trading range."),
        ("ST",   "Secondary Test",         "Test av SC-nivå på LAVERE volum. Bekrefter at supply er tømt."),
        ("SOS",  "Sign of Strength",       "Breakout av trading range på HØYT volum. Demand dominerer."),
        ("LPS",  "Last Point of Support",  "Siste pullback etter SOS. Gammel resistance er ny support."),
        ("UTAD", "Upthrust After Dist.",   "Bearish: falsk breakout over topp på høyt volum, lukker under."),
        ("SOW",  "Sign of Weakness",       "Distribusjon bekreftet: breakdown av support på høyt volum."),
        ("BUTC", "Back-Up to the Creek",   "Pullback til brutt resistance-nivå. Sekundær entry-mulighet."),
    ]
    col_b1, col_b2 = st.columns(2)
    for i, (forkort, navn, forklaring) in enumerate(begreper):
        col = col_b1 if i % 2 == 0 else col_b2
        col.markdown(f"""
        <div class='concept-card'>
          <h4><span style='color:#388bfd; font-family:monospace;'>{forkort}</span>
              &nbsp;—&nbsp;{navn}</h4>
          <p>{forklaring}</p>
        </div>
        """, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# TAB 3: VSA
# ─────────────────────────────────────────────────────────────────────────────
with tab_vsa:
    st.markdown("## Volume Spread Analysis (VSA)")
    st.markdown("""
    <p style='color:#8b949e; font-size:14px; line-height:1.75; max-width:780px;'>
    VSA ble utviklet av Tom Williams basert på Wyckoffs arbeid. Kjerneprinsippet:
    <b style='color:#c9d1d9;'>sammenhengen mellom volum og prisspread avslører hvem som
    kontrollerer markedet</b>. Høyt volum betyr at store aktører er involvert —
    spørsmålet er om de kjøper eller selger.
    </p>
    """, unsafe_allow_html=True)

    st.markdown("### Effort vs. Result — grunnprinsippet")
    st.plotly_chart(plot_absorpsjon(), use_container_width=True,
                    config={'displayModeBar': False})

    st.markdown("""
    <div class='callout green'>
      <b style='color:#3fb950;'>Absorpsjon (det viktigste signalet):</b>
      Høyt volum + liten prisreaksjon. Composite Man kjøper ALT som tilbys
      uten å la prisen falle. Prisen «klistrer» fordi en stor kjøper absorberer supply.
    </div>
    <div class='callout' style='border-left-color:#388bfd;'>
      <b style='color:#388bfd;'>Volume Thrust:</b>
      Høyt volum + stor prisoppgang + lukker i øvre del av dagens range.
      Institusjoner kjøper aggressivt — dette er ikke skjult akkumulering,
      men åpen demand som overvelder supply.
    </div>
    <div class='callout yellow'>
      <b style='color:#d29922;'>Shakeout / Spring:</b>
      Enormt volum + pris faller intradag MEN lukker i midten av range.
      CM dytter prisen ned for å utløse stop-losses — og kjøper alt de får.
      Neste dag returnerer prisen over support.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### OBV — On-Balance Volume (den skjulte indikatoren)")
    col_obv1, col_obv2 = st.columns([3, 2], gap='large')
    with col_obv1:
        st.plotly_chart(plot_obv_divergens(), use_container_width=True,
                        config={'displayModeBar': False})
    with col_obv2:
        st.markdown("""
        <p style='color:#8b949e; font-size:13px; line-height:1.75; margin-top:1rem;'>
        OBV (On-Balance Volume) legger til volumet på opp-dager og trekker fra
        på ned-dager. Resultatet er et kumulativt mål på hvem som akkumulerer.
        </p>
        <p style='color:#8b949e; font-size:13px; line-height:1.75;'>
        <b style='color:#3fb950;'>Bullish divergens:</b> OBV stiger mens prisen
        er flat eller svakt ned. Dette er Composite Mans fingeravtrykk —
        han kan ikke skjule nettokjøpene sine i OBV-kurven.
        </p>
        <p style='color:#8b949e; font-size:13px; line-height:1.75;'>
        <b style='color:#f85149;'>Bearish divergens:</b> OBV faller mens prisen
        holder seg oppe. Distribusjons-signal — institusjoner selger til
        retail-kjøpere som tror trenden fortsetter.
        </p>
        """, unsafe_allow_html=True)

    st.markdown("### Slik leses VSA-chartet i dashboardet")
    signaler = [
        ("▲ Grønn pil under candle",    "#3fb950", "Absorpsjonsdag",
         "Volum > 1.8× snitt, prisendring < 0.8%. Se etter serier av disse dagene — det betyr at CM bygger en stor posisjon."),
        ("◆ Gul diamant over candle",   "#d29922", "Shakeout / Spring",
         "Volum > 2.5× snitt, pris faller men lukker i midten. Neste dags bekreftelse over support er kritisk."),
        ("Blå volumsøyle",              "#388bfd", "Volume Thrust",
         "Volum > 1.5× snitt, pris +0.8% eller mer, lukker i øvre 35% av range. Breakout-signal."),
        ("Lilla OBV-kurve (bunn-panel)","#a371f7", "On-Balance Volume",
         "Stigende OBV mens pris konsoliderer = skjult akkumulering. Avgjørende bekreftelse."),
    ]
    for sym, farge, navn, forklaring in signaler:
        st.markdown(f"""
        <div class='signal-row'>
          <div style='min-width:160px; font-family:monospace; font-size:12px;
                       color:{farge}; padding-top:2px;'>{sym}</div>
          <div>
            <div style='font-size:13px; font-weight:500; color:#c9d1d9;
                         margin-bottom:3px;'>{navn}</div>
            <div style='font-size:12px; color:#8b949e;'>{forklaring}</div>
          </div>
        </div>
        """, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# TAB 4: RELATIV STYRKE
# ─────────────────────────────────────────────────────────────────────────────
with tab_rs:
    st.markdown("## Relativ styrke — kapitalflyt-signalet")
    st.markdown("""
    <p style='color:#8b949e; font-size:14px; line-height:1.75; max-width:780px;'>
    Relativ styrke (RS) måler om en aksje eller sektor stiger <i>mer</i> eller <i>mindre</i>
    enn markedet (SPY). Det er det mest direkte målet på kapitalflyt:
    penger beveger seg inn i noe — og ut av noe annet.
    </p>
    """, unsafe_allow_html=True)

    col_rs1, col_rs2 = st.columns([3, 2], gap='large')
    with col_rs1:
        st.plotly_chart(plot_rs_illustrasjon(), use_container_width=True,
                        config={'displayModeBar': False})
    with col_rs2:
        st.markdown("""
        <div style='margin-top:0.5rem;'>
        <div class='callout green'>
          <b style='color:#3fb950;'>Positiv RS</b> betyr at aksjen stiger
          mer (eller faller mindre) enn SPY. Institusjonelle kjøper relativt til markedet.
        </div>
        <div class='callout red'>
          <b style='color:#f85149;'>Negativ RS</b> betyr at kapital strømmer ut av
          aksjen og inn i noe annet. Unngå eller short-kandidat.
        </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <p style='color:#8b949e; font-size:13px; line-height:1.75; margin-top:1rem;'>
        <b style='color:#c9d1d9;'>Cross-timeframe-regel:</b> En aksje som er sterk
        på 1M, 3M <i>og</i> 6M sender et mye sterkere signal enn en som bare er sterk
        denne uken. Vedvarende styrke = institusjonell overbevisning.
        </p>
        """, unsafe_allow_html=True)

    st.markdown("### Sektorrotasjon — 'The Smart Money Roadmap'")
    st.markdown("""
    <p style='color:#8b949e; font-size:14px; line-height:1.75; max-width:780px;'>
    Sam Stovall (S&P) dokumenterte at visse sektorer leder markedet i ulike faser
    av konjunktursyklusen. Sektorrotasjons-varmekartet (Modul 1) lar deg se dette mønsteret:
    </p>
    """, unsafe_allow_html=True)

    col_r1, col_r2, col_r3 = st.columns(3)
    syklus = [
        ("Tidlig bull", ["XLY — Forbruk", "XLK — Teknologi", "XLF — Finans"],
         "#3fb950", "Risiko-on. Vekst-sektorer leder."),
        ("Mid bull",    ["XLI — Industri", "XLB — Materialer", "XLE — Energi"],
         "#388bfd", "Sykliske sektorer tar over. Råvarer stiger."),
        ("Sen bull / Usikkerhet", ["XLV — Helse", "XLP — Dagligvare", "XLU — Utilities"],
         "#d29922", "Defensive sektorer styrkes. Smart money reduserer risiko."),
    ]
    for col, (fase, sekt, farge, beskr) in zip([col_r1, col_r2, col_r3], syklus):
        col.markdown(f"""
        <div style='background:#161b22; border:1px solid #30363d; border-radius:8px;
                     padding:14px; height:180px;'>
          <div style='font-size:12px; color:{farge}; font-weight:500;
                       margin-bottom:8px;'>{fase}</div>
          {''.join(f"<div style='font-size:12px; color:#c9d1d9; margin-bottom:4px;'>→ {s}</div>" for s in sekt)}
          <div style='font-size:11px; color:#6e7681; margin-top:8px;'>{beskr}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("""
    <div class='callout' style='margin-top:1rem;'>
      <b style='color:#c9d1d9;'>Praktisk bruk:</b> Bruk varmekartet til å finne sektorer
      med positiv RS over <i>alle tre</i> tidsperioder. Disse er dine universe for Modul 2-scanning.
      En sektor som er grønn på 6M men rød på 1M kan indikere at
      akkumuleringsperioden er over og distribusjon er i gang.
    </div>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# TAB 5: SMART MONEY SCORE
# ─────────────────────────────────────────────────────────────────────────────
with tab_sms:
    st.markdown("## Smart Money Score (SMS)")
    st.markdown("""
    <p style='color:#8b949e; font-size:14px; line-height:1.75; max-width:780px;'>
    SMS er dashboardets sammensatte rangerings-metrikk (0–100). Den kombinerer alle fire
    analysedimensjoner til ett tall — slik at du kan sortere og filtrere raskt
    uten å manuelt vurdere hver enkelt indikator.
    </p>
    """, unsafe_allow_html=True)

    col_sms1, col_sms2 = st.columns([2, 3], gap='large')
    with col_sms1:
        st.plotly_chart(plot_sms_radar(), use_container_width=True,
                        config={'displayModeBar': False})
    with col_sms2:
        komponenter = [
            ("Relativ styrke", "25%", "#388bfd",
             "Aksje vs SPY over valgt tidsperiode. Normalisert til 0–100."),
            ("VSA Score",      "30%", "#3fb950",
             "Absorpsjonsdager × 8 + Vol-thrust × 10 + Shakeout × 6 + OBV-bonus."),
            ("Wyckoff CM",     "30%", "#a371f7",
             "Composite Man confidence score. Spring + Spring = høyest mulig."),
            ("OBV Trend",      "15%", "#d29922",
             "Binær: stiger OBV over 20 dager? +15 poeng."),
        ]
        for navn, vekt, farge, beskr in komponenter:
            st.markdown(f"""
            <div style='display:flex; gap:12px; align-items:flex-start;
                        padding:10px 0; border-bottom:1px solid #21262d;'>
              <div style='min-width:50px; padding:3px 0; text-align:center;
                           font-size:15px; font-weight:500; color:{farge};
                           font-family:monospace; flex-shrink:0;'>{vekt}</div>
              <div>
                <div style='font-size:13px; font-weight:500; color:#c9d1d9;
                             margin-bottom:2px;'>{navn}</div>
                <div style='font-size:12px; color:#8b949e;'>{beskr}</div>
              </div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("### Tolkningstabel")
    tolkninger = [
        ("70 – 100", "🟢 Sterk institusjonell interesse",  "#3fb950",
         "Høy prioritet. Alle fire dimensjoner peker i riktig retning. Sjekk VSA-chart for entry-timing."),
        ("50 – 69",  "🟡 Moderat — avvent bekreftelse",    "#d29922",
         "Signaler er der, men ikke fullt bekreftet. Sett på watch-list og vent på Spring eller SOS."),
        ("0 – 49",   "🔴 Svak eller negativ",               "#f85149",
         "Unngå long-posisjoner. Kan være i distribusjon eller mark-down."),
    ]
    for score, label, farge, tekst in tolkninger:
        st.markdown(f"""
        <div style='display:flex; gap:14px; align-items:flex-start;
                    padding:12px 0; border-bottom:1px solid #21262d;'>
          <div style='min-width:90px; font-family:monospace; font-size:13px;
                       color:{farge}; font-weight:500; padding-top:2px;'>{score}</div>
          <div>
            <div style='font-size:13px; font-weight:500; color:#c9d1d9;
                         margin-bottom:3px;'>{label}</div>
            <div style='font-size:12px; color:#8b949e;'>{tekst}</div>
          </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("""
    <div class='callout yellow' style='margin-top:1rem;'>
      <b style='color:#d29922;'>Viktig:</b> SMS er et <i>screening</i>-verktøy, ikke et
      handelssignal i seg selv. En høy score betyr at aksjen fortjener grundigere analyse —
      ikke at du skal kjøpe uten å lese chart og forstå konteksten.
      Kombiner alltid med din egen vurdering av makro og sektortrend.
    </div>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# TAB 6: BRUKERVEILEDNING
# ─────────────────────────────────────────────────────────────────────────────
with tab_bruk:
    st.markdown("## Brukerveiledning")

    st.markdown("### Sidepanel (venstre)")
    sidebar_felter = [
        ("Analysehorisont",
         "Velg tidsperiode for alle beregninger. "
         "1M = kortsiktig momentum. 3–6M = swing-trading og trendbekreftelse. 1Y = langsiktig posisjonering."),
        ("Velg sektor",
         "Hvilken sektor-ETF du vil drill-down på. Bruk Modul 1-varmekartet til å velge den sterkeste sektoren."),
        ("Vis VSA-chart for",
         "Velg en enkeltaksje for å se candlestick-chart med VSA-markering i fane 3."),
        ("Oppdater analyse",
         "Henter fersk data fra Yahoo Finance og kjører full analyse. Data caches i 30 minutter for ytelse."),
        ("Tøm cache",
         "Tvinger ny datahenting umiddelbart. Bruk etter markedsstengetid for å få dagsoppdatering."),
    ]
    for felt, beskr in sidebar_felter:
        st.markdown(f"""
        <div class='concept-card' style='margin-bottom:8px;'>
          <h4>{felt}</h4>
          <p>{beskr}</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("### Fanene i dashboardet")
    faner = [
        ("🗺 Sektor-varmekart",
         "Heatmap over alle 11 S&P 500-sektorer mot SPY. Grønn = outperformer. "
         "Les alle tre kolonner (1M/3M/6M) — konsistent grønn = sterkest signal."),
        ("🔬 Drill-down scanner",
         "Boble-diagram + detaljert tabell over de 20 største komponentene i valgt sektor. "
         "Sorter på 'Smart Money'-kolonnen. Klikk kolonneoverskrift for re-sortering."),
        ("📊 VSA-chart",
         "Candlestick med volum-panel og OBV. ▲ = absorpsjon. ◆ = shakeout. "
         "Zoom med scroll, pan med drag. Bruk 'Modebar' øverst til høyre for fullskjerm."),
        ("📈 RS-tidslinje",
         "Kumulativ relativ styrke over tid for topp 5 aksjer vs SPY. "
         "Stiplet linje = sektor-ETF som referanse. Aksjer over stiplet linje = outperformer sektoren."),
    ]
    for fane, beskr in faner:
        st.markdown(f"""
        <div style='display:flex; gap:12px; padding:12px 0;
                    border-bottom:1px solid #21262d;'>
          <div style='font-size:13px; font-weight:500; color:#c9d1d9;
                       min-width:190px; flex-shrink:0;'>{fane}</div>
          <div style='font-size:13px; color:#8b949e;'>{beskr}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("### Anbefalte kolonner i tabellen")
    kolonner = [
        ("Smart Money",  "Sammensatt score 0–100. Primær sorteringskolonne."),
        ("Wyckoff Fase", "🌱 Spring = beste entry · 📈 Mark-up = bekreftelse · ⚠ Dist. = unngå."),
        ("RS vs SPY",    "Relativ styrke mot benchmark. Vil du ha > 0 (helst > +3%) for lang posisjon."),
        ("RS vs Sektor", "Outperformer aksjen sin egen sektor? Sterkeste hester i løpet."),
        ("Absorpsjon",   "Antall absorpsjonsdager (30d). Høyere = mer institusjonell aktivitet."),
        ("OBV Opp",      "✓ = OBV stigende. Kritisk bekreftelse. Unngå hvis OBV er fallende."),
        ("CM Score",     "Composite Man confidence (Wyckoff-spesifikk del). Over 70 = godt."),
    ]
    col_k1, col_k2 = st.columns(2)
    for i, (kol, beskr) in enumerate(kolonner):
        col = col_k1 if i % 2 == 0 else col_k2
        col.markdown(f"""
        <div style='padding:8px 0; border-bottom:1px solid #21262d;'>
          <span style='font-family:monospace; font-size:12px; color:#388bfd;'>{kol}</span>
          <span style='font-size:12px; color:#8b949e; margin-left:8px;'>{beskr}</span>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### Tekniske detaljer")
    col_t1, col_t2 = st.columns(2)
    with col_t1:
        st.markdown("""
        <div class='concept-card'>
          <h4>Datakilder og oppdatering</h4>
          <p>All data hentes fra Yahoo Finance via yfinance.
          Priser er «adjusted close» (justert for dividender og splits).
          Cache TTL er 30 minutter. Kjør om natten for mest fersk data.
          Yahoo Finance kan ha mangler for tynne aksjer.</p>
        </div>
        """, unsafe_allow_html=True)
    with col_t2:
        st.markdown("""
        <div class='concept-card'>
          <h4>Beregningsparametere</h4>
          <p>Volum-snitt: 20-dagers SMA. Absorpsjon-terskel: 1.8× snitt.
          Swing-nivåer: scipy argrelextrema med order=8–10.
          RS beregnes som total-avkastning aksje minus total-avkastning SPY.
          OBV-trend: 20-dagers SMA-slope.</p>
        </div>
        """, unsafe_allow_html=True)
