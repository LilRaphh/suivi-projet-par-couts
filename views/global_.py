import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots

from data.phases import PHASE_COLORS, PHASES, PLOTLY_LAYOUT
from utils.formatting import fmt_eur, kpi_card, progress_bar, section_title, stat_row


def _hex_rgba(hex_color: str, alpha: float = 0.10) -> str:
    h = hex_color.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return f"rgba({r},{g},{b},{alpha})"


# ── Helpers ──────────────────────────────────────────────────────────────────

def _health_score(d: dict) -> float:
    budget_score   = max(0, (1 - d["real_cost"] / d["budget_total"])) * 40 + 30
    schedule_score = (d["tasks_on_time"] / d["tasks_done"]) * 35
    completion_score = (d["tasks_done"] / d["tasks_planned"]) * 25
    return round(min(budget_score + schedule_score + completion_score, 100), 1)


def _global_stats():
    total_budget   = sum(d["budget_total"]   for d in PHASES.values())
    total_real     = sum(d["real_cost"]       for d in PHASES.values())
    total_unplanned= sum(d["unplanned_costs"] for d in PHASES.values())
    total_planned  = sum(d["tasks_planned"]   for d in PHASES.values())
    total_done     = sum(d["tasks_done"]      for d in PHASES.values())
    total_on_time  = sum(d["tasks_on_time"]   for d in PHASES.values())
    rh_total_budget  = sum(d["budget_rh"] for d in PHASES.values())
    rh_total_consumed= sum(
        sum(r["consumed"] for r in d["resources"].values()) for d in PHASES.values()
    )
    health = round(sum(_health_score(d) for d in PHASES.values()) / len(PHASES), 1)
    return {
        "total_budget":    total_budget,
        "total_real":      total_real,
        "total_unplanned": total_unplanned,
        "total_planned":   total_planned,
        "total_done":      total_done,
        "total_on_time":   total_on_time,
        "rh_budget":       rh_total_budget,
        "rh_consumed":     rh_total_consumed,
        "savings":         total_budget - total_real,
        "pct_budget":      round(total_real / total_budget * 100, 1),
        "pct_tasks":       round(total_done / total_planned * 100, 1),
        "pct_on_time":     round(total_on_time / total_done * 100, 1),
        "health":          health,
    }


# ── Main render ───────────────────────────────────────────────────────────────

