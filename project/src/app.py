import streamlit as st # type: ignore
import pandas as pd
import plotly.express as px

#  Configuração da Página
st.set_page_config(page_title="World Bank Indicators Dashboard",
                   page_icon="📊",
                   layout="wide")

## Carregar os dados em cache por motivos de performance
@st.cache_data
def load_data():
    df = pd.read_csv('eu_data_world_bank.csv')

    ## Criar Média dos EU 27 para comparação
    eu_average = df.groupby('year').mean(numeric_only=True).reset_index()
    eu_average['country'] = 'União Europeia (Média)'
    eu_average['country_code'] = 'EU27'

    # Juntar ao DF original
    df_final = pd.concat([df, eu_average], ignore_index=True)
    return df_final

df_full = load_data()

# --------------------------------
# Título e introdução
st.title("📊 Análise Socioeconómica: União Europeia")
st.markdown("""
Esta plataforma permite explorar a evolução de indicadores do **World Bank** (Source 2) para os países da UE. 
Utilize os filtros na lateral para personalizar a análise.
""")

# --------------------------------
# Filtros
with st.sidebar:
    st.header("⚙️ Configurações de Filtro")
    # ordenar países
    todos_paises = df_full['country'].unique().tolist()
    benchmark_name = "União Europeia (Média)"
    outros_paises = sorted([c for c in todos_paises if c != benchmark_name])
    paises_lista = [benchmark_name] + outros_paises


    ## Filtro de Países
    control_country = st.selectbox(
        "País em Análise",
        options=paises_lista,
        index=paises_lista.index("Portugal") # Mantém Portugal como default
    )

    target_country = st.selectbox(
        "País de Referência",
        options=paises_lista,
        index=0 # Define automaticamente o primeiro da lista (União Europeia)
    )

    ## Filtro de Anos
    min_year = int(df_full['year'].min())
    max_year = int(df_full['year'].max())
    anos = st.slider(
        "Intervalo Temporal",
        min_value=min_year,
        max_value=max_year,
        value=(min_year, max_year)
    )

    st.divider()
    st.header("📊 Visualização")
    metrics_dict = {
        "PIB per Capita (€)": "pib_per_capita_eur",
        "População Total": "populacao",
        "Taxa de Desemprego (%)": "desemprego_absoluto",
        "Expectativa de Vida (Anos)": "esperanca_de_vida",
        "Variação % PIB": "pib_pc_eur_crescimento"
    }
    selected_metric_label = st.selectbox("Métrica para o Gráfico", options=list(metrics_dict.keys()))
    selected_metric_column = metrics_dict[selected_metric_label]


# ----------------------------------
# Lógica dos Filtros
df_filtered = df_full[
    (df_full['country'].isin([control_country, target_country])) &
    (df_full['year'] >= anos[0]) &
    (df_full['year'] <= anos[1])
]


# 6. FUNÇÃO AUXILIAR PARA KPIs
def get_metrics(country, year):
    row = df_filtered[(df_filtered['country'] == country) & (df_filtered['year'] == year)]
    return row.iloc[0] if not row.empty else None

# Obter dados do último ano selecionado
data_c = get_metrics(control_country, anos[1])
data_t = get_metrics(target_country, anos[1])

