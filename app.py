import base64
import calendar
from datetime import date, timedelta
from pathlib import Path

import pandas as pd
import streamlit as st


# =========================================================
# CONFIGURACIÓN GENERAL
# =========================================================
st.set_page_config(
    page_title="RRHH | Vacaciones del Personal",
    page_icon="📅",
    layout="wide",
)


# =========================================================
# PALETA DE COLORES POR PERSONA
# Más sobria / menos encendida
# =========================================================
PERSON_COLORS = [
    {"bg": "#e8eef5", "border": "#c8d4e3", "text": "#334155"},  # azul grisáceo
    {"bg": "#eaf3ee", "border": "#c8ddcf", "text": "#355244"},  # verde suave
    {"bg": "#f4efe6", "border": "#ded2bb", "text": "#5b4b32"},  # beige
    {"bg": "#f2eaf0", "border": "#dcc9d8", "text": "#5b4252"},  # malva suave
    {"bg": "#eceaf5", "border": "#cfcae2", "text": "#4b4865"},  # violeta gris
    {"bg": "#f5ece6", "border": "#dfcbbc", "text": "#65493a"},  # terracota suave
    {"bg": "#e8f1f2", "border": "#c7dbde", "text": "#35525a"},  # teal suave
    {"bg": "#edf3ec", "border": "#d1ddd0", "text": "#425244"},  # oliva suave
    {"bg": "#f4eaea", "border": "#e0caca", "text": "#5e4242"},  # rojo polvo
    {"bg": "#eceff5", "border": "#cfd6e2", "text": "#3f4a63"},  # índigo suave
    {"bg": "#f3f4ea", "border": "#dfe1cb", "text": "#55593b"},  # lima suave
    {"bg": "#f3edf4", "border": "#ddd0df", "text": "#58455d"},  # morado suave
]


@st.cache_data(show_spinner=False)
def build_color_map(names: tuple) -> dict:
    return {name: PERSON_COLORS[i % len(PERSON_COLORS)] for i, name in enumerate(sorted(names))}


# =========================================================
# UTILIDAD PARA CARGAR LOGO
# =========================================================
def image_to_base64(image_path: str) -> str:
    path = Path(image_path)
    if not path.exists():
        return ""
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()


