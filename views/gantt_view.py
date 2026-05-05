from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from data.tasks import CATEGORY_ORDER, PROJECT_START, RESOURCES, TASK_CATEGORIES, TASKS
from utils.formatting import fmt_eur, kpi_card, progress_bar, section_title
from utils.gantt import compute_critical_path, compute_schedule, resource_workload


# ── Session state ─────────────────────────────────────────────────────────────

def _init_ss() -> None:
    if "task_dur"     not in st.session_state:
        st.session_state.task_dur     = {t["id"]: t["duration"] for t in TASKS}
    if "task_res"     not in st.session_state:
        st.session_state.task_res     = {t["id"]: t["resource"] for t in TASKS}
    if "task_lag"     not in st.session_state:
        st.session_state.task_lag     = {t["id"]: 0 for t in TASKS}
    if "start_date"   not in st.session_state:
        st.session_state.start_date   = PROJECT_START
    if "resource_tjm" not in st.session_state:
        st.session_state.resource_tjm = {r: RESOURCES[r]["tjm"] for r in RESOURCES}


def _reset_ss() -> None:
    st.session_state.task_dur     = {t["id"]: t["duration"] for t in TASKS}
    st.session_state.task_res     = {t["id"]: t["resource"] for t in TASKS}
    st.session_state.task_lag     = {t["id"]: 0 for t in TASKS}
    st.session_state.start_date   = PROJECT_START
    st.session_state.resource_tjm = {r: RESOURCES[r]["tjm"] for r in RESOURCES}


# ── Gantt figure ──────────────────────────────────────────────────────────────

def _build_gantt(tasks, schedule, critical, durations, resources_map, start_date):
    sorted_tasks = sorted(
        tasks,
        key=lambda t: (CATEGORY_ORDER.index(t["category"]), schedule[t["id"]]["es_day"]),
    )

    # X-axis bounds: project range only (+ 5% padding)
    project_start_ts = pd.Timestamp(start_date)
    last_ef = max(schedule[t["id"]]["ef"] for t in tasks)
    span_days = (last_ef - start_date).days
    x_min = project_start_ts - pd.Timedelta(days=max(2, span_days * 0.02))
    x_max = pd.Timestamp(last_ef)  + pd.Timedelta(days=max(3, span_days * 0.05))

    fig = go.Figure()
    legend_added: set = set()

    for task in sorted_tasks:
        tid     = task["id"]
        res     = resources_map[tid]
        is_crit = tid in critical
        color   = RESOURCES[res]["color"]
        dur     = durations[tid]

        es = pd.Timestamp(schedule[tid]["es"])
        ef = pd.Timestamp(schedule[tid]["ef"])
        dur_ms = int((ef - es).total_seconds() * 1000)
        if dur_ms <= 0:
            continue

        label    = f"{'⚡' if is_crit else '○'} #{tid:02d}  {task['name']}"
        show_leg = res not in legend_added
        legend_added.add(res)

        fig.add_trace(go.Bar(
            name=res,
            legendgroup=res,
            showlegend=show_leg,
            x=[dur_ms],
            y=[label],
            base=[es.isoformat()],
            orientation="h",
            marker=dict(
                color=color,
                opacity=1.0 if is_crit else 0.55,
                line=dict(
                    color="#ef4444" if is_crit else "rgba(255,255,255,0.06)",
                    width=2.5 if is_crit else 0.8,
                ),
            ),
            text=[f"{dur}j"] if dur_ms >= 2 * 24 * 3600 * 1000 else [""],
            textposition="inside",
            insidetextanchor="middle",
            textfont=dict(color="#ffffff", size=10, family="DM Sans"),
            hovertemplate=(
                f"<b>#{tid:02d} {task['name']}</b><br>"
                f"Ressource : {res} · {RESOURCES[res]['type']}<br>"
                f"Durée : {dur} jours ouvrés<br>"
                f"Début : %{{base|%d/%m/%Y}}<br>"
                f"Fin : %{{x|%d/%m/%Y}}<br>"
                f"{'⚡ Chemin critique — marge nulle' if is_crit else '○ Marge disponible'}"
                f"<extra></extra>"
            ),
        ))

    # Project start line
    start_iso = project_start_ts.isoformat()
    fig.add_shape(type="line", x0=start_iso, x1=start_iso, y0=0, y1=1,
                  xref="x", yref="paper",
                  line=dict(color="#3b82f6", width=1.5, dash="dash"))
    fig.add_annotation(x=start_iso, y=1, xref="x", yref="paper",
                       text=" Démarrage", showarrow=False,
                       font=dict(color="#3b82f6", size=10),
                       xanchor="left", yanchor="bottom")

    # Delivery line
    end_iso = pd.Timestamp(last_ef).isoformat()
    fig.add_shape(type="line", x0=end_iso, x1=end_iso, y0=0, y1=1,
                  xref="x", yref="paper",
                  line=dict(color="#22c55e", width=1.5, dash="dash"))
    fig.add_annotation(x=end_iso, y=1, xref="x", yref="paper",
                       text=" Livraison ", showarrow=False,
                       font=dict(color="#22c55e", size=10),
                       xanchor="right", yanchor="bottom")

    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="DM Sans", color="#64748b", size=11),
        height=max(580, len(tasks) * 26 + 80),
        barmode="overlay",
        margin=dict(l=10, r=20, t=55, b=20),
        xaxis=dict(
            type="date",
            range=[x_min.isoformat(), x_max.isoformat()],   # ← project range only
            gridcolor="#1a2236", linecolor="#1a2236",
            tickcolor="#64748b", tickformat="%d %b %Y",
            tickfont=dict(size=10),
        ),
        yaxis=dict(
            gridcolor="#1a2236", linecolor="#1a2236",
            autorange="reversed",
            tickfont=dict(size=10.5, color="#94a3b8"),
        ),
        legend=dict(
            orientation="h", y=1.05, x=0,
            font=dict(color="#94a3b8", size=11),
            bgcolor="rgba(0,0,0,0)", traceorder="normal",
        ),
    )
    return fig


