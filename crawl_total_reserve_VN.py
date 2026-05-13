import requests
import pandas as pd

url = "https://api.worldbank.org/v2/country/VN/indicator/FI.RES.TOTL.CD?format=json&per_page=100"

response = requests.get(url)

# JSON trả về dạng [metadata, data]
data = response.json()[1]

rows = []

for item in data:
    rows.append({
        "year": item["date"],
        "value_usd": item["value"]
    })

df = pd.DataFrame(rows)

# bỏ các dòng null
df = df.dropna()

# sort theo năm tăng dần
df = df.sort_values("year")

print(df)

# lưu csv
df.to_csv("cleaned_data/vietnam_forex_reserves.csv", index=False)