"""
Black Minds in STEM: ML Pipeline Readiness Validation
Comprehensive quality assessment and readiness scoring
"""

import pandas as pd
import numpy as np
from pathlib import Path
from collections import Counter
import json
import warnings
warnings.filterwarnings('ignore')

# Constants
BASE_DIR = Path(r"C:\Users\u_wos\Downloads\Black Minds In STEM")
INPUT_FILE = BASE_DIR / "ml_ready_data" / "bmis_ml_ready_dataset_fixed.csv"
OUTPUT_DIR = BASE_DIR / "validation_reports_fixed"

# Create output directories
(OUTPUT_DIR / "quality_issues").mkdir(parents=True, exist_ok=True)
(OUTPUT_DIR / "distribution_analysis").mkdir(parents=True, exist_ok=True)
(OUTPUT_DIR / "sample_data").mkdir(parents=True, exist_ok=True)

# Global variables for scoring
readiness_scores = {}
action_items = {'critical': [], 'high': [], 'medium': [], 'low': []}
quality_issues = {}

print("="*80)
print("BLACK MINDS IN STEM - ML PIPELINE READINESS VALIDATION")
print("="*80)
print()

# ============================================================================
# PHASE 1: DATASET OVERVIEW & BASIC STATISTICS
# ============================================================================

def load_and_analyze_dataset():
    """Load dataset and generate basic statistics"""
    print("="*80)
    print("PHASE 1: DATASET OVERVIEW & BASIC STATISTICS")
    print("="*80)
    print()

    df = pd.read_csv(INPUT_FILE)

    print(f"Dataset loaded successfully: {INPUT_FILE.name}")
    print()
    print("SECTION 1.1: BASIC DATASET INFORMATION")
    print("-"*80)
    print(f"Total resources: {len(df):,}")
    print(f"Total columns: {len(df.columns)}")
    print(f"Memory usage: {df.memory_usage(deep=True).sum() / 1024**2:.2f} MB")
    print()

    # Data types distribution
    dtype_counts = df.dtypes.value_counts()
    print("Data types distribution:")
    for dtype, count in dtype_counts.items():
        print(f"  {dtype}: {count} columns")
    print()

    print("SECTION 1.2: COLUMN INVENTORY")
    print("-"*80)

    original_cols = ['name', 'description', 'url', 'source', 'category', 'stem_fields',
                    'target_grade', 'cost', 'location_type', 'time_commitment',
                    'prerequisite_level', 'support_level', 'deadline',
                    'financial_barrier_level', 'financial_aid_available',
                    'family_income_consideration', 'hidden_costs_level', 'cost_category',
                    'diversity_focus', 'underrepresented_friendly', 'first_gen_support',
                    'cultural_competency', 'rural_accessible', 'transportation_required',
                    'internet_dependency', 'regional_availability',
                    'family_involvement_required', 'peer_network_building',
                    'mentor_access_level']

    print(f"Original core columns (29): {len([c for c in df.columns if c in original_cols])}")

    prediction_cols = [c for c in df.columns if '_predicted' in c or '_confidence' in c]
    print(f"Prediction columns (6): {len(prediction_cols)}")
    if prediction_cols:
        for col in prediction_cols:
            print(f"  - {col}")

    enhancement_cols = ['word_count', 'tfidf_text']
    print(f"Enhancement columns (2): {len([c for c in df.columns if c in enhancement_cols])}")

    standardization_cols = ['category_tier1', 'category_tier2', 'stem_field_tier1', 'stem_field_tier2']
    print(f"Standardization columns (4): {len([c for c in df.columns if c in standardization_cols])}")

    tracking_cols = ['source_file', 'program_family']
    print(f"Tracking columns (2): {len([c for c in df.columns if c in tracking_cols])}")
    print()

    print("SECTION 1.3: OVERALL DATA COMPLETENESS")
    print("-"*80)
    total_cells = len(df) * len(df.columns)
    non_null_cells = df.notna().sum().sum()
    null_cells = total_cells - non_null_cells

    print(f"Total cells in dataset: {total_cells:,}")
    print(f"Non-null cells: {non_null_cells:,} ({non_null_cells/total_cells*100:.1f}%)")
    print(f"Null cells: {null_cells:,} ({null_cells/total_cells*100:.1f}%)")
    print()

    # Top 10 columns with most missing data
    missing_by_col = df.isna().sum().sort_values(ascending=False).head(10)
    print("Top 10 columns with most missing data:")
    for col, count in missing_by_col.items():
        if count > 0:
            print(f"  {col:40s} {count:4d} missing ({count/len(df)*100:.1f}%)")

    print("\n" + "="*80 + "\n")

    return df

# ============================================================================
# PHASE 2: ML CLUSTERING DIMENSIONS COMPLETENESS
# ============================================================================

