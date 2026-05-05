import random

import plotly.graph_objects as go
import streamlit as st

from utils.formatting import fmt_eur, kpi_card, progress_bar, section_title, stat_row

_RISK_META = {
    "high": {
        "label": "CRITIQUE", "cls": "risk-high",
        "cat":   "RH / Gouvernance",
        "impact": "Élevé", "proba": "75–90%",
        "prob_val": 0.82, "impact_val": 0.88,
        "size": 22, "color": "#ef4444",
        "score_weight": 9,
    },
    "med": {
        "label": "MODÉRÉ", "cls": "risk-med",
        "cat":   "Technique / Planning",
        "impact": "Moyen", "proba": "40–60%",
        "prob_val": 0.50, "impact_val": 0.55,
        "size": 16, "color": "#f59e0b",
        "score_weight": 4,
    },
    "low": {
        "label": "FAIBLE", "cls": "risk-low",
        "cat":   "Budget / Qualité",
        "impact": "Faible", "proba": "10–25%",
        "prob_val": 0.18, "impact_val": 0.25,
        "size": 12, "color": "#22c55e",
        "score_weight": 1,
    },
}

_MITIGATION = {
    "high": ("Plan d'action immédiat requis", "#ef4444"),
    "med":  ("Surveillance active",           "#f59e0b"),
    "low":  ("Accepté / sous contrôle",       "#22c55e"),
}


