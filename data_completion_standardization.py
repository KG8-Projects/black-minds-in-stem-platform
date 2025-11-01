"""
Black Minds in STEM: Data Completion & Standardization
Prepares cleaned dataset for ML pipeline through description enhancement,
ML-based prediction, and hierarchical standardization
"""

import pandas as pd
import numpy as np
from pathlib import Path
import json
from collections import defaultdict, Counter
import re

# ML libraries
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import cross_val_score, train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

# Constants
BASE_DIR = Path(r"C:\Users\u_wos\Downloads\Black Minds In STEM")
INPUT_FILE = BASE_DIR / "cleaned_data" / "bmis_clean_master_dataset.csv"
OUTPUT_DIR = BASE_DIR / "ml_ready_data"

# Create output directories
(OUTPUT_DIR / "processing_artifacts").mkdir(parents=True, exist_ok=True)
(OUTPUT_DIR / "manual_review_needed").mkdir(parents=True, exist_ok=True)

print("="*80)
print("BLACK MINDS IN STEM - DATA COMPLETION & STANDARDIZATION")
print("="*80)
print()

# ============================================================================
# PHASE 1: DESCRIPTION QUALITY ENHANCEMENT
# ============================================================================

def analyze_description_quality(df):
    """Analyze current description quality"""
    print("="*80)
    print("PHASE 1A: ANALYZING DESCRIPTION QUALITY")
    print("="*80)
    print()

    # Calculate word counts
    df['word_count'] = df['description'].fillna('').apply(lambda x: len(str(x).split()))

    stats = {
        'total': len(df),
        'with_descriptions': df['description'].notna().sum(),
        'min_words': df['word_count'].min(),
        'max_words': df['word_count'].max(),
        'avg_words': df['word_count'].mean(),
        'median_words': df['word_count'].median(),
        'under_20_words': (df['word_count'] < 20).sum(),
        'under_10_words': (df['word_count'] < 10).sum(),
        'under_30_words': (df['word_count'] < 30).sum(),
        'over_80_words': (df['word_count'] >= 80).sum()
    }

    print(f"Total resources: {stats['total']:,}")
    print(f"Resources with descriptions: {stats['with_descriptions']:,}")
    print()
    print("WORD COUNT DISTRIBUTION:")
    print(f"  Minimum: {stats['min_words']} words")
    print(f"  Maximum: {stats['max_words']} words")
    print(f"  Average: {stats['avg_words']:.1f} words")
    print(f"  Median: {stats['median_words']:.1f} words")
    print()
    print("DESCRIPTION LENGTH CATEGORIES:")
    print(f"  Critical (< 10 words): {stats['under_10_words']}")
    print(f"  Very short (< 20 words): {stats['under_20_words']}")
    print(f"  Short (< 30 words): {stats['under_30_words']}")
    print(f"  Good length (>= 80 words): {stats['over_80_words']}")
    print()

    # Show samples
    print("SAMPLE SHORT DESCRIPTIONS (10 shortest):")
    print("-"*80)
    shortest = df.nsmallest(10, 'word_count')[['name', 'description', 'word_count']]
    for idx, row in shortest.iterrows():
        print(f"\n[{row['word_count']} words] {row['name']}")
        print(f"  {row['description'][:150]}...")

    print("\n" + "-"*80)
    print("\nSAMPLE MEDIUM DESCRIPTIONS (10 around median):")
    print("-"*80)
    median_val = df['word_count'].median()
    median_samples = df.iloc[(df['word_count'] - median_val).abs().argsort()[:10]]
    for idx, row in median_samples.iterrows():
        print(f"\n[{row['word_count']} words] {row['name']}")
        print(f"  {row['description'][:150]}...")

    print("\n" + "-"*80)
    print("\nSAMPLE LONG DESCRIPTIONS (10 longest):")
    print("-"*80)
    longest = df.nlargest(10, 'word_count')[['name', 'description', 'word_count']]
    for idx, row in longest.iterrows():
        print(f"\n[{row['word_count']} words] {row['name']}")
        print(f"  {row['description'][:150]}...")

    print("\n" + "="*80 + "\n")

    return stats

