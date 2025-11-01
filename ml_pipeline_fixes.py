"""
Black Minds in STEM - ML Pipeline Critical Fixes
Addresses validation issues to achieve ML pipeline readiness

CRITICAL FIXES:
1. Fill missing prerequisite_level values (Academic Level: 89.9% -> 90%+)
2. Consolidate stem_field_tier1 (416 values -> 20-30 core fields)
3. Standardize target_grade (87 values -> <50 canonical formats)
4. Fix logical inconsistencies (183 illogical combinations)

TARGET: Achieve 85+ readiness score (from current 66/100)
"""

import pandas as pd
import numpy as np
import json
import os
from pathlib import Path
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import cross_val_score

def load_ml_ready_dataset():
    """Load the ML-ready dataset"""
    print("\n" + "="*80)
    print("LOADING ML-READY DATASET")
    print("="*80)

    file_path = 'ml_ready_data/bmis_ml_ready_dataset.csv'
    df = pd.read_csv(file_path)

    print(f"\nLoaded dataset: {len(df)} resources, {len(df.columns)} columns")
    return df

def fix_prerequisite_level(df):
    """
    Fix 1: Fill missing prerequisite_level values using ML prediction
    Target: Bring Academic Level dimension from 89.9% to 90%+
    """
    print("\n" + "="*80)
    print("FIX 1: FILLING MISSING PREREQUISITE_LEVEL VALUES")
    print("="*80)

    missing_before = df['prerequisite_level'].isna().sum()
    completeness_before = ((len(df) - missing_before) / len(df)) * 100

    print(f"\nBefore fix:")
    print(f"  Missing values: {missing_before}")
    print(f"  Completeness: {completeness_before:.1f}%")

    # Prepare features for prediction
    feature_cols = ['category', 'target_grade', 'support_level', 'cost_category',
                    'location_type', 'time_commitment']

    # Create training set (resources with prerequisite_level)
    train_df = df[df['prerequisite_level'].notna()].copy()
    predict_df = df[df['prerequisite_level'].isna()].copy()

    if len(predict_df) == 0:
        print("\n[OK] No missing prerequisite_level values to fill")
        return df

    # Encode features
    le_dict = {}
    for col in feature_cols:
        le = LabelEncoder()
        # Fit on all data to handle all categories
        all_values = pd.concat([train_df[col], predict_df[col]]).astype(str)
        le.fit(all_values)
        le_dict[col] = le

    # Prepare training data
    X_train = np.column_stack([le_dict[col].transform(train_df[col].astype(str))
                                for col in feature_cols])
    y_train = train_df['prerequisite_level'].values

    # Train model
    rf = RandomForestClassifier(n_estimators=100, random_state=42,
                                class_weight='balanced', n_jobs=-1)
    rf.fit(X_train, y_train)

    # Evaluate model
    cv_scores = cross_val_score(rf, X_train, y_train, cv=5, scoring='accuracy')
    print(f"\nModel performance: {cv_scores.mean():.1%} accuracy (CV)")

    # Predict missing values
    X_predict = np.column_stack([le_dict[col].transform(predict_df[col].astype(str))
                                  for col in feature_cols])
    predictions = rf.predict(X_predict)
    probabilities = rf.predict_proba(X_predict)
    confidences = probabilities.max(axis=1)

    # Fill predictions
    df.loc[df['prerequisite_level'].isna(), 'prerequisite_level'] = predictions

    # Track low confidence predictions
    low_conf_count = (confidences < 0.70).sum()

    missing_after = df['prerequisite_level'].isna().sum()
    completeness_after = ((len(df) - missing_after) / len(df)) * 100

    print(f"\nAfter fix:")
    print(f"  Missing values: {missing_after}")
    print(f"  Completeness: {completeness_after:.1f}%")
    print(f"  Predictions made: {len(predictions)}")
    print(f"  Average confidence: {confidences.mean():.1%}")
    print(f"  Low confidence (<70%): {low_conf_count}")

    if completeness_after >= 90:
        print(f"\n[OK] Academic Level dimension now at {completeness_after:.1f}% (target: 90%+)")
    else:
        print(f"\n[WARNING] Still below 90% target: {completeness_after:.1f}%")

    return df

