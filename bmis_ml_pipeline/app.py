"""
BMIS Recommendation System - Professional Multi-Tab Application

Streamlit web app for the Black Minds in STEM recommendation system.
Features: Home page, personalized recommendations, resource browsing, feedback collection.

Version: 2.0 Professional
"""

import streamlit as st
import pandas as pd
import sys
from pathlib import Path
from datetime import datetime
import csv
import os

# Add src to path
sys.path.append(str(Path(__file__).parent / 'src'))

from recommendation_engine import BMISRecommendationEngine


# Page configuration
st.set_page_config(
    page_title="Black Minds in STEM - AI-Powered Resource Finder",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for dark/electric blue theme
st.markdown("""
<style>
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* Dark theme background */
    .stApp {
        background: linear-gradient(135deg, #0A1628 0%, #1a2332 100%);
    }

    /* Electric blue borders on resource cards - SIMPLE AND DIRECT */
    div[data-testid="element-container"] > div[data-testid="stVerticalBlock"] > div[style*="border"] {
        border: 2px solid #00D9FF !important;
        border-radius: 8px !important;
        transition: transform 0.3s ease, box-shadow 0.3s ease !important;
    }

    div[data-testid="element-container"] > div[data-testid="stVerticalBlock"] > div[style*="border"]:hover {
        transform: scale(1.02) !important;
        box-shadow: 0 8px 16px rgba(0, 217, 255, 0.3) !important;
    }

    /* FORCE badge column spacing globally */
    div[data-testid="stHorizontalBlock"]:has(.stMarkdown) {
        gap: 6px !important;
    }

    /* FORCE all inline badge divs to have consistent spacing */
    div[style*="background"][style*="padding"][style*="border-radius"] {
        margin-right: 10px !important;
    }

    div[style*="background"][style*="padding"][style*="border-radius"]:last-child {
        margin-right: 0 !important;
    }

    /* Custom tab styling using radio buttons */
    div[data-testid="stHorizontalBlock"] div[role="radiogroup"] {
        gap: 8px;
        background-color: rgba(10, 22, 40, 0.6);
        padding: 10px;
        border-radius: 8px;
        display: flex;
        justify-content: center;
    }

    div[data-testid="stHorizontalBlock"] div[role="radiogroup"] label {
        background-color: rgba(0, 217, 255, 0.1);
        border-radius: 8px;
        color: #00D9FF !important;
        padding: 12px 24px;
        font-weight: 600;
        border: 1px solid rgba(0, 217, 255, 0.2);
        cursor: pointer;
        transition: all 0.3s ease;
    }

    div[data-testid="stHorizontalBlock"] div[role="radiogroup"] label:hover {
        background-color: rgba(0, 217, 255, 0.15);
        border-color: #00D9FF;
    }

    div[data-testid="stHorizontalBlock"] div[role="radiogroup"] label[data-checked="true"] {
        background: linear-gradient(135deg, #00D9FF 0%, #0099CC 100%);
        color: #0A1628 !important;
        border: 1px solid #00D9FF;
    }

    div[data-testid="stHorizontalBlock"] div[role="radiogroup"] input[type="radio"] {
        display: none;
    }

    /* Headers */
    .main-header {
        font-size: 3.5rem;
        font-weight: 900;
        background: linear-gradient(135deg, #00D9FF 0%, #0099CC 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 0.5rem;
        letter-spacing: -1px;
    }

    .sub-header {
        font-size: 1.3rem;
        color: #B0E0FF;
        text-align: center;
        margin-bottom: 2rem;
        font-weight: 400;
    }

    .tagline {
        font-size: 1.1rem;
        color: #80C0E0;
        text-align: center;
        margin: 1.5rem 0;
        font-style: italic;
    }

    /* Feature cards */
    .feature-box {
        background: rgba(0, 217, 255, 0.1);
        border: 1px solid rgba(0, 217, 255, 0.3);
        border-radius: 12px;
        padding: 1.5rem;
        text-align: center;
        margin: 1rem 0;
        transition: all 0.3s ease;
    }

    .feature-box:hover {
        background: rgba(0, 217, 255, 0.15);
        border-color: #00D9FF;
        transform: translateY(-2px);
    }

    .feature-icon {
        font-size: 2.5rem;
        margin-bottom: 0.5rem;
    }

    .feature-title {
        font-size: 1.1rem;
        font-weight: 700;
        color: #00D9FF;
        margin-bottom: 0.5rem;
    }

    .feature-text {
        color: #B0E0FF;
        font-size: 0.95rem;
    }

    /* Info boxes */
    .info-box {
        background: rgba(0, 217, 255, 0.08);
        border-left: 4px solid #00D9FF;
        padding: 1.2rem;
        margin: 1.5rem 0;
        border-radius: 8px;
        color: #B0E0FF;
    }

    .success-box {
        background: rgba(16, 185, 129, 0.1);
        border-left: 4px solid #10B981;
        padding: 1rem;
        margin: 1rem 0;
        border-radius: 8px;
        color: #6EE7B7;
    }

    .warning-box {
        background: rgba(245, 158, 11, 0.1);
        border-left: 4px solid #F59E0B;
        padding: 1rem;
        margin: 1rem 0;
        border-radius: 8px;
        color: #FCD34D;
    }

    /* Resource cards */
    .rec-card {
        background: linear-gradient(135deg, rgba(10, 22, 40, 0.9) 0%, rgba(26, 35, 50, 0.9) 100%);
        border: 1px solid rgba(0, 217, 255, 0.2);
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1.2rem 0;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
        transition: all 0.3s ease;
    }

    .rec-card:hover {
        border-color: #00D9FF;
        box-shadow: 0 6px 20px rgba(0, 217, 255, 0.2);
        transform: translateY(-3px);
    }

    .rec-title {
        font-size: 1.4rem;
        font-weight: 700;
        color: #00D9FF;
        margin-bottom: 1rem;
    }

    .rec-detail {
        display: inline-block;
        margin-right: 1.5rem;
        margin-bottom: 0.75rem;
        font-size: 0.9rem;
        color: #B0E0FF;
    }

    .rec-description {
        color: #80C0E0;
        font-size: 0.95rem;
        line-height: 1.6;
        margin: 1rem 0;
    }

    /* Badges - Updated padding for better visibility */
    .badge-virtual {
        background-color: #10B981;
        color: white;
        padding: 10px 18px;
        border-radius: 6px;
        font-size: 0.85rem;
        font-weight: 600;
        display: inline-block;
        margin-right: 0.5rem;
        margin-bottom: 0.5rem;
    }

    .badge-inperson {
        background-color: #3B82F6;
        color: white;
        padding: 10px 18px;
        border-radius: 6px;
        font-size: 0.85rem;
        font-weight: 600;
        display: inline-block;
        margin-right: 0.5rem;
        margin-bottom: 0.5rem;
    }

    .badge-hybrid {
        background-color: #F59E0B;
        color: white;
        padding: 10px 18px;
        border-radius: 6px;
        font-size: 0.85rem;
        font-weight: 600;
        display: inline-block;
        margin-right: 0.5rem;
        margin-bottom: 0.5rem;
    }

    .badge-free {
        background: linear-gradient(135deg, #FFD700 0%, #FFA500 100%);
        color: #0A1628;
        padding: 10px 18px;
        border-radius: 6px;
        font-size: 0.85rem;
        font-weight: 700;
        display: inline-block;
        margin-right: 0.5rem;
        margin-bottom: 0.5rem;
    }

    .badge-low {
        background-color: #10B981;
        color: white;
        padding: 10px 18px;
        border-radius: 6px;
        font-size: 0.85rem;
        font-weight: 600;
        display: inline-block;
        margin-right: 0.5rem;
        margin-bottom: 0.5rem;
    }

    .badge-medium {
        background-color: #F59E0B;
        color: white;
        padding: 10px 18px;
        border-radius: 6px;
        font-size: 0.85rem;
        font-weight: 600;
        display: inline-block;
        margin-right: 0.5rem;
        margin-bottom: 0.5rem;
    }

    .badge-high {
        background-color: #EF4444;
        color: white;
        padding: 10px 18px;
        border-radius: 6px;
        font-size: 0.85rem;
        font-weight: 600;
        display: inline-block;
        margin-right: 0.5rem;
        margin-bottom: 0.5rem;
    }

    .badge-diversity {
        background-color: #10B981;
        color: white;
        padding: 10px 18px;
        border-radius: 6px;
        font-size: 0.85rem;
        font-weight: 600;
        display: inline-block;
        margin-right: 0.5rem;
        margin-bottom: 0.5rem;
    }

    .badge-popular {
        background: linear-gradient(135deg, #FFD700 0%, #FFA500 100%);
        color: #0A1628;
        padding: 10px 18px;
        border-radius: 6px;
        font-size: 0.85rem;
        font-weight: 700;
        display: inline-block;
        margin-right: 0.5rem;
        margin-bottom: 0.5rem;
    }

    /* Match percentage badges */
    .badge-match-excellent {
        background: linear-gradient(135deg, #10B981 0%, #059669 100%);
        color: white;
        padding: 10px 18px;
        border-radius: 8px;
        font-size: 0.9rem;
        font-weight: 700;
        display: inline-block;
        margin-right: 0.5rem;
        margin-bottom: 0.5rem;
    }

    .badge-match-good {
        background: linear-gradient(135deg, #F59E0B 0%, #D97706 100%);
        color: white;
        padding: 10px 18px;
        border-radius: 8px;
        font-size: 0.9rem;
        font-weight: 700;
        display: inline-block;
        margin-right: 0.5rem;
        margin-bottom: 0.5rem;
    }

    .badge-match-fair {
        background: linear-gradient(135deg, #F97316 0%, #EA580C 100%);
        color: white;
        padding: 10px 18px;
        border-radius: 8px;
        font-size: 0.9rem;
        font-weight: 700;
        display: inline-block;
        margin-right: 0.5rem;
        margin-bottom: 0.5rem;
    }

    .badge-match-low {
        background: linear-gradient(135deg, #6B7280 0%, #4B5563 100%);
        color: white;
        padding: 10px 18px;
        border-radius: 8px;
        font-size: 0.9rem;
        font-weight: 700;
        display: inline-block;
        margin-right: 0.5rem;
        margin-bottom: 0.5rem;
    }

    /* Buttons - NO HOVER by default */
    .stButton > button {
        background: linear-gradient(135deg, #00D9FF 0%, #0099CC 100%);
        color: #0A1628;
        font-weight: 700;
        border: none;
        border-radius: 8px;
        padding: 0.75rem 2rem;
        font-size: 1.1rem;
        transition: none;
    }

    /* Modal/Dialog styling */
    [data-testid="stDialog"] {
        max-width: 800px !important;
        max-height: 85vh !important;
    }

    [data-testid="stDialog"] > div {
        max-height: 85vh !important;
        overflow-y: auto !important;
        padding: 1.5rem !important;
    }

    /* Reduce modal padding for better space usage */
    [data-testid="stDialog"] section {
        padding: 1rem !important;
    }

    /* Form elements */
    .stSelectbox, .stMultiSelect, .stTextArea, .stTextInput {
        color: #B0E0FF;
    }

    /* Links */
    a {
        color: #00D9FF;
        text-decoration: none;
        font-weight: 600;
        transition: all 0.2s ease;
    }

    a:hover {
        color: #33E0FF;
        text-decoration: underline;
    }


    /* How it works section */
    .step-number {
        display: inline-block;
        background: linear-gradient(135deg, #00D9FF 0%, #0099CC 100%);
        color: #0A1628;
        width: 40px;
        height: 40px;
        line-height: 40px;
        border-radius: 50%;
        text-align: center;
        font-weight: 900;
        font-size: 1.3rem;
        margin-right: 1rem;
    }

    .step-text {
        color: #B0E0FF;
        font-size: 1.1rem;
    }

    /* FORCE badge spacing on ALL pages - even more aggressive */
    [data-testid="stHorizontalBlock"] [data-testid="column"] {
        padding-left: 5px !important;
        padding-right: 5px !important;
    }

    [data-testid="stHorizontalBlock"] [data-testid="column"]:first-child {
        padding-left: 0 !important;
    }

    [data-testid="stHorizontalBlock"] [data-testid="column"]:last-child {
        padding-right: 0 !important;
    }
</style>
<script>
// Force electric blue borders on resource cards - NUCLEAR OPTION
(function() {
    function applyBorders() {
        // Find all containers with borders (resource cards)
        const containers = document.querySelectorAll('[data-testid="stVerticalBlock"] div[style*="border"]');

        containers.forEach(container => {
            if (container.style.border && container.style.border.includes('1px')) {
                container.style.border = '2px solid #00D9FF';
                container.style.borderRadius = '8px';
            }
        });
    }

    // Run immediately
    applyBorders();

    // Run again after delays (to catch dynamically loaded content)
    setTimeout(applyBorders, 100);
    setTimeout(applyBorders, 500);
    setTimeout(applyBorders, 1000);

    // Re-run on any DOM change
    const observer = new MutationObserver(applyBorders);
    observer.observe(document.body, { childList: true, subtree: true });
})();
</script>
""", unsafe_allow_html=True)


@st.cache_resource
def load_recommendation_engine():
    """Load the recommendation engine (cached for performance)"""
    engine = BMISRecommendationEngine()
    engine.load_all_models()
    return engine


def log_usage(event_type, data=None):
    """
    Log usage analytics to CSV file.

    Args:
        event_type: Type of event (e.g., 'search', 'filter', 'feedback')
        data: Additional data to log (dict)
    """
    try:
        # Create logs directory if it doesn't exist
        logs_dir = Path(__file__).parent / 'logs'
        logs_dir.mkdir(exist_ok=True)

        log_file = logs_dir / 'usage_log.csv'

        # Prepare log entry
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'event_type': event_type,
            'session_id': st.session_state.get('session_id', 'unknown'),
        }

        # Add additional data
        if data:
            log_entry.update(data)

        # Write to CSV
        file_exists = log_file.exists()
        with open(log_file, 'a', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=log_entry.keys())
            if not file_exists:
                writer.writeheader()
            writer.writerow(log_entry)
    except Exception as e:
        # Silently fail - don't interrupt user experience
        pass


