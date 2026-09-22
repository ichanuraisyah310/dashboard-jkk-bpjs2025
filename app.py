import os
import textwrap
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st

# ============================================================
# CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Dashboard JKK Analytics & Insights",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# HELPER FUNCTIONS (FORMATTING INTERNASIONAL)
# ============================================================

def format_number(val):
    """Format angka ribuan dengan pemisah titik (.)"""
    if pd.isna(val):
        return "0"
    return f"{int(val):,}".replace(",", ".")


def format_currency(val):
    """Format mata uang IDR: Pemisah ribuan titik (.), desimal koma (,)"""
    if pd.isna(val) or val == 0:
        return "Rp 0"

    if val % 1 != 0:
        formatted = f"{val:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    else:
        formatted = f"{int(val):,}".replace(",", ".")

    return f"Rp {formatted}"


def format_currency_compact_intl(val):
    """Format ringkas standar internasional (B = Billion/Miliar, M = Million/Juta, K = Thousand/Ribu)"""
    if pd.isna(val) or val == 0:
        return "Rp 0"
    if val >= 1e12:
        return f"Rp {val / 1e12:,.1f} T".replace(".", ",").replace(",0", "")
    elif val >= 1e9:
        return f"Rp {val / 1e9:,.1f} B".replace(".", ",").replace(",0", "")
    elif val >= 1e6:
        return f"Rp {val / 1e6:,.1f} M".replace(".", ",").replace(",0", "")
    elif val >= 1e3:
        return f"Rp {val / 1e3:,.1f} K".replace(".", ",").replace(",0", "")
    else:
        return format_currency(val)


def wrap_labels(labels, width=14):
    """Membungkus teks label menjadi beberapa baris (wrap text)"""
    return ["<br>".join(textwrap.wrap(str(lbl), width=width)) for lbl in labels]


# ============================================================
# CUSTOM CSS (TEXT SELECTION, STYLING & PRINT-TO-PDF FIX)
# ============================================================

st.markdown(
    """
<style>
    .stApp {
        background: linear-gradient(135deg, #ffffff 0%, #f4f8fb 60%, #eef5fa 100%);
        color: #0f172a;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        user-select: text !important;
        -webkit-user-select: text !important;
        -moz-user-select: text !important;
        -ms-user-select: text !important;
    }

    header[data-testid="stHeader"] {
        background-color: transparent;
    }
    
    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 3rem;
        user-select: text !important;
    }

    .corporate-title-center {
        text-align: center;
        margin-bottom: 25px;
        padding-bottom: 20px;
        border-bottom: 2px solid #e2e8f0;
        user-select: text !important;
    }

    .corporate-title-main {
        font-size: 40px;
        font-weight: 900;
        background: linear-gradient(135deg, #1d4ed8 0%, #0284c7 40%, #0d9488 70%, #059669 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0;
        letter-spacing: -1px;
        text-shadow: 0 2px 8px rgba(13, 148, 136, 0.12);
        display: inline-block;
        background-color: #ecfdf5;
        padding: 4px 24px;
        border-radius: 50px;
        user-select: text !important;
    }

    .corporate-subtitle-main {
        color: #475569;
        font-size: 14.5px;
        margin-top: 12px;
        font-weight: 700;
        letter-spacing: -0.2px;
        user-select: text !important;
    }

    .stMultiSelect [data-baseweb="tag"] {
        background-color: #1d4ed8 !important;
        color: white !important;
    }

    div[data-testid="stMetric"] {
        background-color: #ffffff;
        border-radius: 10px;
        padding: 12px 16px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 2px 6px 0 rgba(15, 23, 42, 0.02);
    }

    div[data-testid="stMetricValue"] {
        font-size: 16px !important;
        font-weight: 800 !important;
        color: #1e3a8a !important;
    }

    div[data-testid="stMetricLabel"] {
        color: #64748b !important;
        font-size: 11px !important;
        font-weight: 700 !important;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    section[data-testid="stSidebar"] {
        background-color: #ffffff;
        border-right: 1px solid #e2e8f0;
    }
    
    section[data-testid="stSidebar"] .stMarkdown {
        color: #0f172a;
        font-weight: 600;
    }

    .stTabs [data-baseweb="tab-list"] {
        gap: 16px;
        background-color: transparent;
        padding: 0px;
        border-bottom: 2px solid #cbd5e1;
        margin-bottom: 20px;
    }

    .stTabs [data-baseweb="tab"] {
        height: 38px;
        border-radius: 0px;
        border: none;
        color: #64748b;
        font-weight: 700;
        background-color: transparent;
        padding: 0 4px;
        border-bottom: 2px solid transparent;
    }

    .stTabs [aria-selected="true"] {
        background-color: transparent !important;
        color: #1d4ed8 !important;
        border-bottom: 2px solid #1d4ed8 !important;
        box-shadow: none !important;
    }

    h2, h3, .stSubheader {
        color: #0f172a !important;
        font-weight: 800 !important;
        font-size: 18px !important;
        letter-spacing: -0.3px;
        user-select: text !important;
    }

    .stDataFrame {
        border-radius: 10px;
        overflow: hidden;
        border: 1px solid #e2e8f0;
        background-color: #ffffff;
    }

    .stButton > button, .stDownloadButton > button {
        background-color: #1e3a8a;
        color: white;
        border: none;
        border-radius: 8px;
        padding: 8px 18px;
        font-weight: 700;
        font-size: 13px;
        box-shadow: 0 2px 4px 0 rgba(30, 58, 138, 0.2);
    }

    @media print {
        section[data-testid="stSidebar"] {
            display: none !important;
        }
        header {
            display: none !important;
        }
        .stButton, .stDownloadButton {
            display: none !important;
        }
        .stTabs [data-baseweb="tab-list"] {
            display: none !important;
        }
        body {
            background: white !important;
            color: black !important;
        }
        .block-container {
            padding: 0 !important;
            max-width: 100% !important;
        }
    }
</style>
""",
    unsafe_allow_html=True,
)


# ============================================================
# DATA LOADING & PREPROCESSING (PURE ID KASUS FINAL & GROUPING)
# ============================================================

DATA_FOLDER = "data"


def find_excel_file():
    if not os.path.exists(DATA_FOLDER):
        return None
    excel_files = [
        f
        for f in os.listdir(DATA_FOLDER)
        if f.lower().endswith((".xlsx", ".xls")) and not f.startswith("~$")
    ]
    if len(excel_files) == 0:
        return None
    return os.path.join(DATA_FOLDER, excel_files[0])