def enhance_descriptions(df):
    """Enhance short descriptions using metadata"""
    print("="*80)
    print("PHASE 1B: ENHANCING SHORT/INCOMPLETE DESCRIPTIONS")
    print("="*80)
    print()

    # Identify descriptions needing enhancement (< 30 words)
    needs_enhancement = df['word_count'] < 30
    enhancement_count = needs_enhancement.sum()

    print(f"Resources needing description enhancement: {enhancement_count}")
    print()

    enhancements = []
    enhanced_count = 0

    for idx, row in df[needs_enhancement].iterrows():
        original_desc = row['description']

        # Build enhanced description using template
        parts = []

        # Start with existing description if not empty
        if pd.notna(original_desc) and len(str(original_desc).strip()) > 0:
            parts.append(str(original_desc).strip())

        # Add context from metadata
        name = row['name']
        category = row.get('category', '')
        stem_fields = row.get('stem_fields', '')
        target_grade = row.get('target_grade', '')
        time_commitment = row.get('time_commitment', '')
        cost = row.get('cost', '')
        location_type = row.get('location_type', '')
        prerequisite = row.get('prerequisite_level', '')

        # Build additional context sentence
        if pd.notna(category) and pd.notna(stem_fields) and pd.notna(target_grade):
            if len(parts) == 0:
                # No original description - create from scratch
                context = f"{name} is a {category} focused on {stem_fields} for grade {target_grade} students."
            else:
                # Enhance existing description
                context = f"This {category} focuses on {stem_fields} and serves grade {target_grade} students."
            parts.append(context)

        # Add program details
        details = []
        if pd.notna(time_commitment) and time_commitment != 'Unknown':
            details.append(f"{time_commitment} commitment")
        if pd.notna(cost) and cost != 'Unknown':
            details.append(cost.lower())
        if pd.notna(location_type) and location_type != 'Unknown':
            details.append(f"available {location_type.lower()}")

        if details:
            parts.append(f"The program requires {', '.join(details)}.")

        # Add prerequisites if meaningful
        if pd.notna(prerequisite) and prerequisite not in ['None', 'Unknown', 'Beginner']:
            parts.append(f"Prerequisites: {prerequisite} level.")

        # Combine parts
        enhanced_desc = ' '.join(parts)

        # Only update if we actually enhanced it
        if len(enhanced_desc.split()) > row['word_count']:
            df.at[idx, 'description'] = enhanced_desc
            df.at[idx, 'word_count'] = len(enhanced_desc.split())

            enhancements.append({
                'name': name,
                'original': original_desc,
                'enhanced': enhanced_desc,
                'original_words': row['word_count'],
                'enhanced_words': len(enhanced_desc.split())
            })
            enhanced_count += 1

    print(f"Descriptions successfully enhanced: {enhanced_count}")
    print(f"Average word count increase: {np.mean([e['enhanced_words'] - e['original_words'] for e in enhancements]):.1f} words")
    print()

    # Show samples
    print("SAMPLE ENHANCEMENTS (first 10):")
    print("-"*80)
    for i, enh in enumerate(enhancements[:10], 1):
        print(f"\n{i}. {enh['name']}")
        print(f"   BEFORE ({enh['original_words']} words): {enh['original'][:100]}...")
        print(f"   AFTER ({enh['enhanced_words']} words): {enh['enhanced'][:150]}...")

    print("\n" + "="*80 + "\n")

    # Save enhancement log
    enh_df = pd.DataFrame(enhancements)
    if not enh_df.empty:
        enh_df.to_csv(
            OUTPUT_DIR / "processing_artifacts" / "description_enhancements.csv",
            index=False,
            encoding='utf-8'
        )

    return df, enhanced_count

def create_tfidf_text(df):
    """Create rich text field for TF-IDF"""
    print("="*80)
    print("PHASE 1C: CREATING TF-IDF TEXT FIELD")
    print("="*80)
    print()

    # Combine multiple columns for rich text representation
    df['tfidf_text'] = (
        df['name'].fillna('') + ' ' +
        df['description'].fillna('') + ' ' +
        df['stem_fields'].fillna('') + ' ' +
        df['category'].fillna('') + ' ' +
        df['target_grade'].fillna('') + ' ' +
        df['prerequisite_level'].fillna('') + ' ' +
        df['support_level'].fillna('') + ' ' +
        df['location_type'].fillna('')
    )

    # Clean up extra whitespace
    df['tfidf_text'] = df['tfidf_text'].str.replace(r'\s+', ' ', regex=True).str.strip()

    # Calculate statistics
    avg_length = df['tfidf_text'].str.len().mean()
    avg_words = df['tfidf_text'].str.split().str.len().mean()

    print(f"TF-IDF text field created for {len(df):,} resources")
    print(f"Average character length: {avg_length:.0f}")
    print(f"Average word count: {avg_words:.0f}")
    print()

    # Show samples
    print("SAMPLE TF-IDF TEXT (first 5 resources):")
    print("-"*80)
    for idx, text in df['tfidf_text'].head().items():
        print(f"\n{df.loc[idx, 'name']}")
        print(f"  {text[:200]}...")

    print("\n" + "="*80 + "\n")

    return df

