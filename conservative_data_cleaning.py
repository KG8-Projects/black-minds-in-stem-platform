"""
Black Minds in STEM: Conservative Data Cleaning Script
Preserves legitimate program variations while removing only true duplicates
"""

import pandas as pd
import numpy as np
from pathlib import Path
from difflib import SequenceMatcher
import os
from collections import defaultdict

# Constants
BASE_DIR = Path(r"C:\Users\u_wos\Downloads\Black Minds In STEM")
DATA_DIRS = [
    BASE_DIR / "Data",
    BASE_DIR / "Scrapers" / "data",
    BASE_DIR / "Scrapers" / "scrapers" / "data"
]
REVIEW_DIR = BASE_DIR / "data_quality_reports"
OUTPUT_DIR = BASE_DIR / "cleaned_data"

# Create output directories
(OUTPUT_DIR / "removal_records").mkdir(parents=True, exist_ok=True)
(OUTPUT_DIR / "review_needed").mkdir(parents=True, exist_ok=True)

def calculate_similarity(str1, str2):
    """Calculate string similarity ratio (0-1)"""
    if pd.isna(str1) or pd.isna(str2):
        return 0.0
    return SequenceMatcher(None, str(str1).lower(), str(str2).lower()).ratio()

def load_all_data():
    """Load all CSV files from the three data directories"""
    print("=" * 80)
    print("STEP 1: LOADING ALL DATA")
    print("=" * 80)

    all_data = []
    file_counts = {}

    for data_dir in DATA_DIRS:
        if not data_dir.exists():
            print(f"\nWarning: Directory not found: {data_dir}")
            continue

        print(f"\nScanning: {data_dir}")
        csv_files = list(data_dir.glob("*.csv"))
        print(f"Found {len(csv_files)} CSV files")

        for csv_file in csv_files:
            try:
                # Skip progress files and other non-resource files
                if 'progress' in csv_file.stem.lower():
                    continue

                df = pd.read_csv(csv_file)
                if not df.empty:
                    df['source_file'] = csv_file.stem
                    all_data.append(df)
                    file_counts[csv_file.stem] = len(df)
                    print(f"  [OK] {csv_file.name}: {len(df)} resources")
            except Exception as e:
                print(f"  [ERROR] Error reading {csv_file.name}: {e}")

    # Combine all data
    master_df = pd.concat(all_data, ignore_index=True)

    # Ensure source column exists
    if 'source' not in master_df.columns and 'source_file' in master_df.columns:
        master_df['source'] = master_df['source_file']

    print(f"\n{'='*80}")
    print(f"TOTAL RESOURCES LOADED: {len(master_df)}")
    print(f"{'='*80}\n")

    return master_df, file_counts

def load_review_files():
    """Load all review/flag files"""
    print("Loading review files...")

    review_files = {}

    # Load non-K-12 review file
    non_k12_file = REVIEW_DIR / "flagged_non_k12_resources.csv"
    if non_k12_file.exists():
        review_files['non_k12'] = pd.read_csv(non_k12_file)
        print(f"  [OK] Non-K-12 review: {len(review_files['non_k12'])} resources")
    else:
        print(f"  [MISSING] Non-K-12 review file not found")
        review_files['non_k12'] = pd.DataFrame()

    # Load educator resources file
    educator_file = REVIEW_DIR / "flagged_educator_resources.csv"
    if educator_file.exists():
        review_files['educator'] = pd.read_csv(educator_file)
        print(f"  [OK] Educator resources: {len(review_files['educator'])} resources")
    else:
        print(f"  [MISSING] Educator resources file not found")
        review_files['educator'] = pd.DataFrame()

    # Load duplicate analysis file
    duplicates_file = REVIEW_DIR / "duplicate_resources_analysis.csv"
    if duplicates_file.exists():
        review_files['duplicates'] = pd.read_csv(duplicates_file)
        print(f"  [OK] Duplicate analysis: {len(review_files['duplicates'])} entries")
    else:
        print(f"  [MISSING] Duplicate analysis file not found")
        review_files['duplicates'] = pd.DataFrame()

    print()
    return review_files