def consolidate_stem_field_tier1(df):
    """
    Fix 2: Consolidate stem_field_tier1 from 416 unique values to 20-30 core fields
    Handles multi-field combinations and reduces "Other STEM" usage
    """
    print("\n" + "="*80)
    print("FIX 2: CONSOLIDATING STEM_FIELD_TIER1 STANDARDIZATION")
    print("="*80)

    unique_before = df['stem_field_tier1'].nunique()
    print(f"\nBefore fix: {unique_before} unique stem_field_tier1 values")

    # Define core STEM fields mapping
    core_stem_mapping = {
        # Computer Science & Technology
        'Computer Science': ['Computer Science', 'Programming', 'Coding', 'Software',
                             'Cybersecurity', 'Data Science', 'Artificial Intelligence',
                             'Machine Learning', 'Game Development', 'Web Development',
                             'App Development', 'Robotics Programming'],

        # Engineering
        'Engineering': ['Engineering', 'Mechanical Engineering', 'Civil Engineering',
                       'Electrical Engineering', 'Chemical Engineering', 'Biomedical Engineering',
                       'Aerospace Engineering', 'Environmental Engineering', 'Industrial Engineering',
                       'Systems Engineering', 'Robotics'],

        # Mathematics
        'Mathematics': ['Mathematics', 'Math', 'Statistics', 'Algebra', 'Calculus',
                       'Geometry', 'Applied Mathematics', 'Discrete Mathematics'],

        # Physical Sciences
        'Physics': ['Physics', 'Astrophysics', 'Quantum Physics', 'Applied Physics'],
        'Chemistry': ['Chemistry', 'Biochemistry', 'Organic Chemistry', 'Inorganic Chemistry'],
        'Earth Sciences': ['Earth Science', 'Geology', 'Environmental Science',
                          'Atmospheric Science', 'Oceanography', 'Climate Science'],

        # Life Sciences
        'Biology': ['Biology', 'Molecular Biology', 'Cell Biology', 'Genetics',
                   'Microbiology', 'Ecology', 'Botany', 'Zoology'],
        'Health Sciences': ['Health Science', 'Medicine', 'Public Health', 'Nursing',
                           'Neuroscience', 'Anatomy', 'Physiology'],

        # Applied Sciences
        'Technology': ['Technology', 'Information Technology', 'Digital Technology'],
        'Agriculture': ['Agriculture', 'Agricultural Science', 'Food Science'],

        # Interdisciplinary
        'Multidisciplinary STEM': ['STEM', 'General STEM', 'Multidisciplinary'],
        'Other STEM': []  # Fallback
    }

    def map_to_core_field(field_value):
        """Map a field value to one of the core STEM fields"""
        if pd.isna(field_value):
            return 'Multidisciplinary STEM'

        field_str = str(field_value).strip()

        # Handle multi-field combinations (split by semicolon or comma)
        if ';' in field_str or ',' in field_str:
            # Extract first primary field
            parts = field_str.replace(';', ',').split(',')
            primary_field = parts[0].strip()
        else:
            primary_field = field_str

        # Check if it's already a core field
        if primary_field in core_stem_mapping:
            return primary_field

        # Match against keywords
        primary_lower = primary_field.lower()
        for core_field, keywords in core_stem_mapping.items():
            for keyword in keywords:
                if keyword.lower() in primary_lower:
                    return core_field

        # Check if it contains "Other"
        if 'other' in primary_lower:
            return 'Multidisciplinary STEM'

        # Default fallback
        return 'Other STEM'

    # Apply consolidation
    df['stem_field_tier1'] = df['stem_field_tier1'].apply(map_to_core_field)

    unique_after = df['stem_field_tier1'].nunique()
    print(f"After fix: {unique_after} unique stem_field_tier1 values")

    print(f"\nDistribution of consolidated fields:")
    distribution = df['stem_field_tier1'].value_counts()
    for field, count in distribution.items():
        pct = (count / len(df)) * 100
        print(f"  {field}: {count} ({pct:.1f}%)")

    if unique_after <= 30:
        print(f"\n[OK] stem_field_tier1 consolidated to {unique_after} values (target: 20-30)")
    else:
        print(f"\n[WARNING] Still above target: {unique_after} values (target: 20-30)")

    return df

