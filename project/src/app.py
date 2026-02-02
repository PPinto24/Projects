import streamlit as st
import pandas as pd

# Page configuration
st.set_page_config(page_title="Economic Indicators Dashboard", layout="wide")

@st.cache_data
def load_data():
    df = pd.read_csv('prt_esp_indicators.csv')
    df['year'] = df['year'].astype(int)
    # Ensure data is sorted for correct calculation of annual variations
    df = df.sort_values(['country', 'year'])
    
    # KPI Calculations per country
    for country in df['country'].unique():
        mask = df['country'] == country
        # a & b. Population Variations
        df.loc[mask, 'pop_abs_var'] = df.loc[mask, 'population'].diff()
        df.loc[mask, 'pop_pct_var'] = df.loc[mask, 'population'].pct_change() * 100
        
        # c & d. GDP per Capita Variations
        df.loc[mask, 'gdp_pc_abs_var'] = df.loc[mask, 'gdp_per_capita_usd'].diff()
        df.loc[mask, 'gdp_pc_pct_var'] = df.loc[mask, 'gdp_per_capita_usd'].pct_change() * 100
        
    return df

df = load_data()

# Sidebar Filter
st.sidebar.header("Filters")
selected_country = st.sidebar.selectbox("Select Country", df['country'].unique())

# Filter data
country_df = df[df['country'] == selected_country].copy()
latest_year = country_df['year'].max()
latest_data = country_df[country_df['year'] == latest_year].iloc[0]

st.title(f"Economic Analysis: {selected_country}")

# --- SECTION 1: Annual KPIs (Latest Year) ---
st.subheader(f"Key Performance Indicators ({latest_year})")
col1, col2, col3, col4 = st.columns(4)

col1.metric("Pop. Variation (Abs)", f"{latest_data['pop_abs_var']:,.0f}")
col2.metric("Pop. Variation (%)", f"{latest_data['pop_pct_var']:.2f}%")
col3.metric("GDP pc Var (Abs)", f"${latest_data['gdp_pc_abs_var']:,.2f}")
col4.metric("GDP pc Var (%)", f"{latest_data['gdp_pc_pct_var']:.2f}%")

# --- SECTION 2: Long Term & Custom KPIs ---
st.divider()
col_a, col_b = st.columns(2)

with col_a:
    # e. Average growth last 25 years
    avg_growth_25 = country_df.tail(25)['gdp_growth_pct'].mean()
    st.info(f"**Avg. GDP Growth (Last 25 years):** {avg_growth_25:.2f}%")

with col_b:
    # f. Custom KPI: Unemployment vs Labor Force Ratio
    # This shows what percentage of the total labor force is currently unemployed
    current_unemployment = latest_data['unemployment_pct']
    st.warning(f"**Current Unemployment Rate:** {current_unemployment:.2f}%")

# --- SECTION 3: Visualizations ---
st.subheader("Historical Trends")
tab1, tab2 = st.tabs(["GDP & Population", "Labor Market"])

with tab1:
    st.line_chart(country_df.set_index('year')[['gdp_growth_pct', 'gdp_pc_pct_var']])

with tab2:
    st.bar_chart(country_df.set_index('year')['unemployment_pct'])

st.write("### Raw Data View")
st.dataframe(country_df)