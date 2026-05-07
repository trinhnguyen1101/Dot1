import requests
import pandas as pd

# URL API
url = "https://api.worldbank.org/v2/country/all/indicator/SP.POP.TOTL"

# Parameters
params = {
    "format": "json",
    "per_page": 20000
}

# Gửi request
response = requests.get(url, params=params)

# Chuyển sang JSON
data = response.json()

# data[0] = metadata
# data[1] = dữ liệu thật
records = data[1]

# Trích xuất dữ liệu cần thiết
rows = []

for item in records:
    rows.append({
        "country": item["country"]["value"],
        "country_id": item["country"]["id"],
        "year": item["date"],
        "population": item["value"]
    })

# Tạo DataFrame
df = pd.DataFrame(rows)

# Xóa dòng null
df = df.dropna(subset=["population"])

# Xem thử
print(df.head())

# Lưu CSV
df.to_csv("worldbank_population.csv", index=False)

print("Đã lưu file worldbank_population.csv")