# ── Main render ───────────────────────────────────────────────────────────────

def render_gantt() -> None:
    _init_ss()

    # ── ÉTAPE 1 : contrôles – lus EN PREMIER, session state mis à jour immédiatement
    with st.expander("⚙️ Paramètres globaux du projet", expanded=True):
        col_date, col_sep, col_tjm = st.columns([1, 0.04, 4])

        with col_date:
            st.markdown(
                '<div style="font-size:0.72rem;text-transform:uppercase;'
                'letter-spacing:0.1em;color:#64748b;margin-bottom:6px;">Date de démarrage</div>',
                unsafe_allow_html=True,
            )
            # Lire la valeur du widget → mettre à jour session state dans la foulée
            picked = st.date_input(
                "Début", value=st.session_state.start_date,
                label_visibility="collapsed", key="date_input_start",
            )
            st.session_state.start_date = picked          # mise à jour immédiate

        with col_sep:
            st.markdown(
                '<div style="border-left:1px solid rgba(255,255,255,0.07);'
                'height:80px;margin-top:8px;"></div>',
                unsafe_allow_html=True,
            )

        with col_tjm:
            st.markdown(
                '<div style="font-size:0.72rem;text-transform:uppercase;'
                'letter-spacing:0.1em;color:#64748b;margin-bottom:6px;">TJM par ressource (€/jour)</div>',
                unsafe_allow_html=True,
            )
            tjm_cols = st.columns(len(RESOURCES))
            for i, (res_name, res_info) in enumerate(RESOURCES.items()):
                with tjm_cols[i]:
                    badge = (
                        f'<span style="background:{res_info["color"]}22;color:{res_info["color"]};'
                        f'border:1px solid {res_info["color"]}44;padding:1px 6px;border-radius:8px;'
                        f'font-size:0.65rem;font-weight:600;">{res_info["type"]}</span>'
                    )
                    st.markdown(
                        f'<div style="font-size:0.75rem;color:#94a3b8;margin-bottom:2px;">'
                        f'{res_name.split()[0]} {badge}</div>',
                        unsafe_allow_html=True,
                    )
                    new_tjm = st.number_input(
                        res_name, min_value=50, max_value=3000, step=25,
                        value=st.session_state.resource_tjm[res_name],
                        label_visibility="collapsed",
                        key=f"tjm_{res_name}",
                    )
                    st.session_state.resource_tjm[res_name] = new_tjm   # mise à jour immédiate

    # ── ÉTAPE 2 : lire les valeurs courantes (toutes à jour)
    durations     = dict(st.session_state.task_dur)
    resources_map = dict(st.session_state.task_res)
    lags          = dict(st.session_state.task_lag)
    start_date    = st.session_state.start_date
    tjms          = dict(st.session_state.resource_tjm)

    # ── ÉTAPE 3 : calculs (sur les valeurs courantes)
    schedule = compute_schedule(TASKS, start_date, durations, lags)
    critical = compute_critical_path(TASKS, schedule)
    workload = resource_workload(TASKS, schedule, durations, resources_map)

    last_tid     = max(schedule, key=lambda k: schedule[k]["ef_day"])
    project_days = schedule[last_tid]["ef_day"]
    project_end  = schedule[last_tid]["ef"]
    total_jh     = sum(durations[t["id"]] for t in TASKS)
    total_cost   = sum(durations[t["id"]] * tjms[resources_map[t["id"]]] for t in TASKS)
    weeks        = round(project_days / 5, 1)

    # ── ÉTAPE 4 : KPIs
    st.markdown(section_title("🗓️ Gantt — Beta Amazon Mobile", "#3b82f6"), unsafe_allow_html=True)

    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        st.markdown(kpi_card(
            "Durée projet", f"{project_days}j",
            delta_text=f"≈ {weeks} semaines",
            delta_type="pos" if project_days <= 55 else "neg",
            accent="#3b82f6", pct=min(project_days / 80 * 100, 100),
            sub=f"Livraison : {project_end.strftime('%d/%m/%Y')}",
        ), unsafe_allow_html=True)
    with c2:
        st.markdown(kpi_card(
            "Jours / homme", f"{total_jh}j",
            delta_text=f"5 ressources · {len(TASKS)} tâches",
            delta_type="neu", accent="#a855f7",
            pct=min(total_jh / 200 * 100, 100),
            sub=f"Moy. {round(total_jh/len(TASKS),1)} j/tâche",
        ), unsafe_allow_html=True)
    with c3:
        st.markdown(kpi_card(
            "Budget RH estimé", fmt_eur(total_cost),
            delta_text="TJMs × durées affectées",
            delta_type="neu", accent="#f97316",
            sub="Hors charges patronales",
        ), unsafe_allow_html=True)
    with c4:
        n_crit = len(critical)
        st.markdown(kpi_card(
            "Chemin critique", f"{n_crit} tâches",
            delta_text="Marge nulle — risque max",
            delta_type="neg", accent="#ef4444",
            pct=round(n_crit / len(TASKS) * 100),
            sub="⚡ = tâche critique",
        ), unsafe_allow_html=True)
    with c5:
        freelance_cost = sum(
            durations[t["id"]] * tjms[resources_map[t["id"]]]
            for t in TASKS if RESOURCES[resources_map[t["id"]]]["type"] == "Freelance"
        )
        pct_fl = round(freelance_cost / total_cost * 100) if total_cost else 0
        st.markdown(kpi_card(
            "Coût Freelance", fmt_eur(freelance_cost),
            delta_text=f"{pct_fl}% du budget total",
            delta_type="neg" if pct_fl > 60 else "neu",
            accent="#f97316", pct=pct_fl,
            sub=f"TJM actuel : {tjms['Freelance Backend']} €/j",
        ), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── ÉTAPE 5 : Gantt
    st.markdown(section_title("Diagramme de Gantt", "#3b82f6"), unsafe_allow_html=True)

    col_leg1, col_leg2 = st.columns(2)
    with col_leg1:
        st.markdown(
            '<div class="info-box">⚡ Bordure rouge = chemin critique (marge = 0). '
            'Toute modification de ces tâches décale la livraison.</div>',
            unsafe_allow_html=True,
        )
    with col_leg2:
        badges = " ".join(
            f'<span style="background:{TASK_CATEGORIES[c]}22;color:{TASK_CATEGORIES[c]};'
            f'border:1px solid {TASK_CATEGORIES[c]}44;padding:2px 8px;border-radius:12px;'
            f'font-size:0.68rem;font-weight:600;margin-right:4px;">{c}</span>'
            for c in CATEGORY_ORDER
        )
        st.markdown(f'<div style="padding:0.55rem 0;font-size:0.75rem;color:#64748b;">{badges}</div>',
                    unsafe_allow_html=True)

    fig = _build_gantt(TASKS, schedule, critical, durations, resources_map, start_date)
    st.plotly_chart(fig, use_container_width=True)

    # ── ÉTAPE 6 : éditeur tâches + graphiques
    st.markdown("<br>", unsafe_allow_html=True)
    col_edit, col_charts = st.columns([3, 2])

    with col_edit:
        st.markdown(section_title("✏️ Modifier les tâches", "#f59e0b"), unsafe_allow_html=True)
        st.markdown(
            '<div class="info-box" style="background:rgba(245,158,11,0.08);'
            'border-color:rgba(245,158,11,0.25);color:#fcd34d;">'
            'Éditez <b>Ressource</b>, <b>Durée</b> ou <b>Délai</b> (j d\'attente après '
            'les prédécesseurs) → recalcul instantané.</div>',
            unsafe_allow_html=True,
        )

        df_edit = pd.DataFrame([{
            "ID":        t["id"],
            "Tâche":     t["name"],
            "Cat.":      t["category"],
            "Ressource": resources_map[t["id"]],
            "Durée (j)": durations[t["id"]],
            "Délai (j)": lags[t["id"]],
            "⚡":         "⚡" if t["id"] in critical else "○",
            "Début":     schedule[t["id"]]["es"].strftime("%d/%m/%Y"),
            "Fin":       schedule[t["id"]]["ef"].strftime("%d/%m/%Y"),
            "Coût (€)":  durations[t["id"]] * tjms[resources_map[t["id"]]],
        } for t in TASKS])

        try:
            edited = st.data_editor(
                df_edit,
                column_config={
                    "ID":        st.column_config.NumberColumn("ID",    disabled=True, width="small"),
                    "Tâche":     st.column_config.TextColumn("Tâche",   disabled=True, width="large"),
                    "Cat.":      st.column_config.TextColumn("Cat.",    disabled=True, width="small"),
                    "Ressource": st.column_config.SelectboxColumn(
                        "Ressource", options=list(RESOURCES.keys()), width="medium"),
                    "Durée (j)": st.column_config.NumberColumn(
                        "Durée (j)", min_value=1, max_value=60, step=1, width="small"),
                    "Délai (j)": st.column_config.NumberColumn(
                        "Délai (j)", min_value=0, max_value=30, step=1, width="small",
                        help="Jours d'attente supplémentaires après le prédécesseur"),
                    "⚡":         st.column_config.TextColumn("⚡",      disabled=True, width="small"),
                    "Début":     st.column_config.TextColumn("Début",   disabled=True, width="small"),
                    "Fin":       st.column_config.TextColumn("Fin",     disabled=True, width="small"),
                    "Coût (€)":  st.column_config.NumberColumn(
                        "Coût (€)", disabled=True, format="%d €", width="small"),
                },
                hide_index=True,
                use_container_width=True,
                num_rows="fixed",
            )
            # Propager les modifications dans session state (Streamlit rerun auto ensuite)
            for _, row in edited.iterrows():
                tid = int(row["ID"])
                st.session_state.task_dur[tid] = int(row["Durée (j)"])
                st.session_state.task_res[tid] = row["Ressource"]
                st.session_state.task_lag[tid] = int(row["Délai (j)"])

        except AttributeError:
            st.dataframe(df_edit, use_container_width=True, hide_index=True)
            st.caption("Mettez à jour Streamlit (≥1.19) pour l'édition interactive.")

        if st.button("↺ Réinitialiser le planning"):
            _reset_ss()
            st.rerun()

    # ── Graphiques latéraux
    with col_charts:
        st.markdown(section_title("👥 Charge par ressource", "#a855f7"), unsafe_allow_html=True)

        res_names  = list(RESOURCES.keys())
        res_days   = [workload.get(r, 0) for r in res_names]
        res_costs  = [workload.get(r, 0) * tjms[r] for r in res_names]
        res_colors = [RESOURCES[r]["color"] for r in res_names]

        fig_wl = go.Figure(go.Bar(
            x=res_names, y=res_days,
            marker_color=res_colors, opacity=0.85,
            text=[f"{d}j" for d in res_days],
            textposition="outside",
            textfont=dict(color="#f0f4f8", size=10),
            hovertemplate="<b>%{x}</b><br>%{y} jours ouvrés<extra></extra>",
        ))
        fig_wl.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font=dict(family="DM Sans", color="#64748b"),
            height=200, margin=dict(l=10, r=10, t=10, b=55),
            xaxis=dict(gridcolor="#1a2236", linecolor="#1a2236",
                       tickangle=-15, tickfont=dict(size=9.5)),
            yaxis=dict(gridcolor="#1a2236", linecolor="#1a2236", title="Jours"),
            showlegend=False,
        )
        st.plotly_chart(fig_wl, use_container_width=True)

        st.markdown(section_title("💰 Budget par ressource", "#f97316"), unsafe_allow_html=True)

        fig_cost = go.Figure(go.Pie(
            labels=[f"{r.split()[0]}\n({RESOURCES[r]['type']})" for r in res_names],
            values=res_costs, hole=0.55,
            marker=dict(colors=res_colors, line=dict(color="#07090e", width=3)),
            textfont=dict(size=10, color="#f0f4f8"),
            hovertemplate="<b>%{label}</b><br>%{value:,.0f} €<br>%{percent}<extra></extra>",
        ))
        fig_cost.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(family="DM Sans", color="#64748b"),
            height=200, margin=dict(l=0, r=0, t=10, b=0),
            legend=dict(font=dict(color="#94a3b8", size=9), orientation="v"),
        )
        st.plotly_chart(fig_cost, use_container_width=True)

        st.markdown(section_title("📋 Récapitulatif", "#22c55e"), unsafe_allow_html=True)
        for r in res_names:
            d   = workload.get(r, 0)
            c   = d * tjms[r]
            pct = round(c / total_cost * 100) if total_cost else 0
            st.markdown(
                f'<div style="font-size:0.78rem;display:flex;justify-content:space-between;margin-bottom:2px;">'
                f'<span style="color:#94a3b8;">{r.split()[0]} '
                f'<span style="color:#3d4f6b;font-size:0.68rem;">({RESOURCES[r]["type"]} · {tjms[r]}€/j)</span></span>'
                f'<span style="color:#f0f4f8;font-family:Syne,sans-serif;">{fmt_eur(c)}'
                f'<span style="color:#3d4f6b;font-weight:400;font-family:DM Sans,sans-serif;font-size:0.7rem;"> {pct}%</span></span></div>'
                f'{progress_bar(pct, RESOURCES[r]["color"], 4)}',
                unsafe_allow_html=True,
            )
