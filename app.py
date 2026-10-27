
import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

# ==========================================
# PAGE CONFIGURATION
# ==========================================

st.set_page_config(
    page_title="Malaysia Data Visualisation",
    page_icon="📊",
    layout="wide"
)

# ==========================================
# LOAD CLEANED DATASETS
# ==========================================

BASE_DIR = Path(__file__).parent

@st.cache_data
def load_data():
    income = pd.read_csv(BASE_DIR / "household_income_cleaned.csv")
    prisoners = pd.read_csv(BASE_DIR / "prisoners_cleaned.csv")
    marriages = pd.read_csv(BASE_DIR / "marriages_cleaned.csv")

    income["date"] = pd.to_datetime(income["date"])
    prisoners["date"] = pd.to_datetime(prisoners["date"])
    marriages["date"] = pd.to_datetime(marriages["date"])

    return income, prisoners, marriages

income, prisoners, marriages = load_data()

# ==========================================
# PREPARE DATA
# ==========================================

income_median = income[
    income["variable"] == "median"
].copy()

income_trend = (
    income_median
    .groupby(["date", "percentile"], as_index=False)["income"]
    .mean()
)

income_2024 = income_median[
    income_median["date"].dt.year == 2024
].copy()

income_heatmap_data = income_2024[
    income_2024["percentile"].isin([10, 25, 50, 75, 90])
].pivot(
    index="state",
    columns="percentile",
    values="income"
)

income_state_2024 = income_2024[
    income_2024["percentile"] == 50
].copy()

prisoners_both = prisoners[
    prisoners["sex"] == "both"
].copy()

prisoners_national = prisoners_both[
    prisoners_both["state"] == "Malaysia"
].sort_values("date")

prisoners_state_2024 = prisoners_both[
    (prisoners_both["date"].dt.year == 2024)
    & (prisoners_both["state"] != "Malaysia")
].copy()

prisoners_sex_national = prisoners[
    (prisoners["state"] == "Malaysia")
    & (prisoners["sex"].isin(["male", "female"]))
].copy()

marriages_age_only = marriages[
    marriages["age"] != "all"
].copy()

marriages_count_2024 = marriages_age_only[
    marriages_age_only["date"].dt.year == 2024
].copy()

marriages_rate_2024 = marriages_count_2024.copy()

marriages_annual = marriages[
    (marriages["age"] == "all")
    & (marriages["sex"] == "female")
].sort_values("date")

age_order = [
    "< 20", "20-24", "25-29", "30-34", "35-39",
    "40-44", "45-49", "50-54", "55-59", "60-64", "65+"
]

# ==========================================
# SIDEBAR NAVIGATION
# ==========================================

st.sidebar.title("📊 Navigation")

page = st.sidebar.radio(
    "Select a page:",
    [
        "Overview",
        "1. Household Income",
        "2. Prisoners",
        "3. Marriages"
    ]
)

st.sidebar.divider()
st.sidebar.caption("JIE42403 – Scientific Visualisation")
st.sidebar.caption("Data source: OpenDOSM / data.gov.my")

# ==========================================
# OVERVIEW PAGE
# ==========================================