def save_feedback(rating, liked, improve, found_resources, success_story, email):
    """
    Save user feedback to CSV file.

    Args:
        rating: Star rating (1-5)
        liked: What user liked most
        improve: What could be improved
        found_resources: Did user find new resources
        success_story: User's success story (optional)
        email: User's email (optional)
    """
    try:
        # Create logs directory if it doesn't exist
        logs_dir = Path(__file__).parent / 'logs'
        logs_dir.mkdir(exist_ok=True)

        feedback_file = logs_dir / 'feedback.csv'

        # Prepare feedback entry
        feedback_entry = {
            'timestamp': datetime.now().isoformat(),
            'rating': rating,
            'liked_most': liked,
            'improvements': improve,
            'found_resources': found_resources,
            'success_story': success_story,
            'email': email if email else 'anonymous'
        }

        # Write to CSV
        file_exists = feedback_file.exists()
        with open(feedback_file, 'a', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=feedback_entry.keys())
            if not file_exists:
                writer.writeheader()
            writer.writerow(feedback_entry)

        return True
    except Exception as e:
        return False


def save_resource_vote(resource_id, resource_name, vote_type):
    """
    Save resource vote (helpful/not_helpful) to CSV file.

    Args:
        resource_id: Unique identifier for the resource
        resource_name: Name of the resource
        vote_type: 'helpful' or 'not_helpful'
    """
    try:
        # Create logs directory if it doesn't exist
        logs_dir = Path(__file__).parent / 'logs'
        logs_dir.mkdir(exist_ok=True)

        vote_file = logs_dir / 'resource_votes.csv'

        # Prepare vote entry
        vote_entry = {
            'timestamp': datetime.now().isoformat(),
            'session_id': st.session_state.get('session_id', 'unknown'),
            'resource_id': resource_id,
            'resource_name': resource_name,
            'vote_type': vote_type
        }

        # Write to CSV
        file_exists = vote_file.exists()
        with open(vote_file, 'a', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=vote_entry.keys())
            if not file_exists:
                writer.writeheader()
            writer.writerow(vote_entry)

        return True
    except Exception as e:
        return False


def load_resource_votes():
    """
    Load resource votes from CSV file.

    Returns:
        DataFrame with vote counts per resource
    """
    try:
        logs_dir = Path(__file__).parent / 'logs'
        vote_file = logs_dir / 'resource_votes.csv'

        if vote_file.exists():
            votes_df = pd.read_csv(vote_file)
            # Count helpful votes per resource
            helpful_counts = votes_df[votes_df['vote_type'] == 'helpful'].groupby('resource_id').size()
            return helpful_counts
        else:
            return pd.Series(dtype=int)
    except Exception:
        return pd.Series(dtype=int)


def save_problem_report(issue_type, resource_info, description, email):
    """
    Save problem report to CSV file.

    Args:
        issue_type: Type of issue reported
        resource_info: Resource name or URL
        description: Description of the problem
        email: User's email (optional)
    """
    try:
        # Create logs directory if it doesn't exist
        logs_dir = Path(__file__).parent / 'logs'
        logs_dir.mkdir(exist_ok=True)

        report_file = logs_dir / 'problem_reports.csv'

        # Prepare report entry
        report_entry = {
            'timestamp': datetime.now().isoformat(),
            'session_id': st.session_state.get('session_id', 'unknown'),
            'issue_type': issue_type,
            'resource_name_url': resource_info,
            'description': description,
            'email': email if email else 'anonymous'
        }

        # Write to CSV
        file_exists = report_file.exists()
        with open(report_file, 'a', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=report_entry.keys())
            if not file_exists:
                writer.writeheader()
            writer.writerow(report_entry)

        return True
    except Exception as e:
        return False


@st.dialog("Report a Problem")
def report_problem_modal():
    """Display the Report a Problem modal form"""
    st.markdown("Help us improve BMIS by reporting issues you encounter.")

    with st.form("problem_report_form", clear_on_submit=True):
        issue_type = st.selectbox(
            "Issue Type",
            options=[
                "Broken link / 404 error",
                "Link works but goes to wrong page",
                "Incorrect resource information",
                "Technical bug",
                "Other"
            ]
        )

        resource_info = st.text_input(
            "Resource Name/URL",
            placeholder="Which resource has the problem?",
            help="Enter the name or URL of the resource with the issue"
        )

        description = st.text_area(
            "Description",
            placeholder="Please describe the issue in detail",
            help="The more details you provide, the faster we can fix it",
            height=120
        )

        email = st.text_input(
            "Your Email (Optional)",
            placeholder="If you'd like us to follow up",
            help="Leave your email if you want updates on the issue"
        )

        col1, col2 = st.columns(2)

        with col1:
            submit = st.form_submit_button("Submit Report", use_container_width=True)

        with col2:
            cancel = st.form_submit_button("Cancel", use_container_width=True)

        if submit:
            if not resource_info.strip() or not description.strip():
                st.error("⚠️ Please provide both resource info and a description.")
            else:
                success = save_problem_report(issue_type, resource_info, description, email)
                if success:
                    st.success("✅ Thank you! We've received your report and will investigate.")
                    log_usage('problem_reported', {'issue_type': issue_type})
                    import time
                    time.sleep(2)
                    st.rerun()
                else:
                    st.error("❌ Error saving report. Please try again.")

        if cancel:
            st.rerun()


@st.dialog("Resource Details", width="wide")
def show_resource_preview(resource):
    """
    Display detailed resource preview modal - WIDER for better readability.

    Args:
        resource: Resource dictionary/Series with all details
    """
    # Modal CSS styling - PORTRAIT-ORIENTED modal with minimal spacing
    st.markdown("""<style>
    /* CRITICAL: Make close button (X) VISIBLE - white color on dark background */
    [data-testid="stDialog"] button[aria-label="Close"] {
        background-color: rgba(0, 0, 0, 0.5) !important;
        color: white !important;
        border-radius: 50% !important;
        width: 32px !important;
        height: 32px !important;
        padding: 4px !important;
    }

    [data-testid="stDialog"] button[aria-label="Close"]:hover {
        background-color: rgba(255, 0, 0, 0.8) !important;
        color: white !important;
    }

    /* Center modal - PORTRAIT-ORIENTED, not landscape */
    [data-testid="stDialog"] {
        position: fixed !important;
        top: 50% !important;
        left: 50% !important;
        transform: translate(-50%, -50%) !important;
        max-height: 85vh !important;
        max-width: 700px !important;
        width: 65vw !important;
        overflow-y: auto !important;
        padding: 2rem !important;
    }

    /* MINIMAL SPACING - tight gap between title and content */
    [data-testid="stDialog"] h3 {
        margin-top: 0 !important;
        margin-bottom: 0.2rem !important;
        line-height: 1.2 !important;
    }

    [data-testid="stDialog"] hr {
        margin: 0.3rem 0 !important;
    }

    [data-testid="stDialog"] p {
        margin-bottom: 0.3rem !important;
        line-height: 1.5 !important;
    }

    [data-testid="stDialog"] .stMarkdown {
        margin-bottom: 0.2rem !important;
    }

    [data-testid="stDialog"] [data-testid="column"] {
        padding: 0.2rem !important;
    }

    /* Compact modal content */
    [data-testid="stDialog"] > div {
        padding: 0.5rem !important;
    }
    </style>""", unsafe_allow_html=True)

    # Scroll to top instantly
    st.markdown("""<script>
    (function() {
        const dialog = document.querySelector('[data-testid="stDialog"]');
        if (dialog) { dialog.scrollTop = 0; }
    })();
    </script>""", unsafe_allow_html=True)

    # Resource name as header - NO horizontal rule after title
    st.markdown(f"### {resource.get('name', 'Untitled Resource')}")

    # Match score badge (if available)
    # Use match_percentage if available (from percentile ranking), otherwise fall back to similarity_score
    if 'match_percentage' in resource and not pd.isna(resource.get('match_percentage')):
        match_score = resource.get('match_percentage')
    else:
        # Fallback: convert similarity_score to percentage
        sim_score = resource.get('similarity_score', 'N/A')
        if sim_score != 'N/A' and not pd.isna(sim_score):
            match_score = float(sim_score) * 100
        else:
            match_score = 'N/A'

    if match_score != 'N/A' and not pd.isna(match_score):
        match_badge = format_match_score(match_score)
        st.markdown(match_badge, unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)

    # Key information in columns
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**📍 Attendance Type**")
        st.write(resource.get('location_type', 'N/A'))

        st.markdown("**🎓 Grade Level**")
        st.write(resource.get('target_grade', resource.get('target_grade_standardized', 'N/A')))

        st.markdown("**🏷️ Category**")
        st.write(resource.get('category', resource.get('category_tier1', 'N/A')))

        st.markdown("**⏱️ Time Commitment**")
        formatted_time = format_time_commitment(resource.get('time_commitment', 'N/A'))
        # Remove icon since we already have it in the label
        formatted_time_display = formatted_time.replace('⏱️ Time: ', '')
        st.write(formatted_time_display)

    with col2:
        st.markdown("**🔬 STEM Field**")
        st.write(resource.get('stem_field', resource.get('stem_field_tier1', 'N/A')))

        st.markdown("**📅 Deadline**")
        st.write(resource.get('deadline', 'N/A'))

        st.markdown("**🤝 Support Level**")
        st.write(resource.get('support_level', 'N/A'))

    # Full description
    st.markdown("---")
    st.markdown("**📝 Description**")
    description = resource.get('description', 'No description available.')
    st.write(description)

    # For short descriptions, add organized metadata
    if len(str(description)) < 100:
        st.markdown("---")
        st.markdown("**📋 Program Details:**")

        st.markdown(f"""
        - **Category:** {resource.get('category', resource.get('category_tier1', 'N/A'))}
        - **STEM Field:** {resource.get('stem_field', resource.get('stem_field_tier1', 'N/A'))}
        - **Grade Level:** {resource.get('target_grade', resource.get('target_grade_standardized', 'N/A'))}
        - **Attendance Type:** {resource.get('location_type', 'N/A')}
        """)
        st.info("💡 For complete details, visit the official website")

    # Additional details if available
    if resource.get('prerequisite_level') and resource.get('prerequisite_level') != 'N/A':
        st.markdown("---")
        st.markdown("**📚 Prerequisites**")
        st.write(resource.get('prerequisite_level'))

    # Visit website and Google search buttons
    st.markdown("---")
    url = resource.get('url', '#')

    col1, col2 = st.columns(2)

    with col1:
        if url and url != '#' and not pd.isna(url):
            st.link_button(
                "🔗 Visit Official Website",
                url,
                use_container_width=True
            )
        else:
            st.button("🔗 Visit Official Website", disabled=True, use_container_width=True)

    with col2:
        # Google Search button
        resource_name = resource.get('name', '')
        source = resource.get('source', '')
        search_query = f"{resource_name} {source}".strip()
        google_search_url = f"https://www.google.com/search?q={search_query.replace(' ', '+')}"
        st.link_button(
            "🔍 Search Google",
            google_search_url,
            use_container_width=True
        )

    st.caption("⚠️ Links verified Oct 2025. Use Google Search if link doesn't work.")