# ============================================================================
# PHASE 2: ML-BASED MISSING DATA PREDICTION
# ============================================================================

def prepare_ml_features(df, target_feature, predictor_features):
    """Prepare training and prediction datasets"""

    # Split into training (has target) and prediction (missing target)
    train_mask = df[target_feature].notna()

    train_df = df[train_mask].copy()
    predict_df = df[~train_mask].copy()

    print(f"  Training samples: {len(train_df):,}")
    print(f"  Prediction samples: {len(predict_df):,}")

    return train_df, predict_df

def encode_features(train_df, predict_df, predictor_features):
    """Encode categorical features for ML"""

    encoders = {}
    X_train_encoded = pd.DataFrame(index=train_df.index)
    X_predict_encoded = pd.DataFrame(index=predict_df.index) if len(predict_df) > 0 else pd.DataFrame()

    for feature in predictor_features:
        if feature not in train_df.columns:
            continue

        # Fill missing values with 'Unknown'
        train_vals = train_df[feature].fillna('Unknown').astype(str)
        predict_vals = predict_df[feature].fillna('Unknown').astype(str) if len(predict_df) > 0 else pd.Series()

        # Label encode
        le = LabelEncoder()

        # Fit on both train and predict to handle all categories
        all_vals = pd.concat([train_vals, predict_vals])
        le.fit(all_vals.unique())

        X_train_encoded[feature] = le.transform(train_vals)
        if len(predict_df) > 0:
            X_predict_encoded[feature] = le.transform(predict_vals)

        encoders[feature] = le

    return X_train_encoded, X_predict_encoded, encoders

def train_rf_classifier(X_train, y_train, feature_name):
    """Train Random Forest classifier"""

    print(f"\n  Training Random Forest for {feature_name}...")

    # Initialize Random Forest
    rf = RandomForestClassifier(
        n_estimators=100,
        random_state=42,
        class_weight='balanced',
        n_jobs=-1
    )

    # Train
    rf.fit(X_train, y_train)

    # Cross-validation
    cv_scores = cross_val_score(rf, X_train, y_train, cv=5, scoring='accuracy')

    print(f"  Cross-validation accuracy: {cv_scores.mean():.2%} (+/- {cv_scores.std()*2:.2%})")

    # Feature importance
    importance = pd.DataFrame({
        'feature': X_train.columns,
        'importance': rf.feature_importances_
    }).sort_values('importance', ascending=False)

    print(f"\n  Top 5 most important features:")
    for _, row in importance.head().iterrows():
        print(f"    - {row['feature']}: {row['importance']:.3f}")

    return rf, cv_scores.mean(), importance

def predict_missing_values(df, target_feature, predictor_features):
    """Predict missing values for a single feature"""

    print(f"\nPredicting: {target_feature}")
    print("-"*80)

    # Check if there are any missing values
    missing_count = df[target_feature].isna().sum()
    if missing_count == 0:
        print(f"  No missing values for {target_feature}")
        return df, None, None

    print(f"  Missing values: {missing_count:,} ({missing_count/len(df)*100:.1f}%)")

    # Prepare data
    train_df, predict_df = prepare_ml_features(df, target_feature, predictor_features)

    if len(train_df) == 0:
        print(f"  ERROR: No training data available for {target_feature}")
        return df, None, None

    if len(predict_df) == 0:
        print(f"  No predictions needed (all values present)")
        return df, None, None

    # Encode features
    X_train, X_predict, encoders = encode_features(train_df, predict_df, predictor_features)
    y_train = train_df[target_feature]

    # Train model
    model, accuracy, importance = train_rf_classifier(X_train, y_train, target_feature)

    # Make predictions
    predictions = model.predict(X_predict)
    probabilities = model.predict_proba(X_predict)

    # Get confidence scores (max probability for each prediction)
    confidence_scores = probabilities.max(axis=1)

    # Create prediction log
    prediction_log = pd.DataFrame({
        'index': predict_df.index,
        'name': predict_df['name'],
        'predicted_value': predictions,
        'confidence': confidence_scores
    })

    # Flag low confidence predictions
    low_confidence = prediction_log[prediction_log['confidence'] < 0.7]

    print(f"\n  Predictions made: {len(predictions):,}")
    print(f"  Average confidence: {confidence_scores.mean():.2%}")
    print(f"  Low confidence predictions (< 70%): {len(low_confidence)}")

    # Update dataframe
    df.loc[predict_df.index, target_feature] = predictions
    df.loc[predict_df.index, f'{target_feature}_predicted'] = True
    df.loc[predict_df.index, f'{target_feature}_confidence'] = confidence_scores

    # Fill prediction flag for non-predicted rows
    df[f'{target_feature}_predicted'] = df[f'{target_feature}_predicted'].fillna(False)

    # Show sample predictions
    print(f"\n  Sample HIGH confidence predictions (>= 90%):")
    high_conf = prediction_log[prediction_log['confidence'] >= 0.9].head(5)
    for _, row in high_conf.iterrows():
        print(f"    - {row['name'][:50]:50s} -> {row['predicted_value']:20s} ({row['confidence']:.1%})")

    print(f"\n  Sample LOW confidence predictions (< 70%):")
    for _, row in low_confidence.head(5).iterrows():
        print(f"    - {row['name'][:50]:50s} -> {row['predicted_value']:20s} ({row['confidence']:.1%})")

    return df, prediction_log, importance

