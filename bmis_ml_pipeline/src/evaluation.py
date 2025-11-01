"""
Evaluation Module for BMIS ML Pipeline

Evaluates:
1. Clustering quality metrics
2. Recommendation diversity and coverage
3. Sample test cases with manual validation
"""

import numpy as np
import pandas as pd
import json
from collections import Counter
import joblib


class BMISEvaluator:
    """Comprehensive evaluation of BMIS ML pipeline"""

    def __init__(self, models_dir='models', data_path='data/bmis_final_ml_ready_dataset_cs_refined.csv'):
        self.models_dir = models_dir
        self.data_path = data_path
        self.df = None
        self.cluster_assignments = {}

    def load_data(self):
        """Load data and cluster assignments"""
        self.df = pd.read_csv(self.data_path)

        # Load cluster assignments
        for model_name in ['accessibility', 'academic', 'stem_field', 'format']:
            try:
                clusters = pd.read_csv(f'{self.models_dir}/{model_name}_clusters.csv', index_col=0)
                self.cluster_assignments[model_name] = clusters.iloc[:, 0]
            except Exception as e:
                print(f"[WARNING] Could not load {model_name} clusters: {e}")

        print(f"[OK] Loaded {len(self.df)} resources and cluster assignments")
        return self

    def evaluate_clustering_quality(self):
        """Evaluate clustering quality across all models"""
        print("\n" + "="*80)
        print("CLUSTERING QUALITY EVALUATION")
        print("="*80)

        # Load metrics from JSON
        try:
            with open(f'{self.models_dir}/cluster_metrics.json', 'r') as f:
                metrics = json.load(f)

            for model_name, model_metrics in metrics.items():
                print(f"\n{model_name.upper()} MODEL:")
                print("-" * 60)
                print(f"  Number of Clusters: {model_metrics['n_clusters']}")
                print(f"  Silhouette Score: {model_metrics['silhouette']:.3f}")
                print(f"  Davies-Bouldin Index: {model_metrics['davies_bouldin']:.3f}")
                print(f"  Inertia: {model_metrics['inertia']:.2f}")

                # Check quality thresholds
                sil_score = model_metrics['silhouette']
                if sil_score >= 0.5:
                    quality = "EXCELLENT"
                elif sil_score >= 0.3:
                    quality = "GOOD"
                else:
                    quality = "ACCEPTABLE"

                print(f"  Quality Assessment: {quality}")

        except Exception as e:
            print(f"[ERROR] Could not load metrics: {e}")

        return self

    def evaluate_cluster_sizes(self):
        """Check cluster size distribution"""
        print("\n" + "="*80)
        print("CLUSTER SIZE DISTRIBUTION")
        print("="*80)

        for model_name, assignments in self.cluster_assignments.items():
            print(f"\n{model_name.upper()}:")
            print("-" * 60)

            cluster_sizes = assignments.value_counts().sort_index()

            min_size = cluster_sizes.min()
            max_size = cluster_sizes.max()
            mean_size = cluster_sizes.mean()

            print(f"  Min cluster size: {min_size}")
            print(f"  Max cluster size: {max_size}")
            print(f"  Mean cluster size: {mean_size:.1f}")

            # Check for problematic clusters
            small_clusters = cluster_sizes[cluster_sizes < 20]
            large_clusters = cluster_sizes[cluster_sizes > 400]

            if len(small_clusters) > 0:
                print(f"  [WARNING] {len(small_clusters)} clusters with < 20 resources")

            if len(large_clusters) > 0:
                print(f"  [WARNING] {len(large_clusters)} clusters with > 400 resources")

            if len(small_clusters) == 0 and len(large_clusters) == 0:
                print(f"  [OK] All clusters within acceptable size range")

        return self

    def evaluate_recommendation_diversity(self, recommendation_engine, test_profiles):
        """
        Evaluate diversity of recommendations across test profiles

        Args:
            recommendation_engine: Loaded BMISRecommendationEngine
            test_profiles: List of student profile dicts
        """
        print("\n" + "="*80)
        print("RECOMMENDATION DIVERSITY EVALUATION")
        print("="*80)

        all_recommendations = []
        cluster_distributions = []

        for i, profile in enumerate(test_profiles, 1):
            print(f"\nTest Profile {i}:")
            recs = recommendation_engine.get_recommendations(profile, top_n=20, min_similarity=0.2)

            if len(recs) == 0:
                print("[WARNING] No recommendations generated")
                continue

            # Analyze diversity
            categories = recs['category'].value_counts()
            stem_fields = recs['stem_field'].value_counts()

            print(f"  Total recommendations: {len(recs)}")
            print(f"  Unique categories: {len(categories)}")
            print(f"  Unique STEM fields: {len(stem_fields)}")

            # Store for coverage analysis
            all_recommendations.extend(recs.index.tolist() if hasattr(recs, 'index') else [])

            # Check diversity threshold (>= 3 categories and >= 3 STEM fields)
            if len(categories) >= 3 and len(stem_fields) >= 3:
                print(f"  [OK] Good diversity (>= 3 categories and STEM fields)")
            else:
                print(f"  [WARNING] Low diversity")

        # Overall coverage
        unique_recommended = len(set(all_recommendations))
        coverage_pct = 100 * unique_recommended / len(self.df)

        print(f"\nOVERALL COVERAGE:")
        print(f"  Unique resources recommended: {unique_recommended}/{len(self.df)} ({coverage_pct:.1f}%)")

        return self

    def evaluate_accessibility_alignment(self, recommendation_engine, test_profiles):
        """
        Evaluate if recommendations match student accessibility constraints

        Args:
            recommendation_engine: Loaded BMISRecommendationEngine
            test_profiles: List of student profile dicts with expected accessibility
        """
        print("\n" + "="*80)
        print("ACCESSIBILITY ALIGNMENT EVALUATION")
        print("="*80)

        for i, profile in enumerate(test_profiles, 1):
            print(f"\nTest Profile {i}:")
            print(f"  Financial Situation: {profile.get('financial_situation', 'N/A')}")
            print(f"  Location Preference: {profile.get('location', 'N/A')}")

            recs = recommendation_engine.get_recommendations(profile, top_n=20, min_similarity=0.2)

            if len(recs) == 0:
                continue

            # Check financial alignment
            financial_situation = profile.get('financial_situation', 'Medium')
            if financial_situation == 'Low':
                # Should prioritize Low/Free resources
                low_barrier = recs[recs['financial_barrier'].isin(['Low', 'Free'])].shape[0]
                pct = 100 * low_barrier / len(recs)
                print(f"  Low/Free barrier resources: {low_barrier}/{len(recs)} ({pct:.0f}%)")

                if pct >= 50:
                    print(f"  [OK] Good alignment with low-income student")
                else:
                    print(f"  [WARNING] Poor alignment - should prioritize low-cost resources")

            # Check location alignment
            location_pref = profile.get('location', 'Virtual')
            matching_location = recs[recs['location_type'].str.contains(location_pref, case=False, na=False)].shape[0]
            pct = 100 * matching_location / len(recs)
            print(f"  Matching location type: {matching_location}/{len(recs)} ({pct:.0f}%)")

        return self

    def evaluate_academic_appropriateness(self, recommendation_engine, test_profiles):
        """
        Evaluate if recommendations match student academic level

        Args:
            recommendation_engine: Loaded BMISRecommendationEngine
            test_profiles: List of student profile dicts with academic info
        """
        print("\n" + "="*80)
        print("ACADEMIC APPROPRIATENESS EVALUATION")
        print("="*80)

        for i, profile in enumerate(test_profiles, 1):
            print(f"\nTest Profile {i}:")
            print(f"  Grade Level: {profile.get('grade_level', 'N/A')}")
            print(f"  Academic Level: {profile.get('academic_level', 'N/A')}")

            recs = recommendation_engine.get_recommendations(profile, top_n=20, min_similarity=0.2)

            if len(recs) == 0:
                continue

            # Parse target grades (this is simplified - would need better parsing in production)
            student_grade = profile.get('grade_level', 9)

            # Count resources that match grade level (within ±2 years)
            # This is a simplified check
            print(f"  Recommendations generated: {len(recs)}")
            print(f"  [INFO] Grade-level matching requires more sophisticated parsing")

        return self

    def generate_evaluation_report(self, output_dir='outputs'):
        """Generate comprehensive evaluation report"""
        import os
        os.makedirs(output_dir, exist_ok=True)

        report_lines = []
        report_lines.append("="*80)
        report_lines.append("BMIS ML PIPELINE EVALUATION REPORT")
        report_lines.append("="*80)
        report_lines.append("")

        # Load clustering metrics
        try:
            with open(f'{self.models_dir}/cluster_metrics.json', 'r') as f:
                metrics = json.load(f)

            report_lines.append("CLUSTERING QUALITY METRICS")
            report_lines.append("-"*80)

            for model_name, model_metrics in metrics.items():
                report_lines.append(f"\n{model_name.upper()}:")
                report_lines.append(f"  Clusters: {model_metrics['n_clusters']}")
                report_lines.append(f"  Silhouette: {model_metrics['silhouette']:.3f}")
                report_lines.append(f"  Davies-Bouldin: {model_metrics['davies_bouldin']:.3f}")

            report_lines.append("")

        except Exception as e:
            report_lines.append(f"[ERROR] Could not load metrics: {e}")

        # Cluster sizes
        report_lines.append("\nCLUSTER SIZE DISTRIBUTION")
        report_lines.append("-"*80)

        for model_name, assignments in self.cluster_assignments.items():
            cluster_sizes = assignments.value_counts()
            report_lines.append(f"\n{model_name.upper()}:")
            report_lines.append(f"  Min: {cluster_sizes.min()}")
            report_lines.append(f"  Max: {cluster_sizes.max()}")
            report_lines.append(f"  Mean: {cluster_sizes.mean():.1f}")

        # Save report
        report_text = "\n".join(report_lines)
        with open(f'{output_dir}/evaluation_report.txt', 'w') as f:
            f.write(report_text)

        print(f"\n[OK] Generated evaluation report at {output_dir}/evaluation_report.txt")
        return report_text