# 7. EXIBIÇÃO DE KPI CARDS
if data_c is not None and data_t is not None:
    st.subheader(f"📍 Resumo Comparativo: {anos[1]}")

    # Cálculo de Insight Automático
    diff_pib = ((data_c['pib_per_capita_eur'] / data_t['pib_per_capita_eur']) - 1) * 100
    status = "acima" if diff_pib > 0 else "abaixo"
    st.info(f"**Insight:** Em {anos[1]}, o PIB per Capita de **{control_country}** estava **{abs(diff_pib):.1f}% {status}** da referência (**{target_country}**).")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("#### 💶 PIB per Capita")
        # KPI Controle
        val_c = data_c['pib_per_capita_eur']
        var_c = data_c['pib_pc_eur_crescimento']
        st.metric(label=control_country, value=f"{val_c:,.0f} €", delta=f"{var_c:.2f}% (Anual)")
        
        # Comparação com Target
        val_t = data_t['pib_per_capita_eur']
        diff_pct = ((val_c / val_t) - 1) * 100
        st.metric(label=f"vs {target_country}", value=f"{val_t:,.0f} €", 
                  delta=f"{diff_pct:.1f}% vs Target", delta_color="off")

    with col2:
        st.markdown("#### 👥 População")
        pop_c = data_c['populacao']
        pop_var = data_c['pop_abs_var']
        st.metric(label=control_country, value=f"{pop_c/1e6:.2f} M", delta=f"{pop_var:,.0f} hab.")
        
        pop_t = data_t['populacao']
        st.metric(label=f"vs {target_country}", value=f"{pop_t/1e6:.2f} M", delta_color="off")

    with col3:
        st.markdown("#### 📈 Crescimento Médio (25a)")
        avg_c = data_c['pib_crescimento_med_25y']
        st.metric(label=f"Média {control_country}", value=f"{avg_c:.2f} %")
        
        avg_t = data_t['pib_crescimento_med_25y']
        diff_avg = avg_c - avg_t
        st.metric(label=f"Média {target_country}", value=f"{avg_t:.2f} %", 
                  delta=f"{diff_avg:.2f} pp", delta_color="normal")

st.markdown("---")

# Line Chart
st.subheader(f"📈 Tendência Histórica: {selected_metric_label}")
st.caption(f"Trajetória de **{control_country}** vs **{target_country}** entre {anos[0]} e {anos[1]}.")

fig = px.line(
        df_filtered, 
        x='year', 
        y=selected_metric_column, 
        color='country',
        markers=True, 
        template="plotly_white",
        color_discrete_map={control_country: "#1f77b4", target_country: "#ff7f0e"}
    )
    
fig.update_layout(
        hovermode="x unified", 
        legend=dict(orientation="h", y=1.1, x=1, xanchor="right")
    )
    
st.plotly_chart(fig, use_container_width=True)

# 7. ANÁLISE DE CORRELAÇÃO (SCATTER PLOT)
st.markdown("---")
st.subheader("🎯 Análise de Correlação Dinâmica")
st.caption("Compare como duas métricas se relacionam entre si ao longo do tempo para os países selecionados.")

# Colunas para escolher os eixos do Scatter Plot
col_x, col_y = st.columns(2)

with col_x:
    x_label = st.selectbox("Eixo X (Independente)", options=list(metrics_dict.keys()), index=0)
    x_col = metrics_dict[x_label]

with col_y:
    y_label = st.selectbox("Eixo Y (Dependente)", options=list(metrics_dict.keys()), index=3) # Default: Expectativa de Vida
    y_col = metrics_dict[y_label]

# Criação do Gráfico de Dispersão
fig_scatter = px.scatter(
    df_filtered,
    x=x_col,
    y=y_col,
    color='country',
    size='populacao', # O tamanho da bolha representa a população
    hover_name='year',
    text='year',
    trendline="ols", # Adiciona a linha de tendência estatística
    labels={x_col: x_label, y_col: y_label, 'country': 'País'},
    template="plotly_white",
    color_discrete_map={control_country: "#1f77b4", target_country: "#ff7f0e"}
)

# Ajuste estético para não poluir com muitos textos de anos
fig_scatter.update_traces(textposition='top center')

st.plotly_chart(fig_scatter, use_container_width=True)

# Nota interpretativa
st.info(f"**Como ler este gráfico:** Se as bolhas seguem uma linha ascendente, existe uma correlação positiva entre {x_label} e {y_label}. O tamanho das bolhas indica a dimensão populacional em cada ponto temporal.")