def ml_predict_all_features(df):
    """Run ML prediction for all missing features"""

    print("="*80)
    print("PHASE 2: ML-BASED MISSING DATA PREDICTION")
    print("="*80)
    print()

    # Define features to predict and their predictors
    prediction_tasks = {
        'financial_barrier_level': ['category', 'cost', 'location_type', 'time_commitment',
                                     'stem_fields', 'target_grade', 'support_level'],
        'hidden_costs_level': ['category', 'cost', 'location_type', 'time_commitment',
                               'cost_category', 'financial_barrier_level'],
        'cost_category': ['cost', 'category', 'location_type', 'time_commitment'],
        'transportation_required': ['location_type', 'category', 'cost', 'regional_availability'],
        'rural_accessible': ['location_type', 'internet_dependency', 'transportation_required',
                             'category', 'regional_availability'],
        'internet_dependency': ['location_type', 'category', 'time_commitment']
    }

    all_predictions = {}
    all_importances = {}
    all_low_confidence = []

    for target, predictors in prediction_tasks.items():
        df_updated, pred_log, importance = predict_missing_values(df, target, predictors)

        if pred_log is not None:
            all_predictions[target] = pred_log
            all_importances[target] = importance

            # Collect low confidence predictions
            low_conf = pred_log[pred_log['confidence'] < 0.7].copy()
            low_conf['predicted_feature'] = target
            all_low_confidence.append(low_conf)

        df = df_updated

    # Combine and save low confidence predictions
    if all_low_confidence:
        low_conf_df = pd.concat(all_low_confidence, ignore_index=True)
        low_conf_df.to_csv(
            OUTPUT_DIR / "manual_review_needed" / "low_confidence_predictions.csv",
            index=False,
            encoding='utf-8'
        )
        print(f"\nTotal low confidence predictions: {len(low_conf_df)}")

    print("\n" + "="*80 + "\n")

    return df, all_predictions, all_importances

# ============================================================================
# PHASE 3: HIERARCHICAL STANDARDIZATION
# ============================================================================

def analyze_category_distribution(df):
    """Analyze current category values"""

    print("="*80)
    print("PHASE 3A: ANALYZING CATEGORY DISTRIBUTION")
    print("="*80)
    print()

    category_counts = df['category'].value_counts()

    print(f"Total unique categories: {len(category_counts)}")
    print(f"\nTop 20 most common categories:")
    print("-"*80)
    for cat, count in category_counts.head(20).items():
        print(f"  {cat:50s} {count:4d} ({count/len(df)*100:.1f}%)")

    print(f"\n\nCategories with < 5 occurrences: {(category_counts < 5).sum()}")

    print("\n" + "="*80 + "\n")

    return category_counts

