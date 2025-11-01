#!/usr/bin/env python3
"""
Black Minds in STEM - Data Cleaning Execution Script
Executes cleaning based on manual review decisions from data_quality_reports/
Produces clean master dataset ready for ML pipeline
"""

import os
import glob
import pandas as pd
import numpy as np
from datetime import datetime
from collections import defaultdict
import warnings
warnings.filterwarnings('ignore')

class DataCleaner:
    """Executes data cleaning based on manual review decisions"""

    def __init__(self):
        self.directories = ['Data', 'Scrapers/data', 'Scrapers/scrapers/data']
        self.master_df = None
        self.cleaned_df = None
        self.removal_records = {
            'non_k12': [],
            'educator': [],
            'exact_duplicates': [],
            'keep_duplicates': []
        }
        self.stats = {
            'starting_count': 0,
            'removed_non_k12': 0,
            'removed_educator': 0,
            'removed_exact_dupes': 0,
            'removed_keep_dupes': 0,
            'final_count': 0
        }

        # Create output directories
        os.makedirs('cleaned_data', exist_ok=True)
        os.makedirs('cleaned_data/removal_records', exist_ok=True)

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
        failed_files = []

        for directory in self.directories:
            if not os.path.exists(directory):
                self.log(f"WARNING: Directory not found: {directory}", 'WARN')
                continue

            csv_files = glob.glob(os.path.join(directory, "*.csv"))
            self.log(f"Loading {len(csv_files)} CSV files from {directory}")

            for csv_file in csv_files:
                try:
                    # Try UTF-8 first
                    df = pd.read_csv(csv_file, encoding='utf-8')
                    df['file_source'] = os.path.basename(csv_file)
                    df['directory_source'] = directory
                    all_dfs.append(df)
                except UnicodeDecodeError:
                    try:
                        # Try latin-1 as fallback
                        df = pd.read_csv(csv_file, encoding='latin-1')
                        df['file_source'] = os.path.basename(csv_file)
                        df['directory_source'] = directory
                        all_dfs.append(df)
                    except Exception as e:
                        failed_files.append({'file': csv_file, 'error': str(e)})
                except Exception as e:
                    failed_files.append({'file': csv_file, 'error': str(e)})

        if not all_dfs:
            raise ValueError("No CSV files could be loaded!")

        # Combine all dataframes
        self.master_df = pd.concat(all_dfs, ignore_index=True)
        self.stats['starting_count'] = len(self.master_df)

        self.log(f"Successfully loaded {len(all_dfs)} files")
        self.log(f"Total resources in master dataset: {len(self.master_df)}")

        if failed_files:
            self.log(f"Failed to load {len(failed_files)} files", 'WARN')

        # Load review files
        self.load_review_files()

        return self.master_df

    def load_review_files(self):
        """Load manual review files from data_quality_reports/"""
        self.log("\nLoading manual review files...")

        # Load non-K-12 review
        non_k12_path = 'data_quality_reports/flagged_non_k12_resources.csv'
        if os.path.exists(non_k12_path):
            self.non_k12_review = pd.read_csv(non_k12_path)
            # Clean up column names (remove extra spaces/unnamed columns)
            self.non_k12_review.columns = [col.strip() for col in self.non_k12_review.columns]
            # Check if Decision or Decisions column exists
            if 'Decision' in self.non_k12_review.columns:
                decision_col = 'Decision'
            elif 'Decisions' in self.non_k12_review.columns:
                decision_col = 'Decisions'
            else:
                self.log("WARNING: No Decision/Decisions column found in non-K-12 review", 'WARN')
                decision_col = None

            if decision_col:
                self.non_k12_review['decision_clean'] = self.non_k12_review[decision_col].astype(str).str.strip().str.upper()
                # Replace various blank representations with empty string
                self.non_k12_review['decision_clean'] = self.non_k12_review['decision_clean'].replace(
                    ['NAN', 'NONE', ''], ''
                )

            self.log(f"Loaded {len(self.non_k12_review)} non-K-12 flagged resources")
        else:
            self.log("WARNING: Non-K-12 review file not found", 'WARN')
            self.non_k12_review = pd.DataFrame()

        # Load educator resources review
        educator_path = 'data_quality_reports/flagged_educator_resources.csv'
        if os.path.exists(educator_path):
            self.educator_review = pd.read_csv(educator_path)
            self.log(f"Loaded {len(self.educator_review)} educator resources")
        else:
            self.log("WARNING: Educator review file not found", 'WARN')
            self.educator_review = pd.DataFrame()

        # Load duplicates
        dupes_path = 'data_quality_reports/duplicate_resources_analysis.csv'
        if os.path.exists(dupes_path):
            self.duplicates_review = pd.read_csv(dupes_path)
            self.log(f"Loaded {len(self.duplicates_review)} duplicate groups")
        else:
            self.log("WARNING: Duplicates review file not found", 'WARN')
            self.duplicates_review = pd.DataFrame()

    # ==================== STEP 2: Remove Non-K-12 Resources ====================

    def remove_non_k12_resources(self):
        """Remove non-K-12 resources based on manual review decisions"""
        self.log("\n" + "=" * 80)
        self.log("STEP 2: Removing Non-K-12 Resources")
        self.log("=" * 80)

        if self.non_k12_review.empty:
            self.log("No non-K-12 review data to process")
            return

        # Check if we have the decision column
        if 'decision_clean' not in self.non_k12_review.columns:
            self.log("No decisions found in non-K-12 review file", 'WARN')
            return

        # Count decisions
        total_flagged = len(self.non_k12_review)
        keep_count = (self.non_k12_review['decision_clean'] == 'KEEP').sum()
        remove_count = total_flagged - keep_count

        self.log(f"Total flagged: {total_flagged}")
        self.log(f"Marked as KEEP: {keep_count}")
        self.log(f"To be removed (blank or REMOVE): {remove_count}")

        # Get resources to remove (decision is not KEEP)
        to_remove = self.non_k12_review[self.non_k12_review['decision_clean'] != 'KEEP'].copy()

        if len(to_remove) == 0:
            self.log("No non-K-12 resources to remove")
            return

        # Create removal list matching by name AND source
        removal_keys = set()
        for idx, row in to_remove.iterrows():
            name = str(row.get('name', '')).strip()
            source = str(row.get('file_source', '')).strip()
            if name and source:
                removal_keys.add((name, source))

        self.log(f"Created removal list with {len(removal_keys)} unique resource identifiers")

        # Find matching resources in master dataset
        before_count = len(self.master_df)
        removed_resources = []

        for name, file_source in removal_keys:
            matching = self.master_df[
                (self.master_df['name'].astype(str).str.strip() == name) &
                (self.master_df['file_source'].astype(str).str.strip() == file_source)
            ]

            if len(matching) > 0:
                removed_resources.append(matching.copy())
                # Remove from master dataset
                self.master_df = self.master_df[
                    ~((self.master_df['name'].astype(str).str.strip() == name) &
                      (self.master_df['file_source'].astype(str).str.strip() == file_source))
                ]

        # Combine removed resources
        if removed_resources:
            self.removal_records['non_k12'] = pd.concat(removed_resources, ignore_index=True)

        after_count = len(self.master_df)
        actual_removed = before_count - after_count
        self.stats['removed_non_k12'] = actual_removed

        self.log(f"Removed {actual_removed} non-K-12 resources")
        self.log(f"Remaining resources: {after_count}")

    # ==================== STEP 3: Remove Educator Resources ====================

    def remove_educator_resources(self):
        """Remove all educator resources"""
        self.log("\n" + "=" * 80)
        self.log("STEP 3: Removing Educator Resources")
        self.log("=" * 80)

        if self.educator_review.empty:
            self.log("No educator resources to remove")
            return

        # Create removal list matching by name AND file_source
        removal_keys = set()
        for idx, row in self.educator_review.iterrows():
            name = str(row.get('name', '')).strip()
            source = str(row.get('file_source', '')).strip()
            if name and source:
                removal_keys.add((name, source))

        self.log(f"Removing {len(removal_keys)} educator resources")

        # Find matching resources in master dataset
        before_count = len(self.master_df)
        removed_resources = []

        for name, file_source in removal_keys:
            matching = self.master_df[
                (self.master_df['name'].astype(str).str.strip() == name) &
                (self.master_df['file_source'].astype(str).str.strip() == file_source)
            ]

            if len(matching) > 0:
                removed_resources.append(matching.copy())
                # Remove from master dataset
                self.master_df = self.master_df[
                    ~((self.master_df['name'].astype(str).str.strip() == name) &
                      (self.master_df['file_source'].astype(str).str.strip() == file_source))
                ]

        # Combine removed resources
        if removed_resources:
            self.removal_records['educator'] = pd.concat(removed_resources, ignore_index=True)

        after_count = len(self.master_df)
        actual_removed = before_count - after_count
        self.stats['removed_educator'] = actual_removed

        self.log(f"Removed {actual_removed} educator resources")
        self.log(f"Remaining resources: {after_count}")

    # ==================== STEP 4: Handle Exact Duplicates ====================

    def calculate_completeness_score(self, row):
        """Calculate completeness score for a resource"""
        # Count non-null values
        non_null_count = row.notna().sum()

        # Add bonus for description length
        desc_length = len(str(row.get('description', '')))

        # Add bonus for having URL
        has_url = 1 if pd.notna(row.get('url')) and str(row.get('url')).strip() != '' else 0

        return non_null_count + (desc_length / 100) + (has_url * 2)

    def remove_exact_duplicates(self):
        """Remove exact duplicates keeping most complete version"""
        self.log("\n" + "=" * 80)
        self.log("STEP 4: Handling Exact Duplicates")
        self.log("=" * 80)

        if self.duplicates_review.empty:
            self.log("No duplicate groups to process")
            return

        self.log(f"Processing {len(self.duplicates_review)} duplicate groups")

        removed_count = 0
        removed_resources = []

        for idx, dupe_group in self.duplicates_review.iterrows():
            dupe_type = dupe_group.get('duplicate_type', '')
            name = str(dupe_group.get('name', '')).strip()

            # Find all resources matching this duplicate group
            if 'Same name and URL' in dupe_type:
                url = str(dupe_group.get('url', '')).strip()
                matching = self.master_df[
                    (self.master_df['name'].astype(str).str.strip() == name) &
                    (self.master_df['url'].astype(str).str.strip() == url)
                ]
            elif 'Same name, source' in dupe_type:
                source_val = str(dupe_group.get('source', '')).strip()
                matching = self.master_df[
                    (self.master_df['name'].astype(str).str.strip() == name) &
                    (self.master_df['source'].astype(str).str.strip() == source_val)
                ]
            else:
                continue

            if len(matching) <= 1:
                continue  # No duplicates found in current dataset

            # Calculate completeness scores
            scores = matching.apply(self.calculate_completeness_score, axis=1)

            # Keep the one with highest score
            best_idx = scores.idxmax()

            # Remove all others
            to_remove = matching[matching.index != best_idx]

            if len(to_remove) > 0:
                removed_resources.append(to_remove.copy())
                # Remove from master dataset
                self.master_df = self.master_df.drop(to_remove.index)
                removed_count += len(to_remove)

        # Combine removed resources
        if removed_resources:
            self.removal_records['exact_duplicates'] = pd.concat(removed_resources, ignore_index=True)

        self.stats['removed_exact_dupes'] = removed_count

        self.log(f"Removed {removed_count} duplicate entries")
        self.log(f"Remaining resources: {len(self.master_df)}")

    # ==================== STEP 5: Identify Additional Duplicates ====================

    def identify_keep_resource_duplicates(self):
        """Identify duplicates among resources marked as KEEP"""
        self.log("\n" + "=" * 80)
        self.log("STEP 5: Identifying Additional Duplicates Among KEEP Resources")
        self.log("=" * 80)

        # Get list of KEEP resources
        if 'decision_clean' in self.non_k12_review.columns:
            keep_resources = self.non_k12_review[
                self.non_k12_review['decision_clean'] == 'KEEP'
            ].copy()

            self.log(f"Analyzing {len(keep_resources)} KEEP resources for duplicates")

            # Create set of keep resource identifiers
            keep_keys = set()
            for idx, row in keep_resources.iterrows():
                name = str(row.get('name', '')).strip()
                if name:
                    keep_keys.add(name)

            # Filter master dataset to only KEEP resources
            keep_df = self.master_df[
                self.master_df['name'].astype(str).str.strip().isin(keep_keys)
            ].copy()

            self.log(f"Found {len(keep_df)} KEEP resources in master dataset")
        else:
            # If no decision column, analyze all remaining resources
            keep_df = self.master_df.copy()
            self.log(f"Analyzing all {len(keep_df)} remaining resources for duplicates")

        # Find duplicates using multiple methods
        duplicates_found = []

        # Method 1: Exact name + URL duplicates
        self.log("\nMethod 1: Finding exact name + URL duplicates...")
        url_dupes = keep_df.groupby(['name', 'url']).size()
        url_dupes = url_dupes[url_dupes > 1]

        for (name, url), count in url_dupes.items():
            if pd.notna(url) and str(url).strip() != '':
                matching = keep_df[
                    (keep_df['name'] == name) &
                    (keep_df['url'] == url)
                ]

                for idx, row in matching.iterrows():
                    duplicates_found.append({
                        'duplicate_type': 'Exact name + URL',
                        'duplicate_key': f"{name}|{url}",
                        'name': name,
                        'url': url,
                        'source': row.get('source', ''),
                        'file_source': row.get('file_source', ''),
                        'description': str(row.get('description', ''))[:100],
                        'index': idx
                    })

        self.log(f"Found {len([d for d in duplicates_found if d['duplicate_type'] == 'Exact name + URL'])} name+URL duplicates")

        # Method 2: Exact name + source duplicates (for resources without URLs)
        self.log("\nMethod 2: Finding exact name + source duplicates...")
        source_dupes = keep_df.groupby(['name', 'source']).size()
        source_dupes = source_dupes[source_dupes > 1]

        for (name, source), count in source_dupes.items():
            if pd.notna(source) and str(source).strip() != '':
                matching = keep_df[
                    (keep_df['name'] == name) &
                    (keep_df['source'] == source)
                ]

                # Check if these are already in url duplicates
                existing_keys = set(d['duplicate_key'] for d in duplicates_found)

                for idx, row in matching.iterrows():
                    key = f"{name}|{source}"
                    if key not in existing_keys:
                        duplicates_found.append({
                            'duplicate_type': 'Exact name + source',
                            'duplicate_key': key,
                            'name': name,
                            'url': row.get('url', ''),
                            'source': source,
                            'file_source': row.get('file_source', ''),
                            'description': str(row.get('description', ''))[:100],
                            'index': idx
                        })

        self.log(f"Found {len([d for d in duplicates_found if d['duplicate_type'] == 'Exact name + source'])} name+source duplicates")

        # Method 3: Same URL, different names
        self.log("\nMethod 3: Finding same URL with different names...")
        url_groups = keep_df.groupby('url')
        for url, group in url_groups:
            if pd.notna(url) and str(url).strip() != '' and len(group) > 1:
                unique_names = group['name'].nunique()
                if unique_names > 1:  # Different names for same URL
                    for idx, row in group.iterrows():
                        key = f"URL:{url}"
                        duplicates_found.append({
                            'duplicate_type': 'Same URL, different names',
                            'duplicate_key': key,
                            'name': row.get('name', ''),
                            'url': url,
                            'source': row.get('source', ''),
                            'file_source': row.get('file_source', ''),
                            'description': str(row.get('description', ''))[:100],
                            'index': idx
                        })

        self.log(f"Found {len([d for d in duplicates_found if d['duplicate_type'] == 'Same URL, different names'])} same-URL duplicates")

        # Save duplicate report
        if duplicates_found:
            dupes_df = pd.DataFrame(duplicates_found)
            output_path = 'data_quality_reports/keep_resources_duplicates_found.csv'
            dupes_df.to_csv(output_path, index=False)
            self.log(f"\nSaved duplicate report to: {output_path}")
            self.log(f"Total duplicates found among KEEP resources: {len(duplicates_found)}")

            # Count unique duplicate groups
            unique_groups = dupes_df['duplicate_key'].nunique()
            self.log(f"Unique duplicate groups: {unique_groups}")

            return dupes_df
        else:
            self.log("\nNo duplicates found among KEEP resources")
            return pd.DataFrame()

    # ==================== STEP 6: Remove Duplicates Among KEEP Resources ====================

    def remove_keep_resource_duplicates(self, duplicates_df):
        """Remove duplicates identified among KEEP resources"""
        self.log("\n" + "=" * 80)
        self.log("STEP 6: Removing Duplicates Among KEEP Resources")
        self.log("=" * 80)

        if duplicates_df.empty:
            self.log("No KEEP resource duplicates to remove")
            return

        # Group by duplicate_key
        duplicate_groups = duplicates_df.groupby('duplicate_key')
        self.log(f"Processing {len(duplicate_groups)} duplicate groups")

        removed_count = 0
        removed_resources = []

        for key, group in duplicate_groups:
            if len(group) <= 1:
                continue

            # Get full resource data for these duplicates
            indices = group['index'].tolist()
            matching = self.master_df.loc[self.master_df.index.isin(indices)]

            if len(matching) <= 1:
                continue  # Already removed or not found

            # Calculate completeness scores
            scores = matching.apply(self.calculate_completeness_score, axis=1)

            # Keep the one with highest score
            best_idx = scores.idxmax()

            # Remove all others
            to_remove = matching[matching.index != best_idx]

            if len(to_remove) > 0:
                removed_resources.append(to_remove.copy())
                # Remove from master dataset
                self.master_df = self.master_df.drop(to_remove.index)
                removed_count += len(to_remove)

        # Combine removed resources
        if removed_resources:
            self.removal_records['keep_duplicates'] = pd.concat(removed_resources, ignore_index=True)

        self.stats['removed_keep_dupes'] = removed_count

        self.log(f"Removed {removed_count} duplicate KEEP resources")
        self.log(f"Remaining resources: {len(self.master_df)}")

    # ==================== STEP 7: Generate Summary Report ====================

    def generate_summary_report(self):
        """Generate comprehensive cleaning summary report"""
        self.log("\n" + "=" * 80)
        self.log("STEP 7: Generating Cleaning Summary Report")
        self.log("=" * 80)

        self.stats['final_count'] = len(self.master_df)
        total_removed = (self.stats['starting_count'] - self.stats['final_count'])
        reduction_pct = (total_removed / self.stats['starting_count'] * 100)

        # Create summary report
        output_path = 'cleaned_data/cleaning_summary_report.txt'

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("=" * 80 + "\n")
            f.write("BLACK MINDS IN STEM - DATA CLEANING SUMMARY REPORT\n")
            f.write("=" * 80 + "\n\n")

            f.write(f"Cleaning Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

            # Removal Summary
            f.write("-" * 80 + "\n")
            f.write("REMOVAL SUMMARY\n")
            f.write("-" * 80 + "\n\n")

            f.write(f"Starting Dataset: {self.stats['starting_count']:,} resources\n\n")

            f.write("Removal Breakdown:\n")
            f.write(f"  - Non-K-12 Resources: {self.stats['removed_non_k12']:,}\n")
            f.write(f"  - Educator Resources: {self.stats['removed_educator']:,}\n")
            f.write(f"  - Exact Duplicates: {self.stats['removed_exact_dupes']:,}\n")
            f.write(f"  - KEEP Resource Duplicates: {self.stats['removed_keep_dupes']:,}\n")
            f.write(f"  {'_' * 40}\n")
            f.write(f"  Total Removed: {total_removed:,}\n\n")

            f.write(f"Final Clean Dataset: {self.stats['final_count']:,} resources\n")
            f.write(f"Reduction: {reduction_pct:.1f}%\n\n")

            # Cleaned Dataset Statistics
            f.write("-" * 80 + "\n")
            f.write("CLEANED DATASET STATISTICS\n")
            f.write("-" * 80 + "\n\n")

            # Category distribution
            if 'category' in self.master_df.columns:
                f.write("Top 10 Categories:\n")
                cat_dist = self.master_df['category'].value_counts().head(10)
                for cat, count in cat_dist.items():
                    f.write(f"  {cat}: {count}\n")
                f.write("\n")

            # Target grade distribution
            if 'target_grade' in self.master_df.columns:
                f.write("Top 10 Target Grades:\n")
                grade_dist = self.master_df['target_grade'].value_counts().head(10)
                for grade, count in grade_dist.items():
                    f.write(f"  {grade}: {count}\n")
                f.write("\n")

            # Top sources
            if 'source' in self.master_df.columns:
                f.write("Top 10 Sources:\n")
                source_dist = self.master_df['source'].value_counts().head(10)
                for source, count in source_dist.items():
                    f.write(f"  {source}: {count}\n")
                f.write("\n")

            # Data Completeness
            f.write("-" * 80 + "\n")
            f.write("DATA COMPLETENESS AFTER CLEANING\n")
            f.write("-" * 80 + "\n\n")

            # Critical columns
            critical_cols = [
                'name', 'description', 'url', 'source', 'category', 'stem_fields',
                'target_grade', 'cost', 'location_type', 'time_commitment'
            ]

            f.write("Critical Columns:\n")
            for col in critical_cols:
                if col in self.master_df.columns:
                    completeness = (self.master_df[col].notna().sum() / len(self.master_df) * 100)
                    if completeness >= 95:
                        status = "[OK]"
                    elif completeness >= 80:
                        status = "[!]"
                    else:
                        status = "[X]"
                    f.write(f"  {status} {col}: {completeness:.1f}%\n")

            f.write("\n")

            # All columns
            f.write("All Columns Completeness:\n")
            for col in self.master_df.columns:
                if col not in ['file_source', 'directory_source']:
                    completeness = (self.master_df[col].notna().sum() / len(self.master_df) * 100)
                    f.write(f"  {col}: {completeness:.1f}%\n")

            f.write("\n")

            # Next Steps
            f.write("-" * 80 + "\n")
            f.write("NEXT STEPS\n")
            f.write("-" * 80 + "\n\n")
            f.write("1. Review cleaned dataset: cleaned_data/bmis_clean_master_dataset.csv\n")
            f.write("2. Review removal records in cleaned_data/removal_records/\n")
            f.write("3. Proceed with missing data inference for ML pipeline\n")
            f.write("4. Build recommendation system with TF-IDF + K-Means clustering\n")

        self.log(f"Saved cleaning summary report to: {output_path}")

        # Print summary to console
        self.log("\n" + "=" * 80)
        self.log("CLEANING SUMMARY")
        self.log("=" * 80)
        self.log(f"Starting: {self.stats['starting_count']:,} resources")
        self.log(f"Removed non-K-12: {self.stats['removed_non_k12']:,}")
        self.log(f"Removed educator: {self.stats['removed_educator']:,}")
        self.log(f"Removed exact duplicates: {self.stats['removed_exact_dupes']:,}")
        self.log(f"Removed KEEP duplicates: {self.stats['removed_keep_dupes']:,}")
        self.log(f"Final: {self.stats['final_count']:,} resources ({reduction_pct:.1f}% reduction)")

    # ==================== STEP 8: Save Cleaned Dataset ====================

    def save_cleaned_data(self):
        """Save cleaned dataset and removal records"""
        self.log("\n" + "=" * 80)
        self.log("STEP 8: Saving Cleaned Dataset and Removal Records")
        self.log("=" * 80)

        # Save cleaned master dataset
        output_path = 'cleaned_data/bmis_clean_master_dataset.csv'
        self.master_df.to_csv(output_path, index=False, encoding='utf-8')
        self.log(f"Saved cleaned dataset: {output_path} ({len(self.master_df):,} resources)")

        # Save removal records
        for record_type, df in self.removal_records.items():
            if isinstance(df, pd.DataFrame) and not df.empty:
                filename = f'cleaned_data/removal_records/removed_{record_type}.csv'
                df.to_csv(filename, index=False, encoding='utf-8')
                self.log(f"Saved removal record: {filename} ({len(df):,} entries)")
            elif isinstance(df, list) and len(df) > 0:
                combined = pd.concat(df, ignore_index=True) if df else pd.DataFrame()
                if not combined.empty:
                    filename = f'cleaned_data/removal_records/removed_{record_type}.csv'
                    combined.to_csv(filename, index=False, encoding='utf-8')
                    self.log(f"Saved removal record: {filename} ({len(combined):,} entries)")

        self.log("\n[OK] All files saved successfully!")

    # ==================== Main Execution ====================

    def execute_cleaning(self):
        """Execute the complete cleaning pipeline"""
        self.log("=" * 80)
        self.log("BLACK MINDS IN STEM - DATA CLEANING EXECUTION")
        self.log("=" * 80)

        try:
            # Step 1: Load data
            self.load_master_dataset()

            # Step 2: Remove non-K-12 resources
            self.remove_non_k12_resources()

            # Step 3: Remove educator resources
            self.remove_educator_resources()

            # Step 4: Handle exact duplicates
            self.remove_exact_duplicates()

            # Step 5: Identify KEEP resource duplicates
            keep_dupes = self.identify_keep_resource_duplicates()

            # Step 6: Remove KEEP resource duplicates
            if not keep_dupes.empty:
                self.remove_keep_resource_duplicates(keep_dupes)

            # Step 7: Generate summary report
            self.generate_summary_report()

            # Step 8: Save cleaned data
            self.save_cleaned_data()

            self.log("\n" + "=" * 80)
            self.log("[OK] DATA CLEANING COMPLETE!")
            self.log("=" * 80)
            self.log(f"\nCleaned dataset ready: cleaned_data/bmis_clean_master_dataset.csv")
            self.log(f"Total resources: {self.stats['final_count']:,}")

        except Exception as e:
            self.log(f"ERROR: Cleaning failed: {str(e)}", 'ERROR')
            import traceback
            traceback.print_exc()

# ==================== Entry Point ====================

if __name__ == "__main__":
    cleaner = DataCleaner()
    cleaner.execute_cleaning()
