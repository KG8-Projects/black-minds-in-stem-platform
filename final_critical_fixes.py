"""
Black Minds in STEM: Final Critical Fixes & Validation
Addresses critical issues before ML pipeline development

CRITICAL FIXES:
1. Target grade standardization - preserve specificity (not 72% K-12!)
2. ML prediction validation - assess reliability
3. Description quality - identify thin descriptions
4. Final validation - GO/NO-GO decision

Target: 80+ readiness score, <20% K-12, reliable predictions
"""

import pandas as pd
import numpy as np
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# Paths
BASE_DIR = Path(r"C:\Users\u_wos\Downloads\Black Minds In STEM")
INPUT_FILE = BASE_DIR / "ml_ready_data" / "bmis_ml_ready_dataset_fixed.csv"
ORIGINAL_FILE = BASE_DIR / "ml_ready_data" / "bmis_ml_ready_dataset.csv"  # For original target_grade
OUTPUT_DIR = BASE_DIR / "final_ml_ready_data"
MANUAL_REVIEW_DIR = OUTPUT_DIR / "manual_review"
VALIDATION_DIR = OUTPUT_DIR / "validation_reports"

# Create directories
OUTPUT_DIR.mkdir(exist_ok=True)
MANUAL_REVIEW_DIR.mkdir(exist_ok=True)
VALIDATION_DIR.mkdir(exist_ok=True)

print("="*80)
print("BLACK MINDS IN STEM - FINAL CRITICAL FIXES & VALIDATION")
print("="*80)
print()

# ============================================================================
# PHASE 1: TARGET GRADE STANDARDIZATION FIX (CRITICAL)
# ============================================================================

def analyze_current_target_grade(df):
    """Analyze current problematic target_grade distribution"""
    print("="*80)
    print("PHASE 1: TARGET GRADE STANDARDIZATION FIX")
    print("="*80)
    print()

    print("CURRENT STATE ANALYSIS")
    print("-"*80)

    unique_count = df['target_grade'].nunique()
    k12_count = (df['target_grade'] == 'K-12').sum()
    k12_pct = (k12_count / len(df)) * 100

    print(f"Unique target_grade values: {unique_count}")
    print(f"Resources marked K-12: {k12_count} ({k12_pct:.1f}%)")
    print(f"\nPROBLEM: {k12_pct:.1f}% marked K-12 is TOO BROAD!")
    print(f"Target: 15-20% should be K-12 (truly all-grade resources)")
    print()

    print("Current distribution (top 15):")
    for grade, count in df['target_grade'].value_counts().head(15).items():
        pct = (count / len(df)) * 100
        print(f"  {grade:15s} {count:5d} ({pct:5.1f}%)")

    print()
    return k12_pct

def load_original_target_grades(df):
    """Load original target_grade values before aggressive standardization"""
    print("LOADING ORIGINAL TARGET_GRADE VALUES")
    print("-"*80)

    try:
        df_orig = pd.read_csv(ORIGINAL_FILE)
        # Create mapping from name to original target_grade
        orig_grades = dict(zip(df_orig['name'], df_orig['target_grade']))
        df['target_grade_original'] = df['name'].map(orig_grades)

        print(f"Successfully loaded {len(orig_grades):,} original target_grade values")
        print(f"Unique original values: {df['target_grade_original'].nunique()}")
        print()

        return df
    except Exception as e:
        print(f"Warning: Could not load original values: {e}")
        df['target_grade_original'] = df['target_grade']
        return df