def analyze_dimension_1_accessibility(df):
    """Analyze Accessibility Profile dimension"""
    print("DIMENSION 1: ACCESSIBILITY PROFILE")
    print("-"*80)

    features = {
        'financial_barrier_level': 10,  # Weight
        'hidden_costs_level': 10,
        'cost_category': 8,
        'location_type': 7,
        'transportation_required': 7,
        'rural_accessible': 7,
        'internet_dependency': 6
    }

    dimension_scores = []

    for feature, weight in features.items():
        if feature not in df.columns:
            print(f"\n{feature}: MISSING COLUMN")
            continue

        completeness = df[feature].notna().sum() / len(df) * 100

        # Check if predicted
        predicted_col = f'{feature}_predicted'
        confidence_col = f'{feature}_confidence'

        if predicted_col in df.columns:
            predicted_count = (df[predicted_col] == True).sum()
            actual_count = df[feature].notna().sum() - predicted_count

            if confidence_col in df.columns:
                avg_confidence = df.loc[df[predicted_col] == True, confidence_col].mean()
                print(f"\n{feature}:")
                print(f"  Completeness: {completeness:.1f}%")
                print(f"  Actual values: {actual_count:,} ({actual_count/len(df)*100:.1f}%)")
                print(f"  Predicted values: {predicted_count:,} ({predicted_count/len(df)*100:.1f}%)")
                print(f"  Avg prediction confidence: {avg_confidence:.2%}")
            else:
                print(f"\n{feature}:")
                print(f"  Completeness: {completeness:.1f}%")
                print(f"  Actual values: {actual_count:,}")
                print(f"  Predicted values: {predicted_count:,}")
        else:
            print(f"\n{feature}:")
            print(f"  Completeness: {completeness:.1f}%")

        # Value distribution
        value_counts = df[feature].value_counts()
        print(f"  Value distribution:")
        for val, count in value_counts.head(5).items():
            print(f"    {val}: {count:,} ({count/len(df)*100:.1f}%)")

        dimension_scores.append((feature, completeness, weight))

    # Calculate weighted average
    total_weight = sum(w for _, _, w in dimension_scores)
    weighted_score = sum(score * weight for _, score, weight in dimension_scores) / total_weight

    print(f"\n{'='*80}")
    print(f"Accessibility Profile Dimension: {weighted_score:.1f}% complete")

    status = "[OK]" if weighted_score >= 90 else "[WARNING]"
    print(f"Status: {status}")

    if weighted_score < 90:
        action_items['critical'].append({
            'issue': 'Accessibility Profile below 90% complete',
            'current': f'{weighted_score:.1f}%',
            'target': '90%+',
            'time_estimate': '2-3 hours',
            'approach': 'Manual review or retrain ML models for missing features'
        })

    readiness_scores['accessibility_profile'] = weighted_score

    print("="*80 + "\n")

    return weighted_score

def analyze_dimension_2_academic(df):
    """Analyze Academic Level dimension"""
    print("DIMENSION 2: ACADEMIC LEVEL")
    print("-"*80)

    features = ['prerequisite_level', 'target_grade', 'time_commitment']
    dimension_scores = []

    for feature in features:
        if feature not in df.columns:
            continue

        completeness = df[feature].notna().sum() / len(df) * 100
        unique_count = df[feature].nunique()

        print(f"\n{feature}:")
        print(f"  Completeness: {completeness:.1f}%")
        print(f"  Unique values: {unique_count}")

        # Value distribution
        value_counts = df[feature].value_counts()
        print(f"  Top 10 values:")
        for val, count in value_counts.head(10).items():
            print(f"    {val}: {count:,} ({count/len(df)*100:.1f}%)")

        # Special analysis for target_grade
        if feature == 'target_grade':
            if unique_count > 50:
                print(f"  [WARNING] {unique_count} unique values - needs standardization!")
                action_items['high'].append({
                    'issue': 'target_grade has too many unique values',
                    'current': f'{unique_count} values',
                    'target': '<50 standardized values',
                    'time_estimate': '1-2 hours',
                    'approach': 'Create mapping to standard grade ranges'
                })

        dimension_scores.append(completeness)

    avg_score = np.mean(dimension_scores)

    print(f"\n{'='*80}")
    print(f"Academic Level Dimension: {avg_score:.1f}% complete")

    status = "[OK]" if avg_score >= 90 else "[WARNING]"
    print(f"Status: {status}")

    if avg_score < 90:
        action_items['critical'].append({
            'issue': 'Academic Level dimension below 90% complete',
            'current': f'{avg_score:.1f}%',
            'target': '90%+',
            'time_estimate': '1-2 hours',
            'approach': 'Fill missing prerequisite_level or time_commitment values'
        })

    readiness_scores['academic_level'] = avg_score

    print("="*80 + "\n")

    return avg_score

def analyze_dimension_3_stem_field(df):
    """Analyze STEM Field Focus dimension"""
    print("DIMENSION 3: STEM FIELD FOCUS")
    print("-"*80)

    # Analyze stem_field_tier1
    print("\nstem_field_tier1 (Standardized for ML):")
    tier1_complete = df['stem_field_tier1'].notna().sum() / len(df) * 100
    tier1_unique = df['stem_field_tier1'].nunique()

    print(f"  Completeness: {tier1_complete:.1f}%")
    print(f"  Unique values: {tier1_unique}")

    if tier1_unique > 35:
        print(f"  [WARNING] {tier1_unique} unique tier1 fields - should be 20-30!")
        action_items['high'].append({
            'issue': 'stem_field_tier1 not standardized enough',
            'current': f'{tier1_unique} unique values',
            'target': '20-30 core STEM fields',
            'time_estimate': '2-3 hours',
            'approach': 'Consolidate similar fields, better mapping'
        })

    # Show distribution
    print(f"  Top 15 tier1 STEM fields:")
    for field, count in df['stem_field_tier1'].value_counts().head(15).items():
        print(f"    {field[:60]:60s} {count:4d} ({count/len(df)*100:.1f}%)")

    # Check for "Other" values
    other_count = df['stem_field_tier1'].str.contains('Other', case=False, na=False).sum()
    other_pct = other_count / len(df) * 100
    print(f"  Resources with 'Other': {other_count} ({other_pct:.1f}%)")

    # Analyze category_tier1
    print("\ncategory_tier1 (Standardized for ML):")
    cat1_complete = df['category_tier1'].notna().sum() / len(df) * 100
    cat1_unique = df['category_tier1'].nunique()

    print(f"  Completeness: {cat1_complete:.1f}%")
    print(f"  Unique values: {cat1_unique}")

    if cat1_unique > 20:
        print(f"  [WARNING] {cat1_unique} unique tier1 categories - should be 10-15!")
        action_items['high'].append({
            'issue': 'category_tier1 not standardized enough',
            'current': f'{cat1_unique} unique values',
            'target': '10-15 standard categories',
            'time_estimate': '1-2 hours',
            'approach': 'Consolidate similar categories'
        })

    print(f"  All tier1 categories:")
    for cat, count in df['category_tier1'].value_counts().items():
        print(f"    {cat:40s} {count:4d} ({count/len(df)*100:.1f}%)")

    # Calculate dimension score
    avg_score = np.mean([tier1_complete, cat1_complete])

    print(f"\n{'='*80}")
    print(f"STEM Field Focus Dimension: {avg_score:.1f}% complete")

    standardization_ok = (tier1_unique <= 35 and cat1_unique <= 20)
    status = "[OK]" if avg_score >= 95 and standardization_ok else "[WARNING]"
    print(f"Status: {status}")

    if avg_score < 95:
        action_items['critical'].append({
            'issue': 'STEM Field Focus dimension below 95% complete',
            'current': f'{avg_score:.1f}%',
            'target': '95%+',
            'time_estimate': '1 hour',
            'approach': 'Fill missing stem_field_tier1 or category_tier1'
        })

    readiness_scores['stem_field_focus'] = avg_score

    print("="*80 + "\n")

    return avg_score