def create_category_mapping():
    """Create hierarchical category mapping"""

    # Define tier 1 standard categories
    tier1_mapping = {
        # Scholarships
        'Scholarship': 'Scholarship',
        'Merit Scholarship': 'Scholarship',
        'STEM Scholarship': 'Scholarship',
        'Need-Based Scholarship': 'Scholarship',
        'Academic Scholarship': 'Scholarship',
        'Award': 'Award/Recognition',
        'Grant': 'Scholarship',
        'Fellowship': 'Fellowship',

        # Competitions
        'Competition': 'Competition',
        'Math Competition': 'Competition',
        'Science Competition': 'Competition',
        'Coding Competition': 'Competition',
        'Robotics Competition': 'Competition',
        'Engineering Competition': 'Competition',
        'Challenge': 'Challenge/Hackathon',
        'Hackathon': 'Challenge/Hackathon',

        # Camps
        'Camp': 'Camp',
        'Summer Camp': 'Camp',
        'Day Camp': 'Camp',
        'Residential Camp': 'Camp',
        'Virtual Camp': 'Camp',
        'Coding Camp': 'Camp',
        'STEM Camp': 'Camp',

        # Summer Programs
        'Summer Program': 'Summer Program',
        'Summer Institute': 'Summer Program',
        'Summer Course': 'Summer Program',
        'Pre-College Program': 'Summer Program',

        # Research
        'Research Opportunity': 'Research Opportunity',
        'Research Program': 'Research Opportunity',
        'Research Internship': 'Research Opportunity',

        # Internships
        'Internship': 'Internship',
        'Tech Internship': 'Internship',

        # Online Learning
        'Online Course': 'Online Course',
        'Learning Platform': 'Learning Platform',
        'Online Class': 'Online Course',
        'MOOC': 'Online Course',
        'Tutorial': 'Learning Platform',
        'Educational Platform': 'Learning Platform',

        # Programs & Organizations
        'Program': 'Program/Initiative',
        'Initiative': 'Program/Initiative',
        'Organization': 'Organization/Club',
        'Club': 'Organization/Club',
        'Network': 'Organization/Club',

        # Training & Workshops
        'Workshop': 'Workshop/Training',
        'Training': 'Workshop/Training',
        'Bootcamp': 'Workshop/Training',
        'Curriculum': 'Workshop/Training',

        # Events
        'Conference': 'Conference/Event',
        'Event': 'Conference/Event',
        'Symposium': 'Conference/Event',

        # Mentorship
        'Mentorship': 'Mentorship Program',
        'Mentorship Program': 'Mentorship Program',
    }

    return tier1_mapping

def create_stem_field_mapping():
    """Create hierarchical STEM field mapping"""

    # Define tier 1 core STEM disciplines
    tier1_mapping = {
        # Computer Science
        'Computer Science': 'Computer Science',
        'Programming': 'Computer Science',
        'Coding': 'Computer Science',
        'Software Development': 'Computer Science',
        'Software Engineering': 'Computer Science',
        'Web Development': 'Computer Science',
        'App Development': 'Computer Science',
        'Game Development': 'Computer Science',

        # AI/ML
        'Artificial Intelligence': 'Artificial Intelligence/Machine Learning',
        'Machine Learning': 'Artificial Intelligence/Machine Learning',
        'Deep Learning': 'Artificial Intelligence/Machine Learning',
        'Neural Networks': 'Artificial Intelligence/Machine Learning',
        'AI': 'Artificial Intelligence/Machine Learning',
        'ML': 'Artificial Intelligence/Machine Learning',

        # Data Science
        'Data Science': 'Data Science',
        'Data Analysis': 'Data Science',
        'Big Data': 'Data Science',
        'Analytics': 'Data Science',

        # Cybersecurity
        'Cybersecurity': 'Cybersecurity',
        'Security': 'Cybersecurity',
        'Ethical Hacking': 'Cybersecurity',
        'Information Security': 'Cybersecurity',

        # Robotics
        'Robotics': 'Robotics',
        'Robot Design': 'Robotics',

        # Biology
        'Biology': 'Biology',
        'Molecular Biology': 'Biology',
        'Cell Biology': 'Biology',
        'Marine Biology': 'Marine Biology',
        'Ecology': 'Biology',
        'Genetics': 'Biotechnology',
        'Genomics': 'Biotechnology',

        # Chemistry
        'Chemistry': 'Chemistry',
        'Organic Chemistry': 'Chemistry',
        'Biochemistry': 'Chemistry',

        # Physics
        'Physics': 'Physics',
        'Quantum Physics': 'Physics',
        'Astrophysics': 'Astronomy/Space Science',
        'Astronomy': 'Astronomy/Space Science',
        'Space Science': 'Astronomy/Space Science',

        # Mathematics
        'Mathematics': 'Mathematics',
        'Math': 'Mathematics',
        'Algebra': 'Mathematics',
        'Calculus': 'Mathematics',
        'Geometry': 'Mathematics',
        'Statistics': 'Statistics',
        'Applied Mathematics': 'Applied Mathematics',

        # Engineering (General)
        'Engineering': 'Engineering',
        'STEM': 'Multi-disciplinary STEM',

        # Specific Engineering
        'Mechanical Engineering': 'Mechanical Engineering',
        'Electrical Engineering': 'Electrical Engineering',
        'Civil Engineering': 'Civil Engineering',
        'Aerospace Engineering': 'Aerospace Engineering',
        'Chemical Engineering': 'Chemical Engineering',
        'Biomedical Engineering': 'Biomedical Engineering',

        # Environmental
        'Environmental Science': 'Environmental Science',
        'Climate Science': 'Environmental Science',
        'Sustainability': 'Environmental Science',

        # Medicine/Health
        'Medicine': 'Medicine/Healthcare',
        'Healthcare': 'Medicine/Healthcare',
        'Neuroscience': 'Neuroscience',
        'Biomedical': 'Biomedical Engineering',

        # Technology
        'Technology': 'Technology',
        'IT': 'Information Technology',
        'Information Technology': 'Information Technology',

        # Materials Science
        'Materials Science': 'Materials Science',
        'Nanotechnology': 'Materials Science',
    }

    return tier1_mapping