def remove_non_k12_resources(master_df, non_k12_review):
    """Remove non-K-12 resources based on Decisions column"""
    print("=" * 80)
    print("STEP 2: REMOVING NON-K-12 RESOURCES")
    print("=" * 80)

    if non_k12_review.empty:
        print("No non-K-12 review file found. Skipping this step.\n")
        return master_df, pd.DataFrame()

    print(f"\nTotal flagged non-K-12 resources: {len(non_k12_review)}")

    # Clean the Decisions column - handle various blank representations
    non_k12_review['Decisions'] = non_k12_review['Decisions'].fillna('').str.strip().str.upper()

    # Count decisions
    keep_count = (non_k12_review['Decisions'] == 'KEEP').sum()
    remove_count = (non_k12_review['Decisions'].isin(['REMOVE', ''])).sum()

    print(f"Resources marked as KEEP: {keep_count}")
    print(f"Resources marked as REMOVE or blank: {remove_count}")

    # Identify resources to remove
    to_remove = non_k12_review[
        (non_k12_review['Decisions'] == 'REMOVE') |
        (non_k12_review['Decisions'] == '')
    ].copy()

    if to_remove.empty:
        print("\nNo resources to remove.")
        return master_df, to_remove

    # Create removal list matching by name AND source_file
    # Review files use 'file_source' column with .csv extension
    initial_count = len(master_df)
    removed_resources = []

    for _, row in to_remove.iterrows():
        name = row['name']
        # Get file_source and remove .csv extension
        file_source = row.get('file_source', '')
        if file_source.endswith('.csv'):
            file_source = file_source[:-4]

        # Find matching resources in master dataset by name and source_file
        mask = (master_df['name'] == name) & (master_df['source_file'] == file_source)
        if mask.any():
            removed_resources.append(master_df[mask].copy())
            master_df = master_df[~mask].reset_index(drop=True)

    # Combine removed resources
    if removed_resources:
        removed_df = pd.concat(removed_resources, ignore_index=True)
    else:
        removed_df = pd.DataFrame()

    final_count = len(master_df)
    removed_count = initial_count - final_count

    print(f"\nResources removed: {removed_count}")
    print(f"Resources remaining: {final_count}")
    print("=" * 80 + "\n")

    return master_df, removed_df

def remove_educator_resources(master_df, educator_review):
    """Remove all educator resources"""
    print("=" * 80)
    print("STEP 3: REMOVING EDUCATOR RESOURCES")
    print("=" * 80)

    if educator_review.empty:
        print("No educator resources file found. Skipping this step.\n")
        return master_df, pd.DataFrame()

    print(f"\nTotal educator resources flagged: {len(educator_review)}")

    initial_count = len(master_df)
    removed_resources = []

    for _, row in educator_review.iterrows():
        name = row['name']
        # Get file_source and remove .csv extension
        file_source = row.get('file_source', '')
        if file_source.endswith('.csv'):
            file_source = file_source[:-4]

        # Find matching resources in master dataset by name and source_file
        mask = (master_df['name'] == name) & (master_df['source_file'] == file_source)
        if mask.any():
            removed_resources.append(master_df[mask].copy())
            master_df = master_df[~mask].reset_index(drop=True)

    # Combine removed resources
    if removed_resources:
        removed_df = pd.concat(removed_resources, ignore_index=True)
    else:
        removed_df = pd.DataFrame()

    final_count = len(master_df)
    removed_count = initial_count - final_count

    print(f"Educator resources removed: {removed_count}")
    print(f"Resources remaining: {final_count}")
    print("=" * 80 + "\n")

    return master_df, removed_df

def identify_program_family(name, description=''):
    """Identify program family from name/description"""
    name_lower = str(name).lower()
    desc_lower = str(description).lower()
    text = name_lower + ' ' + desc_lower

    families = {
        'Pioneer Academics': ['pioneer academic'],
        'RISE Program': ['rise @ ', 'rise at ', 'rise program'],
        'Stanford Pre-Collegiate': ['stanford pre-collegiate', 'stanford precollege'],
        'AI4ALL': ['ai4all'],
        'CMU Pre-College': ['cmu pre-college', 'carnegie mellon pre-college'],
        'MIT Programs': ['mit ', 'massachusetts institute of technology'],
        'CTY (Johns Hopkins)': ['cty', 'center for talented youth', 'johns hopkins'],
        'COSMOS': ['cosmos'],
        'SSP (Summer Science Program)': ['summer science program', 'ssp '],
        'RSI (Research Science Institute)': ['research science institute', 'rsi '],
        'Garcia Program': ['garcia ', 'garcia program'],
        'Clark Scholars': ['clark scholar'],
        'SSTP': ['sstp', 'secondary student training program'],
        'Boston Leadership Institute': ['boston leadership institute', 'bli '],
    }

    for family, keywords in families.items():
        for keyword in keywords:
            if keyword in text:
                return family

    return None