if page == "Overview":

    st.title("Malaysia Data Visualisation")
    st.subheader("JIE42403 – Scientific Visualisation")

    st.write(
        "This interactive application explores three Malaysian "
        "datasets: household income, prisoners, and marriages."
    )

    st.info(
        "Use the navigation menu on the left to explore the three "
        "datasets, their visualisations, and key findings."
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Datasets", "3")

    with col2:
        st.metric("Visualisations", "9")

    with col3:
        st.metric("Income years", "2019, 2022, 2024")

    st.markdown("### Visualisation objectives")

    st.markdown(
        """
        **1. Household Income**

        Examine changes in household median income across selected
        percentiles and compare income differences between states
        from 2019 to 2024.

        **2. Prisoners**

        Analyse changes in the number of prisoners in Malaysia from
        2017 to 2024 and compare their distribution across states
        and sexes.

        **3. Marriages**

        Identify age groups with the highest marriage counts and
        rates, and examine annual changes in marriage records from
        2017 to 2024.
        """
    )

    st.markdown("### Dataset overview")

    overview_data = pd.DataFrame({
        "Dataset": [
            "Household Income",
            "Prisoners",
            "Marriages"
        ],
        "Records": [
            len(income),
            len(prisoners),
            len(marriages)
        ],
        "Years covered": [
            "2019, 2022, 2024",
            "2017–2024",
            "2017–2024"
        ]
    })

    st.dataframe(overview_data, use_container_width=True, hide_index=True)

# ==========================================
# PAGE 1: HOUSEHOLD INCOME
# ==========================================

elif page == "1. Household Income":

    st.title("Household Income in Malaysia")

    st.write(
        "Objective: To examine changes in household median income "
        "across selected percentiles and compare differences "
        "between Malaysian states."
    )

    avg_median = (
        income_median.groupby(
            income_median["date"].dt.year
        )["income"].mean()
    )

    avg_2019 = avg_median.get(2019, float("nan"))
    avg_2024 = avg_median.get(2024, float("nan"))

    pct_change = (
        ((avg_2024 - avg_2019) / avg_2019) * 100
        if pd.notna(avg_2019) and avg_2019 != 0
        else float("nan")
    )

    highest_state = income_state_2024.loc[
        income_state_2024["income"].idxmax()
    ]

    c1, c2, c3 = st.columns(3)

    c1.metric("Average state median, 2019", f"RM {avg_2019:,.2f}")
    c2.metric("Average state median, 2024", f"RM {avg_2024:,.2f}")
    c3.metric("Change, 2019–2024", f"{pct_change:+.2f}%")

    st.caption(
        "The average state median is the mean of state-level median "
        "income values; it is not the national median income."
    )

    st.divider()

    # Chart 1
    st.subheader("Visualisation 1: Income Trend by Percentile")

    trend_chart_data = income_trend[
        income_trend["percentile"].isin([10, 25, 50, 75, 90])
    ]

    fig1 = px.line(
        trend_chart_data,
        x="date",
        y="income",
        color="percentile",
        markers=True,
        title="Average State Median Income by Percentile",
        labels={
            "date": "Year",
            "income": "Average income (RM)",
            "percentile": "Percentile"
        }
    )

    st.plotly_chart(fig1, use_container_width=True)

    st.write(
        "Interpretation: Compare the income levels across the "
        "selected percentiles and years. Higher percentiles represent "
        "higher positions in the income distribution. The lines show "
        "how the state-level income averages change between the "
        "available survey years."
    )

    # Chart 2
    st.subheader("Visualisation 2: Income Heatmap by State")

    fig2 = px.imshow(
        income_heatmap_data,
        aspect="auto",
        color_continuous_scale="YlGnBu",
        title="Median Income by State and Percentile (2024)",
        labels={
            "x": "Percentile",
            "y": "State",
            "color": "Income (RM)"
        }
    )

    st.plotly_chart(fig2, use_container_width=True)

    st.write(
        "Interpretation: Darker or more intense colours indicate "
        "higher income values according to the colour scale. The "
        "heatmap helps compare income levels across states and "
        "percentile positions."
    )

    # Chart 3
    st.subheader("Visualisation 3: Median Income by State")

    fig3 = px.bar(
        income_state_2024.sort_values("income"),
        x="income",
        y="state",
        orientation="h",
        title="Median Income by State, 50th Percentile (2024)",
        labels={
            "income": "Median income (RM)",
            "state": "State"
        }
    )

    st.plotly_chart(fig3, use_container_width=True)

    lowest_state = income_state_2024.loc[
        income_state_2024["income"].idxmin()
    ]

    st.write(
        f"Interpretation: {highest_state['state']} recorded the "
        f"highest median income at the 50th percentile "
        f"(RM {highest_state['income']:,.0f}), while "
        f"{lowest_state['state']} recorded the lowest "
        f"(RM {lowest_state['income']:,.0f}). This indicates "
        "differences in median household income between states."
    )

# ==========================================
# PAGE 2: PRISONERS
# ==========================================

elif page == "2. Prisoners":

    st.title("Prisoners in Malaysia")

    st.write(
        "Objective: To analyse changes in prisoner numbers over time "
        "and compare the distribution across states and sexes."
    )

    latest_national = prisoners_national.iloc[-1]
    lowest_national = prisoners_national.loc[
        prisoners_national["prisoners"].idxmin()
    ]

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "National total, 2024",
        f"{int(latest_national['prisoners']):,}"
    )

    c2.metric(
        "Lowest annual total",
        f"{int(lowest_national['prisoners']):,}"
    )

    c3.metric(
        "Year of lowest total",
        str(lowest_national["date"].year)
    )

    st.caption(
        "National totals use the 'both' category. State comparisons "
        "exclude the separate Malaysia national record."
    )

    st.divider()

    # Chart 4
    st.subheader("Visualisation 4: National Prisoner Trend")

    fig4 = px.line(
        prisoners_national,
        x="date",
        y="prisoners",
        markers=True,
        title="National Prisoner Trend (2017–2024)",
        labels={
            "date": "Year",
            "prisoners": "Number of prisoners"
        }
    )

    st.plotly_chart(fig4, use_container_width=True)

    st.write(
        "Interpretation: The series shows changes in national prisoner "
        "numbers over time. The total reached its lowest point in "
        f"{int(lowest_national['date'].year)} and later increased. "
        "The chart describes changes in recorded numbers and does not "
        "by itself explain their causes."
    )

    # Chart 5
    st.subheader("Visualisation 5: Prisoners by State")

    fig5 = px.bar(
        prisoners_state_2024.sort_values("prisoners"),
        x="prisoners",
        y="state",
        orientation="h",
        title="Prisoners by State (2024)",
        labels={
            "prisoners": "Number of prisoners",
            "state": "State"
        }
    )

    st.plotly_chart(fig5, use_container_width=True)

    top_state = prisoners_state_2024.loc[
        prisoners_state_2024["prisoners"].idxmax()
    ]

    st.write(
        f"Interpretation: {top_state['state']} recorded the largest "
        f"number of prisoners among the states included in the "
        f"2024 comparison ({int(top_state['prisoners']):,}). "
        "Differences in absolute counts should be interpreted "
        "carefully because state populations may differ."
    )

    # Chart 6
    st.subheader("Visualisation 6: Prisoners by Sex")

    fig6 = px.line(
        prisoners_sex_national.sort_values("date"),
        x="date",
        y="prisoners",
        color="sex",
        markers=True,
        title="National Prisoners by Sex (2017–2024)",
        labels={
            "date": "Year",
            "prisoners": "Number of prisoners",
            "sex": "Sex"
        }
    )

    st.plotly_chart(fig6, use_container_width=True)

    sex_2024 = prisoners_sex_national[
        prisoners_sex_national["date"].dt.year == 2024
    ]

    st.write(
        "Interpretation: Compare the male and female series to examine "
        "differences in recorded prisoner numbers over time. These "
        "figures describe the counts in the dataset, not rates adjusted "
        "for population size."
    )

    st.dataframe(sex_2024[["sex", "prisoners"]], hide_index=True)