def apply_hierarchical_standardization(df):
    """Apply hierarchical standardization to categories and STEM fields"""

    print("="*80)
    print("PHASE 3B-D: APPLYING HIERARCHICAL STANDARDIZATION")
    print("="*80)
    print()

    # Get mappings
    category_mapping = create_category_mapping()
    stem_mapping = create_stem_field_mapping()

    # Apply category standardization
    print("Standardizing categories...")
    unmapped_categories = set()

    df['category_tier2'] = df['category']  # Preserve original
    df['category_tier1'] = df['category'].apply(
        lambda x: category_mapping.get(x, 'Other') if pd.notna(x) else 'Other'
    )

    # Track unmapped
    for cat in df['category'].unique():
        if pd.notna(cat) and cat not in category_mapping:
            unmapped_categories.add(cat)

    print(f"  Tier 1 categories: {df['category_tier1'].nunique()}")
    print(f"  Tier 2 categories: {df['category_tier2'].nunique()}")
    print(f"  Unmapped categories: {len(unmapped_categories)}")

    # Apply STEM field standardization
    print("\nStandardizing STEM fields...")
    unmapped_stems = set()

    df['stem_field_tier2'] = df['stem_fields']  # Preserve original

    def map_stem_fields(field_str):
        if pd.isna(field_str):
            return 'Multi-disciplinary STEM'

        # Handle multi-field resources (comma or semicolon separated)
        fields = [f.strip() for f in str(field_str).replace(';', ',').split(',')]
        mapped = []

        for field in fields:
            if field in stem_mapping:
                mapped.append(stem_mapping[field])
            else:
                # Try partial matching
                found = False
                for key, value in stem_mapping.items():
                    if key.lower() in field.lower() or field.lower() in key.lower():
                        mapped.append(value)
                        found = True
                        break
                if not found:
                    mapped.append('Other STEM')
                    unmapped_stems.add(field)

        # Remove duplicates and join
        return '; '.join(sorted(set(mapped)))

    df['stem_field_tier1'] = df['stem_fields'].apply(map_stem_fields)

    print(f"  Tier 1 STEM fields: {df['stem_field_tier1'].nunique()}")
    print(f"  Tier 2 STEM fields: {df['stem_field_tier2'].nunique()}")
    print(f"  Unmapped STEM terms: {len(unmapped_stems)}")

    # Save unmapped values
    unmapped_df = pd.DataFrame({
        'type': ['category'] * len(unmapped_categories) + ['stem_field'] * len(unmapped_stems),
        'value': list(unmapped_categories) + list(unmapped_stems)
    })

    if not unmapped_df.empty:
        unmapped_df.to_csv(
            OUTPUT_DIR / "manual_review_needed" / "unmapped_values.csv",
            index=False,
            encoding='utf-8'
        )

    # Save mappings as JSON
    with open(OUTPUT_DIR / "processing_artifacts" / "category_mapping.json", 'w') as f:
        json.dump(category_mapping, f, indent=2)

    with open(OUTPUT_DIR / "processing_artifacts" / "stem_field_mapping.json", 'w') as f:
        json.dump(stem_mapping, f, indent=2)

    print("\n" + "="*80 + "\n")

    return df