def standardize_target_grade_conservative(row):
    """
    Context-aware conservative standardization preserving specificity

    Principles:
    1. Preserve specificity - don't broaden unnecessarily
    2. Use context from category, prerequisite_level, description
    3. Only use K-12 if truly appropriate for ALL grades
    """

    # Get original value and context
    original = str(row.get('target_grade_original', row.get('target_grade', ''))).strip().upper()
    category = str(row.get('category', '')).upper()
    prereq = str(row.get('prerequisite_level', '')).upper()
    name = str(row.get('name', '')).upper()
    desc = str(row.get('description', ''))[:200].upper()  # First 200 chars

    if pd.isna(original) or original == '' or original == 'NAN':
        return 'K-12'  # Default for missing

    # Remove common noise
    grade = original.replace('GRADES ', '').replace('GRADE ', '')
    grade = grade.replace('TH', '').replace('ST', '').replace('ND', '').replace('RD', '')

    # ========================================================================
    # CONTEXT-BASED OVERRIDE LOGIC (prevents over-broadening)
    # ========================================================================

    # High school/senior indicators - NEVER map these to K-12
    senior_indicators = ['SCHOLARSHIP', 'RESEARCH', 'INTERNSHIP', 'COLLEGE PREP',
                        'UNIVERSITY', 'UNDERGRADUATE', 'SAT', 'ACT', 'AP ',
                        'COLLEGE', 'UPPERCLASS']

    if any(ind in category for ind in senior_indicators) or \
       any(ind in name for ind in senior_indicators):
        # This is clearly high school focused
        if 'JUNIOR' in name or 'SENIOR' in name or '11' in original or '12' in original:
            return '11-12'
        # Default to general high school
        return '9-12'

    # Advanced prerequisite - likely not K-12
    if prereq in ['ADVANCED', 'HIGH']:
        if any(ind in category for ind in ['SCHOLARSHIP', 'RESEARCH']):
            return '11-12'
        return '9-12'

    # Elementary indicators
    elementary_indicators = ['ELEMENTARY', 'KINDERGARTEN', 'PRESCHOOL', 'PRE-K',
                            'YOUNG CHILDREN', 'EARLY CHILDHOOD']
    if any(ind in category for ind in elementary_indicators) or \
       any(ind in name for ind in elementary_indicators):
        return 'K-5'

    # Middle school indicators
    middle_indicators = ['MIDDLE SCHOOL', 'JUNIOR HIGH']
    if any(ind in category for ind in middle_indicators) or \
       any(ind in name for ind in middle_indicators):
        return '6-8'

    # ========================================================================
    # STANDARDIZATION MAPPING (format normalization)
    # ========================================================================

    # Exact matches to preserve
    if grade in ['9-12', '10-12', '11-12', '6-8', 'K-5', 'K-8', '6-12', '7-12', '8-12']:
        return grade

    # PreK variations
    if 'PREK' in grade or 'PRE-K' in grade:
        if '-1' in grade or '-K' in grade:
            return 'PreK-1'
        if '-2' in grade:
            return 'PreK-2'
        if '-3' in grade:
            return 'PreK-3'
        if '-5' in grade:
            return 'K-5'
        return 'PreK'

    # Elementary ranges
    if grade in ['K-5', 'K-4', 'K-3', 'K-2', 'K-1']:
        return 'K-5'
    if grade in ['1-5', '2-5', '3-5', '4-5']:
        return 'K-5'

    # Elementary + Middle
    if grade in ['K-8', '1-8', '2-8', '3-8', '4-8', '5-8']:
        return 'K-8'

    # Middle school ranges
    if grade in ['6-8', '6-7', '7-8']:
        return '6-8'

    # Middle + High overlaps
    if grade in ['6-9', '7-9', '6-10', '7-10']:
        return '6-8'  # More middle school focused

    # Cross-level spans (middle + high)
    if grade in ['6-12', '7-12', '8-12']:
        # Keep as-is if already specific
        if '6-12' in original:
            return '6-12'
        if '7-12' in original:
            return '7-12'
        if '8-12' in original:
            return '8-12'
        return '6-12'

    # High school ranges
    if grade in ['9-12']:
        return '9-12'
    if grade in ['9-10', '9-11']:
        return '9-10'
    if grade in ['10-11', '10-12']:
        return '10-12'
    if grade in ['11-12']:
        return '11-12'

    # Post-secondary
    if 'COLLEGE' in grade or 'UNIVERSITY' in grade or 'UNDERGRADUATE' in grade:
        return '12+'
    if 'ALUMNI' in grade:
        return '12+'

    # Single grades - keep as-is if specific
    if grade in ['K', 'KINDERGARTEN']:
        return 'K'
    if grade.isdigit():
        grade_num = int(grade)
        if 1 <= grade_num <= 5:
            # Elementary single grade - be specific if context supports it
            if 'SPECIFIC' in category or grade_num >= 3:
                return str(grade_num)
            return 'K-5'
        if 6 <= grade_num <= 8:
            # Middle school single grade
            return str(grade_num) if grade_num >= 7 else '6-8'
        if 9 <= grade_num <= 12:
            # High school single grade - keep specific
            return str(grade_num)
        if grade_num > 12:
            return '12+'

    # Age-based conversions
    if 'AGE' in grade or 'AGES' in grade:
        if '5-10' in grade or '5-11' in grade:
            return 'K-5'
        if '11-13' in grade or '11-14' in grade or '10-13' in grade:
            return '6-8'
        if '14-18' in grade or '13-18' in grade:
            return '9-12'

    # Keyword-based mapping
    keyword_map = {
        'ELEMENTARY': 'K-5',
        'MIDDLE SCHOOL': '6-8',
        'JUNIOR HIGH': '6-8',
        'HIGH SCHOOL': '9-12',
        'SECONDARY': '9-12',
        'TEEN': '9-12',
        'TEENAGE': '9-12'
    }

    for keyword, value in keyword_map.items():
        if keyword in grade:
            return value

    # K-12 patterns - ONLY if explicitly "all grades" or appropriate
    if grade in ['K-12', 'K THROUGH 12', 'KINDERGARTEN-12', 'ALL GRADES', 'ALL']:
        # Double-check context before allowing K-12
        if any(ind in category for ind in ['SCHOLARSHIP', 'RESEARCH', 'INTERNSHIP']):
            return '9-12'  # Override - not truly K-12
        if 'ADVANCED' in prereq or 'HIGH' in prereq:
            return '9-12'  # Override
        # Truly seems to be all grades
        return 'K-12'

    # Elementary + Middle + High (1-12, 2-12, 3-12, etc.)
    if '-12' in grade and any(d in grade.split('-')[0] for d in '123456789'):
        start_grade = grade.split('-')[0]
        if start_grade.isdigit():
            start_num = int(start_grade)
            if start_num <= 3:
                # 1-12, 2-12, 3-12 -> probably K-12
                # But check context
                if any(ind in category for ind in ['SCHOLARSHIP', 'RESEARCH']):
                    return '9-12'
                return 'K-12'
            elif start_num <= 5:
                # 4-12, 5-12 -> probably K-12
                return 'K-12'
            elif start_num <= 8:
                # 6-12, 7-12, 8-12 -> keep specific
                return f"{start_num}-12"
            else:
                # 9-12, 10-12, 11-12
                return f"{start_num}-12"

    # Default fallback - use original if it looks reasonable
    if len(grade) <= 10 and not any(c in grade for c in ['?', '!', '@']):
        return grade

    # Last resort
    return 'K-12'

