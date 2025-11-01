# BMIS ML Pipeline: Production-Ready Recommendation System

**Status**: ✅ Beta Deployment Ready (Version 1.1 Beta)
**Last Updated**: 2025-10-15
**Web App**: Streamlit application with location and grade filters

---

## 🚀 Quick Start (Beta)

### Run Web Application

```bash
pip install -r requirements.txt
streamlit run app.py
```

**App opens automatically at** `http://localhost:8501`

### Features

- ✅ **Interactive Web Interface**: Complete student profile form and get recommendations
- ✅ **Location Filter**: Virtual/In-person/Hybrid filtering
- ✅ **Grade Filter**: Age-appropriate resource filtering
- ✅ **67.7% Accessibility**: Low-income students get affordable resources
- ✅ **Mobile Responsive**: Works on all devices
- ✅ **Export**: Download recommendations as CSV

### For Full Details

- **Quick Start**: See `QUICK_START.md`
- **Beta Deployment**: See `BETA_DEPLOYMENT_GUIDE.md`
- **Validation Report**: See `testing/VALIDATION_REPORT.md`

---

## 🎉 Critical Fixes Applied!

**Version 1.1** includes three critical bug fixes that dramatically improve recommendation quality:

- ✅ **Fixed accessibility encoding**: Low-income students now get 55% Low/Free resources (was 0%)
- ✅ **Improved filtering logic**: 10-40x more candidates per profile
- ✅ **Optimized parameters**: Better diversity and coverage

**See [FIXES_APPLIED.md](FIXES_APPLIED.md) for detailed before/after metrics.**

---

## Overview

This is a complete machine learning pipeline for **Black Minds in STEM (BMIS)** - a platform that matches Black high school students with STEM resources based on their complete contextual profile, not just academic interests.

### Key Innovation

Multi-dimensional clustering that considers:
- Financial circumstances
- Geographic location
- Family support
- Academic preparation
- STEM interests

## Dataset

- **File**: `bmis_final_ml_ready_dataset_cs_refined.csv`
- **Resources**: 2,237 high-quality K-12 STEM opportunities
- **Quality Score**: 96-97/100 (production-ready)

## Architecture

### Four Independent K-Means Models

1. **Accessibility Profile Clustering** (15 clusters, Silhouette: 0.688)
   - Financial barriers
   - Hidden costs
   - Location type
   - Transportation requirements

2. **Academic Level Clustering** (12 clusters, Silhouette: 0.549)
   - Prerequisite level
   - Target grade
   - Time commitment
   - Support level

3. **STEM Field Focus Clustering** (19 clusters, Silhouette: 0.419)
   - 18 balanced STEM categories
   - Resource types
   - Specializations

4. **Resource Format Clustering** (15 clusters, Silhouette: 0.757)
   - Program format
   - Time structure
   - Engagement type

### TF-IDF Similarity Engine

- **Vocabulary**: 500 terms
- **Matrix**: 2,237 x 500 (sparse)
- **Similarity Distribution**: Mean 0.098, Std 0.101

## Installation

```bash
cd bmis_ml_pipeline
pip install -r requirements.txt
```

## Usage

### Training Models

```bash
# Run complete training pipeline
cd src
python kmeans_clustering.py
python tfidf_similarity.py
```

### Getting Recommendations

```python
from src.recommendation_engine import BMISRecommendationEngine

# Load trained models
engine = BMISRecommendationEngine()
engine.load_all_models()

# Define student profile
student_profile = {
    'financial_situation': 'Low',  # Low/Medium/High budget
    'location': 'Virtual',  # Virtual/Hybrid/In-person
    'transportation_available': False,
    'grade_level': 11,  # 6-12
    'academic_level': 'Intermediate',  # Beginner/Intermediate/Advanced
    'time_availability': 10,  # hours/week
    'support_needed': 'High',  # Low/Medium/High
    'stem_interests': 'machine learning programming python',
    'stem_fields': ['Artificial Intelligence/Machine Learning', 'Computer Science'],
    'format_preferences': ['Online Course', 'Learning Platform']
}

# Get recommendations
recommendations = engine.get_recommendations(
    student_profile,
    top_n=20,
    min_similarity=0.2
)

print(recommendations[['name', 'category', 'stem_field', 'similarity_score']])
```

## File Structure

```
bmis_ml_pipeline/
├── data/
│   └── bmis_final_ml_ready_dataset_cs_refined.csv
├── models/
│   ├── accessibility_kmeans.pkl
│   ├── academic_kmeans.pkl
│   ├── stem_field_kmeans.pkl
│   ├── format_kmeans.pkl
│   ├── tfidf_vectorizer.pkl
│   ├── tfidf_matrix.npz
│   └── similarity_matrix.npy
├── preprocessors/
│   ├── accessibility_scaler.pkl
│   ├── academic_scaler.pkl
│   ├── format_scaler.pkl
│   └── preprocessed_data.csv
├── outputs/
│   ├── cluster_analysis/
│   │   └── cluster_report.txt
│   ├── tfidf_analysis_report.txt
│   └── evaluation_report.txt
├── src/
│   ├── preprocessing.py
│   ├── kmeans_clustering.py
│   ├── tfidf_similarity.py
│   ├── recommendation_engine.py
│   └── evaluation.py
├── requirements.txt
└── README.md
```

