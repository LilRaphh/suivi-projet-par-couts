import streamlit as st
from data.phases import PHASES, THEMES
from utils.formatting import fmt_eur, progress_bar


def render_sidebar():
    with st.sidebar:
        st.markdown("""
        <div class="sidebar-logo">
            <div class="sidebar-logo-title">📦 AMAZON</div>
            <div class="sidebar-logo-sub">Budget Dashboard</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("**THÈME**")
        theme_key = st.radio(
            "Thème",
            list(THEMES.keys()),
            label_visibility="collapsed",
        )
        theme = THEMES[theme_key]

        if theme in ("global", "gantt"):
            st.markdown("---")
            total_budget = sum(d["budget_total"] for d in PHASES.values())
            total_real   = sum(d["real_cost"]    for d in PHASES.values())
            total_tasks  = sum(d["tasks_done"]   for d in PHASES.values())
            pct_budget   = round(total_real / total_budget * 100, 1)
            st.markdown(f"""
            <div style="font-size:0.75rem; color:#64748b; line-height:2;">
                <div style="color:#94a3b8; font-weight:600; font-size:0.7rem; letter-spacing:0.1em; text-transform:uppercase; margin-bottom:0.5rem;">Synthèse projet</div>
                <div>💼 Budget total : <b style='color:#f0f4f8'>{fmt_eur(total_budget)}</b></div>
                <div>💸 Coût réel    : <b style='color:#f0f4f8'>{fmt_eur(total_real)}</b></div>
                <div>✅ Tâches réalisées : <b style='color:#f0f4f8'>{total_tasks}</b></div>
            </div>
            """, unsafe_allow_html=True)
            st.markdown(f"**Consommation globale · {pct_budget}%**")
            st.markdown(progress_bar(pct_budget, "#f97316", 6), unsafe_allow_html=True)
            phase_key = list(PHASES.keys())[0]
            data = PHASES[phase_key]
        else:
            st.markdown("<br>**PHASE**", unsafe_allow_html=True)
            phase_key = st.selectbox(
                "Phase",
                list(PHASES.keys()),
                label_visibility="collapsed",
            )
            data = PHASES[phase_key]
            pct_budget = round(data["real_cost"] / data["budget_total"] * 100, 1)

            st.markdown("---")
            st.markdown(f"""
            <div style="font-size:0.75rem; color:#64748b; line-height:2;">
                <div>📅 {data['date_range'][0]} → {data['date_range'][1]}</div>
                <div>💼 Budget total : <b style='color:#f0f4f8'>{fmt_eur(data['budget_total'])}</b></div>
                <div>👥 Budget RH    : <b style='color:#f0f4f8'>{fmt_eur(data['budget_rh'])}</b></div>
                <div>✅ Tâches       : <b style='color:#f0f4f8'>{data['tasks_done']}/{data['tasks_planned']}</b></div>
            </div>
            """, unsafe_allow_html=True)
            st.markdown(f"**Consommation budgétaire · {pct_budget}%**")
            st.markdown(progress_bar(pct_budget, "#f97316", 6), unsafe_allow_html=True)

    return phase_key, theme, data