@st.cache_data(show_spinner=False)
def load_and_process_data(file_path):
    df = pd.read_excel(file_path, sheet_name="JKK_CLEANING")
    
    try:
        df_grouping = pd.read_excel(file_path, sheet_name="GROUPING")
    except Exception:
        df_grouping = pd.DataFrame()
    
    def get_col(df_obj, target_names):
        cols_map = {str(col).strip().lower(): col for col in df_obj.columns}
        for target in target_names:
            key = target.strip().lower()
            if key in cols_map:
                return cols_map[key]
        return None

    jam_col_name = get_col(
        df, ["Ket Jam Final", "ket_jam_final", "Ket_Jam_Final", "jam_kecelakaan"]
    )
    range_usia_col_name = get_col(df, ["Range Usia", "range usia", "range_usia", "usia"])
    
    cols_list = list(df.columns)
    npp_col_name = cols_list[1] if len(cols_list) > 1 else get_col(df, ["NPP", "npp"])
    perusahaan_col_name = cols_list[2] if len(cols_list) > 2 else get_col(df, ["Nama Perusahaan Final", "Nama Perusahaan", "nama perusahaan", "nama_perusahaan"])

    if "tgl_kejadian" in df.columns:
        df["tgl_kejadian"] = pd.to_datetime(df["tgl_kejadian"], errors="coerce")

    if "nom_manfaat_netto" in df.columns:
        df["nom_manfaat_netto"] = pd.to_numeric(
            df["nom_manfaat_netto"], errors="coerce"
        ).fillna(0)

    if "ID Kasus Final" in df.columns:
        df = df[df["ID Kasus Final"].notna()].copy()

    if "Jenis Kelamin" in df.columns:
        df["Jenis Kelamin"] = df["Jenis Kelamin"].astype(str).str.strip().replace({
            "L": "Laki-laki",
            "P": "Perempuan",
            "l": "Laki-laki",
            "p": "Perempuan"
        })

    case_cols = [
        "ID Kasus Final",
        "Kode TK Final",
        "Nama TK Final",
        "tgl_kejadian",
        "Nama Kanwil Pelayanan",
        "Nama Kantor Pelayanan (Cabang)",
        "Jenis Kelamin",
        "Nama Sumber Cedera Final",
        "Nama Bagian Sakit Final",
        "Nama Lokasi Kecelakaan Final",
        "Nama Tempat Kecelakaa Final",
        "Kondisi Akhir",
        "Sektor BPS Final",
    ]

    if range_usia_col_name:
        case_cols.append(range_usia_col_name)
    if jam_col_name:
        case_cols.append(jam_col_name)
    if npp_col_name:
        case_cols.append(npp_col_name)
    if perusahaan_col_name:
        case_cols.append(perusahaan_col_name)

    available_case_cols = [col for col in case_cols if col in df.columns]
    
    groupby_keys = ["ID Kasus Final"]

    agg_dict = {col: "first" for col in available_case_cols if col not in groupby_keys}
    if "nom_manfaat_netto" in df.columns:
        agg_dict["nom_manfaat_netto"] = "sum"

    cases_df = df.groupby(groupby_keys, as_index=False).agg(agg_dict)

    if "tgl_kejadian" in cases_df.columns:
        cases_df["Tahun"] = cases_df["tgl_kejadian"].dt.year
        cases_df["Bulan"] = cases_df["tgl_kejadian"].dt.month
        cases_df["Nama Bulan"] = cases_df["tgl_kejadian"].dt.strftime("%b")

    if range_usia_col_name and range_usia_col_name in cases_df.columns:
        numeric_age = pd.to_numeric(cases_df[range_usia_col_name], errors="coerce")
        
        if numeric_age.notna().sum() > 0:
            cases_df["Range Usia"] = "Tidak Diketahui"
            valid_mask = (numeric_age >= 18) & (numeric_age <= 100)
            
            cases_df.loc[valid_mask & (numeric_age <= 30), "Range Usia"] = "≤ 30 Tahun"
            cases_df.loc[valid_mask & (numeric_age >= 31) & (numeric_age <= 50), "Range Usia"] = "31 - 50 Tahun"
            cases_df.loc[valid_mask & (numeric_age >= 51), "Range Usia"] = "≥ 51 Tahun"
        else:
            cases_df["Range Usia Clean"] = cases_df[range_usia_col_name].astype(str).str.strip()
            
            mapping_usia = {
                "<= 30 Tahun": "≤ 30 Tahun",
                "<=30": "≤ 30 Tahun",
                "31 - 50 Tahun": "31 - 50 Tahun",
                "31-50": "31 - 50 Tahun",
                ">= 51 Tahun": "≥ 51 Tahun",
                ">=51": "≥ 51 Tahun",
            }
            cases_df["Range Usia"] = cases_df["Range Usia Clean"].replace(mapping_usia)
            
            valid_age_labels = [
                "≤ 30 Tahun",
                "31 - 50 Tahun",
                "≥ 51 Tahun"
            ]
            cases_df.loc[~cases_df["Range Usia"].isin(valid_age_labels), "Range Usia"] = "Tidak Diketahui"
    else:
        cases_df["Range Usia"] = "Tidak Diketahui"

    if not df_grouping.empty:
        df_grouping.columns = [str(c).strip() for c in df_grouping.columns]
        
        col_map_group = {}
        for c in df_grouping.columns:
            c_low = c.lower()
            if "kanwil" in c_low:
                col_map_group[c] = "Nama Kanwil Pelayanan"
            elif "cabang" in c_low or "kantor" in c_low:
                col_map_group[c] = "Nama Kantor Pelayanan (Cabang)"
            elif "jumlah" in c_low and "kasus" in c_low:
                col_map_group[c] = "Jumlah_Kasus"
            elif "nominal" in c_low or "manfaat" in c_low:
                col_map_group[c] = "Total_Nominal"
        df_grouping = df_grouping.rename(columns=col_map_group)

        if "Jumlah_Kasus" in df_grouping.columns:
            df_grouping["Jumlah_Kasus"] = pd.to_numeric(df_grouping["Jumlah_Kasus"], errors="coerce").fillna(0)
        if "Total_Nominal" in df_grouping.columns:
            df_grouping["Total_Nominal"] = pd.to_numeric(df_grouping["Total_Nominal"], errors="coerce").fillna(0)

    return cases_df, df_grouping, jam_col_name, npp_col_name, perusahaan_col_name


file_path = find_excel_file()
if file_path is None:
    st.error("File Excel tidak ditemukan. Pastikan file JKK berada di folder 'data'.")
    st.stop()

try:
    with st.spinner("Memuat dan memproses data..."):
        cases, df_grouping, jam_col, npp_col_name, perusahaan_col_name = load_and_process_data(file_path)
except Exception as e:
    st.error(f"Gagal membaca file Excel: {e}")
    st.stop()


# ============================================================
# SIDEBAR FILTER
# ============================================================

st.sidebar.title("🎛️ Filter Dashboard")
st.sidebar.markdown("---")

years = sorted(cases["Tahun"].dropna().unique().tolist()) if "Tahun" in cases.columns else []
selected_year = st.sidebar.multiselect("Tahun", options=years, default=years)

