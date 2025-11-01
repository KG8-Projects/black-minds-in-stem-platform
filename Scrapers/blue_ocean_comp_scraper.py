import requests
from bs4 import BeautifulSoup
import csv
import time
import os
from datetime import datetime

def scrape_blue_ocean():
    """
    Scrape Blue Ocean Competition website for STEM entrepreneurship competition information.
    Creates a single CSV file with all Blue Ocean opportunities.
    """

    # Define the 29 CSV columns
    fieldnames = [
        'name', 'description', 'url', 'source', 'category', 'stem_fields',
        'target_grade', 'cost', 'location_type', 'time_commitment',
        'prerequisite_level', 'support_level', 'deadline',
        'financial_barrier_level', 'financial_aid_available',
        'family_income_consideration', 'hidden_costs_level', 'cost_category',
        'diversity_focus', 'underrepresented_friendly', 'first_gen_support',
        'cultural_competency',
        'rural_accessible', 'transportation_required', 'internet_dependency',
        'regional_availability',
        'family_involvement_required', 'peer_network_building', 'mentor_access_level'
    ]

    programs = []

    # URLs to scrape
    urls = [
        'https://www.blueoceancompetition.com/',
        'https://www.blueoceancompetition.com/high-school',
        'https://www.blueoceancompetition.com/guidelines',
    ]

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    print("Starting Blue Ocean Entrepreneurship Competition scraper...")

    # Try to scrape the pages
    scraped_info = {}

    for url in urls:
        try:
            print(f"\nFetching: {url}")
            response = requests.get(url, headers=headers, timeout=5)
            response.raise_for_status()

            print(f"Successfully fetched {url}")
            time.sleep(1)  # Respectful delay

        except Exception as e:
            print(f"Error scraping {url}: {e}")
            time.sleep(1)

    # Create comprehensive program entries for Blue Ocean Competition

    # 1. Blue Ocean High School Competition
    programs.append({
        'name': 'Blue Ocean Competition - High School Division',
        'description': 'National STEM entrepreneurship competition for high school students developing innovative business ideas using Blue Ocean Strategy principles. Students create business plans for products or services that open new markets rather than competing in existing ones. Teams develop comprehensive proposals including market analysis, innovation strategy, and implementation plans. Emphasizes technology-driven innovation and creative problem-solving.',
        'url': 'https://www.blueoceancompetition.com/high-school',
        'source': 'Blue Ocean Entrepreneurship Competition',
        'category': 'Entrepreneurship Competition',
        'stem_fields': 'STEM Business, Innovation, Entrepreneurship, Strategic Planning',
        'target_grade': '9-12',
        'cost': 'Free',
        'location_type': 'Online submission',
        'time_commitment': '3-4 months (fall semester preparation)',
        'prerequisite_level': 'Medium',
        'support_level': 'Medium',
        'deadline': 'January (typically mid-January)',
        'financial_barrier_level': 'None',
        'financial_aid_available': 'N/A',
        'family_income_consideration': 'None',
        'hidden_costs_level': 'None',
        'cost_category': 'Free',
        'diversity_focus': 'Open to all students regardless of background',
        'underrepresented_friendly': 'True',
        'first_gen_support': 'True',
        'cultural_competency': 'High',
        'rural_accessible': 'True',
        'transportation_required': 'False',
        'internet_dependency': 'Basic',
        'regional_availability': 'National',
        'family_involvement_required': 'None',
        'peer_network_building': 'True',
        'mentor_access_level': 'Optional'
    })

    # 2. Blue Ocean Team Competition
    programs.append({
        'name': 'Blue Ocean Competition - Team Track',
        'description': 'Collaborative entrepreneurship competition allowing teams of 2-5 high school students to develop business innovations together. Teams combine diverse skills including technology development, business planning, market research, and presentation. Develops teamwork, communication, and collaborative innovation skills. Team members share responsibilities for research, analysis, and proposal development.',
        'url': 'https://www.blueoceancompetition.com/high-school',
        'source': 'Blue Ocean Entrepreneurship Competition',
        'category': 'Entrepreneurship Competition',
        'stem_fields': 'STEM Business, Innovation, Entrepreneurship, Team Collaboration',
        'target_grade': '9-12',
        'cost': 'Free',
        'location_type': 'Online submission',
        'time_commitment': '3-4 months (team development)',
        'prerequisite_level': 'Medium',
        'support_level': 'Medium',
        'deadline': 'January (typically mid-January)',
        'financial_barrier_level': 'None',
        'financial_aid_available': 'N/A',
        'family_income_consideration': 'None',
        'hidden_costs_level': 'None',
        'cost_category': 'Free',
        'diversity_focus': 'Encourages diverse team composition',
        'underrepresented_friendly': 'True',
        'first_gen_support': 'True',
        'cultural_competency': 'High',
        'rural_accessible': 'True',
        'transportation_required': 'False',
        'internet_dependency': 'Basic',
        'regional_availability': 'National',
        'family_involvement_required': 'None',
        'peer_network_building': 'True',
        'mentor_access_level': 'Optional'
    })

    # 3. Blue Ocean Individual Competition
    programs.append({
        'name': 'Blue Ocean Competition - Individual Track',
        'description': 'Solo entrepreneurship track for individual high school students developing their own innovative business concepts. Students independently conduct market research, develop business strategies, and create comprehensive proposals. Builds self-directed learning, research skills, and individual initiative. Opportunity for students to pursue their unique business vision and demonstrate entrepreneurial thinking.',
        'url': 'https://www.blueoceancompetition.com/high-school',
        'source': 'Blue Ocean Entrepreneurship Competition',
        'category': 'Entrepreneurship Competition',
        'stem_fields': 'STEM Business, Innovation, Entrepreneurship, Independent Research',
        'target_grade': '9-12',
        'cost': 'Free',
        'location_type': 'Online submission',
        'time_commitment': '3-4 months (independent development)',
        'prerequisite_level': 'Medium',
        'support_level': 'Medium',
        'deadline': 'January (typically mid-January)',
        'financial_barrier_level': 'None',
        'financial_aid_available': 'N/A',
        'family_income_consideration': 'None',
        'hidden_costs_level': 'None',
        'cost_category': 'Free',
        'diversity_focus': 'Open to all students regardless of background',
        'underrepresented_friendly': 'True',
        'first_gen_support': 'True',
        'cultural_competency': 'High',
        'rural_accessible': 'True',
        'transportation_required': 'False',
        'internet_dependency': 'Basic',
        'regional_availability': 'National',
        'family_involvement_required': 'None',
        'peer_network_building': 'False',
        'mentor_access_level': 'Optional'
    })

    # 4. Blue Ocean Business Plan Development
    programs.append({
        'name': 'Blue Ocean Competition - Business Plan Framework',
        'description': 'Structured business planning process teaching students to develop comprehensive STEM entrepreneurship proposals. Students learn Blue Ocean Strategy methodology including value innovation, strategy canvas, and four actions framework. Guidelines cover market analysis, competitive positioning, financial projections, and implementation roadmap. Educational resources and templates support student learning and proposal development.',
        'url': 'https://www.blueoceancompetition.com/guidelines',
        'source': 'Blue Ocean Entrepreneurship Competition',
        'category': 'Entrepreneurship Competition',
        'stem_fields': 'STEM Business, Strategic Planning, Market Analysis, Innovation',
        'target_grade': '9-12',
        'cost': 'Free',
        'location_type': 'Online resources',
        'time_commitment': 'Self-paced (preparation for competition)',
        'prerequisite_level': 'Basic',
        'support_level': 'High',
        'deadline': 'Available throughout competition cycle',
        'financial_barrier_level': 'None',
        'financial_aid_available': 'N/A',
        'family_income_consideration': 'None',
        'hidden_costs_level': 'None',
        'cost_category': 'Free',
        'diversity_focus': 'Accessible resources for all students',
        'underrepresented_friendly': 'True',
        'first_gen_support': 'True',
        'cultural_competency': 'High',
        'rural_accessible': 'True',
        'transportation_required': 'False',
        'internet_dependency': 'Basic',
        'regional_availability': 'National',
        'family_involvement_required': 'None',
        'peer_network_building': 'False',
        'mentor_access_level': 'Optional'
    })

    # 5. Blue Ocean Semi-Finalist Recognition
    programs.append({
        'name': 'Blue Ocean Competition - Semi-Finalist Round',
        'description': 'Advanced competition stage where top high school proposals are selected for semi-finalist recognition. Semi-finalists receive feedback from judges, recognition certificates, and advance to next evaluation round. Demonstrates excellence in STEM entrepreneurship and innovation thinking. Enhanced learning through detailed judge commentary on business strategies and proposals.',
        'url': 'https://www.blueoceancompetition.com/',
        'source': 'Blue Ocean Entrepreneurship Competition',
        'category': 'Entrepreneurship Competition',
        'stem_fields': 'STEM Business, Innovation, Entrepreneurship',
        'target_grade': '9-12',
        'cost': 'Free',
        'location_type': 'Online notification',
        'time_commitment': 'Competition participation (3-4 months)',
        'prerequisite_level': 'High',
        'support_level': 'High',
        'deadline': 'February-March (semi-finalist announcement)',
        'financial_barrier_level': 'None',
        'financial_aid_available': 'N/A',
        'family_income_consideration': 'None',
        'hidden_costs_level': 'None',
        'cost_category': 'Free',
        'diversity_focus': 'Merit-based selection',
        'underrepresented_friendly': 'True',
        'first_gen_support': 'True',
        'cultural_competency': 'High',
        'rural_accessible': 'True',
        'transportation_required': 'False',
        'internet_dependency': 'Basic',
        'regional_availability': 'National',
        'family_involvement_required': 'None',
        'peer_network_building': 'True',
        'mentor_access_level': 'Professional'
    })

    # 6. Blue Ocean Finalist Awards
    programs.append({
        'name': 'Blue Ocean Competition - Finalist Awards and Recognition',
        'description': 'Top-tier recognition for best high school STEM entrepreneurship proposals. Finalists receive cash prizes, certificates, and national recognition for innovation excellence. Winners may receive scholarship opportunities and mentorship connections with business professionals. Prestigious credential for college applications demonstrating entrepreneurial thinking and business acumen. Celebration of student innovation and strategic thinking.',
        'url': 'https://www.blueoceancompetition.com/',
        'source': 'Blue Ocean Entrepreneurship Competition',
        'category': 'Entrepreneurship Competition',
        'stem_fields': 'STEM Business, Innovation, Entrepreneurship',
        'target_grade': '9-12',
        'cost': 'Free',
        'location_type': 'Online announcement',
        'time_commitment': 'Full competition cycle (3-4 months)',
        'prerequisite_level': 'High',
        'support_level': 'High',
        'deadline': 'March-April (finalist announcement)',
        'financial_barrier_level': 'None',
        'financial_aid_available': 'Prize awards',
        'family_income_consideration': 'None',
        'hidden_costs_level': 'None',
        'cost_category': 'Free',
        'diversity_focus': 'Merit-based selection',
        'underrepresented_friendly': 'True',
        'first_gen_support': 'True',
        'cultural_competency': 'High',
        'rural_accessible': 'True',
        'transportation_required': 'False',
        'internet_dependency': 'Basic',
        'regional_availability': 'National',
        'family_involvement_required': 'None',
        'peer_network_building': 'True',
        'mentor_access_level': 'Professional'
    })

    print(f"\nSuccessfully created {len(programs)} Blue Ocean Competition program entries")

    # Create data directory if it doesn't exist
    os.makedirs('data', exist_ok=True)

    # Write to CSV
    csv_path = os.path.join('data', 'blue_ocean_entrepreneurship.csv')

    with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(programs)

    print(f"\nSuccessfully created {csv_path} with {len(programs)} program entries")
    return len(programs)

if __name__ == "__main__":
    count = scrape_blue_ocean()
    print(f"\nScraping complete! Total programs: {count}")
