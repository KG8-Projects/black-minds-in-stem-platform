"""
Computer Science Tier1 Consolidation Analysis & Potential Split

Analyzes whether 41% CS concentration is appropriate or needs splitting
into sub-domains (AI/ML, Data Science, Cybersecurity, etc.) for better clustering
"""

import pandas as pd
import numpy as np
from pathlib import Path
import re

# Paths
BASE_DIR = Path(r"C:\Users\u_wos\Downloads\Black Minds In STEM")
INPUT_FILE = BASE_DIR / "final_ml_ready_data" / "bmis_final_ml_ready_dataset.csv"
OUTPUT_DIR = BASE_DIR / "final_ml_ready_data"
REPORT_FILE = OUTPUT_DIR / "CS_TIER1_ANALYSIS_REPORT.txt"

print("="*80)
print("COMPUTER SCIENCE TIER1 CONSOLIDATION ANALYSIS")
print("="*80)
print()

# ============================================================================
# PHASE 1: ANALYZE CURRENT CS CONSOLIDATION
# ============================================================================

def analyze_current_distribution(df):
    """Analyze current stem_field_tier1 distribution with focus on CS"""
    print("PHASE 1: CURRENT DISTRIBUTION ANALYSIS")
    print("-"*80)

    total = len(df)
    cs_count = (df['stem_field_tier1'] == 'Computer Science').sum()
    cs_pct = (cs_count / total) * 100

    print(f"\nDataset Overview:")
    print(f"  Total resources: {total:,}")
    print(f"  Computer Science resources: {cs_count:,} ({cs_pct:.1f}%)")
    print()

    if cs_pct > 30:
        print(f"  [WARNING] CS represents {cs_pct:.1f}% of dataset (>30% concentration)")
        print(f"  [ANALYSIS] May need splitting for balanced clustering")
    elif cs_pct > 25:
        print(f"  [CAUTION] CS represents {cs_pct:.1f}% of dataset (25-30% - borderline)")
    else:
        print(f"  [OK] CS represents {cs_pct:.1f}% of dataset (<25%)")

    print()

    # Show full tier1 distribution
    print("Current stem_field_tier1 distribution:")
    for field, count in df['stem_field_tier1'].value_counts().items():
        pct = (count / total) * 100
        status = "[HIGH]" if pct > 25 else "[OK]" if pct >= 5 else "[LOW]"
        print(f"  {status} {field:35s} {count:5d} ({pct:5.1f}%)")

    print()
    return cs_count, cs_pct

def analyze_cs_tier2_breakdown(df):
    """Analyze tier2 values under Computer Science tier1"""
    print("COMPUTER SCIENCE TIER2 BREAKDOWN")
    print("-"*80)

    cs_df = df[df['stem_field_tier1'] == 'Computer Science'].copy()

    unique_tier2 = cs_df['stem_field_tier2'].nunique()
    print(f"\nUnique tier2 categories under CS: {unique_tier2}")
    print()

    print("Top 30 tier2 categories:")
    tier2_counts = cs_df['stem_field_tier2'].value_counts()
    for i, (tier2, count) in enumerate(tier2_counts.head(30).items(), 1):
        pct = (count / len(cs_df)) * 100
        print(f"  {i:2d}. {tier2[:60]:60s} {count:4d} ({pct:5.1f}%)")

    print()
    return cs_df