def apply_target_grade_standardization(df):
    """Apply conservative standardization to preserve specificity"""
    print("APPLYING CONSERVATIVE STANDARDIZATION")
    print("-"*80)

    # Apply standardization
    df['target_grade_standardized'] = df.apply(standardize_target_grade_conservative, axis=1)

    unique_count = df['target_grade_standardized'].nunique()
    k12_count = (df['target_grade_standardized'] == 'K-12').sum()
    k12_pct = (k12_count / len(df)) * 100

    print(f"\nRESULTS:")
    print(f"  Unique standardized values: {unique_count}")
    print(f"  Resources marked K-12: {k12_count} ({k12_pct:.1f}%)")

    if k12_pct <= 20:
        print(f"  [OK] K-12 percentage is {k12_pct:.1f}% (target: 15-20%)")
    elif k12_pct <= 25:
        print(f"  [WARNING] K-12 percentage is {k12_pct:.1f}% (target: 15-20%, acceptable up to 25%)")
    else:
        print(f"  [CRITICAL] K-12 percentage is {k12_pct:.1f}% (still too high!)")

    print("\nDistribution after conservative standardization (top 20):")
    for grade, count in df['target_grade_standardized'].value_counts().head(20).items():
        pct = (count / len(df)) * 100
        print(f"  {grade:15s} {count:5d} ({pct:5.1f}%)")

    print()
    return df