def validate_standardization(df):
    """Validate standardization quality"""

    print("="*80)
    print("PHASE 3E: VALIDATING STANDARDIZATION")
    print("="*80)
    print()

    print("TIER 1 CATEGORY DISTRIBUTION:")
    print("-"*80)
    cat_dist = df['category_tier1'].value_counts()
    for cat, count in cat_dist.items():
        print(f"  {cat:40s} {count:4d} ({count/len(df)*100:.1f}%)")

    print(f"\n\nTIER 1 STEM FIELD DISTRIBUTION (Top 20):")
    print("-"*80)
    stem_dist = df['stem_field_tier1'].value_counts()
    for stem, count in stem_dist.head(20).items():
        print(f"  {stem:50s} {count:4d} ({count/len(df)*100:.1f}%)")

    print("\n" + "="*80 + "\n")

    return cat_dist, stem_dist

# ============================================================================
# PHASE 4: FINAL DATASET ASSEMBLY & VALIDATION
# ============================================================================

def generate_final_quality_report(df, desc_stats, enhanced_count):
    """Generate comprehensive quality report"""

    print("="*80)
    print("PHASE 4B: GENERATING FINAL QUALITY REPORT")
    print("="*80)
    print()

    report_lines = []
    report_lines.append("="*80)
    report_lines.append("BLACK MINDS IN STEM - ML PIPELINE READINESS REPORT")
    report_lines.append("="*80)
    report_lines.append("")

    # Data Completeness
    report_lines.append("DATA COMPLETENESS")
    report_lines.append("-"*80)
    report_lines.append(f"{'Feature':<40} {'Before':<15} {'After':<15} {'Status'}")
    report_lines.append("-"*80)

    critical_features = [
        'description', 'stem_fields', 'category', 'target_grade',
        'cost', 'location_type', 'financial_barrier_level', 'hidden_costs_level',
        'transportation_required', 'rural_accessible', 'internet_dependency'
    ]

    for feature in critical_features:
        if feature in df.columns:
            completeness = (df[feature].notna().sum() / len(df) * 100)
            # We don't have "before" stats, so we'll note if predicted
            if f'{feature}_predicted' in df.columns:
                predicted_pct = (df[f'{feature}_predicted'] == True).sum() / len(df) * 100
                status = f"[PREDICTED {predicted_pct:.0f}%]"
            else:
                status = "[GOOD]" if completeness >= 95 else "[OK]" if completeness >= 80 else "[LOW]"

            report_lines.append(f"{feature:<40} {'N/A':<15} {completeness:>5.1f}%         {status}")

    # Description Quality
    report_lines.append("\n\nDESCRIPTION QUALITY")
    report_lines.append("-"*80)
    report_lines.append(f"Total resources: {len(df):,}")
    report_lines.append(f"Descriptions enhanced: {enhanced_count:,}")
    report_lines.append(f"Average word count: {df['word_count'].mean():.1f} words")
    report_lines.append(f"Median word count: {df['word_count'].median():.1f} words")
    report_lines.append(f"Resources with < 30 words: {(df['word_count'] < 30).sum()} ({(df['word_count'] < 30).sum()/len(df)*100:.1f}%)")
    report_lines.append(f"Resources with >= 80 words: {(df['word_count'] >= 80).sum()} ({(df['word_count'] >= 80).sum()/len(df)*100:.1f}%)")

    # Standardization
    report_lines.append("\n\nHIERARCHICAL STANDARDIZATION")
    report_lines.append("-"*80)
    report_lines.append(f"Category Tier 1 values: {df['category_tier1'].nunique()}")
    report_lines.append(f"Category Tier 2 values: {df['category_tier2'].nunique()}")
    report_lines.append(f"STEM Field Tier 1 values: {df['stem_field_tier1'].nunique()}")
    report_lines.append(f"STEM Field Tier 2 values: {df['stem_field_tier2'].nunique()}")

    # ML Pipeline Readiness
    report_lines.append("\n\nML PIPELINE READINESS")
    report_lines.append("-"*80)
    report_lines.append("Clustering Dimensions:")

    # Accessibility Profile
    access_features = ['financial_barrier_level', 'hidden_costs_level', 'transportation_required',
                      'rural_accessible', 'internet_dependency']
    access_complete = sum(df[f].notna().sum() for f in access_features if f in df.columns)
    access_total = len(df) * len([f for f in access_features if f in df.columns])
    access_pct = (access_complete / access_total * 100) if access_total > 0 else 0

    report_lines.append(f"  1. Accessibility Profile: {access_pct:.1f}% complete")

    # Academic Level
    academic_features = ['target_grade', 'prerequisite_level']
    academic_complete = sum(df[f].notna().sum() for f in academic_features if f in df.columns)
    academic_total = len(df) * len([f for f in academic_features if f in df.columns])
    academic_pct = (academic_complete / academic_total * 100) if academic_total > 0 else 0

    report_lines.append(f"  2. Academic Level: {academic_pct:.1f}% complete")

    # STEM Field Focus
    stem_complete = df['stem_field_tier1'].notna().sum()
    stem_pct = (stem_complete / len(df) * 100)

    report_lines.append(f"  3. STEM Field Focus: {stem_pct:.1f}% complete")

    # Resource Format
    format_features = ['category_tier1', 'location_type', 'time_commitment']
    format_complete = sum(df[f].notna().sum() for f in format_features if f in df.columns)
    format_total = len(df) * len([f for f in format_features if f in df.columns])
    format_pct = (format_complete / format_total * 100) if format_total > 0 else 0

    report_lines.append(f"  4. Resource Format: {format_pct:.1f}% complete")

    # Overall readiness
    overall_pct = (access_pct + academic_pct + stem_pct + format_pct) / 4
    report_lines.append(f"\nOverall ML Pipeline Readiness: {overall_pct:.1f}%")

    if overall_pct >= 95:
        status = "[READY]"
    elif overall_pct >= 85:
        status = "[MOSTLY READY]"
    else:
        status = "[NEEDS WORK]"

    report_lines.append(f"Status: {status}")

    report_lines.append("\n" + "="*80)

    report_text = '\n'.join(report_lines)
    print(report_text)

    # Save report
    with open(OUTPUT_DIR / "ml_ready_summary_report.txt", 'w', encoding='utf-8') as f:
        f.write(report_text)

    print("\n" + "="*80 + "\n")

    return report_text