def classify_cs_subdomains(cs_df):
    """Classify CS resources into sub-domains based on tier2 values"""
    print("CS SUB-DOMAIN CLASSIFICATION")
    print("-"*80)

    # Define sub-domain keyword patterns
    subdomain_keywords = {
        'Artificial Intelligence/Machine Learning': [
            r'\bai\b', r'artificial intelligence', r'machine learning', r'\bml\b',
            r'deep learning', r'neural network', r'data mining', r'natural language',
            r'\bnlp\b', r'computer vision', r'image recognition'
        ],
        'Data Science': [
            r'data science', r'data analytics', r'data analysis', r'big data',
            r'data visualization', r'data engineering', r'analytics',
            r'data-driven', r'data analysis'
        ],
        'Cybersecurity': [
            r'cybersecurity', r'cyber security', r'\bsecurity\b', r'ethical hacking',
            r'penetration testing', r'cryptography', r'infosec', r'information security',
            r'network security', r'cyber defense'
        ],
        'Web Development': [
            r'web development', r'web design', r'frontend', r'front-end', r'backend',
            r'back-end', r'full stack', r'full-stack', r'\bhtml\b', r'\bcss\b',
            r'javascript', r'\breact\b', r'\bvue\b', r'\bangular\b', r'web programming'
        ],
        'Software Engineering': [
            r'software engineering', r'software development', r'programming',
            r'\bcoding\b', r'app development', r'application development',
            r'mobile development', r'\bpython\b', r'\bjava\b', r'\bc\+\+\b',
            r'software design', r'agile', r'devops'
        ],
        'Game Development': [
            r'game development', r'game design', r'game programming', r'\bunity\b',
            r'\bunreal\b', r'gaming', r'game engine', r'game dev'
        ],
        'Robotics': [
            r'\brobotics\b', r'\brobot\b', r'automation', r'embedded systems',
            r'arduino', r'raspberry pi'
        ]
    }

    # Classify each resource
    subdomain_assignments = {}

    for idx, row in cs_df.iterrows():
        tier2 = str(row['stem_field_tier2']).lower()
        name = str(row['name']).lower()
        desc = str(row['description']).lower()

        # Combine text for matching
        full_text = f"{tier2} {name} {desc}"

        matched_subdomain = None

        # Try to match to a specific subdomain
        for subdomain, keywords in subdomain_keywords.items():
            for keyword in keywords:
                if re.search(keyword, full_text):
                    matched_subdomain = subdomain
                    break
            if matched_subdomain:
                break

        # Default to CS General if no match
        if not matched_subdomain:
            matched_subdomain = 'Computer Science (General)'

        subdomain_assignments[idx] = matched_subdomain

    # Add subdomain column
    cs_df['cs_subdomain'] = cs_df.index.map(subdomain_assignments)

    # Count resources per subdomain
    print("\nSub-domain Classification Results:")
    print()

    subdomain_counts = cs_df['cs_subdomain'].value_counts()
    total_cs = len(cs_df)
    total_dataset = len(cs_df)  # Will be corrected by caller

    subdomain_analysis = {}

    for subdomain, count in subdomain_counts.items():
        pct_of_cs = (count / total_cs) * 100
        subdomain_analysis[subdomain] = {
            'count': count,
            'pct_of_cs': pct_of_cs
        }

        status = ""
        if count >= 100:
            status = "[LARGE - Split Candidate]"
        elif count >= 50:
            status = "[MEDIUM]"
        else:
            status = "[SMALL]"

        print(f"  {status:30s} {subdomain:45s} {count:4d} ({pct_of_cs:5.1f}% of CS)")

    print()
    return cs_df, subdomain_analysis

