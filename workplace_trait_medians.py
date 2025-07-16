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
PASTEX_COLUMN_NAMES = [
    "C026", # At my previous organization, all the necessary communication tools were fully available.
    "C028", # At my previous workplace, my employer ensured that the necessary information reached me in a timely manner.
    "C030", # It is so important to me that I receive all the information necessary for my work, that the lack of necessary information contributed to my decision to change jobs. (This is a 1.2 question, but the prompt's list includes it. Will treat as 1.1 for this context)
    "C032", # The management of my previous organization supported being informed about organizational matters through various measures (e.g., newsletters, reminders, regular information sessions).
    "C034", # At my previous organization, communication in person or online (such as daily/weekly group meetings, conferences, conversations with direct supervisors) was regular.
    "C036", # My previous workplace encouraged everyone to share their ideas through various measures (e.g., brainstorming meetings, suggestion boxes).
    "C038", # My previous employer encouraged everyone to openly express their dissatisfaction (e.g., there was a "complaint" box).
    "C040", # At my previous employer it was standard practice that good performance was recognized verbally as well, and positive feedback (such as praise and announcements of successful results).
    "C042", # My previous organization made informal communication and casual conversations possible; they were part of everyday life.
    "C044", # At my previous workplace, the style of communication was honest and respectful.
]
PRESENTEX_COLUMN_NAMES = [
    "C080", # My employer ensures that the necessary information reaches me in a timely manner.
    "C082", # My current employer fully provides all the information necessary for my work.
    "C084", # The management supports being informed about organizational matters through various measures (e.g., newsletters, reminders, regular informational forums).
    "C086", # In our organization, in-person or online communication is regular. We regularly hold meetings, group discussions, and meetings with direct supervisors.
    "C088", # Our organizational leadership encourages everyone to share their ideas through various measures (e.g., brainstorming meetings, suggestion boxes).
    "C090", # My employer encourages everyone to freely express their dissatisfaction (e.g., there is a "complaint" box).
    "C092", # Verbal recognition of good performance and positive feedback (e.g., praise, announcements of successful results) is standard practice at my employer.
    "C094", # Management enables informal communication and casual conversations. These are part of our organization’s everyday life.
    "C096", # At my workplace, the style of communication is honest and respectful.
]
QUESTIONS_ENGLISH_TRANSLATIONS_PASTEX = [
    "At my previous organization, all the necessary communication tools were fully available.",
    "At my previous workplace, my employer ensured that the necessary information reached me in a timely manner.",
    "It is so important to me that I receive all the information necessary for my work, that the lack of necessary information contributed to my decision to change jobs.",
    "The management of my previous organization supported being informed about organizational matters through various measures (e.g., newsletters, reminders, regular information sessions).",
    "At my previous organization, communication in person or online (such as daily/weekly group meetings, conferences, conversations with direct supervisors) was regular.",
    "My previous workplace encouraged everyone to share their ideas through various measures (e.g., brainstorming meetings, suggestion boxes).",
    "My previous employer encouraged everyone to openly express their dissatisfaction (e.g., there was a \"complaint\" box).",
    "At my previous employer it was standard practice that good performance was recognized verbally as well, and positive feedback (such as praise and announcements of successful results).",
    "My previous organization made informal communication and casual conversations possible; they were part of everyday life.",
    "At my previous workplace, the style of communication was honest and respectful.",
]
QUESTIONS_ENGLISH_TRANSLATIONS_PRESENTEX = [
    "My employer ensures that the necessary information reaches me in a timely manner.",
    "My current employer fully provides all the information necessary for my work.",
    "The management supports being informed about organizational matters through various measures (e.g., newsletters, reminders, regular informational forums).",
    "In our organization, in-person or online communication is regular. We regularly hold meetings, group discussions, and meetings with direct supervisors.",
    "Our organizational leadership encourages everyone to share their ideas through various measures (e.g., brainstorming meetings, suggestion boxes).",
    "My employer encourages everyone to freely express their dissatisfaction (e.g., there is a \"complaint\" box).",
    "Verbal recognition of good performance and positive feedback (e.g., praise, announcements of successful results) is standard practice at my employer.",
    "Management enables informal communication and casual conversations. These are part of our organization’s everyday life.",
    "At my workplace, the style of communication is honest and respectful.",
]
if 1: # Data check: Find the unique values of each PastEx and PresentEx Variable observed
    print("--- Unique Values for Workplace Trait Variables ---")
    all_workplace_trait_columns = PASTEX_COLUMN_NAMES + PRESENTEX_COLUMN_NAMES
    for col_id in all_workplace_trait_columns:
        if col_id in data.columns:
            unique_values = data[col_id].unique()
            print(f"\nColumn: {col_id}")
            print(f"Unique values: {unique_values.tolist()}")
        else:
            print(f"\nWarning: Column ID '{col_id}' not found in the DataFrame after renaming.")
