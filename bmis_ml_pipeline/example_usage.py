"""
BMIS ML Pipeline - Quick Start Example

This script demonstrates how to use the recommendation engine
with different student profiles.
"""

import sys
sys.path.append('src')

from recommendation_engine import BMISRecommendationEngine
import pandas as pd

# Set display options for better readability
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)
pd.set_option('display.max_colwidth', 50)


def main():
    print("="*80)
    print("BMIS Recommendation Engine - Quick Start Example")
    print("="*80)

    # Load the recommendation engine
    print("\n1. Loading trained models...")
    engine = BMISRecommendationEngine()
    engine.load_all_models()

    print("\n" + "="*80)
    print("Example 1: Low-income 11th grader interested in Computer Science")
    print("="*80)

    # Define student profile
    student_profile_1 = {
        'financial_situation': 'Low',  # Limited budget
        'location': 'Virtual',  # Prefers online learning
        'transportation_available': False,  # No transportation
        'grade_level': 11,  # Junior in high school
        'academic_level': 'Intermediate',  # Some coding experience
        'time_availability': 8,  # 8 hours per week
        'support_needed': 'High',  # Needs mentorship
        'stem_interests': 'programming web development coding websites apps',
        'stem_fields': ['Software Engineering', 'Web Development', 'Computer Science'],
        'format_preferences': ['Online Course', 'Learning Platform', 'Workshop/Training']
    }

    # Get recommendations
    recommendations = engine.get_recommendations(
        student_profile_1,
        top_n=10,
        min_similarity=0.15  # Lower threshold for more results
    )

    # Display results
    if len(recommendations) > 0:
        print("\nTop 10 Recommendations:")
        print("-" * 80)
        print(recommendations[['rank', 'name', 'category', 'financial_barrier', 'similarity_score']].to_string(index=False))

        print("\n\nDetailed View of Top 3:")
        for _, row in recommendations.head(3).iterrows():
            print(f"\n{row['rank']}. {row['name']}")
            print(f"   Category: {row['category']}")
            print(f"   STEM Field: {row['stem_field']}")
            print(f"   Financial Barrier: {row['financial_barrier']}")
            print(f"   Location: {row['location_type']}")
            print(f"   Grade Level: {row['target_grade']}")
            print(f"   Match Score: {row['similarity_score']}")
            print(f"   URL: {row['url']}")
    else:
        print("\n[WARNING] No recommendations found. Try adjusting parameters.")

    print("\n\n" + "="*80)
    print("Example 2: Middle-income 10th grader interested in Environmental Science")
    print("="*80)

    student_profile_2 = {
        'financial_situation': 'Medium',
        'location': 'Hybrid',  # Open to both online and in-person
        'transportation_available': True,
        'grade_level': 10,  # Sophomore
        'academic_level': 'Beginner',  # New to field
        'time_availability': 12,  # 12 hours per week
        'support_needed': 'Medium',
        'stem_interests': 'environment climate change sustainability ecology conservation',
        'stem_fields': ['Earth Sciences', 'Biology', 'Other STEM'],
        'format_preferences': ['Summer Program', 'Research Opportunity', 'Camp']
    }

    recommendations = engine.get_recommendations(
        student_profile_2,
        top_n=10,
        min_similarity=0.15
    )

    if len(recommendations) > 0:
        print("\nTop 10 Recommendations:")
        print("-" * 80)
        print(recommendations[['rank', 'name', 'category', 'financial_barrier', 'similarity_score']].to_string(index=False))
    else:
        print("\n[WARNING] No recommendations found. Try adjusting parameters.")

    print("\n\n" + "="*80)
    print("Example 3: High-income 12th grader interested in Robotics")
    print("="*80)

    student_profile_3 = {
        'financial_situation': 'High',  # Can afford paid programs
        'location': 'In-person',  # Prefers hands-on
        'transportation_available': True,
        'grade_level': 12,  # Senior
        'academic_level': 'Advanced',  # Strong technical background
        'time_availability': 20,  # 20 hours per week
        'support_needed': 'Low',  # Self-directed
        'stem_interests': 'robotics engineering autonomous systems mechatronics control systems',
        'stem_fields': ['Robotics', 'Engineering', 'Technology'],
        'format_preferences': ['Competition', 'Research Opportunity', 'Internship']
    }

    recommendations = engine.get_recommendations(
        student_profile_3,
        top_n=10,
        min_similarity=0.15
    )

    if len(recommendations) > 0:
        print("\nTop 10 Recommendations:")
        print("-" * 80)
        print(recommendations[['rank', 'name', 'category', 'financial_barrier', 'similarity_score']].to_string(index=False))
    else:
        print("\n[WARNING] No recommendations found. Try adjusting parameters.")

    print("\n\n" + "="*80)
    print("Usage Tips")
    print("="*80)
    print("""
1. STEM Interests: Be specific! Use keywords like:
   - "machine learning neural networks python"
   - "molecular biology genetics research"
   - "robotics programming autonomous systems"

2. Adjusting Parameters:
   - top_n: Number of recommendations (default: 20)
   - min_similarity: Minimum match score (default: 0.3, try 0.1-0.2 for more results)
   - top_clusters: Number of clusters to search (default: 3, try 5 for broader search)

3. If you get few results:
   - Lower min_similarity to 0.1 or 0.15
   - Add more STEM fields to your profile
   - Broaden your format preferences

4. For low-income students:
   - Set financial_situation to 'Low'
   - The system will prioritize free and low-cost resources

5. Location matters:
   - 'Virtual': Online-only programs
   - 'Hybrid': Mix of online and in-person
   - 'In-person': Physical attendance required
    """)

    print("\n" + "="*80)
    print("Example Complete!")
    print("="*80)


if __name__ == '__main__':
    main()