def render_global() -> None:
    g = _global_stats()

    # ── KPI strip ────────────────────────────────────────────────────────────
    st.markdown(section_title("📊 Synthèse Projet", "#f97316"), unsafe_allow_html=True)

    c1, c2, c3, c4, c5 = st.columns(5)

    with c1:
        over = g["total_real"] > g["total_budget"]
        st.markdown(kpi_card(
            "Budget consommé", fmt_eur(g["total_real"]),
            delta_text=f"{'⚠️ Dépassement' if over else '✅ Économie'} {fmt_eur(abs(g['savings']))}",
            delta_type="neg" if over else "pos",
            accent="#f97316",
            pct=g["pct_budget"],
            sub=f"{g['pct_budget']}% du budget total",
        ), unsafe_allow_html=True)

    with c2:
        st.markdown(kpi_card(
            "Tâches réalisées", f"{g['total_done']}/{g['total_planned']}",
            delta_text=f"{g['pct_tasks']}% de complétion",
            delta_type="pos" if g["pct_tasks"] >= 75 else "neg",
            accent="#3b82f6",
            pct=g["pct_tasks"],
            sub=f"{g['total_planned'] - g['total_done']} tâches restantes",
        ), unsafe_allow_html=True)

    with c3:
        st.markdown(kpi_card(
            "Taux de ponctualité", f"{g['pct_on_time']}%",
            delta_text=f"{g['total_on_time']} tâches dans les délais",
            delta_type="pos" if g["pct_on_time"] >= 85 else "neu",
            accent="#22c55e",
            pct=g["pct_on_time"],
            sub=f"{g['total_done'] - g['total_on_time']} tâches en retard",
        ), unsafe_allow_html=True)

    with c4:
        rh_rate = round(g["rh_consumed"] / g["rh_budget"] * 100, 1)
        st.markdown(kpi_card(
            "Consommation RH", f"{rh_rate}%",
            delta_text=f"{fmt_eur(g['rh_consumed'])} / {fmt_eur(g['rh_budget'])}",
            delta_type="neg" if rh_rate > 95 else ("pos" if rh_rate < 85 else "neu"),
            accent="#a855f7",
            pct=rh_rate,
            sub=f"Coûts non planifiés : {fmt_eur(g['total_unplanned'])}",
        ), unsafe_allow_html=True)

    with c5:
        hcolor = "#22c55e" if g["health"] >= 80 else ("#f59e0b" if g["health"] >= 65 else "#ef4444")
        hlabel = "Excellent" if g["health"] >= 85 else ("Bon" if g["health"] >= 70 else "À risque")
        st.markdown(kpi_card(
            "Score de santé", f"{g['health']}/100",
            delta_text=hlabel,
            delta_type="pos" if g["health"] >= 80 else ("neu" if g["health"] >= 65 else "neg"),
            accent=hcolor,
            pct=g["health"],
            sub="Composite budget · planning · tâches",
        ), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Gantt timeline ────────────────────────────────────────────────────────
    col_gantt, col_health = st.columns([3, 1])

    with col_gantt:
        st.markdown(section_title("📅 Timeline du projet", "#3b82f6"), unsafe_allow_html=True)
        rows = []
        for name, d in PHASES.items():
            rows.append({
                "Phase":      name,
                "Start":      d["date_range"][0],
                "Fin":        d["date_range"][1],
                "Complétion": round(d["tasks_done"] / d["tasks_planned"] * 100),
                "Budget":     fmt_eur(d["budget_total"]),
            })
        df = pd.DataFrame(rows)
        fig_gantt = px.timeline(
            df, x_start="Start", x_end="Fin", y="Phase",
            color="Phase",
            color_discrete_map={n: c for n, c in PHASE_COLORS.items()},
            custom_data=["Complétion", "Budget"],
        )
        fig_gantt.update_traces(
            hovertemplate="<b>%{y}</b><br>%{x|%d %b %Y} → %{customdata[0]}% complété<br>Budget : %{customdata[1]}<extra></extra>",
            marker_line_width=0,
            opacity=0.85,
        )
        fig_gantt.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font=dict(family="DM Sans", color="#64748b"),
            height=200,
            margin=dict(l=10, r=10, t=10, b=10),
            showlegend=False,
            xaxis=dict(gridcolor="#1a2236", linecolor="#1a2236"),
            yaxis=dict(gridcolor="#1a2236", linecolor="#1a2236", autorange="reversed"),
        )
        st.plotly_chart(fig_gantt, use_container_width=True)

    with col_health:
        st.markdown(section_title("🏥 Santé par phase", "#22c55e"), unsafe_allow_html=True)
        for name, d in PHASES.items():
            score = _health_score(d)
            color = "#22c55e" if score >= 80 else ("#f59e0b" if score >= 65 else "#ef4444")
            short = name.split("–")[1].strip() if "–" in name else name
            st.markdown(f"""
            <div class="phase-row">
                <div class="phase-row-name">{d['emoji']} {short}</div>
                <div class="phase-row-bar">
                    <div class="phase-row-fill" style="width:{score}%; background:{color};"></div>
                </div>
                <div class="phase-row-pct">{score:.0f}</div>
            </div>
            """, unsafe_allow_html=True)

    # ── Budget + Tâches comparison ────────────────────────────────────────────
    col_a, col_b = st.columns(2)

    with col_a:
        st.markdown(section_title("💰 Budget prévu vs réel par phase", "#f97316"), unsafe_allow_html=True)
        phase_names  = list(PHASES.keys())
        short_names  = [n.split("–")[1].strip() if "–" in n else n for n in phase_names]
        budgets      = [PHASES[n]["budget_total"] for n in phase_names]
        reals        = [PHASES[n]["real_cost"]    for n in phase_names]
        colors_ph    = [PHASE_COLORS[n] for n in phase_names]

        fig_budget = go.Figure()
        fig_budget.add_trace(go.Bar(
            name="Budget prévu", x=short_names, y=budgets,
            marker_color="rgba(255,255,255,0.06)",
            marker_line_color="rgba(255,255,255,0.15)",
            marker_line_width=1,
            text=[fmt_eur(v) for v in budgets],
            textposition="outside",
            textfont=dict(size=10, color="#64748b"),
        ))
        fig_budget.add_trace(go.Bar(
            name="Coût réel", x=short_names, y=reals,
            marker_color=colors_ph,
            opacity=0.85,
            text=[fmt_eur(v) for v in reals],
            textposition="outside",
            textfont=dict(size=10, color="#f0f4f8"),
        ))
        fig_budget.update_layout(
            **PLOTLY_LAYOUT, barmode="overlay", height=280,
            legend=dict(orientation="h", y=-0.22, font=dict(color="#64748b")),
        )
        st.plotly_chart(fig_budget, use_container_width=True)

    with col_b:
        st.markdown(section_title("📊 Avancement par phase", "#3b82f6"), unsafe_allow_html=True)
        fig_tasks = go.Figure()
        for name in phase_names:
            d = PHASES[name]
            short = name.split("–")[1].strip() if "–" in name else name
            pct_done    = round(d["tasks_done"] / d["tasks_planned"] * 100)
            pct_ontime  = round(d["tasks_on_time"] / d["tasks_done"] * 100)
            col = PHASE_COLORS[name]
            fig_tasks.add_trace(go.Bar(
                name=f"{d['emoji']} {short} — Réalisées",
                y=[short],
                x=[pct_done],
                orientation="h",
                marker_color=col,
                opacity=0.85,
                text=[f"{pct_done}%"],
                textposition="inside",
                textfont=dict(color="#f0f4f8", size=11),
            ))
            fig_tasks.add_trace(go.Bar(
                name=f"{d['emoji']} {short} — Dans délais",
                y=[short],
                x=[pct_ontime - pct_done],
                orientation="h",
                marker_color=col,
                opacity=0.25,
                showlegend=False,
            ))
        fig_tasks.update_layout(
            **PLOTLY_LAYOUT, barmode="stack", height=280, showlegend=False,
        )
        fig_tasks.update_xaxes(range=[0, 110], ticksuffix="%")
        st.plotly_chart(fig_tasks, use_container_width=True)

    # ── Risques + Ressources globaux ──────────────────────────────────────────
    col_c, col_d = st.columns([1, 2])

    with col_c:
        st.markdown(section_title("⚠️ Risques consolidés", "#ef4444"), unsafe_allow_html=True)
        all_risks = {
            "Critiques": sum(1 for d in PHASES.values() for r in d["risks"] if r[1] == "high"),
            "Modérés":   sum(1 for d in PHASES.values() for r in d["risks"] if r[1] == "med"),
            "Faibles":   sum(1 for d in PHASES.values() for r in d["risks"] if r[1] == "low"),
        }
        total_risks = sum(all_risks.values())
        colors_risk = {"Critiques": "#ef4444", "Modérés": "#f59e0b", "Faibles": "#22c55e"}
        st.markdown(f"""
        <div style="font-size:0.75rem; color:#64748b; margin-bottom:0.8rem;">
            {total_risks} risques identifiés sur l'ensemble du projet
        </div>""", unsafe_allow_html=True)
        for label, count in all_risks.items():
            pct = round(count / total_risks * 100) if total_risks else 0
            col = colors_risk[label]
            st.markdown(f"""
            <div style="margin-bottom:0.8rem;">
                <div style="display:flex; justify-content:space-between; font-size:0.8rem; margin-bottom:3px;">
                    <span style="color:#94a3b8;">{label}</span>
                    <span style="color:#f0f4f8; font-weight:600; font-family:'Syne',sans-serif;">{count}</span>
                </div>
                {progress_bar(pct, col, 5)}
            </div>
            """, unsafe_allow_html=True)

        st.markdown(section_title("💡 Indicateurs clés", "#a855f7"), unsafe_allow_html=True)
        avg_cost_per_task = round(
            sum(d["real_cost"] for d in PHASES.values()) /
            sum(d["tasks_done"] for d in PHASES.values())
        )
        st.markdown(
            stat_row("Coût moyen / tâche", fmt_eur(avg_cost_per_task)) +
            stat_row("Coûts non planifiés", fmt_eur(g["total_unplanned"])) +
            stat_row("Économies réalisées", fmt_eur(g["savings"])) +
            stat_row("Durée projet", "9 mois"),
            unsafe_allow_html=True,
        )

    with col_d:
        st.markdown(section_title("👥 Consommation RH par phase", "#a855f7"), unsafe_allow_html=True)
        resource_names = list(next(iter(PHASES.values()))["resources"].keys())
        short_r = [r.replace("Chef de Projet", "CDP") for r in resource_names]
        phase_short = [n.split("–")[1].strip() if "–" in n else n for n in PHASES.keys()]
        rh_colors = ["#3b82f6", "#22c55e", "#a855f7", "#f59e0b", "#14b8a6"]

        fig_rh = go.Figure()
        for i, res in enumerate(resource_names):
            vals = [PHASES[pn]["resources"][res]["consumed"] for pn in PHASES]
            fig_rh.add_trace(go.Bar(
                name=short_r[i],
                x=phase_short,
                y=vals,
                marker_color=rh_colors[i],
                opacity=0.85,
            ))
        fig_rh.update_layout(
            **PLOTLY_LAYOUT, barmode="stack", height=280,
            legend=dict(orientation="h", y=-0.25, font=dict(color="#64748b"), traceorder="normal"),
        )
        st.plotly_chart(fig_rh, use_container_width=True)

    # ── Radar multi-phase ─────────────────────────────────────────────────────
    st.markdown(section_title("🕸️ Radar de performance multi-phase", "#14b8a6"), unsafe_allow_html=True)
    categories = ["Efficacité\nbudgétaire", "Taux de\ncomplétion", "Ponctualité", "Maîtrise\ndes risques", "Performance\nRH"]

    fig_radar = go.Figure()
    for name, d in PHASES.items():
        rh_consumed = sum(r["consumed"] for r in d["resources"].values())
        n_high = sum(1 for r in d["risks"] if r[1] == "high")
        vals = [
            min(round((1 - abs(d["real_cost"] - d["budget_total"]) / d["budget_total"]) * 100, 1), 100),
            round(d["tasks_done"] / d["tasks_planned"] * 100, 1),
            round(d["tasks_on_time"] / d["tasks_done"] * 100, 1),
            max(0, 100 - n_high * 25),
            min(round((1 - abs(rh_consumed - d["budget_rh"]) / d["budget_rh"]) * 100, 1), 100),
        ]
        vals_closed = vals + [vals[0]]
        cats_closed = categories + [categories[0]]
        short = name.split("–")[1].strip() if "–" in name else name
        fig_radar.add_trace(go.Scatterpolar(
            r=vals_closed,
            theta=cats_closed,
            fill="toself",
            name=f"{d['emoji']} {short}",
            line=dict(color=PHASE_COLORS[name], width=2),
            fillcolor=_hex_rgba(PHASE_COLORS[name], 0.10),
        ))
    fig_radar.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        polar=dict(
            bgcolor="rgba(0,0,0,0)",
            radialaxis=dict(visible=True, range=[0, 100], gridcolor="#1a2236", tickcolor="#64748b", tickfont=dict(size=9, color="#64748b")),
            angularaxis=dict(gridcolor="#1a2236", linecolor="#1a2236"),
        ),
        font=dict(family="DM Sans", color="#64748b"),
        height=380,
        margin=dict(l=60, r=60, t=20, b=20),
        legend=dict(orientation="h", y=-0.08, font=dict(color="#94a3b8")),
        showlegend=True,
    )
    st.plotly_chart(fig_radar, use_container_width=True)
