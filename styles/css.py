CSS_STYLES = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;0,9..40,600;1,9..40,400&display=swap');

/* ── Tokens ──────────────────────────────────────────────── */
:root {
    --bg-base:     #07090e;
    --bg-card:     #0c1018;
    --bg-elevated: #111827;
    --border:      rgba(255,255,255,0.07);
    --border-strong: rgba(255,255,255,0.12);
    --text-primary: #f0f4f8;
    --text-muted:   #64748b;
    --text-dim:     #3d4f6b;
    --orange:  #f97316;
    --blue:    #3b82f6;
    --green:   #22c55e;
    --red:     #ef4444;
    --amber:   #f59e0b;
    --purple:  #a855f7;
    --teal:    #14b8a6;
    --slate:   #334155;
}

/* ── Base ────────────────────────────────────────────────── */
html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }

.stApp {
    background: var(--bg-base);
    color: var(--text-primary);
}

/* ── Sidebar ─────────────────────────────────────────────── */
section[data-testid="stSidebar"] {
    background: #080c14 !important;
    border-right: 1px solid var(--border);
}
section[data-testid="stSidebar"] * { color: #94a3b8 !important; }
section[data-testid="stSidebar"] b { color: #cbd5e1 !important; }

/* ── Logo sidebar ────────────────────────────────────────── */
.sidebar-logo {
    text-align: center;
    padding: 1.5rem 0 1.2rem;
    border-bottom: 1px solid var(--border);
    margin-bottom: 1.2rem;
}
.sidebar-logo-title {
    font-family: 'Syne', sans-serif;
    font-size: 1.5rem;
    font-weight: 800;
    color: var(--orange) !important;
    letter-spacing: -0.02em;
}
.sidebar-logo-sub {
    font-size: 0.65rem;
    color: var(--text-dim) !important;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    margin-top: 2px;
}

/* ── Page header ─────────────────────────────────────────── */
.dash-header {
    font-family: 'Syne', sans-serif;
    font-weight: 800;
    font-size: 2rem;
    letter-spacing: -0.04em;
    color: var(--text-primary);
    margin-bottom: 0;
    line-height: 1;
}
.dash-header span { color: var(--orange); }
.dash-sub {
    font-size: 0.78rem;
    color: var(--text-muted);
    letter-spacing: 0.14em;
    text-transform: uppercase;
    margin-top: 4px;
    margin-bottom: 1.5rem;
}

/* ── KPI Cards ───────────────────────────────────────────── */
.kpi-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 1.25rem 1.4rem 1.1rem;
    position: relative;
    overflow: hidden;
    transition: border-color 0.2s, box-shadow 0.2s;
    box-shadow: 0 4px 24px rgba(0,0,0,0.35);
    height: 100%;
    box-sizing: border-box;
}
/* Top gradient line */
.kpi-card::after {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, var(--accent, #f97316) 0%, transparent 80%);
    border-radius: 16px 16px 0 0;
}
/* Subtle glow */
.kpi-card::before {
    content: '';
    position: absolute;
    top: -40px; left: -20px;
    width: 120px; height: 120px;
    background: radial-gradient(circle, var(--accent, #f97316) 0%, transparent 70%);
    opacity: 0.04;
    pointer-events: none;
}

.kpi-label {
    font-size: 0.68rem;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: var(--text-muted);
    margin-bottom: 0.6rem;
    font-weight: 500;
}
.kpi-value {
    font-family: 'Syne', sans-serif;
    font-size: 1.9rem;
    font-weight: 700;
    color: var(--text-primary);
    line-height: 1;
    letter-spacing: -0.02em;
}
.kpi-sub {
    font-size: 0.72rem;
    color: var(--text-muted);
    margin-top: 3px;
}
/* Progress bar inside card */
.kpi-bar-track {
    background: rgba(255,255,255,0.06);
    border-radius: 20px;
    height: 4px;
    margin: 0.6rem 0 0.5rem;
    overflow: hidden;
}
.kpi-bar-fill {
    height: 100%;
    border-radius: 20px;
    background: var(--accent, #f97316);
    transition: width 0.6s ease;
}
.kpi-delta {
    font-size: 0.74rem;
    margin-top: 0.3rem;
    font-weight: 500;
    display: flex;
    align-items: center;
    gap: 4px;
}
.delta-pos { color: var(--green); }
.delta-neg { color: var(--red); }
.delta-neu { color: var(--amber); }

/* ── Section title ───────────────────────────────────────── */
.section-title {
    font-family: 'Syne', sans-serif;
    font-size: 0.95rem;
    font-weight: 700;
    color: var(--text-primary);
    letter-spacing: 0.02em;
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 1rem;
    padding-bottom: 0.6rem;
    border-bottom: 1px solid var(--border);
}
.section-title::before {
    content: '';
    display: inline-block;
    width: 3px;
    height: 14px;
    background: var(--accent, #f97316);
    border-radius: 2px;
    flex-shrink: 0;
}

/* ── Phase badges ────────────────────────────────────────── */
.phase-badge {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 0.68rem;
    font-weight: 600;
    letter-spacing: 0.08em;
    text-transform: uppercase;
}
.p1 { background: rgba(59,130,246,0.12); color: #60a5fa; border: 1px solid rgba(59,130,246,0.25); }
.p2 { background: rgba(34,197,94,0.12);  color: #4ade80; border: 1px solid rgba(34,197,94,0.25); }
.p3 { background: rgba(168,85,247,0.12); color: #c084fc; border: 1px solid rgba(168,85,247,0.25); }
.pg { background: rgba(249,115,22,0.12); color: #fb923c; border: 1px solid rgba(249,115,22,0.25); }

/* ── Risk pills ──────────────────────────────────────────── */
.risk-high { background: rgba(239,68,68,0.12);  color: #f87171; border: 1px solid rgba(239,68,68,0.3);  padding: 3px 10px; border-radius: 20px; font-size: 0.68rem; font-weight: 600; }
.risk-med  { background: rgba(245,158,11,0.12); color: #fbbf24; border: 1px solid rgba(245,158,11,0.3); padding: 3px 10px; border-radius: 20px; font-size: 0.68rem; font-weight: 600; }
.risk-low  { background: rgba(34,197,94,0.12);  color: #4ade80; border: 1px solid rgba(34,197,94,0.3);  padding: 3px 10px; border-radius: 20px; font-size: 0.68rem; font-weight: 600; }

/* ── Stat row (inline metric pair) ──────────────────────── */
.stat-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0.55rem 0;
    border-bottom: 1px solid var(--border);
    font-size: 0.82rem;
}
.stat-row:last-child { border-bottom: none; }
.stat-row-label { color: var(--text-muted); }
.stat-row-value { color: var(--text-primary); font-weight: 600; font-family: 'Syne', sans-serif; }

/* ── Health score ring ───────────────────────────────────── */
.health-ring {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 4px;
}
.health-score-num {
    font-family: 'Syne', sans-serif;
    font-size: 2.8rem;
    font-weight: 800;
    line-height: 1;
}
.health-score-label {
    font-size: 0.68rem;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: var(--text-muted);
}

/* ── Timeline phase row ──────────────────────────────────── */
.phase-row {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 1rem;
    font-size: 0.82rem;
}
.phase-row-name { color: var(--text-muted); width: 160px; flex-shrink: 0; }
.phase-row-bar  { flex: 1; background: rgba(255,255,255,0.05); border-radius: 20px; height: 8px; overflow: hidden; }
.phase-row-fill { height: 100%; border-radius: 20px; }
.phase-row-pct  { color: var(--text-primary); font-weight: 600; width: 40px; text-align: right; font-family: 'Syne', sans-serif; font-size: 0.85rem; }

/* ── Streamlit overrides ─────────────────────────────────── */
hr { border-color: var(--border) !important; }
.stSelectbox label, .stRadio label {
    color: var(--text-muted) !important;
    font-size: 0.72rem !important;
    text-transform: uppercase;
    letter-spacing: 0.1em;
}
div[data-testid="stMetricValue"] { font-family: 'Syne', sans-serif; }
.stButton button {
    background: var(--orange);
    color: #000;
    border: none;
    font-weight: 700;
    border-radius: 10px;
    padding: 0.5rem 1.2rem;
}
/* Plotly container */
.js-plotly-plot .plotly { border-radius: 12px; }

/* ── Info box ────────────────────────────────────────────── */
.info-box {
    background: rgba(59,130,246,0.08);
    border: 1px solid rgba(59,130,246,0.2);
    border-radius: 10px;
    padding: 0.75rem 1rem;
    font-size: 0.8rem;
    color: #93c5fd;
    margin-bottom: 1rem;
}
</style>
"""