def save_final_outputs(df):
    """Save all final outputs"""

    print("="*80)
    print("PHASE 4C: SAVING FINAL OUTPUTS")
    print("="*80)
    print()

    # Save main ML-ready dataset
    main_file = OUTPUT_DIR / "bmis_ml_ready_dataset.csv"
    df.to_csv(main_file, index=False, encoding='utf-8')
    print(f"[OK] ML-ready dataset saved: {main_file}")
    print(f"     {len(df):,} resources, {len(df.columns)} columns")

    # Save TF-IDF text corpus separately
    tfidf_file = OUTPUT_DIR / "tfidf_text_corpus.txt"
    with open(tfidf_file, 'w', encoding='utf-8') as f:
        for text in df['tfidf_text']:
            f.write(text + '\n')
    print(f"[OK] TF-IDF corpus saved: {tfidf_file}")

    print("\nAll outputs saved to: {OUTPUT_DIR}")
    print("="*80 + "\n")

# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """Main execution function"""

    # Load cleaned dataset
    print(f"Loading dataset from: {INPUT_FILE}")
    df = pd.read_csv(INPUT_FILE)
    print(f"Loaded {len(df):,} resources with {len(df.columns)} columns")
    print()

    # Phase 1: Description Enhancement
    desc_stats = analyze_description_quality(df)
    df, enhanced_count = enhance_descriptions(df)
    df = create_tfidf_text(df)

    # Phase 2: ML Prediction
    df, predictions, importances = ml_predict_all_features(df)

    # Phase 3: Hierarchical Standardization
    category_dist = analyze_category_distribution(df)
    df = apply_hierarchical_standardization(df)
    cat_dist, stem_dist = validate_standardization(df)

    # Phase 4: Final Assembly
    print("="*80)
    print("PHASE 4A: FINAL DATASET ASSEMBLY")
    print("="*80)
    print()
    print(f"Final dataset: {len(df):,} resources, {len(df.columns)} columns")
    print()

    # Generate quality report
    quality_report = generate_final_quality_report(df, desc_stats, enhanced_count)

    # Save outputs
    save_final_outputs(df)

    print("="*80)
    print("DATA COMPLETION & STANDARDIZATION COMPLETE!")
    print("="*80)
    print()
    print("Next step: Run ML clustering pipeline")
    print("="*80)

if __name__ == "__main__":
    main()