def analyze_dimension_4_resource_format(df):
    """Analyze Resource Format dimension"""
    print("DIMENSION 4: RESOURCE FORMAT")
    print("-"*80)

    features = ['category_tier1', 'time_commitment', 'support_level']
    dimension_scores = []

    for feature in features:
        if feature not in df.columns:
            continue

        completeness = df[feature].notna().sum() / len(df) * 100
        print(f"\n{feature}:")
        print(f"  Completeness: {completeness:.1f}%")

        # Value distribution
        value_counts = df[feature].value_counts()
        print(f"  Top 10 values:")
        for val, count in value_counts.head(10).items():
            print(f"    {val}: {count:,} ({count/len(df)*100:.1f}%)")

        dimension_scores.append(completeness)

    avg_score = np.mean(dimension_scores)

    print(f"\n{'='*80}")
    print(f"Resource Format Dimension: {avg_score:.1f}% complete")

    status = "[OK]" if avg_score >= 90 else "[WARNING]"
    print(f"Status: {status}")

    if avg_score < 90:
        action_items['critical'].append({
            'issue': 'Resource Format dimension below 90% complete',
            'current': f'{avg_score:.1f}%',
            'target': '90%+',
            'time_estimate': '1-2 hours',
            'approach': 'Fill missing time_commitment or support_level'
        })

    readiness_scores['resource_format'] = avg_score

    print("="*80 + "\n")

    return avg_score

def analyze_clustering_dimensions(df):
    """Analyze all clustering dimensions"""
    print("="*80)
    print("PHASE 2: ML CLUSTERING DIMENSIONS COMPLETENESS")
    print("="*80)
    print()

    d1 = analyze_dimension_1_accessibility(df)
    d2 = analyze_dimension_2_academic(df)
    d3 = analyze_dimension_3_stem_field(df)
    d4 = analyze_dimension_4_resource_format(df)

    overall = np.mean([d1, d2, d3, d4])

    print("="*80)
    print("OVERALL CLUSTERING READINESS")
    print("="*80)
    print(f"Accessibility Profile: {d1:.1f}%")
    print(f"Academic Level: {d2:.1f}%")
    print(f"STEM Field Focus: {d3:.1f}%")
    print(f"Resource Format: {d4:.1f}%")
    print()
    print(f"OVERALL: {overall:.1f}% complete")
    print("="*80 + "\n")

    readiness_scores['clustering_overall'] = overall

    return overall

# ============================================================================
# PHASE 3: ML PREDICTION QUALITY ASSESSMENT
# ============================================================================

