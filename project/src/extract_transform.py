"""
Script para extrair os indicadores do World Bank e Guardar os ficheiros em CSV


API Exemplo:
- https://api.worldbank.org/v2/country/PRT/indicator/SP.POP.TOTL?format=json

Indicadores Utilizados:
- População Total            | SP.POP.TOTL
- PIB per capita (USD)       | NY.GDP.PCAP.CD
- Taxa de Desemprego         | SL.UEM.TOTL.ZS
- Força de trabalho (%)      | SL.TLF.TOTL.IN
- Taxa de Cambio de Local Currency para USD | PA.NUS.FCRF

Países:
- Todos os Paises da UE
"""

import requests
import pandas as pd
import numpy as np
from typing import Dict, Any
# Configurações Base

## API Base
url_base = 'https://api.worldbank.org/v2/country/'

## Lista dos 27 Países da União Europeia
eu_27 = [
    'AUT', 'BEL', 'BGR', 'HRV', 'CYP', 'CZE', 'DNK', 'EST', 'FIN', 'FRA', 
    'DEU', 'GRC', 'HUN', 'IRL', 'ITA', 'LVA', 'LTU', 'LUX', 'MLT', 'NLD', 
    'POL', 'PRT', 'ROU', 'SVK', 'SVN', 'ESP', 'SWE'
]
countries = ";".join(eu_27)
start_year = 1999
end_year = 2023

## Lista de Indicadores selecionados
indicators = {
    'SP.POP.TOTL': 'populacao',
    'NY.GDP.PCAP.CD': 'pib_per_capita_usd',
    'SL.UEM.TOTL.ZS': 'desemprego_pct',
    'SP.DYN.LE00.IN': 'esperanca_de_vida',
    'SL.TLF.TOTL.IN': 'classe_trabalhadora',
    'PA.NUS.FCRF': 'cambio_lcu_usd' # Taxa de cambio oficial
}

def api_call(countries: str, indicators:dict, start_year: int, end_year: int)-> pd.DataFrame:
    # Extrai Dados de aPI e retorna um Dataframe
    all_data = []
    for code, name in indicators.items():
        print(f"A extrair: {name}...")
        url = f"{url_base}{countries}/indicator/{code}"

        params = {
            'format': 'json',
            'per_page':5000,
            'date': f'{start_year}:{end_year}',
            'source': 2
        }

        try:
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()

            if len(data) > 1 and data[1]:
                for entry in data[1]:
                    all_data.append({
                        'country_code': entry['countryiso3code'],
                        'country': entry['country']['value'],
                        'year': int(entry['date']),
                        'indicator': name,
                        'value': entry['value']
                    })
        except Exception as e:
            print(f"Erro em {name}: {e}")
            
    return pd.DataFrame(all_data)

def transform_data(df_raw: pd.DataFrame) -> pd.DataFrame:
    # Pivot Table
    df = df_raw.pivot_table(index=['country_code', 'country', 'year'],
                            columns = 'indicator',
                            values = 'value').reset_index()
    # Ordenar DataFrame
    df = df.sort_values(['country', 'year'])

    # Conversão de Moeda
    ## Uma vez que nem todos os paises possuem Euros, vou utilizar portugal um dos paises que se juntou ao Euro em 1999
    euro_rates = df[df['country_code'] == 'PRT'][['year', 'cambio_lcu_usd']].copy()
    euro_rates.columns = ['year', 'usd_to_eur_master']
    df = df.merge(euro_rates, on='year', how='left')
    # Calcular o PIB em Euros
    df['pib_per_capita_eur'] = df['pib_per_capita_usd'] * df['usd_to_eur_master']

    # KPIs
    df_pivot = df.groupby('country')

    #Variações
    ## absolutas
    df['pop_abs_var'] = df_pivot['populacao'].diff()
    df['pib_pc_eur_abs_var'] = df_pivot['pib_per_capita_eur'].diff()
    df['desemprego_abs_var'] = df_pivot['desemprego_pct'].diff() # Variação em pontos percentuais
    df['esperanca_de_vida_abs_var'] = df_pivot['esperanca_de_vida'].diff()
    ## Percentuais
    df['pop_pc_crescimento'] = df_pivot['populacao'].pct_change() * 100
    df['pib_pc_eur_crescimento'] = df_pivot['pib_per_capita_eur'].pct_change() * 100

    # Numeros Absolutos
    df['desemprego_absoluto'] = round((df['desemprego_pct'] / 100) * df['classe_trabalhadora'],0)

    # Crescimento médio dos ultimos 25 anos
    df['pib_crescimento_med_25y'] = df_pivot['pib_pc_eur_crescimento'].transform(
        lambda x: x.rolling(window=25, min_periods=1).mean()
    )

    return df
    
def main():
    df_raw = api_call(countries, indicators, start_year, end_year)
    if not df_raw.empty:
        df_final = transform_data(df_raw)
        df_final.to_csv('eu_data_world_bank.csv', index=False)
        print("Ficheiro 'eu_data_world_bank.csv' gerado com sucesso!")
        
if __name__ =='__main__':
    main()