def make_split_recommendation(subdomain_analysis, total_dataset):
    """Decide whether to split CS based on subdomain sizes"""
    print("SPLIT RECOMMENDATION")
    print("-"*80)

    # Count subdomains meeting size thresholds
    large_subdomains = []  # >=100 resources
    medium_subdomains = []  # 50-99 resources

    for subdomain, stats in subdomain_analysis.items():
        count = stats['count']
        pct_of_dataset = (count / total_dataset) * 100

        if count >= 100:
            large_subdomains.append((subdomain, count, pct_of_dataset))
        elif count >= 50:
            medium_subdomains.append((subdomain, count, pct_of_dataset))

    print(f"\nSub-domain Size Analysis:")
    print(f"  Large (>=100 resources): {len(large_subdomains)}")
    for subdomain, count, pct in large_subdomains:
        print(f"    - {subdomain}: {count} ({pct:.1f}% of dataset)")

    print(f"\n  Medium (50-99 resources): {len(medium_subdomains)}")
    for subdomain, count, pct in medium_subdomains:
        print(f"    - {subdomain}: {count} ({pct:.1f}% of dataset)")

    print()

    # Apply decision logic
    if len(large_subdomains) >= 2:
        print("DECISION: RECOMMEND SPLIT")
        print(f"  Rationale: {len(large_subdomains)} sub-domains have >=100 resources each")
        print(f"  Impact: Better balanced distribution for K-Means clustering")
        print(f"  Quality: More precise resource recommendations for students")
        recommendation = "SPLIT"
    elif len(large_subdomains) == 1 and len(medium_subdomains) >= 2:
        print("DECISION: RECOMMEND SPLIT (Conditional)")
        print(f"  Rationale: 1 large + {len(medium_subdomains)} medium sub-domains")
        print(f"  Impact: Moderate improvement in clustering")
        print(f"  Note: Consider splitting large + promoting medium subdomains")
        recommendation = "SPLIT"
    else:
        print("DECISION: DO NOT SPLIT")
        print(f"  Rationale: Insufficient large sub-domains (need 2+, have {len(large_subdomains)})")
        print(f"  Impact: Keep CS as single tier1 category")
        print(f"  Alternative: Rely on tier2 + TF-IDF for differentiation")
        recommendation = "NO_SPLIT"

    print()
    return recommendation, large_subdomains, medium_subdomains

def apply_cs_split(df, cs_df):
    """Apply CS tier1 split based on subdomain classification"""
    print("APPLYING CS TIER1 SPLIT")
    print("-"*80)

    # Backup original tier1
    df['stem_field_tier1_original'] = df['stem_field_tier1']

    # Map subdomain assignments back to main dataframe
    for idx, row in cs_df.iterrows():
        subdomain = row['cs_subdomain']

        # Simplify subdomain names for tier1
        tier1_mapping = {
            'Artificial Intelligence/Machine Learning': 'Artificial Intelligence/Machine Learning',
            'Data Science': 'Data Science',
            'Cybersecurity': 'Cybersecurity',
            'Web Development': 'Web Development',
            'Software Engineering': 'Software Engineering',
            'Game Development': 'Game Development',
            'Robotics': 'Robotics',
            'Computer Science (General)': 'Computer Science'
        }

        new_tier1 = tier1_mapping.get(subdomain, 'Computer Science')
        df.at[idx, 'stem_field_tier1'] = new_tier1

    # Regenerate tfidf_text with new tier1
    print("\nRegenerating tfidf_text with new tier1 categories...")
    df['tfidf_text'] = (
        df['name'].fillna('') + ' ' +
        df['description'].fillna('') + ' ' +
        df['stem_fields'].fillna('') + ' ' +
        df['category'].fillna('') + ' ' +
        df['target_grade_standardized'].fillna('') + ' ' +
        df['prerequisite_level'].fillna('') + ' ' +
        df['support_level'].fillna('') + ' ' +
        df['location_type'].fillna('') + ' ' +
        df['stem_field_tier1'].fillna('')  # Updated tier1
    )

    print("  [OK] tfidf_text regenerated with new stem_field_tier1")
    print()

    return df