if not df_grouping.empty and "Nama Kanwil Pelayanan" in df_grouping.columns:
    kanwil_options = sorted(df_grouping["Nama Kanwil Pelayanan"].dropna().astype(str).unique())
else:
    kanwil_options = sorted(cases["Nama Kanwil Pelayanan"].dropna().astype(str).unique()) if "Nama Kanwil Pelayanan" in cases.columns else []

selected_kanwil = st.sidebar.multiselect(
    "Kanwil Pelayanan", options=kanwil_options, default=[]
)

if not df_grouping.empty and "Nama Kantor Pelayanan (Cabang)" in df_grouping.columns:
    filtered_for_branch_group = df_grouping.copy()
    if selected_kanwil and "Nama Kanwil Pelayanan" in filtered_for_branch_group.columns:
        filtered_for_branch_group = filtered_for_branch_group[
            filtered_for_branch_group["Nama Kanwil Pelayanan"].isin(selected_kanwil)
        ]
    branch_options = sorted(filtered_for_branch_group["Nama Kantor Pelayanan (Cabang)"].dropna().astype(str).unique())
else:
    filtered_for_branch = cases.copy()
    if selected_kanwil and "Nama Kanwil Pelayanan" in filtered_for_branch.columns:
        filtered_for_branch = filtered_for_branch[
            filtered_for_branch["Nama Kanwil Pelayanan"].isin(selected_kanwil)
        ]
    branch_options = sorted(
        filtered_for_branch["Nama Kantor Pelayanan (Cabang)"]
        .dropna()
        .astype(str)
        .unique()
    ) if "Nama Kantor Pelayanan (Cabang)" in filtered_for_branch.columns else []

selected_branch = st.sidebar.multiselect(
    "Cabang Pelayanan", options=branch_options, default=[]
)

gender_options = sorted(cases["Jenis Kelamin"].dropna().astype(str).unique()) if "Jenis Kelamin" in cases.columns else []
selected_gender = st.sidebar.multiselect(
    "Jenis Kelamin", options=gender_options, default=[]
)

sector_options = sorted(
    cases["Sektor BPS Final"].dropna().astype(str).unique()
) if "Sektor BPS Final" in cases.columns else []
selected_sector = st.sidebar.multiselect(
    "Sektor BPS Final", options=sector_options, default=[]
)

age_group_options = [
    "≤ 30 Tahun",
    "31 - 50 Tahun",
    "≥ 51 Tahun",
    "Tidak Diketahui"
]
selected_age_groups = st.sidebar.multiselect(
    "Range Usia", options=age_group_options, default=[]
)

location_options = sorted(
    cases["Nama Lokasi Kecelakaan Final"].dropna().astype(str).unique()
) if "Nama Lokasi Kecelakaan Final" in cases.columns else []
selected_location = st.sidebar.multiselect(
    "Lokus Kecelakaan", options=location_options, default=[]
)

filtered = cases
if selected_year and "Tahun" in filtered.columns:
    filtered = filtered[filtered["Tahun"].isin(selected_year)]
if selected_kanwil and "Nama Kanwil Pelayanan" in filtered.columns:
    filtered = filtered[filtered["Nama Kanwil Pelayanan"].isin(selected_kanwil)]
if selected_branch and "Nama Kantor Pelayanan (Cabang)" in filtered.columns:
    filtered = filtered[filtered["Nama Kantor Pelayanan (Cabang)"].isin(selected_branch)]
if selected_gender and "Jenis Kelamin" in filtered.columns:
    filtered = filtered[filtered["Jenis Kelamin"].isin(selected_gender)]
if selected_sector and "Sektor BPS Final" in filtered.columns:
    filtered = filtered[filtered["Sektor BPS Final"].isin(selected_sector)]
if selected_age_groups and "Range Usia" in filtered.columns:
    filtered = filtered[filtered["Range Usia"].isin(selected_age_groups)]
if selected_location and "Nama Lokasi Kecelakaan Final" in filtered.columns:
    filtered = filtered[filtered["Nama Lokasi Kecelakaan Final"].isin(selected_location)]


# ============================================================
# TITLE & KPI METRICS
# ============================================================

total_cases = filtered["ID Kasus Final"].nunique() if "ID Kasus Final" in filtered.columns else 0
total_benefit = filtered["nom_manfaat_netto"].sum() if "nom_manfaat_netto" in filtered.columns else 0
total_workers = filtered["Kode TK Final"].nunique() if "Kode TK Final" in filtered.columns else 0
total_branches = filtered["Nama Kantor Pelayanan (Cabang)"].nunique() if "Nama Kantor Pelayanan (Cabang)" in filtered.columns else 0

st.markdown(
    """
    <div class="corporate-title-center">
        <div class="corporate-title-main">Dashboard JKK Analytics & Insights 2025</div>
        <div class="corporate-subtitle-main">Monitoring Kecelakaan Kerja, Profil Risiko & Segmentasi Manfaat JKK</div>
    </div>
    """,
    unsafe_allow_html=True,
)

kcol1, kcol2, kcol3, kcol4 = st.columns(4)
with kcol1:
    st.metric("Total Kasus JKK", format_number(total_cases))
with kcol2:
    st.metric("Total Nominal Manfaat", format_currency(total_benefit))
with kcol3:
    st.metric("Total Tenaga Kerja", format_number(total_workers))
with kcol4:
    st.metric("Jumlah Cabang Active", format_number(total_branches))

st.markdown("<br>", unsafe_allow_html=True)


# ============================================================
# PAGE TABS
# ============================================================

tab1, tab2, tab3, tab4 = st.tabs(
    ["Kanwil & Cabang", "Sektor BPS", "Profil Kecelakaan", "Case Explorer"]
)

chart_theme = "plotly_white"


# ============================================================
# TAB 1: KANWIL & CABANG (SUMBER DATA GROUPING)
# ============================================================

