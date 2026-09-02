import pandas as pd

input_file = "data/Online Retail.xlsx"
output_file = "data/online_retail.csv"

df = pd.read_excel(input_file)

print("Rows:", len(df))
print("Columns:", list(df.columns))

df.to_csv(output_file, index=False)

print(f"CSV created: {output_file}")