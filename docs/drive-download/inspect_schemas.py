import os
import pandas as pd
import glob

directory = r"C:\Users\matts\Downloads\drive-download-20251204T065412Z-1-001"
files = glob.glob(os.path.join(directory, "*.xlsx"))

schemas = {}

for f in files:
    try:
        df = pd.read_excel(f, nrows=0) # Read only headers
        columns = tuple(df.columns.tolist())
        if columns not in schemas:
            schemas[columns] = []
        schemas[columns].append(os.path.basename(f))
    except Exception as e:
        print(f"Error reading {os.path.basename(f)}: {e}")

print(f"Found {len(schemas)} unique schemas:")
for i, (cols, file_list) in enumerate(schemas.items()):
    print(f"\nSchema {i+1} ({len(file_list)} files):")
    print(f"Columns: {cols}")
    print(f"Example files: {file_list[:3]}")