def render_footer():
    """Render the footer with Report a Problem button"""
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("---")

    col1, col2, col3 = st.columns([1, 1, 1])

    with col2:
        if st.button("🚩 Report a Problem", use_container_width=True, key=f"report_problem_{st.session_state.get('current_tab', 'home')}"):
            report_problem_modal()


def get_simplified_cost_category(financial_barrier, cost_category):
    """
    Convert dataset cost values to simplified 4-category system.

    Categories:
    - Free ($0)
    - Low Cost ($1-$500)
    - Medium Cost ($501-$2K)
    - High Cost ($2K+)

    Args:
        financial_barrier: Value from financial_barrier_level column
        cost_category: Value from cost_category column

    Returns:
        One of: 'Free ($0)', 'Low Cost ($1-$500)', 'Medium Cost ($501-$2K)', 'High Cost ($2K+)'
    """
    # Check cost_category first (more specific)
    cost_cat_str = str(cost_category).lower()

    # Free category
    if any(keyword in cost_cat_str for keyword in ['free', 'school-based', '$0']):
        # Exclude "freemium" and similar unless truly free
        if 'freemium' not in cost_cat_str and 'free-tier' not in cost_cat_str:
            return 'Free ($0)'

    # Parse dollar amounts from cost_category
    if '$' in cost_cat_str:
        # Extract numbers
        import re
        numbers = re.findall(r'\d+', cost_cat_str)
        if numbers:
            # Get the maximum value mentioned
            max_cost = max([int(n) for n in numbers])
            if max_cost == 0:
                return 'Free ($0)'
            elif max_cost <= 500:
                return 'Low Cost ($1-$500)'
            elif max_cost <= 2000:
                return 'Medium Cost ($501-$2K)'
            else:
                return 'High Cost ($2K+)'

    # Fall back to financial_barrier_level
    barrier_str = str(financial_barrier).lower()
    if barrier_str == 'low':
        return 'Low Cost ($1-$500)'
    elif barrier_str in ['medium', 'moderate']:
        return 'Medium Cost ($501-$2K)'
    elif barrier_str in ['high', 'prohibitive']:
        return 'High Cost ($2K+)'

    # Default to Low Cost if unclear
    return 'Low Cost ($1-$500)'


def format_time_commitment(time_str):
    """
    Format time commitment string to show both weekly and daily hours.

    Args:
        time_str: Time commitment string (e.g., "10 hours/week", "1-2 hours", "Self-paced")

    Returns:
        Formatted string with weekly and daily hours, or original string if can't parse
    """
    import re

    if pd.isna(time_str) or not time_str or time_str == 'N/A':
        return "⏱️ Time: Varies"

    time_str_lower = str(time_str).lower()

    # Handle common non-numeric patterns
    non_numeric_patterns = ['self-paced', 'flexible', 'variable', 'ongoing', 'academic year',
                           'full-time', 'part-time', 'per-lesson', 'competition']
    if any(pattern in time_str_lower for pattern in non_numeric_patterns):
        return f"⏱️ Time: {time_str}"

    # Try to extract hours from patterns like "10 hours/week", "1-2 hours", "300 hours"
    # Match patterns: "X hours", "X-Y hours", "X hours/week", "X-Y hours/week"
    hours_match = re.search(r'(\d+)(?:-(\d+))?\s*hours?(?:/week)?', time_str_lower)

    if hours_match:
        min_hours = int(hours_match.group(1))
        max_hours = int(hours_match.group(2)) if hours_match.group(2) else min_hours

        # Average the range
        avg_hours = (min_hours + max_hours) / 2

        # If total hours (like "300 hours"), spread over typical program length
        if 'week' not in time_str_lower and avg_hours > 40:
            return f"⏱️ Time: {time_str}"  # Show as-is for large total hours

        # Assume per week if not specified but reasonable range
        if 'week' not in time_str_lower and avg_hours <= 40:
            # Likely per session or per week
            if avg_hours < 5:
                return f"⏱️ Time: {time_str} per session"
            else:
                time_str = f"{time_str}/week"

        # Calculate daily hours (weekly / 7)
        daily_hours = avg_hours / 7

        if daily_hours < 1:
            return f"⏱️ Time: {int(avg_hours)} hrs/week (< 1 hr/day)"
        elif daily_hours >= 5:
            return f"⏱️ Time: {int(avg_hours)} hrs/week (> 5 hrs/day)"
        else:
            return f"⏱️ Time: {int(avg_hours)} hrs/week (~{daily_hours:.1f} hrs/day)"

    # If we couldn't parse, return original with icon
    return f"⏱️ Time: {time_str}"


def parse_grade_range(grade_str):
    """
    Parse grade range string into list of grades.

    Args:
        grade_str: String like "9-12", "K-5", "6", etc.

    Returns:
        List of integer grades, or None if parsing fails
    """
    if pd.isna(grade_str) or grade_str == 'N/A':
        return None

    grade_str = str(grade_str).strip()

    # Handle K-5 format
    if grade_str.startswith('K'):
        if '-' in grade_str:
            parts = grade_str.split('-')
            try:
                max_grade = int(parts[1])
                return list(range(0, max_grade + 1))  # K=0, 1, 2, ..., max_grade
            except:
                return None
        else:
            return [0]  # Just K

    # Handle ranges like "9-12"
    if '-' in grade_str:
        parts = grade_str.split('-')
        try:
            min_grade = int(parts[0])
            max_grade = int(parts[1])
            return list(range(min_grade, max_grade + 1))
        except:
            return None

    # Handle single grade like "10"
    try:
        return [int(grade_str)]
    except:
        return None


def is_grade_appropriate(student_grade, target_grade_str, tolerance=2):
    """
    Check if a resource is appropriate for student's grade level.

    Args:
        student_grade: Student's grade (6-12)
        target_grade_str: Resource's target grade string
        tolerance: How many grades away is acceptable (default: 2)

    Returns:
        Boolean: True if appropriate, False otherwise
    """
    grade_range = parse_grade_range(target_grade_str)

    if grade_range is None:
        return True  # If we can't parse, include it (benefit of doubt)

    # Check if student grade is in range
    if student_grade in grade_range:
        return True

    # Check if within tolerance
    min_grade = min(grade_range)
    max_grade = max(grade_range)

    if abs(student_grade - min_grade) <= tolerance or abs(student_grade - max_grade) <= tolerance:
        return True

    return False


def filter_recommendations(recommendations, location_filter, grade_filter, student_grade):
    """
    Apply client-side filters to recommendations.

    Args:
        recommendations: DataFrame of recommendations
        location_filter: Selected location filter option
        grade_filter: Selected grade filter option
        student_grade: Student's grade level

    Returns:
        Filtered DataFrame
    """
    filtered = recommendations.copy()

    # Apply location filter
    if location_filter == "Virtual/Online Only":
        filtered = filtered[filtered['location_type'].str.contains('Virtual|Hybrid', case=False, na=False)]
    elif location_filter == "In-Person Only":
        filtered = filtered[filtered['location_type'].str.contains('In-person|Hybrid', case=False, na=False)]
    elif location_filter == "Hybrid (Virtual + In-Person)":
        # Show all (Hybrid accepts everything)
        pass
    # "Show All" - no filtering

    # Apply grade filter
    if grade_filter == "My Grade Level Only":
        filtered = filtered[filtered.apply(
            lambda row: student_grade in (parse_grade_range(row['target_grade']) or []),
            axis=1
        )]
    elif grade_filter == "My Grade ±1 Year":
        filtered = filtered[filtered.apply(
            lambda row: is_grade_appropriate(student_grade, row['target_grade'], tolerance=1),
            axis=1
        )]
    elif grade_filter == "My Grade ±2 Years":
        filtered = filtered[filtered.apply(
            lambda row: is_grade_appropriate(student_grade, row['target_grade'], tolerance=2),
            axis=1
        )]
    elif grade_filter == "Elementary (K-5)":
        filtered = filtered[filtered.apply(
            lambda row: any(g <= 5 for g in (parse_grade_range(row['target_grade']) or [])),
            axis=1
        )]
    elif grade_filter == "Middle School (6-8)":
        filtered = filtered[filtered.apply(
            lambda row: any(6 <= g <= 8 for g in (parse_grade_range(row['target_grade']) or [])),
            axis=1
        )]
    elif grade_filter == "High School (9-12)":
        filtered = filtered[filtered.apply(
            lambda row: any(9 <= g <= 12 for g in (parse_grade_range(row['target_grade']) or [])),
            axis=1
        )]
    # "Show All" - no filtering

    return filtered


