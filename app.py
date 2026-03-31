import calendar
from datetime import date, timedelta
from pathlib import Path

import pandas as pd
import streamlit as st

st.set_page_config(page_title="Vacaciones del personal", page_icon="📅", layout="wide")

# Color único estilo iOS — azul sistema
CHIP_BG  = "#dbeafe"
CHIP_FG  = "#1d4ed8"


# ── CSS ───────────────────────────────────────────────────────────────────────
def inject_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..60,700;12..60,800&family=DM+Sans:wght@400;500;600&display=swap');

    html, body, [data-testid="stAppViewContainer"] { background:#eef2f7 !important; }
    .block-container {
        padding-top:1.4rem !important; padding-bottom:3rem !important;
        max-width:100% !important;
        padding-left:2.2rem !important; padding-right:2.2rem !important;
    }
    [data-testid="stHeader"], [data-testid="stToolbar"], footer { display:none !important; }

    .hero-title {
        font-family:'Bricolage Grotesque',sans-serif;
        font-size:2.5rem; font-weight:800; color:#0f172a;
        margin:0 0 0.2rem; letter-spacing:-0.04em; line-height:1.05;
    }
    .hero-sub {
        font-family:'DM Sans',sans-serif; color:#64748b;
        font-size:0.97rem; margin:0 0 1.1rem;
    }

    /* Toolbar — mismo card que los KPIs */
    .toolbar-wrap {
        background:#fff; border:1px solid #e2e8f0; border-radius:14px;
        padding:0.75rem 1rem; box-shadow:0 2px 8px rgba(15,23,42,.04);
        margin-bottom:0.9rem;
    }

    /* KPI cards */
    .metric-card {
        background:#fff; border:1px solid #e2e8f0; border-radius:14px;
        padding:1rem 1.25rem .9rem; box-shadow:0 2px 8px rgba(15,23,42,.04);
    }
    .metric-label { font-family:'DM Sans',sans-serif; color:#64748b; font-size:.84rem; font-weight:500; margin-bottom:.2rem; }
    .metric-value { font-family:'Bricolage Grotesque',sans-serif; color:#0f172a; font-size:2.1rem; font-weight:800; line-height:1; }
    .metric-period { font-family:'Bricolage Grotesque',sans-serif; font-size:1.4rem; font-weight:700; color:#0f172a; }
    .data-note { font-family:'DM Sans',sans-serif; font-size:.78rem; color:#94a3b8; margin-top:.3rem; }

    /* Calendario */
    .cal-outer {
        background:#fff; border:1px solid #e2e8f0; border-radius:18px;
        overflow:hidden; box-shadow:0 4px 20px rgba(15,23,42,.05); margin-top:0.9rem;
    }
    .cal-header { display:grid; grid-template-columns:repeat(7,1fr); background:#f8fafc; border-bottom:2px solid #e2e8f0; }
    .cal-wday {
        padding:.7rem .4rem; text-align:center; font-family:'DM Sans',sans-serif;
        font-size:.78rem; font-weight:600; color:#475569;
        letter-spacing:.06em; text-transform:uppercase;
        border-right:1px solid #edf2f7;
    }
    .cal-wday:last-child { border-right:none; }

    .cal-grid { display:grid; grid-template-columns:repeat(7,1fr); }

    .day-cell {
        min-height:150px; border-right:1px solid #edf2f7; border-bottom:1px solid #edf2f7;
        padding:.5rem 0 .4rem; background:#fff; overflow:hidden;
    }
    .day-cell:nth-child(7n) { border-right:none; }
    .day-cell.other  { background:#f9fafb; }
    .day-cell.today  { background:#f0f7ff; }

    .day-num-wrap { padding:0 .55rem; margin-bottom:.4rem; }
    .day-num {
        font-family:'Bricolage Grotesque',sans-serif; font-size:.9rem; font-weight:700; color:#1e293b;
        width:1.85rem; height:1.85rem; display:inline-flex; align-items:center;
        justify-content:center; border-radius:50%;
    }
    .other .day-num  { color:#cbd5e1; }
    .today .day-num  { background:#2563eb; color:#fff; }

    .chips-col { display:flex; flex-direction:column; gap:3px; padding:0 .45rem; }

    .chip {
        height:22px; display:flex; align-items:center;
        border-radius:6px; padding:0 8px;
        font-family:'DM Sans',sans-serif; font-size:.72rem; font-weight:600;
        white-space:nowrap; overflow:hidden; text-overflow:ellipsis;
        box-sizing:border-box;
        background:#dbeafe; color:#1d4ed8;
    }
    .other .chip { background:#e8f0fe; color:#4b6cb7; opacity:.6; }

    .empty-dash { font-family:'DM Sans',sans-serif; color:#e2e8f0; font-size:.75rem; padding:0 .55rem; }
    </style>
    """, unsafe_allow_html=True)


# ── Datos ─────────────────────────────────────────────────────────────────────
def locate_file():
    for fname, note in [("vacaciones.xlsx", "vacaciones.xlsx"), ("vacaciones_demo.xlsx", "archivo de ejemplo")]:
        p = Path(fname)
        if p.exists():
            return p, note
    raise FileNotFoundError("No se encontró 'vacaciones.xlsx' ni 'vacaciones_demo.xlsx'.")


@st.cache_data(show_spinner=False)
def load_data(path: str) -> pd.DataFrame:
    p = Path(path)
    df = pd.read_csv(p) if p.suffix.lower() == ".csv" else pd.read_excel(p)
    df.columns = [str(c).strip().lower() for c in df.columns]
    missing = {"nombre", "departamento", "fecha_desde", "fecha_hasta"} - set(df.columns)
    if missing:
        raise ValueError(f"Faltan columnas: {', '.join(sorted(missing))}")
    df = df[["nombre", "departamento", "fecha_desde", "fecha_hasta"]].copy()
    df["nombre"]       = df["nombre"].astype(str).str.strip()
    df["departamento"] = df["departamento"].astype(str).str.strip()
    df["fecha_desde"]  = pd.to_datetime(df["fecha_desde"], errors="coerce")
    df["fecha_hasta"]  = pd.to_datetime(df["fecha_hasta"], errors="coerce")
    df = df.dropna(subset=["nombre", "departamento", "fecha_desde", "fecha_hasta"])
    df = df[df["fecha_hasta"] >= df["fecha_desde"]]
    return df.sort_values(["fecha_desde", "nombre"]).reset_index(drop=True)


@st.cache_data(show_spinner=False)
def expand_days(df: pd.DataFrame) -> pd.DataFrame:
    """Expande cada rango a filas individuales por día."""
    rows = []
    for r in df.itertuples(index=False):
        d = r.fecha_desde.date()
        end = r.fecha_hasta.date()
        while d <= end:
            rows.append({"fecha": d, "nombre": r.nombre, "departamento": r.departamento})
            d += timedelta(days=1)
    if not rows:
        return pd.DataFrame(columns=["fecha", "nombre", "departamento"])
    return pd.DataFrame(rows)


# ── Sesión ────────────────────────────────────────────────────────────────────
def init_state():
    t = date.today()
    st.session_state.setdefault("year", t.year)
    st.session_state.setdefault("month", t.month)


def shift(y, m, d):
    m += d
    while m < 1:  m += 12; y -= 1
    while m > 12: m -= 12; y += 1
    return y, m


# ── Calendario HTML ───────────────────────────────────────────────────────────
def render_calendar(expanded: pd.DataFrame, year: int, month: int):
    first = date(year, month, 1)
    last  = date(year, month, calendar.monthrange(year, month)[1])

    month_df = expanded[(expanded["fecha"] >= first) & (expanded["fecha"] <= last)]
    by_day = (
        month_df.groupby("fecha")["nombre"]
        .apply(lambda x: sorted(x.unique().tolist()))
        .to_dict()
        if not month_df.empty else {}
    )

    today = date.today()
    wdays = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]

    p = ["<div class='cal-outer'><div class='cal-header'>"]
    for w in wdays:
        p.append(f"<div class='cal-wday'>{w}</div>")
    p.append("</div><div class='cal-grid'>")

    cal = calendar.Calendar(firstweekday=0)
    for week in cal.monthdatescalendar(year, month):
        for day in week:
            cls = "day-cell"
            if day.month != month: cls += " other"
            if day == today:       cls += " today"

            names = by_day.get(day, [])

            p.append(f"<div class='{cls}'>")
            p.append(f"<div class='day-num-wrap'><div class='day-num'>{day.day}</div></div>")
            p.append("<div class='chips-col'>")

            if names:
                for name in names:
                    safe = name.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
                    p.append(f"<div class='chip'>{safe}</div>")
            elif day.month == month:
                p.append("<div class='empty-dash'>—</div>")

            p.append("</div></div>")

    p.append("</div></div>")
    st.markdown("".join(p), unsafe_allow_html=True)


# ── Main ──────────────────────────────────────────────────────────────────────
MONTHS = ["Enero","Febrero","Marzo","Abril","Mayo","Junio",
          "Julio","Agosto","Septiembre","Octubre","Noviembre","Diciembre"]


def main():
    inject_css()
    init_state()

    st.markdown(
        "<div class='hero-title'>📅 Vacaciones del personal</div>"
        "<div class='hero-sub'>Calendario mensual · Visualiza quién está de vacaciones por fecha y departamento</div>",
        unsafe_allow_html=True,
    )

    try:
        fp, note = locate_file()
        df = load_data(str(fp))
    except Exception as e:
        st.error(str(e)); st.stop()

    expanded = expand_days(df)

    depts     = ["Todos"] + sorted(df["departamento"].dropna().unique().tolist())
    year_opts = list(range(max(2020, df["fecha_desde"].dt.year.min() - 1), df["fecha_hasta"].dt.year.max() + 2))

    # Toolbar
    st.markdown("<div class='toolbar-wrap'>", unsafe_allow_html=True)
    c1, c2, c3, c4, c5, c6 = st.columns([1, .65, 1, 1.8, .9, .9])
    with c1:
        if st.button("◀ Anterior", use_container_width=True):
            st.session_state.year, st.session_state.month = shift(st.session_state.year, st.session_state.month, -1)
            st.rerun()
    with c2:
        if st.button("Hoy", use_container_width=True):
            t = date.today(); st.session_state.year, st.session_state.month = t.year, t.month; st.rerun()
    with c3:
        if st.button("Siguiente ▶", use_container_width=True):
            st.session_state.year, st.session_state.month = shift(st.session_state.year, st.session_state.month, 1)
            st.rerun()
    with c4:
        dept = st.selectbox("Departamento", depts, index=0)
    with c5:
        cy = st.session_state.year
        sy = st.selectbox("Año", year_opts, index=year_opts.index(cy) if cy in year_opts else 0)
        if sy != st.session_state.year: st.session_state.year = sy
    with c6:
        sm = st.selectbox("Mes", list(range(1,13)), index=st.session_state.month-1, format_func=lambda x: MONTHS[x-1])
        if sm != st.session_state.month: st.session_state.month = sm
    st.markdown("</div>", unsafe_allow_html=True)

    year  = st.session_state.year
    month = st.session_state.month

    # Filtrar por departamento
    df_v = df if dept == "Todos" else df[df["departamento"] == dept].copy()
    exp_v = expanded if dept == "Todos" else expanded[expanded["departamento"] == dept].copy()

    # Métricas
    first = date(year, month, 1)
    last  = date(year, month, calendar.monthrange(year, month)[1])
    sub   = df_v[(df_v["fecha_desde"].dt.date <= last) & (df_v["fecha_hasta"].dt.date >= first)]
    pn, dn = sub["nombre"].nunique(), sub["departamento"].nunique()

    m1, m2, m3 = st.columns([1, 1, 2.5])
    with m1:
        st.markdown(f"<div class='metric-card'><div class='metric-label'>Personas en vacaciones</div><div class='metric-value'>{pn}</div></div>", unsafe_allow_html=True)
    with m2:
        st.markdown(f"<div class='metric-card'><div class='metric-label'>Departamentos impactados</div><div class='metric-value'>{dn}</div></div>", unsafe_allow_html=True)
    with m3:
        st.markdown(f"<div class='metric-card'><div class='metric-label'>Período visualizado</div><div class='metric-period'>{MONTHS[month-1]} {year}</div><div class='data-note'>Fuente: {note}</div></div>", unsafe_allow_html=True)

    # Calendario
    render_calendar(exp_v, year, month)


if __name__ == "__main__":
    main()