def validate_new_distribution(df):
    """Validate the new tier1 distribution after split"""
    print("VALIDATION: NEW TIER1 DISTRIBUTION")
    print("-"*80)

    total = len(df)
    unique_tier1 = df['stem_field_tier1'].nunique()

    print(f"\nNew tier1 statistics:")
    print(f"  Unique tier1 categories: {unique_tier1}")
    print()

    print("Updated stem_field_tier1 distribution:")
    tier1_counts = df['stem_field_tier1'].value_counts()

    max_concentration = 0
    max_category = None

    for field, count in tier1_counts.items():
        pct = (count / total) * 100

        if pct > max_concentration:
            max_concentration = pct
            max_category = field

        if pct > 25:
            status = "[HIGH]"
        elif pct >= 15:
            status = "[MEDIUM]"
        elif pct >= 5:
            status = "[OK]"
        else:
            status = "[LOW]"

        print(f"  {status:10s} {field:45s} {count:5d} ({pct:5.1f}%)")

    print()

    # Quality assessment
    if max_concentration <= 25:
        print(f"[OK] Maximum concentration: {max_concentration:.1f}% ({max_category})")
        print(f"[OK] Distribution is balanced for K-Means clustering")
        quality = "EXCELLENT"
    elif max_concentration <= 30:
        print(f"[WARNING] Maximum concentration: {max_concentration:.1f}% ({max_category})")
        print(f"[CAUTION] Acceptable but monitor clustering quality")
        quality = "GOOD"
    else:
        print(f"[CRITICAL] Maximum concentration: {max_concentration:.1f}% ({max_category})")
        print(f"[ISSUE] May still cause clustering imbalance")
        quality = "NEEDS_WORK"

    print()
    return quality, unique_tier1, max_concentration

def generate_analysis_report(df, recommendation, subdomain_analysis,
                            cs_count_before, cs_pct_before,
                            unique_tier1_after=None, max_concentration_after=None):
    """Generate comprehensive analysis report"""

    report_lines = []
    report_lines.append("="*80)
    report_lines.append("COMPUTER SCIENCE TIER1 CONSOLIDATION ANALYSIS REPORT")
    report_lines.append("="*80)
    report_lines.append("")

    # Executive Summary
    report_lines.append("EXECUTIVE SUMMARY")
    report_lines.append("-"*80)

    total = len(df)

    report_lines.append(f"Dataset: {total:,} resources")
    report_lines.append(f"Original CS concentration: {cs_count_before:,} resources ({cs_pct_before:.1f}%)")
    report_lines.append("")

    if recommendation == "SPLIT":
        cs_count_after = (df['stem_field_tier1'] == 'Computer Science').sum()
        cs_pct_after = (cs_count_after / total) * 100

        report_lines.append(f"DECISION: SPLIT RECOMMENDED AND APPLIED")
        report_lines.append(f"New CS concentration: {cs_count_after:,} resources ({cs_pct_after:.1f}%)")
        report_lines.append(f"Improvement: -{cs_pct_before - cs_pct_after:.1f} percentage points")
        report_lines.append(f"New tier1 categories: {unique_tier1_after}")
        report_lines.append(f"Maximum concentration: {max_concentration_after:.1f}%")
    else:
        report_lines.append(f"DECISION: NO SPLIT NEEDED")
        report_lines.append(f"CS remains at: {cs_count_before:,} resources ({cs_pct_before:.1f}%)")
        report_lines.append(f"Rationale: Insufficient large sub-domains to warrant splitting")

    report_lines.append("")

    # Sub-domain Analysis
    report_lines.append("SUB-DOMAIN ANALYSIS")
    report_lines.append("-"*80)

    for subdomain, stats in sorted(subdomain_analysis.items(),
                                   key=lambda x: x[1]['count'], reverse=True):
        count = stats['count']
        pct_cs = stats['pct_of_cs']
        pct_dataset = (count / total) * 100

        size_label = "LARGE" if count >= 100 else "MEDIUM" if count >= 50 else "SMALL"

        report_lines.append(f"  [{size_label:6s}] {subdomain}")
        report_lines.append(f"           Count: {count:,} resources")
        report_lines.append(f"           % of CS: {pct_cs:.1f}%")
        report_lines.append(f"           % of dataset: {pct_dataset:.1f}%")
        report_lines.append("")

    # Recommendation Rationale
    report_lines.append("RECOMMENDATION RATIONALE")
    report_lines.append("-"*80)

    large_count = sum(1 for s in subdomain_analysis.values() if s['count'] >= 100)
    medium_count = sum(1 for s in subdomain_analysis.values() if 50 <= s['count'] < 100)

    report_lines.append(f"Large sub-domains (>=100 resources): {large_count}")
    report_lines.append(f"Medium sub-domains (50-99 resources): {medium_count}")
    report_lines.append("")

    if recommendation == "SPLIT":
        report_lines.append("SPLIT DECISION:")
        report_lines.append("  - Multiple distinct sub-domains with significant resource counts")
        report_lines.append("  - Splitting improves clustering balance and precision")
        report_lines.append("  - Students will receive more targeted recommendations")
    else:
        report_lines.append("NO SPLIT DECISION:")
        report_lines.append("  - Sub-domains too small to warrant separate tier1 categories")
        report_lines.append("  - Keep CS as single category for simplicity")
        report_lines.append("  - Use tier2 and TF-IDF for differentiation within CS cluster")

    report_lines.append("")

    # Final Distribution
    if recommendation == "SPLIT":
        report_lines.append("FINAL TIER1 DISTRIBUTION")
        report_lines.append("-"*80)

        for field, count in df['stem_field_tier1'].value_counts().items():
            pct = (count / total) * 100
            report_lines.append(f"  {field:45s} {count:5d} ({pct:5.1f}%)")

        report_lines.append("")

    report_lines.append("="*80)

    # Write report
    report_text = '\n'.join(report_lines)

    with open(REPORT_FILE, 'w', encoding='utf-8') as f:
        f.write(report_text)

    print(report_text)
    print()
    print(f"Report saved: {REPORT_FILE}")
    print()

