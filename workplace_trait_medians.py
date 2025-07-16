if 1: # Import Libraries
    import pandas as pd
    import numpy as np
if 1: # Import data
    file = "2023-11-14-survey-data-a-szervezeti-kommunikacio-jelentosege-a-munkaero-megtartasaban(1).xlsx"
    data = pd.read_excel(file, sheet_name="Data")
    data.head()
    data.info()
if 1: # Rename columns to C999 format
    new_columns = {old_col: f'C{i:03d}' for i, old_col in enumerate(data.columns)}
    data = data.rename(columns=new_columns)
    data.head()
PASTEX_COLUMN_NAMES = [ # These are ordered to match the English questions list of B04.md
    "C033", # (a) regular meetings requiring physical presence or conducted online
    "C034", # (b) professional briefings, discussions, and exchanges of opinion
    "C035", # (c) opportunities to share new ideas and suggestions with supervisors and colleagues
    "C037", # (d) the ability to freely express negative feedback
    "C039", # (e) receiving positive feedback for good performance
    "C041", # (f) informal conversations
    "C043", # (g) honest and respectful communication between supervisors and subordinates, as well as among colleagues
    ]
QUESTIONS_ENGLISH_TRANSLATIONS = [ # English descriptions of the PastEx questions, ordered to match the questions list of B04.md
    "(a) Regular in-person or online meetings, professional briefings, discussions, and exchanges of views are very important to me. Their absence contributed to my voluntary job change.",
    "(b) In my previous organization, live or online communication was regular (e.g., daily/weekly team meetings, conferences, discussions with direct superiors).",
    "(c) It is very important for me to be able to share my new ideas and suggestions with my superiors and colleagues. The fact that I could not do this contributed to my voluntary job change.",
    "(d) My previous workplace encouraged everyone to share their ideas with a series of measures (e.g., brainstorming sessions, suggestion boxes).",
    "(e) The free expression of negative feedback is a fundamental expectation for me. The fact that I could not express my negative feedback contributed to my voluntary job change.",
    "(f) My previous employer encouraged everyone to freely express their dissatisfaction (e.g., there was a 'complaint' box).",
    "(g) At my previous workplace, the communication style was honest and respectful.",
    ]
if 1: # Data check: Find the unique values of each PastEx Variable observed
    print("--- Unique Values for PastEx Variables ---")
    for col_id in PASTEX_COLUMN_NAMES:
        if col_id in data.columns:
            unique_values = data[col_id].unique()
            print(f"\nColumn: {col_id}")
            print(f"Unique values: {unique_values.tolist()}")
        else:
            print(f"\nWarning: PastEx Column ID '{col_id}' not found in the DataFrame after renaming.")   
if 1: # Add test data column to the data frame and to the lists of questions
    if 1: # Create test data as list
        test_col_name = "Test_Col"
        test_values = [3, 2, np.nan, np.nan, np.nan, np.nan, np.nan]
        # Pad with NaNs (more than needed, truncation will happen later)
        test_values_extended = test_values + [np.nan] * len(data)
    if 1: # Add test column to the data frame and to the lists of questions
        data[test_col_name] = test_values_extended[:len(data)]
        PASTEX_COLUMN_NAMES_WITH_TEST = PASTEX_COLUMN_NAMES + [test_col_name]
        QUESTIONS_WITH_TEST = QUESTIONS_ENGLISH_TRANSLATIONS + ["Test question: Median should be between 'I do not agree' and 'I agree'"]
if 1: # For each survey question and test column convert answers to numbers, calculate medians
    from likert_mapping import LIKERT_MAPPING # Hungarian to code mapping
    medians = [] # Prepare a list to store the calculated medians
    for col_id in PASTEX_COLUMN_NAMES_WITH_TEST:
        if col_id in data.columns:
            if 1: # Code the column: mapping for survey columns, direct numeric for test column
                if col_id == test_col_name:
                    numeric_data = data[col_id].dropna()
                else: # Hungarian to numeric code conversion
                    numeric_data = data[col_id].map(LIKERT_MAPPING).dropna()
            if 1: # Calculate median
                if not numeric_data.empty:
                    medians.append(numeric_data.median())
                else:
                    medians.append(np.nan)  # Append NaN if no valid numeric data
        else:
            print(f"Warning: Column ID '{col_id}' not found in the DataFrame after renaming. Skipping.")
            medians.append(np.nan)  # Append NaN if column is missing
if 1: # Generate the B06 Deliverable 1 (D1) table (finding text form of medians) and save it to a Markdown file
    output_md_path = "workplace_trait_medians.md"
    with open(output_md_path, "w", encoding="utf-8") as f:
        f.write("## B06 D1: Medians for Workplace Traits\n\n")
        from likert_mapping import LIKERT_ENGLISH # Code to English mapping
        f.write('| Group | Survey question (English translation) | Median answer (English translation) |\n')
        f.write('|-------|----------|--------|\n')
        for q, m in zip(QUESTIONS_WITH_TEST, medians):
            if 1: # Determine the text form of the median answer 
                if pd.isna(m):
                    formatted_median = "N/A"
                elif float(m).is_integer(): # The median clearly falls into a Likert scale category: look up
                    formatted_median = LIKERT_ENGLISH[int(m)]
                else: # The median falls between two Likert scale categories, e.g. 2.5: use "between" phrasing
                    lower = int(np.floor(m))
                    upper = int(np.ceil(m))
                    formatted_median = f'Between "{LIKERT_ENGLISH[lower]}" and "{LIKERT_ENGLISH[upper]}"'
            f.write(f'| PastEx | {q} | {formatted_median} |\n')
print(f"✅ Markdown file saved to {output_md_path}")