## Model Performance

### Clustering Quality

| Model | Clusters | Silhouette Score | Quality |
|-------|----------|------------------|---------|
| Accessibility | 15 | 0.688 | Excellent |
| Academic | 12 | 0.549 | Excellent |
| STEM Field | 19 | 0.419 | Good |
| Format | 15 | 0.757 | Excellent |

All models meet the quality threshold (Silhouette > 0.3).

### TF-IDF Performance

- **Vocabulary Size**: 500 terms
- **Mean Similarity**: 0.098
- **High-similarity pairs (>0.7)**: 4,336 pairs (0.17%)
- **Search Accuracy**: Excellent (validated with sample queries)

## Key Features

### Preprocessing (`preprocessing.py`)
- Standardizes categorical variables
- Extracts numeric values from text
- Handles missing values intelligently
- Scales features for clustering

### Clustering (`kmeans_clustering.py`)
- Automatic optimal K selection using elbow method
- Silhouette analysis for validation
- Comprehensive cluster interpretation
- Model persistence for deployment

### TF-IDF Similarity (`tfidf_similarity.py`)
- 500-term vocabulary with n-grams
- Cosine similarity computation
- Text-based resource search
- Similarity matrix caching

### Recommendation Engine (`recommendation_engine.py`)
- Two-stage filtering (cluster + TF-IDF)
- Multi-dimensional profile matching
- Configurable thresholds
- Detailed result explanations

### Evaluation (`evaluation.py`)
- Clustering quality metrics
- Recommendation diversity assessment
- Accessibility alignment checks
- Coverage analysis

## Recommendation Algorithm (v1.1 - FIXED)

### Stage 1: Cluster-Based Filtering (Broad Match)

1. Encode student profile for each dimension
2. Find top **5** closest clusters per model (increased from 3)
3. **Take UNION** of accessibility + academic candidates (changed from intersection)
4. Intersect with STEM field candidates for precision
5. Smart fallback: If <50 candidates, use union instead
6. Expected result: 150-300 candidates

### Stage 2: TF-IDF Ranking (Precise Match)

1. Transform student interest text to TF-IDF vector
2. Compute cosine similarity with all candidates
3. Filter by minimum similarity threshold (default: **0.2**, lowered from 0.3)
4. Rank by similarity score
5. Return top N recommendations (default: 20)

## Evaluation Results (After v1.1 Fixes)

### Clustering Quality: ✅ EXCELLENT (Unchanged)
- All models exceed minimum quality threshold
- Cluster sizes are reasonable (21-408 resources)
- Clear interpretability of clusters

### TF-IDF Quality: ✅ EXCELLENT (Unchanged)
- Good vocabulary coverage (500 terms)
- Proper similarity distribution
- High-similarity pairs are semantically valid

### Recommendation Quality: ✅ EXCELLENT (FIXED!)
- **Candidates**: 150-300 per profile (was 6-33) ✅
- **Recommendations**: 20 per profile (was 1-17) ✅
- **Diversity**: 7-8 categories per profile (was 1-2) ✅
- **Accessibility Alignment**: 55% Low/Free for low-income students (was 0%) ✅✅✅

**Status**: ✅ Production-ready! All critical issues fixed.

## Known Limitations (Minor)

### 1. Location Matching (5-25%)
- **Status**: Minor issue
- **Impact**: Low - users can filter results themselves
- **Future**: Consider weighting location preferences more heavily

### 2. STEM Field Diversity (1-2 fields)
- **Status**: Minor issue
- **Impact**: Medium - could improve discovery
- **Future**: Implement diversity boosting in ranking stage

## Testing

Run comprehensive evaluation:
```bash
cd src
python evaluation.py
```

Test specific profiles:
```bash
python recommendation_engine.py
```

Run all tests:
```bash
python preprocessing.py    # Validate preprocessing
python kmeans_clustering.py  # Train and analyze clusters
python tfidf_similarity.py   # Build TF-IDF and test search
python evaluation.py         # Full pipeline evaluation
```

## Deployment Considerations

### Model Files Size
- K-Means models: ~100 KB each
- TF-IDF vectorizer: ~500 KB
- TF-IDF matrix (sparse): ~2 MB
- Similarity matrix (dense): ~40 MB
- **Total**: ~45 MB (reasonable for deployment)

### Performance
- Model loading: < 2 seconds
- Recommendation generation: < 0.5 seconds
- Suitable for real-time API

### Scalability
- Current: 2,237 resources
- Can scale to ~10,000 resources without architecture changes
- For >10K, consider approximate nearest neighbors (e.g., FAISS)

## Contributing

### Adding New Features
1. Update `preprocessing.py` for new data fields
2. Retrain models with `kmeans_clustering.py`
3. Rebuild TF-IDF with `tfidf_similarity.py`
4. Test with `evaluation.py`

### Tuning Parameters
- Adjust K-means cluster count ranges in `kmeans_clustering.py`
- Modify TF-IDF vocabulary size in `tfidf_similarity.py`
- Change filtering logic in `recommendation_engine.py`

## License

MIT License - see LICENSE file

## Contact

For questions or issues, please contact the BMIS development team.

## Acknowledgments

Built for Black Minds in STEM to help Black high school students discover relevant STEM opportunities based on their complete profile, not just academic interests.
