"""
BMIS Deployment Verification Script

Verifies that the system is ready for beta deployment by testing:
1. Model loading
2. Recommendation generation
3. Filtering functionality
4. Edge cases

Run before deploying to ensure everything works correctly.
"""

import sys
import os
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent / 'src'))

from recommendation_engine import BMISRecommendationEngine
import pandas as pd


class DeploymentVerifier:
    """Verifies system is ready for deployment"""

    def __init__(self):
        self.engine = None
        self.tests_passed = 0
        self.tests_failed = 0

    def print_header(self, text):
        """Print section header"""
        print("\n" + "="*70)
        print(text)
        print("="*70)

    def print_test(self, test_name, passed, details=""):
        """Print test result"""
        status = "[PASS]" if passed else "[FAIL]"
        print(f"{status} - {test_name}")
        if details:
            print(f"       {details}")

        if passed:
            self.tests_passed += 1
        else:
            self.tests_failed += 1

    def test_model_loading(self):
        """Test 1: Verify all models load correctly"""
        self.print_header("TEST 1: Model Loading")

        try:
            self.engine = BMISRecommendationEngine()
            self.engine.load_all_models()

            # Check models loaded
            models_loaded = all([
                self.engine.df is not None,
                len(self.engine.kmeans_models) == 4,
                len(self.engine.scalers) == 3,
                self.engine.tfidf_vectorizer is not None,
                self.engine.tfidf_matrix is not None
            ])

            self.print_test(
                "Load all models and data",
                models_loaded,
                f"Loaded {len(self.engine.df)} resources, 4 K-Means models, TF-IDF engine"
            )

            return models_loaded

        except Exception as e:
            self.print_test("Load all models and data", False, f"Error: {str(e)}")
            return False

    def test_basic_recommendation(self):
        """Test 2: Generate recommendations for typical profile"""
        self.print_header("TEST 2: Basic Recommendation Generation")

        test_profile = {
            'financial_situation': 'Medium',
            'location': 'Virtual',
            'transportation_available': True,
            'grade_level': 10,
            'academic_level': 'Intermediate',
            'time_availability': 10,
            'support_needed': 'Medium',
            'stem_interests': 'computer science programming python web development',
            'stem_fields': ['Computer Science', 'Software Engineering'],
            'format_preferences': ['Online Course', 'Learning Platform']
        }

        try:
            recommendations = self.engine.get_recommendations(
                test_profile,
                top_n=20,
                min_similarity=0.2
            )

            success = len(recommendations) >= 15
            self.print_test(
                "Generate recommendations for typical profile",
                success,
                f"Generated {len(recommendations)} recommendations (target: 15+)"
            )

            return success, recommendations

        except Exception as e:
            self.print_test(
                "Generate recommendations for typical profile",
                False,
                f"Error: {str(e)}"
            )
            return False, pd.DataFrame()

    def test_low_income_accessibility(self):
        """Test 3: Verify accessibility alignment for low-income students"""
        self.print_header("TEST 3: Accessibility Alignment")

        low_income_profile = {
            'financial_situation': 'Low',
            'location': 'Virtual',
            'transportation_available': False,
            'grade_level': 11,
            'academic_level': 'Intermediate',
            'time_availability': 10,
            'support_needed': 'High',
            'stem_interests': 'biology genetics research science',
            'stem_fields': ['Biology', 'Life Sciences'],
            'format_preferences': ['Research Opportunity', 'Online Course']
        }

        try:
            recommendations = self.engine.get_recommendations(
                low_income_profile,
                top_n=20,
                min_similarity=0.2
            )

            if len(recommendations) == 0:
                self.print_test(
                    "Low-income student accessibility",
                    False,
                    "No recommendations generated"
                )
                return False

            # Count Low/Free resources
            if 'financial_barrier' in recommendations.columns:
                low_free_count = recommendations['financial_barrier'].isin(['Low', 'Free']).sum()
                low_free_pct = (low_free_count / len(recommendations) * 100)

                success = low_free_pct >= 55  # Target: 60%, acceptable: 55%
                self.print_test(
                    "Low-income student accessibility",
                    success,
                    f"{low_free_pct:.1f}% Low/Free resources (target: 60%+, min: 55%)"
                )

                return success
            else:
                self.print_test(
                    "Low-income student accessibility",
                    False,
                    "financial_barrier column missing"
                )
                return False

        except Exception as e:
            self.print_test(
                "Low-income student accessibility",
                False,
                f"Error: {str(e)}"
            )
            return False

    def test_filtering(self, recommendations):
        """Test 4: Verify filtering works correctly"""
        self.print_header("TEST 4: Filtering Functionality")

        if len(recommendations) == 0:
            self.print_test(
                "Filter functionality",
                False,
                "No recommendations to filter"
            )
            return False

        try:
            # Test location filter
            if 'location_type' in recommendations.columns:
                virtual_count = recommendations['location_type'].str.contains('Virtual', case=False, na=False).sum()
                location_test = virtual_count > 0
                self.print_test(
                    "Location data present",
                    location_test,
                    f"{virtual_count} virtual resources found"
                )
            else:
                self.print_test("Location data present", False, "location_type column missing")
                location_test = False

            # Test grade filter
            if 'target_grade' in recommendations.columns:
                grade_count = recommendations['target_grade'].notna().sum()
                grade_test = grade_count > 0
                self.print_test(
                    "Grade data present",
                    grade_test,
                    f"{grade_count}/{len(recommendations)} recommendations have grade data"
                )
            else:
                self.print_test("Grade data present", False, "target_grade column missing")
                grade_test = False

            return location_test and grade_test

        except Exception as e:
            self.print_test(
                "Filter functionality",
                False,
                f"Error: {str(e)}"
            )
            return False

    def test_edge_cases(self):
        """Test 5: Verify edge cases don't crash"""
        self.print_header("TEST 5: Edge Case Handling")

        # Test 1: Very young student
        young_student = {
            'financial_situation': 'Low',
            'location': 'Virtual',
            'transportation_available': False,
            'grade_level': 6,
            'academic_level': 'Beginner',
            'time_availability': 5,
            'support_needed': 'High',
            'stem_interests': 'science animals nature experiments',
            'stem_fields': ['Biology', 'Life Sciences'],
            'format_preferences': ['Camp', 'Learning Platform']
        }

        try:
            recs = self.engine.get_recommendations(young_student, top_n=20)
            success = len(recs) > 0
            self.print_test(
                "6th grader edge case",
                success,
                f"Generated {len(recs)} recommendations (may be low for young students)"
            )
        except Exception as e:
            self.print_test("6th grader edge case", False, f"Error: {str(e)}")
            success = False

        # Test 2: Niche interest
        niche_interest = {
            'financial_situation': 'Medium',
            'location': 'Virtual',
            'transportation_available': True,
            'grade_level': 12,
            'academic_level': 'Advanced',
            'time_availability': 15,
            'support_needed': 'Low',
            'stem_interests': 'quantum computing quantum mechanics qubits',
            'stem_fields': ['Physics', 'Computer Science'],
            'format_preferences': ['Research Opportunity', 'Online Course']
        }

        try:
            recs = self.engine.get_recommendations(niche_interest, top_n=20)
            success2 = len(recs) >= 10  # Lower bar for niche interests
            self.print_test(
                "Niche interest (quantum computing)",
                success2,
                f"Generated {len(recs)} recommendations (target: 10+ for niche)"
            )
        except Exception as e:
            self.print_test("Niche interest (quantum computing)", False, f"Error: {str(e)}")
            success2 = False

        return success and success2

    def test_performance(self):
        """Test 6: Verify performance is acceptable"""
        self.print_header("TEST 6: Performance")

        import time

        test_profile = {
            'financial_situation': 'Medium',
            'location': 'Virtual',
            'transportation_available': True,
            'grade_level': 10,
            'academic_level': 'Intermediate',
            'time_availability': 10,
            'support_needed': 'Medium',
            'stem_interests': 'engineering robotics design',
            'stem_fields': ['Engineering', 'Robotics'],
            'format_preferences': ['Summer Program', 'Competition']
        }

        try:
            start_time = time.time()
            recommendations = self.engine.get_recommendations(test_profile, top_n=20)
            elapsed_time = time.time() - start_time

            success = elapsed_time < 2.0  # Target: <0.5s, acceptable: <2s
            self.print_test(
                "Recommendation generation speed",
                success,
                f"{elapsed_time:.2f}s (target: <0.5s, max: 2s)"
            )

            return success

        except Exception as e:
            self.print_test(
                "Recommendation generation speed",
                False,
                f"Error: {str(e)}"
            )
            return False

    def run_all_tests(self):
        """Run all verification tests"""
        print("\n" + "="*70)
        print("BMIS DEPLOYMENT VERIFICATION")
        print("="*70)
        print("\nVerifying system is ready for beta deployment...")

        # Run tests
        models_ok = self.test_model_loading()
        if not models_ok:
            print("\n❌ CRITICAL: Cannot proceed without models. Fix model loading first.")
            return False

        basic_ok, recommendations = self.test_basic_recommendation()
        accessibility_ok = self.test_low_income_accessibility()
        filtering_ok = self.test_filtering(recommendations)
        edge_cases_ok = self.test_edge_cases()
        performance_ok = self.test_performance()

        # Summary
        self.print_header("VERIFICATION SUMMARY")

        total_tests = self.tests_passed + self.tests_failed
        print(f"\nTests Passed: {self.tests_passed}/{total_tests}")
        print(f"Tests Failed: {self.tests_failed}/{total_tests}")
        print(f"Success Rate: {self.tests_passed/total_tests*100:.1f}%")

        # Decision
        critical_tests = [models_ok, basic_ok, accessibility_ok]
        all_critical_pass = all(critical_tests)

        print("\n" + "="*70)
        if all_critical_pass and self.tests_passed >= 10:
            print("[SUCCESS] DEPLOYMENT READY")
            print("="*70)
            print("\nSystem is ready for beta deployment.")
            print("\nNext steps:")
            print("1. Run: streamlit run app.py")
            print("2. Test in browser")
            print("3. Deploy to Streamlit Cloud")
            print("4. Share with beta users")
            return True
        elif all_critical_pass:
            print("[WARNING] DEPLOYMENT READY (WITH WARNINGS)")
            print("="*70)
            print("\nCore functionality works but some tests failed.")
            print("Review failed tests and decide if they're blockers.")
            return True
        else:
            print("[ERROR] NOT READY FOR DEPLOYMENT")
            print("="*70)
            print("\nCritical tests failed. Fix issues before deploying.")
            print("\nFailed critical tests:")
            if not models_ok:
                print("  - Model loading")
            if not basic_ok:
                print("  - Basic recommendation generation")
            if not accessibility_ok:
                print("  - Accessibility alignment")
            return False


def main():
    """Run verification"""
    verifier = DeploymentVerifier()
    success = verifier.run_all_tests()

    # Exit code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
