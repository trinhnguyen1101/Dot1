import requests
import pandas as pd

indicators = {
    "NY.GDP.MKTP.KD.ZG": "gdp_growth_percent",
    "NY.GNP.MKTP.CD": "gni_usd"
}

all_data = []

for indicator, value_name in indicators.items():

    url = f"https://api.worldbank.org/v2/country/all/indicator/{indicator}"

    params = {
        "format": "json",
        "per_page": 20000
    }

    response = requests.get(url, params=params)
    data = response.json()

    records = data[1]

    for item in records:

        row = {
            "indicator": indicator,
            "country": item["country"]["value"],
            "country_code": item["countryiso3code"],
            "year": item["date"],
            value_name: item["value"]
        }

        all_data.append(row)

df = pd.DataFrame(all_data)

# chỉ lấy quốc gia thật
df = df[df["country_code"].str.len() == 3]

print(df.head())

df.to_csv("data/raw/worldbank_macro_data.csv", index=False)

print("Done!")