# ==========================================
# PAGE 3: MARRIAGES
# ==========================================

elif page == "3. Marriages":

    st.title("Marriage Statistics in Malaysia")

    st.write(
        "Objective: To identify age groups with the highest marriage "
        "counts and rates and examine annual changes in marriage records."
    )

    annual_2024 = marriages_annual[
        marriages_annual["date"].dt.year == 2024
    ]

    annual_value = (
        int(annual_2024.iloc[0]["abs"])
        if not annual_2024.empty
        else 0
    )

    peak_annual = marriages_annual.loc[
        marriages_annual["abs"].idxmax()
    ]

    top_count = marriages_count_2024.loc[
        marriages_count_2024["abs"].idxmax()
    ]

    top_rate = marriages_rate_2024.loc[
        marriages_rate_2024["rate"].idxmax()
    ]

    c1, c2, c3 = st.columns(3)

    c1.metric("Annual count, 2024", f"{annual_value:,}")
    c2.metric(
        "Highest annual count in series",
        f"{int(peak_annual['abs']):,}"
    )
    c3.metric(
        "Highest rate in 2024",
        f"{top_rate['rate']:.1f}"
    )

    st.caption(
        "The annual trend uses the female, all-ages record as one "
        "consistent series. Male and female records are not added "
        "together to calculate a total."
    )

    st.divider()

    # Chart 7
    st.subheader("Visualisation 7: Marriage Count by Age and Sex")

    fig7 = px.bar(
        marriages_count_2024,
        x="age",
        y="abs",
        color="sex",
        barmode="group",
        category_orders={"age": age_order},
        title="Number of Marriages by Age Group and Sex (2024)",
        labels={
            "age": "Age group",
            "abs": "Number of records",
            "sex": "Sex"
        }
    )

    st.plotly_chart(fig7, use_container_width=True)

    st.write(
        f"Interpretation: The largest individual count in the "
        f"2024 age-and-sex records was for {top_count['sex']} "
        f"aged {top_count['age']}, with "
        f"{int(top_count['abs']):,} records. Compare the grouped bars "
        "to identify differences between age groups and sexes."
    )

    # Chart 8
    st.subheader("Visualisation 8: Marriage Rate by Age and Sex")

    fig8 = px.bar(
        marriages_rate_2024,
        x="age",
        y="rate",
        color="sex",
        barmode="group",
        category_orders={"age": age_order},
        title="Marriage Rate by Age Group and Sex (2024)",
        labels={
            "age": "Age group",
            "rate": "Rate (as supplied in dataset)",
            "sex": "Sex"
        }
    )

    st.plotly_chart(fig8, use_container_width=True)

    st.write(
        f"Interpretation: The highest rate in the displayed 2024 "
        f"records was {top_rate['rate']:.1f} for "
        f"{top_rate['sex']} aged {top_rate['age']}. The rate uses "
        "the definition and units supplied by the source dataset; "
        "it should not be interpreted as a percentage unless the "
        "source documentation specifies that."
    )

    # Chart 9
    st.subheader("Visualisation 9: Annual Marriage Trend")

    fig9 = px.line(
        marriages_annual,
        x="date",
        y="abs",
        markers=True,
        title="Annual Marriage Trend (2017–2024)",
        labels={
            "date": "Year",
            "abs": "Number of records (female, all ages)"
        }
    )

    st.plotly_chart(fig9, use_container_width=True)

    st.write(
        "Interpretation: The annual series fluctuates over the "
        "period. It reaches its highest value in "
        f"{int(peak_annual['date'].year)} at "
        f"{int(peak_annual['abs']):,} records, then changes in "
        "subsequent years. The trend shows recorded counts and "
        "does not establish the causes of these changes."
    )

# ==========================================
# FOOTER
# ==========================================

st.divider()
st.caption(
    "JIE42403 – Scientific Visualisation | "
    "Data: OpenDOSM and data.gov.my | "
    "Interpretations are based on the selected datasets."
)
