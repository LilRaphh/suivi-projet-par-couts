import streamlit as st

_THEME_LABELS = {
    "global":      ("🌍", "Vue Globale",         "pg"),
    "avancement":  ("📊", "Avancement",          None),
    "budget":      ("💰", "Suivi Budgétaire",    None),
    "ressources":  ("👥", "Ressources Humaines", None),
    "risques":     ("⚠️", "Risques & Alertes",   None),
}


def render_header(phase_key: str, data: dict, theme: str = "") -> None:
    col_h1, col_h2 = st.columns([3, 1])
    with col_h1:
        st.markdown("""
        <p class="dash-header">Dashboard <span>Budget</span></p>
        <p class="dash-sub">Projet Amazon · Sup de Vinci · Suivi opérationnel</p>
        """, unsafe_allow_html=True)
    with col_h2:
        if theme in ("global", "gantt"):
            badge_html = '<span class="phase-badge pg">🌍 Toutes les phases</span>'
            date_html  = '<div style="font-size:0.68rem; color:#64748b; margin-top:5px;">Jan 2024 → Oct 2024</div>'
        else:
            cls = data["label"]
            badge_html = f'<span class="phase-badge {cls}">{data["emoji"]} {phase_key}</span>'
            date_html  = f'<div style="font-size:0.68rem; color:#64748b; margin-top:5px;">{data["date_range"][0]} → {data["date_range"][1]}</div>'
        st.markdown(f"""
        <div style="text-align:right; padding-top:0.6rem;">
            {badge_html}
            {date_html}
        </div>
        """, unsafe_allow_html=True)
    st.markdown("---")