def main():
    """Main execution function"""

    # Load dataset
    print("Loading dataset...")
    df = pd.read_csv(INPUT_FILE)
    print(f"Loaded {len(df):,} resources\n")

    # Phase 1: Analyze current distribution
    cs_count_before, cs_pct_before = analyze_current_distribution(df)
    cs_df = analyze_cs_tier2_breakdown(df)

    # Phase 2: Classify sub-domains
    cs_df, subdomain_analysis = classify_cs_subdomains(cs_df)

    # Add dataset percentage to subdomain analysis
    total_dataset = len(df)
    for subdomain in subdomain_analysis:
        count = subdomain_analysis[subdomain]['count']
        subdomain_analysis[subdomain]['pct_of_dataset'] = (count / total_dataset) * 100

    # Phase 3: Make recommendation
    recommendation, large_subdomains, medium_subdomains = make_split_recommendation(
        subdomain_analysis, total_dataset
    )

    # Phase 4: Apply split if recommended
    if recommendation == "SPLIT":
        df = apply_cs_split(df, cs_df)
        quality, unique_tier1, max_concentration = validate_new_distribution(df)

        # Save updated dataset
        if quality in ["EXCELLENT", "GOOD"]:
            output_file = OUTPUT_DIR / "bmis_final_ml_ready_dataset_cs_refined.csv"
            df.to_csv(output_file, index=False)
            print(f"Updated dataset saved: {output_file}")
            print(f"  Total resources: {len(df):,}")
            print(f"  Total columns: {len(df.columns)}")
            print()

        # Generate report
        generate_analysis_report(df, recommendation, subdomain_analysis,
                                cs_count_before, cs_pct_before,
                                unique_tier1, max_concentration)
    else:
        # No split - save validated dataset
        output_file = OUTPUT_DIR / "bmis_final_ml_ready_dataset_cs_validated.csv"
        df.to_csv(output_file, index=False)
        print(f"Validated dataset saved: {output_file}")
        print(f"  (No changes to stem_field_tier1)")
        print()

        # Generate report
        generate_analysis_report(df, recommendation, subdomain_analysis,
                                cs_count_before, cs_pct_before)

    print("="*80)
    print("CS TIER1 ANALYSIS COMPLETE")
    print("="*80)
    print()

if __name__ == "__main__":
    main()
