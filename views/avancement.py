import numpy as np
import plotly.graph_objects as go
import streamlit as st

from data.phases import PLOTLY_LAYOUT
from utils.formatting import fmt_eur, kpi_card, section_title, stat_row


def render_avancement(d: dict) -> None:
    pct_tasks    = round(d["tasks_done"] / d["tasks_planned"] * 100, 1)
    pct_on_time  = round(d["tasks_on_time"] / d["tasks_done"] * 100, 1)
    retard       = d["tasks_done"] - d["tasks_on_time"]
    velocite     = round(d["tasks_done"] / 8, 1)          # tâches/semaine sur 8 semaines
    projection   = round(d["tasks_planned"] / velocite, 1) if velocite > 0 else None

    # ── KPI strip ─────────────────────────────────────────────────────────────
    st.markdown(section_title("📊 Avancement des Tâches", "#3b82f6"), unsafe_allow_html=True)

    c1, c2, c3, c4, c5 = st.columns(5)

    with c1:
        dtype = "pos" if pct_tasks >= 75 else "neg"
        st.markdown(kpi_card(
            "Complétion globale", f"{pct_tasks}%",
            delta_text="Sur objectif (>75%)" if pct_tasks >= 75 else "En retard sur objectif",
            delta_type=dtype, accent="#3b82f6",
            pct=pct_tasks, sub=f"{d['tasks_done']} / {d['tasks_planned']} tâches",
        ), unsafe_allow_html=True)

    with c2:
        dd   = d["days_delta"]
        sign = "+" if dd > 0 else ""
        dtype = "neg" if dd > 0 else ("pos" if dd < 0 else "neu")
        label = f"{'⚠️ Retard' if dd > 0 else '✅ Avance'} de {abs(dd)} j"
        st.markdown(kpi_card(
            "Écart calendaire", f"{sign}{dd} j",
            delta_text=label, delta_type=dtype,
            accent="#ef4444" if dd > 0 else "#22c55e",
            sub="vs planning initial",
        ), unsafe_allow_html=True)

    with c3:
        dtype = "pos" if pct_on_time >= 85 else ("neu" if pct_on_time >= 70 else "neg")
        st.markdown(kpi_card(
            "Taux de ponctualité", f"{pct_on_time}%",
            delta_text=f"{retard} tâche(s) en retard" if retard else "Toutes à l'heure",
            delta_type=dtype, accent="#22c55e",
            pct=pct_on_time, sub=f"{d['tasks_on_time']} dans les délais",
        ), unsafe_allow_html=True)

    with c4:
        st.markdown(kpi_card(
            "Vélocité", f"{velocite} t/sem",
            delta_text="Tâches réalisées / semaine",
            delta_type="neu", accent="#f97316",
            sub="Sur les 8 dernières semaines",
        ), unsafe_allow_html=True)

    with c5:
        proj_txt = f"{projection} sem. estimées" if projection else "N/A"
        dtype = "pos" if projection and projection <= 10 else "neg"
        st.markdown(kpi_card(
            "Projection fin", proj_txt,
            delta_text="Au rythme actuel",
            delta_type=dtype, accent="#a855f7",
            sub=f"Reste {d['tasks_planned'] - d['tasks_done']} tâches",
        ), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Charts ligne 1 ────────────────────────────────────────────────────────
    col_a, col_b = st.columns([1, 1])

    with col_a:
        st.markdown(section_title("Progression des tâches", "#3b82f6"), unsafe_allow_html=True)
        categories = ["Planifiées", "Terminées", "Dans les délais", "En retard"]
        values     = [d["tasks_planned"], d["tasks_done"], d["tasks_on_time"], retard]
        colors     = ["#334155", "#3b82f6", "#22c55e", "#ef4444"]
        pcts       = [100, pct_tasks, pct_on_time, round(retard / d["tasks_done"] * 100, 1)]

        fig = go.Figure(go.Bar(
            x=categories, y=values,
            marker=dict(
                color=colors,
                line=dict(color="rgba(255,255,255,0.08)", width=1),
            ),
            text=[f"{v}<br><span style='font-size:10px'>{p}%</span>" for v, p in zip(values, pcts)],
            textposition="outside",
            textfont=dict(color="#f0f4f8", size=11),
        ))
        fig.update_layout(**PLOTLY_LAYOUT, height=300, showlegend=False, bargap=0.35)
        st.plotly_chart(fig, use_container_width=True)

    with col_b:
        st.markdown(section_title("Courbe d'avancement cumulée", "#3b82f6"), unsafe_allow_html=True)
        weeks = 8
        cumulative_planned = np.linspace(0, d["tasks_planned"], weeks).round()
        cumulative_done    = np.clip(
            cumulative_planned + np.cumsum(np.random.randint(-2, 3, weeks)),
            0, d["tasks_planned"],
        ).round()
        cumulative_done[-1] = d["tasks_done"]

        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(
            x=list(range(1, weeks + 1)), y=cumulative_planned,
            name="Planifiées", line=dict(color="#334155", dash="dot", width=2),
        ))
        fig2.add_trace(go.Scatter(
            x=list(range(1, weeks + 1)), y=cumulative_done,
            name="Réalisées", line=dict(color="#3b82f6", width=2.5),
            fill="tonexty", fillcolor="rgba(59,130,246,0.07)",
        ))
        fig2.update_layout(**PLOTLY_LAYOUT, height=300,
                           legend=dict(orientation="h", y=-0.18, font=dict(color="#64748b")),
                           xaxis_title="Semaine")
        st.plotly_chart(fig2, use_container_width=True)

    # ── Charts ligne 2 ────────────────────────────────────────────────────────
    col_c, col_d = st.columns([2, 1])

    with col_c:
        st.markdown(section_title("Jauge d'avancement vs objectif 75%", "#3b82f6"), unsafe_allow_html=True)
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=pct_tasks,
            delta={"reference": 75, "suffix": "%", "increasing": {"color": "#22c55e"}, "decreasing": {"color": "#ef4444"}},
            title={"text": "% tâches complétées", "font": {"color": "#64748b", "size": 13}},
            number={"suffix": "%", "font": {"color": "#f0f4f8", "size": 44, "family": "Syne"}},
            gauge={
                "axis": {"range": [0, 100], "tickcolor": "#1a2236", "tickwidth": 1},
                "bar": {"color": "#3b82f6", "thickness": 0.25},
                "bgcolor": "rgba(0,0,0,0)",
                "bordercolor": "rgba(0,0,0,0)",
                "steps": [
                    {"range": [0, 50],  "color": "rgba(59,130,246,0.05)"},
                    {"range": [50, 75], "color": "rgba(59,130,246,0.08)"},
                    {"range": [75, 100],"color": "rgba(34,197,94,0.06)"},
                ],
                "threshold": {"line": {"color": "#22c55e", "width": 3}, "thickness": 0.75, "value": 75},
            },
        ))
        fig_gauge.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", height=220,
            font=dict(family="DM Sans", color="#64748b"),
            margin=dict(l=30, r=30, t=20, b=0),
        )
        st.plotly_chart(fig_gauge, use_container_width=True)

    with col_d:
        st.markdown(section_title("Détail tâches", "#22c55e"), unsafe_allow_html=True)
        st.markdown(
            stat_row("Planifiées", str(d["tasks_planned"])) +
            stat_row("Terminées", str(d["tasks_done"])) +
            stat_row("Dans les délais", str(d["tasks_on_time"])) +
            stat_row("En retard", str(retard)) +
            stat_row("Restantes", str(d["tasks_planned"] - d["tasks_done"])) +
            stat_row("Vélocité", f"{velocite} t/sem") +
            stat_row("Décalage", f"{'+' if d['days_delta']>0 else ''}{d['days_delta']} j"),
            unsafe_allow_html=True,
        )