if 1: # For each survey question convert answers to numbers, calculate medians
    from likert_mapping import LIKERT_MAPPING # Hungarian to code mapping
    medians_data = [] # Prepare a list to store dictionaries with calculated medians and question info
    max_len = max(len(PASTEX_COLUMN_NAMES), len(PRESENTEX_COLUMN_NAMES)) # Interleave PastEx and PresentEx questions for output  
    for i in range(max_len):
        # Process PastEx question if it exists
        if i < len(PASTEX_COLUMN_NAMES):
            col_id_past = PASTEX_COLUMN_NAMES[i]
            question_past = QUESTIONS_ENGLISH_TRANSLATIONS_PASTEX[i]
            median_past = np.nan
            if col_id_past in data.columns:
                numeric_data_past = data[col_id_past].map(LIKERT_MAPPING).dropna()
                if not numeric_data_past.empty:
                    median_past = numeric_data_past.median()
            else:
                print(f"Warning: PastEx Column ID '{col_id_past}' not found. Skipping.")
            medians_data.append({"Group": "PastEx", "Question": question_past, "Median": median_past})
        if i < len(PRESENTEX_COLUMN_NAMES): # Process PresentEx question if it exists
            col_id_present = PRESENTEX_COLUMN_NAMES[i]
            question_present = QUESTIONS_ENGLISH_TRANSLATIONS_PRESENTEX[i]
            median_present = np.nan
            if col_id_present in data.columns:
                numeric_data_present = data[col_id_present].map(LIKERT_MAPPING).dropna()
                if not numeric_data_present.empty:
                    median_present = numeric_data_present.median()
            else:
                print(f"Warning: PresentEx Column ID '{col_id_present}' not found. Skipping.")
            medians_data.append({"Group": "PresentEx", "Question": question_present, "Median": median_present})
if 1: # Generate the B06 Deliverable 1 (D1) table (finding text form of medians) and save it to a Markdown file
    output_md_path = "workplace_trait_medians.md"
    with open(output_md_path, "w", encoding="utf-8") as f:
        f.write("## B06 D1: Medians for Workplace Traits\n\n")
        from likert_mapping import LIKERT_ENGLISH # Code to English mapping
        f.write('| Group | Survey question (English translation) | Median answer (English translation) |\n')
        f.write('|-------|----------|--------|\n')
        for item in medians_data:
            q_group = item["Group"]
            q_text = item["Question"]
            m = item["Median"]

            if pd.isna(m):
                formatted_median = "N/A"
            elif float(m).is_integer():
                formatted_median = LIKERT_ENGLISH[int(m)]
            else:
                lower = int(np.floor(m))
                upper = int(np.ceil(m))
                formatted_median = f'Between "{LIKERT_ENGLISH[lower]}" and "{LIKERT_ENGLISH[upper]}"'
            f.write(f'| {q_group} | {q_text} | {formatted_median} |\n')
print(f"✅ Markdown file saved to {output_md_path}")