with tab1:
    if not df_grouping.empty:
        tab1_source = df_grouping.copy()
        if selected_kanwil and "Nama Kanwil Pelayanan" in tab1_source.columns:
            tab1_source = tab1_source[tab1_source["Nama Kanwil Pelayanan"].isin(selected_kanwil)]
        if selected_branch and "Nama Kantor Pelayanan (Cabang)" in tab1_source.columns:
            tab1_source = tab1_source[tab1_source["Nama Kantor Pelayanan (Cabang)"].isin(selected_branch)]
    else:
        tab1_source = pd.DataFrame()

    if not selected_kanwil:
        if selected_branch:
            branch_str = ", ".join(selected_branch)
            st.markdown(f"### Analisis Kasus & Nominal Manfaat per Cabang di Cabang: {branch_str}")
        else:
            st.markdown("### Analisis Kasus & Nominal Manfaat per Kanwil Pelayanan")
        
        group_col = "Nama Kanwil Pelayanan"
        
        if not tab1_source.empty and group_col in tab1_source.columns:
            kanwil_summary = tab1_source.groupby(group_col, as_index=False).agg({
                "Jumlah_Kasus": "sum",
                "Total_Nominal": "sum"
            })
            kanwil_summary = kanwil_summary.sort_values("Jumlah_Kasus", ascending=False)

            wrapped_names = wrap_labels(kanwil_summary[group_col], width=14)
            compact_labels = [format_currency_compact_intl(n) for n in kanwil_summary["Total_Nominal"]]
            formatted_hover_nominal = [format_currency(val) for val in kanwil_summary["Total_Nominal"]]

            bar_fonts = [
                10.5 if count < 5000 else 9.5 for count in kanwil_summary["Jumlah_Kasus"]
            ]

            max_case_kanwil = kanwil_summary["Jumlah_Kasus"].max() if not kanwil_summary["Jumlah_Kasus"].empty else 10
            
            if max_case_kanwil <= 50:
                suggested_max_y_kanwil = 100
                dynamic_dtick_kanwil = 20
            else:
                suggested_max_y_kanwil = max_case_kanwil * 1.1
                if max_case_kanwil > 20000:
                    dynamic_dtick_kanwil = 5000
                elif max_case_kanwil > 5000:
                    dynamic_dtick_kanwil = 2000
                elif max_case_kanwil > 1000:
                    dynamic_dtick_kanwil = 500
                elif max_case_kanwil > 200:
                    dynamic_dtick_kanwil = 100
                else:
                    dynamic_dtick_kanwil = 20

            max_nominal_kanwil = kanwil_summary["Total_Nominal"].max() if not kanwil_summary["Total_Nominal"].empty else 100
            suggested_max_y2_kanwil = max_nominal_kanwil * 1.1 if max_nominal_kanwil > 0 else 100

            fig_dual_kanwil = go.Figure()

            fig_dual_kanwil.add_trace(go.Bar(
                x=wrapped_names,
                y=kanwil_summary["Jumlah_Kasus"],
                name="Jumlah Kasus",
                marker=dict(color="#d97706", opacity=0.9),
                text=[f"{format_number(c)}" for c in kanwil_summary["Jumlah_Kasus"]],
                textposition="inside",
                insidetextanchor="start",
                textfont=dict(size=bar_fonts, color="#1e3a8a", family="Inter, sans-serif"),
                customdata=kanwil_summary[group_col],
                hovertemplate="<b>%{customdata}</b><br>Jumlah Kasus: <b>%{y:,} kasus</b><extra></extra>",
                yaxis="y"
            ))

            fig_dual_kanwil.add_trace(go.Scatter(
                x=wrapped_names,
                y=kanwil_summary["Total_Nominal"],
                name="Total Nominal Manfaat",
                mode="lines+markers+text",
                line=dict(color="#059669", width=3.5),
                marker=dict(size=10, color="#059669", line=dict(color="#ffffff", width=2)),
                text=compact_labels,
                textposition="top center",
                textfont=dict(size=9.5, color="#065f46", family="Inter, sans-serif"),
                customdata=np.stack([kanwil_summary[group_col], formatted_hover_nominal], axis=-1),
                hovertemplate="<b>%{customdata[0]}</b><br>Total Nominal Manfaat: <b>%{customdata[1]}</b><extra></extra>",
                yaxis="y2"
            ))

            fig_dual_kanwil.update_layout(
                template=chart_theme,
                height=880,
                margin=dict(l=50, r=50, t=20, b=90),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                xaxis=dict(
                    title="",
                    showticklabels=True,
                    showgrid=False,
                    zeroline=False,
                    tickangle=0,
                    tickfont=dict(size=8.5, color="#0f172a", family="Inter, sans-serif")
                ),
                yaxis=dict(
                    title="",
                    showticklabels=False,
                    showgrid=False,
                    zeroline=False,
                    side="left",
                    rangemode="tozero",
                    range=[0, suggested_max_y_kanwil],
                    dtick=dynamic_dtick_kanwil
                ),
                yaxis2=dict(
                    title="",
                    overlaying="y",
                    side="right",
                    showticklabels=False,
                    showgrid=False,
                    zeroline=False,
                    rangemode="tozero",
                    range=[0, suggested_max_y2_kanwil]
                ),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
            )

            st.plotly_chart(fig_dual_kanwil, use_container_width=True)

    else:
        kanwil_str = ", ".join(selected_kanwil)
        if selected_branch:
            branch_str = ", ".join(selected_branch)
            st.markdown(f"### Analisis Kasus & Nominal Manfaat per Cabang di Kanwil: {kanwil_str} | Cabang: {branch_str}")
        else:
            st.markdown(f"### Analisis Kasus & Nominal Manfaat per Cabang di Kanwil: {kanwil_str}")
        group_col = "Nama Kantor Pelayanan (Cabang)"

        if not tab1_source.empty and group_col in tab1_source.columns:
            branch_summary = tab1_source.groupby([ "Nama Kanwil Pelayanan", group_col ], as_index=False).agg({
                "Jumlah_Kasus": "sum",
                "Total_Nominal": "sum"
            })
            branch_summary = branch_summary.sort_values("Jumlah_Kasus", ascending=True)

            branch_names = branch_summary[group_col].tolist()
            kasus_vals = branch_summary["Jumlah_Kasus"].tolist()
            nominal_vals = branch_summary["Total_Nominal"].tolist()

            kasus_text = [f"{format_number(c)}" for c in kasus_vals]
            nominal_text = [format_currency_compact_intl(n) for n in nominal_vals]
            formatted_hover_nominal = [format_currency(n) for n in nominal_vals]

            fig_pyramid = make_subplots(
                rows=1, cols=2,
                shared_yaxes=True,
                horizontal_spacing=0.08
            )

            fig_pyramid.add_trace(go.Bar(
                y=branch_names,
                x=kasus_vals,
                name="Jumlah Kasus",
                orientation="h",
                marker=dict(color="#0284c7"),
                text=kasus_text,
                textposition="inside",
                insidetextanchor="middle",
                textfont=dict(size=11, color="white", family="Inter, sans-serif"),
                customdata=np.stack([branch_names, kasus_vals], axis=-1),
                hovertemplate="Cabang: <b>%{customdata[0]}</b><br>Jumlah Kasus: <b>%{customdata[1]:,} kasus</b><extra></extra>"
            ), row=1, col=1)

            fig_pyramid.add_trace(go.Bar(
                y=branch_names,
                x=nominal_vals,
                name="Total Nominal Manfaat",
                orientation="h",
                marker=dict(color="#059669"),
                text=nominal_text,
                textposition="inside",
                insidetextanchor="middle",
                textfont=dict(size=11, color="white", family="Inter, sans-serif"),
                customdata=np.stack([branch_names, formatted_hover_nominal], axis=-1),
                hovertemplate="Cabang: <b>%{customdata[0]}</b><br>Total Nominal Manfaat: <b>%{customdata[1]}</b><extra></extra>"
            ), row=1, col=2)

            fig_pyramid.update_layout(
                template=chart_theme,
                height=max(650, len(branch_summary) * 40),
                margin=dict(l=180, r=50, t=60, b=40),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                showlegend=True,
                legend=dict(orientation="h", yanchor="bottom", y=1.08, xanchor="center", x=0.5)
            )

            fig_pyramid.update_xaxes(
                title_text="<b>◄ Jumlah Kasus (Log Scale)</b>",
                type="log",
                autorange="reversed",
                row=1, col=1,
                showgrid=True
            )
            fig_pyramid.update_xaxes(
                title_text="<b>Total Nominal Manfaat (Rp, Log Scale) ►</b>",
                type="log",
                row=1, col=2,
                showgrid=True
            )
            fig_pyramid.update_yaxes(tickfont=dict(size=11, color="#0f172a", family="Inter, sans-serif"))

            st.plotly_chart(fig_pyramid, use_container_width=True)

    st.markdown("<hr style='margin: 15px 0 30px 0; border-color: #e2e8f0;'>", unsafe_allow_html=True)
    
    if not selected_kanwil:
        if selected_branch:
            st.markdown("### Detail Jumlah Kasus, Nominal & Rata-rata")
        else:
            st.markdown("### Detail Jumlah Kasus, Nominal & Rata-rata di Masing-masing Kanwil")
    else:
        st.markdown("### Detail Jumlah Kasus, Nominal & Rata-rata di Masing-masing Cabang")

    if not tab1_source.empty:
        if not selected_kanwil:
            summary_table = tab1_source.groupby("Nama Kanwil Pelayanan", as_index=False).agg({
                "Jumlah_Kasus": "sum",
                "Total_Nominal": "sum"
            })
            summary_table.columns = ["Nama Kanwil Pelayanan", "Jumlah_Kasus", "Nominal_Manfaat"]
        else:
            summary_table = tab1_source.groupby(["Nama Kanwil Pelayanan", "Nama Kantor Pelayanan (Cabang)"], as_index=False).agg({
                "Jumlah_Kasus": "sum",
                "Total_Nominal": "sum"
            })
            summary_table.columns = ["Nama Kanwil Pelayanan", "Nama Kantor Pelayanan (Cabang)", "Jumlah_Kasus", "Nominal_Manfaat"]
            
        summary_table["Rata-rata Manfaat/Kasus"] = summary_table.apply(
            lambda row: (row["Nominal_Manfaat"] / row["Jumlah_Kasus"]) if row["Jumlah_Kasus"] > 0 else 0, axis=1
        )
        summary_table = summary_table.sort_values("Jumlah_Kasus", ascending=False)

        display_tbl = summary_table.copy()
        display_tbl["Jumlah_Kasus"] = display_tbl["Jumlah_Kasus"].apply(format_number)
        display_tbl["Nominal_Manfaat"] = display_tbl["Nominal_Manfaat"].apply(format_currency)
        display_tbl["Rata-rata Manfaat/Kasus"] = display_tbl["Rata-rata Manfaat/Kasus"].apply(format_currency)

        st.dataframe(display_tbl, use_container_width=True, hide_index=True)


