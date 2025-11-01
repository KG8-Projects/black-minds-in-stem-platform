# Dataset Versions Guide - Which One to Use?

## Quick Answer

### 🎯 **USE THIS DATASET:**

```
final_ml_ready_data/bmis_final_ml_ready_dataset_cs_refined.csv
```

**Why:** CS split applied, 18 balanced tier1 categories, maximum 18.4% concentration

---

## Dataset Version Comparison

### Version 1: Original (DON'T USE)
**File:** `ml_ready_data/bmis_ml_ready_dataset.csv`

**Issues:**
- ❌ Target grade: 72% marked K-12 (over-standardized)
- ❌ ML predictions: 61.4% avg confidence (unreliable)
- ❌ CS concentration: 41% (too high)
- ❌ Missing reliability flags

**Status:** DEPRECATED - Use for reference only

---

### Version 2: First Fix (DON'T USE)
**File:** `ml_ready_data/bmis_ml_ready_dataset_fixed.csv`

**Improvements:**
- ✅ Prerequisite_level: 100% complete
- ✅ STEM tier1: 11 categories
- ✅ Target grade: 32 unique values
- ✅ Logical inconsistencies: 0

**Remaining Issues:**
- ❌ Target grade: Still 72% marked K-12
- ❌ CS concentration: Still 41%
- ❌ No prediction reliability flags

**Status:** DEPRECATED - Intermediate version

---

### Version 3: Critical Fixes Applied (DON'T USE DIRECTLY)
**File:** `final_ml_ready_data/bmis_final_ml_ready_dataset.csv`

**Improvements:**
- ✅ Target grade: 6.2% K-12 (specificity preserved!)
- ✅ Prediction reliability: 82.9% avg confidence (filtered)
- ✅ Description quality: 0.5% under 30 words
- ✅ ML Readiness: 94.7 / 100

**Remaining Issue:**
- ⚠️ CS concentration: Still 41% (needs splitting)

**Status:** SUPERSEDED by CS-refined version

---

### Version 4: CS-Refined (✅ USE THIS!)
**File:** `final_ml_ready_data/bmis_final_ml_ready_dataset_cs_refined.csv`

**All Improvements:**
- ✅ Target grade: 6.2% K-12 (specificity preserved)
- ✅ Prediction reliability: 82.9% avg confidence
- ✅ CS split: 41% → 18.4% max concentration
- ✅ Tier1 categories: 18 (from 11)
- ✅ Balanced distribution for clustering

**Specifications:**
- Resources: 2,237
- Columns: 52
- Tier1 categories: 18
- Maximum concentration: 18.4%
- ML Readiness: ~96-97 / 100 (estimated)

**Status:** ✅ **PRODUCTION READY - USE THIS!**

---

## Key Differences Summary

| Feature | Version 3 | Version 4 (CS-Refined) |
|---------|-----------|------------------------|
| **Target Grade K-12%** | 6.2% ✅ | 6.2% ✅ |
| **Prediction Reliability** | 82.9% ✅ | 82.9% ✅ |
| **CS Concentration** | 41.0% ❌ | 8.4% ✅ |
| **Max Concentration** | 41.0% ❌ | 18.4% ✅ |
| **Tier1 Categories** | 11 | 18 ✅ |
| **Clustering Balance** | Poor | Excellent ✅ |
| **Columns** | 51 | 52 (+1) |
| **Status** | Superseded | **Production Ready** |

---

## Which Dataset for What Purpose?

### For ML Pipeline Development ✅
**Use:** `bmis_final_ml_ready_dataset_cs_refined.csv`

**Reason:**
- Balanced tier1 distribution (18 categories)
- No category dominates (max 18.4%)
- Clear specializations (AI/ML, Data Science, Cybersecurity, etc.)
- Optimal for K-Means clustering

---

### For Understanding Evolution 📚
**Compare these versions:**
1. `ml_ready_data/bmis_ml_ready_dataset.csv` (original)
2. `final_ml_ready_data/bmis_final_ml_ready_dataset.csv` (critical fixes)
3. `final_ml_ready_data/bmis_final_ml_ready_dataset_cs_refined.csv` (final)

**Shows progression:**
- Original → Critical fixes → CS refinement
- 66/100 → 94.7/100 → ~96-97/100 readiness

---

### For Manual Review (Optional Enhancement)
**Check:** `final_ml_ready_data/manual_review/thin_descriptions.csv`

**Contains:** 11 resources with <30 words (optional enhancement)

---

## Column Differences

### Common Columns (All Versions)
- Core metadata: name, description, url, source
- Classification: category, stem_fields, tier1/tier2
- Academic: target_grade, prerequisite_level, time_commitment
- Accessibility: cost, location, financial barriers, etc.
- 40+ columns total

### Version 3 Additions (51 columns)
```diff
+ target_grade_original (audit trail)
+ target_grade_standardized (fixed!)
+ financial_barrier_level_high_confidence
+ financial_barrier_level_reliable
+ hidden_costs_level_high_confidence
+ hidden_costs_level_reliable
+ internet_dependency_high_confidence
+ internet_dependency_reliable
```

