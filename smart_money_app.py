
# smart_money_app.py  — kjøres med:  streamlit run smart_money_app.py
#
# Sett opp multi-page app ved å legge filer i pages/-mappen.
# Streamlit velger rekkefølge basert på filnavn-prefix (1_, 2_, osv).

import streamlit as st

pg = st.navigation([
    st.Page("home.py",                    title="Guide & Metodikk",    icon="📖"),
    st.Page("smart_money_dashboard.py",   title="Smart Money Dashboard", icon="🐋"),
])
pg.run()