def analyze_ml_predictions(df):
    """Analyze ML prediction quality and confidence"""
    print("="*80)
    print("PHASE 3: ML PREDICTION QUALITY ASSESSMENT")
    print("="*80)
    print()

    predicted_features = []
    for col in df.columns:
        if col.endswith('_predicted'):
            feature_name = col.replace('_predicted', '')
            if feature_name in df.columns:
                predicted_features.append(feature_name)

    all_confidence_scores = []
    low_confidence_resources = []

    for feature in predicted_features:
        pred_col = f'{feature}_predicted'
        conf_col = f'{feature}_confidence'

        print(f"\nFEATURE: {feature}")
        print("-"*80)

        total = len(df)
        predicted = (df[pred_col] == True).sum()
        actual = df[feature].notna().sum() - predicted
        missing = total - df[feature].notna().sum()

        print(f"Total resources: {total:,}")
        print(f"Actual values (not predicted): {actual:,} ({actual/total*100:.1f}%)")
        print(f"Predicted values: {predicted:,} ({predicted/total*100:.1f}%)")
        print(f"Still missing: {missing:,} ({missing/total*100:.1f}%)")

        if conf_col in df.columns and predicted > 0:
            confidence_scores = df.loc[df[pred_col] == True, conf_col]

            print(f"\nConfidence Score Distribution:")
            print(f"  Minimum: {confidence_scores.min():.2%}")
            print(f"  Maximum: {confidence_scores.max():.2%}")
            print(f"  Mean: {confidence_scores.mean():.2%}")
            print(f"  Median: {confidence_scores.median():.2%}")
            print(f"  Std Dev: {confidence_scores.std():.2%}")

            # Confidence buckets
            high_conf = (confidence_scores >= 0.8).sum()
            medium_conf = ((confidence_scores >= 0.7) & (confidence_scores < 0.8)).sum()
            low_conf = ((confidence_scores >= 0.6) & (confidence_scores < 0.7)).sum()
            very_low_conf = (confidence_scores < 0.6).sum()

            print(f"\nConfidence Buckets:")
            print(f"  High (>=0.8): {high_conf:,} ({high_conf/predicted*100:.1f}%)")
            print(f"  Medium (0.7-0.79): {medium_conf:,} ({medium_conf/predicted*100:.1f}%)")
            print(f"  Low (0.6-0.69): {low_conf:,} ({low_conf/predicted*100:.1f}%)")
            print(f"  Very Low (<0.6): {very_low_conf:,} ({very_low_conf/predicted*100:.1f}%)")

            all_confidence_scores.extend(confidence_scores.tolist())

            # Quality assessment
            mean_conf = confidence_scores.mean()
            low_conf_pct = (low_conf + very_low_conf) / predicted * 100

            if mean_conf >= 0.75 and low_conf_pct < 10:
                status = "[OK]"
            elif mean_conf >= 0.65 and low_conf_pct < 20:
                status = "[WARNING]"
            else:
                status = "[CRITICAL]"

            print(f"\nQuality Status: {status}")

            # Collect low confidence predictions
            low_conf_mask = (df[pred_col] == True) & (df[conf_col] < 0.7)
            if low_conf_mask.any():
                low_conf_df = df[low_conf_mask][['name', 'category_tier1', 'cost',
                                                   'location_type', feature, conf_col]].copy()
                low_conf_df['predicted_feature'] = feature
                low_confidence_resources.append(low_conf_df)

            # Sample predictions
            print(f"\nSample HIGH confidence predictions (>= 0.9):")
            high_samples = df[(df[pred_col] == True) & (df[conf_col] >= 0.9)].head(5)
            for idx, row in high_samples.iterrows():
                print(f"  {row['name'][:60]:60s} -> {row[feature]:15s} ({row[conf_col]:.1%})")

            print(f"\nSample LOW confidence predictions (< 0.7):")
            low_samples = df[(df[pred_col] == True) & (df[conf_col] < 0.7)].head(5)
            for idx, row in low_samples.iterrows():
                print(f"  {row['name'][:60]:60s} -> {row[feature]:15s} ({row[conf_col]:.1%})")

    # Overall prediction quality
    if all_confidence_scores:
        avg_confidence = np.mean(all_confidence_scores)
        print(f"\n{'='*80}")
        print(f"OVERALL ML PREDICTION QUALITY")
        print(f"{'='*80}")
        print(f"Average confidence across all predictions: {avg_confidence:.2%}")

        total_low_conf = sum(len(df_chunk) for df_chunk in low_confidence_resources)
        print(f"Total low confidence predictions (< 0.7): {total_low_conf:,}")

        readiness_scores['ml_prediction_confidence'] = avg_confidence

        # Save low confidence predictions
        if low_confidence_resources:
            all_low_conf = pd.concat(low_confidence_resources, ignore_index=True)
            all_low_conf.to_csv(
                OUTPUT_DIR / "quality_issues" / "low_confidence_predictions.csv",
                index=False,
                encoding='utf-8'
            )
            quality_issues['low_confidence_predictions'] = len(all_low_conf)

    print("="*80 + "\n")

# ============================================================================
# PHASE 4: DESCRIPTION & TF-IDF TEXT QUALITY
# ============================================================================

def analyze_description_quality(df):
    """Analyze description and TF-IDF text quality"""
    print("="*80)
    print("PHASE 4: DESCRIPTION & TF-IDF TEXT QUALITY")
    print("="*80)
    print()

    # Word count analysis
    print("DESCRIPTION QUALITY METRICS")
    print("-"*80)

    word_counts = df['word_count']

    print(f"Minimum word count: {word_counts.min()}")
    print(f"Maximum word count: {word_counts.max()}")
    print(f"Mean word count: {word_counts.mean():.1f}")
    print(f"Median word count: {word_counts.median():.1f}")
    print(f"Standard deviation: {word_counts.std():.1f}")
    print()

    # Distribution buckets
    very_short = (word_counts < 20).sum()
    short = ((word_counts >= 20) & (word_counts < 40)).sum()
    adequate = ((word_counts >= 40) & (word_counts < 80)).sum()
    good = ((word_counts >= 80) & (word_counts < 150)).sum()
    excellent = (word_counts >= 150).sum()

    print("Distribution Buckets:")
    print(f"  Very short (<20 words): {very_short:,} ({very_short/len(df)*100:.1f}%)")
    print(f"  Short (20-39 words): {short:,} ({short/len(df)*100:.1f}%)")
    print(f"  Adequate (40-79 words): {adequate:,} ({adequate/len(df)*100:.1f}%)")
    print(f"  Good (80-149 words): {good:,} ({good/len(df)*100:.1f}%)")
    print(f"  Excellent (>=150 words): {excellent:,} ({excellent/len(df)*100:.1f}%)")
    print()

    # Quality assessment
    mean_words = word_counts.mean()
    under_30_pct = (word_counts < 30).sum() / len(df) * 100

    if mean_words >= 50 and under_30_pct < 10:
        status = "[OK]"
    elif mean_words >= 40 and under_30_pct < 20:
        status = "[WARNING]"
    else:
        status = "[CRITICAL]"

    print(f"Quality Status: {status}")

    # Save short descriptions
    short_desc = df[df['word_count'] < 30][['name', 'description', 'word_count']].copy()
    if not short_desc.empty:
        short_desc.to_csv(
            OUTPUT_DIR / "quality_issues" / "short_descriptions.csv",
            index=False,
            encoding='utf-8'
        )
        quality_issues['short_descriptions'] = len(short_desc)

    # TF-IDF text quality
    print(f"\n{'='*80}")
    print("TF-IDF TEXT QUALITY")
    print("-"*80)

    tfidf_complete = df['tfidf_text'].notna().sum() / len(df) * 100
    avg_length = df['tfidf_text'].str.len().mean()

    print(f"Completeness: {tfidf_complete:.1f}%")
    print(f"Average character length: {avg_length:.0f}")
    print()

    print("Sample tfidf_text entries (first 3):")
    for idx, text in df['tfidf_text'].head(3).items():
        print(f"\n{df.loc[idx, 'name']}")
        print(f"  {text[:200]}...")

    readiness_scores['description_quality'] = mean_words

    print("\n" + "="*80 + "\n")