# ============================================================
# TAB 2: SEKTOR BPS
# ============================================================

with tab2:
    if "Sektor BPS Final" in filtered.columns:
        active_filters_list = []
        if selected_kanwil:
            active_filters_list.append(f"Kanwil: {', '.join(selected_kanwil)}")
        if selected_branch:
            active_filters_list.append(f"Cabang: {', '.join(selected_branch)}")
        if selected_sector:
            active_filters_list.append(f"Sektor BPS: {', '.join(selected_sector)}")
        if selected_gender:
            active_filters_list.append(f"Jenis Kelamin: {', '.join(selected_gender)}")
        if selected_age_groups:
            active_filters_list.append(f"Range Usia: {', '.join(selected_age_groups)}")
        if selected_location:
            active_filters_list.append(f"Lokus: {', '.join(selected_location)}")
        
        if active_filters_list:
            st.markdown(f"Menampilkan data berdasarkan filter aktif: *{ ' | '.join(active_filters_list) }*")
        else:
            st.markdown("Menampilkan data secara nasional.")

        st.markdown("### Top 15 Sektor BPS Berdasarkan Jumlah Kasus & Nominal Manfaat")
        
        bps_data = pd.pivot_table(
            filtered,
            index="Sektor BPS Final",
            values=["ID Kasus Final", "nom_manfaat_netto"],
            aggfunc={"ID Kasus Final": "nunique", "nom_manfaat_netto": "sum"}
        ).reset_index()
        
        if not bps_data.empty:
            bps_data.columns = ["Sektor BPS Final", "Jumlah_Kasus", "Total_Nominal"]
            bps_data = bps_data.sort_values("Jumlah_Kasus", ascending=False).head(15)

            wrapped_sector_names = wrap_labels(bps_data["Sektor BPS Final"], width=14)
            compact_labels = [format_currency_compact_intl(n) for n in bps_data["Total_Nominal"]]
            formatted_hover_nominal = [format_currency(val) for val in bps_data["Total_Nominal"]]

            bar_fonts = [9.5 for _ in range(len(bps_data))]

            max_case_bps = bps_data["Jumlah_Kasus"].max() if not bps_data["Jumlah_Kasus"].empty else 10
            
            if max_case_bps <= 50:
                suggested_max_y_bps = 100
                dynamic_dtick_bps = 20
            else:
                suggested_max_y_bps = max_case_bps * 1.15
                if max_case_bps > 20000:
                    dynamic_dtick_bps = 5000
                elif max_case_bps > 5000:
                    dynamic_dtick_bps = 2000
                elif max_case_bps > 1000:
                    dynamic_dtick_bps = 500
                elif max_case_bps > 200:
                    dynamic_dtick_bps = 100
                else:
                    dynamic_dtick_bps = 20

            max_nominal_val = bps_data["Total_Nominal"].max() if not bps_data["Total_Nominal"].empty else 100
            suggested_max_y2 = max_nominal_val * 1.15

            fig_dual = go.Figure()

            fig_dual.add_trace(go.Bar(
                x=wrapped_sector_names,
                y=bps_data["Jumlah_Kasus"],
                name="Jumlah Kasus",
                marker=dict(color="#60a5fa", opacity=0.9),
                text=[f"{format_number(c)}" for c in bps_data["Jumlah_Kasus"]],
                textposition="inside",
                insidetextanchor="start",
                textfont=dict(size=9.5, color="#1e3a8a", family="Inter, sans-serif"),
                customdata=bps_data["Sektor BPS Final"],
                hovertemplate="Sektor: <b>%{customdata}</b><br>Jumlah Kasus: <b>%{y:,} kasus</b><extra></extra>",
                yaxis="y"
            ))

            fig_dual.add_trace(go.Scatter(
                x=wrapped_sector_names,
                y=bps_data["Total_Nominal"],
                name="Total Nominal Manfaat",
                mode="lines+markers+text",
                line=dict(color="#059669", width=3.5),
                marker=dict(size=10, color="#059669", line=dict(color="#ffffff", width=2)),
                text=compact_labels,
                textposition="top center",
                textfont=dict(size=10, color="#065f46", family="Inter, sans-serif"),
                customdata=np.stack([bps_data["Sektor BPS Final"], formatted_hover_nominal], axis=-1),
                hovertemplate="Sektor: <b>%{customdata[0]}</b><br>Total Nominal Manfaat: <b>%{customdata[1]}</b><extra></extra>",
                yaxis="y2"
            ))

            fig_dual.update_layout(
                template=chart_theme,
                height=880,
                margin=dict(l=50, r=50, t=40, b=90),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                xaxis=dict(
                    title="",
                    tickangle=0,
                    showticklabels=True,
                    showgrid=False,
                    zeroline=False,
                    tickfont=dict(size=8.5, color="#0f172a", family="Inter, sans-serif")
                ),
                yaxis=dict(
                    title="",
                    showticklabels=False,
                    showgrid=False,
                    zeroline=False,
                    side="left",
                    rangemode="tozero",
                    range=[0, suggested_max_y_bps],
                    dtick=dynamic_dtick_bps
                ),
                yaxis2=dict(
                    title="",
                    overlaying="y",
                    side="right",
                    showticklabels=False,
                    showgrid=False,
                    zeroline=False,
                    rangemode="tozero",
                    range=[0, suggested_max_y2]
                ),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
            )

            st.plotly_chart(fig_dual, use_container_width=True)

            st.markdown("<hr style='margin: 15px 0 30px 0; border-color: #e2e8f0;'>", unsafe_allow_html=True)
            st.markdown("### Tabel Rincian Seluruh Sektor BPS")

            bps_full = pd.pivot_table(
                filtered,
                index="Sektor BPS Final",
                values=["ID Kasus Final", "nom_manfaat_netto"],
                aggfunc={"ID Kasus Final": "nunique", "nom_manfaat_netto": "sum"}
            ).reset_index()
            bps_full.columns = ["Sektor BPS Final", "Jumlah_Kasus", "Total_Nominal"]
            bps_full = bps_full.sort_values("Jumlah_Kasus", ascending=False)

            bps_display = bps_full.copy()
            bps_display["Jumlah_Kasus"] = bps_display["Jumlah_Kasus"].apply(format_number)
            bps_display["Total_Nominal"] = bps_display["Total_Nominal"].apply(format_currency)

            st.dataframe(bps_display, use_container_width=True, hide_index=True)
        else:
            st.info("Tidak ada data Sektor BPS yang tersedia dengan filter yang dipilih.")