def validate_target_grade_samples(df):
    """Sample and validate standardization quality"""
    print("VALIDATION SAMPLES")
    print("-"*80)

    # Sample K-12 resources
    k12_sample = df[df['target_grade_standardized'] == 'K-12'].sample(min(5, len(df[df['target_grade_standardized'] == 'K-12'])))
    print("\nSample resources marked K-12 (should be truly all-grade appropriate):")
    for idx, row in k12_sample.iterrows():
        print(f"  - {row['name'][:60]}")
        print(f"    Category: {row['category']}, Prerequisite: {row['prerequisite_level']}")
        print(f"    Original grade: {row.get('target_grade_original', 'N/A')}")

    # Sample 11-12 resources
    senior_sample = df[df['target_grade_standardized'] == '11-12'].sample(min(5, len(df[df['target_grade_standardized'] == '11-12'])))
    print("\nSample resources marked 11-12 (should be senior-focused):")
    for idx, row in senior_sample.iterrows():
        print(f"  - {row['name'][:60]}")
        print(f"    Category: {row['category']}, Prerequisite: {row['prerequisite_level']}")
        print(f"    Original grade: {row.get('target_grade_original', 'N/A')}")

    # Sample 9-12 resources
    hs_sample = df[df['target_grade_standardized'] == '9-12'].sample(min(5, len(df[df['target_grade_standardized'] == '9-12'])))
    print("\nSample resources marked 9-12 (should be high school general):")
    for idx, row in hs_sample.iterrows():
        print(f"  - {row['name'][:60]}")
        print(f"    Category: {row['category']}, Prerequisite: {row['prerequisite_level']}")
        print(f"    Original grade: {row.get('target_grade_original', 'N/A')}")

    print("\n" + "="*80 + "\n")

# ============================================================================
# PHASE 2: ML PREDICTION VALIDATION
# ============================================================================

def analyze_prediction_confidence(df):
    """Analyze ML prediction confidence distribution"""
    print("="*80)
    print("PHASE 2: ML PREDICTION VALIDATION & QUALITY ASSESSMENT")
    print("="*80)
    print()

    predicted_features = ['financial_barrier_level', 'hidden_costs_level', 'internet_dependency']

    all_confidence_scores = []
    prediction_analysis = {}

    for feature in predicted_features:
        pred_col = f'{feature}_predicted'
        conf_col = f'{feature}_confidence'

        if pred_col not in df.columns or conf_col not in df.columns:
            continue

        print(f"FEATURE: {feature}")
        print("-"*80)

        # Get predictions
        predicted_mask = df[pred_col] == True
        predicted_count = predicted_mask.sum()

        if predicted_count == 0:
            print("No predictions found for this feature\n")
            continue

        confidences = df.loc[predicted_mask, conf_col]

        # Confidence buckets
        very_high = (confidences >= 0.8).sum()
        high = ((confidences >= 0.7) & (confidences < 0.8)).sum()
        medium = ((confidences >= 0.6) & (confidences < 0.7)).sum()
        low = ((confidences >= 0.5) & (confidences < 0.6)).sum()
        very_low = (confidences < 0.5).sum()

        print(f"Total predictions: {predicted_count:,}")
        print(f"\nConfidence Distribution:")
        print(f"  Very High (>=0.8): {very_high:5d} ({very_high/predicted_count*100:5.1f}%)")
        print(f"  High (0.7-0.79):   {high:5d} ({high/predicted_count*100:5.1f}%)")
        print(f"  Medium (0.6-0.69): {medium:5d} ({medium/predicted_count*100:5.1f}%)")
        print(f"  Low (0.5-0.59):    {low:5d} ({low/predicted_count*100:5.1f}%)")
        print(f"  Very Low (<0.5):   {very_low:5d} ({very_low/predicted_count*100:5.1f}%)")

        print(f"\nConfidence Statistics:")
        print(f"  Mean: {confidences.mean():.2%}")
        print(f"  Median: {confidences.median():.2%}")
        print(f"  Std Dev: {confidences.std():.2%}")
        print(f"  Min: {confidences.min():.2%}")
        print(f"  Max: {confidences.max():.2%}")

        all_confidence_scores.extend(confidences.tolist())

        prediction_analysis[feature] = {
            'total': predicted_count,
            'mean_confidence': confidences.mean(),
            'high_confidence_count': very_high + high,
            'low_confidence_count': low + very_low
        }

        print()

    # Overall summary
    if all_confidence_scores:
        overall_avg = np.mean(all_confidence_scores)
        print("="*80)
        print(f"OVERALL PREDICTION QUALITY")
        print("="*80)
        print(f"Average confidence across all predictions: {overall_avg:.2%}")

        if overall_avg >= 0.75:
            print("[OK] High quality predictions")
        elif overall_avg >= 0.65:
            print("[WARNING] Moderate quality predictions")
        else:
            print("[CRITICAL] Low quality predictions - filtering recommended")

    print("\n" + "="*80 + "\n")

    return prediction_analysis

