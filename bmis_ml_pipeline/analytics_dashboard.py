"""
BMIS Analytics Dashboard

Analyzes usage logs and feedback to generate metrics for impact assessment.
This data can be used for college applications and project presentations.

Usage:
    python analytics_dashboard.py
"""

import pandas as pd
from pathlib import Path
from datetime import datetime
import json


def load_data(logs_dir):
    """Load usage logs and feedback data."""
    usage_log_path = logs_dir / 'usage_log.csv'
    feedback_path = logs_dir / 'feedback.csv'

    usage_df = None
    feedback_df = None

    if usage_log_path.exists():
        usage_df = pd.read_csv(usage_log_path)
        print(f"✓ Loaded usage log: {len(usage_df)} events")
    else:
        print(f"⚠ Usage log not found at {usage_log_path}")

    if feedback_path.exists():
        feedback_df = pd.read_csv(feedback_path)
        print(f"✓ Loaded feedback: {len(feedback_df)} submissions")
    else:
        print(f"⚠ Feedback log not found at {feedback_path}")

    return usage_df, feedback_df


def analyze_usage(usage_df):
    """Analyze usage patterns."""
    if usage_df is None or len(usage_df) == 0:
        print("\nNo usage data available")
        return {}

    print("\n" + "="*60)
    print("USAGE ANALYTICS")
    print("="*60)

    stats = {}

    # Unique users (by session)
    unique_sessions = usage_df['session_id'].nunique()
    stats['unique_users'] = unique_sessions
    print(f"\n📊 Unique Users: {unique_sessions}")

    # Event breakdown
    event_counts = usage_df['event_type'].value_counts()
    print(f"\n📈 Event Breakdown:")
    for event, count in event_counts.items():
        print(f"  {event}: {count}")
        stats[f'event_{event}'] = count

    # Search-specific analytics
    search_events = usage_df[usage_df['event_type'] == 'search']
    if len(search_events) > 0:
        print(f"\n🔍 Search Analytics:")
        print(f"  Total searches: {len(search_events)}")
        stats['total_searches'] = len(search_events)

        # Grade level distribution
        if 'grade_level' in search_events.columns:
            grade_dist = search_events['grade_level'].value_counts().sort_index()
            print(f"\n  Grade Level Distribution:")
            for grade, count in grade_dist.items():
                try:
                    grade_num = int(grade)
                    grade_label = f"Grade {grade_num}" if grade_num > 0 else "Kindergarten"
                    print(f"    {grade_label}: {count}")
                except:
                    print(f"    {grade}: {count}")

        # Financial situation breakdown
        if 'financial_situation' in search_events.columns:
            financial_dist = search_events['financial_situation'].value_counts()
            print(f"\n  Financial Situation:")
            for situation, count in financial_dist.items():
                pct = 100 * count / len(search_events)
                print(f"    {situation}: {count} ({pct:.1f}%)")
                stats[f'financial_{situation}'] = count

        # Location preferences
        if 'location' in search_events.columns:
            location_dist = search_events['location'].value_counts()
            print(f"\n  Location Preferences:")
            for location, count in location_dist.items():
                pct = 100 * count / len(search_events)
                print(f"    {location}: {count} ({pct:.1f}%)")

        # Average STEM fields per search
        if 'num_stem_fields' in search_events.columns:
            avg_fields = search_events['num_stem_fields'].mean()
            print(f"\n  Average STEM fields per search: {avg_fields:.1f}")
            stats['avg_stem_fields'] = round(avg_fields, 2)

        # Average results per search
        if 'num_results' in search_events.columns:
            avg_results = search_events['num_results'].mean()
            print(f"  Average results per search: {avg_results:.1f}")
            stats['avg_results'] = round(avg_results, 2)

    # Browse analytics
    browse_events = usage_df[usage_df['event_type'] == 'browse_search']
    if len(browse_events) > 0:
        print(f"\n🔎 Browse Tab Analytics:")
        print(f"  Total browse searches: {len(browse_events)}")
        stats['total_browse_searches'] = len(browse_events)

    return stats


