from datetime import date

PROJECT_START = date(2025, 1, 6)

RESOURCES = {
    "Chef de Projet":     {"tjm": 600, "type": "CDI",       "color": "#3b82f6"},
    "Freelance Backend":  {"tjm": 750, "type": "Freelance",  "color": "#f97316"},
    "Data Scientist":     {"tjm": 500, "type": "CDI",        "color": "#a855f7"},
    "Alternant Frontend": {"tjm": 150, "type": "Alternant",  "color": "#22c55e"},
    "Stagiaire QA/UX":   {"tjm":  80, "type": "Stagiaire",  "color": "#f59e0b"},
}

TASK_CATEGORIES = {
    "Cadrage":   "#64748b",
    "Design":    "#ec4899",
    "Backend":   "#f97316",
    "Data":      "#a855f7",
    "Frontend":  "#22c55e",
    "QA":        "#ef4444",
    "Livraison": "#3b82f6",
}

CATEGORY_ORDER = ["Cadrage", "Design", "Backend", "Data", "Frontend", "QA", "Livraison"]

# id, name, category, resource, duration (working days), deps (list of ids)
TASKS = [
    # ── Cadrage ──────────────────────────────────────────────────────────────
    {"id":  1, "name": "Kick-off & Définition des KPIs",       "category": "Cadrage",   "resource": "Chef de Projet",     "duration": 2, "deps": []},
    {"id":  2, "name": "Spécifications fonctionnelles",         "category": "Cadrage",   "resource": "Chef de Projet",     "duration": 5, "deps": [1]},
    {"id":  3, "name": "Architecture technique",                "category": "Cadrage",   "resource": "Freelance Backend",  "duration": 7, "deps": [1]},
    # ── Design / UX ──────────────────────────────────────────────────────────
    {"id":  4, "name": "Maquettes UX – Accueil & Navigation",  "category": "Design",    "resource": "Stagiaire QA/UX",   "duration": 5, "deps": [2]},
    {"id":  5, "name": "Maquettes UX – Recherche & Catalogue", "category": "Design",    "resource": "Stagiaire QA/UX",   "duration": 4, "deps": [4]},
    {"id":  6, "name": "Maquettes UX – Panier & Checkout",     "category": "Design",    "resource": "Stagiaire QA/UX",   "duration": 4, "deps": [4]},
    {"id":  7, "name": "Maquettes UX – Livraison & Profil",    "category": "Design",    "resource": "Stagiaire QA/UX",   "duration": 3, "deps": [4]},
    # ── Backend ───────────────────────────────────────────────────────────────
    {"id":  8, "name": "Setup infra & CI/CD",                  "category": "Backend",   "resource": "Freelance Backend",  "duration": 3, "deps": [3]},
    {"id":  9, "name": "API Authentification & Compte",        "category": "Backend",   "resource": "Freelance Backend",  "duration": 5, "deps": [8]},
    {"id": 10, "name": "API Catalogue & Recherche",            "category": "Backend",   "resource": "Freelance Backend",  "duration": 8, "deps": [8]},
    {"id": 11, "name": "API Panier",                           "category": "Backend",   "resource": "Freelance Backend",  "duration": 5, "deps": [9]},
    {"id": 12, "name": "API Paiement",                         "category": "Backend",   "resource": "Freelance Backend",  "duration": 8, "deps": [11]},
    {"id": 13, "name": "API Livraison & Tracking",             "category": "Backend",   "resource": "Freelance Backend",  "duration": 6, "deps": [8]},
    # ── Data ─────────────────────────────────────────────────────────────────
    {"id": 14, "name": "Pipeline données produits",            "category": "Data",      "resource": "Data Scientist",     "duration": 5, "deps": [8]},
    {"id": 15, "name": "Moteur de recommandations ML",         "category": "Data",      "resource": "Data Scientist",     "duration": 8, "deps": [14, 10]},
    {"id": 16, "name": "Dashboard analytics",                  "category": "Data",      "resource": "Data Scientist",     "duration": 4, "deps": [14]},
    {"id": 17, "name": "Setup A/B Testing",                    "category": "Data",      "resource": "Data Scientist",     "duration": 3, "deps": [16]},
    # ── Frontend ─────────────────────────────────────────────────────────────
    {"id": 18, "name": "Écran Accueil & Navigation",           "category": "Frontend",  "resource": "Alternant Frontend", "duration": 5, "deps": [4, 8]},
    {"id": 19, "name": "Écran Recherche & Filtres",            "category": "Frontend",  "resource": "Alternant Frontend", "duration": 6, "deps": [5, 10, 18]},
    {"id": 20, "name": "Écran Fiche Produit",                  "category": "Frontend",  "resource": "Alternant Frontend", "duration": 5, "deps": [10, 18]},
    {"id": 21, "name": "Écran Panier",                         "category": "Frontend",  "resource": "Alternant Frontend", "duration": 4, "deps": [6, 11, 18]},
    {"id": 22, "name": "Écran Checkout & Paiement",            "category": "Frontend",  "resource": "Alternant Frontend", "duration": 6, "deps": [12, 21]},
    {"id": 23, "name": "Écran Suivi Livraison",                "category": "Frontend",  "resource": "Alternant Frontend", "duration": 4, "deps": [7, 13, 18]},
    {"id": 24, "name": "Écran Profil & Compte",                "category": "Frontend",  "resource": "Alternant Frontend", "duration": 3, "deps": [9, 18]},
    {"id": 25, "name": "Intégration Recommandations",          "category": "Frontend",  "resource": "Alternant Frontend", "duration": 3, "deps": [15, 20]},
    # ── QA ───────────────────────────────────────────────────────────────────
    {"id": 26, "name": "Tests unitaires Backend",              "category": "QA",        "resource": "Stagiaire QA/UX",   "duration": 5, "deps": [9, 10, 11, 12, 13]},
    {"id": 27, "name": "Tests intégration Frontend",           "category": "QA",        "resource": "Stagiaire QA/UX",   "duration": 4, "deps": [19, 20, 21, 22, 23, 24]},
    {"id": 28, "name": "Tests E2E & Performance",              "category": "QA",        "resource": "Stagiaire QA/UX",   "duration": 5, "deps": [26, 27]},
    {"id": 29, "name": "Beta test utilisateurs",               "category": "QA",        "resource": "Stagiaire QA/UX",   "duration": 4, "deps": [25, 28]},
    # ── Livraison ─────────────────────────────────────────────────────────────
    {"id": 30, "name": "Go-live & Monitoring",                 "category": "Livraison", "resource": "Chef de Projet",     "duration": 3, "deps": [17, 29]},
]
