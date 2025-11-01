"""
BMIS Recommendation Engine

Main recommendation system that combines:
1. Four K-Means clustering models (accessibility, academic, STEM field, format)
2. TF-IDF similarity scoring

Two-stage filtering:
- Stage 1: Cluster-based filtering (broad match)
- Stage 2: TF-IDF ranking (precise match)
"""

import numpy as np
import pandas as pd
import joblib
from scipy.sparse import load_npz
from sklearn.preprocessing import StandardScaler


class BMISRecommendationEngine:
    """Complete recommendation system for BMIS resources"""

    def __init__(self, models_dir='models', preprocessors_dir='preprocessors', data_path='data/bmis_final_ml_ready_dataset_cs_refined.csv'):
        self.models_dir = models_dir
        self.preprocessors_dir = preprocessors_dir
        self.data_path = data_path

        # Models and data
        self.df = None
        self.preprocessed_df = None
        self.kmeans_models = {}
        self.scalers = {}
        self.tfidf_vectorizer = None
        self.tfidf_matrix = None
        self.cluster_assignments = {}

    def load_all_models(self):
        """Load all trained models and data"""
        print("Loading BMIS Recommendation Engine...")
        print("-" * 60)

        # Load original data
        self.df = pd.read_csv(self.data_path)
        print(f"[OK] Loaded {len(self.df)} resources")

        # Load preprocessed data
        self.preprocessed_df = pd.read_csv(f'{self.preprocessors_dir}/preprocessed_data.csv')
        print(f"[OK] Loaded preprocessed data")

        # Load K-Means models
        for model_name in ['accessibility', 'academic', 'stem_field', 'format']:
            try:
                self.kmeans_models[model_name] = joblib.load(f'{self.models_dir}/{model_name}_kmeans.pkl')
                print(f"[OK] Loaded {model_name} K-Means model")

                # Load cluster assignments
                clusters = pd.read_csv(f'{self.models_dir}/{model_name}_clusters.csv', index_col=0)
                self.cluster_assignments[model_name] = clusters.iloc[:, 0]
            except Exception as e:
                print(f"[WARNING] Could not load {model_name} model: {e}")

        # Load scalers
        for scaler_name in ['accessibility', 'academic', 'format']:
            try:
                self.scalers[scaler_name] = joblib.load(f'{self.preprocessors_dir}/{scaler_name}_scaler.pkl')
                print(f"[OK] Loaded {scaler_name} scaler")
            except Exception as e:
                print(f"[WARNING] Could not load {scaler_name} scaler: {e}")

        # Load TF-IDF models
        try:
            self.tfidf_vectorizer = joblib.load(f'{self.models_dir}/tfidf_vectorizer.pkl')
            self.tfidf_matrix = load_npz(f'{self.models_dir}/tfidf_matrix.npz')
            print(f"[OK] Loaded TF-IDF vectorizer and matrix")
        except Exception as e:
            print(f"[WARNING] Could not load TF-IDF models: {e}")

        print("\n[OK] All models loaded successfully!")
        return self

    def _encode_student_accessibility_features(self, profile):
        """
        Encode student accessibility profile for clustering

        Args:
            profile: dict with keys:
                - financial_situation: 'Low'/'Medium'/'High' (budget availability)
                - location: 'Virtual'/'Hybrid'/'In-person'
                - transportation_available: True/False

        Returns:
            Encoded and scaled feature vector
        """
        # FIXED: Direct mapping - Low budget seeks Low barrier resources
        # Student with Low budget (0) matches with Low barrier resources (0)
        financial_map = {'Low': 0, 'Medium': 1, 'High': 2}
        financial_encoded = financial_map.get(profile.get('financial_situation', 'Low'), 0)

        # Hidden costs preference - Low budget avoids hidden costs
        hidden_costs_map = {'Low': 0, 'Medium': 1, 'High': 2}
        hidden_costs_encoded = hidden_costs_map.get(profile.get('financial_situation', 'Low'), 0)

        # Cost category preference - Low budget prefers free/low-cost
        cost_map = {'Low': 0, 'Medium': 1, 'High': 2}
        cost_encoded = cost_map.get(profile.get('financial_situation', 'Low'), 0)

        # Location preference
        location_map = {'Virtual': 0, 'Hybrid': 1, 'In-person': 2}
        location_encoded = location_map.get(profile.get('location', 'Virtual'), 0)

        # Transportation
        transport_encoded = 2 if not profile.get('transportation_available', False) else 0

        features = np.array([financial_encoded, hidden_costs_encoded, cost_encoded,
                            location_encoded, transport_encoded]).reshape(1, -1)

        # Scale features
        if 'accessibility' in self.scalers:
            features = self.scalers['accessibility'].transform(features)

        return features

    def _encode_student_academic_features(self, profile):
        """
        Encode student academic profile for clustering

        Args:
            profile: dict with keys:
                - grade_level: int (6-12)
                - academic_level: 'Beginner'/'Intermediate'/'Advanced'
                - time_availability: int (hours/week)
                - support_needed: 'Low'/'Medium'/'High'

        Returns:
            Encoded and scaled feature vector
        """
        # Prerequisite level
        prereq_map = {'None': 0, 'Beginner': 1, 'Intermediate': 2, 'Advanced': 3}
        prereq_encoded = prereq_map.get(profile.get('academic_level', 'Beginner'), 1)

        # Grade level
        grade = float(profile.get('grade_level', 9))

        # Time commitment
        time = float(profile.get('time_availability', 5))

        # Support level
        support_map = {'Low': 0, 'Medium': 1, 'High': 2}
        support_encoded = support_map.get(profile.get('support_needed', 'Medium'), 1)

        features = np.array([prereq_encoded, grade, time, support_encoded]).reshape(1, -1)

        # Scale features
        if 'academic' in self.scalers:
            features = self.scalers['academic'].transform(features)

        return features

    def _encode_student_stem_features(self, profile):
        """
        Encode student STEM interest profile for clustering

        Args:
            profile: dict with keys:
                - stem_fields: list of STEM field names
                - format_preferences: list of category names

        Returns:
            Encoded one-hot feature vector
        """
        # Get all possible STEM fields and categories from data
        all_stem_fields = self.df['stem_field_tier1'].unique()
        all_categories = self.df['category_tier1'].unique()

        # Create one-hot encoding
        stem_fields = profile.get('stem_fields', [])
        format_prefs = profile.get('format_preferences', [])

        # STEM field one-hot
        stem_encoding = [1 if field in stem_fields else 0 for field in all_stem_fields]

        # Category one-hot
        category_encoding = [1 if cat in format_prefs else 0 for cat in all_categories]

        features = np.array(stem_encoding + category_encoding).reshape(1, -1)

        return features

    def _encode_student_format_features(self, profile):
        """
        Encode student format preference profile for clustering

        Args:
            profile: dict with keys:
                - format_preferences: list of category names
                - time_availability: int (hours/week)
                - support_needed: 'Low'/'Medium'/'High'

        Returns:
            Encoded feature vector
        """
        # Get all possible categories
        all_categories = self.df['category_tier1'].unique()
        format_prefs = profile.get('format_preferences', [])

        # Category one-hot
        category_encoding = [1 if cat in format_prefs else 0 for cat in all_categories]

        # Time commitment
        time = float(profile.get('time_availability', 5))

        # Support level
        support_map = {'Low': 0, 'Medium': 1, 'High': 2}
        support_encoded = support_map.get(profile.get('support_needed', 'Medium'), 1)

        # Combine
        features = np.array(category_encoding + [time, support_encoded]).reshape(1, -1)

        # Scale numeric features only (last 2 features)
        if 'format' in self.scalers:
            numeric_features = features[:, -2:].reshape(1, -1)
            scaled_numeric = self.scalers['format'].transform(numeric_features)
            features[:, -2:] = scaled_numeric

        return features

    def get_recommendations(self, student_profile, top_n=20, min_similarity=0.2, top_clusters=5):
        """
        Get personalized recommendations for a student

        Args:
            student_profile: dict with student information
            top_n: Number of recommendations to return (default: 20)
            min_similarity: Minimum TF-IDF similarity threshold (default: 0.2, lowered from 0.3 for better coverage)
            top_clusters: Number of top clusters to consider per dimension (default: 5, increased from 3 for better diversity)

        Returns:
            DataFrame of recommended resources with match scores
        """
        print("\n" + "="*60)
        print("Generating Recommendations")
        print("="*60)

        # Stage 1: Cluster-Based Filtering
        print("\nStage 1: Cluster-Based Filtering")
        print("-" * 60)

        # Initialize candidate sets for each dimension
        acc_candidates = set()
        acad_candidates = set()
        stem_candidates = set()

        # 1. Accessibility clustering
        if 'accessibility' in self.kmeans_models:
            acc_features = self._encode_student_accessibility_features(student_profile)
            acc_distances = self.kmeans_models['accessibility'].transform(acc_features)[0]
            top_acc_clusters = np.argsort(acc_distances)[:top_clusters]

            for cluster_id in top_acc_clusters:
                cluster_resources = self.cluster_assignments['accessibility'][
                    self.cluster_assignments['accessibility'] == cluster_id
                ].index.tolist()
                acc_candidates.update(cluster_resources)

            print(f"Accessibility: {len(acc_candidates)} candidates from {top_clusters} clusters")

        # 2. Academic clustering
        if 'academic' in self.kmeans_models:
            acad_features = self._encode_student_academic_features(student_profile)
            acad_distances = self.kmeans_models['academic'].transform(acad_features)[0]
            top_acad_clusters = np.argsort(acad_distances)[:top_clusters]

            for cluster_id in top_acad_clusters:
                cluster_resources = self.cluster_assignments['academic'][
                    self.cluster_assignments['academic'] == cluster_id
                ].index.tolist()
                acad_candidates.update(cluster_resources)

            print(f"Academic: {len(acad_candidates)} candidates from {top_clusters} clusters")

        # 3. STEM field clustering (if preferences provided)
        stem_fields = student_profile.get('stem_fields', [])
        if stem_fields:
            # For STEM, we use TF-IDF search instead of clustering for better precision
            stem_query = " ".join(stem_fields)
            stem_vec = self.tfidf_vectorizer.transform([stem_query])

            from sklearn.metrics.pairwise import cosine_similarity
            stem_similarities = cosine_similarity(stem_vec, self.tfidf_matrix)[0]
            stem_candidates = set(np.where(stem_similarities > 0.1)[0].tolist())

            print(f"STEM Fields: {len(stem_candidates)} candidates matching interests")

        # 4. Format/Category clustering (if preferences provided)
        format_candidates = set()
        format_preferences = student_profile.get('format_preferences', [])
        if format_preferences:
            # Use direct category matching for format preferences
            # This ensures user's selected categories are respected
            for idx in range(len(self.df)):
                resource_category = self.df.iloc[idx]['category_tier1']
                # Check if resource category matches any of user's format preferences
                for pref in format_preferences:
                    if pref.lower() in str(resource_category).lower():
                        format_candidates.add(idx)
                        break

            print(f"Format Preferences: {len(format_candidates)} candidates matching {format_preferences}")

        # FIXED: Use UNION for broader matching (instead of intersection)
        # Stage 1a: Union of accessibility and academic (cast wider net)
        if acc_candidates and acad_candidates:
            candidate_indices = acc_candidates.union(acad_candidates)
            print(f"Accessibility U Academic: {len(candidate_indices)} candidates")
        elif acc_candidates:
            candidate_indices = acc_candidates
        elif acad_candidates:
            candidate_indices = acad_candidates
        else:
            candidate_indices = set(range(len(self.df)))

        # Stage 1b: Intersect with STEM interests for precision (if provided)
        if stem_candidates:
            initial_count = len(candidate_indices)
            candidate_indices = candidate_indices.intersection(stem_candidates)
            print(f"After STEM intersection: {len(candidate_indices)} candidates (from {initial_count})")

            # Fallback: If intersection yields too few results, use union instead
            if len(candidate_indices) < 50:
                print(f"[INFO] STEM intersection too restrictive ({len(candidate_indices)} candidates), using union instead")
                candidate_indices = acc_candidates.union(acad_candidates).union(stem_candidates)

        # Stage 1c: Intersect with Format preferences (MANDATORY if specified)
        # This ensures user's category selections are strictly respected
        if format_candidates:
            initial_count = len(candidate_indices)
            candidate_indices = candidate_indices.intersection(format_candidates)
            print(f"After Format intersection: {len(candidate_indices)} candidates (from {initial_count})")

            # If format intersection yields too few results, use format candidates directly
            # (still respecting format preference as mandatory)
            if len(candidate_indices) < 20:
                print(f"[INFO] Format intersection yielded few results, using format candidates with broader filters")
                # Try format + STEM first
                if stem_candidates:
                    candidate_indices = format_candidates.intersection(stem_candidates)
                    if len(candidate_indices) < 20:
                        # If still too few, use format + accessibility
                        if acc_candidates:
                            candidate_indices = format_candidates.intersection(acc_candidates)
                # Last resort: just format candidates (format is MANDATORY)
                if len(candidate_indices) < 20:
                    candidate_indices = format_candidates
                    print(f"[INFO] Using format candidates only: {len(candidate_indices)} candidates")

        print(f"\nTotal candidates after filtering: {len(candidate_indices)}")

        # Stage 1d: Final fallback for edge cases
        if len(candidate_indices) < 20:
            print(f"[WARNING] Very few candidates ({len(candidate_indices)}). Relaxing filters...")
            # If format preferences specified, keep them as mandatory
            if format_candidates:
                print(f"[INFO] Keeping format preferences mandatory, relaxing other filters")
                candidate_indices = format_candidates
            else:
                # Use union of all dimensions
                all_candidates = acc_candidates.union(acad_candidates)
                if stem_candidates:
                    all_candidates = all_candidates.union(stem_candidates)
                candidate_indices = all_candidates if all_candidates else set(range(len(self.df)))

        # Stage 2: TF-IDF Ranking
        print("\nStage 2: TF-IDF Ranking")
        print("-" * 60)

        # Build student interest text
        interest_text = student_profile.get('stem_interests', '')
        if not interest_text and 'stem_fields' in student_profile:
            interest_text = " ".join(student_profile['stem_fields'])

        print(f"Student interests: '{interest_text}'")

        # Compute TF-IDF similarity
        if interest_text:
            student_vec = self.tfidf_vectorizer.transform([interest_text])

            from sklearn.metrics.pairwise import cosine_similarity
            similarities = cosine_similarity(student_vec, self.tfidf_matrix)[0]

            # Filter to candidates only
            candidate_indices_list = list(candidate_indices)
            candidate_similarities = [(idx, similarities[idx]) for idx in candidate_indices_list
                                     if similarities[idx] >= min_similarity]

            # Sort by similarity
            candidate_similarities.sort(key=lambda x: x[1], reverse=True)

            # Take top N
            top_recommendations = candidate_similarities[:top_n]

            print(f"Found {len(candidate_similarities)} resources above similarity threshold {min_similarity}")
            print(f"Returning top {len(top_recommendations)} recommendations")

        else:
            # No interest text, just return random sample from candidates
            print("[WARNING] No interest text provided. Returning random sample from candidates.")
            candidate_indices_list = list(candidate_indices)
            top_recommendations = [(idx, 0.0) for idx in candidate_indices_list[:top_n]]

        # Build results DataFrame
        results = []
        for rank, (idx, similarity) in enumerate(top_recommendations, 1):
            resource = self.df.iloc[idx]
            results.append({
                'rank': rank,
                'name': resource['name'],
                'category': resource['category_tier1'] if 'category_tier1' in resource else 'N/A',
                'stem_field': resource['stem_field_tier1'] if 'stem_field_tier1' in resource else 'N/A',
                'financial_barrier': resource['financial_barrier_level'] if 'financial_barrier_level' in resource else 'N/A',
                'location_type': resource['location_type'] if 'location_type' in resource else 'N/A',
                'target_grade': resource['target_grade_standardized'] if 'target_grade_standardized' in resource else 'N/A',
                'similarity_score': f"{similarity:.3f}",
                'url': resource['url'] if 'url' in resource else 'N/A',
                'description': resource['description'][:200] + '...' if 'description' in resource and len(str(resource['description'])) > 200 else resource.get('description', 'N/A')
            })

        results_df = pd.DataFrame(results)
        return results_df