# ============================================================================
# PHASE 5: STANDARDIZATION QUALITY ASSESSMENT
# ============================================================================

def analyze_standardization(df):
    """Analyze standardization quality"""
    print("="*80)
    print("PHASE 5: STANDARDIZATION QUALITY ASSESSMENT")
    print("="*80)
    print()

    # Category standardization
    print("CATEGORY STANDARDIZATION")
    print("-"*80)

    cat_tier1_unique = df['category_tier1'].nunique()
    cat_tier1_complete = df['category_tier1'].notna().sum() / len(df) * 100
    other_count = (df['category_tier1'] == 'Other').sum()
    other_pct = other_count / len(df) * 100

    print(f"Tier 1 Categories:")
    print(f"  Unique values: {cat_tier1_unique} (target: 10-15)")
    print(f"  Completeness: {cat_tier1_complete:.1f}%")
    print(f"  'Other' category: {other_count:,} ({other_pct:.1f}%)")
    print()

    print("All Tier 1 categories:")
    for cat, count in df['category_tier1'].value_counts().items():
        print(f"  {cat:40s} {count:4d} ({count/len(df)*100:.1f}%)")
    print()

    # Quality assessment
    if 10 <= cat_tier1_unique <= 15 and cat_tier1_complete == 100 and other_pct == 0:
        cat_status = "[OK]"
    elif 16 <= cat_tier1_unique <= 20 and cat_tier1_complete >= 95 and other_pct <= 5:
        cat_status = "[WARNING]"
    else:
        cat_status = "[CRITICAL]"

    print(f"Category Standardization Status: {cat_status}")

    # STEM field standardization
    print(f"\n{'='*80}")
    print("STEM FIELD STANDARDIZATION")
    print("-"*80)

    stem_tier1_unique = df['stem_field_tier1'].nunique()
    stem_tier1_complete = df['stem_field_tier1'].notna().sum() / len(df) * 100
    other_stem = df['stem_field_tier1'].str.contains('Other', case=False, na=False).sum()
    other_stem_pct = other_stem / len(df) * 100

    print(f"Tier 1 STEM Fields:")
    print(f"  Unique values: {stem_tier1_unique} (target: 20-30)")
    print(f"  Completeness: {stem_tier1_complete:.1f}%")
    print(f"  Contains 'Other': {other_stem:,} ({other_stem_pct:.1f}%)")
    print()

    print("Top 20 Tier 1 STEM fields:")
    for field, count in df['stem_field_tier1'].value_counts().head(20).items():
        print(f"  {field[:60]:60s} {count:4d} ({count/len(df)*100:.1f}%)")
    print()

    # Quality assessment
    if 20 <= stem_tier1_unique <= 30 and stem_tier1_complete == 100 and other_stem_pct < 5:
        stem_status = "[OK]"
    elif 31 <= stem_tier1_unique <= 40 and stem_tier1_complete >= 95 and other_stem_pct <= 10:
        stem_status = "[WARNING]"
    else:
        stem_status = "[CRITICAL]"

    print(f"STEM Field Standardization Status: {stem_status}")

    # Save distribution analysis
    cat_dist = df['category_tier1'].value_counts().reset_index()
    cat_dist.columns = ['category_tier1', 'count']
    cat_dist['percentage'] = cat_dist['count'] / len(df) * 100
    cat_dist.to_csv(
        OUTPUT_DIR / "distribution_analysis" / "category_tier1_distribution.csv",
        index=False
    )

    stem_dist = df['stem_field_tier1'].value_counts().reset_index()
    stem_dist.columns = ['stem_field_tier1', 'count']
    stem_dist['percentage'] = stem_dist['count'] / len(df) * 100
    stem_dist.to_csv(
        OUTPUT_DIR / "distribution_analysis" / "stem_field_tier1_distribution.csv",
        index=False
    )

    readiness_scores['category_standardization'] = cat_tier1_unique
    readiness_scores['stem_standardization'] = stem_tier1_unique

    print("\n" + "="*80 + "\n")

# ============================================================================
# PHASE 6: LOGICAL CONSISTENCY & DATA QUALITY ISSUES
# ============================================================================

