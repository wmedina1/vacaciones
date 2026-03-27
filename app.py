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
# ESTILOS
# =========================================================
def inject_css() -> None:
    st.markdown(
        """
        <style>
        .block-container {
            padding-top: 0.7rem;
            padding-bottom: 0.8rem;
            max-width: 1500px;
        }

        /* Reduce espacio extra de Streamlit */
        div[data-testid="stVerticalBlock"] > div:has(.hero-title) {
            gap: 0.2rem;
        }

        .hero-title {
            font-size: 1.55rem;
            font-weight: 700;
            color: #0f172a;
            margin-bottom: 0.15rem;
            letter-spacing: -0.02em;
            line-height: 1.1;
        }

        .hero-subtitle {
            color: #64748b;
            font-size: 0.9rem;
            margin-bottom: 0.55rem;
            line-height: 1.2;
        }

        .toolbar-wrap {
            background: linear-gradient(180deg, #ffffff 0%, #f8fafc 100%);
            border: 1px solid #e2e8f0;
            border-radius: 16px;
            padding: 0.7rem 0.8rem 0.45rem 0.8rem;
            box-shadow: 0 8px 24px rgba(15, 23, 42, 0.05);
            margin-bottom: 0.65rem;
        }

        .metric-card {
            background: #ffffff;
            border: 1px solid #e2e8f0;
            border-radius: 16px;
            padding: 0.75rem 0.9rem;
            box-shadow: 0 5px 18px rgba(15, 23, 42, 0.04);
        }

        .metric-label {
            color: #64748b;
            font-size: 0.82rem;
            margin-bottom: 0.2rem;
            line-height: 1.15;
        }

        .metric-value {
            color: #0f172a;
            font-size: 1.45rem;
            font-weight: 700;
            line-height: 1.05;
        }

        .calendar-card {
            background: #ffffff;
            border: 1px solid #e2e8f0;
            border-radius: 20px;
            overflow: hidden;
            box-shadow: 0 10px 24px rgba(15, 23, 42, 0.05);
            margin-top: 0.7rem;
        }

        .calendar-header {
            display: grid;
            grid-template-columns: repeat(7, 1fr);
            background: #f8fafc;
            border-bottom: 1px solid #e2e8f0;
        }

        .weekday {
            padding: 0.55rem 0.3rem;
            text-align: center;
            font-size: 0.78rem;
            font-weight: 700;
            color: #475569;
            border-right: 1px solid #edf2f7;
            line-height: 1.1;
        }

        .weekday:last-child {
            border-right: none;
        }

        .calendar-grid {
            display: grid;
            grid-template-columns: repeat(7, 1fr);
        }

        .day-cell {
            min-height: clamp(88px, 12vh, 120px);
            max-height: clamp(88px, 12vh, 120px);
            border-right: 1px solid #edf2f7;
            border-bottom: 1px solid #edf2f7;
            padding: 0.38rem 0.42rem 0.32rem 0.42rem;
            position: relative;
            background: #ffffff;
            overflow: hidden;
        }

        .day-cell:nth-child(7n) {
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
            margin-bottom: 0.3rem;
        }

        .day-number {
            font-size: 0.82rem;
            font-weight: 700;
            color: #0f172a;
            width: 1.6rem;
            height: 1.6rem;
            display: flex;
            align-items: center;
            justify-content: center;
            border-radius: 999px;
            line-height: 1;
        }

        .other-month .day-number {
            color: #94a3b8;
        }

        .today .day-number {
            background: #2563eb;
            color: white;
        }

        .people-list {
            display: flex;
            flex-direction: column;
            gap: 0.18rem;
            margin-top: 0.1rem;
        }

        .person-chip {
            background: #e0f2fe;
            color: #0f172a;
            border-radius: 8px;
            padding: 0.18rem 0.32rem;
            font-size: 0.68rem;
            font-weight: 600;
            line-height: 1.1;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
            border: 1px solid #bae6fd;
        }

        .other-month .person-chip {
            background: #f1f5f9;
            color: #64748b;
            border-color: #e2e8f0;
        }

        .more-chip {
            color: #2563eb;
            font-size: 0.68rem;
            font-weight: 700;
            padding: 0.1rem 0 0 0;
            line-height: 1.1;
        }

        .empty-note {
            color: #94a3b8;
            font-size: 0.68rem;
            margin-top: 0.2rem;
            line-height: 1;
        }

        .data-source-note {
            font-size: 0.76rem;
            color: #64748b;
            margin-top: 0.35rem;
            line-height: 1.15;
        }

        /* Hace más compactos algunos widgets de Streamlit */
        div[data-baseweb="select"] > div {
            min-height: 38px !important;
        }

        .stButton > button {
            min-height: 38px;
            border-radius: 10px;
        }

        /* Ajuste para laptops medianas */
        @media (max-height: 900px) {
            .day-cell {
                min-height: clamp(78px, 10.5vh, 102px);
                max-height: clamp(78px, 10.5vh, 102px);
            }

            .person-chip {
                font-size: 0.64rem;
                padding: 0.14rem 0.28rem;
            }

            .weekday {
                font-size: 0.74rem;
                padding: 0.48rem 0.25rem;
            }
        }

        /* Si la pantalla es pequeña, compacta más */
        @media (max-width: 1200px) {
            .metric-value {
                font-size: 1.2rem;
            }

            .day-cell {
                padding: 0.28rem 0.3rem;
            }

            .day-number {
                width: 1.45rem;
                height: 1.45rem;
                font-size: 0.76rem;
            }

            .person-chip,
            .more-chip,
            .empty-note {
                font-size: 0.62rem;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

# =========================================================
# CARGA DE DATOS
# =========================================================
def locate_data_file() -> tuple[Path, str]:
    """Busca primero el archivo real y si no existe usa el demo."""
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

    expected_cols = {"nombre", "departamento", "fecha_desde", "fecha_hasta"}
    missing_cols = expected_cols - set(df.columns.str.lower())

    # Normalizar nombres de columnas
    df.columns = [str(c).strip().lower() for c in df.columns]
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
    """Expande cada rango de vacaciones a nivel de día individual."""
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
# UTILIDADES DE FECHAS
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


# =========================================================
# FILTRADO Y MÉTRICAS
# =========================================================
def filter_expanded_data(expanded_df: pd.DataFrame, department: str) -> pd.DataFrame:
    if department == "Todos":
        return expanded_df.copy()
    return expanded_df[expanded_df["departamento"] == department].copy()



def get_month_boundaries(year: int, month: int) -> tuple[date, date]:
    first_day = date(year, month, 1)
    last_day = date(year, month, calendar.monthrange(year, month)[1])
    return first_day, last_day



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


# =========================================================
# RENDER DEL CALENDARIO
# =========================================================
def render_month_calendar(filtered_expanded_df: pd.DataFrame, year: int, month: int) -> None:
    cal = calendar.Calendar(firstweekday=0)  # lunes
    month_days = list(cal.monthdatescalendar(year, month))

    if filtered_expanded_df.empty:
        by_day = {}
    else:
        by_day = (
            filtered_expanded_df.groupby("fecha")["nombre"]
            .apply(lambda x: sorted(x.unique().tolist()))
            .to_dict()
        )

    weekday_names = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
    today = date.today()

    html = ["<div class='calendar-card'>"]
    html.append("<div class='calendar-header'>")
    for day_name in weekday_names:
        html.append(f"<div class='weekday'>{day_name}</div>")
    html.append("</div>")

    html.append("<div class='calendar-grid'>")
    for week in month_days:
        for current_day in week:
            classes = ["day-cell"]
            if current_day.month != month:
                classes.append("other-month")
            if current_day == today:
                classes.append("today")

            names = by_day.get(current_day, [])
            visible_names = names[:3]
            remaining_count = max(len(names) - 3, 0)

            html.append(f"<div class='{' '.join(classes)}'>")
            html.append(
                f"<div class='day-top'><div class='day-number'>{current_day.day}</div></div>"
            )
            html.append("<div class='people-list'>")

            if visible_names:
                for person in visible_names:
                    safe_person = (
                        str(person)
                        .replace("&", "&amp;")
                        .replace("<", "&lt;")
                        .replace(">", "&gt;")
                    )
                    html.append(f"<div class='person-chip'>{safe_person}</div>")
                if remaining_count > 0:
                    html.append(f"<div class='more-chip'>+{remaining_count} más</div>")
            else:
                if current_day.month == month:
                    html.append("<div class='empty-note'>—</div>")

            html.append("</div></div>")
    html.append("</div></div>")

    st.markdown("".join(html), unsafe_allow_html=True)


# =========================================================
# APLICACIÓN PRINCIPAL
# =========================================================
def main() -> None:
    inject_css()
    init_session_state()

    st.markdown("<div class='hero-title'>RRHH | Vacaciones del Personal</div>", unsafe_allow_html=True)
    st.markdown(
        "<div class='hero-subtitle'>Calendario mensual para visualizar el personal en vacaciones por fecha y departamento.</div>",
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
    year_options = list(range(max(2020, df["fecha_desde"].dt.year.min() - 1), df["fecha_hasta"].dt.year.max() + 2))
    month_options = list(range(1, 13))

    st.markdown("<div class='toolbar-wrap'>", unsafe_allow_html=True)
    nav_col_1, nav_col_2, nav_col_3, nav_col_4, nav_col_5, nav_col_6 = st.columns([1.1, 1.1, 1.2, 1.7, 1.2, 1.2])

    with nav_col_1:
        if st.button("◀ Mes anterior", use_container_width=True):
            y, m = shift_month(st.session_state.selected_year, st.session_state.selected_month, -1)
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
            y, m = shift_month(st.session_state.selected_year, st.session_state.selected_month, 1)
            st.session_state.selected_year = y
            st.session_state.selected_month = m
            st.rerun()

    with nav_col_4:
        selected_department = st.selectbox("Departamento", departments, index=0)

    with nav_col_5:
        selected_year = st.selectbox(
            "Año",
            year_options,
            index=year_options.index(st.session_state.selected_year) if st.session_state.selected_year in year_options else 0,
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
    people_count, departments_count = build_month_summary(filtered_expanded, selected_year, selected_month)

    metric_col_1, metric_col_2, metric_col_3 = st.columns([1, 1, 2.2])

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
                <div class='metric-value' style='font-size:1.35rem'>{month_name} {selected_year}</div>
                <div class='data-source-note'>{file_note}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    render_month_calendar(filtered_expanded, selected_year, selected_month)

    detail_df = build_month_detail_table(df, selected_department, selected_year, selected_month)
    with st.expander("Ver detalle del mes en tabla", expanded=False):
        if detail_df.empty:
            st.info("No hay vacaciones registradas para el filtro y mes seleccionados.")
        else:
            st.dataframe(detail_df, use_container_width=True, hide_index=True)


if __name__ == "__main__":
    main()
