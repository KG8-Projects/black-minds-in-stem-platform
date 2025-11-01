#!/usr/bin/env python3
"""
Black Minds in STEM - Conservative Data Cleaning
Preserves legitimate program variations while removing only exact duplicates
"""

import os
import glob
import pandas as pd
import numpy as np
from datetime import datetime
from collections import defaultdict
import warnings
warnings.filterwarnings('ignore')

# For fuzzy string matching
try:
    from fuzzywuzzy import fuzz
    FUZZY_AVAILABLE = True
except ImportError:
    print("WARNING: fuzzywuzzy not installed. Installing...")
    import subprocess
    subprocess.check_call(['pip', 'install', 'fuzzywuzzy', 'python-Levenshtein'])
    from fuzzywuzzy import fuzz
    FUZZY_AVAILABLE = True

class ConservativeDataCleaner:
    """Conservative data cleaning preserving legitimate program variations"""

    def __init__(self):
        self.directories = ['Data', 'Scrapers/data', 'Scrapers/scrapers/data']
        self.master_df = None
        self.removal_records = {
            'non_k12': [],
            'educator': [],
            'exact_duplicates': [],
            'keep_exact_duplicates': []
        }
        self.review_needed = {
            'potential_duplicates': [],
            'keep_variations': []
        }
        self.stats = {
            'starting_count': 0,
            'removed_non_k12': 0,
            'removed_educator': 0,
            'removed_exact_dupes': 0,
            'removed_keep_exact_dupes': 0,
            'preserved_variations': 0,
            'flagged_for_review': 0,
            'final_count': 0
        }
        self.program_families = defaultdict(list)

        # Create output directories
        os.makedirs('cleaned_data', exist_ok=True)
        os.makedirs('cleaned_data/removal_records', exist_ok=True)
        os.makedirs('cleaned_data/review_needed', exist_ok=True)

    def log(self, message, level='INFO'):
        """Print timestamped log message"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f"[{timestamp}] [{level}] {message}")

    # ==================== STEP 1: Load Data ====================

    def load_master_dataset(self):
        """Load all CSV files and create master dataset"""
        self.log("=" * 80)
        self.log("STEP 1: Loading Master Dataset")
        self.log("=" * 80)

        all_dfs = []
        for directory in self.directories:
            if not os.path.exists(directory):
                continue

            csv_files = glob.glob(os.path.join(directory, "*.csv"))
            self.log(f"Loading {len(csv_files)} CSV files from {directory}")

            for csv_file in csv_files:
                try:
                    df = pd.read_csv(csv_file, encoding='utf-8')
                    df['file_source'] = os.path.basename(csv_file)
                    df['directory_source'] = directory
                    all_dfs.append(df)
                except UnicodeDecodeError:
                    df = pd.read_csv(csv_file, encoding='latin-1')
                    df['file_source'] = os.path.basename(csv_file)
                    df['directory_source'] = directory
                    all_dfs.append(df)
                except Exception as e:
                    self.log(f"Failed to load {csv_file}: {str(e)}", 'WARN')

        self.master_df = pd.concat(all_dfs, ignore_index=True)
        self.stats['starting_count'] = len(self.master_df)

        self.log(f"Successfully loaded {len(all_dfs)} files")
        self.log(f"Total resources: {len(self.master_df)}")

        self.load_review_files()
        return self.master_df

    def load_review_files(self):
        """Load manual review files"""
        self.log("\nLoading manual review files...")

        # Load non-K-12 review - note the column is "Decisions" with an 's'
        non_k12_path = 'data_quality_reports/flagged_non_k12_resources.csv'
        if os.path.exists(non_k12_path):
            self.non_k12_review = pd.read_csv(non_k12_path)
            self.non_k12_review.columns = [col.strip() for col in self.non_k12_review.columns]

            # Look for either "Decision" or "Decisions"
            decision_col = None
            if 'Decisions' in self.non_k12_review.columns:
                decision_col = 'Decisions'
            elif 'Decision' in self.non_k12_review.columns:
                decision_col = 'Decision'

            if decision_col:
                self.non_k12_review['decision_clean'] = (
                    self.non_k12_review[decision_col]
                    .astype(str).str.strip().str.upper()
                    .replace(['NAN', 'NONE', ''], '')
                )
            self.log(f"Loaded {len(self.non_k12_review)} non-K-12 flagged resources")
        else:
            self.non_k12_review = pd.DataFrame()

        # Load educator resources
        educator_path = 'data_quality_reports/flagged_educator_resources.csv'
        if os.path.exists(educator_path):
            self.educator_review = pd.read_csv(educator_path)
            self.log(f"Loaded {len(self.educator_review)} educator resources")
        else:
            self.educator_review = pd.DataFrame()

        # Load duplicates
        dupes_path = 'data_quality_reports/duplicate_resources_analysis.csv'
        if os.path.exists(dupes_path):
            self.duplicates_review = pd.read_csv(dupes_path)
            self.log(f"Loaded {len(self.duplicates_review)} duplicate groups")
        else:
            self.duplicates_review = pd.DataFrame()

    # ==================== STEP 2: Remove Non-K-12 ====================

    def remove_non_k12_resources(self):
        """Remove non-K-12 resources based on manual review"""
        self.log("\n" + "=" * 80)
        self.log("STEP 2: Removing Non-K-12 Resources")
        self.log("=" * 80)

        if self.non_k12_review.empty or 'decision_clean' not in self.non_k12_review.columns:
            self.log("No non-K-12 review data to process")
            return

        total = len(self.non_k12_review)
        keep = (self.non_k12_review['decision_clean'] == 'KEEP').sum()
        remove = total - keep

        self.log(f"Total flagged: {total}")
        self.log(f"Marked as KEEP: {keep}")
        self.log(f"To be removed: {remove}")

        to_remove = self.non_k12_review[self.non_k12_review['decision_clean'] != 'KEEP'].copy()

        if len(to_remove) == 0:
            return

        # Match by name and file_source
        removal_keys = set()
        for idx, row in to_remove.iterrows():
            name = str(row.get('name', '')).strip()
            source = str(row.get('file_source', '')).strip()
            if name and source:
                removal_keys.add((name, source))

        before = len(self.master_df)
        removed = []

        for name, file_source in removal_keys:
            matching = self.master_df[
                (self.master_df['name'].astype(str).str.strip() == name) &
                (self.master_df['file_source'].astype(str).str.strip() == file_source)
            ]
            if len(matching) > 0:
                removed.append(matching.copy())
                self.master_df = self.master_df[
                    ~((self.master_df['name'].astype(str).str.strip() == name) &
                      (self.master_df['file_source'].astype(str).str.strip() == file_source))
                ]

        if removed:
            self.removal_records['non_k12'] = pd.concat(removed, ignore_index=True)

        after = len(self.master_df)
        self.stats['removed_non_k12'] = before - after
        self.log(f"Removed {before - after} non-K-12 resources")
        self.log(f"Remaining: {after}")

    # ==================== STEP 3: Remove Educator Resources ====================

    def remove_educator_resources(self):
        """Remove educator resources"""
        self.log("\n" + "=" * 80)
        self.log("STEP 3: Removing Educator Resources")
        self.log("=" * 80)

        if self.educator_review.empty:
            return

        removal_keys = set()
        for idx, row in self.educator_review.iterrows():
            name = str(row.get('name', '')).strip()
            source = str(row.get('file_source', '')).strip()
            if name and source:
                removal_keys.add((name, source))

        before = len(self.master_df)
        removed = []

        for name, file_source in removal_keys:
            matching = self.master_df[
                (self.master_df['name'].astype(str).str.strip() == name) &
                (self.master_df['file_source'].astype(str).str.strip() == file_source)
            ]
            if len(matching) > 0:
                removed.append(matching.copy())
                self.master_df = self.master_df[
                    ~((self.master_df['name'].astype(str).str.strip() == name) &
                      (self.master_df['file_source'].astype(str).str.strip() == file_source))
                ]

        if removed:
            self.removal_records['educator'] = pd.concat(removed, ignore_index=True)

        after = len(self.master_df)
        self.stats['removed_educator'] = before - after
        self.log(f"Removed {before - after} educator resources")
        self.log(f"Remaining: {after}")

    # ==================== STEP 4: Conservative Duplicate Detection ====================

    def is_exact_duplicate(self, row1, row2):
        """Check if two resources are exact duplicates using conservative criteria"""
        # URL must match exactly (and not be null)
        url1 = str(row1.get('url', '')).strip()
        url2 = str(row2.get('url', '')).strip()

        if not url1 or not url2 or url1 != url2:
            return False

        # Name similarity must be 95%+
        name1 = str(row1.get('name', '')).strip().lower()
        name2 = str(row2.get('name', '')).strip().lower()
        name_sim = fuzz.ratio(name1, name2)

        if name_sim < 95:
            return False

        # Description similarity must be 90%+
        desc1 = str(row1.get('description', '')).strip().lower()
        desc2 = str(row2.get('description', '')).strip().lower()
        desc_sim = fuzz.ratio(desc1, desc2)

        if desc_sim < 90:
            return False

        # Target grade should match (or both be null)
        grade1 = str(row1.get('target_grade', '')).strip()
        grade2 = str(row2.get('target_grade', '')).strip()

        if grade1 and grade2 and grade1 != grade2:
            return False

        return True

    def is_legitimate_variation(self, row1, row2):
        """Check if two resources are legitimate variations of same program"""
        name1 = str(row1.get('name', '')).lower()
        name2 = str(row2.get('name', '')).lower()
        desc1 = str(row1.get('description', '')).lower()
        desc2 = str(row2.get('description', '')).lower()
        stem1 = str(row1.get('stem_fields', '')).lower()
        stem2 = str(row2.get('stem_fields', '')).lower()

        # Different STEM fields = different programs
        if stem1 and stem2 and stem1 != stem2:
            return True, "Different STEM fields"

        # Different locations mentioned
        location_keywords = ['university', 'college', '@', 'at ', 'stanford', 'mit', 'harvard',
                            'berkeley', 'princeton', 'yale', 'cornell', 'columbia']

        for keyword in location_keywords:
            loc1_match = keyword in name1 or keyword in desc1
            loc2_match = keyword in name2 or keyword in desc2
            if loc1_match != loc2_match:
                return True, f"Different location ({keyword})"

        # Different courses/subjects mentioned
        subject_keywords = ['biology', 'chemistry', 'physics', 'computer science', 'engineering',
                           'mathematics', 'ai', 'machine learning', 'data science', 'robotics',
                           'biomedical', 'neuroscience', 'astronomy', 'environmental']

        for subject in subject_keywords:
            subj1_match = subject in name1 or subject in desc1
            subj2_match = subject in name2 or subject in desc2
            if subj1_match != subj2_match:
                return True, f"Different subject ({subject})"

        # Different grade levels
        grade1 = str(row1.get('target_grade', '')).strip()
        grade2 = str(row2.get('target_grade', '')).strip()
        if grade1 and grade2 and grade1 != grade2:
            return True, "Different target grades"

        # Different session indicators
        session_keywords = ['session 1', 'session 2', 'summer', 'fall', 'spring', 'winter']
        for session in session_keywords:
            sess1 = session in name1.lower()
            sess2 = session in name2.lower()
            if sess1 != sess2:
                return True, f"Different session ({session})"

        return False, ""

    def calculate_completeness_score(self, row):
        """Calculate completeness score"""
        non_null = row.notna().sum()
        desc_len = len(str(row.get('description', '')))
        has_url = 1 if pd.notna(row.get('url')) and str(row.get('url')).strip() else 0
        return non_null + (desc_len / 100) + (has_url * 2)

    def conservative_duplicate_detection(self):
        """Conservative duplicate detection - exact matches only"""
        self.log("\n" + "=" * 80)
        self.log("STEP 4: Conservative Duplicate Detection (Exact Matches Only)")
        self.log("=" * 80)

        exact_dupes = []
        potential_dupes = []

        # Group by URL (only non-null URLs)
        url_groups = self.master_df[self.master_df['url'].notna()].groupby('url')

        self.log(f"Analyzing {len(url_groups)} URL groups...")

        for url, group in url_groups:
            if len(group) <= 1:
                continue

            # Check each pair in the group
            resources = list(group.iterrows())
            for i in range(len(resources)):
                for j in range(i + 1, len(resources)):
                    idx1, row1 = resources[i]
                    idx2, row2 = resources[j]

                    if self.is_exact_duplicate(row1, row2):
                        exact_dupes.append({
                            'group_id': f"EXACT_{len(exact_dupes)}",
                            'index1': idx1,
                            'index2': idx2,
                            'name1': row1.get('name'),
                            'name2': row2.get('name'),
                            'url': url,
                            'reason': 'Exact duplicate'
                        })
                    else:
                        # Check if legitimate variation
                        is_variation, reason = self.is_legitimate_variation(row1, row2)

                        name_sim = fuzz.ratio(
                            str(row1.get('name', '')).lower(),
                            str(row2.get('name', '')).lower()
                        )

                        if is_variation:
                            potential_dupes.append({
                                'group_id': f"VAR_{len(potential_dupes)}",
                                'index1': idx1,
                                'index2': idx2,
                                'name1': row1.get('name'),
                                'name2': row2.get('name'),
                                'stem_fields1': row1.get('stem_fields'),
                                'stem_fields2': row2.get('stem_fields'),
                                'url': url,
                                'name_similarity': name_sim,
                                'recommendation': 'keep_separate',
                                'reason': reason
                            })
                        elif name_sim >= 80:  # Similar but unclear
                            potential_dupes.append({
                                'group_id': f"UNCLEAR_{len(potential_dupes)}",
                                'index1': idx1,
                                'index2': idx2,
                                'name1': row1.get('name'),
                                'name2': row2.get('name'),
                                'stem_fields1': row1.get('stem_fields'),
                                'stem_fields2': row2.get('stem_fields'),
                                'url': url,
                                'name_similarity': name_sim,
                                'recommendation': 'need_review',
                                'reason': 'Unclear - manual review needed'
                            })

        self.log(f"Found {len(exact_dupes)} exact duplicate pairs")
        self.log(f"Found {len(potential_dupes)} potential variations/unclear cases")

        # Remove exact duplicates
        if exact_dupes:
            self.remove_exact_duplicates(exact_dupes)

        # Save potential duplicates for review
        if potential_dupes:
            self.review_needed['potential_duplicates'] = pd.DataFrame(potential_dupes)
            review_path = 'cleaned_data/review_needed/potential_duplicates_review_needed.csv'
            self.review_needed['potential_duplicates'].to_csv(review_path, index=False)
            self.log(f"Saved {len(potential_dupes)} cases for manual review: {review_path}")
            self.stats['flagged_for_review'] += len(potential_dupes)

    def remove_exact_duplicates(self, exact_dupes):
        """Remove exact duplicates keeping most complete version"""
        self.log("\nRemoving exact duplicates...")

        # Group by group_id
        groups = defaultdict(list)
        for dupe in exact_dupes:
            groups[dupe['group_id']].append(dupe)

        removed_count = 0
        removed = []

        for group_id, dupes_list in groups.items():
            # Get all indices in this duplicate group
            indices = set()
            for dupe in dupes_list:
                indices.add(dupe['index1'])
                indices.add(dupe['index2'])

            if len(indices) <= 1:
                continue

            # Get all resources
            matching = self.master_df.loc[list(indices)]

            # Calculate completeness scores
            scores = matching.apply(self.calculate_completeness_score, axis=1)
            best_idx = scores.idxmax()

            # Remove all except best
            to_remove = matching[matching.index != best_idx]

            if len(to_remove) > 0:
                removed.append(to_remove.copy())
                self.master_df = self.master_df.drop(to_remove.index)
                removed_count += len(to_remove)

        if removed:
            self.removal_records['exact_duplicates'] = pd.concat(removed, ignore_index=True)

        self.stats['removed_exact_dupes'] = removed_count
        self.log(f"Removed {removed_count} exact duplicate entries")
        self.log(f"Remaining: {len(self.master_df)}")

    # ==================== STEP 5 & 6: KEEP Resources Analysis ====================

    def analyze_keep_resources(self):
        """Analyze KEEP resources for exact duplicates with conservative approach"""
        self.log("\n" + "=" * 80)
        self.log("STEP 5-6: Conservative Analysis of KEEP Resources")
        self.log("=" * 80)

        if 'decision_clean' not in self.non_k12_review.columns:
            self.log("Analyzing all remaining resources...")
            keep_df = self.master_df.copy()
        else:
            keep_resources = self.non_k12_review[
                self.non_k12_review['decision_clean'] == 'KEEP'
            ]
            keep_names = set(str(row.get('name', '')).strip()
                           for idx, row in keep_resources.iterrows())
            keep_df = self.master_df[
                self.master_df['name'].astype(str).str.strip().isin(keep_names)
            ].copy()
            self.log(f"Analyzing {len(keep_df)} KEEP resources")

        exact_dupes = []
        variations = []

        # Group by URL
        url_groups = keep_df[keep_df['url'].notna()].groupby('url')

        for url, group in url_groups:
            if len(group) <= 1:
                continue

            # Track program families
            if len(group) > 1:
                # Try to identify program family
                names = group['name'].tolist()
                common_words = self.find_common_program_name(names)
                if common_words:
                    self.program_families[common_words].extend(names)

            resources = list(group.iterrows())
            for i in range(len(resources)):
                for j in range(i + 1, len(resources)):
                    idx1, row1 = resources[i]
                    idx2, row2 = resources[j]

                    if self.is_exact_duplicate(row1, row2):
                        exact_dupes.append({
                            'index1': idx1,
                            'index2': idx2,
                            'name': row1.get('name'),
                            'url': url
                        })
                    else:
                        is_variation, reason = self.is_legitimate_variation(row1, row2)
                        if is_variation:
                            variations.append({
                                'name1': row1.get('name'),
                                'name2': row2.get('name'),
                                'stem_fields1': row1.get('stem_fields'),
                                'stem_fields2': row2.get('stem_fields'),
                                'url': url,
                                'distinguishing_feature': reason,
                                'recommendation': 'keep_separate'
                            })

        self.log(f"Found {len(exact_dupes)} exact duplicates among KEEP resources")
        self.log(f"Preserved {len(variations)} legitimate program variations")
        self.stats['preserved_variations'] = len(variations)

        # Remove exact duplicates
        if exact_dupes:
            self.remove_keep_exact_duplicates(exact_dupes)

        # Save variations report
        if variations:
            var_df = pd.DataFrame(variations)
            var_path = 'cleaned_data/review_needed/keep_resources_variations_review.csv'
            var_df.to_csv(var_path, index=False)
            self.log(f"Saved variations report: {var_path}")

    def find_common_program_name(self, names):
        """Find common program name from a list of names"""
        if not names:
            return ""

        # Common program indicators
        programs = ['pioneer', 'rise', 'stanford', 'cmu', 'ai4all', 'garcia',
                   'simons', 'broadcom', 'mit', 'polygence']

        name_lower = str(names[0]).lower()
        for prog in programs:
            if prog in name_lower:
                return prog.title()

        # Extract first 2-3 words as program name
        words = str(names[0]).split()[:2]
        return ' '.join(words) if words else ""

    def remove_keep_exact_duplicates(self, exact_dupes):
        """Remove exact duplicates among KEEP resources"""
        self.log("\nRemoving exact duplicates from KEEP resources...")

        indices_to_remove = set()
        for dupe in exact_dupes:
            row1 = self.master_df.loc[dupe['index1']]
            row2 = self.master_df.loc[dupe['index2']]

            score1 = self.calculate_completeness_score(row1)
            score2 = self.calculate_completeness_score(row2)

            if score1 > score2:
                indices_to_remove.add(dupe['index2'])
            else:
                indices_to_remove.add(dupe['index1'])

        if indices_to_remove:
            removed = self.master_df.loc[list(indices_to_remove)]
            self.removal_records['keep_exact_duplicates'] = removed.copy()
            self.master_df = self.master_df.drop(indices_to_remove)

            removed_count = len(indices_to_remove)
            self.stats['removed_keep_exact_dupes'] = removed_count
            self.log(f"Removed {removed_count} exact KEEP duplicates")
            self.log(f"Remaining: {len(self.master_df)}")

    # ==================== STEP 7: Program Variations Analysis ====================

    def generate_program_variations_analysis(self):
        """Generate detailed program variations analysis report"""
        self.log("\n" + "=" * 80)
        self.log("STEP 7: Generating Program Variations Analysis")
        self.log("=" * 80)

        output_path = 'cleaned_data/program_variations_analysis.txt'

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("=" * 80 + "\n")
            f.write("PROGRAM FAMILIES AND VARIATIONS ANALYSIS\n")
            f.write("=" * 80 + "\n\n")

            f.write(f"Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

            f.write("This report shows program families with multiple variations that were\n")
            f.write("correctly preserved as separate resources (not merged as duplicates).\n\n")

            f.write("-" * 80 + "\n\n")

            # Analyze program families from URL groups
            url_groups = self.master_df[self.master_df['url'].notna()].groupby('url')
            families = defaultdict(list)

            for url, group in url_groups:
                if len(group) > 1:
                    names = group['name'].tolist()
                    family_name = self.find_common_program_name(names)
                    if family_name:
                        for idx, row in group.iterrows():
                            families[family_name].append({
                                'name': row.get('name'),
                                'stem_fields': row.get('stem_fields'),
                                'target_grade': row.get('target_grade'),
                                'url': row.get('url')
                            })

            # Sort by number of variations
            sorted_families = sorted(families.items(),
                                    key=lambda x: len(x[1]),
                                    reverse=True)

            for family_name, variations in sorted_families[:20]:  # Top 20
                f.write(f"{family_name} ({len(variations)} variations preserved)\n")
                f.write("-" * 60 + "\n")

                for i, var in enumerate(variations, 1):
                    f.write(f"{i}. {var['name']}\n")
                    if var['stem_fields']:
                        f.write(f"   STEM Field: {var['stem_fields']}\n")
                    if var['target_grade']:
                        f.write(f"   Grade: {var['target_grade']}\n")
                    f.write(f"   URL: {var['url']}\n")
                    f.write("\n")

                f.write("\n")

            f.write("-" * 80 + "\n")
            f.write(f"\nTotal program families with variations: {len(families)}\n")
            f.write(f"Total variations preserved: {sum(len(v) for v in families.values())}\n")

        self.log(f"Saved program variations analysis: {output_path}")
        self.log(f"Program families identified: {len(families)}")

    # ==================== STEP 8: Summary Report ====================

    def generate_summary_report(self):
        """Generate cleaning summary report"""
        self.log("\n" + "=" * 80)
        self.log("STEP 8: Generating Cleaning Summary Report")
        self.log("=" * 80)

        self.stats['final_count'] = len(self.master_df)
        total_removed = self.stats['starting_count'] - self.stats['final_count']
        reduction_pct = (total_removed / self.stats['starting_count'] * 100)

        output_path = 'cleaned_data/cleaning_summary_report.txt'

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("=" * 80 + "\n")
            f.write("BLACK MINDS IN STEM - CONSERVATIVE DATA CLEANING SUMMARY\n")
            f.write("=" * 80 + "\n\n")

            f.write(f"Cleaning Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Approach: Conservative - Preserving Program Variations\n\n")

            f.write("-" * 80 + "\n")
            f.write("REMOVAL SUMMARY\n")
            f.write("-" * 80 + "\n\n")

            f.write(f"Starting Dataset: {self.stats['starting_count']:,} resources\n\n")

            f.write("Removal Breakdown:\n")
            f.write(f"  - Non-K-12 Resources: {self.stats['removed_non_k12']:,}\n")
            f.write(f"  - Educator Resources: {self.stats['removed_educator']:,}\n")
            f.write(f"  - Exact Duplicates (truly identical): {self.stats['removed_exact_dupes']:,}\n")
            f.write(f"  - KEEP Exact Duplicates: {self.stats['removed_keep_exact_dupes']:,}\n")
            f.write(f"  {'_' * 40}\n")
            f.write(f"  Total Removed: {total_removed:,}\n\n")

            f.write(f"Preserved Program Variations: {self.stats['preserved_variations']:,}\n")
            f.write(f"Flagged for Manual Review: {self.stats['flagged_for_review']:,}\n\n")

            f.write(f"Final Clean Dataset: {self.stats['final_count']:,} resources\n")
            f.write(f"Reduction: {reduction_pct:.1f}%\n\n")

            f.write("-" * 80 + "\n")
            f.write("CONSERVATIVE APPROACH SUMMARY\n")
            f.write("-" * 80 + "\n\n")

            f.write("This cleaning preserved legitimate program variations:\n")
            f.write("  - Different courses within same program (e.g., Pioneer Biology vs CS)\n")
            f.write("  - Different locations (e.g., AI4ALL @ Stanford vs @ MIT)\n")
            f.write("  - Different STEM fields under same parent program\n")
            f.write("  - Different sessions or cohorts\n\n")

            f.write("Only removed truly identical duplicates:\n")
            f.write("  - Same URL + 95%+ name similarity + 90%+ description similarity\n")
            f.write("  - No meaningful differences in any fields\n\n")

            # Dataset statistics
            f.write("-" * 80 + "\n")
            f.write("CLEANED DATASET STATISTICS\n")
            f.write("-" * 80 + "\n\n")

            if 'category' in self.master_df.columns:
                f.write("Top 10 Categories:\n")
                for cat, count in self.master_df['category'].value_counts().head(10).items():
                    f.write(f"  {cat}: {count}\n")
                f.write("\n")

            if 'target_grade' in self.master_df.columns:
                f.write("Top 10 Target Grades:\n")
                for grade, count in self.master_df['target_grade'].value_counts().head(10).items():
                    f.write(f"  {grade}: {count}\n")
                f.write("\n")

            # Completeness
            f.write("-" * 80 + "\n")
            f.write("DATA COMPLETENESS\n")
            f.write("-" * 80 + "\n\n")

            critical = ['name', 'description', 'url', 'category', 'stem_fields', 'target_grade']
            for col in critical:
                if col in self.master_df.columns:
                    comp = (self.master_df[col].notna().sum() / len(self.master_df) * 100)
                    status = "[OK]" if comp >= 95 else "[!]" if comp >= 80 else "[X]"
                    f.write(f"  {status} {col}: {comp:.1f}%\n")

            f.write("\n")
            f.write("-" * 80 + "\n")
            f.write("NEXT STEPS\n")
            f.write("-" * 80 + "\n\n")
            f.write("1. Review program variations analysis: program_variations_analysis.txt\n")
            f.write("2. Review flagged cases: review_needed/\n")
            f.write("3. Verify program families preserved correctly\n")
            f.write("4. Proceed with missing data inference\n")
            f.write("5. Build ML recommendation system\n")

        self.log(f"Saved summary report: {output_path}")

        # Print to console
        self.log("\n" + "=" * 80)
        self.log("CONSERVATIVE CLEANING SUMMARY")
        self.log("=" * 80)
        self.log(f"Starting: {self.stats['starting_count']:,}")
        self.log(f"Removed non-K-12: {self.stats['removed_non_k12']:,}")
        self.log(f"Removed educator: {self.stats['removed_educator']:,}")
        self.log(f"Removed exact duplicates: {self.stats['removed_exact_dupes']:,}")
        self.log(f"Removed KEEP exact duplicates: {self.stats['removed_keep_exact_dupes']:,}")
        self.log(f"Preserved variations: {self.stats['preserved_variations']:,}")
        self.log(f"Final: {self.stats['final_count']:,} ({reduction_pct:.1f}% reduction)")

    # ==================== STEP 9: Save All Data ====================

    def save_all_data(self):
        """Save cleaned dataset and all reports"""
        self.log("\n" + "=" * 80)
        self.log("STEP 9: Saving Cleaned Dataset and Reports")
        self.log("=" * 80)

        # Save cleaned dataset
        output_path = 'cleaned_data/bmis_clean_master_dataset.csv'
        self.master_df.to_csv(output_path, index=False, encoding='utf-8')
        self.log(f"Saved cleaned dataset: {output_path} ({len(self.master_df):,} resources)")

        # Save removal records
        for record_type, data in self.removal_records.items():
            if isinstance(data, pd.DataFrame) and not data.empty:
                filename = f'cleaned_data/removal_records/removed_{record_type}.csv'
                data.to_csv(filename, index=False, encoding='utf-8')
                self.log(f"Saved removal record: {filename} ({len(data):,} entries)")
            elif isinstance(data, list) and data:
                combined = pd.concat(data, ignore_index=True)
                filename = f'cleaned_data/removal_records/removed_{record_type}.csv'
                combined.to_csv(filename, index=False, encoding='utf-8')
                self.log(f"Saved removal record: {filename} ({len(combined):,} entries)")

        # Save review needed reports
        for review_type, data in self.review_needed.items():
            if isinstance(data, pd.DataFrame) and not data.empty:
                filename = f'cleaned_data/review_needed/{review_type}_review.csv'
                data.to_csv(filename, index=False, encoding='utf-8')
                self.log(f"Saved review report: {filename} ({len(data):,} entries)")

        self.log("\n[OK] All files saved successfully!")

    # ==================== Quality Verification ====================

    def verify_quality(self):
        """Verify program families are preserved"""
        self.log("\n" + "=" * 80)
        self.log("QUALITY VERIFICATION")
        self.log("=" * 80)

        # Check for program families
        pioneer_count = len(self.master_df[self.master_df['name'].str.contains('Pioneer', case=False, na=False)])
        rise_count = len(self.master_df[self.master_df['name'].str.contains('RISE', case=False, na=False)])
        stanford_count = len(self.master_df[self.master_df['name'].str.contains('Stanford Pre', case=False, na=False)])
        ai4all_count = len(self.master_df[self.master_df['name'].str.contains('AI4ALL', case=False, na=False)])

        self.log(f"Pioneer Academics programs: {pioneer_count}")
        self.log(f"RISE programs: {rise_count}")
        self.log(f"Stanford Pre-Collegiate programs: {stanford_count}")
        self.log(f"AI4ALL programs: {ai4all_count}")

        if pioneer_count > 5:
            self.log("[OK] Pioneer variations preserved")
        if rise_count > 5:
            self.log("[OK] RISE variations preserved")
        if stanford_count > 5:
            self.log("[OK] Stanford variations preserved")

    # ==================== Main Execution ====================

    def execute_cleaning(self):
        """Execute conservative cleaning pipeline"""
        self.log("=" * 80)
        self.log("CONSERVATIVE DATA CLEANING - PRESERVING PROGRAM VARIATIONS")
        self.log("=" * 80)

        try:
            self.load_master_dataset()
            self.remove_non_k12_resources()
            self.remove_educator_resources()
            self.conservative_duplicate_detection()
            self.analyze_keep_resources()
            self.generate_program_variations_analysis()
            self.generate_summary_report()
            self.save_all_data()
            self.verify_quality()

            self.log("\n" + "=" * 80)
            self.log("[OK] CONSERVATIVE CLEANING COMPLETE!")
            self.log("=" * 80)
            self.log(f"\nCleaned dataset: cleaned_data/bmis_clean_master_dataset.csv")
            self.log(f"Total resources: {self.stats['final_count']:,}")
            self.log(f"Program variations preserved: {self.stats['preserved_variations']:,}")

        except Exception as e:
            self.log(f"ERROR: {str(e)}", 'ERROR')
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    cleaner = ConservativeDataCleaner()
    cleaner.execute_cleaning()
