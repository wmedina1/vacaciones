import calendar
import os
from datetime import date, datetime, timedelta
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
# ESTILOS
# =========================================================
def inject_css() -> None:
    st.markdown(
        """
        <style>
        /* ===== Layout general ===== */
        .block-container {
            padding-top: 0.8rem;
            padding-bottom: 0.8rem;
            max-width: 1500px;
        }

        /* ===== Header ===== */
        .app-title {
            font-size: 1.8rem;
            font-weight: 700;
            color: #0f172a;
            margin: 0 0 0.20rem 0;
            letter-spacing: -0.02em;
            line-height: 1.1;
        }

        .app-subtitle {
            color: #64748b;
            font-size: 0.95rem;
            margin: 0 0 0.8rem 0;
            line-height: 1.2;
        }

        /* ===== Widgets de Streamlit más compactos ===== */
        div[data-baseweb="select"] > div {
            min-height: 40px !important;
            border-radius: 12px !important;
        }

        .stButton > button {
            min-height: 40px;
            border-radius: 12px;
            border: 1px solid #dbe2ea;
            font-weight: 600;
        }

        /* ===== Tarjetas KPI ===== */
        .metric-card {
            background: #ffffff;
            border: 1px solid #dbe2ea;
            border-radius: 18px;
            padding: 0.9rem 1rem;
            box-shadow: 0 6px 16px rgba(15, 23, 42, 0.04);
            min-height: 96px;
        }

        .metric-label {
            color: #64748b;
            font-size: 0.88rem;
            margin-bottom: 0.15rem;
            line-height: 1.1;
        }

        .metric-value {
            color: #0f172a;
            font-size: 1.8rem;
            font-weight: 700;
            line-height: 1.1;
        }

        .metric-note {
            color: #64748b;
            font-size: 0.85rem;
            line-height: 1.15;
            margin-top: 0.25rem;
        }

        /* ===== Calendario ===== */
        .calendar-card {
            background: #ffffff;
            border: 1px solid #dbe2ea;
            border-radius: 20px;
            overflow: hidden;
            box-shadow: 0 8px 20px rgba(15, 23, 42, 0.04);
            margin-top: 0.8rem;
        }

        .calendar-header {
            display: grid;
            grid-template-columns: repeat(7, 1fr);
            background: #f8fafc;
            border-bottom: 1px solid #e5ebf2;
        }

        .weekday {
            padding: 0.65rem 0.3rem;
            text-align: center;
            font-size: 0.82rem;
            font-weight: 700;
            color: #334155;
            border-right: 1px solid #edf2f7;
        }

        .weekday:last-child {
            border-right: none;
        }

        .calendar-grid {
            display: grid;
            grid-template-columns: repeat(7, 1fr);
        }

        .day-cell {
            min-height: clamp(112px, 14vh, 165px);
            max-height: clamp(112px, 14vh, 165px);
            border-right: 1px solid #edf2f7;
            border-bottom: 1px solid #edf2f7;
            padding: 0.42rem 0.42rem 0.35rem 0.42rem;
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
            background: linear-gradient(180deg, #eef6ff 0%, #ffffff 100%);
        }

        .day-top {
            display: flex;
            justify-content: flex-start;
            align-items: center;
            margin-bottom: 0.35rem;
        }

        .day-number {
            font-size: 0.85rem;
            font-weight: 700;
            color: #0f172a;
            width: 1.7rem;
            height: 1.7rem;
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
            color: #ffffff;
        }

        .people-list {
            display: flex;
            flex-direction: column;
            gap: 0.22rem;
            max-height: calc(100% - 2rem);
            overflow-y: auto;
            padding-right: 2px;
        }

        .people-list::-webkit-scrollbar {
            width: 6px;
        }

        .people-list::-webkit-scrollbar-thumb {
            background: #d6dde7;
            border-radius: 10px;
        }

        .person-chip {
            background: #e8f3ff;
            color: #0f172a;
            border: 1px solid #cfe3fb;
            border-radius: 9px;
            padding: 0.20rem 0.38rem;
            font-size: 0.69rem;
            font-weight: 600;
            line-height: 1.1;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }

        .other-month .person-chip {
            background: #f1f5f9;
            color: #64748b;
            border-color: #e2e8f0;
        }

        .empty-note {
            color: #94a3b8;
            font-size: 0.68rem;
            margin-top: 0.15rem;
            line-height: 1.1;
        }

        /* ===== Ajuste especial para meses de 6 semanas ===== */
        .calendar-grid.six-weeks .day-cell {
            min-height: clamp(96px, 11.5vh, 132px);
            max-height: clamp(96px, 11.5vh, 132px);
        }

        /* ===== Responsive ===== */
        @media (max-height: 900px) {
            .day-cell {
                min-height: clamp(100px, 12vh, 145px);
                max-height: clamp(100px, 12vh, 145px);
            }

            .calendar-grid.six-weeks .day-cell {
                min-height: clamp(88px, 10.5vh, 118px);
                max-height: clamp(88px, 10.5vh, 118px);
            }

            .person-chip {
                font-size: 0.64rem;
                padding: 0.16rem 0.32rem;
            }

            .metric-value {
                font-size: 1.55rem;
            }
        }

        @media (max-width: 1200px) {
            .app-title {
                font-size: 1.55rem;
            }

            .weekday {
                font-size: 0.76rem;
                padding: 0.52rem 0.25rem;
            }

            .day-number {
                width: 1.5rem;
                height: 1.5rem;
                font-size: 0.78rem;
            }

            .person-chip {
                font-size: 0.62rem;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


# =========================================================
# UTILIDADES
# =========================================================
def month_name_es(month_number: int) -> str:
    months = [
        "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
        "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
    ]
    return months[month_number - 1]


def shift_month(year: int, month: int, delta: int) -> tuple[int, int]:
    new_month = month + delta
    new_year = year

    while new_month < 1:
        new_month += 12
        new_year -= 1

    while new_month > 12:
        new_month -= 12
        new_year += 1

    return new_year, new_month


def init_session_state() -> None:
    today = date.today()

    if "selected_year" not in st.session_state:
        st.session_state.selected_year = today.year

    if "selected_month" not in st.session_state:
        st.session_state.selected_month = today.month


def locate_data_file() -> tuple[Path, str]:
    """
    Prioridad:
    1) vacaciones.xlsx
    2) vacaciones_demo.xlsx
    """
    real_file = Path("vacaciones.xlsx")
    demo_file = Path("vacaciones_demo.xlsx")

    if real_file.exists():
        return real_file, f"Usando archivo local: {real_file.name}"

    if demo_file.exists():
        return demo_file, f"Usando archivo de ejemplo: {demo_file.name}"

    raise FileNotFoundError(
        "No se encontró 'vacaciones.xlsx' ni 'vacaciones_demo.xlsx' en la carpeta del proyecto."
    )


def load_data(file_path: str) -> pd.DataFrame:
    file_ext = Path(file_path).suffix.lower()

    if file_ext == ".csv":
        df = pd.read_csv(file_path)
    elif file_ext in [".xlsx", ".xls"]:
        df = pd.read_excel(file_path)
    else:
        raise ValueError("Formato no soportado. Use Excel (.xlsx/.xls) o CSV.")

    expected_cols = {"nombre", "departamento", "fecha_desde", "fecha_hasta"}
    missing = expected_cols - set(df.columns.str.strip())

    # normalizar nombres de columnas
    df.columns = [str(c).strip() for c in df.columns]
    missing = expected_cols - set(df.columns)

    if missing:
        raise ValueError(f"Faltan columnas requeridas: {', '.join(sorted(missing))}")

    df = df.copy()
    df["nombre"] = df["nombre"].astype(str).str.strip()
    df["departamento"] = df["departamento"].astype(str).str.strip()
    df["fecha_desde"] = pd.to_datetime(df["fecha_desde"], errors="coerce")
    df["fecha_hasta"] = pd.to_datetime(df["fecha_hasta"], errors="coerce")

    df = df.dropna(subset=["nombre", "departamento", "fecha_desde", "fecha_hasta"])

    invalid_range = df["fecha_desde"] > df["fecha_hasta"]
    if invalid_range.any():
        raise ValueError("Hay registros donde fecha_desde es mayor que fecha_hasta.")

    return df


def expand_vacation_ranges(df: pd.DataFrame) -> pd.DataFrame:
    """
    Expande internamente cada rango de vacaciones a días individuales.
    """
    rows = []

    for _, row in df.iterrows():
        start_date = row["fecha_desde"].date()
        end_date = row["fecha_hasta"].date()

        current = start_date
        while current <= end_date:
            rows.append(
                {
                    "nombre": row["nombre"],
                    "departamento": row["departamento"],
                    "fecha": current,
                    "fecha_desde": start_date,
                    "fecha_hasta": end_date,
                }
            )
            current += timedelta(days=1)

    if not rows:
        return pd.DataFrame(columns=["nombre", "departamento", "fecha", "fecha_desde", "fecha_hasta"])

    return pd.DataFrame(rows)


def filter_month_data(expanded_df: pd.DataFrame, year: int, month: int, department: str) -> pd.DataFrame:
    month_start = date(year, month, 1)
    month_end = date(year, month, calendar.monthrange(year, month)[1])

    df = expanded_df.copy()

    if department != "Todos":
        df = df[df["departamento"] == department]

    df = df[(df["fecha"] >= month_start) & (df["fecha"] <= month_end)]
    return df


def get_month_summary(filtered_month_df: pd.DataFrame) -> tuple[int, int]:
    if filtered_month_df.empty:
        return 0, 0

    people_count = filtered_month_df["nombre"].nunique()
    departments_count = filtered_month_df["departamento"].nunique()

    return people_count, departments_count


def build_calendar_html(expanded_df_filtered_dept: pd.DataFrame, year: int, month: int) -> str:
    cal = calendar.Calendar(firstweekday=0)  # lunes
    month_matrix = list(cal.monthdatescalendar(year, month))
    num_weeks = len(month_matrix)

    grid_class = "calendar-grid six-weeks" if num_weeks == 6 else "calendar-grid"

    if expanded_df_filtered_dept.empty:
        by_day = {}
    else:
        by_day = (
            expanded_df_filtered_dept.groupby("fecha")["nombre"]
            .apply(lambda x: sorted(pd.unique(x).tolist()))
            .to_dict()
        )

    weekday_names = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
    today = date.today()

    html = []
    html.append("<div class='calendar-card'>")

    html.append("<div class='calendar-header'>")
    for wd in weekday_names:
        html.append(f"<div class='weekday'>{wd}</div>")
    html.append("</div>")

    html.append(f"<div class='{grid_class}'>")

    for week in month_matrix:
        for day in week:
            is_other_month = day.month != month
            is_today = day == today

            css_classes = ["day-cell"]
            if is_other_month:
                css_classes.append("other-month")
            if is_today:
                css_classes.append("today")

            names = by_day.get(day, [])

            html.append(f"<div class='{' '.join(css_classes)}'>")
            html.append("<div class='day-top'>")
            html.append(f"<div class='day-number'>{day.day}</div>")
            html.append("</div>")

            if names:
                html.append("<div class='people-list'>")
                for name in names:
                    safe_name = str(name).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
                    html.append(f"<div class='person-chip'>{safe_name}</div>")
                html.append("</div>")
            else:
                html.append("<div class='empty-note'></div>")

            html.append("</div>")

    html.append("</div>")
    html.append("</div>")

    return "".join(html)


def render_metric_card(label: str, value: str, note: str = "") -> None:
    note_html = f"<div class='metric-note'>{note}</div>" if note else ""
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value}</div>
            {note_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


# =========================================================
# APP
# =========================================================
def main() -> None:
    inject_css()
    init_session_state()

    # ===== Título estable, sin HTML frágil =====
    st.markdown("<div class='app-title'>RRHH | Vacaciones del Personal</div>", unsafe_allow_html=True)
    st.markdown(
        "<div class='app-subtitle'>Calendario mensual para visualizar el personal en vacaciones por fecha y departamento.</div>",
        unsafe_allow_html=True,
    )

    # ===== Carga de datos =====
    try:
        file_path, file_note = locate_data_file()
        df = load_data(str(file_path))
        expanded_df = expand_vacation_ranges(df)
    except Exception as exc:
        st.error(f"No fue posible cargar los datos: {exc}")
        st.stop()

    # ===== Opciones de filtros =====
    departments = ["Todos"] + sorted(df["departamento"].dropna().unique().tolist())
    year_min = max(2020, int(df["fecha_desde"].dt.year.min()) - 1)
    year_max = int(df["fecha_hasta"].dt.year.max()) + 1
    year_options = list(range(year_min, year_max + 1))
    month_options = list(range(1, 13))

    if st.session_state.selected_year not in year_options:
        st.session_state.selected_year = year_options[0]

    # ===== Barra de navegación y filtros =====
    nav_col_1, nav_col_2, nav_col_3, nav_col_4, nav_col_5, nav_col_6 = st.columns([1.1, 1.1, 1.2, 1.8, 1.2, 1.2])

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
            options=year_options,
            index=year_options.index(st.session_state.selected_year),
        )
        st.session_state.selected_year = selected_year

    with nav_col_6:
        selected_month = st.selectbox(
            "Mes",
            options=month_options,
            index=st.session_state.selected_month - 1,
            format_func=month_name_es,
        )
        st.session_state.selected_month = selected_month

    # ===== Filtro para métricas del mes =====
    filtered_month_df = filter_month_data(
        expanded_df=expanded_df,
        year=st.session_state.selected_year,
        month=st.session_state.selected_month,
        department=selected_department,
    )

    # ===== Filtro para pintar calendario (incluye días de otras semanas visibles) =====
    expanded_df_filtered_dept = expanded_df.copy()
    if selected_department != "Todos":
        expanded_df_filtered_dept = expanded_df_filtered_dept[
            expanded_df_filtered_dept["departamento"] == selected_department
        ]

    people_count, departments_count = get_month_summary(filtered_month_df)

    # ===== KPI cards =====
    metric_col_1, metric_col_2, metric_col_3 = st.columns([1, 1, 2.2])

    with metric_col_1:
        render_metric_card(
            "Personas con vacaciones en el mes",
            str(people_count)
        )

    with metric_col_2:
        render_metric_card(
            "Departamentos impactados",
            str(departments_count)
        )

    with metric_col_3:
        render_metric_card(
            "Período visualizado",
            f"{month_name_es(st.session_state.selected_month)} {st.session_state.selected_year}",
            file_note
        )

    # ===== Calendario =====
    calendar_html = build_calendar_html(
        expanded_df_filtered_dept=expanded_df_filtered_dept,
        year=st.session_state.selected_year,
        month=st.session_state.selected_month,
    )
    st.markdown(calendar_html, unsafe_allow_html=True)

    # ===== Detalle del mes =====
    with st.expander("Ver detalle del mes", expanded=False):
        if filtered_month_df.empty:
            st.info("No hay vacaciones registradas para los filtros seleccionados.")
        else:
            detail_df = (
                filtered_month_df[["nombre", "departamento", "fecha_desde", "fecha_hasta"]]
                .drop_duplicates()
                .sort_values(["fecha_desde", "nombre"])
                .reset_index(drop=True)
            )

            detail_df["fecha_desde"] = pd.to_datetime(detail_df["fecha_desde"]).dt.strftime("%Y-%m-%d")
            detail_df["fecha_hasta"] = pd.to_datetime(detail_df["fecha_hasta"]).dt.strftime("%Y-%m-%d")

            st.dataframe(
                detail_df,
                use_container_width=True,
                hide_index=True,
            )


if __name__ == "__main__":
    main()
