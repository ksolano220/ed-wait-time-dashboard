import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(
    page_title="ED Wait Times Dashboard",
    page_icon="🏥",
    layout="wide",
)

STATE_NAMES = {
    "AL": "Alabama", "AK": "Alaska", "AZ": "Arizona", "AR": "Arkansas",
    "CA": "California", "CO": "Colorado", "CT": "Connecticut", "DE": "Delaware",
    "DC": "District of Columbia", "FL": "Florida", "GA": "Georgia", "HI": "Hawaii",
    "ID": "Idaho", "IL": "Illinois", "IN": "Indiana", "IA": "Iowa", "KS": "Kansas",
    "KY": "Kentucky", "LA": "Louisiana", "ME": "Maine", "MD": "Maryland",
    "MA": "Massachusetts", "MI": "Michigan", "MN": "Minnesota", "MS": "Mississippi",
    "MO": "Missouri", "MT": "Montana", "NE": "Nebraska", "NV": "Nevada",
    "NH": "New Hampshire", "NJ": "New Jersey", "NM": "New Mexico", "NY": "New York",
    "NC": "North Carolina", "ND": "North Dakota", "OH": "Ohio", "OK": "Oklahoma",
    "OR": "Oregon", "PA": "Pennsylvania", "RI": "Rhode Island", "SC": "South Carolina",
    "SD": "South Dakota", "TN": "Tennessee", "TX": "Texas", "UT": "Utah",
    "VT": "Vermont", "VA": "Virginia", "WA": "Washington", "WV": "West Virginia",
    "WI": "Wisconsin", "WY": "Wyoming", "PR": "Puerto Rico", "GU": "Guam",
    "VI": "Virgin Islands",
}


@st.cache_data
def load_data():
    df = pd.read_csv("data/ed_hospitals.csv", dtype={"facility_id": str, "zip_code": str})
    df["state_name"] = df["state"].map(STATE_NAMES).fillna(df["state"])
    return df


df = load_data()

# --- Header ---
st.title("Emergency Department Wait Times")
st.markdown(
    "Analyzing median ED wait times across **{:,}** US hospitals "
    "using [CMS Timely and Effective Care](https://data.cms.gov/provider-data/dataset/yv7e-xc69) data.".format(len(df))
)

# --- Sidebar filters ---
st.sidebar.header("Filters")

states = sorted(df["state"].dropna().unique())
selected_states = st.sidebar.multiselect(
    "States",
    options=states,
    default=[],
    format_func=lambda x: f"{x} — {STATE_NAMES.get(x, x)}",
    placeholder="All states",
)

volume_options = ["low", "medium", "high", "very high"]
selected_volumes = st.sidebar.multiselect(
    "ED Volume",
    options=volume_options,
    default=[],
    placeholder="All volumes",
)

wait_range = st.sidebar.slider(
    "Median Wait Time (min)",
    min_value=int(df["median_ed_time_min"].min()),
    max_value=int(df["median_ed_time_min"].max()),
    value=(int(df["median_ed_time_min"].min()), int(df["median_ed_time_min"].max())),
)

# Apply filters
filtered = df.copy()
if selected_states:
    filtered = filtered[filtered["state"].isin(selected_states)]
if selected_volumes:
    filtered = filtered[filtered["ed_volume"].isin(selected_volumes)]
filtered = filtered[
    (filtered["median_ed_time_min"] >= wait_range[0])
    & (filtered["median_ed_time_min"] <= wait_range[1])
]

# --- KPI row ---
col1, col2, col3, col4 = st.columns(4)
col1.metric("Hospitals", f"{len(filtered):,}")
col2.metric("Median Wait", f"{filtered['median_ed_time_min'].median():.0f} min")
col3.metric("Longest Wait", f"{filtered['median_ed_time_min'].max():.0f} min")
col4.metric(
    "Avg Left Before Seen",
    f"{filtered['left_before_seen_pct'].mean():.1f}%"
    if filtered["left_before_seen_pct"].notna().any()
    else "N/A",
)

st.divider()

# --- Row 1: Map + Distribution ---
map_col, dist_col = st.columns([3, 2])

with map_col:
    st.subheader("Median ED Wait Time by State")
    state_avg = (
        filtered.groupby("state")
        .agg(
            median_wait=("median_ed_time_min", "median"),
            num_hospitals=("facility_id", "count"),
        )
        .reset_index()
    )
    state_avg["state_name"] = state_avg["state"].map(STATE_NAMES).fillna(state_avg["state"])

    fig_map = px.choropleth(
        state_avg,
        locations="state",
        locationmode="USA-states",
        color="median_wait",
        color_continuous_scale="RdYlGn_r",
        scope="usa",
        hover_name="state_name",
        hover_data={"state": False, "median_wait": ":.0f", "num_hospitals": True},
        labels={"median_wait": "Median Wait (min)", "num_hospitals": "Hospitals"},
    )
    fig_map.update_layout(
        margin=dict(l=0, r=0, t=10, b=0),
        geo=dict(bgcolor="rgba(0,0,0,0)"),
        coloraxis_colorbar=dict(title="Minutes"),
        height=400,
    )
    st.plotly_chart(fig_map, use_container_width=True)

