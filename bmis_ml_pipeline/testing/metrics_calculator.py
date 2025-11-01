"""
BMIS ML Pipeline - Metrics Calculator

Analyzes test results and calculates detailed quality metrics:
- Accessibility alignment (Low/Free % for low-income students)
- STEM field diversity
- Category diversity
- Location alignment
- Academic appropriateness
- Database coverage
"""

import sys
import os
import json
import pandas as pd
import numpy as np
from pathlib import Path
from collections import Counter

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))


class BMISMetricsCalculator:
    """
    Calculates comprehensive quality metrics for BMIS recommendation validation.
    """

    def __init__(self, results_dir='../results'):
        """
        Initialize metrics calculator.

        Args:
            results_dir: Directory containing test results
        """
        self.results_dir = Path(__file__).parent.parent / 'results'
        self.individual_results_dir = self.results_dir / 'individual_results'
        self.analysis_dir = Path(__file__).parent / 'analysis'

        # Create analysis directory
        self.analysis_dir.mkdir(exist_ok=True)

        # Load test summary
        self.summary_df = pd.read_csv(self.results_dir / 'test_summary.csv')

        # Load all individual results
        self.individual_results = self.load_individual_results()

    def load_individual_results(self):
        """
        Load all individual result files.

        Returns:
            Dict mapping profile_id to (profile_metadata, recommendations_df)
        """
        results = {}

        for csv_file in self.individual_results_dir.glob('*_results.csv'):
            profile_id = csv_file.stem.replace('_results', '')

            # Load recommendations
            recommendations = pd.read_csv(csv_file)

            # Load profile metadata
            metadata_file = self.individual_results_dir / f"{profile_id}_profile.json"
            if metadata_file.exists():
                with open(metadata_file, 'r', encoding='utf-8') as f:
                    metadata = json.load(f)
            else:
                metadata = {}

            results[profile_id] = {
                'metadata': metadata,
                'recommendations': recommendations
            }

        print(f"[OK] Loaded {len(results)} individual result files\n")
        return results

    def calculate_accessibility_alignment(self):
        """
        Calculate accessibility alignment: % Low/Free resources for low-income students.

        Returns:
            Dict with alignment metrics
        """
        print("="*80)
        print("ACCESSIBILITY ALIGNMENT ANALYSIS")
        print("="*80 + "\n")

        low_income_profiles = self.summary_df[self.summary_df['financial_situation'] == 'Low']

        results = []

        for _, row in low_income_profiles.iterrows():
            profile_id = row['profile_id']
            profile_name = row['name']

            if profile_id not in self.individual_results:
                continue

            recommendations = self.individual_results[profile_id]['recommendations']

            if len(recommendations) == 0:
                results.append({
                    'profile_id': profile_id,
                    'name': profile_name,
                    'total_recs': 0,
                    'low_free_count': 0,
                    'low_free_pct': 0.0,
                    'medium_count': 0,
                    'high_count': 0
                })
                continue

            # Count by financial barrier
            if 'financial_barrier' in recommendations.columns:
                barrier_counts = recommendations['financial_barrier'].value_counts()

                low_free = barrier_counts.get('Low', 0) + barrier_counts.get('Free', 0)
                medium = barrier_counts.get('Medium', 0) + barrier_counts.get('Moderate', 0)
                high = barrier_counts.get('High', 0) + barrier_counts.get('Prohibitive', 0)

                total = len(recommendations)
                low_free_pct = (low_free / total * 100) if total > 0 else 0.0

                results.append({
                    'profile_id': profile_id,
                    'name': profile_name,
                    'total_recs': total,
                    'low_free_count': low_free,
                    'low_free_pct': low_free_pct,
                    'medium_count': medium,
                    'high_count': high
                })

        # Create DataFrame
        alignment_df = pd.DataFrame(results)

        if len(alignment_df) > 0:
            # Calculate aggregate metrics
            avg_low_free_pct = alignment_df['low_free_pct'].mean()
            median_low_free_pct = alignment_df['low_free_pct'].median()

            print(f"Low-Income Profiles Analyzed: {len(alignment_df)}")
            print(f"\nAggregate Metrics:")
            print(f"  Average Low/Free %: {avg_low_free_pct:.1f}%")
            print(f"  Median Low/Free %: {median_low_free_pct:.1f}%")
            print(f"  Min Low/Free %: {alignment_df['low_free_pct'].min():.1f}%")
            print(f"  Max Low/Free %: {alignment_df['low_free_pct'].max():.1f}%")

            # Target: 60%+
            target = 60.0
            meeting_target = (alignment_df['low_free_pct'] >= target).sum()
            print(f"\nProfiles Meeting Target (>=60%): {meeting_target}/{len(alignment_df)} ({meeting_target/len(alignment_df)*100:.1f}%)")

            # Show distribution
            print(f"\nDetailed Results:")
            print(alignment_df[['profile_id', 'name', 'total_recs', 'low_free_count', 'low_free_pct']].to_string(index=False))

            # Save results
            alignment_df.to_csv(self.analysis_dir / 'accessibility_alignment.csv', index=False)
            print(f"\n[OK] Saved to: {self.analysis_dir / 'accessibility_alignment.csv'}")

        print("\n")
        return alignment_df

    def calculate_stem_field_diversity(self):
        """
        Calculate STEM field diversity: Average number of unique STEM fields per profile.

        Returns:
            Dict with diversity metrics
        """
        print("="*80)
        print("STEM FIELD DIVERSITY ANALYSIS")
        print("="*80 + "\n")

        results = []

        for profile_id, data in self.individual_results.items():
            recommendations = data['recommendations']

            if len(recommendations) == 0 or 'stem_field' not in recommendations.columns:
                results.append({
                    'profile_id': profile_id,
                    'total_recs': 0,
                    'unique_stem_fields': 0,
                    'stem_fields': ''
                })
                continue

            unique_fields = recommendations['stem_field'].nunique()
            field_list = ', '.join(recommendations['stem_field'].value_counts().head(5).index.tolist())

            results.append({
                'profile_id': profile_id,
                'total_recs': len(recommendations),
                'unique_stem_fields': unique_fields,
                'stem_fields': field_list
            })

        # Create DataFrame
        diversity_df = pd.DataFrame(results)
        diversity_df = diversity_df[diversity_df['total_recs'] > 0]  # Filter out empty results

        if len(diversity_df) > 0:
            # Calculate aggregate metrics
            avg_diversity = diversity_df['unique_stem_fields'].mean()
            median_diversity = diversity_df['unique_stem_fields'].median()

            print(f"Profiles Analyzed: {len(diversity_df)}")
            print(f"\nAggregate Metrics:")
            print(f"  Average Unique STEM Fields: {avg_diversity:.2f}")
            print(f"  Median Unique STEM Fields: {median_diversity:.1f}")
            print(f"  Min: {diversity_df['unique_stem_fields'].min()}")
            print(f"  Max: {diversity_df['unique_stem_fields'].max()}")

            # Target: 2.5+ fields
            target = 2.5
            meeting_target = (diversity_df['unique_stem_fields'] >= target).sum()
            print(f"\nProfiles Meeting Target (>=2.5 fields): {meeting_target}/{len(diversity_df)} ({meeting_target/len(diversity_df)*100:.1f}%)")

            # Show distribution
            print(f"\nDistribution:")
            distribution = diversity_df['unique_stem_fields'].value_counts().sort_index()
            for fields, count in distribution.items():
                print(f"  {int(fields)} fields: {count} profiles ({count/len(diversity_df)*100:.1f}%)")

            # Save results
            diversity_df.to_csv(self.analysis_dir / 'stem_field_diversity.csv', index=False)
            print(f"\n[OK] Saved to: {self.analysis_dir / 'stem_field_diversity.csv'}")

        print("\n")
        return diversity_df

    def calculate_category_diversity(self):
        """
        Calculate category diversity: Average number of unique categories per profile.

        Returns:
            Dict with diversity metrics
        """
        print("="*80)
        print("CATEGORY DIVERSITY ANALYSIS")
        print("="*80 + "\n")

        results = []

        for profile_id, data in self.individual_results.items():
            recommendations = data['recommendations']

            if len(recommendations) == 0 or 'category' not in recommendations.columns:
                results.append({
                    'profile_id': profile_id,
                    'total_recs': 0,
                    'unique_categories': 0,
                    'categories': ''
                })
                continue

            unique_cats = recommendations['category'].nunique()
            cat_list = ', '.join(recommendations['category'].value_counts().head(5).index.tolist())

            results.append({
                'profile_id': profile_id,
                'total_recs': len(recommendations),
                'unique_categories': unique_cats,
                'categories': cat_list
            })

        # Create DataFrame
        category_df = pd.DataFrame(results)
        category_df = category_df[category_df['total_recs'] > 0]  # Filter out empty results

        if len(category_df) > 0:
            # Calculate aggregate metrics
            avg_diversity = category_df['unique_categories'].mean()
            median_diversity = category_df['unique_categories'].median()

            print(f"Profiles Analyzed: {len(category_df)}")
            print(f"\nAggregate Metrics:")
            print(f"  Average Unique Categories: {avg_diversity:.2f}")
            print(f"  Median Unique Categories: {median_diversity:.1f}")
            print(f"  Min: {category_df['unique_categories'].min()}")
            print(f"  Max: {category_df['unique_categories'].max()}")

            # Target: 5+ categories
            target = 5
            meeting_target = (category_df['unique_categories'] >= target).sum()
            print(f"\nProfiles Meeting Target (>=5 categories): {meeting_target}/{len(category_df)} ({meeting_target/len(category_df)*100:.1f}%)")

            # Save results
            category_df.to_csv(self.analysis_dir / 'category_diversity.csv', index=False)
            print(f"\n[OK] Saved to: {self.analysis_dir / 'category_diversity.csv'}")

        print("\n")
        return category_df

    def calculate_location_alignment(self):
        """
        Calculate location alignment: % recommendations matching location preference.

        Returns:
            Dict with alignment metrics
        """
        print("="*80)
        print("LOCATION ALIGNMENT ANALYSIS")
        print("="*80 + "\n")

        results = []

        for profile_id, data in self.individual_results.items():
            recommendations = data['recommendations']
            metadata = data['metadata']

            if len(recommendations) == 0 or 'location_type' not in recommendations.columns:
                continue

            profile = metadata.get('student_profile', {})
            preferred_location = profile.get('location', 'Unknown')

            if preferred_location == 'Unknown':
                continue

            # Count matches
            total = len(recommendations)
            if preferred_location == 'Virtual':
                matches = (recommendations['location_type'] == 'Virtual').sum()
            elif preferred_location == 'In-person':
                matches = (recommendations['location_type'] == 'In-person').sum()
            elif preferred_location == 'Hybrid':
                # Hybrid accepts all
                matches = total
            else:
                matches = 0

            match_pct = (matches / total * 100) if total > 0 else 0.0

            results.append({
                'profile_id': profile_id,
                'preferred_location': preferred_location,
                'total_recs': total,
                'matches': matches,
                'match_pct': match_pct
            })

        # Create DataFrame
        location_df = pd.DataFrame(results)

        if len(location_df) > 0:
            # Analyze by location preference
            for location in ['Virtual', 'In-person', 'Hybrid']:
                subset = location_df[location_df['preferred_location'] == location]
                if len(subset) > 0:
                    avg_match = subset['match_pct'].mean()
                    print(f"{location} Preference ({len(subset)} profiles): {avg_match:.1f}% average match")

            # Overall average (excluding Hybrid which is 100% by definition)
            non_hybrid = location_df[location_df['preferred_location'] != 'Hybrid']
            if len(non_hybrid) > 0:
                overall_avg = non_hybrid['match_pct'].mean()
                print(f"\nOverall Average (Virtual & In-person only): {overall_avg:.1f}%")

                # Target: 70%
                target = 70.0
                meeting_target = (non_hybrid['match_pct'] >= target).sum()
                print(f"Profiles Meeting Target (>=70%): {meeting_target}/{len(non_hybrid)} ({meeting_target/len(non_hybrid)*100:.1f}%)")

            # Save results
            location_df.to_csv(self.analysis_dir / 'location_alignment.csv', index=False)
            print(f"\n[OK] Saved to: {self.analysis_dir / 'location_alignment.csv'}")

        print("\n")
        return location_df

    def calculate_academic_appropriateness(self):
        """
        Calculate academic appropriateness: % recommendations within ±2 grade levels.

        Returns:
            Dict with appropriateness metrics
        """
        print("="*80)
        print("ACADEMIC APPROPRIATENESS ANALYSIS")
        print("="*80 + "\n")

        results = []

        for profile_id, data in self.individual_results.items():
            recommendations = data['recommendations']
            metadata = data['metadata']

            if len(recommendations) == 0 or 'target_grade' not in recommendations.columns:
                continue

            profile = metadata.get('student_profile', {})
            student_grade = profile.get('grade_level', None)

            if student_grade is None:
                continue

            # Count recommendations within ±2 grades
            total = len(recommendations)
            within_range = 0

            for _, rec in recommendations.iterrows():
                target_grade_str = str(rec['target_grade'])

                # Parse target grade (may be range like "9-12")
                if '-' in target_grade_str:
                    parts = target_grade_str.split('-')
                    try:
                        min_grade = int(parts[0])
                        max_grade = int(parts[1])
                        if min_grade <= student_grade <= max_grade:
                            within_range += 1
                    except:
                        pass
                else:
                    try:
                        target_grade = int(target_grade_str)
                        if abs(target_grade - student_grade) <= 2:
                            within_range += 1
                    except:
                        pass

            appropriate_pct = (within_range / total * 100) if total > 0 else 0.0

            results.append({
                'profile_id': profile_id,
                'student_grade': student_grade,
                'total_recs': total,
                'appropriate': within_range,
                'appropriate_pct': appropriate_pct
            })

        # Create DataFrame
        academic_df = pd.DataFrame(results)

        if len(academic_df) > 0:
            # Calculate aggregate metrics
            avg_appropriate = academic_df['appropriate_pct'].mean()
            median_appropriate = academic_df['appropriate_pct'].median()

            print(f"Profiles Analyzed: {len(academic_df)}")
            print(f"\nAggregate Metrics:")
            print(f"  Average Appropriate %: {avg_appropriate:.1f}%")
            print(f"  Median Appropriate %: {median_appropriate:.1f}%")
            print(f"  Min: {academic_df['appropriate_pct'].min():.1f}%")
            print(f"  Max: {academic_df['appropriate_pct'].max():.1f}%")

            # Target: 80%
            target = 80.0
            meeting_target = (academic_df['appropriate_pct'] >= target).sum()
            print(f"\nProfiles Meeting Target (>=80%): {meeting_target}/{len(academic_df)} ({meeting_target/len(academic_df)*100:.1f}%)")

            # Save results
            academic_df.to_csv(self.analysis_dir / 'academic_appropriateness.csv', index=False)
            print(f"\n[OK] Saved to: {self.analysis_dir / 'academic_appropriateness.csv'}")

        print("\n")
        return academic_df

    def calculate_coverage(self):
        """
        Calculate database coverage: % of total resources recommended.

        Returns:
            Dict with coverage metrics
        """
        print("="*80)
        print("DATABASE COVERAGE ANALYSIS")
        print("="*80 + "\n")

        # Collect all unique resource names
        all_recommended_resources = set()

        for profile_id, data in self.individual_results.items():
            recommendations = data['recommendations']

            if len(recommendations) > 0 and 'name' in recommendations.columns:
                all_recommended_resources.update(recommendations['name'].unique())

        # Total resources in database (2,237 as per README)
        total_resources = 2237
        unique_recommended = len(all_recommended_resources)
        coverage_pct = (unique_recommended / total_resources * 100)

        print(f"Total Resources in Database: {total_resources}")
        print(f"Unique Resources Recommended: {unique_recommended}")
        print(f"Coverage: {coverage_pct:.1f}%")

        # Target: 10-20%
        if 10 <= coverage_pct <= 20:
            print(f"[OK] Coverage within target range (10-20%)")
        elif coverage_pct < 10:
            print(f"[WARNING] Coverage below target (<10%)")
        else:
            print(f"[INFO] Coverage above target (>20%) - Good!")

        # Save results
        with open(self.analysis_dir / 'coverage_analysis.txt', 'w') as f:
            f.write(f"Database Coverage Analysis\n")
            f.write(f"="*80 + "\n\n")
            f.write(f"Total Resources in Database: {total_resources}\n")
            f.write(f"Unique Resources Recommended: {unique_recommended}\n")
            f.write(f"Coverage: {coverage_pct:.2f}%\n")

        print(f"\n[OK] Saved to: {self.analysis_dir / 'coverage_analysis.txt'}\n")

        return {
            'total_resources': total_resources,
            'unique_recommended': unique_recommended,
            'coverage_pct': coverage_pct
        }

    def run_all_metrics(self):
        """
        Run all metric calculations.

        Returns:
            Dict with all metrics
        """
        print("="*80)
        print("BMIS ML Pipeline - Comprehensive Metrics Calculation")
        print("="*80 + "\n")

        metrics = {}

        # Run each metric calculation
        metrics['accessibility'] = self.calculate_accessibility_alignment()
        metrics['stem_diversity'] = self.calculate_stem_field_diversity()
        metrics['category_diversity'] = self.calculate_category_diversity()
        metrics['location'] = self.calculate_location_alignment()
        metrics['academic'] = self.calculate_academic_appropriateness()
        metrics['coverage'] = self.calculate_coverage()

        print("="*80)
        print("METRICS CALCULATION COMPLETE")
        print("="*80)
        print(f"\nAll metric files saved to: {self.analysis_dir}")
        print("\nNext steps:")
        print("1. Review metric files in testing/analysis/")
        print("2. Generate validation report")
        print("3. Make go/no-go decision for production")
        print("="*80 + "\n")

        return metrics


def main():
    """
    Main execution function.
    """
    calculator = BMISMetricsCalculator()
    metrics = calculator.run_all_metrics()


if __name__ == '__main__':
    main()
