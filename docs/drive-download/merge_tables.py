import os
import pandas as pd
import glob
import warnings

# Suppress openpyxl warnings about strict mode/extensions
warnings.simplefilter("ignore")

directory = r"C:\Users\matts\Downloads\drive-download-20251204T065412Z-1-001"
output_dir = os.path.join(directory, "Merged_Output")
os.makedirs(output_dir, exist_ok=True)

files = glob.glob(os.path.join(directory, "*.xlsx"))

# Buckets for dataframes
people_dfs = []
timeline_dfs = []
narrative_dfs = []

# Logic to classify and normalize
for f in files:
    filename = os.path.basename(f)
    if filename.startswith("~$") or "Merged_" in filename:
        continue
        
    try:
        df = pd.read_excel(f)
        cols = [str(c).strip() for c in df.columns.tolist()]
        
        # Classification logic based on unique keywords in headers
        col_str = " ".join(cols).lower()
        
        if "relationship to petitioner" in col_str:
            # People Table
            # Standardize columns if necessary, but Schema 5 seems consistent
            people_dfs.append(df)
            print(f"Mapped '{filename}' to PEOPLE table.")
            
        elif "legal strategy tag" in col_str or "narrative fact" in col_str:
            # Timeline Table
            # Normalize 'The Narrative Fact...' columns
            new_cols = {}
            for c in cols:
                if "Narrative Fact" in c:
                    new_cols[c] = "The Narrative Fact"
            if new_cols:
                df = df.rename(columns=new_cols)
            timeline_dfs.append(df)
            print(f"Mapped '{filename}' to TIMELINE table.")
            
        elif "raw reality" in col_str or "imprint" in col_str or "weaponized narrative" in col_str or "event / trauma" in col_str or "context" in col_str or "impact on you" in col_str:
            # Narrative Table
            # This is the most diverse group. We need to map columns to a standard set.
            # Target: Era, Event, Raw Reality, Weaponized, Imprint/Inoculation
            
            rename_map = {}
            for c in cols:
                c_lower = c.lower()
                if "era" in c_lower or "date" in c_lower:
                    rename_map[c] = "Era/Date"
                elif "event" in c_lower and "category" not in c_lower: # Avoid 'Event Category' from timeline
                    rename_map[c] = "Event/Trauma"
                elif "raw reality" in c_lower or "full context" in c_lower:
                    rename_map[c] = "The Raw Reality"
                elif "weaponized" in c_lower:
                    rename_map[c] = "The Weaponized Narrative"
                elif "inoculation" in c_lower or "imprint" in c_lower or "effect on future" in c_lower or "impact on you" in c_lower:
                    rename_map[c] = "The Impact/Inoculation"
            
            df = df.rename(columns=rename_map)
            narrative_dfs.append(df)
            print(f"Mapped '{filename}' to NARRATIVE table.")
            
        else:
            print(f"WARNING: Could not classify '{filename}' with columns: {cols}")

    except Exception as e:
        print(f"Error processing {filename}: {e}")

# Function to merge and save
def merge_and_save(dfs, name):
    if not dfs:
        print(f"\nNo files found for {name}.")
        return
    
    print(f"\nMerging {len(dfs)} files for {name}...")
    full_df = pd.concat(dfs, ignore_index=True)
    
    # Deduplicate
    before = len(full_df)
    full_df = full_df.drop_duplicates()
    after = len(full_df)
    print(f"Dropped {before - after} duplicate rows.")
    
    # Save
    output_path = os.path.join(output_dir, f"{name}.xlsx")
    full_df.to_excel(output_path, index=False)
    print(f"Saved {name} to {output_path}")

merge_and_save(people_dfs, "Merged_People")
merge_and_save(timeline_dfs, "Merged_Timeline")
merge_and_save(narrative_dfs, "Merged_Narrative")