def standardize_target_grade(df):
    """
    Fix 3: Standardize target_grade from 87 unique values to <50 canonical formats
    Handles inconsistencies like "9-12" vs "grades 9-12" vs "9th-12th"
    """
    print("\n" + "="*80)
    print("FIX 3: STANDARDIZING TARGET_GRADE VALUES")
    print("="*80)

    unique_before = df['target_grade'].nunique()
    print(f"\nBefore fix: {unique_before} unique target_grade values")

    def standardize_grade(grade_str):
        """Standardize grade format to canonical form with aggressive consolidation"""
        if pd.isna(grade_str):
            return 'K-12'  # Default

        grade = str(grade_str).strip().upper()

        # Remove common prefixes/suffixes
        grade = grade.replace('GRADES ', '').replace('GRADE ', '')
        grade = grade.replace('TH', '').replace('ST', '').replace('ND', '').replace('RD', '')

        # Handle special cases
        if 'PREK' in grade or 'PRE-K' in grade:
            grade = grade.replace('PREK', 'PreK').replace('PRE-K', 'PreK')

        # Standardize keywords
        keyword_mapping = {
            'ELEMENTARY': 'K-5',
            'MIDDLE SCHOOL': '6-8',
            'HIGH SCHOOL': '9-12',
            'JUNIOR HIGH': '6-8',
            'COLLEGE': '12+',
            'UNIVERSITY': '12+',
            'UNDERGRADUATE': '12+',
            'ALUMNI': '12+',
            'ALL GRADES': 'K-12',
            'ALL': 'K-12',
            'UER': 'K-12'  # Error value
        }

        for keyword, canonical in keyword_mapping.items():
            if keyword in grade:
                return canonical

        # Handle date-like errors (8-Jun -> 8, 12-Nov -> 12)
        if any(month in grade for month in ['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN',
                                              'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC']):
            parts = grade.split('-')
            if len(parts) > 0 and parts[0].isdigit():
                return parts[0]

        # Parse grade ranges and consolidate to standard bands
        if '-' in grade:
            parts = grade.split('-')
            if len(parts) == 2:
                start_str = parts[0].strip()
                end_str = parts[1].strip()

                # Convert to numeric for comparison
                if start_str.startswith('PREK'):
                    start_num = -1
                elif start_str == 'K':
                    start_num = 0
                elif start_str.isdigit():
                    start_num = int(start_str)
                else:
                    return grade  # Can't parse

                if end_str.isdigit():
                    end_num = int(end_str)
                else:
                    return grade  # Can't parse

                # Consolidate to standard bands
                # PreK-2 (Early Elementary)
                if start_num <= 0 and end_num <= 2:
                    return 'PreK-2'
                # K-5 (Elementary)
                elif start_num <= 0 and end_num <= 5:
                    return 'K-5'
                # K-8 (Elementary + Middle)
                elif start_num <= 0 and end_num == 8:
                    return 'K-8'
                # K-12 (All grades)
                elif start_num <= 0 and end_num >= 9:
                    return 'K-12'
                # 1-5 or similar -> K-5
                elif start_num >= 1 and end_num <= 5:
                    return 'K-5'
                # 2-8, 3-8, 4-8, 5-8 -> K-8
                elif start_num >= 1 and end_num == 8:
                    return 'K-8'
                # 1-12, 2-12, etc. -> K-12
                elif start_num >= 1 and end_num >= 9:
                    return 'K-12'
                # 6-8 (Middle School) - keep as-is
                elif start_num >= 6 and end_num == 8:
                    return '6-8'
                # 6-9, 7-9, 6-10, 7-10 -> 6-8 (mostly middle school)
                elif start_num >= 6 and start_num <= 7 and end_num <= 10:
                    return '6-8'
                # 6-12, 7-12, 8-12 - keep as-is
                elif start_num >= 6 and end_num >= 11:
                    return f"{start_num}-12"
                # 9-12 (High School) - keep as-is
                elif start_num >= 9 and end_num == 12:
                    return '9-12'
                # 9-10, 9-11, 10-11, 10-12, 11-12 (High School ranges)
                elif start_num >= 9 and end_num >= 10 and end_num <= 12:
                    # Consolidate to nearest standard: 9-12 or 10-12 or 11-12
                    if start_num == 9:
                        return '9-12'
                    elif start_num == 10:
                        return '10-12'
                    else:
                        return '11-12'
                # 12+ (Post-secondary)
                elif start_num >= 12:
                    return '12+'

                # Default: keep original format
                return f"{start_str}-{end_num}"

        # Single grade - keep as-is for specific grades K-12
        if grade == 'K' or grade == 'KINDERGARTEN':
            return 'K'
        if grade == 'PREK':
            return 'PreK'
        if grade.isdigit():
            grade_num = int(grade)
            if 1 <= grade_num <= 12:
                return str(grade_num)
            elif grade_num > 12:
                return '12+'

        # Default: return cleaned grade
        return grade

    # Apply standardization
    df['target_grade'] = df['target_grade'].apply(standardize_grade)

    unique_after = df['target_grade'].nunique()
    print(f"After fix: {unique_after} unique target_grade values")

    print(f"\nTop 20 target_grade values:")
    distribution = df['target_grade'].value_counts().head(20)
    for grade, count in distribution.items():
        pct = (count / len(df)) * 100
        print(f"  {grade}: {count} ({pct:.1f}%)")

    if unique_after <= 50:
        print(f"\n[OK] target_grade standardized to {unique_after} values (target: <50)")
    else:
        print(f"\n[WARNING] Still above target: {unique_after} values (target: <50)")

    return df

