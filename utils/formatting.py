from __future__ import annotations


def fmt_eur(v: float) -> str:
    return f"{v:,.0f} €".replace(",", " ")


def fmt_pct(v: float, decimals: int = 1) -> str:
    return f"{v:.{decimals}f}%"


def kpi_card(
    label: str,
    value: str,
    delta_text: str = "",
    delta_type: str = "neu",
    accent: str = "#f97316",
    pct: float | None = None,
    sub: str = "",
) -> str:
    delta_cls = f"delta-{delta_type}"
    arrow     = "↑ " if delta_type == "pos" else ("↓ " if delta_type == "neg" else "")
    parts = [
        f'<div class="kpi-card" style="--accent:{accent}">',
        f'<div class="kpi-label">{label}</div>',
        f'<div class="kpi-value">{value}</div>',
    ]
    if sub:
        parts.append(f'<div class="kpi-sub">{sub}</div>')
    if pct is not None:
        parts.append(
            f'<div class="kpi-bar-track">'
            f'<div class="kpi-bar-fill" style="width:{min(pct,100):.1f}%;background:{accent};"></div>'
            f'</div>'
        )
    if delta_text:
        parts.append(f'<div class="kpi-delta {delta_cls}">{arrow}{delta_text}</div>')
    parts.append("</div>")
    return "".join(parts)


def section_title(text: str, accent: str = "#f97316") -> str:
    return f'<div class="section-title" style="--accent:{accent}">{text}</div>'


def stat_row(label: str, value: str) -> str:
    return (
        f'<div class="stat-row">'
        f'<span class="stat-row-label">{label}</span>'
        f'<span class="stat-row-value">{value}</span>'
        f'</div>'
    )


def progress_bar(pct: float, color: str = "#f97316", height: int = 6) -> str:
    return (
        f'<div style="background:rgba(255,255,255,0.06);border-radius:20px;height:{height}px;overflow:hidden;margin:4px 0;">'
        f'<div style="background:{color};width:{min(pct,100):.1f}%;height:100%;border-radius:20px;"></div>'
        f'</div>'
    )


def badge(text: str, cls: str) -> str:
    return f'<span class="phase-badge {cls}">{text}</span>'
