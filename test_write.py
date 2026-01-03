import pandas as pd
import os

FILE_PATH = "/home/elric/PurchaseData/PurchaseHistoryDatabase.csv"

print(f"Checking file: {FILE_PATH}")

if os.path.exists(FILE_PATH):
    print("File exists.")
    try:
        df = pd.read_csv(FILE_PATH)
        print(f"Current rows: {len(df)}")
        print(df.head())
    except Exception as e:
        print(f"Error reading: {e}")
else:
    print("File does NOT exist.")

# Try writing
try:
    if os.path.exists(FILE_PATH):
        df = pd.read_csv(FILE_PATH)
    else:
        df = pd.DataFrame(columns=["N", "Date", "Description", "Amount", "Necessity", "Method", "Category", "Tag", "More info"])
    
    new_row = pd.DataFrame([{
        "N": 999,
        "Date": "2025-12-24",
        "Description": "Test Write",
        "Amount": 1.00,
        "Necessity": 1,
        "Method": "Test",
        "Category": "Test",
        "Tag": "",
        "More info": ""
    }])
    
    df = pd.concat([df, new_row], ignore_index=True)
    df.to_csv(FILE_PATH, index=False)
    print("Successfully wrote to file.")
    
    # Verify
    df_new = pd.read_csv(FILE_PATH)
    print(f"New rows: {len(df_new)}")
    print(df_new.tail(1))
    
except Exception as e:
    print(f"Error writing: {e}")