def extract_distinguishing_features(name, description, stem_fields):
    """Extract what makes this program variation unique"""
    features = []

    name_lower = str(name).lower()
    desc_lower = str(description).lower()

    # Check for subject/field mentions
    subjects = ['biology', 'chemistry', 'physics', 'mathematics', 'computer science',
                'engineering', 'economics', 'environmental', 'biomedical', 'artificial intelligence',
                'machine learning', 'data science', 'robotics', 'neuroscience']

    for subject in subjects:
        if subject in name_lower or subject in desc_lower:
            features.append(f"Subject: {subject.title()}")

    # Check for location mentions
    if '@' in name or 'at ' in name_lower:
        # Extract location
        if '@' in name:
            location = name.split('@')[-1].strip()
            features.append(f"Location: {location}")
        elif 'at ' in name_lower:
            parts = name_lower.split('at ')
            if len(parts) > 1:
                location = parts[-1].strip()
                features.append(f"Location: {location.title()}")

    # Check for grade level specifics
    grades = ['middle school', 'high school', 'grades 6-8', 'grades 9-12', '7th grade', '8th grade']
    for grade in grades:
        if grade in name_lower or grade in desc_lower:
            features.append(f"Grade: {grade.title()}")

    # Check for session/track mentions
    sessions = ['session 1', 'session 2', 'session 3', 'track a', 'track b', 'summer', 'winter']
    for session in sessions:
        if session in name_lower:
            features.append(f"Session: {session.title()}")

    # Add STEM field if available
    if pd.notna(stem_fields) and stem_fields:
        features.append(f"Field: {stem_fields}")

    return '; '.join(features) if features else 'No specific features identified'

def find_exact_duplicates(master_df):
    """Identify only truly identical resources (exact duplicates)"""
    print("=" * 80)
    print("STEP 4: CONSERVATIVE DUPLICATE DETECTION - EXACT MATCHES ONLY")
    print("=" * 80)

    exact_duplicates = []
    potential_duplicates = []
    duplicate_groups = defaultdict(list)

    print("\nPhase 4A: Identifying exact duplicates by URL...")

    # Group by URL (non-null, exact matches)
    url_groups = master_df[master_df['url'].notna()].groupby('url')

    url_dup_count = 0
    for url, group in url_groups:
        if len(group) > 1:
            # Check name similarity within this URL group
            names = group['name'].tolist()
            descriptions = group['description'].fillna('').tolist()

            # Compare all pairs
            for i in range(len(group)):
                for j in range(i + 1, len(group)):
                    name_sim = calculate_similarity(names[i], names[j])
                    desc_sim = calculate_similarity(descriptions[i], descriptions[j])

                    if name_sim >= 0.95 and desc_sim >= 0.90:
                        # Exact duplicate
                        url_dup_count += 1
                        exact_duplicates.append({
                            'group_id': f'URL_DUP_{url_dup_count}',
                            'resource_1_idx': group.iloc[i].name,
                            'resource_2_idx': group.iloc[j].name,
                            'name_1': names[i],
                            'name_2': names[j],
                            'url': url,
                            'name_similarity': name_sim,
                            'desc_similarity': desc_sim,
                            'duplicate_type': 'exact_url_match'
                        })
                        duplicate_groups[f'URL_DUP_{url_dup_count}'].extend([group.iloc[i].name, group.iloc[j].name])
                    elif name_sim >= 0.80 and name_sim < 0.95:
                        # Potential variation - needs review
                        potential_duplicates.append({
                            'group_id': f'REVIEW_{url_dup_count}',
                            'name_1': names[i],
                            'name_2': names[j],
                            'source_1': group.iloc[i]['source'],
                            'source_2': group.iloc[j]['source'],
                            'url': url,
                            'stem_fields_1': group.iloc[i].get('stem_fields', ''),
                            'stem_fields_2': group.iloc[j].get('stem_fields', ''),
                            'name_similarity': name_sim,
                            'recommendation': 'need_review',
                            'reason': 'Same URL but different names - possibly different programs'
                        })

    print(f"  Found {url_dup_count} exact duplicate pairs by URL")

    print("\nPhase 4B: Identifying exact duplicates by name + source...")

    # Group by name and source
    name_source_dup_count = 0
    name_source_groups = master_df.groupby(['name', 'source'])

    for (name, source), group in name_source_groups:
        if len(group) > 1:
            # Multiple entries with same name and source
            descriptions = group['description'].fillna('').tolist()

            # Check description similarity
            for i in range(len(group)):
                for j in range(i + 1, len(group)):
                    desc_sim = calculate_similarity(descriptions[i], descriptions[j])

                    if desc_sim >= 0.90:
                        # Exact duplicate
                        name_source_dup_count += 1
                        group_id = f'NAME_DUP_{name_source_dup_count}'
                        exact_duplicates.append({
                            'group_id': group_id,
                            'resource_1_idx': group.iloc[i].name,
                            'resource_2_idx': group.iloc[j].name,
                            'name': name,
                            'source': source,
                            'desc_similarity': desc_sim,
                            'duplicate_type': 'exact_name_source_match'
                        })
                        duplicate_groups[group_id].extend([group.iloc[i].name, group.iloc[j].name])

    print(f"  Found {name_source_dup_count} exact duplicate pairs by name + source")

    # Convert to DataFrames
    exact_dup_df = pd.DataFrame(exact_duplicates)
    potential_dup_df = pd.DataFrame(potential_duplicates)

    print(f"\nTotal exact duplicate pairs identified: {len(exact_dup_df)}")
    print(f"Total potential variations flagged for review: {len(potential_dup_df)}")
    print("=" * 80 + "\n")

    return exact_dup_df, potential_dup_df, duplicate_groups