def create_reliability_flags(df):
    """Create reliability flags for predictions based on confidence thresholds"""
    print("CREATING RELIABILITY FLAGS")
    print("-"*80)

    confidence_threshold = 0.70  # Only trust predictions with >=70% confidence

    predicted_features = ['financial_barrier_level', 'hidden_costs_level', 'internet_dependency']

    for feature in predicted_features:
        pred_col = f'{feature}_predicted'
        conf_col = f'{feature}_confidence'

        if pred_col not in df.columns:
            continue

        # High confidence flag
        df[f'{feature}_high_confidence'] = ((df[pred_col] == True) &
                                             (df[conf_col] >= confidence_threshold))

        # Reliable flag (actual value OR high confidence prediction)
        df[f'{feature}_reliable'] = ((df[pred_col] == False) |  # Actual value
                                      (df[f'{feature}_high_confidence'] == True))  # High conf prediction

        # Count results
        total = len(df)
        actual = (df[pred_col] == False).sum()
        high_conf_pred = df[f'{feature}_high_confidence'].sum()
        low_conf_pred = ((df[pred_col] == True) & (df[conf_col] < confidence_threshold)).sum()
        reliable = df[f'{feature}_reliable'].sum()

        print(f"\n{feature}:")
        print(f"  Actual values: {actual:,} ({actual/total*100:.1f}%)")
        print(f"  High confidence predictions (>=70%): {high_conf_pred:,} ({high_conf_pred/total*100:.1f}%)")
        print(f"  Low confidence predictions (<70%): {low_conf_pred:,} ({low_conf_pred/total*100:.1f}%)")
        print(f"  RELIABLE total: {reliable:,} ({reliable/total*100:.1f}%)")

    print("\n" + "="*80 + "\n")

    return df

# ============================================================================
# PHASE 3: DESCRIPTION QUALITY ASSESSMENT
# ============================================================================

def assess_description_quality(df):
    """Assess description quality and identify thin descriptions"""
    print("="*80)
    print("PHASE 3: DESCRIPTION QUALITY ASSESSMENT")
    print("="*80)
    print()

    print("WORD COUNT DISTRIBUTION")
    print("-"*80)

    word_counts = df['word_count']

    print(f"Statistics:")
    print(f"  Minimum: {word_counts.min()}")
    print(f"  Maximum: {word_counts.max()}")
    print(f"  Mean: {word_counts.mean():.1f}")
    print(f"  Median: {word_counts.median():.1f}")
    print(f"  Std Dev: {word_counts.std():.1f}")

    print(f"\nPercentiles:")
    print(f"  10th: {word_counts.quantile(0.10):.0f}")
    print(f"  25th: {word_counts.quantile(0.25):.0f}")
    print(f"  50th: {word_counts.quantile(0.50):.0f}")
    print(f"  75th: {word_counts.quantile(0.75):.0f}")
    print(f"  90th: {word_counts.quantile(0.90):.0f}")

    # Distribution buckets
    very_short = (word_counts < 20).sum()
    short = ((word_counts >= 20) & (word_counts < 30)).sum()
    borderline = ((word_counts >= 30) & (word_counts < 40)).sum()
    adequate = ((word_counts >= 40) & (word_counts < 60)).sum()
    good = ((word_counts >= 60) & (word_counts < 100)).sum()
    excellent = (word_counts >= 100).sum()

    total = len(df)

    print(f"\nDistribution Buckets:")
    print(f"  Very Short (<20):  {very_short:5d} ({very_short/total*100:5.1f}%)")
    print(f"  Short (20-29):     {short:5d} ({short/total*100:5.1f}%)")
    print(f"  Borderline (30-39):{borderline:5d} ({borderline/total*100:5.1f}%)")
    print(f"  Adequate (40-59):  {adequate:5d} ({adequate/total*100:5.1f}%)")
    print(f"  Good (60-99):      {good:5d} ({good/total*100:5.1f}%)")
    print(f"  Excellent (>=100): {excellent:5d} ({excellent/total*100:5.1f}%)")

    under_30_pct = (very_short + short) / total * 100

    print(f"\nQUALITY ASSESSMENT:")
    print(f"  Under 30 words: {very_short + short:,} ({under_30_pct:.1f}%)")

    if under_30_pct < 10:
        print("  [OK] Description quality is good")
        status = "ACCEPTABLE"
    elif under_30_pct < 20:
        print("  [WARNING] Description quality is borderline")
        status = "BORDERLINE"
    else:
        print("  [CRITICAL] Description quality needs work")
        status = "NEEDS_WORK"

    # Identify thin descriptions
    thin_desc = df[df['word_count'] < 30][['name', 'category', 'description', 'word_count',
                                            'stem_fields', 'target_grade_standardized']].copy()
    thin_desc = thin_desc.sort_values(['category', 'word_count'])

    if len(thin_desc) > 0:
        print(f"\nThin descriptions by category:")
        category_counts = thin_desc['category'].value_counts()
        for cat, count in category_counts.head(10).items():
            print(f"  {cat:30s} {count:3d}")

        # Save for manual review
        thin_desc.to_csv(MANUAL_REVIEW_DIR / "thin_descriptions.csv", index=False)
        print(f"\nSaved {len(thin_desc)} thin descriptions to manual_review/thin_descriptions.csv")

    print("\n" + "="*80 + "\n")

    return status, under_30_pct

