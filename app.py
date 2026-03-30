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
# PALETA DE COLORES POR PERSONA
# =========================================================
PERSON_COLORS = [
    {"bg": "#dbeafe", "border": "#93c5fd", "text": "#1e3a5f"},  # azul
    {"bg": "#dcfce7", "border": "#86efac", "text": "#14532d"},  # verde
    {"bg": "#fef9c3", "border": "#fde047", "text": "#713f12"},  # amarillo
    {"bg": "#fce7f3", "border": "#f9a8d4", "text": "#831843"},  # rosa
    {"bg": "#ede9fe", "border": "#c4b5fd", "text": "#3b0764"},  # violeta
    {"bg": "#ffedd5", "border": "#fdba74", "text": "#7c2d12"},  # naranja
    {"bg": "#cffafe", "border": "#67e8f9", "text": "#164e63"},  # cyan
    {"bg": "#d1fae5", "border": "#6ee7b7", "text": "#064e3b"},  # esmeralda
    {"bg": "#fee2e2", "border": "#fca5a5", "text": "#7f1d1d"},  # rojo
    {"bg": "#e0e7ff", "border": "#a5b4fc", "text": "#312e81"},  # indigo
    {"bg": "#f0fdf4", "border": "#bbf7d0", "text": "#166534"},  # lima
    {"bg": "#fdf4ff", "border": "#e9d5ff", "text": "#581c87"},  # morado
]


@st.cache_data(show_spinner=False)
def build_color_map(names: tuple) -> dict:
    return {name: PERSON_COLORS[i % len(PERSON_COLORS)] for i, name in enumerate(sorted(names))}