def remove_exact_duplicates(master_df, duplicate_groups):
    """Remove exact duplicates, keeping most complete entry"""
    print("=" * 80)
    print("STEP 4C: REMOVING EXACT DUPLICATES")
    print("=" * 80)

    if not duplicate_groups:
        print("\nNo exact duplicates to remove.")
        return master_df, pd.DataFrame()

    initial_count = len(master_df)
    removed_resources = []
    indices_to_remove = set()

    print(f"\nProcessing {len(duplicate_groups)} duplicate groups...")

    for group_id, indices in duplicate_groups.items():
        # Get unique indices
        unique_indices = list(set(indices))

        if len(unique_indices) < 2:
            continue

        # Get resources in this group
        group_resources = master_df.loc[unique_indices]

        # Calculate completeness score for each resource
        completeness_scores = []
        for idx, row in group_resources.iterrows():
            non_null_count = row.notna().sum()
            desc_length = len(str(row.get('description', '')))
            score = non_null_count * 100 + desc_length
            completeness_scores.append((idx, score))

        # Sort by score descending
        completeness_scores.sort(key=lambda x: x[1], reverse=True)

        # Keep the first (most complete), remove the rest
        keep_idx = completeness_scores[0][0]
        remove_indices = [idx for idx, _ in completeness_scores[1:]]

        for idx in remove_indices:
            if idx not in indices_to_remove:
                indices_to_remove.add(idx)
                removed_resources.append(master_df.loc[idx].copy())

    # Remove duplicates
    if removed_resources:
        removed_df = pd.DataFrame(removed_resources)
        master_df = master_df.drop(list(indices_to_remove)).reset_index(drop=True)
    else:
        removed_df = pd.DataFrame()

    final_count = len(master_df)
    removed_count = initial_count - final_count

    print(f"\nExact duplicates removed: {removed_count}")
    print(f"Resources remaining: {final_count}")
    print("=" * 80 + "\n")

    return master_df, removed_df

