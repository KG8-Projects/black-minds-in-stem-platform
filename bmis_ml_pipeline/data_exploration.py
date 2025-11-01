"""
Initial Data Exploration for BMIS ML Pipeline
Validates dataset structure and explores key features for clustering
"""

import pandas as pd
import numpy as np

# Load dataset
df = pd.read_csv('data/bmis_final_ml_ready_dataset_cs_refined.csv')

print("="*80)
print("BMIS Dataset Overview")
print("="*80)
print(f"Total resources: {len(df)}")
print(f"Total columns: {len(df.columns)}")
print(f"\nColumns:\n{list(df.columns)}")

print("\n" + "="*80)
print("Data Quality Check")
print("="*80)
print(f"Missing values per column:")
print(df.isnull().sum()[df.isnull().sum() > 0])

print("\n" + "="*80)
print("Key Features for Clustering")
print("="*80)

# Accessibility Profile features
print("\n1. ACCESSIBILITY PROFILE FEATURES")
print("-" * 40)
if 'financial_barrier_level' in df.columns:
    print(f"financial_barrier_level distribution:")
    print(df['financial_barrier_level'].value_counts())
    if 'financial_barrier_level_reliable' in df.columns:
        print(f"  Reliable values: {df['financial_barrier_level_reliable'].sum()}/{len(df)}")

if 'hidden_costs_level' in df.columns:
    print(f"\nhidden_costs_level distribution:")
    print(df['hidden_costs_level'].value_counts())

if 'cost_category' in df.columns:
    print(f"\ncost_category distribution:")
    print(df['cost_category'].value_counts())

if 'location_type' in df.columns:
    print(f"\nlocation_type distribution:")
    print(df['location_type'].value_counts())

if 'transportation_required' in df.columns:
    print(f"\ntransportation_required distribution:")
    print(df['transportation_required'].value_counts())

# Academic Level features
print("\n2. ACADEMIC LEVEL FEATURES")
print("-" * 40)
if 'prerequisite_level' in df.columns:
    print(f"prerequisite_level distribution:")
    print(df['prerequisite_level'].value_counts())

if 'target_grade_standardized' in df.columns:
    print(f"\ntarget_grade_standardized (top 10):")
    print(df['target_grade_standardized'].value_counts().head(10))

if 'time_commitment' in df.columns:
    print(f"\ntime_commitment (sample values):")
    print(df['time_commitment'].value_counts().head(10))

if 'support_level' in df.columns:
    print(f"\nsupport_level distribution:")
    print(df['support_level'].value_counts())

# STEM Field features
print("\n3. STEM FIELD FEATURES")
print("-" * 40)
if 'stem_field_tier1' in df.columns:
    print(f"stem_field_tier1 distribution:")
    print(df['stem_field_tier1'].value_counts())

if 'category_tier1' in df.columns:
    print(f"\ncategory_tier1 distribution:")
    print(df['category_tier1'].value_counts())

# TF-IDF text
print("\n4. TF-IDF TEXT")
print("-" * 40)
if 'tfidf_text' in df.columns:
    print(f"tfidf_text available: Yes")
    print(f"Sample text (first 200 chars):")
    print(df['tfidf_text'].iloc[0][:200] + "...")
    print(f"\nAverage text length: {df['tfidf_text'].str.len().mean():.0f} characters")
else:
    print("tfidf_text column NOT FOUND")

print("\n" + "="*80)
print("Exploration Complete!")
print("="*80)
