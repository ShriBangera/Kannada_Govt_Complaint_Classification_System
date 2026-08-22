import pandas as pd
data = pd.read_csv("data.csv", encoding='utf-8')

# 🔥 Remove duplicate rows
data = data.drop_duplicates()

# 🔥 Remove wrong rows (like 'text,category' inside data)
data = data[data['text'] != 'text']