with dist_col:
    st.subheader("Wait Time Distribution")
    fig_hist = px.histogram(
        filtered,
        x="median_ed_time_min",
        nbins=40,
        color_discrete_sequence=["#4C78A8"],
        labels={"median_ed_time_min": "Median ED Wait Time (min)"},
    )
    fig_hist.update_layout(
        showlegend=False,
        yaxis_title="Number of Hospitals",
        height=400,
        margin=dict(l=0, r=0, t=10, b=0),
    )
    st.plotly_chart(fig_hist, use_container_width=True)

# --- Row 2: Volume comparison + Left before seen ---
vol_col, lbs_col = st.columns(2)

with vol_col:
    st.subheader("Wait Time by ED Volume")
    volume_order = ["low", "medium", "high", "very high"]
    vol_data = filtered[filtered["ed_volume"].isin(volume_order)]
    fig_box = px.box(
        vol_data,
        x="ed_volume",
        y="median_ed_time_min",
        category_orders={"ed_volume": volume_order},
        color="ed_volume",
        color_discrete_sequence=["#72B7B2", "#4C78A8", "#F58518", "#E45756"],
        labels={"ed_volume": "ED Volume", "median_ed_time_min": "Median Wait (min)"},
    )
    fig_box.update_layout(showlegend=False, height=400, margin=dict(t=10))
    st.plotly_chart(fig_box, use_container_width=True)

with lbs_col:
    st.subheader("Wait Time vs Left Before Seen Rate")
    scatter_data = filtered.dropna(subset=["left_before_seen_pct", "median_ed_time_min"])
    fig_scatter = px.scatter(
        scatter_data,
        x="median_ed_time_min",
        y="left_before_seen_pct",
        color="ed_volume",
        category_orders={"ed_volume": volume_order},
        color_discrete_sequence=["#72B7B2", "#4C78A8", "#F58518", "#E45756"],
        opacity=0.5,
        labels={
            "median_ed_time_min": "Median Wait (min)",
            "left_before_seen_pct": "Left Before Seen (%)",
            "ed_volume": "Volume",
        },
        hover_data=["facility_name", "state"],
    )
    fig_scatter.update_layout(height=400, margin=dict(t=10))
    st.plotly_chart(fig_scatter, use_container_width=True)

# --- Row 3: State ranking bar chart ---
st.subheader("State Ranking — Median ED Wait Time")
state_rank = (
    filtered.groupby("state")
    .agg(median_wait=("median_ed_time_min", "median"))
    .reset_index()
    .sort_values("median_wait", ascending=True)
)
state_rank["state_name"] = state_rank["state"].map(STATE_NAMES).fillna(state_rank["state"])

fig_bar = px.bar(
    state_rank,
    x="median_wait",
    y="state_name",
    orientation="h",
    labels={"median_wait": "Median Wait (min)", "state_name": ""},
    color="median_wait",
    color_continuous_scale="RdYlGn_r",
)
fig_bar.update_layout(
    height=max(400, len(state_rank) * 22),
    margin=dict(l=0, t=10),
    showlegend=False,
    coloraxis_showscale=False,
    yaxis=dict(dtick=1),
)
st.plotly_chart(fig_bar, use_container_width=True)

# --- Table: worst and best ---
st.subheader("Hospital Detail")
tab_worst, tab_best = st.tabs(["Longest Waits", "Shortest Waits"])

display_cols = ["facility_name", "city", "state", "median_ed_time_min", "left_before_seen_pct", "ed_volume", "sample_size"]
col_config = {
    "facility_name": st.column_config.TextColumn("Hospital"),
    "city": st.column_config.TextColumn("City"),
    "state": st.column_config.TextColumn("State"),
    "median_ed_time_min": st.column_config.NumberColumn("Median Wait (min)", format="%d"),
    "left_before_seen_pct": st.column_config.NumberColumn("Left Before Seen (%)", format="%.1f"),
    "ed_volume": st.column_config.TextColumn("Volume"),
    "sample_size": st.column_config.NumberColumn("Sample Size", format="%d"),
}

with tab_worst:
    worst = filtered.nlargest(25, "median_ed_time_min")[display_cols]
    st.dataframe(worst, column_config=col_config, hide_index=True, use_container_width=True)

with tab_best:
    best = filtered.nsmallest(25, "median_ed_time_min")[display_cols]
    st.dataframe(best, column_config=col_config, hide_index=True, use_container_width=True)

# --- Footer ---
st.divider()
st.caption(
    "Data: CMS Timely and Effective Care — Hospital (2024–2025 reporting period). "
    "Median ED wait time is measured in minutes from arrival to departure for discharged patients (OP-18b)."
)