def identify_keep_resource_duplicates(master_df, non_k12_review):
    """Identify duplicates among resources marked as KEEP (conservative)"""
    print("=" * 80)
    print("STEP 5: IDENTIFYING DUPLICATES AMONG KEEP RESOURCES (CONSERVATIVE)")
    print("=" * 80)

    if non_k12_review.empty:
        print("\nNo non-K-12 review file. Skipping this step.")
        return pd.DataFrame(), pd.DataFrame()

    # Get KEEP resources
    non_k12_review['Decisions'] = non_k12_review['Decisions'].fillna('').str.strip().str.upper()
    keep_resources = non_k12_review[non_k12_review['Decisions'] == 'KEEP'].copy()

    print(f"\nTotal KEEP resources: {len(keep_resources)}")

    # Get these resources from master dataset
    # Match by name and source_file (need to remove .csv from file_source)
    keep_df_list = []
    for _, row in keep_resources.iterrows():
        name = row['name']
        file_source = row.get('file_source', '')
        if file_source.endswith('.csv'):
            file_source = file_source[:-4]

        mask = (master_df['name'] == name) & (master_df['source_file'] == file_source)
        if mask.any():
            keep_df_list.append(master_df[mask])

    if keep_df_list:
        keep_df = pd.concat(keep_df_list, ignore_index=True)
    else:
        keep_df = pd.DataFrame()

    print(f"Found {len(keep_df)} KEEP resources in master dataset")

    exact_duplicates = []
    variations = []

    print("\nMethod 1: Identifying duplicates by same URL...")

    # Group by URL
    url_groups = keep_df[keep_df['url'].notna()].groupby('url')

    for url, group in url_groups:
        if len(group) > 1:
            # Check if these are exact duplicates or variations
            for i in range(len(group)):
                for j in range(i + 1, len(group)):
                    name_sim = calculate_similarity(group.iloc[i]['name'], group.iloc[j]['name'])
                    desc_sim = calculate_similarity(
                        group.iloc[i].get('description', ''),
                        group.iloc[j].get('description', '')
                    )

                    if name_sim >= 0.95 and desc_sim >= 0.90:
                        # Exact duplicate
                        exact_duplicates.append({
                            'duplicate_group_id': f'KEEP_URL_{len(exact_duplicates)+1}',
                            'name': group.iloc[i]['name'],
                            'source': group.iloc[i]['source'],
                            'url': url,
                            'stem_fields': group.iloc[i].get('stem_fields', ''),
                            'description_preview': str(group.iloc[i].get('description', ''))[:150],
                            'index': group.iloc[i].name
                        })
                    else:
                        # Possible variation
                        program_family = identify_program_family(
                            group.iloc[i]['name'],
                            group.iloc[i].get('description', '')
                        )

                        distinguishing = extract_distinguishing_features(
                            group.iloc[i]['name'],
                            group.iloc[i].get('description', ''),
                            group.iloc[i].get('stem_fields', '')
                        )

                        variations.append({
                            'variation_group_id': f'VAR_{len(variations)+1}',
                            'program_family': program_family or 'Unknown',
                            'name_1': group.iloc[i]['name'],
                            'name_2': group.iloc[j]['name'],
                            'source': group.iloc[i]['source'],
                            'url': url,
                            'stem_fields_1': group.iloc[i].get('stem_fields', ''),
                            'stem_fields_2': group.iloc[j].get('stem_fields', ''),
                            'distinguishing_feature': distinguishing,
                            'name_similarity': f"{name_sim:.2%}",
                            'recommendation': 'keep_separate',
                            'index_1': group.iloc[i].name,
                            'index_2': group.iloc[j].name
                        })

    print(f"  Found {len(exact_duplicates)} exact duplicates")
    print(f"  Found {len(variations)} legitimate variations")

    print("\nMethod 2: Identifying duplicates by same name + source...")

    # Group by name and source
    name_source_groups = keep_df.groupby(['name', 'source'])

    for (name, source), group in name_source_groups:
        if len(group) > 1:
            # Check description similarity
            for i in range(len(group)):
                for j in range(i + 1, len(group)):
                    desc_sim = calculate_similarity(
                        group.iloc[i].get('description', ''),
                        group.iloc[j].get('description', '')
                    )

                    if desc_sim >= 0.90:
                        # Exact duplicate
                        if group.iloc[i].name not in [d['index'] for d in exact_duplicates]:
                            exact_duplicates.append({
                                'duplicate_group_id': f'KEEP_NAME_{len(exact_duplicates)+1}',
                                'name': name,
                                'source': source,
                                'url': group.iloc[i].get('url', ''),
                                'stem_fields': group.iloc[i].get('stem_fields', ''),
                                'description_preview': str(group.iloc[i].get('description', ''))[:150],
                                'index': group.iloc[i].name
                            })

    print(f"  Found {len(exact_duplicates)} total exact duplicates among KEEP resources")

    # Convert to DataFrames
    exact_dup_df = pd.DataFrame(exact_duplicates)
    variations_df = pd.DataFrame(variations)

    print(f"\nSummary:")
    print(f"  Exact duplicates to remove: {len(exact_dup_df)}")
    print(f"  Legitimate variations to preserve: {len(variations_df)}")
    print("=" * 80 + "\n")

    return exact_dup_df, variations_df

def remove_keep_exact_duplicates(master_df, exact_dup_df):
    """Remove exact duplicates among KEEP resources"""
    print("=" * 80)
    print("STEP 6: REMOVING EXACT DUPLICATES AMONG KEEP RESOURCES")
    print("=" * 80)

    if exact_dup_df.empty:
        print("\nNo exact duplicates among KEEP resources to remove.")
        return master_df, pd.DataFrame()

    initial_count = len(master_df)

    # Get indices to remove
    indices_to_remove = exact_dup_df['index'].tolist()

    # Get removed resources for record
    removed_df = master_df.loc[indices_to_remove].copy()

    # Remove from master dataset
    master_df = master_df.drop(indices_to_remove).reset_index(drop=True)

    final_count = len(master_df)
    removed_count = initial_count - final_count

    print(f"\nExact duplicates among KEEP resources removed: {removed_count}")
    print(f"Resources remaining: {final_count}")
    print("=" * 80 + "\n")

    return master_df, removed_df