def check_logical_consistency(df):
    """Check for illogical value combinations"""
    print("="*80)
    print("PHASE 6: LOGICAL CONSISTENCY & DATA QUALITY ISSUES")
    print("="*80)
    print()

    illogical_issues = []

    # Check 1: Location vs Transportation
    print("CHECK 1: Location vs Transportation")
    print("-"*80)

    virtual_transport = df[(df['location_type'] == 'Virtual') &
                          (df['transportation_required'] == 'Yes')]

    print(f"Virtual resources requiring transportation: {len(virtual_transport)}")
    if len(virtual_transport) > 0:
        print(f"  Examples:")
        for idx, row in virtual_transport.head(5).iterrows():
            print(f"    - {row['name']}")
        illogical_issues.extend(virtual_transport[['name', 'location_type',
                                                    'transportation_required']].to_dict('records'))

    # Check 2: Cost vs Financial Barrier
    print(f"\n{'='*80}")
    print("CHECK 2: Cost vs Financial Barrier")
    print("-"*80)

    free_high_barrier = df[(df['cost'].str.contains('free', case=False, na=False)) &
                           (df['financial_barrier_level'].isin(['High', 'Medium']))]

    print(f"Free resources with Medium/High financial barrier: {len(free_high_barrier)}")
    if len(free_high_barrier) > 0:
        print(f"  Examples:")
        for idx, row in free_high_barrier.head(5).iterrows():
            print(f"    - {row['name']}: {row['cost']} but barrier={row['financial_barrier_level']}")
        illogical_issues.extend(free_high_barrier[['name', 'cost',
                                                    'financial_barrier_level']].to_dict('records'))

    # Check 3: Category vs Hidden Costs
    print(f"\n{'='*80}")
    print("CHECK 3: Category vs Hidden Costs")
    print("-"*80)

    scholarship_hidden = df[(df['category_tier1'] == 'Scholarship') &
                           (df['hidden_costs_level'].isin(['High', 'Medium']))]

    print(f"Scholarships with Medium/High hidden costs: {len(scholarship_hidden)}")
    if len(scholarship_hidden) > 0:
        print(f"  Examples:")
        for idx, row in scholarship_hidden.head(5).iterrows():
            print(f"    - {row['name']}: hidden_costs={row['hidden_costs_level']}")

    # Check 4: Virtual vs Internet Dependency
    print(f"\n{'='*80}")
    print("CHECK 4: Virtual vs Internet Dependency")
    print("-"*80)

    virtual_low_internet = df[(df['location_type'] == 'Virtual') &
                              (df['internet_dependency'] == 'Low')]

    print(f"Virtual resources with Low internet dependency: {len(virtual_low_internet)}")
    if len(virtual_low_internet) > 0:
        print(f"  Examples:")
        for idx, row in virtual_low_internet.head(5).iterrows():
            print(f"    - {row['name']}")

    # Check 5: Virtual vs Rural Accessibility
    print(f"\n{'='*80}")
    print("CHECK 5: Virtual vs Rural Accessibility")
    print("-"*80)

    virtual_not_rural = df[(df['location_type'] == 'Virtual') &
                           (df['rural_accessible'] == 'No')]

    print(f"Virtual resources not rural accessible: {len(virtual_not_rural)}")
    if len(virtual_not_rural) > 0:
        print(f"  Examples:")
        for idx, row in virtual_not_rural.head(5).iterrows():
            print(f"    - {row['name']}")

    # Overall data quality score
    total_illogical = (len(virtual_transport) + len(free_high_barrier) +
                      len(scholarship_hidden) + len(virtual_low_internet) +
                      len(virtual_not_rural))

    quality_pct = (1 - (total_illogical / len(df))) * 100

    print(f"\n{'='*80}")
    print(f"DATA QUALITY SCORE")
    print(f"{'='*80}")
    print(f"Total illogical combinations: {total_illogical:,}")
    print(f"Percentage of dataset with issues: {(total_illogical/len(df)*100):.1f}%")
    print(f"Data Quality Score: {quality_pct:.1f}%")

    if quality_pct >= 97:
        status = "[OK]"
    elif quality_pct >= 93:
        status = "[WARNING]"
    else:
        status = "[CRITICAL]"

    print(f"Status: {status}")

    readiness_scores['data_quality'] = quality_pct
    quality_issues['illogical_combinations'] = total_illogical

    # Save illogical combinations
    if illogical_issues:
        illogical_df = pd.DataFrame(illogical_issues)
        illogical_df.to_csv(
            OUTPUT_DIR / "quality_issues" / "illogical_combinations.csv",
            index=False,
            encoding='utf-8'
        )

    print("\n" + "="*80 + "\n")

# ============================================================================
# PHASE 7: FEATURE-SPECIFIC DEEP DIVES
# ============================================================================

def feature_deep_dives(df):
    """Perform feature-specific analyses"""
    print("="*80)
    print("PHASE 7: FEATURE-SPECIFIC DEEP DIVES")
    print("="*80)
    print()

    # Cost field analysis
    print("COST FIELD ANALYSIS")
    print("-"*80)
    cost_unique = df['cost'].nunique()
    print(f"Unique cost values: {cost_unique}")
    print(f"\nTop 20 cost values:")
    for cost, count in df['cost'].value_counts().head(20).items():
        print(f"  {cost:40s} {count:4d}")

    # Target grade analysis
    print(f"\n{'='*80}")
    print("TARGET GRADE ANALYSIS")
    print("-"*80)
    grade_unique = df['target_grade'].nunique()
    print(f"Unique target_grade values: {grade_unique}")
    print(f"\nAll target_grade values:")
    for grade, count in df['target_grade'].value_counts().items():
        print(f"  {grade:20s} {count:4d} ({count/len(df)*100:.1f}%)")

    # Save distribution
    grade_dist = df['target_grade'].value_counts().reset_index()
    grade_dist.columns = ['target_grade', 'count']
    grade_dist['percentage'] = grade_dist['count'] / len(df) * 100
    grade_dist.to_csv(
        OUTPUT_DIR / "distribution_analysis" / "target_grade_distribution.csv",
        index=False
    )

    # Regional availability
    print(f"\n{'='*80}")
    print("REGIONAL AVAILABILITY ANALYSIS")
    print("-"*80)
    regional_complete = df['regional_availability'].notna().sum() / len(df) * 100
    print(f"Completeness: {regional_complete:.1f}%")
    print(f"\nTop 15 regional availability values:")
    for region, count in df['regional_availability'].value_counts().head(15).items():
        print(f"  {region:30s} {count:4d}")

    print("\n" + "="*80 + "\n")

# ============================================================================
# PHASE 8: ML PIPELINE READINESS SCORE
# ============================================================================