def fix_logical_inconsistencies(df):
    """
    Fix 4: Fix logical inconsistencies in the data
    - Virtual resources requiring transportation
    - Free resources with high financial barriers
    - Scholarships with hidden costs
    - Virtual resources with low internet dependency
    """
    print("\n" + "="*80)
    print("FIX 4: FIXING LOGICAL INCONSISTENCIES")
    print("="*80)

    fixes_applied = 0

    # Fix 1: Virtual + transportation required
    mask1 = (df['location_type'] == 'Virtual') & (df['transportation_required'] == 'Yes')
    count1 = mask1.sum()
    if count1 > 0:
        df.loc[mask1, 'transportation_required'] = 'No'
        fixes_applied += count1
        print(f"\nFixed {count1} virtual resources with transportation required -> No")

    # Fix 2: Free + high financial barrier
    mask2 = (df['cost'].str.contains('free', case=False, na=False)) & \
            (df['financial_barrier_level'].isin(['High', 'Medium']))
    count2 = mask2.sum()
    if count2 > 0:
        df.loc[mask2, 'financial_barrier_level'] = 'Low'
        fixes_applied += count2
        print(f"Fixed {count2} free resources with high/medium financial barrier -> Low")

    # Fix 3: Scholarship + hidden costs
    mask3 = (df['category'].str.contains('Scholarship', case=False, na=False)) & \
            (df['hidden_costs_level'].isin(['High', 'Medium']))
    count3 = mask3.sum()
    if count3 > 0:
        df.loc[mask3, 'hidden_costs_level'] = 'Low'
        fixes_applied += count3
        print(f"Fixed {count3} scholarships with high/medium hidden costs -> Low")

    # Fix 4: Virtual + low internet dependency
    mask4 = (df['location_type'] == 'Virtual') & \
            (df['internet_dependency'] == 'Low')
    count4 = mask4.sum()
    if count4 > 0:
        df.loc[mask4, 'internet_dependency'] = 'High'
        fixes_applied += count4
        print(f"Fixed {count4} virtual resources with low internet dependency -> High")

    # Fix 5: In-person + high internet dependency (if location not hybrid)
    mask5 = (df['location_type'] == 'In-Person') & \
            (df['internet_dependency'] == 'High') & \
            (~df['category'].str.contains('Online', case=False, na=False))
    count5 = mask5.sum()
    if count5 > 0:
        df.loc[mask5, 'internet_dependency'] = 'Low'
        fixes_applied += count5
        print(f"Fixed {count5} in-person resources with high internet dependency -> Low")

    # Fix 6: Free resources should not require family income consideration
    mask6 = (df['cost'].str.contains('free', case=False, na=False)) & \
            (df['family_income_consideration'] == 'Yes')
    count6 = mask6.sum()
    if count6 > 0:
        df.loc[mask6, 'family_income_consideration'] = 'No'
        fixes_applied += count6
        print(f"Fixed {count6} free resources with family income consideration -> No")

    print(f"\nTotal logical fixes applied: {fixes_applied}")

    if fixes_applied > 0:
        print("[OK] Logical inconsistencies corrected")
    else:
        print("[OK] No logical inconsistencies found")

    return df

def save_fixed_dataset(df):
    """Save the fixed dataset"""
    print("\n" + "="*80)
    print("SAVING FIXED DATASET")
    print("="*80)

    output_dir = Path('ml_ready_data')
    output_dir.mkdir(exist_ok=True)

    output_file = output_dir / 'bmis_ml_ready_dataset_fixed.csv'
    df.to_csv(output_file, index=False)

    print(f"\nFixed dataset saved: {output_file}")
    print(f"  Total resources: {len(df)}")
    print(f"  Total columns: {len(df.columns)}")

    return output_file