def run_full_evaluation():
    """Run comprehensive evaluation of BMIS ML pipeline"""
    print("="*80)
    print("BMIS ML PIPELINE COMPREHENSIVE EVALUATION")
    print("="*80)

    # Initialize evaluator
    evaluator = BMISEvaluator()
    evaluator.load_data()

    # Run evaluations
    evaluator.evaluate_clustering_quality()
    evaluator.evaluate_cluster_sizes()

    # Load recommendation engine for diversity tests
    from recommendation_engine import BMISRecommendationEngine

    engine = BMISRecommendationEngine()
    engine.load_all_models()

    # Define test profiles
    test_profiles = [
        # Profile 1: Low-income interested in AI/ML
        {
            'financial_situation': 'Low',
            'location': 'Virtual',
            'transportation_available': False,
            'grade_level': 11,
            'academic_level': 'Intermediate',
            'time_availability': 10,
            'support_needed': 'High',
            'stem_interests': 'machine learning artificial intelligence programming',
            'stem_fields': ['Artificial Intelligence/Machine Learning', 'Computer Science'],
            'format_preferences': ['Online Course', 'Learning Platform']
        },
        # Profile 2: Medium-income interested in Biology
        {
            'financial_situation': 'Medium',
            'location': 'Hybrid',
            'transportation_available': True,
            'grade_level': 10,
            'academic_level': 'Advanced',
            'time_availability': 15,
            'support_needed': 'Medium',
            'stem_interests': 'biology research genetics microbiology',
            'stem_fields': ['Biology'],
            'format_preferences': ['Research Opportunity', 'Summer Program']
        },
        # Profile 3: High-income interested in Engineering
        {
            'financial_situation': 'High',
            'location': 'In-person',
            'transportation_available': True,
            'grade_level': 12,
            'academic_level': 'Advanced',
            'time_availability': 20,
            'support_needed': 'Low',
            'stem_interests': 'robotics mechanical engineering design competitions',
            'stem_fields': ['Engineering', 'Robotics'],
            'format_preferences': ['Competition', 'Camp']
        }
    ]

    # Run recommendation-based evaluations
    evaluator.evaluate_recommendation_diversity(engine, test_profiles)
    evaluator.evaluate_accessibility_alignment(engine, test_profiles)
    evaluator.evaluate_academic_appropriateness(engine, test_profiles)

    # Generate report
    evaluator.generate_evaluation_report()

    print("\n" + "="*80)
    print("[OK] Evaluation Complete!")
    print("="*80)


if __name__ == '__main__':
    run_full_evaluation()