# ============================================================================
# PHASE 4: COMPREHENSIVE FINAL VALIDATION
# ============================================================================

def calculate_final_clustering_completeness(df):
    """Calculate clustering dimensions completeness with reliability flags"""
    print("="*80)
    print("PHASE 4: COMPREHENSIVE FINAL VALIDATION")
    print("="*80)
    print()

    print("CLUSTERING DIMENSIONS COMPLETENESS (WITH RELIABILITY)")
    print("-"*80)

    # Dimension 1: Accessibility Profile
    print("\nDIMENSION 1: ACCESSIBILITY PROFILE")
    acc_features = {
        'financial_barrier_level_reliable': 10,
        'hidden_costs_level_reliable': 10,
        'cost_category': 8,
        'location_type': 7,
        'transportation_required': 7,
        'rural_accessible': 7,
        'internet_dependency_reliable': 6
    }

    acc_scores = []
    for feature, weight in acc_features.items():
        if feature in df.columns:
            if feature.endswith('_reliable'):
                completeness = (df[feature] == True).sum() / len(df) * 100
            else:
                completeness = df[feature].notna().sum() / len(df) * 100
            acc_scores.append((completeness, weight))
            print(f"  {feature:45s} {completeness:6.1f}%")

    acc_avg = sum(c*w for c, w in acc_scores) / sum(w for _, w in acc_scores)
    print(f"  {'AVERAGE (weighted)':45s} {acc_avg:6.1f}%")

    # Dimension 2: Academic Level
    print("\nDIMENSION 2: ACADEMIC LEVEL")
    acad_features = ['prerequisite_level', 'target_grade_standardized', 'time_commitment']
    acad_scores = []
    for feature in acad_features:
        if feature in df.columns:
            completeness = df[feature].notna().sum() / len(df) * 100
            acad_scores.append(completeness)
            print(f"  {feature:45s} {completeness:6.1f}%")

    acad_avg = np.mean(acad_scores)
    print(f"  {'AVERAGE':45s} {acad_avg:6.1f}%")

    # Dimension 3: STEM Field Focus
    print("\nDIMENSION 3: STEM FIELD FOCUS")
    stem_features = ['stem_field_tier1', 'category_tier1']
    stem_scores = []
    for feature in stem_features:
        if feature in df.columns:
            completeness = df[feature].notna().sum() / len(df) * 100
            stem_scores.append(completeness)
            print(f"  {feature:45s} {completeness:6.1f}%")

    stem_avg = np.mean(stem_scores)
    print(f"  {'AVERAGE':45s} {stem_avg:6.1f}%")

    # Dimension 4: Resource Format
    print("\nDIMENSION 4: RESOURCE FORMAT")
    format_features = ['category_tier1', 'time_commitment', 'support_level']
    format_scores = []
    for feature in format_features:
        if feature in df.columns:
            completeness = df[feature].notna().sum() / len(df) * 100
            format_scores.append(completeness)
            print(f"  {feature:45s} {completeness:6.1f}%")

    format_avg = np.mean(format_scores)
    print(f"  {'AVERAGE':45s} {format_avg:6.1f}%")

    # Overall
    overall = np.mean([acc_avg, acad_avg, stem_avg, format_avg])

    print(f"\n{'='*80}")
    print(f"OVERALL CLUSTERING READINESS: {overall:.1f}%")
    print(f"{'='*80}")

    if overall >= 90:
        print("[OK] Ready for ML pipeline")
    else:
        print("[WARNING] Below 90% threshold")

    print()

    return {
        'accessibility': acc_avg,
        'academic': acad_avg,
        'stem': stem_avg,
        'format': format_avg,
        'overall': overall
    }

