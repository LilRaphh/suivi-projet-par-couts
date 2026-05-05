PHASES = {
    "Phase 1 – Cadrage": {
        "label": "p1",
        "emoji": "🔭",
        "date_range": ("2024-01-15", "2024-03-31"),
        "budget_total": 180_000,
        "budget_rh": 120_000,
        "tasks_planned": 24,
        "tasks_done": 18,
        "tasks_on_time": 15,
        "days_delta": -3,
        "unplanned_costs": 7_500,
        "real_cost": 142_000,
        "risks": [
            ("Retard livraison spécifications MOA", "high"),
            ("Sous-effectif équipe data", "med"),
            ("Dépassement budget serveurs cloud", "low"),
        ],
        "resources": {
            "Chef de Projet": {"budget": 30000, "consumed": 28500, "mood": 4, "tasks": 6},
            "Dev Backend":    {"budget": 28000, "consumed": 22000, "mood": 3, "tasks": 5},
            "Dev Frontend":   {"budget": 22000, "consumed": 18000, "mood": 4, "tasks": 4},
            "Data Engineer":  {"budget": 20000, "consumed": 17500, "mood": 2, "tasks": 3},
            "UX Designer":    {"budget": 20000, "consumed": 16000, "mood": 5, "tasks": 4},
        },
    },
    "Phase 2 – Développement": {
        "label": "p2",
        "emoji": "⚙️",
        "date_range": ("2024-04-01", "2024-07-31"),
        "budget_total": 350_000,
        "budget_rh": 240_000,
        "tasks_planned": 58,
        "tasks_done": 41,
        "tasks_on_time": 33,
        "days_delta": 5,
        "unplanned_costs": 22_000,
        "real_cost": 298_000,
        "risks": [
            ("Indisponibilité API partenaire logistique", "high"),
            ("Turnover dev senior", "high"),
            ("Tests de charge insuffisants", "med"),
            ("Retard intégration paiement", "med"),
        ],
        "resources": {
            "Chef de Projet": {"budget": 45000, "consumed": 44000, "mood": 3, "tasks": 10},
            "Dev Backend":    {"budget": 60000, "consumed": 58000, "mood": 2, "tasks": 14},
            "Dev Frontend":   {"budget": 50000, "consumed": 47000, "mood": 3, "tasks": 12},
            "Data Engineer":  {"budget": 45000, "consumed": 43000, "mood": 2, "tasks": 8},
            "UX Designer":    {"budget": 40000, "consumed": 35000, "mood": 4, "tasks": 7},
        },
    },
    "Phase 3 – Livraison": {
        "label": "p3",
        "emoji": "🚀",
        "date_range": ("2024-08-01", "2024-10-15"),
        "budget_total": 120_000,
        "budget_rh": 85_000,
        "tasks_planned": 30,
        "tasks_done": 28,
        "tasks_on_time": 27,
        "days_delta": 1,
        "unplanned_costs": 9_200,
        "real_cost": 108_500,
        "risks": [
            ("Migration données production", "med"),
            ("Formation utilisateurs insuffisante", "low"),
        ],
        "resources": {
            "Chef de Projet": {"budget": 20000, "consumed": 19500, "mood": 5, "tasks": 7},
            "Dev Backend":    {"budget": 18000, "consumed": 17000, "mood": 4, "tasks": 8},
            "Dev Frontend":   {"budget": 17000, "consumed": 16500, "mood": 4, "tasks": 6},
            "Data Engineer":  {"budget": 15000, "consumed": 14000, "mood": 3, "tasks": 4},
            "UX Designer":    {"budget": 15000, "consumed": 13500, "mood": 5, "tasks": 3},
        },
    },
}

THEMES = {
    "🗓️ Gantt Interactif":      "gantt",
    "🌍 Vue Globale":           "global",
    "📊 Avancement des Tâches": "avancement",
    "💰 Suivi Budgétaire":      "budget",
    "👥 Ressources Humaines":   "ressources",
    "⚠️  Risques & Alertes":    "risques",
}

MOOD_EMOJI  = {1: "😡", 2: "😟", 3: "😐", 4: "😊", 5: "🤩"}
MOOD_LABEL  = {1: "Très mauvaise", 2: "Difficile", 3: "Correcte", 4: "Bonne", 5: "Excellente"}
MOOD_COLOR  = {1: "#ef4444", 2: "#fb923c", 3: "#f59e0b", 4: "#22c55e", 5: "#818cf8"}

PHASE_COLORS = {
    "Phase 1 – Cadrage":       "#3b82f6",
    "Phase 2 – Développement": "#22c55e",
    "Phase 3 – Livraison":     "#a855f7",
}

PLOTLY_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="DM Sans", color="#64748b", size=12),
    margin=dict(l=10, r=10, t=35, b=10),
    xaxis=dict(gridcolor="#1a2236", linecolor="#1a2236", tickcolor="#64748b"),
    yaxis=dict(gridcolor="#1a2236", linecolor="#1a2236", tickcolor="#64748b"),
)