# ============================================================
# TAB 3: PROFIL KECELAKAAN
# ============================================================

with tab3:
    active_filters_list = []
    if selected_kanwil:
        active_filters_list.append(f"Kanwil: {', '.join(selected_kanwil)}")
    if selected_branch:
        active_filters_list.append(f"Cabang: {', '.join(selected_branch)}")
    if selected_sector:
        active_filters_list.append(f"Sektor BPS: {', '.join(selected_sector)}")
    if selected_gender:
        active_filters_list.append(f"Jenis Kelamin: {', '.join(selected_gender)}")
    if selected_age_groups:
        active_filters_list.append(f"Range Usia: {', '.join(selected_age_groups)}")
    if selected_location:
        active_filters_list.append(f"Lokus: {', '.join(selected_location)}")
    
    if active_filters_list:
        profile_filter_text = f"Menampilkan data berdasarkan filter aktif: {' | '.join(active_filters_list)}"
    else:
        profile_filter_text = "Menampilkan data secara nasional."

    st.markdown(f"{profile_filter_text}")

    if "Range Usia" in filtered.columns:
        st.markdown("### Persentase Distribusi Range Usia Tenaga Kerja")
        
        age_agg = pd.pivot_table(
            filtered,
            index="Range Usia",
            values="ID Kasus Final",
            aggfunc="nunique"
        ).reset_index()
        
        if not age_agg.empty:
            age_agg.columns = ["Range Usia", "Jumlah_Kasus"]
            
            age_order = [
                "≤ 30 Tahun",
                "31 - 50 Tahun",
                "≥ 51 Tahun",
                "Tidak Diketahui"
            ]
            age_agg["Range Usia"] = pd.Categorical(age_agg["Range Usia"], categories=age_order, ordered=True)
            age_agg = age_agg.sort_values("Range Usia")

            total_age_cases = age_agg["Jumlah_Kasus"].sum()
            age_agg["Persentase"] = (age_agg["Jumlah_Kasus"] / total_age_cases * 100).round(1) if total_age_cases > 0 else 0
            
            col_a, col_b = st.columns([1.2, 1])
            
            with col_a:
                fig_pie = px.pie(
                    age_agg,
                    names="Range Usia",
                    values="Jumlah_Kasus",
                    hole=0.0,
                    color_discrete_sequence=["#db2777", "#fbbf24", "#8b5cf6", "#94a3b8"],
                    template=chart_theme
                )
                fig_pie.update_traces(
                    textinfo="percent+label",
                    textfont=dict(size=12, family="Inter, sans-serif"),
                    marker=dict(line=dict(color="#ffffff", width=2)),
                    customdata=np.stack([
                        age_agg["Jumlah_Kasus"].apply(format_number),
                        age_agg["Persentase"].astype(str)
                    ], axis=-1),
                    hovertemplate="<b>Range Usia:</b> %{label}<br><b>Jumlah Kasus:</b> %{customdata[0]} kasus<br><b>Persentase:</b> %{customdata[1]}%<extra></extra>"
                )
                fig_pie.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    margin=dict(t=20, b=40, l=20, r=20),
                    legend=dict(orientation="h", yanchor="bottom", y=-0.3, xanchor="center", x=0.5)
                )
                st.plotly_chart(fig_pie, use_container_width=True)

            with col_b:
                st.markdown("##### Ringkasan Data Range Usia")
                age_display = age_agg.copy()
                age_display["Persentase (%)"] = age_display["Persentase"].astype(str).str.replace(".", ",") + " %"
                age_display["Jumlah_Kasus"] = age_display["Jumlah_Kasus"].apply(format_number)
                age_display = age_display[["Range Usia", "Jumlah_Kasus", "Persentase (%)"]]
                
                st.dataframe(age_display, use_container_width=True, hide_index=True)

        st.markdown(
            """
            <div style="background-color: #f8fafc; border-left: 4px solid #3b82f6; padding: 10px 15px; border-radius: 4px; font-size: 13.5px; color: #334155; margin-top: 10px; margin-bottom: 25px;">
                <b>Catatan:</b> Data dengan rentang usia di luar 18–100 tahun telah disaring melalui proses data cleansing dan dikategorikan sebagai "Tidak Diketahui".
            </div>
            """,
            unsafe_allow_html=True
        )

        st.markdown("<hr style='margin: 30px 0; border-color: #e2e8f0;'>", unsafe_allow_html=True)

    if "Jenis Kelamin" in filtered.columns:
        gender_agg = pd.pivot_table(
            filtered,
            index="Jenis Kelamin",
            values=["ID Kasus Final", "nom_manfaat_netto"],
            aggfunc={"ID Kasus Final": "nunique", "nom_manfaat_netto": "sum"}
        ).reset_index()
        
        if not gender_agg.empty:
            gender_agg.columns = ["Jenis Kelamin", "Jumlah_Kasus", "Total_Nominal"]
            
            total_g_cases = gender_agg["Jumlah_Kasus"].sum()
            gender_agg["Persentase (%)"] = (
                (gender_agg["Jumlah_Kasus"] / total_g_cases * 100).round(2) if total_g_cases > 0 else 0
            )

            col1, col2 = st.columns([1, 1])

            with col1:
                st.markdown("### Rasio Kasus Berdasarkan Jenis Kelamin")
                fig_gender = px.pie(
                    gender_agg,
                    names="Jenis Kelamin",
                    values="Jumlah_Kasus",
                    hole=0.45,
                    color_discrete_sequence=["#1d4ed8", "#db2777", "#64748b"],
                    template=chart_theme,
                )
                fig_gender.update_traces(
                    textinfo="percent+label", 
                    textfont=dict(size=13),
                    marker=dict(line=dict(color="#ffffff", width=2))
                )
                fig_gender.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)', 
                    plot_bgcolor='rgba(0,0,0,0)',
                    margin=dict(t=20, b=20, l=20, r=20)
                )
                st.plotly_chart(fig_gender, use_container_width=True)

            with col2:
                gender_display = gender_agg.copy()
                gender_display["Jumlah_Kasus"] = gender_display["Jumlah_Kasus"].apply(format_number)
                gender_display["Total_Nominal"] = gender_display["Total_Nominal"].apply(format_currency)
                gender_display["Persentase (%)"] = gender_display["Persentase (%)"].astype(str).str.replace(".", ",") + " %"

                st.markdown("### Tabel Ringkasan Rasio Jenis Kelamin")
                st.dataframe(gender_display, use_container_width=True, hide_index=True)

    st.markdown("<hr style='margin: 30px 0; border-color: #e2e8f0;'>", unsafe_allow_html=True)
    st.markdown("### Jam Kecelakaan & Lokus Kejadian")

    col1, col2 = st.columns(2)

    with col1:
        if jam_col and jam_col in filtered.columns:
            hour_data = pd.pivot_table(
                filtered,
                index=jam_col,
                values="ID Kasus Final",
                aggfunc="nunique"
            ).reset_index()
            
            if not hour_data.empty:
                hour_data.columns = [jam_col, "Jumlah_Kasus"]
                
                fig = px.area(
                    hour_data,
                    x=jam_col,
                    y="Jumlah_Kasus",
                    title="Distribusi Jam Kecelakaan Kerja",
                    markers=True,
                    color_discrete_sequence=["#d97706"],
                    template=chart_theme,
                )
                fig.update_layout(
                    xaxis_title="Waktu",
                    yaxis_title="Jumlah Kasus",
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)'
                )
                st.plotly_chart(fig, use_container_width=True)

    with col2:
        if "Nama Lokasi Kecelakaan Final" in filtered.columns:
            location_data = pd.pivot_table(
                filtered,
                index="Nama Lokasi Kecelakaan Final",
                values="ID Kasus Final",
                aggfunc="nunique"
            ).reset_index()
            
            if not location_data.empty:
                location_data.columns = ["Nama Lokasi Kecelakaan Final", "Jumlah_Kasus"]
                location_data = location_data.sort_values("Jumlah_Kasus", ascending=False)
                
                location_data["Formatted_Cases"] = location_data["Jumlah_Kasus"].apply(format_number)

                soft_colors = ["#93c5fd", "#86efac", "#fef08a", "#fbcfe8", "#cbd5e1"]
                fig = px.treemap(
                    location_data,
                    path=["Nama Lokasi Kecelakaan Final"],
                    values="Jumlah_Kasus",
                    title="Distribusi Lokus Kecelakaan",
                    color="Nama Lokasi Kecelakaan Final",
                    color_discrete_sequence=soft_colors,
                    template=chart_theme,
                )
                
                fig.update_traces(
                    customdata=location_data["Formatted_Cases"],
                    texttemplate="<b>%{label}</b><br><span style='font-size:11px;'>%{customdata} kasus</span>",
                    textfont=dict(size=13, color="#0f172a"),
                )
                fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
                st.plotly_chart(fig, use_container_width=True)

                st.markdown(
                    """
                    <div style="display: flex; flex-wrap: wrap; gap: 12px; font-size: 12.5px; color: #334155; margin-top: -10px; margin-bottom: 20px; align-items: center;">
                        <b></b>
                        <span style="display:inline-flex; align-items:center; gap:5px;"><span style="width:14px; height:14px; background-color:#93c5fd; display:inline-block; border-radius:3px;"></span> Dalam lingkungan kerja</span>
                        <span style="display:inline-flex; align-items:center; gap:5px;"><span style="width:14px; height:14px; background-color:#86efac; display:inline-block; border-radius:3px;"></span> Lalu lintas</span>
                        <span style="display:inline-flex; align-items:center; gap:5px;"><span style="width:14px; height:14px; background-color:#fef08a; display:inline-block; border-radius:3px;"></span> Luar lingkungan kerja</span>
                        <span style="display:inline-flex; align-items:center; gap:5px;"><span style="width:14px; height:14px; background-color:#fbcfe8; display:inline-block; border-radius:3px;"></span> Tidak diketahui</span>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

    st.markdown("<hr style='margin: 30px 0; border-color: #e2e8f0;'>", unsafe_allow_html=True)
    st.markdown("### Sumber Cedera, Bagian Sakit & Kondisi Akhir Pekerja")

    col1, col2 = st.columns(2)

    with col1:
        if "Nama Sumber Cedera Final" in filtered.columns:
            source_data = pd.pivot_table(
                filtered,
                index="Nama Sumber Cedera Final",
                values="ID Kasus Final",
                aggfunc="nunique"
            ).reset_index()
            
            if not source_data.empty:
                source_data.columns = ["Nama Sumber Cedera Final", "Jumlah_Kasus"]
                source_data = source_data.sort_values("Jumlah_Kasus", ascending=False).head(10)
                source_data = source_data.sort_values("Jumlah_Kasus", ascending=True)

                fig = px.bar(
                    source_data,
                    x="Jumlah_Kasus",
                    y="Nama Sumber Cedera Final",
                    orientation="h",
                    title="Top 10 Sumber Cedera",
                    color_discrete_sequence=["#7c3aed"],
                    template=chart_theme,
                    text=[format_number(c) for c in source_data["Jumlah_Kasus"]]
                )
                fig.update_traces(
                    textposition="outside",
                    textfont=dict(size=11, color="#1e293b", family="Inter, sans-serif")
                )
                fig.update_layout(
                    xaxis=dict(showticklabels=False, showgrid=False, zeroline=False, title=""),
                    yaxis=dict(showticklabels=True, title=""),
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    margin=dict(t=40, b=20, l=20, r=40)
                )
                st.plotly_chart(fig, use_container_width=True)

    with col2:
        if "Nama Bagian Sakit Final" in filtered.columns:
            body_data = pd.pivot_table(
                filtered,
                index="Nama Bagian Sakit Final",
                values="ID Kasus Final",
                aggfunc="nunique"
            ).reset_index()
            
            if not body_data.empty:
                body_data.columns = ["Nama Bagian Sakit Final", "Jumlah_Kasus"]
                body_data = body_data.sort_values("Jumlah_Kasus", ascending=False).head(10)
                body_data = body_data.sort_values("Jumlah_Kasus", ascending=True)

                fig = px.bar(
                    body_data,
                    x="Jumlah_Kasus",
                    y="Nama Bagian Sakit Final",
                    orientation="h",
                    title="Top 10 Bagian Tubuh yang Sakit",
                    color_discrete_sequence=["#059669"],
                    template=chart_theme,
                    text=[format_number(c) for c in body_data["Jumlah_Kasus"]]
                )
                fig.update_traces(
                    textposition="outside",
                    textfont=dict(size=11, color="#1e293b", family="Inter, sans-serif")
                )
                fig.update_layout(
                    xaxis=dict(showticklabels=False, showgrid=False, zeroline=False, title=""),
                    yaxis=dict(showticklabels=True, title=""),
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    margin=dict(t=40, b=20, l=20, r=40)
                )
                st.plotly_chart(fig, use_container_width=True)

    if "Kondisi Akhir" in filtered.columns:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("### Distribusi Kondisi Akhir Pekerja (Funnel Chart)")
        
        cond_data = pd.pivot_table(
            filtered,
            index="Kondisi Akhir",
            values="ID Kasus Final",
            aggfunc="nunique"
        ).reset_index()
        
        if not cond_data.empty:
            cond_data.columns = ["Kondisi Akhir", "Jumlah_Kasus"]
            cond_data = cond_data.sort_values("Jumlah_Kasus", ascending=False)
            
            total_cond = cond_data["Jumlah_Kasus"].sum()
            cond_data["Persen"] = (cond_data["Jumlah_Kasus"] / total_cond * 100).round(1) if total_cond > 0 else 0
            cond_data["Formatted_Cases"] = cond_data["Jumlah_Kasus"].apply(format_number)
            
            step = (100 - 30) / max(1, len(cond_data) - 1)
            cond_data["Esthetic_Val"] = [100 - i * step for i in range(len(cond_data))]
            
            fig_funnel = go.Figure(go.Funnel(
                y=cond_data["Kondisi Akhir"],
                x=cond_data["Esthetic_Val"],
                textinfo="none",
                marker=dict(
                    color=["#60a5fa", "#86efac", "#34d399", "#fbbf24", "#f87171", "#c084fc"][:len(cond_data)],
                    line=dict(color="#ffffff", width=2)
                ),
                customdata=np.stack([
                    cond_data["Kondisi Akhir"],
                    cond_data["Formatted_Cases"],
                    cond_data["Persen"]
                ], axis=-1),
                hovertemplate="<b>%{customdata[0]}</b><br>Jumlah Kasus: <b>%{customdata[1]} kasus</b><br>Persentase: <b>%{customdata[2]}%</b><extra></extra>"
            ))
            
            annotations = []
            for i, row in cond_data.reset_index(drop=True).iterrows():
                annotations.append(
                    dict(
                        x=0.5,
                        y=row["Kondisi Akhir"],
                        xref="paper",
                        yref="y",
                        text=f"<b>{row['Kondisi Akhir']}</b>: {row['Formatted_Cases']} kasus ({row['Persen']}%)",
                        showarrow=False,
                        font=dict(size=9.5, color="#0f172a", family="Inter, sans-serif")
                    )
                )

            fig_funnel.update_layout(
                template=chart_theme,
                height=500,
                margin=dict(l=40, r=40, t=20, b=40),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                xaxis=dict(visible=False, showgrid=False),
                yaxis=dict(title="", tickfont=dict(size=11, color="#0f172a")),
                annotations=annotations
            )
            st.plotly_chart(fig_funnel, use_container_width=True)

# ============================================================
# TAB 4: CASE EXPLORER
# ============================================================

with tab4:
    st.markdown("### Eksplorasi Data & Detail Kasus JKK")
    
    filter_status_desc = []
    if selected_kanwil:
        filter_status_desc.append(f"Kanwil: {', '.join(selected_kanwil)}")
    if selected_branch:
        filter_status_desc.append(f"Cabang: {', '.join(selected_branch)}")
    
    if filter_status_desc:
        st.markdown(f"Menampilkan data berdasarkan filter aktif: *{ ' | '.join(filter_status_desc) }*")
    else:
        st.markdown("Menampilkan data secara nasional.")
    
    potential_cols = [
        npp_col_name, perusahaan_col_name, "Kode TK Final", "Nama TK Final", "tgl_kejadian",
        jam_col, "Nama Kanwil Pelayanan", "Nama Kantor Pelayanan (Cabang)", "Jenis Kelamin",
        "Range Usia", "Sektor BPS Final", "Nama Sumber Cedera Final", "Nama Bagian Sakit Final", 
        "Nama Lokasi Kecelakaan Final", "Kondisi Akhir", "nom_manfaat_netto"
    ]
    
    display_cols = []
    seen_cols = set()
    for col in potential_cols:
        if col and col in filtered.columns and col not in seen_cols:
            display_cols.append(col)
            seen_cols.add(col)
    
    df_explorer = filtered[display_cols].copy()
    
    if "tgl_kejadian" in df_explorer.columns:
        df_explorer["tgl_kejadian"] = pd.to_datetime(df_explorer["tgl_kejadian"], errors="coerce").dt.strftime("%Y-%m-%d")
        df_explorer["tgl_kejadian"] = df_explorer["tgl_kejadian"].replace("NaT", "-")

    if "nom_manfaat_netto" in df_explorer.columns:
        df_explorer["nom_manfaat_netto"] = df_explorer["nom_manfaat_netto"].apply(format_currency)

    # Tabel dengan tombol expand/fullscreen aktif secara otomatis di pojok kanan atas oleh Streamlit
    st.dataframe(df_explorer, use_container_width=True, hide_index=True)
    
    csv_data = filtered.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download Data CSV Terfilter",
        data=csv_data,
        file_name="data_jkk_filtered.csv",
        mime="text/csv"
    )