# =========================================================
# ESTILOS
# =========================================================
def inject_css() -> None:
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:wght@400;600;700;800&family=DM+Sans:wght@400;500;600&display=swap');

        html, body, [data-testid="stAppViewContainer"] {
            background: #f0f4f8 !important;
        }

        .block-container {
            padding-top: 2.5rem !important;
            padding-bottom: 3rem !important;
            max-width: 100% !important;
            padding-left: 2rem !important;
            padding-right: 2rem !important;
        }

        [data-testid="stHeader"] {
            display: none !important;
        }

        .hero-wrap {
            margin-bottom: 1.8rem;
        }

        .hero-title {
            font-family: 'Bricolage Grotesque', sans-serif;
            font-size: 2.4rem;
            font-weight: 800;
            color: #0f172a;
            margin: 0 0 0.3rem 0;
            letter-spacing: -0.04em;
            line-height: 1.1;
        }

        .hero-subtitle {
            font-family: 'DM Sans', sans-serif;
            color: #64748b;
            font-size: 1rem;
            margin: 0;
        }

        .toolbar-wrap {
            background: #ffffff;
            border: 1px solid #e2e8f0;
            border-radius: 16px;
            padding: 0.85rem 1rem;
            box-shadow: 0 2px 12px rgba(15,23,42,0.04);
            margin-bottom: 1.2rem;
        }

        .metric-card {
            background: #ffffff;
            border: 1px solid #e2e8f0;
            border-radius: 16px;
            padding: 1rem 1.2rem;
            box-shadow: 0 2px 12px rgba(15,23,42,0.04);
            height: 100%;
        }

        .metric-label {
            font-family: 'DM Sans', sans-serif;
            color: #64748b;
            font-size: 0.88rem;
            font-weight: 500;
            margin-bottom: 0.3rem;
        }

        .metric-value {
            font-family: 'Bricolage Grotesque', sans-serif;
            color: #0f172a;
            font-size: 2rem;
            font-weight: 800;
            line-height: 1;
        }

        .metric-period {
            font-family: 'Bricolage Grotesque', sans-serif;
            font-size: 1.35rem;
            font-weight: 700;
            color: #0f172a;
        }

        .data-note {
            font-family: 'DM Sans', sans-serif;
            font-size: 0.8rem;
            color: #94a3b8;
            margin-top: 0.25rem;
        }

        /* ── CALENDARIO ─────────────────────────── */
        .cal-outer {
            background: #ffffff;
            border: 1px solid #e2e8f0;
            border-radius: 20px;
            overflow: hidden;
            box-shadow: 0 4px 24px rgba(15,23,42,0.05);
            margin-top: 1rem;
        }

        .cal-header {
            display: grid;
            grid-template-columns: repeat(7, 1fr);
            background: #f8fafc;
            border-bottom: 1px solid #e2e8f0;
        }

        .cal-weekday {
            padding: 0.8rem 0.5rem;
            text-align: center;
            font-family: 'DM Sans', sans-serif;
            font-size: 0.82rem;
            font-weight: 600;
            color: #64748b;
            letter-spacing: 0.03em;
            text-transform: uppercase;
            border-right: 1px solid #edf2f7;
        }

        .cal-weekday:last-child { border-right: none; }

        .cal-grid {
            display: grid;
            grid-template-columns: repeat(7, 1fr);
        }

        .day-cell {
            min-height: 140px;
            border-right: 1px solid #edf2f7;
            border-bottom: 1px solid #edf2f7;
            padding: 0.55rem 0.45rem 0.45rem 0.45rem;
            position: relative;
            background: #ffffff;
            overflow: hidden;
        }

        .day-cell:nth-child(7n) { border-right: none; }

        .day-cell.other-month { background: #f9fafb; }

        .day-cell.today {
            background: linear-gradient(160deg, #eff6ff 0%, #ffffff 60%);
        }

        .day-num {
            font-family: 'Bricolage Grotesque', sans-serif;
            font-size: 0.92rem;
            font-weight: 700;
            color: #1e293b;
            width: 1.9rem;
            height: 1.9rem;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            border-radius: 50%;
            margin-bottom: 0.4rem;
        }

        .other-month .day-num { color: #cbd5e1; }

        .today .day-num {
            background: #2563eb;
            color: #ffffff;
        }

        .events-col {
            display: flex;
            flex-direction: column;
            gap: 3px;
        }

        /* Chip genérico – color viene inline */
        .ev-chip {
            border-radius: 6px;
            padding: 3px 7px;
            font-family: 'DM Sans', sans-serif;
            font-size: 0.76rem;
            font-weight: 600;
            line-height: 1.3;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
            border-top: 2px solid transparent;
            border-bottom: 2px solid transparent;
        }

        /* Chip que abarca un rango: distintos bordes según posición */
        .ev-chip.span-start {
            border-radius: 8px 0 0 8px;
            border-left: 3px solid transparent;
            padding-right: 0;
            margin-right: -1px;
        }

        .ev-chip.span-middle {
            border-radius: 0;
            padding-left: 0;
            padding-right: 0;
            margin-left: -1px;
            margin-right: -1px;
        }

        .ev-chip.span-end {
            border-radius: 0 8px 8px 0;
            border-right: 3px solid transparent;
            padding-left: 0;
            margin-left: -1px;
        }

        .ev-chip.span-solo {
            border-radius: 8px;
        }

        .empty-cell {
            font-family: 'DM Sans', sans-serif;
            color: #e2e8f0;
            font-size: 0.78rem;
            margin-top: 0.3rem;
        }

        /* ── Leyenda ── */
        .legend-wrap {
            display: flex;
            flex-wrap: wrap;
            gap: 0.5rem 1rem;
            margin-top: 1.1rem;
            padding: 0.8rem 1rem;
            background: #ffffff;
            border: 1px solid #e2e8f0;
            border-radius: 14px;
        }

        .legend-item {
            display: flex;
            align-items: center;
            gap: 0.4rem;
            font-family: 'DM Sans', sans-serif;
            font-size: 0.82rem;
            font-weight: 500;
            color: #334155;
        }

        .legend-dot {
            width: 12px;
            height: 12px;
            border-radius: 3px;
            flex-shrink: 0;
        }

        /* Streamlit overrides */
        div[data-testid="stSelectbox"] label,
        div[data-testid="stButton"] button {
            font-family: 'DM Sans', sans-serif !important;
        }

        div[data-testid="stButton"] button {
            border-radius: 10px !important;
            font-weight: 600 !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


# =========================================================
# CARGA DE DATOS
# =========================================================
def locate_data_file() -> tuple[Path, str]:
    real_file = Path("vacaciones.xlsx")
    demo_file = Path("vacaciones_demo.xlsx")
    if real_file.exists():
        return real_file, "Archivo local: vacaciones.xlsx"
    if demo_file.exists():
        return demo_file, "Usando archivo de ejemplo: vacaciones_demo.xlsx"
    raise FileNotFoundError(
        "No se encontró 'vacaciones.xlsx' ni 'vacaciones_demo.xlsx'."
    )


@st.cache_data(show_spinner=False)
def load_data(file_path: str) -> pd.DataFrame:
    path = Path(file_path)
    df = pd.read_csv(path) if path.suffix.lower() == ".csv" else pd.read_excel(path)
    df.columns = [str(c).strip().lower() for c in df.columns]
    expected = {"nombre", "departamento", "fecha_desde", "fecha_hasta"}
    missing = expected - set(df.columns)
    if missing:
        raise ValueError(f"Faltan columnas: {', '.join(sorted(missing))}")
    df = df[["nombre", "departamento", "fecha_desde", "fecha_hasta"]].copy()
    df["nombre"] = df["nombre"].astype(str).str.strip()
    df["departamento"] = df["departamento"].astype(str).str.strip()
    df["fecha_desde"] = pd.to_datetime(df["fecha_desde"], errors="coerce")
    df["fecha_hasta"] = pd.to_datetime(df["fecha_hasta"], errors="coerce")
    df = df.dropna(subset=["nombre", "departamento", "fecha_desde", "fecha_hasta"])
    df = df[df["fecha_hasta"] >= df["fecha_desde"]]
    return df.sort_values(["fecha_desde", "nombre"]).reset_index(drop=True)


# =========================================================
# ESTADO DE SESIÓN
# =========================================================
def init_session_state() -> None:
    today = date.today()
    if "selected_year" not in st.session_state:
        st.session_state.selected_year = today.year
    if "selected_month" not in st.session_state:
        st.session_state.selected_month = today.month


def shift_month(year: int, month: int, offset: int) -> tuple[int, int]:
    m, y = month + offset, year
    while m < 1:
        m += 12; y -= 1
    while m > 12:
        m -= 12; y += 1
    return y, m


# =========================================================
# CÁLCULO DE EVENTOS PARA EL CALENDARIO (estilo "span")
# =========================================================
def build_span_events(df: pd.DataFrame, year: int, month: int) -> dict[date, list[dict]]:
    """
    Para cada día del mes devuelve una lista de eventos ordenados por persona.
    Cada evento tiene:
      name, color, position: 'start'|'middle'|'end'|'solo', show_label: bool
    """
    first = date(year, month, 1)
    last = date(year, month, calendar.monthrange(year, month)[1])

    # Filtrar vacaciones que intersectan el mes
    relevant = df[
        (df["fecha_desde"].dt.date <= last) & (df["fecha_hasta"].dt.date >= first)
    ].copy()

    if relevant.empty:
        return {}

    all_names = tuple(df["nombre"].unique())
    color_map = build_color_map(all_names)

    # Por cada persona–rango, generar chips para cada día visible
    day_events: dict[date, list[dict]] = {}

    for row in relevant.itertuples(index=False):
        start = max(row.fecha_desde.date(), first)
        end = min(row.fecha_hasta.date(), last)
        true_start = row.fecha_desde.date()
        true_end = row.fecha_hasta.date()
        person = row.nombre
        color = color_map[person]

        current = start
        while current <= end:
            is_start = (current == true_start)
            is_end = (current == true_end)

            if is_start and is_end:
                pos = "solo"
            elif is_start:
                pos = "start"
            elif is_end:
                pos = "end"
            else:
                pos = "middle"

            show_label = pos in ("start", "solo")

            if current not in day_events:
                day_events[current] = []
            day_events[current].append({
                "name": person,
                "color": color,
                "position": pos,
                "show_label": show_label,
            })
            current += timedelta(days=1)

    # Ordenar cada día por nombre para consistencia visual
    for d in day_events:
        day_events[d].sort(key=lambda e: e["name"])

    return day_events


# =========================================================
# RENDER DEL CALENDARIO
# =========================================================
def _chip_html(ev: dict) -> str:
    c = ev["color"]
    pos = ev["position"]
    label = ev["name"] if ev["show_label"] else "&nbsp;"
    safe = label.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    style = (
        f"background:{c['bg']};"
        f"border-color:{c['border']};"
        f"color:{c['text']};"
    )
    return f"<div class='ev-chip span-{pos}' style='{style}'>{safe}</div>"


def render_month_calendar(
    df: pd.DataFrame,
    year: int,
    month: int,
) -> None:
    cal = calendar.Calendar(firstweekday=0)
    month_weeks = list(cal.monthdatescalendar(year, month))
    today = date.today()
    day_events = build_span_events(df, year, month)

    weekday_names = ["Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom"]

    html = ["<div class='cal-outer'>"]

    # Cabecera días de semana
    html.append("<div class='cal-header'>")
    for wn in weekday_names:
        html.append(f"<div class='cal-weekday'>{wn}</div>")
    html.append("</div>")

    # Grid de días
    html.append("<div class='cal-grid'>")
    for week in month_weeks:
        for day in week:
            classes = "day-cell"
            if day.month != month:
                classes += " other-month"
            if day == today:
                classes += " today"

            events = day_events.get(day, [])

            html.append(f"<div class='{classes}'>")
            html.append(f"<div class='day-num'>{day.day}</div>")
            html.append("<div class='events-col'>")

            if events:
                for ev in events:
                    html.append(_chip_html(ev))
            elif day.month == month:
                html.append("<div class='empty-cell'>—</div>")

            html.append("</div></div>")

    html.append("</div></div>")
    st.markdown("".join(html), unsafe_allow_html=True)


# =========================================================
# LEYENDA DE COLORES
# =========================================================
def render_legend(df: pd.DataFrame, year: int, month: int) -> None:
    first = date(year, month, 1)
    last = date(year, month, calendar.monthrange(year, month)[1])
    in_month = df[
        (df["fecha_desde"].dt.date <= last) & (df["fecha_hasta"].dt.date >= first)
    ]["nombre"].unique()

    if len(in_month) == 0:
        return

    all_names = tuple(df["nombre"].unique())
    color_map = build_color_map(all_names)

    items_html = ""
    for name in sorted(in_month):
        c = color_map[name]
        safe = name.replace("&", "&amp;")
        items_html += (
            f"<div class='legend-item'>"
            f"<div class='legend-dot' style='background:{c[\"bg\"]};border:2px solid {c[\"border\"]};'></div>"
            f"{safe}</div>"
        )

    st.markdown(
        f"<div class='legend-wrap'>{items_html}</div>",
        unsafe_allow_html=True,
    )


# =========================================================
# MÉTRICAS
# =========================================================
def build_month_summary(df: pd.DataFrame, year: int, month: int) -> tuple[int, int]:
    first = date(year, month, 1)
    last = date(year, month, calendar.monthrange(year, month)[1])
    in_month = df[
        (df["fecha_desde"].dt.date <= last) & (df["fecha_hasta"].dt.date >= first)
    ]
    return in_month["nombre"].nunique(), in_month["departamento"].nunique()


# =========================================================
# APLICACIÓN PRINCIPAL
# =========================================================
def main() -> None:
    inject_css()
    init_session_state()

    # ── Hero ──────────────────────────────────────────────
    st.markdown(
        """
        <div class='hero-wrap'>
            <div class='hero-title'>📅 Vacaciones del personal</div>
            <div class='hero-subtitle'>Calendario mensual · Visualiza quién está de vacaciones por fecha y departamento</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── Carga de datos ────────────────────────────────────
    try:
        file_path, file_note = locate_data_file()
        df = load_data(str(file_path))
    except Exception as exc:
        st.error(f"No fue posible cargar los datos: {exc}")
        st.stop()

    departments = ["Todos"] + sorted(df["departamento"].dropna().unique().tolist())
    year_min = max(2020, df["fecha_desde"].dt.year.min() - 1)
    year_max = df["fecha_hasta"].dt.year.max() + 2
    year_options = list(range(year_min, year_max))
    month_options = list(range(1, 13))
    month_names = ["Enero","Febrero","Marzo","Abril","Mayo","Junio",
                   "Julio","Agosto","Septiembre","Octubre","Noviembre","Diciembre"]

    # ── Toolbar ───────────────────────────────────────────
    st.markdown("<div class='toolbar-wrap'>", unsafe_allow_html=True)
    c1, c2, c3, c4, c5, c6 = st.columns([1, 0.7, 1, 1.8, 1, 1])

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
        selected_dept = st.selectbox("Departamento", departments, index=0)
    with c5:
        sel_year = st.selectbox(
            "Año", year_options,
            index=year_options.index(st.session_state.selected_year)
            if st.session_state.selected_year in year_options else 0,
        )
        if sel_year != st.session_state.selected_year:
            st.session_state.selected_year = sel_year
    with c6:
        sel_month = st.selectbox(
            "Mes", month_options,
            index=st.session_state.selected_month - 1,
            format_func=lambda x: month_names[x - 1],
        )
        if sel_month != st.session_state.selected_month:
            st.session_state.selected_month = sel_month

    st.markdown("</div>", unsafe_allow_html=True)

    year = st.session_state.selected_year
    month = st.session_state.selected_month

    # Filtrar por departamento
    df_filtered = df if selected_dept == "Todos" else df[df["departamento"] == selected_dept].copy()

    # ── Métricas ──────────────────────────────────────────
    people_count, dept_count = build_month_summary(df_filtered, year, month)

    m1, m2, m3 = st.columns([1, 1, 2.5])
    with m1:
        st.markdown(
            f"<div class='metric-card'>"
            f"<div class='metric-label'>Personas en vacaciones</div>"
            f"<div class='metric-value'>{people_count}</div>"
            f"</div>",
            unsafe_allow_html=True,
        )
    with m2:
        st.markdown(
            f"<div class='metric-card'>"
            f"<div class='metric-label'>Departamentos impactados</div>"
            f"<div class='metric-value'>{dept_count}</div>"
            f"</div>",
            unsafe_allow_html=True,
        )
    with m3:
        st.markdown(
            f"<div class='metric-card'>"
            f"<div class='metric-label'>Período visualizado</div>"
            f"<div class='metric-period'>{month_names[month-1]} {year}</div>"
            f"<div class='data-note'>{file_note}</div>"
            f"</div>",
            unsafe_allow_html=True,
        )

    # ── Calendario ────────────────────────────────────────
    render_month_calendar(df_filtered, year, month)

    # ── Leyenda ───────────────────────────────────────────
    render_legend(df_filtered, year, month)

    # ── Tabla detalle ─────────────────────────────────────
    first_day = date(year, month, 1)
    last_day = date(year, month, calendar.monthrange(year, month)[1])
    detail = df_filtered[
        (df_filtered["fecha_desde"].dt.date <= last_day)
        & (df_filtered["fecha_hasta"].dt.date >= first_day)
    ].copy()

    with st.expander("Ver detalle del mes en tabla", expanded=False):
        if detail.empty:
            st.info("No hay vacaciones registradas para el filtro y mes seleccionados.")
        else:
            detail_show = detail.copy()
            detail_show["fecha_desde"] = detail_show["fecha_desde"].dt.strftime("%Y-%m-%d")
            detail_show["fecha_hasta"] = detail_show["fecha_hasta"].dt.strftime("%Y-%m-%d")
            detail_show = detail_show.rename(columns={
                "nombre": "Nombre",
                "departamento": "Departamento",
                "fecha_desde": "Fecha desde",
                "fecha_hasta": "Fecha hasta",
            })
            st.dataframe(detail_show, use_container_width=True, hide_index=True)


if __name__ == "__main__":
    main()