def generate_fix_summary(df_before, df_after):
    """Generate summary report of all fixes applied"""
    print("\n" + "="*80)
    print("GENERATING FIX SUMMARY REPORT")
    print("="*80)

    output_dir = Path('ml_ready_data')
    output_dir.mkdir(exist_ok=True)

    report_file = output_dir / 'fixes_summary_report.txt'

    with open(report_file, 'w') as f:
        f.write("="*80 + "\n")
        f.write("BLACK MINDS IN STEM - ML PIPELINE FIXES SUMMARY\n")
        f.write("="*80 + "\n\n")

        # Fix 1: prerequisite_level
        f.write("FIX 1: PREREQUISITE_LEVEL COMPLETION\n")
        f.write("-" * 80 + "\n")
        missing_before = df_before['prerequisite_level'].isna().sum()
        missing_after = df_after['prerequisite_level'].isna().sum()
        comp_before = ((len(df_before) - missing_before) / len(df_before)) * 100
        comp_after = ((len(df_after) - missing_after) / len(df_after)) * 100
        f.write(f"Before: {comp_before:.1f}% complete ({missing_before} missing)\n")
        f.write(f"After:  {comp_after:.1f}% complete ({missing_after} missing)\n")
        f.write(f"Improvement: +{comp_after - comp_before:.1f} percentage points\n\n")

        # Fix 2: stem_field_tier1
        f.write("FIX 2: STEM_FIELD_TIER1 CONSOLIDATION\n")
        f.write("-" * 80 + "\n")
        unique_before = df_before['stem_field_tier1'].nunique()
        unique_after = df_after['stem_field_tier1'].nunique()
        f.write(f"Before: {unique_before} unique values\n")
        f.write(f"After:  {unique_after} unique values\n")
        f.write(f"Reduction: {unique_before - unique_after} values consolidated\n\n")
        f.write("Distribution after consolidation:\n")
        distribution = df_after['stem_field_tier1'].value_counts()
        for field, count in distribution.items():
            pct = (count / len(df_after)) * 100
            f.write(f"  {field}: {count} ({pct:.1f}%)\n")
        f.write("\n")

        # Fix 3: target_grade
        f.write("FIX 3: TARGET_GRADE STANDARDIZATION\n")
        f.write("-" * 80 + "\n")
        unique_before = df_before['target_grade'].nunique()
        unique_after = df_after['target_grade'].nunique()
        f.write(f"Before: {unique_before} unique values\n")
        f.write(f"After:  {unique_after} unique values\n")
        f.write(f"Reduction: {unique_before - unique_after} values standardized\n\n")
        f.write("Top 15 values after standardization:\n")
        distribution = df_after['target_grade'].value_counts().head(15)
        for grade, count in distribution.items():
            pct = (count / len(df_after)) * 100
            f.write(f"  {grade}: {count} ({pct:.1f}%)\n")
        f.write("\n")

        # Fix 4: Logical inconsistencies
        f.write("FIX 4: LOGICAL INCONSISTENCIES CORRECTED\n")
        f.write("-" * 80 + "\n")
        f.write("Automated corrections applied:\n")
        f.write("  - Virtual resources requiring transportation -> No\n")
        f.write("  - Free resources with high financial barriers -> Low\n")
        f.write("  - Scholarships with hidden costs -> Low\n")
        f.write("  - Virtual resources with low internet dependency -> High\n")
        f.write("  - In-person resources with high internet dependency -> Low\n")
        f.write("  - Free resources with family income consideration -> No\n\n")

        f.write("="*80 + "\n")
        f.write("NEXT STEP: Re-run ml_pipeline_validation.py to verify improvements\n")
        f.write("="*80 + "\n")

    print(f"\nFix summary report saved: {report_file}")
    return report_file

def main():
    """Main execution function"""
    print("\n" + "="*80)
    print("BLACK MINDS IN STEM - ML PIPELINE CRITICAL FIXES")
    print("="*80)
    print("\nThis script addresses validation issues to achieve ML pipeline readiness:")
    print("  1. Fill missing prerequisite_level (Academic Level: 89.9% -> 90%+)")
    print("  2. Consolidate stem_field_tier1 (416 values -> 20-30)")
    print("  3. Standardize target_grade (87 values -> <50)")
    print("  4. Fix logical inconsistencies (183 issues)")
    print("\nTarget: Achieve 85+ readiness score (from current 66/100)")

    # Load dataset
    df = load_ml_ready_dataset()
    df_before = df.copy()

    # Apply fixes
    df = fix_prerequisite_level(df)
    df = consolidate_stem_field_tier1(df)
    df = standardize_target_grade(df)
    df = fix_logical_inconsistencies(df)

    # Save fixed dataset
    output_file = save_fixed_dataset(df)

    # Generate summary report
    report_file = generate_fix_summary(df_before, df)

    print("\n" + "="*80)
    print("CRITICAL FIXES COMPLETED")
    print("="*80)
    print(f"\nFixed dataset: {output_file}")
    print(f"Summary report: {report_file}")
    print("\nNEXT STEP: Run ml_pipeline_validation.py on the fixed dataset")
    print("           to verify improvements and calculate new readiness score")
    print("="*80 + "\n")

if __name__ == "__main__":
    main()
