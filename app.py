import os
import textwrap
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
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
# CUSTOM CSS (TEXT SELECTION ENABLED & STYLING)
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
        font-size: 21px !important;
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
</style>
""",
    unsafe_allow_html=True,
)


# ============================================================
# DATA LOADING & PREPROCESSING (CACHED FOR PERFORMANCE)
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
    range_usia_col_name = get_col(df, ["Range Usia", "range usia", "range_usia"])

    if "tgl_kejadian" in df.columns:
        df["tgl_kejadian"] = pd.to_datetime(df["tgl_kejadian"], errors="coerce")

    if "nom_manfaat_netto" in df.columns:
        df["nom_manfaat_netto"] = pd.to_numeric(
            df["nom_manfaat_netto"], errors="coerce"
        ).fillna(0)

    if "ID Kasus Final" in df.columns:
        df = df[df["ID Kasus Final"].notna()].copy()

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

    available_case_cols = [col for col in case_cols if col in df.columns]
    agg_dict = {col: "first" for col in available_case_cols if col != "ID Kasus Final"}
    if "nom_manfaat_netto" in df.columns:
        agg_dict["nom_manfaat_netto"] = "sum"

    cases_df = df.groupby("ID Kasus Final", as_index=False).agg(agg_dict)

    if "tgl_kejadian" in cases_df.columns:
        cases_df["Tahun"] = cases_df["tgl_kejadian"].dt.year
        cases_df["Bulan"] = cases_df["tgl_kejadian"].dt.month
        cases_df["Nama Bulan"] = cases_df["tgl_kejadian"].dt.strftime("%b")

    if range_usia_col_name and range_usia_col_name in cases_df.columns:
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

    return cases_df, jam_col_name


file_path = find_excel_file()
if file_path is None:
    st.error("File Excel tidak ditemukan. Pastikan file JKK berada di folder 'data'.")
    st.stop()

try:
    with st.spinner("Memuat dan memproses data..."):
        cases, jam_col = load_and_process_data(file_path)
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

kanwil_options = sorted(
    cases["Nama Kanwil Pelayanan"].dropna().astype(str).unique()
) if "Nama Kanwil Pelayanan" in cases.columns else []
selected_kanwil = st.sidebar.multiselect(
    "Kanwil Pelayanan", options=kanwil_options, default=[]
)

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
    "≥ 51 Tahun"
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

# Optimized filtering using boolean mask indexing for high performance
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
# TAB 1: KANWIL & CABANG
# ============================================================

with tab1:
    st.markdown("### Analisis Kasus & Nominal Manfaat per Kanwil Pelayanan")

    if "Nama Kanwil Pelayanan" in filtered.columns:
        kanwil_summary = (
            filtered.groupby("Nama Kanwil Pelayanan", observed=False)
            .agg(
                Jumlah_Kasus=("ID Kasus Final", "nunique"),
                Nominal=("nom_manfaat_netto", "sum"),
            )
            .reset_index()
            .sort_values("Jumlah_Kasus", ascending=False)
        )

        kanwils = kanwil_summary["Nama Kanwil Pelayanan"].tolist()
        cases_list = kanwil_summary["Jumlah_Kasus"].tolist()
        nominal_list = kanwil_summary["Nominal"].tolist()

        max_c = max(cases_list) if cases_list and max(cases_list) > 0 else 1
        max_n = max(nominal_list) if nominal_list and max(nominal_list) > 0 else 1

        cases_scaled = [- (c / max_c) * 100 for c in cases_list]
        nominal_scaled = [(n / max_n) * 100 for n in nominal_list]

        color_left = '#0284c7'
        color_right = '#059669'

        fig_bi = go.Figure()

        fig_bi.add_trace(go.Bar(
            y=kanwils,
            x=cases_scaled,
            orientation='h',
            name='Jumlah Kasus JKK',
            marker=dict(color=color_left),
            text=[f"{format_number(c)} kasus" for c in cases_list],
            textposition='outside',
            textfont=dict(size=11, color='#0f172a', family='Inter, sans-serif'),
            customdata=cases_list,
            hovertemplate="<b>%{y}</b><br>Jumlah Kasus: <b>%{customdata:,} kasus</b><extra></extra>"
        ))

        fig_bi.add_trace(go.Bar(
            y=kanwils,
            x=nominal_scaled,
            orientation='h',
            name='Nominal Manfaat JKK',
            marker=dict(color=color_right),
            text=[format_currency_compact_intl(n) for n in nominal_list],
            textposition='outside',
            textfont=dict(size=11, color='#0f172a', family='Inter, sans-serif'),
            customdata=[format_currency(n) for n in nominal_list],
            hovertemplate="<b>%{y}</b><br>Nominal Manfaat: <b>%{customdata}</b><extra></extra>"
        ))

        fig_bi.update_layout(
            barmode='relative',
            template='plotly_white',
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            height=max(550, len(kanwils) * 45),
            margin=dict(l=160, r=40, t=50, b=90),
            xaxis=dict(
                tickvals=[-100, -75, -50, -25, 0, 25, 50, 75, 100],
                ticktext=['100%', '75%', '50%', '25%', '0', '25%', '50%', '75%', '100%'],
                title=dict(
                    text='<b>◄ Jumlah Kasus</b> &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; | &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; <b>Nominal Manfaat ►</b>',
                    font=dict(size=13, color='#0f172a')
                ),
                gridcolor='#e2e8f0',
                zerolinecolor='#334155',
                zerolinewidth=1.5,
                range=[-140, 140]
            ),
            yaxis=dict(
                title='',
                autorange='reversed' if len(kanwils) > 0 else True,
                tickfont=dict(size=11, color='#0f172a', family='Inter, sans-serif'),
                zerolinecolor='#334155',
                zerolinewidth=1.5
            ),
            legend=dict(orientation='h', yanchor='bottom', y=-0.3, xanchor='center', x=0.5)
        )

        st.plotly_chart(fig_bi, use_container_width=True)

    st.markdown("<hr style='margin: 30px 0; border-color: #e2e8f0;'>", unsafe_allow_html=True)
    st.markdown("### Detail Jumlah Kasus & Nominal di Masing-masing Cabang")

    if "Nama Kanwil Pelayanan" in filtered.columns and "Nama Kantor Pelayanan (Cabang)" in filtered.columns:
        branch_summary = (
            filtered.groupby(["Nama Kanwil Pelayanan", "Nama Kantor Pelayanan (Cabang)"], observed=False)
            .agg(
                Jumlah_Kasus=("ID Kasus Final", "nunique"),
                Nominal_Manfaat=("nom_manfaat_netto", "sum"),
            )
            .reset_index()
        )
        branch_summary["Rata-rata Manfaat/Kasus"] = (
            branch_summary["Nominal_Manfaat"] / branch_summary["Jumlah_Kasus"]
        )
        branch_summary = branch_summary.sort_values("Jumlah_Kasus", ascending=False)

        branch_display = branch_summary.copy()
        branch_display["Jumlah_Kasus"] = branch_display["Jumlah_Kasus"].apply(format_number)
        branch_display["Nominal_Manfaat"] = branch_display["Nominal_Manfaat"].apply(format_currency)
        branch_display["Rata-rata Manfaat/Kasus"] = branch_display["Rata-rata Manfaat/Kasus"].apply(format_currency)

        st.dataframe(branch_display, use_container_width=True, hide_index=True)


# ============================================================
# TAB 2: SEKTOR BPS
# ============================================================

with tab2:
    if "Sektor BPS Final" in filtered.columns:
        st.markdown("### Top 15 Sektor BPS Berdasarkan Jumlah Kasus & Nominal Manfaat")
        bps_data = (
            filtered.groupby("Sektor BPS Final", observed=False)
            .agg(
                Jumlah_Kasus=("ID Kasus Final", "nunique"),
                Total_Nominal=("nom_manfaat_netto", "sum"),
            )
            .reset_index()
            .sort_values("Jumlah_Kasus", ascending=False)
            .head(15)
        )

        wrapped_sector_names = wrap_labels(bps_data["Sektor BPS Final"], width=14)
        compact_labels = [format_currency_compact_intl(n) for n in bps_data["Total_Nominal"]]
        formatted_hover_nominal = [format_currency(val) for val in bps_data["Total_Nominal"]]

        bar_fonts = [
            10.5 if count < 5000 else 9.5 for count in bps_data["Jumlah_Kasus"]
        ]

        fig_dual = go.Figure()

        fig_dual.add_trace(go.Bar(
            x=wrapped_sector_names,
            y=bps_data["Jumlah_Kasus"],
            name="Jumlah Kasus",
            marker=dict(color="#60a5fa", opacity=0.9),
            text=[f"{format_number(c)} kasus" for c in bps_data["Jumlah_Kasus"]],
            textposition="inside",
            insidetextanchor="start",
            textfont=dict(size=bar_fonts, color="#1e3a8a", family="Inter, sans-serif"),
            customdata=bps_data["Sektor BPS Final"],
            hovertemplate="Sektor: <b>%{customdata}</b><br>Jumlah Kasus: <b>%{y:,} kasus</b><extra></extra>",
            yaxis="y"
        ))

        fig_dual.add_trace(go.Scatter(
            x=wrapped_sector_names,
            y=bps_data["Total_Nominal"],
            name="Total Nominal Manfaat",
            mode="lines+markers+text",
            line=dict(color="#1d4ed8", width=3.5),
            marker=dict(size=10, color="#1d4ed8", line=dict(color="#ffffff", width=2)),
            text=compact_labels,
            textposition="top center",
            textfont=dict(size=10, color="#1e3a8a", family="Inter, sans-serif"),
            customdata=np.stack([bps_data["Sektor BPS Final"], formatted_hover_nominal], axis=-1),
            hovertemplate="Sektor: <b>%{customdata[0]}</b><br>Total Nominal Manfaat: <b>%{customdata[1]}</b><extra></extra>",
            yaxis="y2"
        ))

        fig_dual.update_layout(
            template=chart_theme,
            height=750,
            margin=dict(l=50, r=50, t=20, b=280),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(
                title="",
                tickangle=0,
                tickfont=dict(size=8.5, color="#0f172a", family="Inter, sans-serif")
            ),
            yaxis=dict(
                title=dict(text="Jumlah Kasus", font=dict(color="#334155")),
                gridcolor="#cbd5e1",
                zeroline=True,
                side="left",
                rangemode="tozero"
            ),
            yaxis2=dict(
                title=dict(text="Total Nominal Manfaat (Rp)", font=dict(color="#1d4ed8")),
                overlaying="y",
                side="right",
                showgrid=False,
                zeroline=False,
                rangemode="tozero"
            ),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )

        st.plotly_chart(fig_dual, use_container_width=True)

        st.markdown("<hr style='margin: 30px 0; border-color: #e2e8f0;'>", unsafe_allow_html=True)
        st.markdown("### Tabel Rincian Seluruh Sektor BPS")

        bps_full = (
            filtered.groupby("Sektor BPS Final", observed=False)
            .agg(
                Jumlah_Kasus=("ID Kasus Final", "nunique"),
                Total_Nominal=("nom_manfaat_netto", "sum"),
            )
            .reset_index()
            .sort_values("Jumlah_Kasus", ascending=False)
        )
        bps_display = bps_full.copy()
        bps_display["Jumlah_Kasus"] = bps_display["Jumlah_Kasus"].apply(format_number)
        bps_display["Total_Nominal"] = bps_display["Total_Nominal"].apply(format_currency)

        st.dataframe(bps_display, use_container_width=True, hide_index=True)


# ============================================================
# TAB 3: PROFIL KECELAKAAN & DISTRIBUSI USIA / GENDER / FUNNEL CHART
# ============================================================

with tab3:
    if "Range Usia" in filtered.columns:
        st.markdown("### Persentase Distribusi Range Usia Tenaga Kerja")
        
        age_agg = (
            filtered.groupby("Range Usia", observed=False)
            .agg(
                Jumlah_Kasus=("ID Kasus Final", "nunique"),
            )
            .reset_index()
        )
        
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
                    age_agg["Range Usia"].astype(str),
                    age_agg["Jumlah_Kasus"].apply(format_number),
                    age_agg["Persentase"].astype(str)
                ], axis=-1),
                hovertemplate="<b>Range Usia:</b> %{customdata[0]}<br><b>Jumlah Kasus:</b> %{customdata[1]} kasus<br><b>Persentase:</b> %{customdata[2]}%<extra></extra>"
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

        st.markdown("<hr style='margin: 30px 0; border-color: #e2e8f0;'>", unsafe_allow_html=True)

    if "Jenis Kelamin" in filtered.columns:
        gender_agg = (
            filtered.groupby("Jenis Kelamin", observed=False)
            .agg(
                Jumlah_Kasus=("ID Kasus Final", "nunique"),
                Total_Nominal=("nom_manfaat_netto", "sum"),
            )
            .reset_index()
        )
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
            hour_data = (
                filtered.groupby(jam_col, observed=False)
                .agg(Jumlah_Kasus=("ID Kasus Final", "nunique"))
                .reset_index()
            )
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
            location_data = (
                filtered.groupby("Nama Lokasi Kecelakaan Final", observed=False)
                .agg(Jumlah_Kasus=("ID Kasus Final", "nunique"))
                .reset_index()
                .sort_values("Jumlah_Kasus", ascending=False)
            )
            
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

    st.markdown("<hr style='margin: 30px 0; border-color: #e2e8f0;'>", unsafe_allow_html=True)
    st.markdown("### Sumber Cedera, Bagian Sakit & Kondisi Akhir Pekerja")

    col1, col2 = st.columns(2)

    with col1:
        if "Nama Sumber Cedera Final" in filtered.columns:
            source_data = (
                filtered.groupby("Nama Sumber Cedera Final", observed=False)
                .agg(Jumlah_Kasus=("ID Kasus Final", "nunique"))
                .reset_index()
                .sort_values("Jumlah_Kasus", ascending=False)
                .head(10)
            )
            source_data = source_data.sort_values("Jumlah_Kasus", ascending=True)

            fig = px.bar(
                source_data,
                x="Jumlah_Kasus",
                y="Nama Sumber Cedera Final",
                orientation="h",
                title="Top 10 Sumber Cedera",
                color_discrete_sequence=["#7c3aed"],
                template=chart_theme,
            )
            fig.update_layout(
                xaxis_title="Jumlah Kasus",
                yaxis_title="",
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)'
            )
            st.plotly_chart(fig, use_container_width=True)

    with col2:
        if "Nama Bagian Sakit Final" in filtered.columns:
            body_data = (
                filtered.groupby("Nama Bagian Sakit Final", observed=False)
                .agg(Jumlah_Kasus=("ID Kasus Final", "nunique"))
                .reset_index()
                .sort_values("Jumlah_Kasus", ascending=False)
                .head(10)
            )
            body_data = body_data.sort_values("Jumlah_Kasus", ascending=True)

            fig = px.bar(
                body_data,
                x="Jumlah_Kasus",
                y="Nama Bagian Sakit Final",
                orientation="h",
                title="Top 10 Bagian Tubuh yang Sakit",
                color_discrete_sequence=["#059669"],
                template=chart_theme,
            )
            fig.update_layout(
                xaxis_title="Jumlah Kasus",
                yaxis_title="",
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)'
            )
            st.plotly_chart(fig, use_container_width=True)

    if "Kondisi Akhir" in filtered.columns:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("### Distribusi Kondisi Akhir Pekerja (Funnel Chart)")
        cond_data = (
            filtered.groupby("Kondisi Akhir", observed=False)
            .agg(Jumlah_Kasus=("ID Kasus Final", "nunique"))
            .reset_index()
            .sort_values("Jumlah_Kasus", ascending=False)
        )
        
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
                    font=dict(size=10.5, color="#0f172a", family="Inter, sans-serif")
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
    st.markdown("Berikut adalah tabel data mentah kasus JKK yang telah difilter sesuai parameter di sidebar.")
    
    display_cols = [col for col in [
        "ID Kasus Final", "Kode TK Final", "Nama TK Final", "tgl_kejadian",
        "Nama Kanwil Pelayanan", "Nama Kantor Pelayanan (Cabang)", "Jenis Kelamin",
        "Range Usia", "Sektor BPS Final", "Nama Lokasi Kecelakaan Final", "Kondisi Akhir", "nom_manfaat_netto"
    ] if col in filtered.columns]
    
    df_explorer = filtered[display_cols].copy()
    if "nom_manfaat_netto" in df_explorer.columns:
        df_explorer["nom_manfaat_netto"] = df_explorer["nom_manfaat_netto"].apply(format_currency)
        
    st.dataframe(df_explorer, use_container_width=True, hide_index=True)
    
    csv_data = filtered.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download Data CSV Terfilter",
        data=csv_data,
        file_name="data_jkk_filtered.csv",
        mime="text/csv"
    )