def calculate_final_readiness_score(df, clustering_scores, desc_status):
    """Calculate final ML readiness score (0-100)"""
    print("FINAL ML READINESS SCORE CALCULATION")
    print("-"*80)

    total_score = 0

    # 1. Clustering Dimensions (40 points)
    print("\n1. CLUSTERING DIMENSIONS COMPLETENESS (40 points)")
    acc_points = (clustering_scores['accessibility'] / 100) * 10
    acad_points = (clustering_scores['academic'] / 100) * 10
    stem_points = (clustering_scores['stem'] / 100) * 10
    format_points = (clustering_scores['format'] / 100) * 10

    print(f"   Accessibility Profile: {acc_points:5.1f} / 10.0")
    print(f"   Academic Level:        {acad_points:5.1f} / 10.0")
    print(f"   STEM Field Focus:      {stem_points:5.1f} / 10.0")
    print(f"   Resource Format:       {format_points:5.1f} / 10.0")

    clustering_total = acc_points + acad_points + stem_points + format_points
    total_score += clustering_total

    # 2. ML Prediction Quality (20 points)
    print("\n2. ML PREDICTION QUALITY (20 points)")

    # Get average confidence of high-confidence predictions only
    high_conf_scores = []
    for feature in ['financial_barrier_level', 'hidden_costs_level', 'internet_dependency']:
        conf_col = f'{feature}_confidence'
        high_conf_col = f'{feature}_high_confidence'
        if high_conf_col in df.columns:
            high_conf_predictions = df[df[high_conf_col] == True][conf_col]
            if len(high_conf_predictions) > 0:
                high_conf_scores.extend(high_conf_predictions.tolist())

    if high_conf_scores:
        avg_confidence = np.mean(high_conf_scores)
        if avg_confidence >= 0.75:
            pred_points = 20
        elif avg_confidence >= 0.70:
            pred_points = 16
        elif avg_confidence >= 0.65:
            pred_points = 12
        else:
            pred_points = 8
    else:
        avg_confidence = 0
        pred_points = 5

    print(f"   Average confidence (high-conf only): {avg_confidence:.2%}")
    print(f"   Score: {pred_points:5.1f} / 20.0")
    total_score += pred_points

    # 3. Standardization Quality (20 points)
    print("\n3. STANDARDIZATION QUALITY (20 points)")

    cat_unique = df['category_tier1'].nunique()
    stem_unique = df['stem_field_tier1'].nunique()
    grade_unique = df['target_grade_standardized'].nunique()

    # Category score
    if 10 <= cat_unique <= 15:
        cat_points = 10
    elif 16 <= cat_unique <= 20:
        cat_points = 7
    else:
        cat_points = 3

    # STEM score
    if 10 <= stem_unique <= 15:
        stem_points = 10
    elif 16 <= stem_unique <= 20 or 8 <= stem_unique <= 9:
        stem_points = 7
    else:
        stem_points = 3

    print(f"   Category tier1 ({cat_unique} unique): {cat_points:5.1f} / 10.0")
    print(f"   STEM field tier1 ({stem_unique} unique): {stem_points:5.1f} / 10.0")

    standard_points = cat_points + stem_points
    total_score += standard_points

    # 4. Description Quality (10 points)
    print("\n4. DESCRIPTION/TF-IDF QUALITY (10 points)")

    mean_words = df['word_count'].mean()
    if mean_words >= 50:
        desc_points = 10
    elif mean_words >= 45:
        desc_points = 8
    elif mean_words >= 40:
        desc_points = 6
    else:
        desc_points = 3

    print(f"   Mean word count: {mean_words:.1f}")
    print(f"   Score: {desc_points:5.1f} / 10.0")
    total_score += desc_points

    # 5. Data Quality (10 points)
    print("\n5. DATA QUALITY/CONSISTENCY (10 points)")

    # Check for illogical combinations (should be 0 from previous fixes)
    virtual_transport = ((df['location_type'] == 'Virtual') &
                        (df['transportation_required'] == 'Yes')).sum()
    free_high_barrier = ((df['cost'].str.contains('free', case=False, na=False)) &
                        (df['financial_barrier_level'].isin(['High', 'Medium']))).sum()

    total_illogical = virtual_transport + free_high_barrier
    quality_pct = (1 - (total_illogical / len(df))) * 100

    if quality_pct >= 97:
        quality_points = 10
    elif quality_pct >= 93:
        quality_points = 6
    else:
        quality_points = 2

    print(f"   Data quality: {quality_pct:.1f}%")
    print(f"   Illogical combinations: {total_illogical}")
    print(f"   Score: {quality_points:5.1f} / 10.0")
    total_score += quality_points

    # Final score
    print(f"\n{'='*80}")
    print(f"TOTAL READINESS SCORE: {total_score:.1f} / 100 points")
    print(f"{'='*80}")

    # Status determination
    if total_score >= 85:
        status = "READY FOR ML PIPELINE"
        decision = "GO"
        recommendation = "All systems go! Dataset is production-ready for ML clustering."
    elif total_score >= 80:
        status = "READY WITH MINOR CAVEATS"
        decision = "GO"
        recommendation = "Dataset is ready. Minor quality improvements recommended but not blocking."
    elif total_score >= 75:
        status = "MOSTLY READY - PROCEED WITH CAUTION"
        decision = "CONDITIONAL GO"
        recommendation = "Dataset is usable but has some quality concerns. Review manual_review/ files."
    else:
        status = "NEEDS MORE WORK"
        decision = "NO-GO"
        recommendation = "Dataset requires additional fixes before ML pipeline development."

    print(f"\nStatus: {status}")
    print(f"GO/NO-GO Decision: {decision}")
    print(f"\nRecommendation: {recommendation}")
    print()

    return {
        'total_score': total_score,
        'clustering': clustering_total,
        'predictions': pred_points,
        'standardization': standard_points,
        'descriptions': desc_points,
        'quality': quality_points,
        'status': status,
        'decision': decision,
        'recommendation': recommendation
    }

# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """Main execution function"""

    # Load dataset
    print("Loading dataset...")
    df = pd.read_csv(INPUT_FILE)
    print(f"Loaded {len(df):,} resources with {len(df.columns)} columns\n")

    # Phase 1: Target Grade Fix
    k12_pct_before = analyze_current_target_grade(df)
    df = load_original_target_grades(df)
    df = apply_target_grade_standardization(df)
    validate_target_grade_samples(df)

    # Phase 2: ML Prediction Validation
    pred_analysis = analyze_prediction_confidence(df)
    df = create_reliability_flags(df)

    # Phase 3: Description Quality
    desc_status, under_30_pct = assess_description_quality(df)

    # Phase 4: Final Validation
    clustering_scores = calculate_final_clustering_completeness(df)
    readiness_scores = calculate_final_readiness_score(df, clustering_scores, desc_status)

    # Phase 5: Save Final Dataset
    print("="*80)
    print("PHASE 5: GENERATING FINAL DATASET")
    print("="*80)
    print()

    output_file = OUTPUT_DIR / "bmis_final_ml_ready_dataset.csv"
    df.to_csv(output_file, index=False)

    print(f"Final dataset saved: {output_file}")
    print(f"  Total resources: {len(df):,}")
    print(f"  Total columns: {len(df.columns)}")
    print()

    # Phase 6: Generate Final Report
    print("="*80)
    print("FINAL SUMMARY")
    print("="*80)
    print()
    print(f"READINESS SCORE: {readiness_scores['total_score']:.1f} / 100")
    print(f"STATUS: {readiness_scores['status']}")
    print(f"DECISION: {readiness_scores['decision']}")
    print()
    k12_pct_after = (df['target_grade_standardized'] == 'K-12').sum() / len(df) * 100
    print(f"Target Grade Fix: {k12_pct_before:.1f}% -> {k12_pct_after:.1f}% marked K-12")
    print(f"Clustering Completeness: {clustering_scores['overall']:.1f}%")
    print(f"Description Quality: {desc_status} ({under_30_pct:.1f}% under 30 words)")
    print()
    print("="*80)

if __name__ == "__main__":
    main()
