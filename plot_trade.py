import pandas as pd
import matplotlib.pyplot as plt
import os

df = pd.read_csv(r"c:\Users\phucb\Documents\DaiHoc\HK3_2\2\Data Analytics\Dot1\cleaned_data\VNM_macro_cleaned.csv")
df.set_index('Year', inplace=True)
df.sort_index(inplace=True)

df['Trade_Balance_Billion_USD'] = df['Trade_Balance_USD'] / 1e9

fig, ax1 = plt.subplots(figsize=(12, 6))

# Plot Economic Openness on primary y-axis
color = 'tab:blue'
ax1.set_xlabel('Năm (Year)')
ax1.set_ylabel('Độ mở kinh tế (% GDP)', color=color)
ax1.plot(df.index, df['Economic_Openness_Pct'], color=color, linewidth=2, label='Độ mở kinh tế')
ax1.tick_params(axis='y', labelcolor=color)
ax1.grid(True, linestyle='--', alpha=0.6)

# Instantiate a second axes that shares the same x-axis
ax2 = ax1.twinx()  
ax2.set_ylabel('Cán cân thương mại (Tỷ USD)', color='black')  

# Phân loại màu sắc: Xuất siêu (dương) màu xanh, Nhập siêu (âm) màu đỏ
colors = ['tab:green' if val >= 0 else 'tab:red' for val in df['Trade_Balance_Billion_USD']]

ax2.bar(df.index, df['Trade_Balance_Billion_USD'], color=colors, alpha=0.6, label='Cán cân thương mại')
ax2.tick_params(axis='y', labelcolor='black')

# Add a horizontal line for trade balance = 0
ax2.axhline(0, color='black', linewidth=1, linestyle='--')

fig.suptitle('Độ mở kinh tế và Cán cân thương mại của Việt Nam qua các năm', fontsize=14)

# Layout adjustments
fig.tight_layout()  

# Save the figure
os.makedirs('fig', exist_ok=True)
plt.savefig('fig/openness_vs_trade_balance.png')
print("Chart generated successfully.")