def generate_program_variations_analysis(master_df, variations_df):
    """Generate detailed analysis of program families and variations"""
    print("=" * 80)
    print("STEP 7: GENERATING PROGRAM VARIATIONS ANALYSIS")
    print("=" * 80)

    report_lines = []
    report_lines.append("=" * 80)
    report_lines.append("PROGRAM FAMILIES ANALYSIS")
    report_lines.append("Legitimate Program Variations Preserved")
    report_lines.append("=" * 80)
    report_lines.append("")

    # Identify program families in the dataset
    master_df['program_family'] = master_df.apply(
        lambda row: identify_program_family(row['name'], row.get('description', '')),
        axis=1
    )

    # Group by program family
    family_groups = master_df[master_df['program_family'].notna()].groupby('program_family')

    total_variations = 0

    for family, group in family_groups:
        if len(group) > 1:
            report_lines.append(f"\n{family} ({len(group)} variations preserved)")
            report_lines.append("-" * 80)

            for idx, row in group.iterrows():
                features = extract_distinguishing_features(
                    row['name'],
                    row.get('description', ''),
                    row.get('stem_fields', '')
                )

                report_lines.append(f"  - {row['name']}")
                report_lines.append(f"    Features: {features}")
                report_lines.append(f"    Grade: {row.get('target_grade', 'N/A')}")
                report_lines.append(f"    URL: {row.get('url', 'N/A')}")
                report_lines.append("")

            total_variations += len(group)

    report_lines.append("=" * 80)
    report_lines.append(f"TOTAL PROGRAM VARIATIONS PRESERVED: {total_variations}")
    report_lines.append("=" * 80)

    # Add variations from Step 5 analysis
    if not variations_df.empty:
        report_lines.append("\n\nDETAILED VARIATIONS FROM KEEP RESOURCES ANALYSIS")
        report_lines.append("=" * 80)

        for family in variations_df['program_family'].unique():
            family_vars = variations_df[variations_df['program_family'] == family]
            if len(family_vars) > 0:
                report_lines.append(f"\n{family} - {len(family_vars)} variation pairs")
                report_lines.append("-" * 40)

                for _, var in family_vars.iterrows():
                    report_lines.append(f"  Variation 1: {var['name_1']}")
                    report_lines.append(f"  Variation 2: {var['name_2']}")
                    report_lines.append(f"  Distinguishing: {var['distinguishing_feature']}")
                    report_lines.append(f"  Similarity: {var['name_similarity']}")
                    report_lines.append("")

    report_text = '\n'.join(report_lines)

    # Save report
    report_file = OUTPUT_DIR / "program_variations_analysis.txt"
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report_text)

    print(f"\n[OK] Program variations analysis saved to: {report_file}")
    print(f"  Total program families identified: {master_df['program_family'].notna().sum()}")
    print(f"  Total variations preserved: {total_variations}")
    print("=" * 80 + "\n")

    return report_text