def calculate_readiness_score():
    """Calculate overall ML pipeline readiness score (0-100)"""
    print("="*80)
    print("PHASE 8: ML PIPELINE READINESS SCORE CALCULATION")
    print("="*80)
    print()

    total_score = 0
    max_score = 100

    # Clustering Dimensions Completeness (40 points)
    print("CLUSTERING DIMENSIONS COMPLETENESS (40 points)")
    print("-"*80)

    accessibility = readiness_scores.get('accessibility_profile', 0)
    academic = readiness_scores.get('academic_level', 0)
    stem = readiness_scores.get('stem_field_focus', 0)
    resource = readiness_scores.get('resource_format', 0)

    dim_scores = {
        'Accessibility Profile': (accessibility / 100) * 10,
        'Academic Level': (academic / 100) * 10,
        'STEM Field Focus': (stem / 100) * 10,
        'Resource Format': (resource / 100) * 10
    }

    for dim, score in dim_scores.items():
        print(f"  {dim:30s} {score:5.1f} / 10.0 points")
        total_score += score

    # ML Prediction Quality (20 points)
    print(f"\n{'='*80}")
    print("ML PREDICTION QUALITY (20 points)")
    print("-"*80)

    avg_confidence = readiness_scores.get('ml_prediction_confidence', 0)
    if avg_confidence >= 0.75:
        pred_score = 20
    elif avg_confidence >= 0.65:
        pred_score = 12
    else:
        pred_score = 5

    print(f"  Average confidence: {avg_confidence:.2%}")
    print(f"  Score: {pred_score:.1f} / 20.0 points")
    total_score += pred_score

    # Standardization Quality (20 points)
    print(f"\n{'='*80}")
    print("STANDARDIZATION QUALITY (20 points)")
    print("-"*80)

    cat_unique = readiness_scores.get('category_standardization', 99)
    stem_unique = readiness_scores.get('stem_standardization', 99)

    if 10 <= cat_unique <= 15:
        cat_score = 10
    elif 16 <= cat_unique <= 20:
        cat_score = 7
    else:
        cat_score = 3

    if 20 <= stem_unique <= 30:
        stem_score = 10
    elif 31 <= stem_unique <= 40:
        stem_score = 7
    else:
        stem_score = 3

    print(f"  Category tier1 ({cat_unique} unique): {cat_score:.1f} / 10.0 points")
    print(f"  STEM field tier1 ({stem_unique} unique): {stem_score:.1f} / 10.0 points")
    total_score += cat_score + stem_score

    # Description/TF-IDF Quality (10 points)
    print(f"\n{'='*80}")
    print("DESCRIPTION/TF-IDF QUALITY (10 points)")
    print("-"*80)

    mean_words = readiness_scores.get('description_quality', 0)
    if mean_words >= 50:
        desc_score = 10
    elif mean_words >= 40:
        desc_score = 7
    else:
        desc_score = 3

    print(f"  Mean word count: {mean_words:.1f}")
    print(f"  Score: {desc_score:.1f} / 10.0 points")
    total_score += desc_score

    # Data Quality/Consistency (10 points)
    print(f"\n{'='*80}")
    print("DATA QUALITY/CONSISTENCY (10 points)")
    print("-"*80)

    quality_pct = readiness_scores.get('data_quality', 0)
    if quality_pct >= 97:
        quality_score = 10
    elif quality_pct >= 93:
        quality_score = 6
    else:
        quality_score = 2

    print(f"  Data quality: {quality_pct:.1f}%")
    print(f"  Score: {quality_score:.1f} / 10.0 points")
    total_score += quality_score

    # Final score
    print(f"\n{'='*80}")
    print(f"TOTAL READINESS SCORE: {total_score:.1f} / {max_score} points")
    print(f"{'='*80}")

    # Readiness assessment
    if total_score >= 90:
        status = "READY FOR ML PIPELINE"
        symbol = "[OK]"
        recommendation = "All systems go! Proceed with ML pipeline development with confidence."
    elif total_score >= 75:
        status = "MOSTLY READY - Minor Fixes Needed"
        symbol = "[WARNING]"
        recommendation = "2-4 hours of targeted fixes required. Address critical items before proceeding."
    elif total_score >= 60:
        status = "NEEDS WORK - Medium Refinement Required"
        symbol = "[WARNING][WARNING]"
        recommendation = "5-8 hours of work required. Do NOT proceed until gaps are addressed."
    else:
        status = "NOT READY - Major Issues"
        symbol = "[CRITICAL]"
        recommendation = "10+ hours of work required. Must address fundamental issues before any ML work."

    print(f"\nStatus: {symbol} {status}")
    print(f"\nRecommendation: {recommendation}")
    print()

    readiness_scores['total_score'] = total_score
    readiness_scores['status'] = status
    readiness_scores['recommendation'] = recommendation

    return total_score, status

# ============================================================================
# PHASE 9: DETAILED ACTION ITEMS REPORT
# ============================================================================

def generate_action_items():
    """Generate prioritized action items"""
    print("="*80)
    print("PHASE 9: DETAILED ACTION ITEMS")
    print("="*80)
    print()

    # Critical items
    if action_items['critical']:
        print("CRITICAL (Must Fix Before ML Pipeline)")
        print("-"*80)
        for i, item in enumerate(action_items['critical'], 1):
            print(f"\n{i}. {item['issue']}")
            print(f"   Current: {item['current']}")
            print(f"   Target: {item['target']}")
            print(f"   Est. Time: {item['time_estimate']}")
            print(f"   Approach: {item['approach']}")
    else:
        print("CRITICAL: None - Excellent!")

    # High priority
    print(f"\n{'='*80}")
    if action_items['high']:
        print("HIGH PRIORITY (Should Fix Soon)")
        print("-"*80)
        for i, item in enumerate(action_items['high'], 1):
            print(f"\n{i}. {item['issue']}")
            print(f"   Current: {item['current']}")
            print(f"   Target: {item['target']}")
            print(f"   Est. Time: {item['time_estimate']}")
            print(f"   Approach: {item['approach']}")
    else:
        print("HIGH PRIORITY: None - Great!")

    print("\n" + "="*80 + "\n")

# ============================================================================
# PHASE 10: GENERATE COMPREHENSIVE REPORTS
# ============================================================================

