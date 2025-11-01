"""
BMIS ML Pipeline - Comprehensive Test Runner

Loads 45+ diverse test profiles and generates recommendations for systematic validation.
Saves individual results and aggregates metrics for analysis.
"""

import sys
import os
import json
import pandas as pd
from datetime import datetime
from pathlib import Path

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from recommendation_engine import BMISRecommendationEngine


class BMISTestRunner:
    """
    Comprehensive test runner for BMIS recommendation engine validation.
    """

    def __init__(self, test_profiles_dir='test_profiles', results_dir='results'):
        """
        Initialize test runner.

        Args:
            test_profiles_dir: Directory containing test profile JSON files
            results_dir: Directory to save results
        """
        # Save original directory
        self.original_dir = os.getcwd()

        # Change to bmis_ml_pipeline root directory for model loading
        self.project_root = Path(__file__).parent.parent
        os.chdir(self.project_root)

        self.test_profiles_dir = Path(__file__).parent / test_profiles_dir
        self.results_dir = self.project_root / results_dir
        self.individual_results_dir = self.results_dir / 'individual_results'

        # Create results directories
        self.results_dir.mkdir(exist_ok=True)
        self.individual_results_dir.mkdir(exist_ok=True)

        # Initialize recommendation engine
        print("[INFO] Loading recommendation engine...")
        self.engine = BMISRecommendationEngine()
        self.engine.load_all_models()
        print("[OK] Models loaded successfully\n")

        # Storage for all results
        self.all_results = []
        self.all_profiles = []

    def load_test_profiles(self):
        """
        Load all test profiles from JSON files.

        Returns:
            List of (category, profile_dict) tuples
        """
        profiles = []

        # Define profile categories
        categories = {
            'financial_diversity_profiles.json': 'Financial Diversity',
            'grade_diversity_profiles.json': 'Grade Diversity',
            'interest_diversity_profiles.json': 'Interest Diversity',
            'edge_case_profiles.json': 'Edge Cases'
        }

        for filename, category in categories.items():
            filepath = self.test_profiles_dir / filename

            if not filepath.exists():
                print(f"[WARNING] File not found: {filepath}")
                continue

            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)

            print(f"[OK] Loaded {len(data['profiles'])} profiles from {category}")

            for profile in data['profiles']:
                profiles.append({
                    'category': category,
                    'profile_id': profile['profile_id'],
                    'name': profile['name'],
                    'profile': profile
                })

        print(f"\n[OK] Total profiles loaded: {len(profiles)}\n")
        return profiles

    def run_single_test(self, profile_data):
        """
        Run recommendation engine on a single test profile.

        Args:
            profile_data: Dict containing category, profile_id, name, and profile

        Returns:
            Dict with test results
        """
        profile_id = profile_data['profile_id']
        name = profile_data['name']
        category = profile_data['category']
        profile = profile_data['profile']

        print(f"Testing {profile_id}: {name}")
        print(f"  Category: {category}")
        print(f"  Financial: {profile['financial_situation']}, Grade: {profile['grade_level']}, Academic: {profile['academic_level']}")

        # Extract student profile (excluding metadata)
        student_profile = {
            'financial_situation': profile['financial_situation'],
            'location': profile['location'],
            'transportation_available': profile['transportation_available'],
            'grade_level': profile['grade_level'],
            'academic_level': profile['academic_level'],
            'time_availability': profile['time_availability'],
            'support_needed': profile['support_needed'],
            'stem_interests': profile['stem_interests'],
            'stem_fields': profile['stem_fields'],
            'format_preferences': profile['format_preferences']
        }

        # Get recommendations
        try:
            recommendations = self.engine.get_recommendations(
                student_profile,
                top_n=20,
                min_similarity=0.2,
                top_clusters=5
            )

            num_recommendations = len(recommendations)
            print(f"  [OK] Generated {num_recommendations} recommendations\n")

            # Save individual result
            self.save_individual_result(profile_id, name, student_profile, recommendations)

            # Return result summary
            result = {
                'profile_id': profile_id,
                'name': name,
                'category': category,
                'financial_situation': profile['financial_situation'],
                'grade_level': profile['grade_level'],
                'academic_level': profile['academic_level'],
                'location': profile['location'],
                'stem_fields': ', '.join(profile['stem_fields']),
                'num_recommendations': num_recommendations,
                'success': num_recommendations >= 15,
                'recommendations_df': recommendations
            }

            return result

        except Exception as e:
            print(f"  [ERROR] Failed to generate recommendations: {e}\n")
            return {
                'profile_id': profile_id,
                'name': name,
                'category': category,
                'financial_situation': profile['financial_situation'],
                'grade_level': profile['grade_level'],
                'academic_level': profile['academic_level'],
                'location': profile['location'],
                'stem_fields': ', '.join(profile['stem_fields']),
                'num_recommendations': 0,
                'success': False,
                'error': str(e),
                'recommendations_df': pd.DataFrame()
            }

    def save_individual_result(self, profile_id, name, student_profile, recommendations):
        """
        Save individual test result to CSV file.

        Args:
            profile_id: Profile identifier
            name: Profile name
            student_profile: Student profile dict
            recommendations: Recommendations DataFrame
        """
        # Create result file
        filename = f"{profile_id}_results.csv"
        filepath = self.individual_results_dir / filename

        # Save recommendations
        if len(recommendations) > 0:
            recommendations.to_csv(filepath, index=False)
        else:
            # Save empty file with headers
            pd.DataFrame(columns=['rank', 'name', 'category', 'similarity_score']).to_csv(filepath, index=False)

        # Also save profile metadata
        metadata_file = self.individual_results_dir / f"{profile_id}_profile.json"
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump({
                'profile_id': profile_id,
                'name': name,
                'student_profile': student_profile,
                'num_recommendations': len(recommendations),
                'timestamp': datetime.now().isoformat()
            }, f, indent=2)

    def run_all_tests(self):
        """
        Run all test profiles and collect results.

        Returns:
            DataFrame with all test results
        """
        # Load all profiles
        self.all_profiles = self.load_test_profiles()

        print("="*80)
        print(f"Running {len(self.all_profiles)} test profiles...")
        print("="*80 + "\n")

        # Run each test
        for i, profile_data in enumerate(self.all_profiles, 1):
            print(f"[{i}/{len(self.all_profiles)}] ", end='')
            result = self.run_single_test(profile_data)
            self.all_results.append(result)

        # Create summary DataFrame
        summary_df = pd.DataFrame([{
            'profile_id': r['profile_id'],
            'name': r['name'],
            'category': r['category'],
            'financial_situation': r['financial_situation'],
            'grade_level': r['grade_level'],
            'academic_level': r['academic_level'],
            'location': r['location'],
            'stem_fields': r['stem_fields'],
            'num_recommendations': r['num_recommendations'],
            'success': r['success']
        } for r in self.all_results])

        # Save summary
        summary_file = self.results_dir / 'test_summary.csv'
        summary_df.to_csv(summary_file, index=False)
        print(f"\n[OK] Test summary saved to: {summary_file}")

        return summary_df

    def generate_quick_stats(self, summary_df):
        """
        Generate quick statistics from test results.

        Args:
            summary_df: DataFrame with test summary
        """
        print("\n" + "="*80)
        print("QUICK STATISTICS")
        print("="*80)

        total_tests = len(summary_df)
        successful_tests = summary_df['success'].sum()
        failed_tests = total_tests - successful_tests

        print(f"\nTotal Tests: {total_tests}")
        print(f"Successful (>=15 recs): {successful_tests} ({successful_tests/total_tests*100:.1f}%)")
        print(f"Failed (<15 recs): {failed_tests} ({failed_tests/total_tests*100:.1f}%)")

        print(f"\nRecommendations per Profile:")
        print(f"  Mean: {summary_df['num_recommendations'].mean():.1f}")
        print(f"  Median: {summary_df['num_recommendations'].median():.1f}")
        print(f"  Min: {summary_df['num_recommendations'].min()}")
        print(f"  Max: {summary_df['num_recommendations'].max()}")

        print(f"\nBreakdown by Category:")
        category_stats = summary_df.groupby('category').agg({
            'num_recommendations': ['count', 'mean', 'min', 'max'],
            'success': 'sum'
        }).round(1)
        print(category_stats)

        print(f"\nBreakdown by Financial Situation:")
        financial_stats = summary_df.groupby('financial_situation').agg({
            'num_recommendations': ['count', 'mean', 'min', 'max'],
            'success': 'sum'
        }).round(1)
        print(financial_stats)

        print(f"\nBreakdown by Grade Level:")
        grade_stats = summary_df.groupby('grade_level').agg({
            'num_recommendations': ['count', 'mean', 'min', 'max'],
            'success': 'sum'
        }).round(1)
        print(grade_stats)

        if failed_tests > 0:
            print(f"\n[WARNING] Failed Profiles (< 15 recommendations):")
            failed_profiles = summary_df[~summary_df['success']][['profile_id', 'name', 'num_recommendations']]
            print(failed_profiles.to_string(index=False))

        print("\n" + "="*80)


def main():
    """
    Main execution function.
    """
    print("="*80)
    print("BMIS ML Pipeline - Comprehensive Test Runner")
    print("="*80)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    # Initialize test runner
    runner = BMISTestRunner()

    # Run all tests
    summary_df = runner.run_all_tests()

    # Generate quick statistics
    runner.generate_quick_stats(summary_df)

    print(f"\nCompleted: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)
    print("\nNext steps:")
    print("1. Review individual results in: results/individual_results/")
    print("2. Run metrics_calculator.py for detailed analysis")
    print("3. Generate validation report")
    print("="*80)


if __name__ == '__main__':
    main()