def display_recommendation_card(rec, rank, show_save_button=True):
    """
    Display a single recommendation as a styled card.

    Args:
        rec: Row from recommendations DataFrame
        rank: Recommendation rank number
        show_save_button: Whether to show the save/heart button
    """
    # Initialize saved resources in session state
    if 'saved_resources' not in st.session_state:
        st.session_state['saved_resources'] = []

    # Determine location badge style
    location_type = str(rec.get('location_type', 'N/A'))
    if 'Virtual' in location_type:
        location_badge = f'<span class="badge-virtual">🟢 {location_type}</span>'
    elif 'In-person' in location_type:
        location_badge = f'<span class="badge-inperson">🔵 {location_type}</span>'
    else:
        location_badge = f'<span class="badge-hybrid">🟡 {location_type}</span>'

    # Determine cost badge style using simplified 4-category system
    financial_barrier = rec.get('financial_barrier', rec.get('financial_barrier_level', 'N/A'))
    cost_category = rec.get('cost_category', 'N/A')
    simplified_cost = get_simplified_cost_category(financial_barrier, cost_category)

    if 'Free' in simplified_cost:
        cost_badge = f'<span class="badge-free">💎 FREE</span>'
    elif 'Low Cost' in simplified_cost:
        cost_badge = f'<span class="badge-low">💵 Low Cost</span>'
    elif 'Medium Cost' in simplified_cost:
        cost_badge = f'<span class="badge-medium">💰 Medium Cost</span>'
    else:  # High Cost
        cost_badge = f'<span class="badge-high">💸 High Cost</span>'

    # Format match score as percentage with badge
    # Use match_percentage if available (from percentile ranking), otherwise fall back to similarity_score
    if 'match_percentage' in rec and not pd.isna(rec.get('match_percentage')):
        match_score = rec.get('match_percentage')
    else:
        # Fallback: convert similarity_score to percentage
        sim_score = rec.get('similarity_score', 'N/A')
        if sim_score != 'N/A' and not pd.isna(sim_score):
            match_score = float(sim_score) * 100
        else:
            match_score = 'N/A'

    match_badge = format_match_score(match_score)

    # Check for diversity focus
    diversity_badge = ''
    underrep_friendly = rec.get('underrepresented_friendly', False)
    diversity_focus = str(rec.get('diversity_focus', '')).lower()

    # Check if resource has diversity focus
    diversity_keywords = ['diversity', 'inclusion', 'underrepresented', 'minority',
                         'black', 'african american', 'equity', 'first-generation']

    if underrep_friendly or any(keyword in diversity_focus for keyword in diversity_keywords):
        diversity_badge = '<span class="badge-diversity">🤝 Diversity Focus</span>'

    # Build card HTML with dark theme
    description = str(rec.get('description', 'No description available.'))
    description_preview = description[:250] + '...' if len(description) > 250 else description

    # Format time commitment
    time_formatted = format_time_commitment(rec.get('time_commitment', 'N/A'))

    # Container for resource card - border and hover styling applied via global CSS
    with st.container(border=True, key=f"card_{rank}_{rec.get('name', 'x')[:5]}"):
        # Title
        st.markdown(f"### #{rank}. {rec.get('name', 'Untitled Resource')}")

        # Badge styling with proper padding for comfortable spacing
        st.markdown("""<style>
        /* Badge styling with 12px 20px padding - more space around text */
        [data-testid="stVerticalBlock"] .stAlert,
        .stAlert,
        [class*="badge"] {
            padding: 12px 20px !important;
            display: inline-flex !important;
            align-items: center !important;
            justify-content: center !important;
            font-size: 14px !important;
            margin: 0 !important;
            margin-right: 6px !important;
            width: auto !important;
            min-width: auto !important;
            max-width: none !important;
            border-radius: 6px !important;
        }

        [data-testid="stVerticalBlock"] .stAlert p,
        .stAlert p {
            font-size: 14px !important;
            margin: 0 !important;
            padding: 0 !important;
            line-height: 1.4 !important;
            font-weight: 500 !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            text-align: center !important;
        }

        [data-testid="stVerticalBlock"] .stAlert div,
        .stAlert div {
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            margin: 0 !important;
            padding: 0 !important;
        }

        /* TINY 6px gap between columns */
        [data-testid="stVerticalBlock"] [data-testid="stHorizontalBlock"] {
            gap: 6px !important;
        }

        /* Remove last badge right margin */
        [data-testid="stVerticalBlock"] .stAlert:last-child {
            margin-right: 0 !important;
        }

        /* Force proper spacing on Streamlit's alert/badge components */
        div[data-testid="stAlert"] {
            padding: 12px 20px !important;
            margin: 0 6px 0 0 !important;
        }

        div[data-testid="stAlert"] > div {
            padding: 0 !important;
            margin: 0 !important;
        }
        </style>""", unsafe_allow_html=True)

        # DYNAMIC column widths based on whether we have a match score
        if match_score != 'N/A' and not pd.isna(match_score):
            # Has match score: Location | Cost | Match | Diversity
            badge_cols = st.columns([0.8, 0.7, 1.0, 0.8, 6.7])  # Added 5th column for diversity
        else:
            # No match score: Location | Cost | Diversity (shift diversity left)
            if diversity_badge:
                badge_cols = st.columns([0.8, 0.7, 0.8, 7.7])  # 3 badges only
            else:
                badge_cols = st.columns([0.8, 0.7, 8.5])  # 2 badges only

        # Render badges based on configuration
        with badge_cols[0]:
            # Location badge - always first
            if 'Virtual' in location_type:
                st.markdown(f"""
                <div style="background: #10B981; color: white; padding: 8px 20px;
                            border-radius: 8px; font-size: 14px; font-weight: 600;
                            display: inline-block; text-align: center; white-space: nowrap;">
                    🟢 {location_type}
                </div>
                """, unsafe_allow_html=True)
            elif 'In-person' in location_type:
                st.markdown(f"""
                <div style="background: #3B82F6; color: white; padding: 8px 20px;
                            border-radius: 8px; font-size: 14px; font-weight: 600;
                            display: inline-block; text-align: center; white-space: nowrap;">
                    🔵 {location_type}
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div style="background: #F59E0B; color: white; padding: 8px 20px;
                            border-radius: 8px; font-size: 14px; font-weight: 600;
                            display: inline-block; text-align: center; white-space: nowrap;">
                    🟡 {location_type}
                </div>
                """, unsafe_allow_html=True)

        with badge_cols[1]:
            # Cost badge - always second
            if 'Free' in simplified_cost:
                st.markdown("""
                <div style="background: linear-gradient(135deg, #FFD700 0%, #FFA500 100%);
                            color: #0A1628; padding: 8px 20px;
                            border-radius: 8px; font-size: 14px; font-weight: 700;
                            display: inline-block; text-align: center; white-space: nowrap;">
                    💎 FREE
                </div>
                """, unsafe_allow_html=True)
            elif 'Low Cost' in simplified_cost:
                st.markdown("""
                <div style="background: #10B981; color: white; padding: 8px 20px;
                            border-radius: 8px; font-size: 14px; font-weight: 600;
                            display: inline-block; text-align: center; white-space: nowrap;">
                    💵 Low
                </div>
                """, unsafe_allow_html=True)
            elif 'Medium Cost' in simplified_cost:
                st.markdown("""
                <div style="background: #F59E0B; color: white; padding: 8px 20px;
                            border-radius: 8px; font-size: 14px; font-weight: 600;
                            display: inline-block; text-align: center; white-space: nowrap;">
                    💰 Med
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div style="background: #EF4444; color: white; padding: 8px 20px;
                            border-radius: 8px; font-size: 14px; font-weight: 600;
                            display: inline-block; text-align: center; white-space: nowrap;">
                    💸 High
                </div>
                """, unsafe_allow_html=True)

        # Match badge - only if we have a match score
        if match_score != 'N/A' and not pd.isna(match_score):
            with badge_cols[2]:
                match_percent = float(match_score)
                if match_percent >= 80:
                    st.markdown(f"""
                    <div style="background: linear-gradient(135deg, #10B981 0%, #059669 100%);
                                color: white; padding: 8px 20px;
                                border-radius: 8px; font-size: 14px; font-weight: 700;
                                display: inline-block; text-align: center; white-space: nowrap;">
                        🌟 {match_percent:.0f}% Match
                    </div>
                    """, unsafe_allow_html=True)
                elif match_percent >= 60:
                    st.markdown(f"""
                    <div style="background: linear-gradient(135deg, #F59E0B 0%, #D97706 100%);
                                color: white; padding: 8px 20px;
                                border-radius: 8px; font-size: 14px; font-weight: 700;
                                display: inline-block; text-align: center; white-space: nowrap;">
                        ⭐ {match_percent:.0f}% Match
                    </div>
                    """, unsafe_allow_html=True)
                elif match_percent >= 40:
                    st.markdown(f"""
                    <div style="background: linear-gradient(135deg, #F97316 0%, #EA580C 100%);
                                color: white; padding: 8px 20px;
                                border-radius: 8px; font-size: 14px; font-weight: 700;
                                display: inline-block; text-align: center; white-space: nowrap;">
                        ✨ {match_percent:.0f}% Match
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div style="background: #6B7280; color: white; padding: 8px 20px;
                                border-radius: 8px; font-size: 14px; font-weight: 600;
                                display: inline-block; text-align: center; white-space: nowrap;">
                        ○ {match_percent:.0f}% Match
                    </div>
                    """, unsafe_allow_html=True)

            # Diversity badge in 4th column (when match exists)
            if diversity_badge:
                with badge_cols[3]:
                    st.markdown("""
                    <div style="background: #10B981; color: white; padding: 8px 20px;
                                border-radius: 8px; font-size: 14px; font-weight: 600;
                                display: inline-block; text-align: center; white-space: nowrap;">
                        🤝 Diversity
                    </div>
                    """, unsafe_allow_html=True)
        else:
            # No match score - diversity goes in 3rd column
            if diversity_badge:
                with badge_cols[2]:
                    st.markdown("""
                    <div style="background: #10B981; color: white; padding: 8px 20px;
                                border-radius: 8px; font-size: 14px; font-weight: 600;
                                display: inline-block; text-align: center; white-space: nowrap;">
                        🤝 Diversity
                    </div>
                    """, unsafe_allow_html=True)

        # Details in ONE HORIZONTAL ROW - LARGER font for better visibility
        # Display all 4 details side-by-side with separators
        grade = rec.get('target_grade', rec.get('target_grade_standardized', 'N/A'))
        category = rec.get('category', rec.get('category_tier1', 'N/A'))
        stem_field = rec.get('stem_field', rec.get('stem_field_tier1', 'N/A'))

        st.markdown(f"""
        <div style="font-size: 1.05rem; margin: 0.6rem 0; line-height: 1.5; font-weight: 500;">
            🎓 <strong>Grade:</strong> {grade} <span style="color: #666;">|</span>
            🏷️ <strong>Category:</strong> {category} <span style="color: #666;">|</span>
            🔬 <strong>STEM Field:</strong> {stem_field} <span style="color: #666;">|</span>
            {time_formatted}
        </div>
        """, unsafe_allow_html=True)

        # Description
        st.write(description_preview)

        # Warning about link verification
        st.markdown("""
        <div style="font-size: 0.75rem; color: #80C0E0; margin-top: 0.5rem; margin-bottom: 0.8rem;">
            ⚠️ Note: External links verified Oct 2025. Use 'Search Google' button if link doesn't work.
        </div>
        """, unsafe_allow_html=True)

        # Primary action buttons (Row 1) - ALL same size, ALL electric blue
        # Centered layout with equal column widths
        col_spacer1, col_btn1, col_btn2, col_btn3, col_spacer2 = st.columns([0.5, 2, 2, 2, 0.5])

        with col_btn1:
            if st.button("👁️ View Details", key=f"view_{rank}_{rec.get('name', 'unknown')[:20]}", use_container_width=True):
                # Track modal opens
                log_usage('modal_opened', {
                    'resource_name': rec.get('name', 'Unknown'),
                    'resource_category': rec.get('category', rec.get('category_tier1', 'N/A')),
                    'rank': rank
                })
                show_resource_preview(rec)

        with col_btn2:
            url = rec.get('url', '#')
            if url and url != '#' and not pd.isna(url):
                if st.button("🔗 Visit Website", key=f"visit_{rank}_{rec.get('name', 'unknown')[:20]}", use_container_width=True):
                    # Track external link clicks
                    log_usage('external_link_clicked', {
                        'resource_name': rec.get('name', 'Unknown'),
                        'resource_url': url,
                        'rank': rank
                    })
                    # Open link in new tab
                    st.markdown(f'<meta http-equiv="refresh" content="0;url={url}" target="_blank">', unsafe_allow_html=True)
            else:
                st.button("🔗 Visit Website", disabled=True, use_container_width=True, key=f"visit_disabled_{rank}")

        with col_btn3:
            if show_save_button:
                # Check if resource is saved
                resource_id = f"{rec.get('name', '')}_{rec.get('url', '')}"
                is_saved = any(saved.get('id') == resource_id for saved in st.session_state['saved_resources'])

                if is_saved:
                    if st.button("❤️ Saved", key=f"unsave_{rank}_{resource_id[:20]}", use_container_width=True, help="Remove from saved"):
                        # Remove from saved
                        st.session_state['saved_resources'] = [
                            saved for saved in st.session_state['saved_resources']
                            if saved.get('id') != resource_id
                        ]
                        log_usage('resource_unsaved', {'resource_name': rec.get('name', 'Unknown')})
                        st.rerun()
                else:
                    if st.button("♡ Save", key=f"save_{rank}_{resource_id[:20]}", use_container_width=True, help="Save for later"):
                        # Add to saved
                        saved_resource = rec.to_dict() if hasattr(rec, 'to_dict') else dict(rec)
                        saved_resource['id'] = resource_id
                        saved_resource['saved_at'] = datetime.now().isoformat()
                        st.session_state['saved_resources'].append(saved_resource)
                        log_usage('resource_saved', {'resource_name': rec.get('name', 'Unknown')})
                        st.rerun()

        # Voting section (Row 2) - centered with vote count
        resource_id = f"{rec.get('name', '')}_{rec.get('url', '')}"
        helpful_count = st.session_state['vote_counts'].get(resource_id, 0)

        # Small spacing before vote section
        st.markdown('<div style="margin-top: 0.8rem;"></div>', unsafe_allow_html=True)

        # Display vote count centered
        if helpful_count > 0:
            st.markdown(f"""
            <div style="font-size: 0.85rem; color: #B0E0FF; text-align: center; margin-bottom: 0.5rem;">
                👍 {helpful_count} student{'s' if helpful_count != 1 else ''} found this helpful
            </div>
            """, unsafe_allow_html=True)

        # Voting buttons (Row 2) - ALL same size, ALL electric blue, centered
        col_vote_spacer1, col_vote1, col_vote2, col_vote_spacer2 = st.columns([2, 2, 2, 2])

        with col_vote1:
            if resource_id not in st.session_state['voted_resources']:
                if st.button("👍 Helpful", key=f"helpful_{rank}_{resource_id[:15]}", use_container_width=True):
                    save_resource_vote(resource_id, rec.get('name', 'Unknown'), 'helpful')
                    st.session_state['voted_resources'].add(resource_id)
                    # Reload vote counts
                    st.session_state['vote_counts'] = load_resource_votes()
                    log_usage('resource_voted', {'resource_name': rec.get('name', 'Unknown'), 'vote': 'helpful'})
                    st.rerun()
            else:
                st.button("👍 Helpful", key=f"helpful_{rank}_{resource_id[:15]}", disabled=True, use_container_width=True)

        with col_vote2:
            if resource_id not in st.session_state['voted_resources']:
                if st.button("👎 Not Helpful", key=f"not_helpful_{rank}_{resource_id[:15]}", use_container_width=True):
                    save_resource_vote(resource_id, rec.get('name', 'Unknown'), 'not_helpful')
                    st.session_state['voted_resources'].add(resource_id)
                    log_usage('resource_voted', {'resource_name': rec.get('name', 'Unknown'), 'vote': 'not_helpful'})
                    st.rerun()
            else:
                st.button("👎 Not Helpful", key=f"not_helpful_{rank}_{resource_id[:15]}", disabled=True, use_container_width=True)


    # Container automatically closes - all content now properly inside bordered container