def generate_cleaning_summary(master_df, initial_count, removal_stats, variations_count):
    """Generate comprehensive cleaning summary report"""
    print("=" * 80)
    print("STEP 8: GENERATING CLEANING SUMMARY REPORT")
    print("=" * 80)

    report_lines = []
    report_lines.append("=" * 80)
    report_lines.append("BLACK MINDS IN STEM - DATA CLEANING SUMMARY REPORT")
    report_lines.append("Conservative Approach: Preserving Program Variations")
    report_lines.append("=" * 80)
    report_lines.append("")

    # Removal Summary
    report_lines.append("REMOVAL SUMMARY")
    report_lines.append("-" * 80)
    report_lines.append(f"Starting dataset: {initial_count:,} resources")
    report_lines.append("")
    report_lines.append("Removals by category:")

    total_removed = 0
    for category, count in removal_stats.items():
        report_lines.append(f"  • {category}: {count:,} resources")
        total_removed += count

    report_lines.append(f"\n  Total removed: {total_removed:,} resources")
    report_lines.append(f"  Preserved variations: {variations_count:,} legitimate program variations")
    report_lines.append(f"\nFinal clean dataset: {len(master_df):,} resources")

    reduction_pct = (total_removed / initial_count * 100) if initial_count > 0 else 0
    report_lines.append(f"Reduction: {reduction_pct:.1f}%")
    report_lines.append("")

    # Dataset Statistics
    report_lines.append("\nCLEANED DATASET STATISTICS")
    report_lines.append("-" * 80)

    # Category distribution
    if 'category' in master_df.columns:
        report_lines.append("\nTop 10 Categories:")
        cat_counts = master_df['category'].value_counts().head(10)
        for cat, count in cat_counts.items():
            report_lines.append(f"  {cat}: {count}")

    # Target grade distribution
    if 'target_grade' in master_df.columns:
        report_lines.append("\nTop 10 Target Grades:")
        grade_counts = master_df['target_grade'].value_counts().head(10)
        for grade, count in grade_counts.items():
            report_lines.append(f"  {grade}: {count}")

    # Top sources
    if 'source' in master_df.columns:
        report_lines.append("\nTop 10 Sources:")
        source_counts = master_df['source'].value_counts().head(10)
        for source, count in source_counts.items():
            report_lines.append(f"  {source}: {count}")

    # Program families
    if 'program_family' in master_df.columns:
        report_lines.append("\nProgram Families with Multiple Variations (Top 10):")
        family_counts = master_df['program_family'].value_counts().head(10)
        for family, count in family_counts.items():
            if pd.notna(family) and count > 1:
                report_lines.append(f"  {family}: {count} variations")

    # Data Completeness
    report_lines.append("\n\nDATA COMPLETENESS AFTER CLEANING")
    report_lines.append("-" * 80)
    report_lines.append(f"{'Column':<30} {'Completeness':<15} {'Status':<10}")
    report_lines.append("-" * 80)

    for column in master_df.columns:
        completeness = (master_df[column].notna().sum() / len(master_df) * 100)

        if completeness >= 95:
            status = "[GOOD]"
        elif completeness >= 80:
            status = "[OK]"
        else:
            status = "[LOW]"

        report_lines.append(f"{column:<30} {completeness:>6.1f}%         {status}")

    # Conservative Approach Summary
    report_lines.append("\n\nCONSERVATIVE DUPLICATE APPROACH SUMMARY")
    report_lines.append("-" * 80)
    report_lines.append(f"Exact duplicates removed (true redundancy): {removal_stats.get('Exact duplicates', 0) + removal_stats.get('KEEP exact duplicates', 0)}")
    report_lines.append(f"Program variations preserved: {variations_count}")
    report_lines.append("")
    report_lines.append("This approach ensures that legitimate program variations")
    report_lines.append("(different courses, locations, subjects, etc.) are kept as")
    report_lines.append("separate resources while removing only truly identical entries.")

    # Next Steps
    report_lines.append("\n\nNEXT STEPS")
    report_lines.append("-" * 80)
    report_lines.append("1. Review flagged variations in: review_needed/keep_resources_variations_review.csv")
    report_lines.append("2. Review potential duplicates in: review_needed/potential_duplicates_review_needed.csv")
    report_lines.append("3. Verify program families in: program_variations_analysis.txt")
    report_lines.append("4. Check removal records in: removal_records/ directory")
    report_lines.append("5. Use cleaned dataset: bmis_clean_master_dataset.csv")

    report_lines.append("\n" + "=" * 80)

    report_text = '\n'.join(report_lines)

    # Save report
    report_file = OUTPUT_DIR / "cleaning_summary_report.txt"
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report_text)

    print(f"\n[OK] Cleaning summary report saved to: {report_file}")
    print("=" * 80 + "\n")

    return report_text

