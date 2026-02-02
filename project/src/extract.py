"""
Script para extrair os indicadores do World Bank e Guardar os ficheiros em CSV


API Exemplo:
- https://api.worldbank.org/v2/country/PRT/indicator/SP.POP.TOTL?format=json

Indicadores Utilizados:
- População Total            | SP.POP.TOTL
- PIB per capita (USD)       | NY.GDP.PCAP.CD
- Taxa de Crescimento do PIB | NY.GDP.MKTP.KD.ZG
- Taxa de Desemprego         | SL.UEM.TOTL.ZS
- Força de trabalho (%)      | SL.TLF.TOTL.IN

Países:
- PRT
- ESP
"""

import requests
import pandas as pd
from typing import Dict, Any

url_base = 'https://api.worldbank.org/v2/country/'
format = 'json'

def api_call(countries: str, indicators:str, start_year: int, end_year: int):
    url = f"{url_base}{countries}/indicator/{indicators}"

    params = {
        'format': format,
        'per_page':2000,
        'date': f'{start_year}:{end_year}',
        'source': 2
    }

    response = requests.get(url, params=params, timeout=30)
    response.raise_for_status()

    data = response.json()

    if len(data) < 2 or data[1] is None:
        return []
    return data[1]
    
def main():
    countries = 'PRT;ESP'
    start_year = 1996
    end_year = 2024

    indicators = (
        'SP.POP.TOTL;'
        'NY.GDP.PCAP.CD;'
        'NY.GDP.MKTP.KD.ZG;'
        'SL.UEM.TOTL.ZS;'
        'SL.TLF.TOTL.IN'
    )

    raw_data = api_call(
        countries = countries,
        indicators = indicators,
        start_year=start_year,
        end_year=end_year
    )

    data_by_country_year: Dict[tuple, Dict[str, Any]] = {}

    for entry in raw_data:
        country = entry['country']['value']
        year = int(entry['date'])
        indicator_id = entry['indicator']['id']
        value = entry['value']

        key = (country, year)

        if key not in data_by_country_year:
            data_by_country_year[key] = {
                'country': country,
                'year': year,
                'population': None,
                'gdp_per_capita_usd': None,
                'gdp_growth_pct': None,
                'unemployment_pct': None,
                'labor_force_total': None
                }


        if indicator_id == 'SP.POP.TOTL':
            data_by_country_year[key]["population"] = value
        elif indicator_id == "NY.GDP.PCAP.CD":
            data_by_country_year[key]["gdp_per_capita_usd"] = value
        elif indicator_id == "NY.GDP.MKTP.KD.ZG":
            data_by_country_year[key]["gdp_growth_pct"] = value
        elif indicator_id == "SL.UEM.TOTL.ZS":
            data_by_country_year[key]["unemployment_pct"] = value
        elif indicator_id == "SL.TLF.TOTL.IN":
            data_by_country_year[key]["labor_force_total"] = value

    # Ordenar por pais e ano
    final_rows = sorted(
        data_by_country_year.values(),
        key = lambda x: (x['country'], x['year'])
    )

    #Criar DataFrame e guardar em CSV
    df = pd.DataFrame(final_rows)
    df.to_csv('prt_esp_indicators.csv', index = False)

    print('Ficheiro criado com sucesso com o nome prt_esp_indicators')

if __name__ =='__main__':
    main()