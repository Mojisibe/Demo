#Import Libraries
import pandas as pd
import numpy as np

#Import data
file = "2023-11-14-survey-data-a-szervezeti-kommunikacio-jelentosege-a-munkaero-megtartasaban(1).xlsx"
data = pd.read_excel(file, sheet_name = "Data")
data.head()
data.info()

# Rename columns to C999 format
new_columns = {old_col: f'C{i:03d}' for i, old_col in enumerate(data.columns)}
data = data.rename(columns=new_columns)
data.head()

# These are ordered to match the English questions list below.
PASTEX_COLUMN_NAMES = [
    "C034", # (a) regular meetings requiring physical presence or conducted online
    "C035", # (b) professional briefings, discussions, and exchanges of opinion
    "C036", # (c) opportunities to share new ideas and suggestions with supervisors and colleagues
    "C037", # (d) the ability to freely express negative feedback
    "C038", # (e) receiving positive feedback for good performance
    "C039", # (f) informal conversations
    "C040", # (g) honest and respectful communication between supervisors and subordinates, as well as among colleagues
]

# English descriptions of the PastEx questions, ordered to match the CXXX column IDs.
QUESTIONS_ENGLISH_TRANSLATIONS = [
    "(a) regular meetings requiring physical presence or conducted online",
    "(b) professional briefings, discussions, and exchanges of opinion",
    "(c) opportunities to share new ideas and suggestions with supervisors and colleagues",
    "(d) the ability to freely express negative feedback",
    "(e) receiving positive feedback for good performance",
    "(f) informal conversations",
    "(g) honest and respectful communication between supervisors and subordinates, as well as among colleagues",
]

#Find the unique values of each PastEx Varible observed
print("--- Unique Values for PastEx Variables ---")
for col_id in PASTEX_COLUMN_NAMES:
    if col_id in data.columns:
        unique_values = data[col_id].unique()
        print(f"\nColumn: {col_id}")
        print(f"Unique values: {unique_values.tolist()}")
    else:
        print(f"\nWarning: PastEx Column ID '{col_id}' not found in the DataFrame after renaming.")

# Prepare a list to store the calculated medians
medians = []

# Calculate medians for each PastEx column after applying Likert mapping
for col_id in PASTEX_COLUMN_NAMES:
    if col_id in data.columns:
        # Apply the Likert mapping and drop any NaN values that result from unmapped text
        numeric_data = data[col_id].map(LIKERT_MAPPING).dropna()
        if not numeric_data.empty:
            medians.append(numeric_data.median())
        else:
            medians.append(np.nan) # Append NaN if no valid numeric data
    else:
        print(f"Warning: Column ID '{col_id}' not found in the DataFrame after renaming. Skipping.")
        medians.append(np.nan) # Append NaN if column is missing

# Output Markdown table
print('| Question | Median |')
print('|----------|--------|')
for q, m in zip(QUESTIONS_ENGLISH_TRANSLATIONS, medians):
    # Format median to 2 decimal places if it's a number, otherwise print 'N/A'
    formatted_median = f"{m:.2f}" if pd.notna(m) else "N/A"
    print(f'| {q} | {formatted_median} |')