def analyze_feedback(feedback_df):
    """Analyze user feedback."""
    if feedback_df is None or len(feedback_df) == 0:
        print("\nNo feedback data available")
        return {}

    print("\n" + "="*60)
    print("FEEDBACK ANALYTICS")
    print("="*60)

    stats = {}

    # Total feedback
    total_feedback = len(feedback_df)
    stats['total_feedback'] = total_feedback
    print(f"\n💬 Total Feedback Submissions: {total_feedback}")

    # Average rating
    if 'rating' in feedback_df.columns:
        avg_rating = feedback_df['rating'].mean()
        rating_dist = feedback_df['rating'].value_counts().sort_index()

        stats['average_rating'] = round(avg_rating, 2)
        print(f"\n⭐ Average Rating: {avg_rating:.2f}/5.0")
        print(f"\n  Rating Distribution:")
        for rating, count in rating_dist.items():
            stars = "⭐" * int(rating)
            pct = 100 * count / total_feedback
            print(f"    {stars}: {count} ({pct:.1f}%)")

    # Found resources
    if 'found_resources' in feedback_df.columns:
        resource_dist = feedback_df['found_resources'].value_counts()
        print(f"\n🎯 Did Users Find New Resources?")
        for response, count in resource_dist.items():
            pct = 100 * count / total_feedback
            print(f"  {response}: {count} ({pct:.1f}%)")

        # Calculate "success rate" (found several or a few)
        success_responses = feedback_df['found_resources'].str.contains('Yes', na=False)
        success_rate = 100 * success_responses.sum() / total_feedback
        stats['resource_discovery_rate'] = round(success_rate, 1)
        print(f"\n  Discovery Success Rate: {success_rate:.1f}%")

    # Success stories
    if 'success_story' in feedback_df.columns:
        success_stories = feedback_df['success_story'].dropna()
        success_stories = success_stories[success_stories.str.strip() != '']
        num_stories = len(success_stories)
        stats['num_success_stories'] = num_stories
        print(f"\n🎉 Success Stories: {num_stories}")

        if num_stories > 0:
            print(f"\n  Sample Success Stories:")
            for i, story in enumerate(success_stories.head(3), 1):
                preview = story[:150] + "..." if len(story) > 150 else story
                print(f"\n  {i}. \"{preview}\"")

    # Contact rate
    if 'email' in feedback_df.columns:
        with_email = feedback_df['email'].notna() & (feedback_df['email'] != 'anonymous')
        contact_rate = 100 * with_email.sum() / total_feedback
        stats['contact_rate'] = round(contact_rate, 1)
        print(f"\n📧 Contact Rate: {contact_rate:.1f}% provided email")

    return stats


def generate_summary_report(usage_stats, feedback_stats, output_path):
    """Generate a summary JSON report."""
    report = {
        'generated_at': datetime.now().isoformat(),
        'usage_metrics': usage_stats,
        'feedback_metrics': feedback_stats,
        'key_highlights': []
    }

    # Generate key highlights for college essay
    highlights = []

    if 'unique_users' in usage_stats:
        highlights.append(f"Reached {usage_stats['unique_users']} unique users")

    if 'total_searches' in usage_stats:
        highlights.append(f"Generated {usage_stats['total_searches']} personalized recommendations")

    if 'average_rating' in feedback_stats:
        highlights.append(f"Achieved {feedback_stats['average_rating']}/5.0 average user rating")

    if 'resource_discovery_rate' in feedback_stats:
        highlights.append(f"{feedback_stats['resource_discovery_rate']}% of users discovered new STEM opportunities")

    if 'num_success_stories' in feedback_stats:
        highlights.append(f"Collected {feedback_stats['num_success_stories']} student success stories")

    report['key_highlights'] = highlights

    # Save report
    with open(output_path, 'w') as f:
        json.dump(report, f, indent=2)

    return report


def main():
    """Main function"""
    base_dir = Path(__file__).parent
    logs_dir = base_dir / 'logs'

    print("="*60)
    print("BMIS ANALYTICS DASHBOARD")
    print("="*60)
    print(f"Analyzing data from: {logs_dir}")
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    # Check if logs directory exists
    if not logs_dir.exists():
        print(f"⚠ Logs directory not found at {logs_dir}")
        print("Run the app first to generate usage data.")
        return

    # Load data
    usage_df, feedback_df = load_data(logs_dir)

    # Analyze usage
    usage_stats = analyze_usage(usage_df)

    # Analyze feedback
    feedback_stats = analyze_feedback(feedback_df)

    # Generate summary report
    report_path = logs_dir / f'analytics_summary_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
    report = generate_summary_report(usage_stats, feedback_stats, report_path)

    print("\n" + "="*60)
    print("KEY HIGHLIGHTS FOR COLLEGE ESSAY")
    print("="*60)
    for highlight in report['key_highlights']:
        print(f"  • {highlight}")

    print(f"\n📊 Full report saved to: {report_path}")
    print("="*60)


if __name__ == "__main__":
    main()
