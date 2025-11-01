#!/usr/bin/env python3
"""
Comprehensive Data Quality Assessment for Black Minds in STEM
Analyzes 2,433+ K-12 STEM resources across 151+ CSV files
Generates detailed reports WITHOUT removing any data
"""

import os
import glob
import pandas as pd
import numpy as np
import re
from collections import Counter, defaultdict
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# For fuzzy string matching
try:
    from fuzzywuzzy import fuzz
    FUZZY_AVAILABLE = True
except ImportError:
    print("WARNING: fuzzywuzzy not installed. Installing for near-duplicate detection...")
    import subprocess
    subprocess.check_call(['pip', 'install', 'fuzzywuzzy', 'python-Levenshtein'])
    from fuzzywuzzy import fuzz
    FUZZY_AVAILABLE = True

# For visualizations
try:
    import matplotlib.pyplot as plt
    import seaborn as sns
    PLOT_AVAILABLE = True
except ImportError:
    print("WARNING: matplotlib/seaborn not installed. Skipping visualizations...")
    PLOT_AVAILABLE = False

class DataQualityAnalyzer:
    """Comprehensive data quality analyzer for K-12 STEM resources"""

    def __init__(self):
        self.directories = ['Data', 'Scrapers/data', 'Scrapers/scrapers/data']
        self.master_df = None
        self.issues = defaultdict(list)
        self.stats = {}
        self.reports = {}

        # Expected columns
        self.expected_columns = [
            'name', 'description', 'url', 'source', 'category', 'stem_fields',
            'target_grade', 'cost', 'location_type', 'time_commitment',
            'prerequisite_level', 'support_level', 'deadline',
            'financial_barrier_level', 'financial_aid_available',
            'family_income_consideration', 'hidden_costs_level', 'cost_category',
            'diversity_focus', 'underrepresented_friendly', 'first_gen_support',
            'cultural_competency',
            'rural_accessible', 'transportation_required', 'internet_dependency',
            'regional_availability', 'family_involvement_required',
            'peer_network_building', 'mentor_access_level'
        ]

        # Create output directory
        os.makedirs('data_quality_reports', exist_ok=True)

    def log(self, message):
        """Print timestamped log message"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        # Remove special characters for Windows compatibility
        message = message.replace('\u2713', '[OK]').replace('\u2717', '[X]').replace('\u26A0', '[!]')
        print(f"[{timestamp}] {message}")

    # ==================== PHASE 1: Data Loading ====================

    def load_all_csvs(self):
        """Load all CSV files from the three directories"""
        self.log("Phase 1: Loading all CSV files...")

        all_dfs = []
        failed_files = []
        encoding_issues = []

        for directory in self.directories:
            if not os.path.exists(directory):
                self.log(f"  WARNING: Directory not found: {directory}")
                continue

            csv_files = glob.glob(os.path.join(directory, "*.csv"))
            self.log(f"  Found {len(csv_files)} CSV files in {directory}")

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
                        encoding_issues.append(csv_file)
                    except Exception as e:
                        failed_files.append({'file': csv_file, 'error': str(e)})
                except Exception as e:
                    failed_files.append({'file': csv_file, 'error': str(e)})

        if not all_dfs:
            raise ValueError("No CSV files could be loaded!")

        # Combine all dataframes
        self.master_df = pd.concat(all_dfs, ignore_index=True)

        # Store stats
        self.stats['total_files'] = len(all_dfs)
        self.stats['total_resources'] = len(self.master_df)
        self.stats['failed_files'] = failed_files
        self.stats['encoding_issues'] = encoding_issues

        self.log(f"  [OK] Loaded {len(all_dfs)} files with {len(self.master_df)} total resources")
        if failed_files:
            self.log(f"  [!] Failed to load {len(failed_files)} files")
        if encoding_issues:
            self.log(f"  [!] Encoding issues in {len(encoding_issues)} files")

        return self.master_df

    def check_column_consistency(self):
        """Check if all CSV files have consistent columns"""
        self.log("Phase 1.2: Checking column consistency...")

        column_issues = []

        # Group by file and check columns
        for file_name in self.master_df['file_source'].unique():
            file_df = self.master_df[self.master_df['file_source'] == file_name]
            file_columns = set(file_df.columns) - {'file_source', 'directory_source'}
            expected_set = set(self.expected_columns)

            missing = expected_set - file_columns
            extra = file_columns - expected_set

            if missing or extra:
                column_issues.append({
                    'file': file_name,
                    'missing_columns': list(missing),
                    'extra_columns': list(extra)
                })

        self.issues['column_consistency'] = column_issues

        if column_issues:
            self.log(f"  [\!] Found column inconsistencies in {len(column_issues)} files")
        else:
            self.log(f"  [OK] All files have consistent columns")

    def generate_basic_statistics(self):
        """Generate basic statistics about the dataset"""
        self.log("Phase 1.3: Generating basic statistics...")

        stats = {}

        # Resources per directory
        stats['resources_per_directory'] = self.master_df['directory_source'].value_counts().to_dict()

        # Resources per file (top 10)
        stats['top_files_by_count'] = self.master_df['file_source'].value_counts().head(10).to_dict()

        # Distribution by category
        if 'category' in self.master_df.columns:
            stats['category_distribution'] = self.master_df['category'].value_counts().to_dict()

        # Distribution by source
        if 'source' in self.master_df.columns:
            stats['top_sources'] = self.master_df['source'].value_counts().head(20).to_dict()

        # Average description length
        if 'description' in self.master_df.columns:
            self.master_df['description_length'] = self.master_df['description'].astype(str).str.len()
            stats['avg_description_length'] = self.master_df['description_length'].mean()
            stats['min_description_length'] = self.master_df['description_length'].min()
            stats['max_description_length'] = self.master_df['description_length'].max()

        # Null counts per column
        null_counts = self.master_df.isnull().sum()
        stats['null_counts'] = null_counts[null_counts > 0].to_dict()

        self.stats['basic_statistics'] = stats
        self.log(f"  [OK] Generated basic statistics")

    # ==================== PHASE 2: K-12 Eligibility ====================

    def identify_non_k12_resources(self):
        """Identify resources that are NOT for K-12 students"""
        self.log("Phase 2.1: Identifying non-K-12 resources...")

        flagged_resources = []

        # Keywords indicating non-K-12
        college_keywords = [
            r'\bcollege student', r'\bundergraduate', r'\bgrad student', r'\bgraduate student',
            r'\bphd', r'\bmaster\'?s', r'\bdoctoral', r'\bpostdoc',
            r'\bcollege freshman', r'\bcollege sophomore', r'\bcollege junior', r'\bcollege senior',
            r'\buniversity student', r'\bcollegiate', r'\bpost-?secondary',
            r'\b18\+', r'\bages? 19', r'\bages? 20', r'\bages? 21', r'\bages? 22-',
            r'\bfaculty', r'\bprofessor', r'\binstructor', r'\beducator', r'\bteacher',
            r'\bprofessional development', r'\bcontinuing education', r'\bworking adult'
        ]

        # Keywords that are OK (high school seniors preparing for college)
        ok_keywords = [
            r'high school senior.*college', r'preparing for college',
            r'transitioning to college', r'college-?bound',
            r'rising college', r'incoming college'
        ]

        for idx, row in self.master_df.iterrows():
            name = str(row.get('name', '')).lower()
            description = str(row.get('description', '')).lower()
            target_grade = str(row.get('target_grade', '')).lower()

            combined_text = f"{name} {description} {target_grade}"

            # Check for OK keywords first
            is_ok = any(re.search(pattern, combined_text) for pattern in ok_keywords)
            if is_ok:
                continue

            # Check for college/non-K-12 keywords
            reasons = []
            confidence = 'LOW'

            for pattern in college_keywords:
                if re.search(pattern, combined_text):
                    reasons.append(f"Found: {pattern}")

            if reasons:
                # Determine confidence level
                if any(keyword in combined_text for keyword in ['undergraduate only', 'college students only', 'graduate student', 'phd', 'faculty', 'professor']):
                    confidence = 'HIGH'
                elif any(keyword in combined_text for keyword in ['college', 'undergraduate', '18+']):
                    confidence = 'MEDIUM'

                flagged_resources.append({
                    'file_source': row.get('file_source', ''),
                    'name': row.get('name', ''),
                    'description': row.get('description', '')[:200],
                    'target_grade': row.get('target_grade', ''),
                    'reason_flagged': '; '.join(reasons[:3]),
                    'confidence_level': confidence
                })

        self.issues['non_k12_resources'] = flagged_resources
        self.log(f"  [\!] Flagged {len(flagged_resources)} potentially non-K-12 resources")

    def identify_educator_resources(self):
        """Identify resources designed for educators, not students"""
        self.log("Phase 2.2: Identifying educator/teacher resources...")

        flagged_resources = []

        educator_keywords = [
            r'\bteacher professional development', r'\beducator training',
            r'\bteaching certification', r'\bclassroom resources for teachers',
            r'\bcurriculum for educators', r'\bfaculty fellowship',
            r'\binstructor program', r'\bpd credits', r'\bceu\b',
            r'\bteacher workshop', r'\beducator workshop',
            r'\bfor teachers', r'\bfor educators', r'\bfor instructors',
            r'\bteaching credential', r'\bteacher certification'
        ]

        for idx, row in self.master_df.iterrows():
            name = str(row.get('name', '')).lower()
            description = str(row.get('description', '')).lower()
            category = str(row.get('category', '')).lower()

            combined_text = f"{name} {description} {category}"

            reasons = []
            confidence = 'LOW'

            for pattern in educator_keywords:
                if re.search(pattern, combined_text):
                    reasons.append(f"Found: {pattern}")

            if reasons:
                # Higher confidence if multiple matches or in name/category
                if len(reasons) >= 2 or any(re.search(pattern, name) for pattern in educator_keywords):
                    confidence = 'HIGH'
                elif any(re.search(pattern, description) for pattern in educator_keywords):
                    confidence = 'MEDIUM'

                flagged_resources.append({
                    'file_source': row.get('file_source', ''),
                    'name': row.get('name', ''),
                    'description': row.get('description', '')[:200],
                    'reason_flagged': '; '.join(reasons[:3]),
                    'confidence_level': confidence
                })

        self.issues['educator_resources'] = flagged_resources
        self.log(f"  [\!] Flagged {len(flagged_resources)} potentially educator-focused resources")

    # ==================== PHASE 3: STEM Relevance ====================

    def identify_non_stem_resources(self):
        """Identify resources that are NOT clearly STEM-related"""
        self.log("Phase 3.1: Identifying non-STEM resources...")

        flagged_resources = []

        # Non-STEM keywords
        non_stem_keywords = [
            r'\bhumanities', r'\bliberal arts', r'\bsocial sciences?\b',
            r'\bbusiness administration', r'\bmarketing', r'\bfinance\b',
            r'\bart\b', r'\bmusic\b', r'\btheatre', r'\bdrama\b',
            r'\benglish literature', r'\bcreative writing',
            r'\bhistory\b', r'\bphilosophy', r'\blanguages?\b'
        ]

        # STEM-adjacent that should be included
        stem_ok_keywords = [
            r'\benvironmental', r'\bdata science', r'\bcomputational',
            r'\bbioethics', r'\bmedical', r'\bhealth', r'\bsteam\b',
            r'\bastronomy', r'\bgeology', r'\bmeteorology'
        ]

        for idx, row in self.master_df.iterrows():
            name = str(row.get('name', '')).lower()
            description = str(row.get('description', '')).lower()
            stem_fields = str(row.get('stem_fields', '')).lower()
            category = str(row.get('category', '')).lower()

            combined_text = f"{name} {description} {stem_fields} {category}"

            # Check if empty stem_fields
            reasons = []
            confidence = 'LOW'

            if pd.isna(row.get('stem_fields')) or stem_fields in ['', 'nan', 'none']:
                reasons.append("Empty stem_fields column")
                confidence = 'MEDIUM'

            # Check for STEM-adjacent keywords first (these are OK)
            is_stem_ok = any(re.search(pattern, combined_text) for pattern in stem_ok_keywords)

            # Check for non-STEM keywords
            if not is_stem_ok:
                for pattern in non_stem_keywords:
                    if re.search(pattern, combined_text):
                        reasons.append(f"Found: {pattern}")
                        confidence = 'MEDIUM'

            # Check for generic programs without STEM mention
            has_stem_mention = any(word in combined_text for word in [
                'stem', 'science', 'technology', 'engineering', 'math', 'computer',
                'biology', 'chemistry', 'physics', 'robotics', 'coding', 'programming'
            ])

            if not has_stem_mention and not reasons:
                reasons.append("No clear STEM field mentioned")
                confidence = 'LOW'

            if reasons:
                flagged_resources.append({
                    'file_source': row.get('file_source', ''),
                    'name': row.get('name', ''),
                    'description': row.get('description', '')[:200],
                    'stem_fields': row.get('stem_fields', ''),
                    'category': row.get('category', ''),
                    'reason_flagged': '; '.join(reasons[:3]),
                    'confidence_level': confidence
                })

        self.issues['non_stem_resources'] = flagged_resources
        self.log(f"  [\!] Flagged {len(flagged_resources)} potentially non-STEM resources")

    def validate_stem_field_consistency(self):
        """Check STEM field values for consistency"""
        self.log("Phase 3.2: Validating STEM field consistency...")

        if 'stem_fields' not in self.master_df.columns:
            return

        # Get all unique STEM field values
        stem_values = self.master_df['stem_fields'].dropna().unique()
        self.stats['unique_stem_fields'] = sorted([str(v) for v in stem_values])

        self.log(f"  [OK] Found {len(stem_values)} unique STEM field values")

    # ==================== PHASE 4: Duplicate Detection ====================

    def detect_exact_duplicates(self):
        """Detect exact duplicate resources"""
        self.log("Phase 4.1: Detecting exact duplicates...")

        duplicate_groups = []

        # Check for duplicates by name + url
        if 'url' in self.master_df.columns:
            name_url_dupes = self.master_df.groupby(['name', 'url']).size()
            name_url_dupes = name_url_dupes[name_url_dupes > 1]

            for (name, url), count in name_url_dupes.items():
                if pd.notna(url) and url != '':
                    dupes = self.master_df[(self.master_df['name'] == name) & (self.master_df['url'] == url)]
                    duplicate_groups.append({
                        'duplicate_type': 'Same name and URL',
                        'count': len(dupes),
                        'name': name,
                        'url': url,
                        'files': ', '.join(dupes['file_source'].unique()),
                        'recommendation': 'Keep one, remove others'
                    })

        # Check for duplicates by name + source + description
        name_source_desc_dupes = self.master_df.groupby(['name', 'source', 'description']).size()
        name_source_desc_dupes = name_source_desc_dupes[name_source_desc_dupes > 1]

        for (name, source, desc), count in name_source_desc_dupes.items():
            if pd.notna(name) and pd.notna(source):
                dupes = self.master_df[
                    (self.master_df['name'] == name) &
                    (self.master_df['source'] == source) &
                    (self.master_df['description'] == desc)
                ]
                duplicate_groups.append({
                    'duplicate_type': 'Same name, source, and description',
                    'count': len(dupes),
                    'name': name,
                    'source': source,
                    'files': ', '.join(dupes['file_source'].unique()),
                    'recommendation': 'Keep one, remove others'
                })

        self.issues['exact_duplicates'] = duplicate_groups
        self.log(f"  [\!] Found {len(duplicate_groups)} exact duplicate groups")

    def detect_near_duplicates(self):
        """Detect near-duplicate resources using fuzzy matching"""
        self.log("Phase 4.2: Detecting near-duplicates (this may take a while)...")

        if not FUZZY_AVAILABLE:
            self.log("  [\!] Skipping near-duplicate detection (fuzzywuzzy not available)")
            return

        near_duplicates = []

        # Group by URL and check for name variations
        if 'url' in self.master_df.columns:
            url_groups = self.master_df.groupby('url')
            for url, group in url_groups:
                if pd.notna(url) and url != '' and len(group) > 1:
                    names = group['name'].unique()
                    if len(names) > 1:
                        near_duplicates.append({
                            'duplicate_type': 'Same URL, different names',
                            'url': url,
                            'names': ' | '.join(str(n) for n in names),
                            'count': len(group),
                            'files': ', '.join(group['file_source'].unique()),
                            'similarity_score': 100
                        })

        # Fuzzy match on names within same source (limit to avoid long runtime)
        source_groups = self.master_df.groupby('source')
        for source, group in source_groups:
            if pd.notna(source) and len(group) > 1 and len(group) < 500:  # Limit to avoid O(n²) explosion
                names = group['name'].dropna().unique()

                for i, name1 in enumerate(names):
                    for name2 in names[i+1:]:
                        similarity = fuzz.ratio(str(name1).lower(), str(name2).lower())
                        if similarity >= 85 and similarity < 100:  # Near match but not exact
                            near_duplicates.append({
                                'duplicate_type': 'Similar names, same source',
                                'source': source,
                                'name1': name1,
                                'name2': name2,
                                'similarity_score': similarity,
                                'count': 2
                            })

        self.issues['near_duplicates'] = near_duplicates[:500]  # Limit report size
        self.log(f"  [\!] Found {len(near_duplicates)} near-duplicate pairs (showing top 500)")

    # ==================== PHASE 5: Data Quality ====================

    def check_missing_critical_data(self):
        """Flag resources with missing critical data"""
        self.log("Phase 5.1: Checking for missing critical data...")

        critical_fields = ['name', 'description', 'url', 'category', 'stem_fields', 'target_grade']

        missing_issues = []

        for idx, row in self.master_df.iterrows():
            missing_fields = []
            severity = 'LOW'

            for field in critical_fields:
                if pd.isna(row.get(field)) or str(row.get(field)).strip() == '':
                    missing_fields.append(field)

            if missing_fields:
                # Determine severity
                if 'name' in missing_fields or 'category' in missing_fields:
                    severity = 'CRITICAL'
                elif 'description' in missing_fields or 'url' in missing_fields:
                    severity = 'HIGH'
                elif len(missing_fields) >= 3:
                    severity = 'MEDIUM'

                missing_issues.append({
                    'file_source': row.get('file_source', ''),
                    'name': row.get('name', 'MISSING NAME'),
                    'missing_fields': ', '.join(missing_fields),
                    'severity': severity,
                    'field_count': len(missing_fields)
                })

        self.issues['missing_critical_data'] = missing_issues
        self.log(f"  [\!] Found {len(missing_issues)} resources with missing critical data")

    def check_invalid_values(self):
        """Flag resources with invalid or inconsistent values"""
        self.log("Phase 5.2: Checking for invalid values...")

        invalid_issues = []

        # Expected valid categories
        valid_categories = [
            'Scholarship', 'Competition', 'Camp', 'Program', 'Research Opportunity',
            'Internship', 'Learning Material', 'Organization', 'Shadowing', 'Workshop'
        ]

        # Expected location types
        valid_locations = ['Virtual', 'In-Person', 'Hybrid', 'Flexible', 'Online', 'Remote']

        for idx, row in self.master_df.iterrows():
            issues_found = []

            # Check target_grade format
            target_grade = str(row.get('target_grade', ''))
            if target_grade and target_grade not in ['', 'nan', 'None']:
                if re.search(r'\b(grade )?(13|14|15)', target_grade, re.IGNORECASE):
                    issues_found.append("Invalid grade level (13-15)")

            # Check category
            category = str(row.get('category', ''))
            if category and category not in ['', 'nan', 'None']:
                if not any(valid_cat.lower() in category.lower() for valid_cat in valid_categories):
                    issues_found.append(f"Unusual category: {category}")

            # Check location_type
            location_type = str(row.get('location_type', ''))
            if location_type and location_type not in ['', 'nan', 'None']:
                if not any(valid_loc.lower() in location_type.lower() for valid_loc in valid_locations):
                    issues_found.append(f"Unusual location_type: {location_type}")

            if issues_found:
                invalid_issues.append({
                    'file_source': row.get('file_source', ''),
                    'name': row.get('name', ''),
                    'issues': '; '.join(issues_found),
                    'severity': 'MEDIUM'
                })

        self.issues['invalid_values'] = invalid_issues
        self.log(f"  [\!] Found {len(invalid_issues)} resources with invalid values")

    def check_suspicious_data(self):
        """Flag resources with suspicious or placeholder data"""
        self.log("Phase 5.3: Checking for suspicious/placeholder data...")

        suspicious_issues = []

        placeholder_patterns = [
            r'\btbd\b', r'\bcoming soon\b', r'\bto be determined\b',
            r'\bplaceholder\b', r'\btest\b', r'\bexample\b'
        ]

        for idx, row in self.master_df.iterrows():
            issues_found = []

            # Check description length
            description = str(row.get('description', ''))
            if description and description not in ['', 'nan', 'None']:
                if len(description) < 50:
                    issues_found.append(f"Very short description ({len(description)} chars)")

                # Check for placeholder text
                for pattern in placeholder_patterns:
                    if re.search(pattern, description, re.IGNORECASE):
                        issues_found.append(f"Placeholder text: {pattern}")

            # Check for generic names
            name = str(row.get('name', ''))
            if name and name not in ['', 'nan', 'None']:
                if name.lower() in ['stem program', 'science competition', 'math competition']:
                    issues_found.append(f"Generic name: {name}")

            if issues_found:
                suspicious_issues.append({
                    'file_source': row.get('file_source', ''),
                    'name': row.get('name', ''),
                    'description': description[:100],
                    'issues': '; '.join(issues_found),
                    'severity': 'LOW'
                })

        self.issues['suspicious_data'] = suspicious_issues
        self.log(f"  [\!] Found {len(suspicious_issues)} resources with suspicious data")

    def check_logical_inconsistencies(self):
        """Flag resources with illogical combinations"""
        self.log("Phase 5.4: Checking for logical inconsistencies...")

        inconsistent_issues = []

        for idx, row in self.master_df.iterrows():
            issues_found = []

            location_type = str(row.get('location_type', '')).lower()
            transportation = str(row.get('transportation_required', '')).lower()
            cost = str(row.get('cost', '')).lower()
            financial_barrier = str(row.get('financial_barrier_level', '')).lower()
            category = str(row.get('category', '')).lower()

            # Virtual but needs transportation
            if 'virtual' in location_type and 'yes' in transportation:
                issues_found.append("Virtual but transportation_required=Yes")

            # Free but high financial barrier
            if 'free' in cost and 'high' in financial_barrier:
                issues_found.append("Free but financial_barrier_level=High")

            # Scholarship but not free
            if 'scholarship' in category:
                if 'free' not in cost and cost not in ['', 'nan', 'none']:
                    issues_found.append("Scholarship but cost is not Free")

            if issues_found:
                inconsistent_issues.append({
                    'file_source': row.get('file_source', ''),
                    'name': row.get('name', ''),
                    'issues': '; '.join(issues_found),
                    'severity': 'MEDIUM'
                })

        self.issues['logical_inconsistencies'] = inconsistent_issues
        self.log(f"  [\!] Found {len(inconsistent_issues)} resources with logical inconsistencies")

    # ==================== PHASE 6: URL Validation ====================

    def validate_urls(self):
        """Validate URL formats and detect duplicates"""
        self.log("Phase 6: Validating URLs...")

        url_issues = []

        if 'url' not in self.master_df.columns:
            return

        # URL format validation
        url_pattern = re.compile(r'^https?://')
        placeholder_domains = ['example.com', 'website.com', 'test.com', 'domain.com']

        for idx, row in self.master_df.iterrows():
            url = str(row.get('url', ''))
            if url and url not in ['', 'nan', 'None']:
                issues = []

                # Check format
                if not url_pattern.match(url):
                    issues.append("Missing http:// or https://")

                # Check for spaces
                if ' ' in url:
                    issues.append("URL contains spaces")

                # Check for placeholder
                if any(domain in url.lower() for domain in placeholder_domains):
                    issues.append("Placeholder URL")

                if issues:
                    url_issues.append({
                        'file_source': row.get('file_source', ''),
                        'name': row.get('name', ''),
                        'url': url,
                        'issues': '; '.join(issues),
                        'severity': 'MEDIUM'
                    })

        self.issues['url_validation'] = url_issues
        self.log(f"  [\!] Found {len(url_issues)} resources with URL issues")

    # ==================== PHASE 7: Source Analysis ====================

    def analyze_sources(self):
        """Analyze source consistency"""
        self.log("Phase 7: Analyzing source consistency...")

        if 'source' not in self.master_df.columns:
            return

        # Get all unique sources
        sources = self.master_df['source'].dropna()
        source_counts = sources.value_counts()

        self.stats['unique_sources'] = len(source_counts)
        self.stats['source_distribution'] = source_counts.head(50).to_dict()

        # Find sources with very few resources (might be errors)
        rare_sources = source_counts[source_counts <= 2]
        self.stats['rare_sources'] = rare_sources.to_dict()

        self.log(f"  [OK] Found {len(source_counts)} unique sources")
        self.log(f"  [\!] Found {len(rare_sources)} sources with <=2 resources")

    def analyze_problematic_files(self):
        """Analyze which files have the most issues"""
        self.log("Phase 7.2: Analyzing problematic files...")

        file_issues = defaultdict(lambda: defaultdict(int))

        # Count issues per file
        for issue_type, issues in self.issues.items():
            for issue in issues:
                if 'file_source' in issue:
                    file_issues[issue['file_source']][issue_type] += 1
                    file_issues[issue['file_source']]['total'] += 1

        # Create summary
        problematic_files = []
        for file_name, issues in file_issues.items():
            total_resources = len(self.master_df[self.master_df['file_source'] == file_name])
            problematic_files.append({
                'file': file_name,
                'total_resources': total_resources,
                'total_issues': issues['total'],
                'issue_rate': f"{(issues['total']/total_resources*100):.1f}%",
                'issue_breakdown': dict(issues)
            })

        # Sort by issue count
        problematic_files.sort(key=lambda x: x['total_issues'], reverse=True)

        self.issues['problematic_files'] = problematic_files[:50]  # Top 50
        self.log(f"  [OK] Analyzed {len(problematic_files)} files for quality issues")

    # ==================== PHASE 8: ML Analysis ====================

    def analyze_ml_readiness(self):
        """Assess readiness for ML pipeline"""
        self.log("Phase 8: Analyzing ML pipeline readiness...")

        ml_stats = {}

        # Clustering dimension 1: Accessibility Profile
        accessibility_cols = ['cost_category', 'location_type', 'financial_barrier_level', 'rural_accessible']
        ml_stats['accessibility_completeness'] = self._check_completeness(accessibility_cols)

        # Clustering dimension 2: Academic Level
        academic_cols = ['prerequisite_level', 'target_grade', 'time_commitment']
        ml_stats['academic_completeness'] = self._check_completeness(academic_cols)

        # Clustering dimension 3: STEM Field Focus
        stem_cols = ['stem_fields', 'category']
        ml_stats['stem_completeness'] = self._check_completeness(stem_cols)

        # Clustering dimension 4: Resource Format
        format_cols = ['category', 'time_commitment', 'support_level']
        ml_stats['format_completeness'] = self._check_completeness(format_cols)

        # Overall TF-IDF readiness (need descriptions)
        ml_stats['tfidf_readiness'] = {
            'total_resources': len(self.master_df),
            'with_descriptions': self.master_df['description'].notna().sum(),
            'percentage': f"{(self.master_df['description'].notna().sum() / len(self.master_df) * 100):.1f}%"
        }

        self.stats['ml_readiness'] = ml_stats
        self.log(f"  [OK] ML readiness analysis complete")

    def _check_completeness(self, columns):
        """Helper to check completeness of specific columns"""
        total = len(self.master_df)
        complete = 0

        for idx, row in self.master_df.iterrows():
            if all(pd.notna(row.get(col)) and str(row.get(col)).strip() != '' for col in columns):
                complete += 1

        return {
            'total_resources': total,
            'complete_resources': complete,
            'percentage': f"{(complete/total*100):.1f}%",
            'columns_checked': columns
        }

    # ==================== PHASE 9: Report Generation ====================

    def generate_all_reports(self):
        """Generate all output reports"""
        self.log("Phase 9: Generating comprehensive reports...")

        # Create output directory
        os.makedirs('data_quality_reports', exist_ok=True)

        # 1. Executive Summary
        self.generate_executive_summary()

        # 2-10. Detailed reports
        self.generate_csv_report('non_k12_resources', 'flagged_non_k12_resources.csv')
        self.generate_csv_report('non_stem_resources', 'flagged_non_stem_resources.csv')
        self.generate_csv_report('educator_resources', 'flagged_educator_resources.csv')
        self.generate_csv_report('exact_duplicates', 'duplicate_resources_analysis.csv')
        self.generate_csv_report('url_validation', 'url_validation_issues.csv')
        self.generate_csv_report('problematic_files', 'problematic_files_summary.csv')

        # Combine all data quality issues
        self.generate_combined_quality_report()

        # ML readiness report
        self.generate_ml_readiness_report()

        # Statistical analysis
        self.generate_statistical_report()

        self.log("[OK] All reports generated successfully!")

    def generate_executive_summary(self):
        """Generate executive summary report"""
        output_path = 'data_quality_reports/data_quality_summary.txt'

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("=" * 80 + "\n")
            f.write("BLACK MINDS IN STEM - DATA QUALITY ASSESSMENT\n")
            f.write("Executive Summary Report\n")
            f.write("=" * 80 + "\n\n")

            f.write(f"Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Total CSV Files Analyzed: {self.stats.get('total_files', 0)}\n")
            f.write(f"Total Resources Analyzed: {self.stats.get('total_resources', 0)}\n\n")

            f.write("-" * 80 + "\n")
            f.write("ISSUES FOUND BY CATEGORY\n")
            f.write("-" * 80 + "\n\n")

            total_issues = 0
            for issue_type, issues in self.issues.items():
                count = len(issues)
                total_issues += count
                f.write(f"{issue_type.replace('_', ' ').title()}: {count}\n")

            f.write(f"\nTotal Issues Found: {total_issues}\n\n")

            # Data quality score
            resources_with_issues = len(set(
                issue.get('file_source', '') + str(issue.get('name', ''))
                for issue_list in self.issues.values()
                for issue in issue_list
                if isinstance(issue, dict) and 'name' in issue
            ))

            quality_score = ((self.stats['total_resources'] - resources_with_issues) /
                           self.stats['total_resources'] * 100)

            f.write("-" * 80 + "\n")
            f.write("OVERALL DATA QUALITY SCORE\n")
            f.write("-" * 80 + "\n\n")
            f.write(f"Resources without issues: {self.stats['total_resources'] - resources_with_issues}\n")
            f.write(f"Resources with issues: {resources_with_issues}\n")
            f.write(f"Quality Score: {quality_score:.1f}%\n\n")

            f.write("-" * 80 + "\n")
            f.write("RECOMMENDATIONS\n")
            f.write("-" * 80 + "\n\n")
            f.write("1. Review all HIGH confidence flagged resources for removal\n")
            f.write("2. Manually verify MEDIUM confidence flagged resources\n")
            f.write("3. Address exact duplicates - keep most complete entries\n")
            f.write("4. Fill in missing critical data where possible\n")
            f.write("5. Standardize formatting for categories, grades, and other fields\n")
            f.write("6. Fix URL formatting issues\n")
            f.write("7. Consider re-scraping files with high issue rates\n\n")

            f.write("-" * 80 + "\n")
            f.write("NEXT STEPS\n")
            f.write("-" * 80 + "\n\n")
            f.write("1. Review detailed reports in data_quality_reports/ directory\n")
            f.write("2. Make decisions on flagged resources\n")
            f.write("3. Create data cleaning script based on approved changes\n")
            f.write("4. Re-run quality assessment after cleaning\n")

        self.log(f"  [OK] Generated executive summary: {output_path}")

    def generate_csv_report(self, issue_type, filename):
        """Generate CSV report for a specific issue type"""
        if issue_type not in self.issues or not self.issues[issue_type]:
            return

        output_path = f'data_quality_reports/{filename}'
        df = pd.DataFrame(self.issues[issue_type])
        df.to_csv(output_path, index=False, encoding='utf-8')
        self.log(f"  [OK] Generated report: {output_path} ({len(df)} entries)")

    def generate_combined_quality_report(self):
        """Combine all data quality issues into one report"""
        output_path = 'data_quality_reports/data_quality_issues.csv'

        all_issues = []

        for issue_type in ['missing_critical_data', 'invalid_values', 'suspicious_data', 'logical_inconsistencies']:
            if issue_type in self.issues:
                for issue in self.issues[issue_type]:
                    issue['issue_type'] = issue_type
                    all_issues.append(issue)

        if all_issues:
            df = pd.DataFrame(all_issues)
            df.to_csv(output_path, index=False, encoding='utf-8')
            self.log(f"  [OK] Generated combined quality report: {output_path} ({len(df)} entries)")

    def generate_ml_readiness_report(self):
        """Generate ML pipeline readiness report"""
        output_path = 'data_quality_reports/ml_pipeline_readiness.txt'

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("=" * 80 + "\n")
            f.write("ML PIPELINE READINESS ASSESSMENT\n")
            f.write("K-Means Clustering + TF-IDF Analysis\n")
            f.write("=" * 80 + "\n\n")

            ml_stats = self.stats.get('ml_readiness', {})

            f.write("CLUSTERING DIMENSION COMPLETENESS\n")
            f.write("-" * 80 + "\n\n")

            for dimension, stats in ml_stats.items():
                if dimension != 'tfidf_readiness':
                    f.write(f"{dimension.replace('_', ' ').title()}:\n")
                    if isinstance(stats, dict):
                        f.write(f"  Columns: {', '.join(stats.get('columns_checked', []))}\n")
                        f.write(f"  Complete resources: {stats.get('complete_resources', 0)}/{stats.get('total_resources', 0)}\n")
                        f.write(f"  Completeness: {stats.get('percentage', 'N/A')}\n\n")

            f.write("\nTF-IDF READINESS (Description Availability)\n")
            f.write("-" * 80 + "\n\n")
            tfidf = ml_stats.get('tfidf_readiness', {})
            f.write(f"Resources with descriptions: {tfidf.get('with_descriptions', 0)}/{tfidf.get('total_resources', 0)}\n")
            f.write(f"Percentage: {tfidf.get('percentage', 'N/A')}\n\n")

            f.write("\nRECOMMENDATIONS\n")
            f.write("-" * 80 + "\n\n")
            f.write("1. Prioritize filling in missing descriptions for TF-IDF analysis\n")
            f.write("2. Standardize category and stem_fields values\n")
            f.write("3. Ensure target_grade is populated for all resources\n")
            f.write("4. Fill in cost_category and location_type for accessibility clustering\n")

        self.log(f"  [OK] Generated ML readiness report: {output_path}")

    def generate_statistical_report(self):
        """Generate statistical analysis report"""
        output_path = 'data_quality_reports/dataset_statistics.txt'

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("=" * 80 + "\n")
            f.write("DATASET STATISTICAL ANALYSIS\n")
            f.write("=" * 80 + "\n\n")

            # Resources per directory
            f.write("RESOURCES PER DIRECTORY\n")
            f.write("-" * 80 + "\n")
            stats = self.stats.get('basic_statistics', {})
            for dir, count in stats.get('resources_per_directory', {}).items():
                f.write(f"{dir}: {count}\n")
            f.write("\n")

            # Category distribution
            f.write("CATEGORY DISTRIBUTION\n")
            f.write("-" * 80 + "\n")
            for category, count in stats.get('category_distribution', {}).items():
                f.write(f"{category}: {count}\n")
            f.write("\n")

            # Top sources
            f.write("TOP 20 SOURCES\n")
            f.write("-" * 80 + "\n")
            for source, count in list(stats.get('top_sources', {}).items())[:20]:
                f.write(f"{source}: {count}\n")
            f.write("\n")

            # Description statistics
            f.write("DESCRIPTION LENGTH STATISTICS\n")
            f.write("-" * 80 + "\n")
            f.write(f"Average: {stats.get('avg_description_length', 0):.0f} characters\n")
            f.write(f"Minimum: {stats.get('min_description_length', 0):.0f} characters\n")
            f.write(f"Maximum: {stats.get('max_description_length', 0):.0f} characters\n\n")

            # Null counts
            f.write("MISSING DATA BY COLUMN\n")
            f.write("-" * 80 + "\n")
            for col, count in stats.get('null_counts', {}).items():
                percentage = (count / self.stats['total_resources'] * 100)
                f.write(f"{col}: {count} ({percentage:.1f}%)\n")

        self.log(f"  [OK] Generated statistical report: {output_path}")

    # ==================== Main Execution ====================

    def run_full_analysis(self):
        """Run the complete analysis pipeline"""
        self.log("Starting comprehensive data quality analysis...")
        self.log("=" * 80)

        try:
            # Phase 1: Data Loading
            self.load_all_csvs()
            self.check_column_consistency()
            self.generate_basic_statistics()

            # Phase 2: K-12 Eligibility
            self.identify_non_k12_resources()
            self.identify_educator_resources()

            # Phase 3: STEM Relevance
            self.identify_non_stem_resources()
            self.validate_stem_field_consistency()

            # Phase 4: Duplicate Detection
            self.detect_exact_duplicates()
            self.detect_near_duplicates()

            # Phase 5: Data Quality
            self.check_missing_critical_data()
            self.check_invalid_values()
            self.check_suspicious_data()
            self.check_logical_inconsistencies()

            # Phase 6: URL Validation
            self.validate_urls()

            # Phase 7: Source & File Analysis
            self.analyze_sources()
            self.analyze_problematic_files()

            # Phase 8: ML Analysis
            self.analyze_ml_readiness()

            # Phase 9: Generate Reports
            self.generate_all_reports()

            self.log("=" * 80)
            self.log("[OK] Analysis complete! Check data_quality_reports/ directory for results.")

        except Exception as e:
            self.log(f"ERROR: Analysis failed: {str(e)}")
            import traceback
            traceback.print_exc()

# ==================== Entry Point ====================

if __name__ == "__main__":
    analyzer = DataQualityAnalyzer()
    analyzer.run_full_analysis()
