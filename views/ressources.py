import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots

from data.phases import MOOD_COLOR, MOOD_EMOJI, MOOD_LABEL, PLOTLY_LAYOUT
from utils.formatting import fmt_eur, kpi_card, progress_bar, section_title, stat_row


def render_ressources(d: dict) -> None:
    resources    = d["resources"]
    rh_consumed  = sum(r["consumed"] for r in resources.values())
    rh_budget    = d["budget_rh"]
    rh_rate      = round(rh_consumed / rh_budget * 100, 1)
    avg_mood     = round(sum(r["mood"] for r in resources.values()) / len(resources), 1)
    total_tasks  = sum(r["tasks"] for r in resources.values())
    most_loaded  = max(resources, key=lambda k: resources[k]["consumed"] / resources[k]["budget"])
    efficiency   = round(
        sum(r["tasks"] / (r["consumed"] / 1000) for r in resources.values()) / len(resources), 2
    )

    # ── KPI strip ─────────────────────────────────────────────────────────────
    st.markdown(section_title("👥 Ressources Humaines", "#a855f7"), unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        dtype = "neg" if rh_rate > 95 else ("pos" if rh_rate < 85 else "neu")
        st.markdown(kpi_card(
            "Consommation RH totale", f"{rh_rate}%",
            delta_text=f"{fmt_eur(rh_consumed)} / {fmt_eur(rh_budget)}",
            delta_type=dtype, accent="#a855f7",
            pct=rh_rate, sub="Budget ressources humaines",
        ), unsafe_allow_html=True)

    with c2:
        mood_emoji = MOOD_EMOJI[round(avg_mood)]
        mood_label = MOOD_LABEL[round(avg_mood)]
        mood_color = MOOD_COLOR[round(avg_mood)]
        st.markdown(kpi_card(
            "Météo équipe moyenne", f"{mood_emoji} {avg_mood}/5",
            delta_text=mood_label,
            delta_type="pos" if avg_mood >= 4 else ("neu" if avg_mood >= 3 else "neg"),
            accent=mood_color,
            pct=avg_mood / 5 * 100,
            sub=f"{len(resources)} collaborateurs évalués",
        ), unsafe_allow_html=True)

    with c3:
        st.markdown(kpi_card(
            "Tâches achevées (RH)", str(total_tasks),
            delta_text=f"{round(total_tasks / d['tasks_done'] * 100)}% coverage",
            delta_type="pos", accent="#14b8a6",
            sub=f"Moy. {round(total_tasks/len(resources),1)} tâches/ressource",
        ), unsafe_allow_html=True)

    with c4:
        st.markdown(kpi_card(
            "Efficacité équipe", f"{efficiency:.1f} t/k€",
            delta_text=f"Ressource clé : {most_loaded}",
            delta_type="neu", accent="#f59e0b",
            sub="Tâches par tranche de 1 000 €",
        ), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Cards par ressource ───────────────────────────────────────────────────
    st.markdown(section_title("Détail par collaborateur", "#a855f7"), unsafe_allow_html=True)
    cols = st.columns(len(resources))
    for i, (name, r) in enumerate(resources.items()):
        with cols[i]:
            rate  = round(r["consumed"] / r["budget"] * 100)
            dtype = "neg" if rate > 95 else ("pos" if rate < 80 else "neu")
            mood  = r["mood"]
            short = name.replace("Chef de Projet", "CDP")
            st.markdown(kpi_card(
                short, fmt_eur(r["consumed"]),
                delta_text=f"{MOOD_EMOJI[mood]} {MOOD_LABEL[mood]}",
                delta_type=dtype, accent=MOOD_COLOR[mood],
                pct=rate,
                sub=f"{rate}% consommé · {r['tasks']} tâches",
            ), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Charts ligne 1 ────────────────────────────────────────────────────────
    col_a, col_b = st.columns([3, 2])

    with col_a:
        st.markdown(section_title("Budget alloué vs consommé", "#a855f7"), unsafe_allow_html=True)
        names    = list(resources.keys())
        budgets  = [r["budget"]   for r in resources.values()]
        consumed = [r["consumed"] for r in resources.values()]
        rates    = [round(c / b * 100) for b, c in zip(budgets, consumed)]
        bar_colors = ["#22c55e" if r < 85 else "#f59e0b" if r < 95 else "#ef4444" for r in rates]

        fig6 = go.Figure()
        fig6.add_trace(go.Bar(
            name="Budget alloué", x=names, y=budgets,
            marker=dict(color="rgba(255,255,255,0.05)", line=dict(color="rgba(255,255,255,0.12)", width=1)),
        ))
        fig6.add_trace(go.Bar(
            name="Consommé", x=names, y=consumed,
            marker_color=bar_colors,
            opacity=0.85,
            text=[f"{r}%" for r in rates],
            textposition="outside",
            textfont=dict(color="#f0f4f8", size=11),
        ))
        fig6.update_layout(**PLOTLY_LAYOUT, barmode="overlay", height=300,
                           legend=dict(orientation="h", y=-0.22, font=dict(color="#64748b")))
        st.plotly_chart(fig6, use_container_width=True)

    with col_b:
        st.markdown(section_title("Météo des collaborateurs", "#f59e0b"), unsafe_allow_html=True)
        for name, r in resources.items():
            mood  = r["mood"]
            bar_w = mood / 5 * 100
            bar_c = MOOD_COLOR[mood]
            st.markdown(f"""
            <div style="margin-bottom:0.9rem;">
                <div style="display:flex; justify-content:space-between; margin-bottom:4px; font-size:0.82rem;">
                    <span style="color:#94a3b8;">{name}</span>
                    <span style="font-size:1rem;">{MOOD_EMOJI[mood]}</span>
                </div>
                {progress_bar(bar_w, bar_c, 6)}
                <div style="display:flex; justify-content:space-between; font-size:0.68rem; margin-top:2px;">
                    <span style="color:{bar_c};">{MOOD_LABEL[mood]}</span>
                    <span style="color:#3d4f6b;">{r['tasks']} tâches</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

    # ── Charts ligne 2 ────────────────────────────────────────────────────────
    col_c, col_d = st.columns([2, 1])

    with col_c:
        st.markdown(section_title("Tâches achevées & coût moyen par ressource", "#14b8a6"), unsafe_allow_html=True)
        names_r = list(resources.keys())
        tasks_r = [r["tasks"]    for r in resources.values()]
        costs_r = [r["consumed"] / r["tasks"] for r in resources.values()]

        fig7 = make_subplots(specs=[[{"secondary_y": True}]])
        fig7.add_trace(go.Bar(
            name="Tâches achevées", x=names_r, y=tasks_r,
            marker_color="#3b82f6", opacity=0.85,
        ), secondary_y=False)
        fig7.add_trace(go.Scatter(
            name="Coût moyen/tâche (€)", x=names_r, y=costs_r,
            mode="lines+markers",
            line=dict(color="#f59e0b", width=2.5),
            marker=dict(size=9, color="#f59e0b", line=dict(color="#07090e", width=2)),
        ), secondary_y=True)
        fig7.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font=dict(family="DM Sans", color="#64748b"),
            height=280, margin=dict(l=10, r=70, t=20, b=10),
            legend=dict(orientation="h", y=-0.28, font=dict(color="#64748b")),
        )
        fig7.update_yaxes(gridcolor="#1a2236", linecolor="#1a2236", secondary_y=False)
        fig7.update_yaxes(
            gridcolor="#1a2236", linecolor="#1a2236", secondary_y=True,
            title_text="€/tâche", title_font=dict(color="#f59e0b", size=11),
        )
        st.plotly_chart(fig7, use_container_width=True)

    with col_d:
        st.markdown(section_title("Synthèse RH", "#a855f7"), unsafe_allow_html=True)
        st.markdown(
            stat_row("Budget RH total", fmt_eur(rh_budget)) +
            stat_row("Consommé RH", fmt_eur(rh_consumed)) +
            stat_row("Taux RH", f"{rh_rate}%") +
            stat_row("Total tâches", str(total_tasks)) +
            stat_row("Efficacité", f"{efficiency:.1f} t/k€") +
            stat_row("Météo moy.", f"{MOOD_EMOJI[round(avg_mood)]} {avg_mood}/5") +
            stat_row("Ressource + chargée", most_loaded.split()[0]),
            unsafe_allow_html=True,
        )
