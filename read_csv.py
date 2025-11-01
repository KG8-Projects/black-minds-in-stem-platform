import pandas as pd

try:
    df = pd.read_csv('Scrapers/scrapers/data/cty_programs_combined.csv')
    print(f"Total rows in file: {len(df)}")
    print(f"Columns available: {list(df.columns)}")
    print("\nFirst 5 rows with 'name' and 'target_grade' columns:")
    print(df[['name', 'target_grade']].head(5))
except FileNotFoundError:
    print("Error: cty_programs_combined.csv file not found in current directory")
except KeyError as e:
    print(f"Error: Column not found - {e}")
    print(f"Available columns: {list(df.columns)}")
except Exception as e:
    print(f"Error reading CSV: {e}")