def display_logo():
    """Display the BMIS logo at the top of the page, centered"""
    try:
        logo_path = Path(__file__).parent / 'assets' / 'BMIS Logo.png'
        if logo_path.exists():
            # Center logo using CSS
            st.markdown("""
            <div style="display: flex; justify-content: center; align-items: center; margin-bottom: 1rem;">
                <img src="data:image/png;base64,{}" width="200" style="display: block;">
            </div>
            """.format(
                __import__('base64').b64encode(open(str(logo_path), 'rb').read()).decode()
            ), unsafe_allow_html=True)
    except Exception:
        # Silently fail if logo can't be loaded
        pass


def apply_percentile_ranking(recommendations_df):
    """
    Transform similarity scores to percentile-based match percentages.

    For each user's recommendations:
    - Rank resources by similarity score (highest to lowest)
    - Assign match percentages based on ranking:
      - Rank 1-4 (top 20%): 85-95% match
      - Rank 5-8 (next 20%): 75-84% match
      - Rank 9-14 (next 30%): 60-74% match
      - Rank 15-20 (bottom 30%): 45-59% match

    Args:
        recommendations_df: DataFrame with similarity_score column

    Returns:
        DataFrame with new match_percentage column
    """
    if len(recommendations_df) == 0:
        return recommendations_df

    # Create a copy to avoid modifying original
    df = recommendations_df.copy()

    # Sort by similarity score descending
    df['rank'] = df['similarity_score'].rank(method='first', ascending=False)

    # Assign match percentages based on rank
    def assign_match_percentage(rank, total_count):
        rank = int(rank)

        if rank <= 4:
            # Top 20%: 85-95%
            # Rank 1 = 95%, Rank 2 = 92%, Rank 3 = 88%, Rank 4 = 85%
            percentages = [95, 92, 88, 85]
            return percentages[min(rank-1, 3)]
        elif rank <= 8:
            # Next 20%: 75-84%
            # Rank 5 = 84%, Rank 6 = 81%, Rank 7 = 78%, Rank 8 = 75%
            percentages = [84, 81, 78, 75]
            return percentages[min(rank-5, 3)]
        elif rank <= 14:
            # Next 30%: 60-74%
            # Distribute evenly: 74, 72, 70, 67, 64, 60
            percentages = [74, 72, 70, 67, 64, 60]
            return percentages[min(rank-9, 5)]
        else:
            # Bottom 30%: 45-59%
            # Distribute evenly: 59, 56, 53, 50, 47, 45
            percentages = [59, 56, 53, 50, 47, 45]
            idx = min(rank-15, 5)
            return percentages[idx]

    df['match_percentage'] = df['rank'].apply(lambda r: assign_match_percentage(r, len(df)))

    # Keep original similarity_score and add match_percentage
    return df


def format_match_score(match_percentage):
    """
    Convert match percentage to colored badge.

    Args:
        match_percentage: Float between 0 and 100, or 'N/A'

    Returns:
        HTML string with colored badge
    """
    if match_percentage == 'N/A' or pd.isna(match_percentage):
        return '<span class="badge-match-low">N/A</span>'

    try:
        # Use percentage directly
        percentage = float(match_percentage)

        # Determine badge class and icon based on percentage
        if percentage >= 80:
            badge_class = "badge-match-excellent"
            icon = "🌟"
        elif percentage >= 60:
            badge_class = "badge-match-good"
            icon = "⭐"
        elif percentage >= 40:
            badge_class = "badge-match-fair"
            icon = "✨"
        else:
            badge_class = "badge-match-low"
            icon = "○"

        return f'<span class="{badge_class}">{icon} {percentage:.0f}% Match</span>'
    except (ValueError, TypeError):
        return '<span class="badge-match-low">N/A</span>'