def test_recommendation_engine():
    """Test the recommendation engine with sample profiles"""
    print("="*80)
    print("Testing BMIS Recommendation Engine")
    print("="*80)

    # Load engine
    engine = BMISRecommendationEngine()
    engine.load_all_models()

    # Test profile 1: Low-income student interested in AI/ML
    print("\n\n" + "="*80)
    print("TEST 1: Low-income 11th grader interested in AI/ML")
    print("="*80)

    profile1 = {
        'financial_situation': 'Low',  # Limited budget
        'location': 'Virtual',  # Prefers online
        'transportation_available': False,
        'grade_level': 11,
        'academic_level': 'Intermediate',
        'time_availability': 10,  # 10 hours/week
        'support_needed': 'High',
        'stem_interests': 'machine learning artificial intelligence programming python data science',
        'stem_fields': ['Artificial Intelligence/Machine Learning', 'Computer Science', 'Data Science'],
        'format_preferences': ['Online Course', 'Learning Platform']
    }

    recs1 = engine.get_recommendations(profile1, top_n=15, min_similarity=0.2)
    print("\n" + "-"*80)
    print("TOP RECOMMENDATIONS:")
    print("-"*80)
    print(recs1[['rank', 'name', 'category', 'stem_field', 'financial_barrier', 'similarity_score']].to_string(index=False))

    # Test profile 2: High school student interested in Biology research
    print("\n\n" + "="*80)
    print("TEST 2: 10th grader interested in Biology research with transportation")
    print("="*80)

    profile2 = {
        'financial_situation': 'Medium',
        'location': 'Hybrid',
        'transportation_available': True,
        'grade_level': 10,
        'academic_level': 'Advanced',
        'time_availability': 15,  # 15 hours/week
        'support_needed': 'Medium',
        'stem_interests': 'biology research genetics microbiology laboratory experiments science fair',
        'stem_fields': ['Biology', 'Health Sciences'],
        'format_preferences': ['Research Opportunity', 'Summer Program', 'Competition']
    }

    recs2 = engine.get_recommendations(profile2, top_n=15, min_similarity=0.2)
    print("\n" + "-"*80)
    print("TOP RECOMMENDATIONS:")
    print("-"*80)
    print(recs2[['rank', 'name', 'category', 'stem_field', 'financial_barrier', 'similarity_score']].to_string(index=False))

    print("\n\n[OK] Recommendation engine tests complete!")


if __name__ == '__main__':
    test_recommendation_engine()
