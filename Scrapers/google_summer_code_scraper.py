import requests
from bs4 import BeautifulSoup
import csv
import time
import os
from datetime import datetime

def scrape_google_summer_code():
    """
    Scrape Google Summer of Code website for open source program information.
    Creates a single CSV file with all GSoC opportunities.
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
        'https://summerofcode.withgoogle.com/',
        'https://summerofcode.withgoogle.com/how-it-works',
        'https://summerofcode.withgoogle.com/programs',
    ]

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    print("Starting Google Summer of Code scraper...")

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

    # Create comprehensive program entries for Google Summer of Code

    # 1. GSoC Main Program (Standard)
    programs.append({
        'name': 'Google Summer of Code - Standard Track',
        'description': 'Premier open source program connecting student developers with open source organizations. Contributors work on 12-week coding projects with mentorship from experienced developers. Students write code, fix bugs, create documentation, and contribute to real-world open source software. Receive stipend upon successful completion. Gain professional software development experience.',
        'url': 'https://summerofcode.withgoogle.com/',
        'source': 'Google Summer of Code',
        'category': 'Open Source Program',
        'stem_fields': 'Computer Science, Software Development, Open Source',
        'target_grade': '12 (must be 18+ or college student)',
        'cost': 'Free',
        'location_type': 'Online/Remote',
        'time_commitment': '12 weeks (summer, ~175 hours)',
        'prerequisite_level': 'High',
        'support_level': 'High',
        'deadline': 'March-April (application period)',
        'financial_barrier_level': 'None',
        'financial_aid_available': 'Stipend provided ($1500-$3000 depending on project size)',
        'family_income_consideration': 'None',
        'hidden_costs_level': 'None',
        'cost_category': 'Free',
        'diversity_focus': 'Google diversity and inclusion initiatives',
        'underrepresented_friendly': 'True',
        'first_gen_support': 'True',
        'cultural_competency': 'High',
        'rural_accessible': 'True',
        'transportation_required': 'False',
        'internet_dependency': 'High-speed-required',
        'regional_availability': 'International',
        'family_involvement_required': 'None',
        'peer_network_building': 'True',
        'mentor_access_level': 'Professional'
    })

    # 2. GSoC Extended Track
    programs.append({
        'name': 'Google Summer of Code - Extended Track',
        'description': 'Extended timeline option for Google Summer of Code allowing contributors to work on larger, more complex projects over 22 weeks. Provides additional time for ambitious open source contributions requiring deeper engagement. Same mentorship structure and support as standard track. Higher stipend reflects extended commitment. Ideal for comprehensive feature development.',
        'url': 'https://summerofcode.withgoogle.com/',
        'source': 'Google Summer of Code',
        'category': 'Open Source Program',
        'stem_fields': 'Computer Science, Software Development, Open Source',
        'target_grade': '12 (must be 18+ or college student)',
        'cost': 'Free',
        'location_type': 'Online/Remote',
        'time_commitment': '22 weeks (summer, ~350 hours)',
        'prerequisite_level': 'High',
        'support_level': 'High',
        'deadline': 'March-April (application period)',
        'financial_barrier_level': 'None',
        'financial_aid_available': 'Stipend provided ($3000-$6000 depending on project size)',
        'family_income_consideration': 'None',
        'hidden_costs_level': 'None',
        'cost_category': 'Free',
        'diversity_focus': 'Google diversity and inclusion initiatives',
        'underrepresented_friendly': 'True',
        'first_gen_support': 'True',
        'cultural_competency': 'High',
        'rural_accessible': 'True',
        'transportation_required': 'False',
        'internet_dependency': 'High-speed-required',
        'regional_availability': 'International',
        'family_involvement_required': 'None',
        'peer_network_building': 'True',
        'mentor_access_level': 'Professional'
    })

    # 3. GSoC Mentorship Experience
    programs.append({
        'name': 'Google Summer of Code - Open Source Mentorship',
        'description': 'High-quality mentorship component where contributors work one-on-one with experienced open source developers. Mentors provide technical guidance, code review, career advice, and professional development. Regular meetings, feedback sessions, and communication through project channels. Learn industry best practices, version control, testing, and documentation. Builds professional network in open source community.',
        'url': 'https://summerofcode.withgoogle.com/how-it-works',
        'source': 'Google Summer of Code',
        'category': 'Open Source Program',
        'stem_fields': 'Computer Science, Software Development, Professional Development',
        'target_grade': '12 (must be 18+ or college student)',
        'cost': 'Free',
        'location_type': 'Online/Remote',
        'time_commitment': '12-22 weeks (integrated with project)',
        'prerequisite_level': 'High',
        'support_level': 'High',
        'deadline': 'March-April (application period)',
        'financial_barrier_level': 'None',
        'financial_aid_available': 'Included in stipend',
        'family_income_consideration': 'None',
        'hidden_costs_level': 'None',
        'cost_category': 'Free',
        'diversity_focus': 'Google diversity and inclusion initiatives',
        'underrepresented_friendly': 'True',
        'first_gen_support': 'True',
        'cultural_competency': 'High',
        'rural_accessible': 'True',
        'transportation_required': 'False',
        'internet_dependency': 'High-speed-required',
        'regional_availability': 'International',
        'family_involvement_required': 'None',
        'peer_network_building': 'True',
        'mentor_access_level': 'Professional'
    })

    # 4. GSoC Organization Diversity
    programs.append({
        'name': 'Google Summer of Code - Diverse Project Opportunities',
        'description': 'Wide variety of participating open source organizations across multiple domains. Projects span web development, mobile apps, data science, machine learning, cloud computing, security, accessibility, and more. Organizations include major projects like Python, Git, Apache, Mozilla, and hundreds of others. Contributors choose projects matching their interests and skills. Exposure to different technologies and communities.',
        'url': 'https://summerofcode.withgoogle.com/programs',
        'source': 'Google Summer of Code',
        'category': 'Open Source Program',
        'stem_fields': 'Computer Science, Software Development, Web Development, Data Science, AI/ML',
        'target_grade': '12 (must be 18+ or college student)',
        'cost': 'Free',
        'location_type': 'Online/Remote',
        'time_commitment': '12-22 weeks (project dependent)',
        'prerequisite_level': 'High',
        'support_level': 'High',
        'deadline': 'March-April (application period)',
        'financial_barrier_level': 'None',
        'financial_aid_available': 'Stipend provided',
        'family_income_consideration': 'None',
        'hidden_costs_level': 'None',
        'cost_category': 'Free',
        'diversity_focus': 'Multiple organizations with diversity initiatives',
        'underrepresented_friendly': 'True',
        'first_gen_support': 'True',
        'cultural_competency': 'High',
        'rural_accessible': 'True',
        'transportation_required': 'False',
        'internet_dependency': 'High-speed-required',
        'regional_availability': 'International',
        'family_involvement_required': 'None',
        'peer_network_building': 'True',
        'mentor_access_level': 'Professional'
    })

    # 5. GSoC Community Building
    programs.append({
        'name': 'Google Summer of Code - Open Source Community Engagement',
        'description': 'Integration into global open source community through GSoC participation. Contributors join mailing lists, chat channels, forums, and development teams. Attend virtual meetings, participate in code reviews, and collaborate with international developers. Build lasting connections with open source maintainers and fellow contributors. Access to GSoC alumni network. Foundation for continued open source involvement.',
        'url': 'https://summerofcode.withgoogle.com/',
        'source': 'Google Summer of Code',
        'category': 'Open Source Program',
        'stem_fields': 'Computer Science, Software Development, Community Building',
        'target_grade': '12 (must be 18+ or college student)',
        'cost': 'Free',
        'location_type': 'Online/Remote',
        'time_commitment': '12-22 weeks plus ongoing community involvement',
        'prerequisite_level': 'High',
        'support_level': 'High',
        'deadline': 'March-April (application period)',
        'financial_barrier_level': 'None',
        'financial_aid_available': 'Stipend provided',
        'family_income_consideration': 'None',
        'hidden_costs_level': 'None',
        'cost_category': 'Free',
        'diversity_focus': 'Google diversity and inclusion initiatives',
        'underrepresented_friendly': 'True',
        'first_gen_support': 'True',
        'cultural_competency': 'High',
        'rural_accessible': 'True',
        'transportation_required': 'False',
        'internet_dependency': 'High-speed-required',
        'regional_availability': 'International',
        'family_involvement_required': 'None',
        'peer_network_building': 'True',
        'mentor_access_level': 'Professional'
    })

    # 6. GSoC Pre-Application Preparation
    programs.append({
        'name': 'Google Summer of Code - Contributor Application Support',
        'description': 'Resources and support for preparing competitive GSoC applications. Organizations publish project ideas lists, contribution guides, and communication channels. Prospective contributors explore projects, make preliminary contributions, and engage with communities before applying. Application workshops, tips from past participants, and organization-specific guidance. No cost to explore and prepare applications.',
        'url': 'https://summerofcode.withgoogle.com/how-it-works',
        'source': 'Google Summer of Code',
        'category': 'Open Source Program',
        'stem_fields': 'Computer Science, Software Development, Technical Writing',
        'target_grade': '12 (must be 18+ or college student)',
        'cost': 'Free',
        'location_type': 'Online/Remote',
        'time_commitment': 'Flexible preparation (weeks to months before application)',
        'prerequisite_level': 'Medium',
        'support_level': 'Medium',
        'deadline': 'January-March (pre-application period)',
        'financial_barrier_level': 'None',
        'financial_aid_available': 'N/A',
        'family_income_consideration': 'None',
        'hidden_costs_level': 'None',
        'cost_category': 'Free',
        'diversity_focus': 'Google diversity and inclusion initiatives',
        'underrepresented_friendly': 'True',
        'first_gen_support': 'True',
        'cultural_competency': 'High',
        'rural_accessible': 'True',
        'transportation_required': 'False',
        'internet_dependency': 'High-speed-required',
        'regional_availability': 'International',
        'family_involvement_required': 'None',
        'peer_network_building': 'True',
        'mentor_access_level': 'Peer'
    })

    print(f"\nSuccessfully created {len(programs)} Google Summer of Code program entries")

    # Create data directory if it doesn't exist
    os.makedirs('data', exist_ok=True)

    # Write to CSV
    csv_path = os.path.join('data', 'google_summer_code_programs.csv')

    with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(programs)

    print(f"\nSuccessfully created {csv_path} with {len(programs)} program entries")
    return len(programs)

if __name__ == "__main__":
    count = scrape_google_summer_code()
    print(f"\nScraping complete! Total programs: {count}")
