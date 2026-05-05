import numpy as np
import plotly.graph_objects as go
import streamlit as st

from data.phases import PLOTLY_LAYOUT
from utils.formatting import fmt_eur, kpi_card, section_title, stat_row


def _evm(d: dict):
    """Compute basic Earned Value metrics."""
    completion = d["tasks_done"] / d["tasks_planned"]
    pv  = d["budget_total"] * completion   # Planned Value au niveau actuel
    ev  = d["budget_total"] * completion   # Earned Value (simplifié)
    ac  = d["real_cost"]
    cpi = round(ev / ac, 2)               # Cost Performance Index
    spi = round(d["tasks_done"] / d["tasks_planned"], 2)  # Schedule PI
    eac = round(d["budget_total"] / cpi) if cpi else d["budget_total"]   # Estimate at Completion
    vac = d["budget_total"] - eac          # Variance at Completion
    return {"pv": pv, "ev": ev, "ac": ac, "cpi": cpi, "spi": spi, "eac": eac, "vac": vac}


def render_budget(d: dict, phase_key: str) -> None:
    rh_consumed   = sum(r["consumed"] for r in d["resources"].values())
    rh_rate       = round(rh_consumed / d["budget_rh"] * 100, 1)
    avg_per_task  = round(d["real_cost"] / d["tasks_done"])
    budget_rate   = round(d["real_cost"] / d["budget_total"] * 100, 1)
    savings       = d["budget_total"] - d["real_cost"]
    evm           = _evm(d)

    # ── KPI strip ─────────────────────────────────────────────────────────────
    st.markdown(section_title("💰 Suivi Budgétaire", "#f97316"), unsafe_allow_html=True)

    c1, c2, c3, c4, c5 = st.columns(5)

    with c1:
        over  = d["real_cost"] > d["budget_total"]
        st.markdown(kpi_card(
            "Coût réel", fmt_eur(d["real_cost"]),
            delta_text=f"{'⚠️ +' if over else '✅ -'}{fmt_eur(abs(savings))} vs budget",
            delta_type="neg" if over else "pos",
            accent="#ef4444" if over else "#22c55e",
            pct=budget_rate,
            sub=f"{budget_rate}% du budget consommé",
        ), unsafe_allow_html=True)

    with c2:
        unp_rate = round(d["unplanned_costs"] / d["budget_total"] * 100, 1)
        dtype    = "neg" if unp_rate > 5 else "neu"
        st.markdown(kpi_card(
            "Coûts non planifiés", fmt_eur(d["unplanned_costs"]),
            delta_text=f"{'⚠️ ' if unp_rate > 5 else ''}{unp_rate}% du budget total",
            delta_type=dtype, accent="#fb923c",
            pct=unp_rate,
            sub="Seuil acceptable : <5%",
        ), unsafe_allow_html=True)

    with c3:
        dtype = "neg" if rh_rate > 95 else ("pos" if rh_rate < 85 else "neu")
        st.markdown(kpi_card(
            "Consommation RH", f"{rh_rate}%",
            delta_text=f"{fmt_eur(rh_consumed)} / {fmt_eur(d['budget_rh'])}",
            delta_type=dtype, accent="#a855f7",
            pct=rh_rate, sub="Budget ressources humaines",
        ), unsafe_allow_html=True)

    with c4:
        cpi_type = "pos" if evm["cpi"] >= 1 else "neg"
        st.markdown(kpi_card(
            "CPI (Cost Perf. Index)", f"{evm['cpi']:.2f}",
            delta_text="Sous budget" if evm["cpi"] >= 1 else "Sur budget",
            delta_type=cpi_type, accent="#14b8a6",
            sub=f"EAC estimé : {fmt_eur(evm['eac'])}",
        ), unsafe_allow_html=True)

    with c5:
        st.markdown(kpi_card(
            "Coût moyen / tâche", fmt_eur(avg_per_task),
            delta_text=f"{d['tasks_done']} tâches réalisées",
            delta_type="neu", accent="#f59e0b",
            sub=f"Écart EAC : {fmt_eur(abs(evm['vac']))} {'gagné' if evm['vac'] > 0 else 'perdu'}",
        ), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Charts ligne 1 ────────────────────────────────────────────────────────
    col_a, col_b = st.columns([3, 2])

    with col_a:
        st.markdown(section_title("Budget prévu vs réel par mois", "#f97316"), unsafe_allow_html=True)
        months = (
            ["Jan", "Fév", "Mar", "Avr", "Mai", "Jun", "Jul", "Aoû"]
            if "Développement" in phase_key or "Livraison" in phase_key
            else ["Jan", "Fév", "Mar"]
        )
        n = len(months)
        planned_m = np.linspace(d["budget_total"] * 0.05, d["budget_total"] / n * 1.2, n)
        planned_m = (planned_m / planned_m.sum() * (d["budget_total"] - d["unplanned_costs"])).round()
        real_m    = planned_m * (0.85 + np.random.uniform(-0.1, 0.2, n))
        real_m[-1] += d["unplanned_costs"]

        fig3 = go.Figure()
        fig3.add_trace(go.Bar(
            name="Budget prévu", x=months, y=planned_m,
            marker=dict(color="rgba(255,255,255,0.06)", line=dict(color="rgba(255,255,255,0.12)", width=1)),
            text=[fmt_eur(v) for v in planned_m],
            textposition="outside", textfont=dict(size=9, color="#64748b"),
        ))
        fig3.add_trace(go.Bar(
            name="Coût réel", x=months, y=real_m,
            marker=dict(color="#f97316", opacity=0.8, line=dict(color="rgba(249,115,22,0.4)", width=1)),
            text=[fmt_eur(v) for v in real_m],
            textposition="outside", textfont=dict(size=9, color="#f0f4f8"),
        ))
        fig3.update_layout(**PLOTLY_LAYOUT, barmode="group", height=300,
                           legend=dict(orientation="h", y=-0.22, font=dict(color="#64748b")))
        st.plotly_chart(fig3, use_container_width=True)

    with col_b:
        st.markdown(section_title("Répartition du budget", "#a855f7"), unsafe_allow_html=True)
        labels     = ["RH", "Infrastructure", "Licences", "Formation", "Non planifié"]
        vals       = [rh_consumed, d["real_cost"]*0.12, d["real_cost"]*0.06, d["real_cost"]*0.04, d["unplanned_costs"]]
        colors_pie = ["#3b82f6", "#a855f7", "#22c55e", "#f59e0b", "#ef4444"]
        fig4 = go.Figure(go.Pie(
            labels=labels, values=vals, hole=0.6,
            marker=dict(colors=colors_pie, line=dict(color="#07090e", width=3)),
            textfont=dict(size=11, color="#f0f4f8"),
        ))
        fig4.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", height=300,
            font=dict(family="DM Sans", color="#64748b"),
            margin=dict(l=0, r=0, t=10, b=0),
            legend=dict(font=dict(color="#94a3b8"), orientation="v"),
        )
        st.plotly_chart(fig4, use_container_width=True)

    # ── Charts ligne 2 ────────────────────────────────────────────────────────
    col_c, col_d = st.columns([3, 1])

    with col_c:
        st.markdown(section_title("Burndown budgétaire", "#f97316"), unsafe_allow_html=True)
        pts = 20
        ideal  = np.linspace(d["budget_total"], 0, pts)
        noise  = np.cumsum(np.random.uniform(-3000, 5000, pts))
        actual = np.clip(d["budget_total"] - np.linspace(0, d["real_cost"], pts) + noise, 0, d["budget_total"])

        fig5 = go.Figure()
        fig5.add_trace(go.Scatter(
            x=list(range(pts)), y=ideal,
            name="Consommation idéale",
            line=dict(color="#334155", dash="dot", width=2),
        ))
        fig5.add_trace(go.Scatter(
            x=list(range(pts)), y=actual,
            name="Consommation réelle",
            line=dict(color="#f97316", width=2.5),
            fill="tonexty", fillcolor="rgba(249,115,22,0.05)",
        ))
        fig5.add_hline(
            y=d["budget_total"] * 0.1,
            line_dash="dot", line_color="#ef4444",
            annotation_text="Seuil d'alerte 10%",
            annotation_font=dict(color="#ef4444", size=11),
        )
        fig5.update_layout(**PLOTLY_LAYOUT, height=260,
                           legend=dict(orientation="h", y=-0.22, font=dict(color="#64748b")),
                           xaxis_title="Semaines", yaxis_title="Budget restant (€)")
        st.plotly_chart(fig5, use_container_width=True)

    with col_d:
        st.markdown(section_title("EVM", "#14b8a6"), unsafe_allow_html=True)
        cpi_color = "#22c55e" if evm["cpi"] >= 1 else "#ef4444"
        spi_color = "#22c55e" if evm["spi"] >= 1 else "#f59e0b"
        st.markdown(
            stat_row("Budget prévu", fmt_eur(d["budget_total"])) +
            stat_row("Coût réel (AC)", fmt_eur(d["real_cost"])) +
            stat_row("Valeur acquise (EV)", fmt_eur(evm["ev"])) +
            stat_row("CPI", f"{evm['cpi']:.2f}") +
            stat_row("SPI", f"{evm['spi']:.2f}") +
            stat_row("EAC", fmt_eur(evm["eac"])) +
            stat_row("VAC", f"{'+' if evm['vac']>0 else ''}{fmt_eur(evm['vac'])}"),
            unsafe_allow_html=True,
        )
