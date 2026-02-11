# 📊 EU Socio-Economic Trends: A Dual-Country Comparison

Este projeto é um dashboard interativo desenvolvido para analisar e comparar indicadores macroeconómicos dos países da União Europeia. Utilizando dados reais extraídos da API do **World Bank**, a aplicação foca-se na transparência de dados e na facilidade de comparação entre diferentes economias europeias.

## 🚀 Funcionalidades Principais

* **Comparação (A vs B):** Sistema de seleção que permite isolar um país de análise e compará-lo diretamente com outro país ou com a **Média da UE27**.
* **Métricas Dinâmicas:** Análise de tendências para:
    * PIB per Capita (€) - *ajustado por taxa de câmbio*.
    * População Total.
    * Taxa de Desemprego (%).
    * Expectativa de Vida (Anos).
* **Análise de Correlação:** Gráfico de dispersão (Scatter Plot) interativo com linha de tendência (OLS) para validar relações entre métricas (ex: PIB vs. Longevidade).
* **Insights Contextuais:** Geração automática de resumos comparativos e variações percentuais.

## 🧠 Desafios Técnicos & Engenharia de Dados

### 1. Normalização Monetária
Um dos pilares deste projeto foi a conversão de valores nominais de USD para EUR. Implementei uma lógica de **Taxa de Câmbio Anualizada** que permite comparar países fora da Zona Euro (como Suécia ou Dinamarca) com países que utilizam o Euro.

### 2. Tratamento do Paradoxo de Simpson
Em análise estatística, os dados agregados podem esconder a realidade individual. Este dashboard resolve esse problema permitindo a **análise de séries temporais localizadas**, onde o utilizador pode verificar se a tendência de um país específico segue ou desafia a tendência do bloco europeu.

### 3. Performance e Cache
A aplicação utiliza `@st.cache_data` para otimizar o carregamento do DataFrame e o processamento das agregações da média da UE, garantindo que a navegação entre filtros seja instantânea.

## 🛠️ Tecnologias Utilizadas

* **Python 3.11+**
* **matplotlib**: Para a Criação de visualizações durante a exploratory data analysis
* **Pandas**: Limpeza, transformação e agregação (GroupBy).
* **Plotly Express**: Visualizações dinâmicas e interativas.
* **Requests**: Para a a extração de dados
* **Statsmodels**: Cálculo de regressão linear para linhas de tendência.
* **Streamlit**: Interface do utilizador e deploy.
* **typing**: Para declarar o tipo de variavel utilizda

## 📦 Como Instalar e Correr

1.  **Clone o repositório:**
    ```bash
    git clone https://github.com/PPinto24/Projects.git
    cd Projects/project
    ```

2.  **Crie um ambiente virtual e instale as dependências:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # No Windows: .\venv\Scripts\activate
    pip install -r requirements.txt
    ```

3.  **Execute a aplicação:**
    ```bash
    streamlit run src/app.py
    ```

---
**Desenvolvido por Carlos Pedro Pinto** 