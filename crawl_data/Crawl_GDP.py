import requests
import pandas as pd

url = "https://api.worldbank.org/v2/country/all/indicator/NY.GDP.MKTP.CD"

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
        "gdp_usd": item["value"]
    })

df = pd.DataFrame(rows)

# bỏ null
df = df.dropna(subset=["gdp_usd"])

# chỉ lấy quốc gia thật
df = df[df["country_code"].str.len() == 3]

print(df.head())

df.to_csv("data/raw/gdp_current_usd.csv", index=False)