def render_home_tab():
    """Render the home/welcome tab"""
    display_logo()
    st.markdown('<div class="main-header">🧠 Black Minds in STEM</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">AI-Powered STEM Discovery Platform for Black Students</div>', unsafe_allow_html=True)
    st.markdown('<div class="tagline">"Finding STEM opportunities shouldn\'t be this hard."</div>', unsafe_allow_html=True)
    st.markdown('<div class="tagline">BMIS uses machine learning to match you with scholarships, programs, and resources designed for students like you.</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Feature columns
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        <div class="feature-box">
            <div class="feature-icon">📚</div>
            <div class="feature-title">2,200+ Resources</div>
            <div class="feature-text">Curated database of STEM opportunities</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="feature-box">
            <div class="feature-icon">🎯</div>
            <div class="feature-title">Personalized Matching</div>
            <div class="feature-text">AI-powered recommendations just for you</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div class="feature-box">
            <div class="feature-icon">💰</div>
            <div class="feature-title">Affordable Options</div>
            <div class="feature-text">Free and low-cost programs prioritized</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br><br>", unsafe_allow_html=True)

    # Get Started button with hover effect - Target Streamlit's button directly
    st.markdown("""<style>
    /* Target Get Started button specifically using aggressive selectors */
    div.stButton > button[data-testid="baseButton-secondary"] {
        transition: transform 0.3s ease, box-shadow 0.3s ease !important;
    }

    div.stButton > button[data-testid="baseButton-secondary"]:hover {
        transform: scale(1.05) !important;
        box-shadow: 0 8px 20px rgba(0, 217, 255, 0.5) !important;
        cursor: pointer !important;
    }

    /* Also target by primary type */
    div.stButton > button[kind="primary"] {
        transition: transform 0.3s ease, box-shadow 0.3s ease !important;
    }

    div.stButton > button[kind="primary"]:hover {
        transform: scale(1.05) !important;
        box-shadow: 0 8px 20px rgba(0, 217, 255, 0.5) !important;
        cursor: pointer !important;
    }
    </style>""", unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("🚀 Get Started", use_container_width=True, key="get_started_btn", type="primary"):
            st.session_state['current_tab'] = "🎯 Get Recommendations"  # Switch to Get Recommendations tab
            st.rerun()

    st.markdown("<br><br>", unsafe_allow_html=True)

    # Why BMIS Matters Section - Redesigned with authentic messaging
    st.markdown("""
    <div style="background: linear-gradient(135deg, rgba(0, 217, 255, 0.1) 0%, rgba(0, 153, 204, 0.05) 100%);
                border: 1px solid rgba(0, 217, 255, 0.3); border-radius: 12px;
                padding: 2.5rem; margin: 2rem auto; max-width: 1200px;">
        <h2 style="color: #00D9FF; text-align: center; margin-bottom: 1rem; font-size: 2rem;">Why BMIS Matters</h2>
        <p style="color: #B0E0FF; text-align: center; font-size: 1.2rem; margin-bottom: 2.5rem; line-height: 1.6;">
            Searching Google for hours. Opening 47 tabs. Still not sure which programs fit your budget or schedule.
        </p>
    """, unsafe_allow_html=True)

    col_problem, col_solution = st.columns(2, gap="large")

    with col_problem:
        st.markdown("""
        <div style="padding: 1.2rem; height: 100%;">
            <h3 style="color: #00D9FF; margin-bottom: 1.2rem; font-size: 1.4rem; border-bottom: 2px solid rgba(0, 217, 255, 0.3); padding-bottom: 0.5rem;">The Problem</h3>
            <div style="color: #B0E0FF; line-height: 1.7; font-size: 1.05rem;">
                <p style="margin-bottom: 1rem;">You're talented. You're motivated. But there are <strong style="color: #00D9FF;">2,200+ STEM programs</strong> out there, and most weren't designed with you in mind.</p>
                <p style="margin-bottom: 1rem;">Some cost thousands. Some are hours away. Some assume you have a car, a college counselor, or parents who navigated this before.</p>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col_solution:
        st.markdown("""
        <div style="padding: 1.2rem; height: 100%;">
            <h3 style="color: #00D9FF; margin-bottom: 1.2rem; font-size: 1.4rem; border-bottom: 2px solid rgba(0, 217, 255, 0.3); padding-bottom: 0.5rem;">What BMIS Does</h3>
            <div style="color: #B0E0FF; line-height: 1.7; font-size: 1.05rem;">
                <p style="margin-bottom: 0.8rem;">🎯 Matches based on <strong style="color: #00D9FF;">YOUR</strong> situation—budget, location, grade, interests</p>
                <p style="margin-bottom: 0.8rem;">💰 Prioritizes accessible options (80% of recommendations are free/low-cost)</p>
                <p style="margin-bottom: 0.8rem;">👥 Real students sharing real experiences about programs</p>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Bottom stat centered
    st.markdown("""
        <div style="text-align: center; margin-top: 2rem; padding-top: 1.5rem; border-top: 1px solid rgba(0, 217, 255, 0.2);">
            <p style="color: #B0E0FF; font-size: 1.05rem; line-height: 1.6;">
                The gap in STEM isn't about talent. It's about access to information.<br>
                Black students: 13% of US population, only <strong style="color: #00D9FF; font-size: 1.3rem;">9%</strong> of STEM graduates.
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Quick Stats Section
    try:
        dataset_path = Path(__file__).parent / 'data' / 'bmis_final_ml_ready_dataset_cs_refined.csv'
        if dataset_path.exists():
            stats_df = pd.read_csv(dataset_path)

            total_resources = len(stats_df)
            free_low_cost = len(stats_df[stats_df['financial_barrier'].isin(['Free', 'Low'])])
            virtual_resources = len(stats_df[stats_df['location_type'].str.contains('Virtual|Online', case=False, na=False)])
            scholarships = len(stats_df[stats_df['category'].str.contains('Scholarship', case=False, na=False)])

            st.markdown("""
            <div style="background: rgba(0, 217, 255, 0.08); border: 1px solid rgba(0, 217, 255, 0.3); border-radius: 12px; padding: 2rem; margin: 2rem 0;">
            """, unsafe_allow_html=True)

            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.markdown(f"""
                <div style="text-align: center;">
                    <div style="font-size: 3rem;">📚</div>
                    <div style="font-size: 2.5rem; font-weight: 900; color: #00D9FF; margin: 0.5rem 0;">{total_resources:,}</div>
                    <div style="color: #B0E0FF; font-size: 0.95rem;">Total Resources</div>
                </div>
                """, unsafe_allow_html=True)

            with col2:
                st.markdown(f"""
                <div style="text-align: center;">
                    <div style="font-size: 3rem;">💰</div>
                    <div style="font-size: 2.5rem; font-weight: 900; color: #00D9FF; margin: 0.5rem 0;">{free_low_cost:,}</div>
                    <div style="color: #B0E0FF; font-size: 0.95rem;">Free/Low-Cost</div>
                </div>
                """, unsafe_allow_html=True)

            with col3:
                st.markdown(f"""
                <div style="text-align: center;">
                    <div style="font-size: 3rem;">🌐</div>
                    <div style="font-size: 2.5rem; font-weight: 900; color: #00D9FF; margin: 0.5rem 0;">{virtual_resources:,}</div>
                    <div style="color: #B0E0FF; font-size: 0.95rem;">Virtual Options</div>
                </div>
                """, unsafe_allow_html=True)

            with col4:
                st.markdown(f"""
                <div style="text-align: center;">
                    <div style="font-size: 3rem;">🎓</div>
                    <div style="font-size: 2.5rem; font-weight: 900; color: #00D9FF; margin: 0.5rem 0;">{scholarships:,}</div>
                    <div style="color: #B0E0FF; font-size: 0.95rem;">Scholarships</div>
                </div>
                """, unsafe_allow_html=True)

            st.markdown("</div>", unsafe_allow_html=True)
    except Exception:
        # Silently fail if stats can't be calculated
        pass

    st.markdown("<br>", unsafe_allow_html=True)

    # How it works
    st.markdown("""
    <div class="info-box">
        <h2 style="color: #00D9FF; margin-bottom: 1.5rem;">How It Works</h2>
    """, unsafe_allow_html=True)

    st.markdown("""
        <div style="margin: 1.5rem 0;">
            <span class="step-number">1</span>
            <span class="step-text"><strong>Tell us about yourself</strong> - Share your interests, grade level, and circumstances (2 minutes)</span>
        </div>
        <div style="margin: 1.5rem 0;">
            <span class="step-number">2</span>
            <span class="step-text"><strong>Get personalized recommendations</strong> - Receive up to 20 AI-matched STEM opportunities</span>
        </div>
        <div style="margin: 1.5rem 0;">
            <span class="step-number">3</span>
            <span class="step-text"><strong>Apply, save, and succeed</strong> - Explore programs and take action on your future</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # What makes us different
    st.markdown("""
    <div class="info-box">
        <h2 style="color: #00D9FF; margin-bottom: 1rem;">What Makes Us Different</h2>
        <ul style="color: #B0E0FF; font-size: 1rem; line-height: 2;">
            <li><strong style="color: #00D9FF;">Accessibility-first:</strong> We prioritize free and low-cost resources for students with limited budgets</li>
            <li><strong style="color: #00D9FF;">Context-aware:</strong> Recommendations consider your location, transportation, and time availability</li>
            <li><strong style="color: #00D9FF;">Diverse options:</strong> From scholarships to competitions to research opportunities</li>
            <li><strong style="color: #00D9FF;">Powered by AI:</strong> Machine learning models trained on 2,200+ STEM resources</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

    # FAQ Section
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("""
    <div class="info-box">
        <h2 style="color: #00D9FF; margin-bottom: 1.5rem;">Frequently Asked Questions</h2>
    </div>
    """, unsafe_allow_html=True)

    with st.expander("❓ Is BMIS really free?"):
        st.markdown("""
        Yes! BMIS is completely free to use. We don't charge students anything to access our recommendation
        system or browse resources. Some of the resources we recommend may have costs, but we prioritize
        free and low-cost options, especially for students with limited budgets.
        """)

    with st.expander("🤖 How does the matching algorithm work?"):
        st.markdown("""
        BMIS uses machine learning to match you with relevant STEM resources. We use:
        - **K-Means clustering** to group resources by accessibility, academic level, format, and stem discipline
        - **TF-IDF similarity scoring** to match your interests with resource descriptions
        - Your profile information (grade, budget, location) to personalize recommendations

        The match percentage shows how closely a resource aligns with your profile.
        """)

    with st.expander("✅ Can I trust these resources?"):
        st.markdown("""
        All resources in BMIS are curated from official sources including:
        - Government programs (NSF, NASA, NIH)
        - Established organizations (NSBE)
        - Accredited universities
        - Verified STEM education nonprofits

        We verify links regularly, but organizations sometimes change URLs or end programs.
        If you find a broken link, please use the "Report a Problem" button.
        """)

    with st.expander("🔗 What if a link doesn't work?"):
        st.markdown("""
        Click the **"Report a Problem"** button at the bottom of any page and let us know!
        We review all reports and update broken links as quickly as possible. You can
        also try searching for the program name directly on Google to find the updated URL.
        """)

    with st.expander("👥 Who can use BMIS?"):
        st.markdown("""
        BMIS is designed for Black students (grades K-12) interested in STEM fields.
        However, anyone can use the platform to search for STEM opportunities. We focus
        on resources that are accessible to underrepresented students and consider factors
        like financial barriers and location.
        """)

    with st.expander("🔄 How often is the database updated?"):
        st.markdown("""
        We continuously add new resources and verify existing links. The database currently
        contains 2,200+ resources updated as of October 2025. Resources with past deadlines
        are kept in the database for reference and may be available again in future years.
        """)

    with st.expander("💡 Can I suggest a resource to add?"):
        st.markdown("""
        Yes! Use the **"Report a Problem"** form and select "Other" to suggest new resources.
        Include the resource name, URL, and why you think it would be valuable for Black
        students in STEM.
        """)

    # Privacy note
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""
    <div style="text-align: center; margin-top: 3rem; color: #80C0E0; font-size: 0.85rem;">
        🔒 Your privacy matters. We collect anonymous usage data to improve the platform. No personal information is stored.
    </div>
    """, unsafe_allow_html=True)

    # Footer with Report a Problem button
    render_footer()


def render_recommendations_tab():
    """Render the Get Recommendations tab"""
    display_logo()
    st.markdown('<div class="main-header">🎯 Get Your Recommendations</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Tell us about yourself to receive personalized STEM opportunities</div>', unsafe_allow_html=True)

    # Profile form
    with st.form("profile_form"):
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("#### 📋 Personal Information")
            # K-12 grade level with mapping
            grade_options = {
                'Kindergarten (K)': 0,
                'Grade 1': 1,
                'Grade 2': 2,
                'Grade 3': 3,
                'Grade 4': 4,
                'Grade 5': 5,
                'Grade 6': 6,
                'Grade 7': 7,
                'Grade 8': 8,
                'Grade 9': 9,
                'Grade 10': 10,
                'Grade 11': 11,
                'Grade 12': 12
            }

            grade_selection = st.selectbox(
                "Grade Level",
                options=list(grade_options.keys()),
                index=9,  # Default to Grade 9
                help="Select your current grade level"
            )
            grade_level = grade_options[grade_selection]

            financial_situation = st.selectbox(
                "Financial Situation",
                options=["Low", "Medium", "High"],
                help="Low: Limited budget\nMedium: Some budget\nHigh: Cost not a concern"
            )

            location = st.selectbox(
                "Attendance Preference",
                options=["Virtual", "In-person", "Hybrid", "No preference"],
                help="Virtual: Online only\nIn-person: Physical location\nHybrid: Either works"
            )

            transportation = st.checkbox(
                "I have reliable transportation",
                value=False
            )

        with col2:
            st.markdown("#### 🎓 Academic Background")

            academic_level = st.selectbox(
                "Academic Level",
                options=["Beginner", "Intermediate", "Advanced"],
                index=1
            )

            time_availability = st.slider(
                "Time Available (hours/week)",
                min_value=0,
                max_value=40,
                value=10,
                step=1
            )

            support_needed = st.selectbox(
                "Support/Mentorship Needed",
                options=["Low", "Medium", "High"],
                index=1
            )

        st.markdown("#### 🔬 STEM Interests")

        stem_interests = st.text_area(
            "Describe your STEM interests",
            placeholder="e.g., machine learning, biology research, robotics, environmental science...",
            help="Be specific! Mention topics, technologies, or areas you're passionate about."
        )

        stem_fields = st.multiselect(
            "Select STEM Fields (up to 5)",
            options=[
                "Artificial Intelligence/Machine Learning",
                "Biology",
                "Biomedical Sciences",
                "Chemistry",
                "Computer Science",
                "Cybersecurity",
                "Data Science",
                "Earth Sciences",
                "Engineering",
                "Environmental Science",
                "Game Design",
                "Mathematics",
                "Physics",
                "Robotics",
                "Software Engineering",
                "Web Development",
                "Other STEM"
            ],
            max_selections=5
        )

        format_preferences = st.multiselect(
            "Preferred Resource Types (up to 5)",
            options=[
                "Online Course",
                "Learning Platform",
                "Summer Program",
                "Research Opportunity",
                "Competition",
                "Scholarship",
                "Internship",
                "Mentorship Program",
                "Workshop/Training",
                "Camp",
                "Bootcamp"
            ],
            max_selections=5
        )

        submit_button = st.form_submit_button("🚀 Get My Recommendations", use_container_width=True)

    # Process form submission
    if submit_button:
        # Validate inputs
        if not stem_interests.strip():
            st.error("⚠️ Please describe your STEM interests to get personalized recommendations.")
            st.stop()

        if not stem_fields:
            st.error("⚠️ Please select at least one STEM field.")
            st.stop()

        # Build profile
        student_profile = {
            'financial_situation': financial_situation,
            'location': location,
            'transportation_available': transportation,
            'grade_level': grade_level,
            'academic_level': academic_level,
            'time_availability': time_availability,
            'support_needed': support_needed,
            'stem_interests': stem_interests,
            'stem_fields': stem_fields,
            'format_preferences': format_preferences if format_preferences else []
        }

        # Generate recommendations
        with st.spinner("🔄 Analyzing your profile and matching with 2,200+ resources..."):
            try:
                engine = load_recommendation_engine()
                recommendations = engine.get_recommendations(
                    student_profile,
                    top_n=20,
                    min_similarity=0.2,
                    top_clusters=5
                )

                # Handle zero results with fallback logic
                is_relaxed_search = False
                relaxation_method = None

                if len(recommendations) == 0:
                    is_relaxed_search = True
                    relaxation_method = "Broadened search criteria"

                    # Try relaxed search - lower similarity threshold
                    recommendations = engine.get_recommendations(
                        student_profile,
                        top_n=20,
                        min_similarity=0.1,  # Lower threshold
                        top_clusters=10  # More clusters
                    )

                    # If still no results, get top resources from dataset based on grade/location only
                    if len(recommendations) == 0:
                        dataset_path = Path(__file__).parent / 'data' / 'bmis_final_ml_ready_dataset_cs_refined.csv'
                        if dataset_path.exists():
                            all_resources = pd.read_csv(dataset_path)

                            # Filter by location if specified
                            if student_profile['location'] != "No preference":
                                location_match = all_resources[
                                    all_resources['location_type'].str.contains(
                                        student_profile['location'], case=False, na=False
                                    )
                                ]
                                if len(location_match) > 0:
                                    recommendations = location_match.head(20)
                                    relaxation_method = f"Showing resources matching your location preference"
                                else:
                                    recommendations = all_resources.head(20)
                                    relaxation_method = "Showing top resources from our database"
                            else:
                                recommendations = all_resources.head(20)
                                relaxation_method = "Showing top resources from our database"

                            # Add a dummy similarity score for display
                            recommendations['similarity_score'] = 0.3

                # Apply percentile ranking transformation
                if len(recommendations) > 0:
                    recommendations = apply_percentile_ranking(recommendations)

                # Log analytics (anonymous)
                log_usage('search', {
                    'grade_level': grade_level,
                    'financial_situation': financial_situation,
                    'location': location,
                    'num_stem_fields': len(stem_fields),
                    'num_format_prefs': len(format_preferences),
                    'num_results': len(recommendations),
                    'is_relaxed_search': is_relaxed_search
                })

                # Store in session state
                st.session_state['recommendations'] = recommendations
                st.session_state['student_grade'] = grade_level
                st.session_state['profile_submitted'] = True
                st.session_state['is_relaxed_search'] = is_relaxed_search
                st.session_state['relaxation_method'] = relaxation_method

                if is_relaxed_search and len(recommendations) > 0:
                    st.markdown(f"""
                    <div class="warning-box">
                        🔍 <strong>No Perfect Matches Found</strong><br><br>
                        We couldn't find resources that exactly match all your criteria, but here are some options you might be interested in.<br>
                        <em>{relaxation_method}</em>
                    </div>
                    """, unsafe_allow_html=True)

                    st.markdown("""
                    <div class="info-box">
                        <strong style="color: #00D9FF;">💡 Tips for Better Matches:</strong><br>
                        • Try selecting "No preference" for location<br>
                        • Broaden your STEM interests (add more fields)<br>
                        • Adjust your budget filter if too restrictive<br>
                        • Consider different resource types
                    </div>
                    """, unsafe_allow_html=True)

                    col1, col2, col3 = st.columns([1, 1, 1])
                    with col2:
                        if st.button("🔄 Adjust My Profile", use_container_width=True, key="adjust_profile_btn"):
                            st.session_state['profile_submitted'] = False
                            st.rerun()

                    st.markdown("<br>", unsafe_allow_html=True)
                elif len(recommendations) > 0:
                    st.success(f"✅ Found {len(recommendations)} personalized recommendations!")
                else:
                    st.error("❌ No resources found. Please try adjusting your search criteria.")

            except Exception as e:
                st.error(f"❌ Error generating recommendations: {str(e)}")
                st.error("Please try again. If the problem persists, please report this issue.")
                st.stop()

    # Display recommendations if available
    if st.session_state.get('profile_submitted', False) and 'recommendations' in st.session_state:
        recommendations = st.session_state['recommendations']
        student_grade = st.session_state['student_grade']

        st.markdown("<br>", unsafe_allow_html=True)

        # Info box
        st.markdown("""
        <div class="info-box">
            <strong style="color: #00D9FF; font-size: 1.1rem;">ℹ️ About Your Recommendations</strong><br><br>
            These are personalized suggestions based on your profile. Use the filters below to refine results by location or grade level.
            Always review program requirements before applying.
        </div>
        """, unsafe_allow_html=True)

        # Filters
        col1, col2 = st.columns(2)

        with col1:
            location_filter = st.selectbox(
                "📍 Filter by Attendance Type",
                options=[
                    "Show All",
                    "Virtual/Online Only",
                    "In-Person Only",
                    "Hybrid (Virtual + In-Person)"
                ],
                key="location_filter"
            )

        with col2:
            grade_filter = st.selectbox(
                "🎓 Filter by Grade Level",
                options=[
                    "Show All",
                    "My Grade Level Only",
                    "My Grade ±1 Year",
                    "My Grade ±2 Years",
                    "Elementary (K-5)",
                    "Middle School (6-8)",
                    "High School (9-12)"
                ],
                key="grade_filter"
            )

        # Apply filters
        filtered_recs = filter_recommendations(
            recommendations,
            location_filter,
            grade_filter,
            student_grade
        )

        # Filter info
        total_recs = len(recommendations)
        filtered_count = len(filtered_recs)

        if location_filter != "Show All" or grade_filter != "Show All":
            if filtered_count > 0:
                st.markdown(f"""
                <div class="success-box">
                    ✅ <strong>Showing {filtered_count} of {total_recs} resources</strong> matching your filters.
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div class="warning-box">
                    ⚠️ <strong>No resources match your current filters.</strong> Try "Show All" or adjust your filters.
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="success-box">
                📊 <strong>Showing all {total_recs} recommendations.</strong> Use filters above to narrow results.
            </div>
            """, unsafe_allow_html=True)

        # Display filtered recommendations
        if filtered_count > 0:
            st.markdown("### 📚 Your Personalized Recommendations")

            with st.container(border=True):
                for idx, (_, rec) in enumerate(filtered_recs.iterrows(), 1):
                    display_recommendation_card(rec, idx)

        # Export option
        if filtered_count > 0:
            st.markdown("---")
            st.markdown("### 💾 Export Your Recommendations")

            csv = filtered_recs.to_csv(index=False)
            st.download_button(
                label="📥 Download as CSV",
                data=csv,
                file_name="bmis_recommendations.csv",
                mime="text/csv",
                use_container_width=True
            )

    # Footer with Report a Problem button
    render_footer()


def render_browse_tab():
    """Render the Browse All Resources tab"""
    display_logo()
    st.markdown('<div class="main-header">🔍 Browse All Resources</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Search and explore our complete database of 2,200+ STEM opportunities</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Load dataset
    try:
        dataset_path = Path(__file__).parent / 'data' / 'bmis_final_ml_ready_dataset_cs_refined.csv'
        if not dataset_path.exists():
            st.error("❌ Resource database not found. Please contact support.")
            st.stop()

        all_resources = pd.read_csv(dataset_path)

        # Search bar with button
        col_search, col_button = st.columns([4, 1])

        with col_search:
            search_query = st.text_input(
                "🔎 Search resources",
                placeholder="Search by keyword (press Enter or click Search)",
                help="Search across all resource fields",
                key="browse_search_input"
            )

        with col_button:
            st.markdown("<br>", unsafe_allow_html=True)  # Align with text input
            search_button = st.button("🔍 Search", use_container_width=True, key="browse_search_btn")

        # Filters (simplified with curated options)
        col1, col2, col3 = st.columns(3)

        with col1:
            # Simplified category filter - only 7 main categories
            category_options = [
                "Scholarship",
                "Summer Program",
                "Competition",
                "Online Course",
                "Research Opportunity",
                "Camp",
                "Internship"
            ]
            category_filter = st.multiselect(
                "Category",
                options=category_options,
                help="Filter by resource category"
            )

        with col2:
            field_filter = st.multiselect(
                "STEM Field",
                options=sorted(all_resources['stem_field_tier1'].dropna().unique()) if 'stem_field_tier1' in all_resources.columns else [],
                help="Filter by STEM field"
            )

        with col3:
            cost_filter = st.multiselect(
                "Cost",
                options=['Free ($0)', 'Low Cost ($1-$500)', 'Medium Cost ($501-$2K)', 'High Cost ($2K+)'],
                help="Filter by cost range - select one or more options"
            )

        col4, col5 = st.columns(2)

        with col4:
            # Simplified location filter - only 3 options
            location_options = [
                "Virtual",
                "In-person",
                "Hybrid"
            ]
            location_filter = st.multiselect(
                "Attendance Type",
                options=location_options,
                help="Filter by attendance type (Virtual, In-person, Hybrid)"
            )

        with col5:
            sort_by = st.selectbox(
                "Sort by",
                options=["Name (A-Z)", "Name (Z-A)", "Category", "Cost (Low to High)"],
                index=0
            )

        # Apply filters with proper index management
        filtered_resources = all_resources.copy()
        filtered_resources = filtered_resources.reset_index(drop=True)

        # Add simplified cost category column for filtering
        filtered_resources['simplified_cost'] = filtered_resources.apply(
            lambda row: get_simplified_cost_category(
                row.get('financial_barrier_level'),
                row.get('cost_category')
            ), axis=1
        )

        if search_query:
            search_cols = ['name', 'description', 'stem_field_tier1', 'category']
            mask = pd.Series([False] * len(filtered_resources))
            for col in search_cols:
                if col in filtered_resources.columns:
                    mask |= filtered_resources[col].astype(str).str.contains(search_query, case=False, na=False)
            filtered_resources = filtered_resources[mask].reset_index(drop=True)

            # Log search
            log_usage('browse_search', {'query': search_query, 'results': len(filtered_resources)})

        if category_filter:
            # Use case-insensitive partial matching for categories
            filtered_resources = filtered_resources.reset_index(drop=True)
            category_mask = pd.Series([False] * len(filtered_resources))
            for cat in category_filter:
                category_mask |= filtered_resources['category'].astype(str).str.contains(cat, case=False, na=False)
            filtered_resources = filtered_resources[category_mask].reset_index(drop=True)
            # Track filter usage
            log_usage('filter_applied', {
                'filter_type': 'category',
                'filter_values': category_filter,
                'results': len(filtered_resources)
            })

        if field_filter:
            filtered_resources = filtered_resources.reset_index(drop=True)
            mask = filtered_resources['stem_field_tier1'].isin(field_filter)
            filtered_resources = filtered_resources[mask].reset_index(drop=True)
            # Track filter usage
            log_usage('filter_applied', {
                'filter_type': 'stem_field',
                'filter_values': field_filter,
                'results': len(filtered_resources)
            })

        if cost_filter:
            filtered_resources = filtered_resources.reset_index(drop=True)
            mask = filtered_resources['simplified_cost'].isin(cost_filter)
            filtered_resources = filtered_resources[mask].reset_index(drop=True)
            # Track filter usage
            log_usage('filter_applied', {
                'filter_type': 'cost',
                'filter_values': cost_filter,
                'results': len(filtered_resources)
            })

        if location_filter:
            # Use case-insensitive partial matching for location
            filtered_resources = filtered_resources.reset_index(drop=True)
            location_mask = pd.Series([False] * len(filtered_resources))
            for loc in location_filter:
                location_mask |= filtered_resources['location_type'].astype(str).str.contains(loc, case=False, na=False)
            filtered_resources = filtered_resources[location_mask].reset_index(drop=True)
            # Track filter usage
            log_usage('filter_applied', {
                'filter_type': 'location',
                'filter_values': location_filter,
                'results': len(filtered_resources)
            })

        # Apply sorting
        if sort_by == "Name (A-Z)":
            filtered_resources = filtered_resources.sort_values('name')
        elif sort_by == "Name (Z-A)":
            filtered_resources = filtered_resources.sort_values('name', ascending=False)
        elif sort_by == "Category":
            filtered_resources = filtered_resources.sort_values('category')
        elif sort_by == "Cost (Low to High)":
            cost_order = {'Free': 0, 'Low': 1, 'Medium': 2, 'High': 3}
            if 'financial_barrier' in filtered_resources.columns:
                filtered_resources['sort_key'] = filtered_resources['financial_barrier'].map(cost_order).fillna(999)
                filtered_resources = filtered_resources.sort_values('sort_key')
                filtered_resources = filtered_resources.drop('sort_key', axis=1)

        # Display results count
        st.markdown(f"""
        <div class="success-box">
            📊 <strong>Showing {len(filtered_resources):,} of {len(all_resources):,} resources</strong>
        </div>
        """, unsafe_allow_html=True)

        # Display resources
        if len(filtered_resources) > 0:
            # Pagination
            results_per_page = 20
            total_pages = (len(filtered_resources) - 1) // results_per_page + 1

            if 'browse_page' not in st.session_state:
                st.session_state['browse_page'] = 1

            start_idx = (st.session_state['browse_page'] - 1) * results_per_page
            end_idx = start_idx + results_per_page

            # Display current page
            page_resources = filtered_resources.iloc[start_idx:end_idx]

            with st.container(border=True):
                for idx, (_, resource) in enumerate(page_resources.iterrows(), start=start_idx + 1):
                    # Add temporary similarity score for display
                    resource_with_score = resource.copy()
                    resource_with_score['similarity_score'] = 'N/A'
                    display_recommendation_card(resource_with_score, idx)

            # Pagination controls
            if total_pages > 1:
                st.markdown("<br>", unsafe_allow_html=True)
                col1, col2, col3, col4, col5 = st.columns([1, 1, 2, 1, 1])

                with col1:
                    if st.button("⬅️ Previous", disabled=(st.session_state['browse_page'] == 1)):
                        st.session_state['browse_page'] -= 1
                        st.rerun()

                with col3:
                    st.markdown(f"<div style='text-align: center; color: #B0E0FF; padding-top: 8px;'>Page {st.session_state['browse_page']} of {total_pages}</div>", unsafe_allow_html=True)

                with col5:
                    if st.button("Next ➡️", disabled=(st.session_state['browse_page'] == total_pages)):
                        st.session_state['browse_page'] += 1
                        st.rerun()

            # Export option
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("### 💾 Export Results")
            csv = filtered_resources.to_csv(index=False)
            st.download_button(
                label="📥 Download Results as CSV",
                data=csv,
                file_name="bmis_browse_results.csv",
                mime="text/csv",
                use_container_width=True
            )

        else:
            st.markdown("""
            <div class="warning-box">
                ⚠️ <strong>No resources found matching your criteria.</strong> Try adjusting your filters or search query.
            </div>
            """, unsafe_allow_html=True)

    except Exception as e:
        st.error(f"❌ Error loading resources: {str(e)}")

    # Footer with Report a Problem button
    render_footer()


def render_saved_resources_tab():
    """Render the My Saved Resources tab"""
    display_logo()
    st.markdown('<div class="main-header">💾 My Saved Resources</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Your bookmarked STEM opportunities</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Initialize saved resources if not exists
    if 'saved_resources' not in st.session_state:
        st.session_state['saved_resources'] = []

    saved_count = len(st.session_state['saved_resources'])

    # Display count
    st.markdown(f"""
    <div class="info-box">
        <strong style="color: #00D9FF; font-size: 1.1rem;">📚 You have {saved_count} saved resource{'s' if saved_count != 1 else ''}</strong>
    </div>
    """, unsafe_allow_html=True)

    if saved_count == 0:
        # Empty state
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown("""
        <div style="text-align: center; padding: 3rem;">
            <div style="font-size: 4rem; margin-bottom: 1rem;">📚</div>
            <h3 style="color: #00D9FF;">No saved resources yet</h3>
            <p style="color: #B0E0FF; font-size: 1.1rem; margin: 1.5rem 0;">
                Click the ♡ button on any resource card to save it for later!
            </p>
        </div>
        """, unsafe_allow_html=True)

        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            if st.button("🔍 Browse All Resources", use_container_width=True, key="browse_from_saved"):
                st.session_state['current_tab'] = "🔍 Browse All"
                st.rerun()

    else:
        # Action buttons
        col1, col2, col3 = st.columns([2, 2, 1])

        with col1:
            if st.button("🗑️ Clear All", use_container_width=True, key="clear_all_saved"):
                if st.session_state.get('confirm_clear'):
                    st.session_state['saved_resources'] = []
                    st.session_state['confirm_clear'] = False
                    log_usage('saved_resources_cleared', {'count': saved_count})
                    st.rerun()
                else:
                    st.session_state['confirm_clear'] = True
                    st.warning("⚠️ Click 'Clear All' again to confirm deletion of all saved resources.")

        with col2:
            if saved_count > 0:
                # Export saved resources
                saved_df = pd.DataFrame(st.session_state['saved_resources'])
                csv = saved_df.to_csv(index=False)
                st.download_button(
                    label="📥 Export as CSV",
                    data=csv,
                    file_name=f"bmis_saved_resources_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv",
                    use_container_width=True,
                    key="export_saved"
                )

        st.markdown("<br>", unsafe_allow_html=True)

        # Display saved resources
        st.markdown("### 💎 Your Saved Resources")

        # Sort by saved date (most recent first)
        sorted_saved = sorted(
            st.session_state['saved_resources'],
            key=lambda x: x.get('saved_at', ''),
            reverse=True
        )

        for idx, saved_resource in enumerate(sorted_saved, 1):
            # Convert back to Series-like object for display_recommendation_card
            rec_series = pd.Series(saved_resource)
            display_recommendation_card(rec_series, idx, show_save_button=True)

    # Footer with Report a Problem button
    render_footer()


def render_feedback_tab():
    """Render the Share Feedback tab"""
    display_logo()
    st.markdown('<div class="main-header">💬 Share Your Feedback</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Help us improve BMIS for future students</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown("""
    <div class="info-box">
        <p style="font-size: 1.1rem;">Your feedback helps us improve the platform and helps demonstrate the impact of this project.</p>
        <p>All feedback is anonymous unless you choose to share your email.</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    with st.form("feedback_form"):
        # Star rating
        st.markdown("#### ⭐ Overall Experience")
        rating = st.select_slider(
            "How would you rate your experience with BMIS?",
            options=[1, 2, 3, 4, 5],
            value=4,
            format_func=lambda x: "⭐" * x
        )

        st.markdown("<br>", unsafe_allow_html=True)

        # What did you like
        st.markdown("#### 💚 What did you like most?")
        liked_most = st.text_area(
            "",
            placeholder="What features or aspects did you find most helpful?",
            height=100,
            label_visibility="collapsed"
        )

        # What to improve
        st.markdown("#### 🔧 What could we improve?")
        improvements = st.text_area(
            "",
            placeholder="What features are missing? What could work better?",
            height=100,
            label_visibility="collapsed"
        )

        # Did they find resources
        st.markdown("#### 🎯 Did you find new resources?")
        found_resources = st.radio(
            "",
            options=["Yes, I found several new opportunities", "Yes, I found a few", "Not sure yet", "No, nothing new"],
            label_visibility="collapsed"
        )

        # Success story (optional)
        st.markdown("#### 🎉 Success Story (Optional)")
        success_story = st.text_area(
            "",
            placeholder="Did you apply to or get accepted into any programs? Share your success story to inspire others!",
            height=120,
            label_visibility="collapsed"
        )

        # Email (optional)
        st.markdown("#### 📧 Email (Optional)")
        email = st.text_input(
            "",
            placeholder="Leave your email if you'd like us to follow up (optional)",
            label_visibility="collapsed"
        )

        # Submit button
        submit_feedback = st.form_submit_button("📤 Submit Feedback", use_container_width=True)

    if submit_feedback:
        # Validate at least one field is filled
        if not any([liked_most.strip(), improvements.strip(), success_story.strip()]):
            st.warning("⚠️ Please share at least some feedback before submitting.")
        else:
            # Save feedback
            success = save_feedback(rating, liked_most, improvements, found_resources, success_story, email)

            if success:
                # Log feedback submission
                log_usage('feedback_submitted', {'rating': rating, 'has_email': bool(email)})

                st.markdown("""
                <div class="success-box">
                    <h3 style="color: #6EE7B7; margin-bottom: 1rem;">✅ Thank you for your feedback!</h3>
                    <p>Your input helps make BMIS better for future students.</p>
                </div>
                """, unsafe_allow_html=True)

                # Show success stories prompt
                if success_story.strip():
                    st.markdown("""
                    <div class="info-box">
                        <p style="font-size: 1rem;">🌟 <strong>Thank you for sharing your success story!</strong></p>
                        <p>Your story will inspire other students to pursue their STEM dreams.</p>
                    </div>
                    """, unsafe_allow_html=True)

                st.balloons()
            else:
                st.error("❌ Error saving feedback. Please try again.")

    # Footer with Report a Problem button
    render_footer()


def main():
    """Main application with tab structure"""
    # Initialize session state
    if 'session_id' not in st.session_state:
        import uuid
        st.session_state['session_id'] = str(uuid.uuid4())

    if 'current_tab' not in st.session_state:
        st.session_state['current_tab'] = "🏠 Home"

    if 'profile_submitted' not in st.session_state:
        st.session_state['profile_submitted'] = False

    if 'browse_page' not in st.session_state:
        st.session_state['browse_page'] = 1

    # Load vote counts (cache in session state)
    if 'vote_counts' not in st.session_state:
        st.session_state['vote_counts'] = load_resource_votes()

    # Track which resources user has voted on
    if 'voted_resources' not in st.session_state:
        st.session_state['voted_resources'] = set()

    # Create custom tab navigation using radio buttons
    tab_titles = ["🏠 Home", "🎯 Get Recommendations", "💾 My Saved", "🔍 Browse All", "💬 Share Feedback"]

    # Display tab selection (styled as tabs via CSS)
    selected_tab = st.radio(
        "Navigation",
        tab_titles,
        index=tab_titles.index(st.session_state['current_tab']) if st.session_state['current_tab'] in tab_titles else 0,
        horizontal=True,
        label_visibility="collapsed",
        key="tab_selector"
    )

    # Update session state if tab changed
    if selected_tab != st.session_state['current_tab']:
        # Track page/tab visits
        log_usage('page_visit', {
            'page': selected_tab,
            'previous_page': st.session_state['current_tab']
        })
        st.session_state['current_tab'] = selected_tab
        st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    # Render the selected tab
    if st.session_state['current_tab'] == "🏠 Home":
        render_home_tab()
    elif st.session_state['current_tab'] == "🎯 Get Recommendations":
        render_recommendations_tab()
    elif st.session_state['current_tab'] == "💾 My Saved":
        render_saved_resources_tab()
    elif st.session_state['current_tab'] == "🔍 Browse All":
        render_browse_tab()
    elif st.session_state['current_tab'] == "💬 Share Feedback":
        render_feedback_tab()


if __name__ == "__main__":
    main()