# =========================================================
# ESTILOS
# =========================================================
def inject_css() -> None:
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:wght@400;600;700;800&family=DM+Sans:wght@400;500;600&display=swap');

        html, body, [data-testid="stAppViewContainer"] {
            background: #eef2f5 !important;
        }

        .block-container {
            padding-top: 2.8rem !important;
            padding-bottom: 2rem !important;
            max-width: 100% !important;
            padding-left: 1.8rem !important;
            padding-right: 1.8rem !important;
        }

        [data-testid="stHeader"] {
            display: none !important;
        }

        .hero-wrap {
            display: flex;
            align-items: center;
            gap: 16px;
            margin-bottom: 1.45rem;
        }

        .hero-logo {
            width: 74px;
            height: 74px;
            object-fit: contain;
            background: #ffffff;
            border: 1px solid #dde5ec;
            border-radius: 16px;
            padding: 8px;
            box-shadow: 0 2px 10px rgba(15,23,42,0.04);
            flex-shrink: 0;
        }

        .hero-title {
            font-family: 'Bricolage Grotesque', sans-serif;
            font-size: 2.2rem;
            font-weight: 800;
            color: #0f172a;
            margin: 0 0 0.2rem 0;
            letter-spacing: -0.04em;
            line-height: 1.05;
        }

        .hero-subtitle {
            font-family: 'DM Sans', sans-serif;
            color: #6b7280;
            font-size: 0.98rem;
            margin: 0;
        }

        .toolbar-wrap {
            background: #ffffff;
            border: 1px solid #dde5ec;
            border-radius: 16px;
            padding: 0.85rem 1rem;
            box-shadow: 0 2px 12px rgba(15,23,42,0.035);
            margin-bottom: 1.1rem;
        }

        .metric-card {
            background: #ffffff;
            border: 1px solid #dde5ec;
            border-radius: 16px;
            padding: 1rem 1.15rem;
            box-shadow: 0 2px 12px rgba(15,23,42,0.035);
            height: 100%;
        }

        .metric-label {
            font-family: 'DM Sans', sans-serif;
            color: #6b7280;
            font-size: 0.88rem;
            font-weight: 500;
            margin-bottom: 0.3rem;
        }

        .metric-value {
            font-family: 'Bricolage Grotesque', sans-serif;
            color: #111827;
            font-size: 1.9rem;
            font-weight: 800;
            line-height: 1;
        }

        .metric-period {
            font-family: 'Bricolage Grotesque', sans-serif;
            font-size: 1.28rem;
            font-weight: 700;
            color: #111827;
        }

        .data-note {
            font-family: 'DM Sans', sans-serif;
            font-size: 0.8rem;
            color: #8a94a6;
            margin-top: 0.25rem;
        }

        /* ── CALENDARIO ─────────────────────────── */
        .cal-outer {
            background: #ffffff;
            border: 1px solid #dde5ec;
            border-radius: 20px;
            overflow: hidden;
            box-shadow: 0 4px 22px rgba(15,23,42,0.04);
            margin-top: 1rem;
        }

        .cal-header {
            display: grid;
            grid-template-columns: repeat(7, 1fr);
            background: #f7f9fb;
            border-bottom: 1px solid #e5ebf1;
        }

        .cal-weekday {
            padding: 0.8rem 0.5rem;
            text-align: center;
            font-family: 'DM Sans', sans-serif;
            font-size: 0.8rem;
            font-weight: 700;
            color: #6b7280;
            letter-spacing: 0.03em;
            text-transform: uppercase;
            border-right: 1px solid #edf1f5;
        }

        .cal-weekday:last-child { border-right: none; }

        .cal-grid {
            display: grid;
            grid-template-columns: repeat(7, 1fr);
        }

        .day-cell {
            min-height: 148px;
            border-right: 1px solid #edf1f5;
            border-bottom: 1px solid #edf1f5;
            padding: 0.52rem 0.42rem 0.42rem 0.42rem;
            position: relative;
            background: #ffffff;
            overflow: hidden;
        }

        .day-cell:nth-child(7n) { border-right: none; }

        .day-cell.other-month { background: #f8fafc; }

        .day-cell.today {
            background: linear-gradient(160deg, #f2f6fb 0%, #ffffff 65%);
        }

        .day-num {
            font-family: 'Bricolage Grotesque', sans-serif;
            font-size: 0.92rem;
            font-weight: 700;
            color: #1f2937;
            width: 1.9rem;
            height: 1.9rem;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            border-radius: 50%;
            margin-bottom: 0.42rem;
        }

        .other-month .day-num { color: #c5ced8; }

        .today .day-num {
            background: #4b5563;
            color: #ffffff;
        }

        .events-col {
            display: flex;
            flex-direction: column;
            gap: 4px;
        }

        /* ── Barra tipo Google Calendar ── */
        .ev-chip {
            min-height: 24px;
            display: flex;
            align-items: center;
            font-family: 'DM Sans', sans-serif;
            font-size: 0.72rem;
            font-weight: 600;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
            box-sizing: border-box;
            padding-top: 2px;
            padding-bottom: 2px;
            border: 1px solid transparent;
        }

        .ev-chip span {
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
            width: 100%;
            display: block;
        }

        .ev-chip.span-start {
            border-radius: 6px 0 0 6px;
            padding-left: 8px;
            padding-right: 6px;
            margin-left: -0.42rem;
            margin-right: 0;
        }

        .ev-chip.span-middle {
            border-radius: 0;
            padding-left: 8px;
            padding-right: 6px;
            margin-left: 0;
            margin-right: 0;
        }

        .ev-chip.span-end {
            border-radius: 0 6px 6px 0;
            padding-left: 8px;
            padding-right: 6px;
            margin-left: 0;
            margin-right: -0.42rem;
        }

        .ev-chip.span-solo {
            border-radius: 6px;
            padding-left: 8px;
            padding-right: 8px;
            margin-left: -0.42rem;
            margin-right: -0.42rem;
        }

        .empty-cell {
            font-family: 'DM Sans', sans-serif;
            color: #d2dae3;
            font-size: 0.78rem;
            margin-top: 0.3rem;
        }

        /* ── Leyenda ── */
        .legend-wrap {
            display: flex;
            flex-wrap: wrap;
            gap: 0.5rem 1rem;
            margin-top: 1rem;
            padding: 0.8rem 1rem;
            background: #ffffff;
            border: 1px solid #dde5ec;
            border-radius: 14px;
        }

        .legend-item {
            display: flex;
            align-items: center;
            gap: 0.42rem;
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
    raise FileNotFoundError("No se encontró 'vacaciones.xlsx' ni 'vacaciones_demo.xlsx'.")


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
        m += 12
        y -= 1
    while m > 12:
        m -= 12
        y += 1
    return y, m


# =========================================================
# CÁLCULO DE EVENTOS PARA EL CALENDARIO
# Ahora el nombre sale en cada tramo visible
# =========================================================
def build_span_events(df: pd.DataFrame, year: int, month: int) -> dict[date, list[dict]]:
    first = date(year, month, 1)
    last = date(year, month, calendar.monthrange(year, month)[1])

    relevant = df[
        (df["fecha_desde"].dt.date <= last) & (df["fecha_hasta"].dt.date >= first)
    ].copy()

    if relevant.empty:
        return {}

    all_names = tuple(df["nombre"].unique())
    color_map = build_color_map(all_names)
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
            is_start = current == true_start
            is_end = current == true_end

            if is_start and is_end:
                pos = "solo"
            elif is_start:
                pos = "start"
            elif is_end:
                pos = "end"
            else:
                pos = "middle"

            # Aquí cambiamos la lógica: el nombre sale siempre
            show_label = True

            if current not in day_events:
                day_events[current] = []

            day_events[current].append(
                {
                    "name": person,
                    "color": color,
                    "position": pos,
                    "show_label": show_label,
                }
            )
            current += timedelta(days=1)

    for d in day_events:
        day_events[d].sort(key=lambda e: e["name"])

    return day_events


# =========================================================
# RENDER DEL CALENDARIO
# =========================================================
def _safe_html(text: str) -> str:
    return (
        str(text)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


def _chip_html(ev: dict) -> str:
    c = ev["color"]
    pos = ev["position"]
    label = ev["name"] if ev["show_label"] else ""
    safe = _safe_html(label)

    style = (
        f"background:{c['bg']};"
        f"color:{c['text']};"
        f"border-color:{c['border']};"
    )

    return f"<div class='ev-chip span-{pos}' style='{style}'><span>{safe}</span></div>"


def render_month_calendar(df: pd.DataFrame, year: int, month: int) -> None:
    cal = calendar.Calendar(firstweekday=0)
    month_weeks = list(cal.monthdatescalendar(year, month))
    today = date.today()
    day_events = build_span_events(df, year, month)

    weekday_names = ["Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom"]
    html = ["<div class='cal-outer'>"]

    html.append("<div class='cal-header'>")
    for wn in weekday_names:
        html.append(f"<div class='cal-weekday'>{wn}</div>")
    html.append("</div>")

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
        safe = _safe_html(name)
        items_html += (
            f"<div class='legend-item'>"
            f"<div class='legend-dot' style='background:{c['bg']};border:2px solid {c['border']};'></div>"
            f"{safe}</div>"
        )

    st.markdown(f"<div class='legend-wrap'>{items_html}</div>", unsafe_allow_html=True)


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
# HERO
# =========================================================
def render_hero() -> None:
    logo_base64 = image_to_base64("ghr_logo.png")

    if logo_base64:
        logo_html = f"<img class='hero-logo' src='data:image/png;base64,{logo_base64}' />"
    else:
        logo_html = (
            "<div class='hero-logo' style='display:flex;align-items:center;justify-content:center;"
            "font-size:1.6rem;color:#4b5563;'>🏢</div>"
        )

    st.markdown(
        f"""
        <div class='hero-wrap'>
            {logo_html}
            <div>
                <div class='hero-title'>RRHH | Vacaciones del Personal</div>
                <div class='hero-subtitle'>
                    Calendario mensual · Visualiza quién está de vacaciones por fecha y departamento
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# =========================================================
# APLICACIÓN PRINCIPAL
# =========================================================
def main() -> None:
    inject_css()
    init_session_state()
    render_hero()

    try:
        file_path, file_note = locate_data_file()
        df = load_data(str(file_path))
    except Exception as exc:
        st.error(f"No fue posible cargar los datos: {exc}")
        st.stop()

    if st.button("🔄 Limpiar caché y recargar"):
        st.cache_data.clear()
        st.cache_data.clear()
        st.rerun()
        
    departments = ["Todos"] + sorted(df["departamento"].dropna().unique().tolist())
    year_min = max(2020, df["fecha_desde"].dt.year.min() - 1)
    year_max = df["fecha_hasta"].dt.year.max() + 2
    year_options = list(range(year_min, year_max))
    month_options = list(range(1, 13))
    month_names = [
        "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
        "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
    ]

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
            "Año",
            year_options,
            index=year_options.index(st.session_state.selected_year)
            if st.session_state.selected_year in year_options else 0,
        )
        if sel_year != st.session_state.selected_year:
            st.session_state.selected_year = sel_year

    with c6:
        sel_month = st.selectbox(
            "Mes",
            month_options,
            index=st.session_state.selected_month - 1,
            format_func=lambda x: month_names[x - 1],
        )
        if sel_month != st.session_state.selected_month:
            st.session_state.selected_month = sel_month

    st.markdown("</div>", unsafe_allow_html=True)

    year = st.session_state.selected_year
    month = st.session_state.selected_month

    df_filtered = df if selected_dept == "Todos" else df[df["departamento"] == selected_dept].copy()

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
            f"<div class='metric-period'>{month_names[month - 1]} {year}</div>"
            f"<div class='data-note'>{_safe_html(file_note)}</div>"
            f"</div>",
            unsafe_allow_html=True,
        )

    render_month_calendar(df_filtered, year, month)
    render_legend(df_filtered, year, month)


if __name__ == "__main__":
    main()