def generate_executive_summary():
    """Generate executive summary report"""

    lines = []
    lines.append("="*80)
    lines.append("BLACK MINDS IN STEM - ML PIPELINE READINESS REPORT")
    lines.append("="*80)
    lines.append("")

    total_score = readiness_scores.get('total_score', 0)
    status = readiness_scores.get('status', 'UNKNOWN')

    lines.append(f"OVERALL READINESS SCORE: {total_score:.1f} / 100 points")
    lines.append("")
    lines.append(f"Status: {status}")
    lines.append("")

    lines.append("="*80)
    lines.append("CLUSTERING DIMENSIONS COMPLETENESS")
    lines.append("="*80)

    accessibility = readiness_scores.get('accessibility_profile', 0)
    academic = readiness_scores.get('academic_level', 0)
    stem = readiness_scores.get('stem_field_focus', 0)
    resource = readiness_scores.get('resource_format', 0)

    symbol_a = "[OK]" if accessibility >= 90 else "[WARNING]"
    symbol_ac = "[OK]" if academic >= 90 else "[WARNING]"
    symbol_s = "[OK]" if stem >= 95 else "[WARNING]"
    symbol_r = "[OK]" if resource >= 90 else "[WARNING]"

    lines.append(f"{symbol_a} Accessibility Profile: {accessibility:.1f}% complete")
    lines.append(f"{symbol_ac} Academic Level: {academic:.1f}% complete")
    lines.append(f"{symbol_s} STEM Field Focus: {stem:.1f}% complete")
    lines.append(f"{symbol_r} Resource Format: {resource:.1f}% complete")
    lines.append("")
    lines.append(f"Overall: {np.mean([accessibility, academic, stem, resource]):.1f}% average completeness")
    lines.append("")

    lines.append("="*80)
    lines.append("ML PREDICTION QUALITY")
    lines.append("="*80)

    avg_conf = readiness_scores.get('ml_prediction_confidence', 0)
    conf_symbol = "[OK]" if avg_conf >= 0.75 else "[WARNING]"

    lines.append(f"{conf_symbol} Average Confidence: {avg_conf:.2%}")

    low_conf_count = quality_issues.get('low_confidence_predictions', 0)
    lines.append(f"Low Confidence Predictions: {low_conf_count:,} resources need manual review")
    lines.append("")

    lines.append("="*80)
    lines.append("STANDARDIZATION QUALITY")
    lines.append("="*80)

    cat_unique = readiness_scores.get('category_standardization', 0)
    stem_unique = readiness_scores.get('stem_standardization', 0)

    cat_symbol = "[OK]" if 10 <= cat_unique <= 15 else "[WARNING]"
    stem_symbol = "[OK]" if 20 <= stem_unique <= 30 else "[WARNING]"

    lines.append(f"{cat_symbol} Tier 1 Categories: {cat_unique} unique (target: 10-15)")
    lines.append(f"{stem_symbol} Tier 1 STEM Fields: {stem_unique} unique (target: 20-30)")
    lines.append("")

    lines.append("="*80)
    lines.append("DESCRIPTION QUALITY")
    lines.append("="*80)

    mean_words = readiness_scores.get('description_quality', 0)
    desc_symbol = "[OK]" if mean_words >= 50 else "[WARNING]"

    short_count = quality_issues.get('short_descriptions', 0)

    lines.append(f"{desc_symbol} Average Word Count: {mean_words:.1f} words")
    lines.append(f"Under 30 words: {short_count:,} resources")
    lines.append("")

    lines.append("="*80)
    lines.append("DATA QUALITY")
    lines.append("="*80)

    quality_pct = readiness_scores.get('data_quality', 0)
    quality_symbol = "[OK]" if quality_pct >= 97 else "[WARNING]"

    illogical_count = quality_issues.get('illogical_combinations', 0)

    lines.append(f"{quality_symbol} Logical Consistency: {quality_pct:.1f}%")
    lines.append(f"Total Issues Found: {illogical_count:,} resources")
    lines.append("")

    lines.append("="*80)
    lines.append("CRITICAL ACTION ITEMS")
    lines.append("="*80)

    if action_items['critical']:
        for item in action_items['critical']:
            lines.append(f"- {item['issue']} ({item['time_estimate']})")
    else:
        lines.append("None - Dataset is ready!")

    lines.append("")
    lines.append("="*80)
    lines.append("RECOMMENDATION")
    lines.append("="*80)

    recommendation = readiness_scores.get('recommendation', '')
    lines.append(recommendation)
    lines.append("")

    if action_items['critical']:
        total_time = sum(
            int(item['time_estimate'].split('-')[0])
            for item in action_items['critical']
        )
        lines.append(f"Estimated time to address critical issues: {total_time}+ hours")
    else:
        lines.append("No critical issues - proceed immediately!")

    lines.append("")
    lines.append("="*80)

    report_text = '\n'.join(lines)

    # Save executive summary
    with open(OUTPUT_DIR / "ml_readiness_summary.txt", 'w', encoding='utf-8') as f:
        f.write(report_text)

    print(report_text)
    print()

# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """Main execution function"""

    # Phase 1: Load and analyze dataset
    df = load_and_analyze_dataset()

    # Phase 2: Analyze clustering dimensions
    analyze_clustering_dimensions(df)

    # Phase 3: Analyze ML predictions
    analyze_ml_predictions(df)

    # Phase 4: Analyze descriptions
    analyze_description_quality(df)

    # Phase 5: Analyze standardization
    analyze_standardization(df)

    # Phase 6: Check logical consistency
    check_logical_consistency(df)

    # Phase 7: Feature deep dives
    feature_deep_dives(df)

    # Phase 8: Calculate readiness score
    calculate_readiness_score()

    # Phase 9: Generate action items
    generate_action_items()

    # Phase 10: Generate executive summary
    generate_executive_summary()

    print("="*80)
    print("ML PIPELINE READINESS VALIDATION COMPLETE!")
    print("="*80)
    print(f"\nAll reports saved to: {OUTPUT_DIR}")
    print("="*80)

if __name__ == "__main__":
    main()
