import calendar
import html
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
# ESTILOS
# =========================================================
def inject_css() -> None:
    st.markdown(
        """
        <style>
        .stApp {
            background: #f8fafc;
        }

        .block-container {
            padding-top: 2.9rem !important;   /* baja más todo el contenido */
            padding-bottom: 1.2rem !important;
            padding-left: 1.2rem !important;
            padding-right: 1.2rem !important;
            max-width: 100% !important;       /* ocupa pantalla completa */
        }

        .hero-wrap {
            margin-top: 0.8rem;
            margin-bottom: 0.85rem;
        }

        .hero-title {
            font-size: 2.15rem;
            font-weight: 800;
            color: #0f172a;
            margin-bottom: 0.2rem;
            letter-spacing: -0.02em;
            line-height: 1.1;
        }

        .hero-subtitle {
            color: #64748b;
            font-size: 0.96rem;
            margin-bottom: 0.65rem;
        }

        .toolbar-wrap {
            background: linear-gradient(180deg, #ffffff 0%, #f8fafc 100%);
            border: 1px solid #e2e8f0;
            border-radius: 18px;
            padding: 0.8rem 0.9rem 0.35rem 0.9rem;
            box-shadow: 0 8px 24px rgba(15, 23, 42, 0.05);
            margin-bottom: 0.75rem;
        }

        .metric-card {
            background: #ffffff;
            border: 1px solid #e2e8f0;
            border-radius: 18px;
            padding: 0.8rem 1rem;
            box-shadow: 0 6px 20px rgba(15, 23, 42, 0.04);
            min-height: 96px;
        }

        .metric-label {
            color: #64748b;
            font-size: 0.9rem;
            margin-bottom: 0.22rem;
        }

        .metric-value {
            color: #0f172a;
            font-size: 1.65rem;
            font-weight: 800;
            line-height: 1.08;
        }

        .data-source-note {
            font-size: 0.8rem;
            color: #64748b;
            margin-top: 0.35rem;
        }

        .calendar-card {
            background: #ffffff;
            border: 1px solid #e2e8f0;
            border-radius: 22px;
            overflow: hidden;
            box-shadow: 0 12px 30px rgba(15, 23, 42, 0.05);
            margin-top: 0.75rem;
            width: 100%;
        }

        .calendar-header {
            display: grid;
            grid-template-columns: repeat(7, minmax(0, 1fr));
            background: #f8fafc;
            border-bottom: 1px solid #e2e8f0;
        }

        .weekday {
            padding: 0.8rem 0.35rem;
            text-align: center;
            font-size: 0.83rem;
            font-weight: 800;
            color: #475569;
            border-right: 1px solid #edf2f7;
        }

        .weekday:last-child {
            border-right: none;
        }

        .week-row {
            display: grid;
            grid-template-columns: repeat(7, minmax(0, 1fr));
        }

        .day-cell {
            min-height: 118px; /* más compacto para que quepa mejor */
            border-right: 1px solid #edf2f7;
            border-bottom: 1px solid #edf2f7;
            padding: 0.45rem 0.45rem 0.35rem 0.45rem;
            position: relative;
            background: #ffffff;
        }

        .week-row .day-cell:last-child {
            border-right: none;
        }

        .day-cell.other-month {
            background: #f8fafc;
        }

        .day-cell.today {
            background: linear-gradient(180deg, #eff6ff 0%, #ffffff 100%);
        }

        .day-top {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 0.2rem;
            position: relative;
            z-index: 3;
        }

        .day-number {
            font-size: 0.92rem;
            font-weight: 800;
            color: #0f172a;
            width: 1.8rem;
            height: 1.8rem;
            display: flex;
            align-items: center;
            justify-content: center;
            border-radius: 999px;
        }

        .other-month .day-number {
            color: #94a3b8;
        }

        .today .day-number {
            background: #2563eb;
            color: white;
        }

        .track-layer {
            position: relative;
            margin-top: 0.15rem;
            z-index: 2;
        }

        .vac-line {
            height: 22px;
            display: flex;
            align-items: center;
            font-size: 0.73rem;
            font-weight: 700;
            line-height: 1;
            white-space: nowrap;
            overflow: hidden;
            color: var(--txt);
            position: relative;
            margin-bottom: 0.16rem;
            padding-left: 0.1rem;
            background: rgba(255,255,255,0.0);
        }

        .vac-line::after {
            content: "";
            position: absolute;
            left: 0;
            right: 0;
            bottom: 1px;
            height: 3px;
            background: var(--bg);
            opacity: 0.95;
            border-radius: 999px;
        }

        .vac-line.start {
            padding-left: 0.3rem;
        }

        .vac-line.start::after {
            border-top-left-radius: 999px;
            border-bottom-left-radius: 999px;
        }

        .vac-line.end::after {
            border-top-right-radius: 999px;
            border-bottom-right-radius: 999px;
        }

        .vac-line.single::after {
            border-radius: 999px;
        }

        .vac-name {
            position: relative;
            z-index: 1;
            display: inline-block;
            max-width: 100%;
            overflow: hidden;
            text-overflow: ellipsis;
            background: rgba(255,255,255,0.82);
            padding: 0.06rem 0.3rem;
            border-radius: 8px;
        }

        .extra-note {
            font-size: 0.7rem;
            color: #64748b;
            margin-top: 0.2rem;
            font-weight: 700;
        }

        .empty-note {
            color: #cbd5e1;
            font-size: 0.75rem;
            margin-top: 0.7rem;
        }

        .calendar-legend {
            display: flex;
            gap: 0.8rem;
            flex-wrap: wrap;
            padding: 0.8rem 1rem 0.15rem 1rem;
            background: #ffffff;
            border-bottom: 1px solid #eef2f7;
        }

        .legend-item {
            display: flex;
            align-items: center;
            gap: 0.35rem;
            font-size: 0.78rem;
            color: #475569;
            font-weight: 600;
        }

        .legend-dot {
            width: 12px;
            height: 12px;
            border-radius: 999px;
            flex: 0 0 12px;
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
        return real_file, "Archivo local detectado: vacaciones.xlsx"
    if demo_file.exists():
        return demo_file, "Usando archivo de ejemplo: vacaciones_demo.xlsx"

    raise FileNotFoundError(
        "No se encontró 'vacaciones.xlsx' ni 'vacaciones_demo.xlsx' en la carpeta del proyecto."
    )


@st.cache_data(show_spinner=False)
def load_data(file_path: str) -> pd.DataFrame:
    path = Path(file_path)

    if path.suffix.lower() == ".csv":
        df = pd.read_csv(path)
    else:
        df = pd.read_excel(path)

    df.columns = [str(c).strip().lower() for c in df.columns]

    expected_cols = {"nombre", "departamento", "fecha_desde", "fecha_hasta"}
    missing_cols = expected_cols - set(df.columns)

    if missing_cols:
        raise ValueError(
            f"Faltan columnas obligatorias en el archivo: {', '.join(sorted(missing_cols))}"
        )

    df = df[["nombre", "departamento", "fecha_desde", "fecha_hasta"]].copy()
    df["nombre"] = df["nombre"].astype(str).str.strip()
    df["departamento"] = df["departamento"].astype(str).str.strip()
    df["fecha_desde"] = pd.to_datetime(df["fecha_desde"], errors="coerce")
    df["fecha_hasta"] = pd.to_datetime(df["fecha_hasta"], errors="coerce")

    df = df.dropna(subset=["nombre", "departamento", "fecha_desde", "fecha_hasta"]).copy()
    df = df[df["fecha_hasta"] >= df["fecha_desde"]].copy()

    return df.sort_values(["fecha_desde", "nombre"]).reset_index(drop=True)


@st.cache_data(show_spinner=False)
def expand_vacation_ranges(df: pd.DataFrame) -> pd.DataFrame:
    records = []

    for row in df.itertuples(index=False):
        start_date = row.fecha_desde.date()
        end_date = row.fecha_hasta.date()
        current = start_date

        while current <= end_date:
            records.append(
                {
                    "fecha": current,
                    "nombre": row.nombre,
                    "departamento": row.departamento,
                    "fecha_desde": row.fecha_desde.date(),
                    "fecha_hasta": row.fecha_hasta.date(),
                }
            )
            current += timedelta(days=1)

    expanded = pd.DataFrame(records)
    if not expanded.empty:
        expanded = expanded.sort_values(["fecha", "nombre"]).reset_index(drop=True)
    return expanded


# =========================================================
# ESTADO DE SESIÓN
# =========================================================
def init_session_state() -> None:
    today = date.today()
    if "selected_year" not in st.session_state:
        st.session_state.selected_year = today.year
    if "selected_month" not in st.session_state:
        st.session_state.selected_month = today.month


# =========================================================
# UTILIDADES
# =========================================================
def shift_month(year: int, month: int, offset: int) -> tuple[int, int]:
    new_month = month + offset
    new_year = year

    while new_month < 1:
        new_month += 12
        new_year -= 1
    while new_month > 12:
        new_month -= 12
        new_year += 1

    return new_year, new_month


def get_month_boundaries(year: int, month: int) -> tuple[date, date]:
    first_day = date(year, month, 1)
    last_day = date(year, month, calendar.monthrange(year, month)[1])
    return first_day, last_day


def filter_expanded_data(expanded_df: pd.DataFrame, department: str) -> pd.DataFrame:
    if department == "Todos":
        return expanded_df.copy()
    return expanded_df[expanded_df["departamento"] == department].copy()


def build_month_summary(filtered_expanded_df: pd.DataFrame, year: int, month: int) -> tuple[int, int]:
    first_day, last_day = get_month_boundaries(year, month)
    month_df = filtered_expanded_df[
        (filtered_expanded_df["fecha"] >= first_day)
        & (filtered_expanded_df["fecha"] <= last_day)
    ].copy()

    people_count = month_df["nombre"].nunique() if not month_df.empty else 0
    departments_count = month_df["departamento"].nunique() if not month_df.empty else 0
    return people_count, departments_count


def build_month_detail_table(raw_df: pd.DataFrame, department: str, year: int, month: int) -> pd.DataFrame:
    if department != "Todos":
        raw_df = raw_df[raw_df["departamento"] == department].copy()

    first_day, last_day = get_month_boundaries(year, month)
    detail = raw_df[
        (raw_df["fecha_desde"].dt.date <= last_day)
        & (raw_df["fecha_hasta"].dt.date >= first_day)
    ].copy()

    if detail.empty:
        return detail

    detail["fecha_desde"] = detail["fecha_desde"].dt.strftime("%Y-%m-%d")
    detail["fecha_hasta"] = detail["fecha_hasta"].dt.strftime("%Y-%m-%d")
    return detail.rename(
        columns={
            "nombre": "Nombre",
            "departamento": "Departamento",
            "fecha_desde": "Fecha desde",
            "fecha_hasta": "Fecha hasta",
        }
    )


def escape_html(text: str) -> str:
    return html.escape(str(text), quote=True)


def get_person_color_map(names: list[str]) -> dict[str, dict[str, str]]:
    palette = [
        ("#3b82f6", "#1d4ed8"),
        ("#10b981", "#047857"),
        ("#f59e0b", "#b45309"),
        ("#ef4444", "#b91c1c"),
        ("#8b5cf6", "#6d28d9"),
        ("#06b6d4", "#0e7490"),
        ("#84cc16", "#4d7c0f"),
        ("#f97316", "#c2410c"),
        ("#ec4899", "#be185d"),
        ("#14b8a6", "#0f766e"),
        ("#6366f1", "#4338ca"),
        ("#22c55e", "#15803d"),
    ]

    sorted_names = sorted(set(names))
    color_map = {}
    for i, person in enumerate(sorted_names):
        bg, txt = palette[i % len(palette)]
        color_map[person] = {"bg": bg, "txt": txt}
    return color_map


def assign_tracks_for_week(week_days: list[date], person_ranges: list[dict]) -> list[dict]:
    """
    Asigna una fila/track por persona para dibujar bandas horizontales limpias.
    Cada rango semanal tendrá:
    - track
    - start_idx / end_idx dentro de la semana (0-6)
    """
    if not person_ranges:
        return []

    ranges = sorted(
        person_ranges,
        key=lambda x: (x["start_idx"], x["end_idx"], x["nombre"].lower())
    )

    track_end_positions = []
    assigned = []

    for item in ranges:
        assigned_track = None
        for track_idx, last_end in enumerate(track_end_positions):
            if item["start_idx"] > last_end:
                assigned_track = track_idx
                track_end_positions[track_idx] = item["end_idx"]
                break

        if assigned_track is None:
            assigned_track = len(track_end_positions)
            track_end_positions.append(item["end_idx"])

        item_copy = item.copy()
        item_copy["track"] = assigned_track
        assigned.append(item_copy)

    return assigned


def build_week_segments(filtered_expanded_df: pd.DataFrame, week_days: list[date]) -> tuple[dict, int]:
    """
    Genera segmentos semanales para que el nombre solo salga una vez
    y el subrayado continúe por los días consecutivos.
    """
    if filtered_expanded_df.empty:
        return {d: [] for d in week_days}, 0

    week_start = week_days[0]
    week_end = week_days[-1]

    relevant = filtered_expanded_df[
        (filtered_expanded_df["fecha"] >= week_start)
        & (filtered_expanded_df["fecha"] <= week_end)
    ].copy()

    if relevant.empty:
        return {d: [] for d in week_days}, 0

    ranges = []
    for person, g in relevant.groupby("nombre"):
        person_days = sorted(g["fecha"].unique().tolist())
        start_idx = week_days.index(person_days[0])
        end_idx = week_days.index(person_days[-1])

        ranges.append(
            {
                "nombre": person,
                "start_idx": start_idx,
                "end_idx": end_idx,
            }
        )

    assigned_ranges = assign_tracks_for_week(week_days, ranges)
    per_day = {d: [] for d in week_days}

    for item in assigned_ranges:
        for idx in range(item["start_idx"], item["end_idx"] + 1):
            current_day = week_days[idx]
            per_day[current_day].append(
                {
                    "nombre": item["nombre"],
                    "track": item["track"],
                    "start": idx == item["start_idx"],
                    "end": idx == item["end_idx"],
                    "single": item["start_idx"] == item["end_idx"],
                }
            )

    max_tracks = max((item["track"] for item in assigned_ranges), default=-1) + 1
    return per_day, max_tracks


# =========================================================
# RENDER DEL CALENDARIO
# =========================================================
def render_month_calendar(filtered_expanded_df: pd.DataFrame, year: int, month: int) -> None:
    cal = calendar.Calendar(firstweekday=0)  # lunes
    month_weeks = list(cal.monthdatescalendar(year, month))
    today = date.today()

    unique_people = (
        sorted(filtered_expanded_df["nombre"].unique().tolist())
        if not filtered_expanded_df.empty
        else []
    )
    color_map = get_person_color_map(unique_people)

    weekday_names = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]

    html_parts = ["<div class='calendar-card'>"]

    # Leyenda compacta
    if unique_people:
        legend_people = unique_people[:8]
        html_parts.append("<div class='calendar-legend'>")
        for person in legend_people:
            colors = color_map[person]
            html_parts.append(
                f"""
                <div class='legend-item'>
                    <span class='legend-dot' style='background:{colors["bg"]}'></span>
                    <span>{escape_html(person)}</span>
                </div>
                """
            )
        if len(unique_people) > 8:
            html_parts.append(
                f"<div class='legend-item'><span style='color:#64748b'>+{len(unique_people)-8} más</span></div>"
            )
        html_parts.append("</div>")

    # Encabezado días
    html_parts.append("<div class='calendar-header'>")
    for day_name in weekday_names:
        html_parts.append(f"<div class='weekday'>{day_name}</div>")
    html_parts.append("</div>")

    # Semanas
    for week in month_weeks:
        week_segments, max_tracks = build_week_segments(filtered_expanded_df, week)
        html_parts.append("<div class='week-row'>")

        for current_day in week:
            classes = ["day-cell"]
            if current_day.month != month:
                classes.append("other-month")
            if current_day == today:
                classes.append("today")

            html_parts.append(f"<div class='{' '.join(classes)}'>")
            html_parts.append(
                f"<div class='day-top'><div class='day-number'>{current_day.day}</div></div>"
            )

            html_parts.append("<div class='track-layer'>")

            day_items = sorted(week_segments.get(current_day, []), key=lambda x: x["track"])

            if max_tracks == 0 and current_day.month == month:
                html_parts.append("<div class='empty-note'>—</div>")
            else:
                items_by_track = {item["track"]: item for item in day_items}

                hidden_count = 0
                max_visible_tracks = 4  # para mantener limpio

                for track_idx in range(max_tracks):
                    if track_idx >= max_visible_tracks:
                        if track_idx in items_by_track:
                            hidden_count += 1
                        continue

                    item = items_by_track.get(track_idx)
                    if item is None:
                        html_parts.append("<div class='vac-line' style='visibility:hidden'></div>")
                        continue

                    person = item["nombre"]
                    colors = color_map.get(person, {"bg": "#94a3b8", "txt": "#334155"})

                    class_names = ["vac-line"]
                    if item["single"]:
                        class_names.append("single")
                    else:
                        if item["start"]:
                            class_names.append("start")
                        if item["end"]:
                            class_names.append("end")

                    name_html = (
                        f"<span class='vac-name'>{escape_html(person)}</span>"
                        if item["start"]
                        else ""
                    )

                    html_parts.append(
                        f"""
                        <div class="{' '.join(class_names)}"
                             style="--bg:{colors['bg']}; --txt:{colors['txt']};">
                            {name_html}
                        </div>
                        """
                    )

                if hidden_count > 0:
                    html_parts.append(f"<div class='extra-note'>+{hidden_count} más</div>")

            html_parts.append("</div></div>")

        html_parts.append("</div>")

    html_parts.append("</div>")
    st.markdown("".join(html_parts), unsafe_allow_html=True)


# =========================================================
# APLICACIÓN PRINCIPAL
# =========================================================
def main() -> None:
    inject_css()
    init_session_state()

    st.markdown(
        """
        <div class='hero-wrap'>
            <div class='hero-title'>Vacaciones del personal</div>
            <div class='hero-subtitle'>
                Calendario mensual para visualizar el personal en vacaciones por fecha y departamento.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    try:
        file_path, file_note = locate_data_file()
        df = load_data(str(file_path))
        expanded_df = expand_vacation_ranges(df)
    except Exception as exc:
        st.error(f"No fue posible cargar los datos: {exc}")
        st.stop()

    departments = ["Todos"] + sorted(df["departamento"].dropna().unique().tolist())
    year_options = list(
        range(
            max(2020, df["fecha_desde"].dt.year.min() - 1),
            df["fecha_hasta"].dt.year.max() + 2,
        )
    )
    month_options = list(range(1, 13))

    st.markdown("<div class='toolbar-wrap'>", unsafe_allow_html=True)

    nav_col_1, nav_col_2, nav_col_3, nav_col_4, nav_col_5, nav_col_6 = st.columns(
        [1.05, 0.7, 1.05, 1.65, 0.95, 1.05]
    )

    with nav_col_1:
        if st.button("◀ Mes anterior", use_container_width=True):
            y, m = shift_month(
                st.session_state.selected_year,
                st.session_state.selected_month,
                -1
            )
            st.session_state.selected_year = y
            st.session_state.selected_month = m
            st.rerun()

    with nav_col_2:
        if st.button("Hoy", use_container_width=True):
            today = date.today()
            st.session_state.selected_year = today.year
            st.session_state.selected_month = today.month
            st.rerun()

    with nav_col_3:
        if st.button("Mes siguiente ▶", use_container_width=True):
            y, m = shift_month(
                st.session_state.selected_year,
                st.session_state.selected_month,
                1
            )
            st.session_state.selected_year = y
            st.session_state.selected_month = m
            st.rerun()

    with nav_col_4:
        selected_department = st.selectbox("Departamento", departments, index=0)

    with nav_col_5:
        selected_year = st.selectbox(
            "Año",
            year_options,
            index=year_options.index(st.session_state.selected_year)
            if st.session_state.selected_year in year_options else 0,
        )
        if selected_year != st.session_state.selected_year:
            st.session_state.selected_year = selected_year

    with nav_col_6:
        selected_month = st.selectbox(
            "Mes",
            month_options,
            index=st.session_state.selected_month - 1,
            format_func=lambda x: [
                "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
                "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
            ][x - 1],
        )
        if selected_month != st.session_state.selected_month:
            st.session_state.selected_month = selected_month

    st.markdown("</div>", unsafe_allow_html=True)

    selected_year = st.session_state.selected_year
    selected_month = st.session_state.selected_month

    filtered_expanded = filter_expanded_data(expanded_df, selected_department)
    people_count, departments_count = build_month_summary(
        filtered_expanded,
        selected_year,
        selected_month
    )

    metric_col_1, metric_col_2, metric_col_3 = st.columns([1, 1, 2.4])

    with metric_col_1:
        st.markdown(
            f"""
            <div class='metric-card'>
                <div class='metric-label'>Personas con vacaciones en el mes</div>
                <div class='metric-value'>{people_count}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with metric_col_2:
        st.markdown(
            f"""
            <div class='metric-card'>
                <div class='metric-label'>Departamentos impactados</div>
                <div class='metric-value'>{departments_count}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with metric_col_3:
        month_name = [
            "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
            "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
        ][selected_month - 1]

        st.markdown(
            f"""
            <div class='metric-card'>
                <div class='metric-label'>Período visualizado</div>
                <div class='metric-value' style='font-size:1.3rem'>{month_name} {selected_year}</div>
                <div class='data-source-note'>{escape_html(file_note)}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    render_month_calendar(filtered_expanded, selected_year, selected_month)

    # Si luego quieres volver a mostrar la tabla, la dejas activa.
    # Por ahora la dejo fuera para que el calendario use mejor la pantalla.


if __name__ == "__main__":
    main()
