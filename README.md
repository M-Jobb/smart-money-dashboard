# 🐋 Smart Money Dashboard

Et forskningsverktøy for å identifisere institusjonell aktivitet i aksjemarkedet,
bygget på **Wyckoff-teori** og **Volume Spread Analysis (VSA)**.

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://streamlit.io)
![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)

---

## Hva gjør dette verktøyet?

Dashboardet analyserer S&P 500-sektorer og enkeltaksjer i tre lag:

| Modul | Funksjon | Metodikk |
|-------|----------|----------|
| **Modul 1** | Sektor-varmekart | Relativ styrke vs SPY over 1M / 3M / 6M |
| **Modul 2** | Whale Tracker | VSA — absorpsjon, vol-thrust, shakeout |
| **Modul 3** | Wyckoff-scanner | Fase-klassifisering + entry/stop-nivåer |

---

## Installasjon og kjøring

### Lokalt

```bash
git clone https://github.com/ditt-brukernavn/smart-money-dashboard
cd smart-money-dashboard

pip install -r requirements.txt

# Start appen (velg én av to metoder):

# Metode A — multi-page (anbefalt):
streamlit run smart_money_app.py

# Metode B — kun dashboardet:
streamlit run smart_money_dashboard.py
```

### Streamlit Cloud

1. Fork dette repoet til din GitHub-konto
2. Gå til [share.streamlit.io](https://share.streamlit.io)
3. Klikk **New app** → velg repoet ditt
4. **Main file path:** `smart_money_app.py`
5. Klikk **Deploy**

---

## Filstruktur

```
smart-money-dashboard/
├── smart_money_app.py          # Inngangspunkt for multi-page app
├── home.py                     # Forside — guide og metodikk
├── smart_money_dashboard.py    # Hoveddashboard
├── requirements.txt
└── README.md
```

---

## Avhengigheter

```
streamlit>=1.35.0
yfinance>=0.2.40
pandas>=2.0.0
pandas_ta>=0.3.14b
numpy>=1.24.0
plotly>=5.18.0
scipy>=1.11.0
```

---

## ⚠ Ansvarsfraskrivelse

Dette er et **forsknings- og opplæringsverktøy**, ikke finansiell rådgivning.
All handel innebærer risiko. Data fra Yahoo Finance kan ha forsinkelser og mangler.
Gjør alltid din egen analyse (DYOR) og konsulter en lisensiert finansrådgiver
før du tar investeringsbeslutninger.

---

## Metodikk

- **Wyckoff-metoden**: Richard D. Wyckoffs markedsstruktur-analyse (1910-1934)
- **VSA**: Volume Spread Analysis av Tom Williams
- **Sektorrotasjon**: Sam Stovalls konjunktursyklus-modell
- **Posisjonssizing**: Fixed fraction + Kelly Criterion
