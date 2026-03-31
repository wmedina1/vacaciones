import calendar
from datetime import date, timedelta
from pathlib import Path

import pandas as pd
import streamlit as st

# =========================================================
# CONFIGURACIÓN GENERAL
# =========================================================
st.set_page_config(
    page_title="Vacaciones del personal",
    page_icon="📅",
    layout="wide",
)

# =========================================================
# PALETA DE COLORES
# =========================================================
PERSON_COLORS = [
    {"bar": "#bfdbfe", "border": "#3b82f6", "text": "#1e3a5f"},
    {"bar": "#bbf7d0", "border": "#22c55e", "text": "#14532d"},
    {"bar": "#fde68a", "border": "#f59e0b", "text": "#78350f"},
    {"bar": "#fbcfe8", "border": "#ec4899", "text": "#831843"},
    {"bar": "#ddd6fe", "border": "#8b5cf6", "text": "#3b0764"},
    {"bar": "#fed7aa", "border": "#f97316", "text": "#7c2d12"},
    {"bar": "#a5f3fc", "border": "#06b6d4", "text": "#164e63"},
    {"bar": "#6ee7b7", "border": "#10b981", "text": "#064e3b"},
    {"bar": "#fca5a5", "border": "#ef4444", "text": "#7f1d1d"},
    {"bar": "#c7d2fe", "border": "#6366f1", "text": "#312e81"},
    {"bar": "#d9f99d", "border": "#84cc16", "text": "#365314"},
    {"bar": "#e9d5ff", "border": "#a855f7", "text": "#581c87"},
]


@st.cache_data(show_spinner=False)
def build_color_map(names: tuple) -> dict:
    return {name: PERSON_COLORS[i % len(PERSON_COLORS)] for i, name in enumerate(sorted(names))}


