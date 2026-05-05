import random
from datetime import date

import numpy as np
import streamlit as st

from components.header import render_header
from components.sidebar import render_sidebar
from styles.css import CSS_STYLES
from views.avancement import render_avancement
from views.budget import render_budget
from views.gantt_view import render_gantt
from views.global_ import render_global
from views.ressources import render_ressources
from views.risques import render_risques

st.set_page_config(
    page_title="Dashboard Budget – Projet Amazon",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(CSS_STYLES, unsafe_allow_html=True)

random.seed(42)
np.random.seed(42)

phase_key, theme, data = render_sidebar()
render_header(phase_key, data, theme)

if theme == "gantt":
    render_gantt()
elif theme == "global":
    render_global()
elif theme == "avancement":
    render_avancement(data)
elif theme == "budget":
    render_budget(data, phase_key)
elif theme == "ressources":
    render_ressources(data)
elif theme == "risques":
    render_risques(data)

st.markdown("---")
st.markdown(f"""
<div style="display:flex; justify-content:space-between; font-size:0.68rem; color:#3d4f6b;">
    <div>📦 Projet Amazon · Dashboard opérationnel · Sup de Vinci</div>
    <div>Données simulées · {date.today().strftime('%d/%m/%Y')}</div>
</div>
""", unsafe_allow_html=True)