### Version 4 Addition (52 columns)
```diff
All Version 3 columns PLUS:
+ stem_field_tier1_original (audit trail for CS split)
```

---

## How to Use CS-Refined Dataset

### Load the Dataset
```python
import pandas as pd

df = pd.read_csv('final_ml_ready_data/bmis_final_ml_ready_dataset_cs_refined.csv')

print(f"Resources: {len(df):,}")
print(f"Columns: {len(df.columns)}")
```

### Check Tier1 Distribution
```python
# See new CS sub-domains
print("\nTier1 STEM Fields:")
print(df['stem_field_tier1'].value_counts())

# Compare to original (before split)
print("\nOriginal (before CS split):")
print(df['stem_field_tier1_original'].value_counts())
```

### Filter by CS Sub-Domain
```python
# Get AI/ML resources specifically
ai_ml = df[df['stem_field_tier1'] == 'Artificial Intelligence/Machine Learning']
print(f"AI/ML resources: {len(ai_ml)}")  # 85

# Get Cybersecurity resources
cybersec = df[df['stem_field_tier1'] == 'Cybersecurity']
print(f"Cybersecurity resources: {len(cybersec)}")  # 60

# Get Data Science resources
data_sci = df[df['stem_field_tier1'] == 'Data Science']
print(f"Data Science resources: {len(data_sci)}")  # 65

# Get general CS resources
cs_general = df[df['stem_field_tier1'] == 'Computer Science']
print(f"CS General resources: {len(cs_general)}")  # 189
```

### Clustering with CS Sub-Domains
```python
from sklearn.cluster import KMeans
from sklearn.preprocessing import LabelEncoder

# Use refined tier1 for clustering
le = LabelEncoder()
df['stem_tier1_encoded'] = le.fit_transform(df['stem_field_tier1'])

# Now 18 categories instead of 11
print(f"Unique tier1 categories: {df['stem_field_tier1'].nunique()}")  # 18

# Better balance for clustering
print(df['stem_field_tier1'].value_counts() / len(df))
```

---

## Important Notes

### ⚠️ Use Correct Column Names

**Target Grade:**
```python
# ❌ WRONG - Over-standardized (72% K-12)
df['target_grade']

# ✅ CORRECT - Fixed (6% K-12)
df['target_grade_standardized']
```

**STEM Field Tier1:**
```python
# ✅ Use this for clustering
df['stem_field_tier1']  # 18 categories, max 18.4%

# 📚 Use this for audit/comparison only
df['stem_field_tier1_original']  # 11 categories, 41% CS
```

**Prediction Reliability:**
```python
# ✅ Check reliability flags before using predictions
reliable_financial = df[df['financial_barrier_level_reliable'] == True]
reliable_hidden = df[df['hidden_costs_level_reliable'] == True]
reliable_internet = df[df['internet_dependency_reliable'] == True]
```

---

## Validation Checklist

Before using the dataset, verify:

- [x] File: `bmis_final_ml_ready_dataset_cs_refined.csv` ✅
- [x] Resources: 2,237 ✅
- [x] Columns: 52 ✅
- [x] Tier1 categories: 18 ✅
- [x] Maximum concentration: <20% ✅
- [x] Target grade column: `target_grade_standardized` ✅
- [x] STEM field column: `stem_field_tier1` ✅
- [x] Reliability flags: Present ✅

---

## Quick Reference

### Production Dataset
```
📄 bmis_final_ml_ready_dataset_cs_refined.csv
   ├─ 2,237 resources
   ├─ 52 columns
   ├─ 18 tier1 STEM categories
   ├─ Max 18.4% concentration (Software Engineering)
   ├─ 6.2% marked K-12 (target_grade_standardized)
   └─ 82.9% prediction confidence (filtered)
```

### Key Columns to Use
```python
# Academic matching
df['target_grade_standardized']  # Fixed specificity
df['prerequisite_level']
df['time_commitment']

# STEM field clustering
df['stem_field_tier1']  # 18 balanced categories
df['category_tier1']    # 13 categories

# Accessibility filtering
df['financial_barrier_level_reliable']
df['hidden_costs_level_reliable']
df['internet_dependency_reliable']
df['location_type']
df['transportation_required']
df['rural_accessible']

# Semantic similarity
df['tfidf_text']  # Pre-generated, updated with CS split
```

---

## Summary

**✅ For ML Pipeline:** Use `bmis_final_ml_ready_dataset_cs_refined.csv`

**📊 Key Stats:**
- 2,237 resources
- 18 tier1 categories (balanced)
- 18.4% maximum concentration
- 6.2% K-12 (specific grades preserved)
- 82.9% prediction confidence (reliable only)

**🎯 Status:** PRODUCTION READY FOR ML CLUSTERING

---

**Last Updated:** 2025-10-14
**Current Version:** CS-Refined (Version 4)
**Readiness:** ~96-97 / 100
**Decision:** 🟢 GO FOR ML PIPELINE