# =========================================================
# CSS
# =========================================================
def inject_css() -> None:
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..60,700;12..60,800&family=DM+Sans:wght@400;500;600&display=swap');

        html, body, [data-testid="stAppViewContainer"] {
            background: #eef2f7 !important;
        }
        .block-container {
            padding-top: 2.8rem !important;
            padding-bottom: 3rem !important;
            max-width: 100% !important;
            padding-left: 2.2rem !important;
            padding-right: 2.2rem !important;
        }
        [data-testid="stHeader"]  { display: none !important; }
        [data-testid="stToolbar"] { display: none !important; }
        footer { display: none !important; }

        /* Hero */
        .hero-wrap { margin-bottom: 1.6rem; }
        .hero-title {
            font-family: 'Bricolage Grotesque', sans-serif;
            font-size: 2.6rem;
            font-weight: 800;
            color: #0f172a;
            margin: 0 0 0.25rem 0;
            letter-spacing: -0.04em;
            line-height: 1.05;
        }
        .hero-sub {
            font-family: 'DM Sans', sans-serif;
            color: #64748b;
            font-size: 0.97rem;
            margin: 0;
        }

        /* Toolbar */
        .toolbar-wrap {
            background: #ffffff;
            border: 1px solid #e2e8f0;
            border-radius: 14px;
            padding: 0.8rem 1rem;
            box-shadow: 0 2px 8px rgba(15,23,42,0.04);
            margin-bottom: 1.1rem;
        }

        /* Metric cards */
        .metric-card {
            background: #ffffff;
            border: 1px solid #e2e8f0;
            border-radius: 14px;
            padding: 1rem 1.25rem 0.9rem;
            box-shadow: 0 2px 8px rgba(15,23,42,0.04);
            height: 100%;
        }
        .metric-label {
            font-family: 'DM Sans', sans-serif;
            color: #64748b;
            font-size: 0.84rem;
            font-weight: 500;
            margin-bottom: 0.25rem;
        }
        .metric-value {
            font-family: 'Bricolage Grotesque', sans-serif;
            color: #0f172a;
            font-size: 2.1rem;
            font-weight: 800;
            line-height: 1;
        }
        .metric-period {
            font-family: 'Bricolage Grotesque', sans-serif;
            font-size: 1.4rem;
            font-weight: 700;
            color: #0f172a;
            line-height: 1.15;
        }
        .data-note {
            font-family: 'DM Sans', sans-serif;
            font-size: 0.78rem;
            color: #94a3b8;
            margin-top: 0.3rem;
        }

        /* Calendario */
        .cal-outer {
            background: #ffffff;
            border: 1px solid #e2e8f0;
            border-radius: 18px;
            overflow: hidden;
            box-shadow: 0 4px 20px rgba(15,23,42,0.05);
            margin-top: 1rem;
        }
        .cal-header {
            display: grid;
            grid-template-columns: repeat(7, 1fr);
            background: #f8fafc;
            border-bottom: 2px solid #e2e8f0;
        }
        .cal-weekday {
            padding: 0.75rem 0.4rem;
            text-align: center;
            font-family: 'DM Sans', sans-serif;
            font-size: 0.78rem;
            font-weight: 600;
            color: #475569;
            letter-spacing: 0.06em;
            text-transform: uppercase;
            border-right: 1px solid #edf2f7;
        }
        .cal-weekday:last-child { border-right: none; }

        .cal-grid {
            display: grid;
            grid-template-columns: repeat(7, 1fr);
        }

        /* Celda */
        .day-cell {
            min-height: 148px;
            border-right: 1px solid #edf2f7;
            border-bottom: 1px solid #edf2f7;
            padding: 0.5rem 0 0.4rem 0;
            background: #ffffff;
            overflow: hidden;
        }
        .day-cell:nth-child(7n) { border-right: none; }
        .day-cell.other-month   { background: #f9fafb; }
        .day-cell.today         { background: #f0f7ff; }

        .day-num-wrap { padding: 0 0.55rem; margin-bottom: 0.45rem; }
        .day-num {
            font-family: 'Bricolage Grotesque', sans-serif;
            font-size: 0.9rem;
            font-weight: 700;
            color: #1e293b;
            width: 1.85rem;
            height: 1.85rem;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            border-radius: 50%;
        }
        .other-month .day-num { color: #cbd5e1; }
        .today .day-num { background: #2563eb; color: #ffffff; }

        .events-col {
            display: flex;
            flex-direction: column;
            gap: 3px;
        }

        /* ── Barras de vacaciones ──
         *
         *  pos-solo   → pill completo, margen en ambos lados
         *  pos-start  → redondeado izquierda, se extiende al borde derecho de la celda
         *  pos-middle → barra plana de borde a borde
         *  pos-end    → redondeado derecha, viene del borde izquierdo de la celda
         *
         *  El nombre aparece en TODOS los días.
         */
        .ev-bar {
            height: 23px;
            display: flex;
            align-items: center;
            font-family: 'DM Sans', sans-serif;
            font-size: 0.72rem;
            font-weight: 600;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
            box-sizing: border-box;
            line-height: 1;
        }

        .ev-bar.pos-solo {
            border-radius: 6px;
            margin-left: 0.5rem;
            margin-right: 0.5rem;
            padding: 0 8px;
        }
        .ev-bar.pos-start {
            border-radius: 6px 0 0 6px;
            margin-left: 0.5rem;
            margin-right: 0;
            padding-left: 8px;
            padding-right: 4px;
        }
        .ev-bar.pos-middle {
            border-radius: 0;
            margin-left: 0;
            margin-right: 0;
            padding-left: 6px;
            padding-right: 4px;
        }
        .ev-bar.pos-end {
            border-radius: 0 6px 6px 0;
            margin-left: 0;
            margin-right: 0.5rem;
            padding-left: 6px;
            padding-right: 8px;
        }

        .empty-dash {
            font-family: 'DM Sans', sans-serif;
            color: #e2e8f0;
            font-size: 0.75rem;
            padding: 0 0.55rem;
        }

        /* Leyenda */
        .legend-outer {
            display: flex;
            flex-wrap: wrap;
            gap: 0.45rem 1rem;
            margin-top: 1rem;
            padding: 0.8rem 1.1rem;
            background: #ffffff;
            border: 1px solid #e2e8f0;
            border-radius: 14px;
            box-shadow: 0 2px 8px rgba(15,23,42,0.03);
        }
        .legend-item {
            display: flex;
            align-items: center;
            gap: 0.45rem;
            font-family: 'DM Sans', sans-serif;
            font-size: 0.82rem;
            font-weight: 500;
            color: #334155;
        }
        .legend-swatch {
            width: 14px;
            height: 14px;
            border-radius: 4px;
            flex-shrink: 0;
            border: 2px solid transparent;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


# =========================================================
# CARGA DE DATOS
# =========================================================
def locate_data_file() -> tuple[Path, str]:
    for fname, note in [
        ("vacaciones.xlsx", "Archivo local: vacaciones.xlsx"),
        ("vacaciones_demo.xlsx", "Usando archivo de ejemplo"),
    ]:
        p = Path(fname)
        if p.exists():
            return p, note
    raise FileNotFoundError("No se encontró 'vacaciones.xlsx' ni 'vacaciones_demo.xlsx'.")


@st.cache_data(show_spinner=False)
def load_data(file_path: str) -> pd.DataFrame:
    path = Path(file_path)
    df = pd.read_csv(path) if path.suffix.lower() == ".csv" else pd.read_excel(path)
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


# =========================================================
# SESIÓN / NAVEGACIÓN
# =========================================================
def init_session_state() -> None:
    t = date.today()
    st.session_state.setdefault("selected_year", t.year)
    st.session_state.setdefault("selected_month", t.month)


def shift_month(year: int, month: int, delta: int) -> tuple[int, int]:
    m, y = month + delta, year
    while m < 1:  m += 12; y -= 1
    while m > 12: m -= 12; y += 1
    return y, m


# =========================================================
# POSICIÓN DE BARRA POR DÍA
# =========================================================
def bar_position(
    current: date,
    true_start: date,
    true_end: date,
    month_first: date,
    month_last: date,
    week: list[date],
) -> str:
    """
    Calcula si este día es inicio, medio, fin o evento de un día (solo)
    de la barra, teniendo en cuenta:
      - El límite real del rango (true_start / true_end)
      - El límite del mes visible (month_first / month_last)
      - El límite de la fila/semana (week[0] / week[-1])
    Así los rangos que cruzan semanas o meses se cortan y reinician
    correctamente fila a fila.
    """
    vis_start = max(true_start, month_first)
    vis_end   = min(true_end,   month_last)

    # Segmento dentro de esta semana
    seg_start = max(vis_start, week[0])
    seg_end   = min(vis_end,   week[-1])

    is_start = current == seg_start
    is_end   = current == seg_end

    if is_start and is_end:
        return "solo"
    if is_start:
        return "start"
    if is_end:
        return "end"
    return "middle"


# =========================================================
# CONSTRUIR EVENTOS POR DÍA
# =========================================================
def build_day_events(df: pd.DataFrame, year: int, month: int) -> dict[date, list[dict]]:
    month_first = date(year, month, 1)
    month_last  = date(year, month, calendar.monthrange(year, month)[1])

    relevant = df[
        (df["fecha_desde"].dt.date <= month_last)
        & (df["fecha_hasta"].dt.date >= month_first)
    ].copy()

    if relevant.empty:
        return {}

    color_map = build_color_map(tuple(df["nombre"].unique()))

    # Mapear día → semana
    cal = calendar.Calendar(firstweekday=0)
    day_to_week: dict[date, list[date]] = {}
    for week in cal.monthdatescalendar(year, month):
        for d in week:
            day_to_week[d] = week

    day_events: dict[date, list[dict]] = {}

    for row in relevant.itertuples(index=False):
        true_start = row.fecha_desde.date()
        true_end   = row.fecha_hasta.date()
        person     = row.nombre
        color      = color_map[person]

        seg_start = max(true_start, month_first)
        seg_end   = min(true_end, month_last)

        current = seg_start
        while current <= seg_end:
            week = day_to_week.get(current)
            if week is None:
                current += timedelta(days=1)
                continue

            pos = bar_position(current, true_start, true_end, month_first, month_last, week)
            day_events.setdefault(current, []).append({
                "name":     person,
                "color":    color,
                "position": pos,
            })
            current += timedelta(days=1)

    for d in day_events:
        day_events[d].sort(key=lambda e: e["name"])

    return day_events


# =========================================================
# HTML DE UNA BARRA
# =========================================================
def _bar_html(ev: dict) -> str:
    c    = ev["color"]
    pos  = ev["position"]
    bar  = c["bar"]
    bdr  = c["border"]
    txt  = c["text"]
    name = (
        ev["name"]
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )
    # Borde izquierdo de acento solo en inicio / evento de un día
    accent = f"border-left:3px solid {bdr};" if pos in ("start", "solo") else ""
    style  = f"background:{bar};color:{txt};{accent}"
    return f"<div class='ev-bar pos-{pos}' style='{style}'>{name}</div>"


# =========================================================
# RENDER CALENDARIO
# =========================================================
def render_calendar(df: pd.DataFrame, year: int, month: int) -> None:
    cal   = calendar.Calendar(firstweekday=0)
    weeks = list(cal.monthdatescalendar(year, month))
    today = date.today()
    evts  = build_day_events(df, year, month)

    days_es = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]

    p = ["<div class='cal-outer'>"]

    p.append("<div class='cal-header'>")
    for d in days_es:
        p.append(f"<div class='cal-weekday'>{d}</div>")
    p.append("</div>")

    p.append("<div class='cal-grid'>")
    for week in weeks:
        for day in week:
            cls = "day-cell"
            if day.month != month: cls += " other-month"
            if day == today:       cls += " today"

            bars = evts.get(day, [])

            p.append(f"<div class='{cls}'>")
            p.append(f"<div class='day-num-wrap'><div class='day-num'>{day.day}</div></div>")
            p.append("<div class='events-col'>")

            if bars:
                for ev in bars:
                    p.append(_bar_html(ev))
            elif day.month == month:
                p.append("<div class='empty-dash'>—</div>")

            p.append("</div></div>")

    p.append("</div></div>")
    st.markdown("".join(p), unsafe_allow_html=True)


# =========================================================
# LEYENDA
# =========================================================
def render_legend(df: pd.DataFrame, year: int, month: int) -> None:
    first = date(year, month, 1)
    last  = date(year, month, calendar.monthrange(year, month)[1])
    names = df[
        (df["fecha_desde"].dt.date <= last) & (df["fecha_hasta"].dt.date >= first)
    ]["nombre"].unique()

    if not len(names):
        return

    color_map = build_color_map(tuple(df["nombre"].unique()))
    items = ""
    for name in sorted(names):
        c    = color_map[name]
        safe = name.replace("&", "&amp;")
        bar  = c["bar"]
        bdr  = c["border"]
        items += (
            f"<div class='legend-item'>"
            f"<div class='legend-swatch' style='background:{bar};border-color:{bdr};'></div>"
            f"{safe}</div>"
        )
    st.markdown(f"<div class='legend-outer'>{items}</div>", unsafe_allow_html=True)


# =========================================================
# MÉTRICAS
# =========================================================
def month_summary(df: pd.DataFrame, year: int, month: int) -> tuple[int, int]:
    first = date(year, month, 1)
    last  = date(year, month, calendar.monthrange(year, month)[1])
    sub   = df[(df["fecha_desde"].dt.date <= last) & (df["fecha_hasta"].dt.date >= first)]
    return sub["nombre"].nunique(), sub["departamento"].nunique()


# =========================================================
# MAIN
# =========================================================
MONTH_NAMES = [
    "Enero","Febrero","Marzo","Abril","Mayo","Junio",
    "Julio","Agosto","Septiembre","Octubre","Noviembre","Diciembre",
]


def main() -> None:
    inject_css()
    init_session_state()

    st.markdown(
        "<div class='hero-wrap'>"
        "<div class='hero-title'>📅 Vacaciones del personal</div>"
        "<div class='hero-sub'>Calendario mensual · Visualiza quién está de vacaciones por fecha y departamento</div>"
        "</div>",
        unsafe_allow_html=True,
    )

    try:
        file_path, file_note = locate_data_file()
        df = load_data(str(file_path))
    except Exception as exc:
        st.error(f"No fue posible cargar los datos: {exc}")
        st.stop()

    depts     = ["Todos"] + sorted(df["departamento"].dropna().unique().tolist())
    year_min  = max(2020, df["fecha_desde"].dt.year.min() - 1)
    year_max  = df["fecha_hasta"].dt.year.max() + 2
    year_opts = list(range(year_min, year_max))

    # Toolbar
    st.markdown("<div class='toolbar-wrap'>", unsafe_allow_html=True)
    c1, c2, c3, c4, c5, c6 = st.columns([1, 0.65, 1, 1.8, 0.9, 0.9])

    with c1:
        if st.button("◀ Anterior", use_container_width=True):
            y, m = shift_month(st.session_state.selected_year, st.session_state.selected_month, -1)
            st.session_state.selected_year, st.session_state.selected_month = y, m
            st.rerun()
    with c2:
        if st.button("Hoy", use_container_width=True):
            t = date.today()
            st.session_state.selected_year, st.session_state.selected_month = t.year, t.month
            st.rerun()
    with c3:
        if st.button("Siguiente ▶", use_container_width=True):
            y, m = shift_month(st.session_state.selected_year, st.session_state.selected_month, 1)
            st.session_state.selected_year, st.session_state.selected_month = y, m
            st.rerun()
    with c4:
        selected_dept = st.selectbox("Departamento", depts, index=0)
    with c5:
        cur_y = st.session_state.selected_year
        sel_y = st.selectbox("Año", year_opts, index=year_opts.index(cur_y) if cur_y in year_opts else 0)
        if sel_y != st.session_state.selected_year:
            st.session_state.selected_year = sel_y
    with c6:
        sel_m = st.selectbox(
            "Mes", list(range(1, 13)),
            index=st.session_state.selected_month - 1,
            format_func=lambda x: MONTH_NAMES[x - 1],
        )
        if sel_m != st.session_state.selected_month:
            st.session_state.selected_month = sel_m

    st.markdown("</div>", unsafe_allow_html=True)

    year  = st.session_state.selected_year
    month = st.session_state.selected_month
    df_v  = df if selected_dept == "Todos" else df[df["departamento"] == selected_dept].copy()

    # Métricas
    pn, dn = month_summary(df_v, year, month)
    m1, m2, m3 = st.columns([1, 1, 2.5])
    with m1:
        st.markdown(
            f"<div class='metric-card'><div class='metric-label'>Personas en vacaciones</div>"
            f"<div class='metric-value'>{pn}</div></div>",
            unsafe_allow_html=True,
        )
    with m2:
        st.markdown(
            f"<div class='metric-card'><div class='metric-label'>Departamentos impactados</div>"
            f"<div class='metric-value'>{dn}</div></div>",
            unsafe_allow_html=True,
        )
    with m3:
        st.markdown(
            f"<div class='metric-card'><div class='metric-label'>Período visualizado</div>"
            f"<div class='metric-period'>{MONTH_NAMES[month-1]} {year}</div>"
            f"<div class='data-note'>{file_note}</div></div>",
            unsafe_allow_html=True,
        )

    render_calendar(df_v, year, month)
    render_legend(df_v, year, month)


if __name__ == "__main__":
    main()