def render_risques(d: dict) -> None:
    risks      = d["risks"]
    high_risks = [r for r in risks if r[1] == "high"]
    med_risks  = [r for r in risks if r[1] == "med"]
    low_risks  = [r for r in risks if r[1] == "low"]
    total      = len(risks)

    risk_score = round(
        sum(_RISK_META[r[1]]["score_weight"] for r in risks) / (total * 9) * 100
    ) if risks else 0
    exposure_label = "Critique" if risk_score >= 70 else ("Modéré" if risk_score >= 40 else "Faible")
    exposure_color = "#ef4444" if risk_score >= 70 else ("#f59e0b" if risk_score >= 40 else "#22c55e")

    # ── KPI strip ─────────────────────────────────────────────────────────────
    st.markdown(section_title("⚠️ Risques & Alertes", "#ef4444"), unsafe_allow_html=True)

    c1, c2, c3, c4, c5 = st.columns(5)

    with c1:
        st.markdown(kpi_card(
            "Risques CRITIQUES", str(len(high_risks)),
            delta_text="Action immédiate requise" if high_risks else "Aucun risque critique",
            delta_type="neg" if high_risks else "pos",
            accent="#ef4444",
            pct=len(high_risks) / total * 100 if total else 0,
        ), unsafe_allow_html=True)

    with c2:
        st.markdown(kpi_card(
            "Risques MODÉRÉS", str(len(med_risks)),
            delta_text="À surveiller activement",
            delta_type="neu", accent="#f59e0b",
            pct=len(med_risks) / total * 100 if total else 0,
        ), unsafe_allow_html=True)

    with c3:
        st.markdown(kpi_card(
            "Risques FAIBLES", str(len(low_risks)),
            delta_text="Sous contrôle",
            delta_type="pos", accent="#22c55e",
            pct=len(low_risks) / total * 100 if total else 0,
        ), unsafe_allow_html=True)

    with c4:
        st.markdown(kpi_card(
            "Score d'exposition", f"{risk_score}/100",
            delta_text=exposure_label,
            delta_type="neg" if risk_score >= 70 else ("neu" if risk_score >= 40 else "pos"),
            accent=exposure_color,
            pct=risk_score,
            sub="Probabilité × Impact pondérés",
        ), unsafe_allow_html=True)

    with c5:
        st.markdown(kpi_card(
            "Risques total", str(total),
            delta_text=f"{len(high_risks)} critique(s) · {len(med_risks)} modéré(s)",
            delta_type="neg" if len(high_risks) >= 2 else "neu",
            accent="#64748b",
            sub="Sur cette phase du projet",
        ), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Registre + Exposition ──────────────────────────────────────────────────
    col_a, col_b = st.columns([3, 2])

    with col_a:
        st.markdown(section_title("Registre des risques", "#ef4444"), unsafe_allow_html=True)
        for r_name, r_level in risks:
            meta    = _RISK_META[r_level]
            mit_txt, mit_col = _MITIGATION[r_level]
            score   = meta["score_weight"]
            st.markdown(f"""
            <div style="background:#0c1018; border:1px solid rgba(255,255,255,0.07); border-radius:14px;
                        padding:1rem 1.2rem; margin-bottom:0.65rem;">
                <div style="display:flex; align-items:center; gap:12px; margin-bottom:8px;">
                    <span class="{meta['cls']}">{meta['label']}</span>
                    <div style="flex:1; color:#f0f4f8; font-weight:500; font-size:0.88rem;">{r_name}</div>
                    <div style="font-family:'Syne',sans-serif; font-size:1.1rem; font-weight:700; color:{meta['color']};">{score}/9</div>
                </div>
                <div style="display:flex; justify-content:space-between; font-size:0.72rem; margin-bottom:6px;">
                    <span style="color:#64748b;">Catégorie : {meta['cat']}</span>
                    <span style="color:#64748b;">Impact : <b style="color:#94a3b8;">{meta['impact']}</b>
                        &nbsp;·&nbsp; Probabilité : <b style="color:#94a3b8;">{meta['proba']}</b></span>
                </div>
                <div style="display:flex; align-items:center; gap:8px; font-size:0.72rem;">
                    <div style="width:8px; height:8px; border-radius:50%; background:{mit_col}; flex-shrink:0;"></div>
                    <span style="color:{mit_col};">{mit_txt}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

    with col_b:
        st.markdown(section_title("Exposition par niveau", "#f59e0b"), unsafe_allow_html=True)
        for label, lst, col in [("Critiques", high_risks, "#ef4444"), ("Modérés", med_risks, "#f59e0b"), ("Faibles", low_risks, "#22c55e")]:
            pct_w = round(len(lst) / total * 100) if total else 0
            st.markdown(f"""
            <div style="margin-bottom:1rem;">
                <div style="display:flex; justify-content:space-between; font-size:0.8rem; margin-bottom:4px;">
                    <span style="color:#94a3b8;">{label}</span>
                    <span style="color:#f0f4f8; font-weight:600; font-family:'Syne',sans-serif;">{len(lst)} <span style="color:#3d4f6b; font-weight:400; font-family:'DM Sans',sans-serif; font-size:0.72rem;">({pct_w}%)</span></span>
                </div>
                {progress_bar(pct_w, col, 7)}
            </div>
            """, unsafe_allow_html=True)

        st.markdown(section_title("Score global", "#ef4444"), unsafe_allow_html=True)
        st.markdown(
            stat_row("Exposition globale", f"{risk_score}/100") +
            stat_row("Niveau", exposure_label) +
            stat_row("Risques total", str(total)) +
            stat_row("Critiques", str(len(high_risks))) +
            stat_row("Score max possible", "100"),
            unsafe_allow_html=True,
        )

    # ── Matrice Impact × Probabilité ──────────────────────────────────────────
    st.markdown(section_title("Matrice Impact × Probabilité", "#a855f7"), unsafe_allow_html=True)
    fig8 = go.Figure()

    for xi, yi, col, txt in [
        ([0, 0.5, 0.5, 0], [0, 0, 0.5, 0.5], "rgba(34,197,94,0.04)",  "Zone verte"),
        ([0.5,1,1,0.5],    [0, 0, 0.5, 0.5], "rgba(245,158,11,0.04)", "Zone orange"),
        ([0, 0.5, 0.5, 0], [0.5,0.5,1,1],    "rgba(245,158,11,0.04)", "Zone orange"),
        ([0.5,1,1,0.5],    [0.5,0.5,1,1],    "rgba(239,68,68,0.07)",  "Zone rouge"),
    ]:
        fig8.add_trace(go.Scatter(
            x=xi + [xi[0]], y=yi + [yi[0]],
            fill="toself", fillcolor=col,
            line=dict(color="rgba(255,255,255,0.05)"),
            showlegend=False, hoverinfo="skip",
        ))

    for r_name, r_level in risks:
        meta = _RISK_META[r_level]
        jx   = random.uniform(-0.04, 0.04)
        jy   = random.uniform(-0.04, 0.04)
        label_txt = r_name[:28] + "…" if len(r_name) > 28 else r_name
        fig8.add_trace(go.Scatter(
            x=[meta["prob_val"] + jx], y=[meta["impact_val"] + jy],
            mode="markers+text",
            text=[label_txt], textposition="top center",
            textfont=dict(size=10, color="#f0f4f8"),
            marker=dict(size=meta["size"] * 1.5, color=meta["color"], opacity=0.8,
                        line=dict(color=meta["color"], width=1)),
            showlegend=False,
            hovertemplate=f"<b>{r_name}</b><br>Probabilité: {meta['proba']}<br>Impact: {meta['impact']}<extra></extra>",
        ))

    for txt, x, y in [("Zone verte", 0.25, 0.06), ("Zone orange", 0.75, 0.06),
                      ("Zone orange", 0.25, 0.94), ("Zone rouge", 0.75, 0.94)]:
        fig8.add_annotation(x=x, y=y, text=txt, showarrow=False,
                            font=dict(color="#3d4f6b", size=10))

    fig8.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="DM Sans", color="#64748b"),
        height=400, margin=dict(l=50, r=20, t=20, b=50),
        xaxis=dict(title="Probabilité", range=[0, 1], gridcolor="#1a2236", linecolor="#1a2236",
                   tickformat=".0%", tickvals=[0, 0.25, 0.5, 0.75, 1]),
        yaxis=dict(title="Impact", range=[0, 1], gridcolor="#1a2236", linecolor="#1a2236",
                   tickformat=".0%", tickvals=[0, 0.25, 0.5, 0.75, 1]),
    )
    st.plotly_chart(fig8, use_container_width=True)
