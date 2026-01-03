import pandas as pd
import os
from datetime import datetime

LOCAL_FILE = "/home/elric/PurchaseData/PurchaseHistoryDatabase.csv"
COLUMNS = ["N", "Date", "Description", "Amount", "Necessity", "Method", "Category", "Tag", "More info"]

if os.path.exists(LOCAL_FILE):
    raw_df = pd.read_csv(LOCAL_FILE)
    print(f"RAW_ROWS: {len(raw_df)}")
    
    # Date parsing check
    parsed_dates = pd.to_datetime(raw_df['Date'], errors='coerce')
    valid_dates = parsed_dates.notna().sum()
    print(f"VALID_DATES: {valid_dates}")
    
    if valid_dates < len(raw_df):
        print("EXAMPLES OF FAILED DATES:")
        print(raw_df[parsed_dates.isna()]['Date'].head())
    
    # Content check
    print("LAST 5 ROWS:")
    print(raw_df.tail())
else:
    print("FILE NOT FOUND")