def main():
    """Main execution function"""
    print("\n" + "=" * 80)
    print("BLACK MINDS IN STEM - CONSERVATIVE DATA CLEANING")
    print("Preserving Program Variations, Removing Only True Duplicates")
    print("=" * 80 + "\n")

    # Step 1: Load all data
    master_df, file_counts = load_all_data()
    initial_count = len(master_df)

    review_files = load_review_files()

    # Track removal statistics
    removal_stats = {}

    # Step 2: Remove non-K-12 resources
    master_df, removed_non_k12 = remove_non_k12_resources(
        master_df,
        review_files.get('non_k12', pd.DataFrame())
    )
    removal_stats['Non-K-12 resources'] = len(removed_non_k12)

    # Step 3: Remove educator resources
    master_df, removed_educator = remove_educator_resources(
        master_df,
        review_files.get('educator', pd.DataFrame())
    )
    removal_stats['Educator resources'] = len(removed_educator)

    # Step 4: Identify and remove exact duplicates
    exact_dup_df, potential_dup_df, duplicate_groups = find_exact_duplicates(master_df)
    master_df, removed_exact_dups = remove_exact_duplicates(master_df, duplicate_groups)
    removal_stats['Exact duplicates'] = len(removed_exact_dups)

    # Step 5: Identify duplicates among KEEP resources
    keep_exact_dups, keep_variations = identify_keep_resource_duplicates(
        master_df,
        review_files.get('non_k12', pd.DataFrame())
    )

    # Step 6: Remove exact duplicates among KEEP resources
    master_df, removed_keep_dups = remove_keep_exact_duplicates(master_df, keep_exact_dups)
    removal_stats['KEEP exact duplicates'] = len(removed_keep_dups)

    # Step 7: Generate program variations analysis
    variations_count = len(keep_variations)
    program_variations_report = generate_program_variations_analysis(master_df, keep_variations)

    # Step 8: Generate cleaning summary
    cleaning_summary = generate_cleaning_summary(
        master_df,
        initial_count,
        removal_stats,
        variations_count
    )

    # Step 9: Save all outputs
    print("=" * 80)
    print("STEP 9: SAVING CLEANED DATASET AND REPORTS")
    print("=" * 80)

    # Save cleaned master dataset
    clean_file = OUTPUT_DIR / "bmis_clean_master_dataset.csv"
    master_df.to_csv(clean_file, index=False, encoding='utf-8')
    print(f"\n[OK] Cleaned master dataset saved: {clean_file}")
    print(f"  Total resources: {len(master_df):,}")

    # Save removal records
    if not removed_non_k12.empty:
        removed_non_k12.to_csv(
            OUTPUT_DIR / "removal_records" / "removed_non_k12.csv",
            index=False, encoding='utf-8'
        )
        print(f"[OK] Non-K-12 removal record: {len(removed_non_k12)} resources")

    if not removed_educator.empty:
        removed_educator.to_csv(
            OUTPUT_DIR / "removal_records" / "removed_educator.csv",
            index=False, encoding='utf-8'
        )
        print(f"[OK] Educator removal record: {len(removed_educator)} resources")

    if not removed_exact_dups.empty:
        removed_exact_dups.to_csv(
            OUTPUT_DIR / "removal_records" / "removed_exact_duplicates.csv",
            index=False, encoding='utf-8'
        )
        print(f"[OK] Exact duplicates removal record: {len(removed_exact_dups)} resources")

    if not removed_keep_dups.empty:
        removed_keep_dups.to_csv(
            OUTPUT_DIR / "removal_records" / "removed_keep_exact_duplicates.csv",
            index=False, encoding='utf-8'
        )
        print(f"[OK] KEEP exact duplicates removal record: {len(removed_keep_dups)} resources")

    # Save review needed files
    if not potential_dup_df.empty:
        potential_dup_df.to_csv(
            OUTPUT_DIR / "review_needed" / "potential_duplicates_review_needed.csv",
            index=False, encoding='utf-8'
        )
        print(f"[OK] Potential duplicates for review: {len(potential_dup_df)} cases")

    if not keep_variations.empty:
        keep_variations.to_csv(
            OUTPUT_DIR / "review_needed" / "keep_resources_variations_review.csv",
            index=False, encoding='utf-8'
        )
        print(f"[OK] Program variations for review: {len(keep_variations)} cases")

    print("\n" + "=" * 80)
    print("DATA CLEANING COMPLETE!")
    print("=" * 80)
    print(f"\nStarting resources: {initial_count:,}")
    print(f"Final clean dataset: {len(master_df):,}")
    print(f"Total removed: {initial_count - len(master_df):,}")
    print(f"Variations preserved: {variations_count:,}")
    print(f"\nAll outputs saved to: {OUTPUT_DIR}")
    print("=" * 80 + "\n")

    # Quality assurance checks
    print("=" * 80)
    print("QUALITY ASSURANCE CHECKS")
    print("=" * 80)

    # Check 1: Program families with multiple variations
    if 'program_family' in master_df.columns:
        multi_var_families = master_df['program_family'].value_counts()
        multi_var_families = multi_var_families[multi_var_families > 1]
        print(f"\n[OK] Program families with multiple variations: {len(multi_var_families)}")
        if len(multi_var_families) > 0:
            print("  Top program families:")
            for family, count in multi_var_families.head(10).items():
                if pd.notna(family):
                    print(f"    - {family}: {count} variations")

    # Check 2: Verify different locations preserved
    pioneer_programs = master_df[master_df['name'].str.contains('Pioneer', case=False, na=False)]
    if len(pioneer_programs) > 1:
        print(f"\n[OK] Pioneer Academics variations preserved: {len(pioneer_programs)}")

    rise_programs = master_df[master_df['name'].str.contains('RISE', case=False, na=False)]
    if len(rise_programs) > 1:
        print(f"[OK] RISE program variations preserved: {len(rise_programs)}")

    ai4all_programs = master_df[master_df['name'].str.contains('AI4ALL', case=False, na=False)]
    if len(ai4all_programs) > 1:
        print(f"[OK] AI4ALL program variations preserved: {len(ai4all_programs)}")

    print("\n" + "=" * 80)
    print("All quality assurance checks completed!")
    print("=" * 80 + "\n")

if __name__ == "__main__":
    main()
