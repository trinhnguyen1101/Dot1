import requests
import pandas as pd

url = "https://api.worldbank.org/v2/country/all/indicator/NE.IMP.GNFS.CD"

params = {
    "format": "json",
    "per_page": 20000
}

response = requests.get(url, params=params)
data = response.json()

records = data[1]

rows = []

for item in records:
    rows.append({
        "country": item["country"]["value"],
        "country_code": item["countryiso3code"],
        "year": item["date"],
        "imports_gdp_value": item["value"]
    })

df = pd.DataFrame(rows)

# bỏ null
df = df.dropna(subset=["imports_gdp_value"])

print(df.head())

df.to_csv("imports_value_gdp.csv", index=False)