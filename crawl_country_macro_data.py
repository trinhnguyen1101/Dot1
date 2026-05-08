import requests
import pandas as pd
import time
import os # Thư viện mới thêm để kiểm tra file tồn tại

# 1. Danh sách ID và Tên cột giữ nguyên
indicator_ids = [
    'BX.KLT.DINV.CD.WD', 'BX.TRF.PWKR.DT.GD.ZS', 'FP.CPI.TOTL.ZG', 
    'FR.INR.LEND', 'NE.EXP.GNFS.CD', 'NE.IMP.GNFS.CD', 
    'NY.GDP.MKTP.KD.ZG', 'SL.UEM.TOTL.ZS', 'SP.POP.TOTL', 
    'NY.GNP.MKTP.CD', 'NY.GDP.MKTP.CD', 'SL.TLF.TOTL.IN'
]

column_names = {
    'BX.KLT.DINV.CD.WD': 'FDI_Inflows_USD', 'BX.TRF.PWKR.DT.GD.ZS': 'Remittances_Pct_GDP',
    'FP.CPI.TOTL.ZG': 'Inflation_CPI_Pct', 'FR.INR.LEND': 'Lending_Interest_Rate_Pct',
    'NE.EXP.GNFS.CD': 'Exports_USD', 'NE.IMP.GNFS.CD': 'Imports_USD',
    'NY.GDP.MKTP.KD.ZG': 'GDP_Growth_Pct', 'SL.UEM.TOTL.ZS': 'Unemployment_Pct',
    'SP.POP.TOTL': 'Population', 'NY.GNP.MKTP.CD': 'GNI_USD',
    'NY.GDP.MKTP.CD': 'GDP_Current_USD', 'SL.TLF.TOTL.IN': 'Labor_Force_Total' 
}

# 2. Danh sách tổng hợp (Code sẽ tự nhận diện nước nào đã có)
country_code = [
    'VNM', 'THA', 'MYS', 'IDN', 'PHL', 'SGP', 'CHN', 'IND', 'PAK', 'KOR',
    'MEX', 'BRA', 'IRL', 'DEU', 'ZAF', 'USA', 'JPN' 
    ]

for code in country_code:
    output_file = f'{code}_macro_data.csv'
    
    # KIỂM TRA FILE ĐÃ TỒN TẠI CHƯA
    if os.path.exists(output_file):
        print(f"Bỏ qua {code}: File '{output_file}' đã tồn tại.")
        continue # Chuyển sang quốc gia tiếp theo
        
    print(f"\n=========================================")
    print(f"ĐANG TẢI DỮ LIỆU MỚI CHO QUỐC GIA: {code}")
    print(f"=========================================")
    
    master_df = pd.DataFrame() 

    for ind_id in indicator_ids:
        print(f"  + Đang kéo: {ind_id}...")
        url = f"https://api.worldbank.org/v2/country/{code}/indicator/{ind_id}?format=json&per_page=100"

        try:
            response = requests.get(url)
            data = response.json()
        
            if len(data) > 1 and data[1]:
                df_temp = pd.DataFrame(data[1])
                df_temp = df_temp[['date', 'value']]
                df_temp.columns = ['Year', ind_id]
                
                if master_df.empty:
                    master_df = df_temp
                else:
                    master_df = pd.merge(master_df, df_temp, on='Year', how='outer')
                    
            time.sleep(0.5) 
        
        except Exception as e:
            print(f"Lỗi khi tải {ind_id}: {e}")

    if master_df.empty:
        print(f"Không lấy được dữ liệu cho mã {code}.")
        continue

    # 3. Tiền xử lý & Tính toán
    master_df['Year'] = master_df['Year'].astype(int)
    master_df = master_df.sort_values('Year', ascending=False)
    master_df = master_df.rename(columns=column_names)

    master_df['Trade_Balance_USD'] = master_df['Exports_USD'] - master_df['Imports_USD']

    cols_to_fix = ['GDP_Current_USD', 'Population', 'GNI_USD', 'Exports_USD', 'Imports_USD', 'Labor_Force_Total', 'FDI_Inflows_USD']
    for col in cols_to_fix:
        if col in master_df.columns:
            master_df[col] = pd.to_numeric(master_df[col], errors='coerce')

    if 'GDP_Current_USD' in master_df.columns and 'Population' in master_df.columns:
        master_df['GDP_Per_Capita_USD'] = master_df['GDP_Current_USD'] / master_df['Population']

    if 'GDP_Current_USD' in master_df.columns and 'GNI_USD' in master_df.columns:
        master_df['GDP_GNI_Gap_Pct'] = ((master_df['GDP_Current_USD'] - master_df['GNI_USD']) / master_df['GDP_Current_USD']) * 100

    if 'Exports_USD' in master_df.columns and 'Imports_USD' in master_df.columns and 'GDP_Current_USD' in master_df.columns:
        master_df['Economic_Openness_Pct'] = ((master_df['Exports_USD'] + master_df['Imports_USD']) / master_df['GDP_Current_USD']) * 100

    if 'FDI_Inflows_USD' in master_df.columns and 'GDP_Current_USD' in master_df.columns:
        master_df['FDI_to_GDP_Pct'] = (master_df['FDI_Inflows_USD'] / master_df['GDP_Current_USD']) * 100

    if 'Labor_Force_Total' in master_df.columns and 'Population' in master_df.columns:
        master_df['Labor_Participation_Rate_Pct'] = (master_df['Labor_Force_Total'] / master_df['Population']) * 100

    # 4. Xuất file
    master_df.to_csv(output_file, index=False)
    print(f"Hoàn tất! Đã lưu file: {output_file}")