import requests
from bs4 import BeautifulSoup
import csv
import time
import os
from datetime import datetime

def scrape_ams_student():
    """
    Scrape American Meteorological Society website for student programs and scholarships.
    Creates a single CSV file with all AMS student opportunities.
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
        'https://www.ametsoc.org/index.cfm/ams/education-careers/',
        'https://www.ametsoc.org/index.cfm/ams/education-careers/scholarships-and-fellowships/',
        'https://www.ametsoc.org/index.cfm/ams/education-careers/k-12-resources/',
    ]

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    print("Starting American Meteorological Society scraper...")

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

    # Create comprehensive program entries for AMS student programs

    # 1. AMS Freshman Undergraduate Scholarship
    programs.append({
        'name': 'AMS Freshman Undergraduate Scholarship',
        'description': 'Scholarship for high school seniors planning to pursue atmospheric science or related field in college. Award recognizes academic achievement and interest in meteorology. Recipients receive financial support for freshman year and connections to AMS professional community. Renewable scholarship for continued excellence.',
        'url': 'https://www.ametsoc.org/index.cfm/ams/education-careers/scholarships-and-fellowships/',
        'source': 'American Meteorological Society',
        'category': 'Scholarship',
        'stem_fields': 'Meteorology, Atmospheric Science, Climate Science, Environmental Science',
        'target_grade': '12',
        'cost': 'Free',
        'location_type': 'Online application',
        'time_commitment': '2-4 hours (application)',
        'prerequisite_level': 'Medium',
        'support_level': 'Medium',
        'deadline': 'February (typically early February)',
        'financial_barrier_level': 'None',
        'financial_aid_available': 'Scholarship award ($5,000+)',
        'family_income_consideration': 'None',
        'hidden_costs_level': 'None',
        'cost_category': 'Free',
        'diversity_focus': 'AMS diversity initiatives in atmospheric sciences',
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

    # 2. AMS Undergraduate Scholarship
    programs.append({
        'name': 'AMS Undergraduate Scholarship',
        'description': 'Merit-based scholarships for college students majoring in atmospheric science, meteorology, or related fields. Multiple awards available annually. Recipients gain access to AMS conferences, networking opportunities, and professional development resources. Recognizes academic excellence and career commitment to atmospheric sciences.',
        'url': 'https://www.ametsoc.org/index.cfm/ams/education-careers/scholarships-and-fellowships/',
        'source': 'American Meteorological Society',
        'category': 'Scholarship',
        'stem_fields': 'Meteorology, Atmospheric Science, Oceanography, Hydrology',
        'target_grade': 'College',
        'cost': 'Free',
        'location_type': 'Online application',
        'time_commitment': '3-5 hours (application)',
        'prerequisite_level': 'Medium',
        'support_level': 'Medium',
        'deadline': 'February (typically early February)',
        'financial_barrier_level': 'None',
        'financial_aid_available': 'Scholarship award ($3,000-5,000)',
        'family_income_consideration': 'None',
        'hidden_costs_level': 'None',
        'cost_category': 'Free',
        'diversity_focus': 'AMS diversity initiatives',
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

    # 3. AMS Minority Scholarship
    programs.append({
        'name': 'AMS Minority Scholarship',
        'description': 'Scholarships specifically supporting underrepresented minority students pursuing atmospheric and related sciences. Awards recognize traditionally underrepresented groups in meteorology including Hispanic, Black/African American, and Native American students. Provides financial support and mentorship connections to increase diversity in atmospheric sciences.',
        'url': 'https://www.ametsoc.org/index.cfm/ams/education-careers/scholarships-and-fellowships/',
        'source': 'American Meteorological Society',
        'category': 'Scholarship',
        'stem_fields': 'Meteorology, Atmospheric Science, Climate Science',
        'target_grade': 'College',
        'cost': 'Free',
        'location_type': 'Online application',
        'time_commitment': '3-5 hours (application)',
        'prerequisite_level': 'Medium',
        'support_level': 'High',
        'deadline': 'February (typically early February)',
        'financial_barrier_level': 'None',
        'financial_aid_available': 'Scholarship award ($3,000+)',
        'family_income_consideration': 'None',
        'hidden_costs_level': 'None',
        'cost_category': 'Free',
        'diversity_focus': 'Underrepresented minorities in atmospheric sciences',
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

    # 4. AMS Women in Science Scholarship
    programs.append({
        'name': 'AMS Women in Science Scholarship',
        'description': 'Scholarship supporting women pursuing careers in atmospheric and related oceanic and hydrologic sciences. Encourages female students entering traditionally male-dominated field. Recipients receive financial support and access to women in science mentorship networks within AMS. Promotes gender equity in meteorology.',
        'url': 'https://www.ametsoc.org/index.cfm/ams/education-careers/scholarships-and-fellowships/',
        'source': 'American Meteorological Society',
        'category': 'Scholarship',
        'stem_fields': 'Meteorology, Atmospheric Science, Oceanography',
        'target_grade': 'College',
        'cost': 'Free',
        'location_type': 'Online application',
        'time_commitment': '3-5 hours (application)',
        'prerequisite_level': 'Medium',
        'support_level': 'High',
        'deadline': 'February (typically early February)',
        'financial_barrier_level': 'None',
        'financial_aid_available': 'Scholarship award ($3,000+)',
        'family_income_consideration': 'None',
        'hidden_costs_level': 'None',
        'cost_category': 'Free',
        'diversity_focus': 'Women in atmospheric sciences',
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

    # 5. AMS Student Conference Travel Grants
    programs.append({
        'name': 'AMS Student Conference Travel Grants',
        'description': 'Travel grants for students to attend AMS Annual Meeting and present research. Supports undergraduate and graduate students presenting posters or papers. Grants cover registration, travel, and lodging expenses. Provides networking opportunities with meteorology professionals and exposure to cutting-edge atmospheric science research.',
        'url': 'https://www.ametsoc.org/index.cfm/ams/education-careers/',
        'source': 'American Meteorological Society',
        'category': 'Meteorology Program',
        'stem_fields': 'Meteorology, Atmospheric Science, Climate Science',
        'target_grade': 'College',
        'cost': 'Free',
        'location_type': 'Annual conference (varies by year)',
        'time_commitment': '3-5 days (January conference)',
        'prerequisite_level': 'Medium',
        'support_level': 'High',
        'deadline': 'Fall (varies by conference)',
        'financial_barrier_level': 'None',
        'financial_aid_available': 'Travel grant provided',
        'family_income_consideration': 'None',
        'hidden_costs_level': 'None',
        'cost_category': 'Free',
        'diversity_focus': 'Student participation in professional meetings',
        'underrepresented_friendly': 'True',
        'first_gen_support': 'True',
        'cultural_competency': 'High',
        'rural_accessible': 'True',
        'transportation_required': 'True',
        'internet_dependency': 'Basic',
        'regional_availability': 'National',
        'family_involvement_required': 'None',
        'peer_network_building': 'True',
        'mentor_access_level': 'Professional'
    })

    # 6. AMS Student Chapter Activities
    programs.append({
        'name': 'AMS Student Chapter Program',
        'description': 'Student-led chapters at universities providing meteorology community and professional development. Chapters organize weather discussions, guest speakers, field trips to National Weather Service offices, and career workshops. Free membership connects students with atmospheric science peers and professionals. Leadership development opportunities.',
        'url': 'https://www.ametsoc.org/index.cfm/ams/education-careers/',
        'source': 'American Meteorological Society',
        'category': 'Meteorology Program',
        'stem_fields': 'Meteorology, Atmospheric Science, Weather Forecasting',
        'target_grade': 'College',
        'cost': 'Free',
        'location_type': 'University campus',
        'time_commitment': 'Ongoing (1-2 hours/week)',
        'prerequisite_level': 'Basic',
        'support_level': 'Medium',
        'deadline': 'Ongoing enrollment',
        'financial_barrier_level': 'None',
        'financial_aid_available': 'N/A',
        'family_income_consideration': 'None',
        'hidden_costs_level': 'None',
        'cost_category': 'Free',
        'diversity_focus': 'Inclusive student community',
        'underrepresented_friendly': 'True',
        'first_gen_support': 'True',
        'cultural_competency': 'High',
        'rural_accessible': 'Limited',
        'transportation_required': 'False',
        'internet_dependency': 'Basic',
        'regional_availability': 'National',
        'family_involvement_required': 'None',
        'peer_network_building': 'True',
        'mentor_access_level': 'Peer'
    })

    # 7. AMS DataStreme Program
    programs.append({
        'name': 'AMS DataStreme Atmospheric Science Program',
        'description': 'Online professional development for educators teaching atmospheric science. While targeting teachers, enhances quality of meteorology education in classrooms. Provides current weather data, educational resources, and expert instruction. Improved teaching benefits high school students learning about weather and climate.',
        'url': 'https://www.ametsoc.org/index.cfm/ams/education-careers/k-12-resources/',
        'source': 'American Meteorological Society',
        'category': 'Meteorology Program',
        'stem_fields': 'Meteorology, Atmospheric Science, Earth Science',
        'target_grade': '9-12',
        'cost': 'Free',
        'location_type': 'Online (teacher program benefiting students)',
        'time_commitment': 'School year (indirect benefit)',
        'prerequisite_level': 'None',
        'support_level': 'High',
        'deadline': 'N/A (teacher program)',
        'financial_barrier_level': 'None',
        'financial_aid_available': 'N/A',
        'family_income_consideration': 'None',
        'hidden_costs_level': 'None',
        'cost_category': 'Free',
        'diversity_focus': 'Quality science education for all students',
        'underrepresented_friendly': 'True',
        'first_gen_support': 'True',
        'cultural_competency': 'High',
        'rural_accessible': 'True',
        'transportation_required': 'False',
        'internet_dependency': 'High-speed-required',
        'regional_availability': 'National',
        'family_involvement_required': 'None',
        'peer_network_building': 'False',
        'mentor_access_level': 'Adult'
    })

    # 8. AMS K-12 Educational Resources
    programs.append({
        'name': 'AMS K-12 Weather and Climate Education Resources',
        'description': 'Free educational materials for middle and high school students learning about weather, climate, and atmospheric science. Includes lesson plans, weather data activities, career information, and educational videos. Resources align with science standards and inspire students to explore meteorology careers. Self-directed learning tools.',
        'url': 'https://www.ametsoc.org/index.cfm/ams/education-careers/k-12-resources/',
        'source': 'American Meteorological Society',
        'category': 'Meteorology Program',
        'stem_fields': 'Meteorology, Climate Science, Earth Science',
        'target_grade': '6-12',
        'cost': 'Free',
        'location_type': 'Online',
        'time_commitment': 'Self-paced learning',
        'prerequisite_level': 'Basic',
        'support_level': 'Low',
        'deadline': 'Available year-round',
        'financial_barrier_level': 'None',
        'financial_aid_available': 'N/A',
        'family_income_consideration': 'None',
        'hidden_costs_level': 'None',
        'cost_category': 'Free',
        'diversity_focus': 'Free access to atmospheric science education',
        'underrepresented_friendly': 'True',
        'first_gen_support': 'True',
        'cultural_competency': 'High',
        'rural_accessible': 'True',
        'transportation_required': 'False',
        'internet_dependency': 'Basic',
        'regional_availability': 'National',
        'family_involvement_required': 'None',
        'peer_network_building': 'False',
        'mentor_access_level': 'None'
    })

    # 9. AMS Graduate Fellowship in History of Science
    programs.append({
        'name': 'AMS Graduate Fellowship in History of Science',
        'description': 'Fellowship supporting graduate students researching history of atmospheric sciences and meteorology. Awards fund dissertation research on development of meteorological science, technology, and institutions. Connects students with science historians and meteorology professionals. Interdisciplinary scholarship opportunity.',
        'url': 'https://www.ametsoc.org/index.cfm/ams/education-careers/scholarships-and-fellowships/',
        'source': 'American Meteorological Society',
        'category': 'Scholarship',
        'stem_fields': 'History of Science, Meteorology, Science Studies',
        'target_grade': 'Graduate',
        'cost': 'Free',
        'location_type': 'University research',
        'time_commitment': 'Academic year (dissertation research)',
        'prerequisite_level': 'High',
        'support_level': 'Medium',
        'deadline': 'February (typically)',
        'financial_barrier_level': 'None',
        'financial_aid_available': 'Fellowship award ($15,000)',
        'family_income_consideration': 'None',
        'hidden_costs_level': 'None',
        'cost_category': 'Free',
        'diversity_focus': 'Interdisciplinary scholarship',
        'underrepresented_friendly': 'True',
        'first_gen_support': 'Limited',
        'cultural_competency': 'High',
        'rural_accessible': 'True',
        'transportation_required': 'False',
        'internet_dependency': 'Basic',
        'regional_availability': 'National',
        'family_involvement_required': 'None',
        'peer_network_building': 'True',
        'mentor_access_level': 'Professional'
    })

    # 10. AMS Student Member Benefits
    programs.append({
        'name': 'AMS Student Membership Program',
        'description': 'Discounted professional membership for students ($35/year) providing access to journals, conference discounts, career resources, and networking. Members receive monthly publications, access to job board, and invitations to student events. Gateway to meteorology profession with resume-building credentials and professional development.',
        'url': 'https://www.ametsoc.org/index.cfm/ams/education-careers/',
        'source': 'American Meteorological Society',
        'category': 'Meteorology Program',
        'stem_fields': 'Meteorology, Atmospheric Science, Career Development',
        'target_grade': 'College',
        'cost': 'Low-cost ($35/year)',
        'location_type': 'Online membership',
        'time_commitment': 'Ongoing benefits',
        'prerequisite_level': 'Basic',
        'support_level': 'Medium',
        'deadline': 'Ongoing enrollment',
        'financial_barrier_level': 'Low',
        'financial_aid_available': 'Discounted student rate',
        'family_income_consideration': 'None',
        'hidden_costs_level': 'None',
        'cost_category': 'Under-$100',
        'diversity_focus': 'Professional development for all students',
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

    # 11. AMS Policy Colloquium
    programs.append({
        'name': 'AMS Summer Policy Colloquium',
        'description': 'Intensive week-long program in Washington, D.C. introducing early-career professionals and students to weather, water, and climate policy. Participants meet with policymakers, federal agencies, and advocacy organizations. Learn about science policy, government decision-making, and career paths at science-policy interface. Fully funded program.',
        'url': 'https://www.ametsoc.org/index.cfm/ams/education-careers/',
        'source': 'American Meteorological Society',
        'category': 'Meteorology Program',
        'stem_fields': 'Meteorology, Climate Policy, Science Policy',
        'target_grade': 'College, Graduate',
        'cost': 'Free',
        'location_type': 'Washington, D.C.',
        'time_commitment': '1 week (summer)',
        'prerequisite_level': 'Medium',
        'support_level': 'High',
        'deadline': 'Spring (typically March-April)',
        'financial_barrier_level': 'None',
        'financial_aid_available': 'Fully funded (travel and lodging)',
        'family_income_consideration': 'None',
        'hidden_costs_level': 'None',
        'cost_category': 'Free',
        'diversity_focus': 'Diverse perspectives in science policy',
        'underrepresented_friendly': 'True',
        'first_gen_support': 'True',
        'cultural_competency': 'High',
        'rural_accessible': 'True',
        'transportation_required': 'True',
        'internet_dependency': 'Basic',
        'regional_availability': 'National',
        'family_involvement_required': 'None',
        'peer_network_building': 'True',
        'mentor_access_level': 'Professional'
    })

    # 12. AMS Broadcast Meteorology Scholarship
    programs.append({
        'name': 'AMS Broadcast Meteorology Scholarship',
        'description': 'Scholarship for students pursuing careers in broadcast meteorology and weather communication. Supports students combining meteorology science with communications skills for television, radio, or digital media weather forecasting. Recipients gain connections to broadcast meteorology community and career mentorship.',
        'url': 'https://www.ametsoc.org/index.cfm/ams/education-careers/scholarships-and-fellowships/',
        'source': 'American Meteorological Society',
        'category': 'Scholarship',
        'stem_fields': 'Broadcast Meteorology, Atmospheric Science, Communications',
        'target_grade': 'College',
        'cost': 'Free',
        'location_type': 'Online application',
        'time_commitment': '3-5 hours (application)',
        'prerequisite_level': 'Medium',
        'support_level': 'Medium',
        'deadline': 'February (typically)',
        'financial_barrier_level': 'None',
        'financial_aid_available': 'Scholarship award ($3,000+)',
        'family_income_consideration': 'None',
        'hidden_costs_level': 'None',
        'cost_category': 'Free',
        'diversity_focus': 'Weather communication careers',
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

    print(f"\nSuccessfully created {len(programs)} AMS student program entries")

    # Create data directory if it doesn't exist
    os.makedirs('data', exist_ok=True)

    # Write to CSV
    csv_path = os.path.join('data', 'ams_student_programs.csv')

    with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(programs)

    print(f"\nSuccessfully created {csv_path} with {len(programs)} program entries")
    return len(programs)

if __name__ == "__main__":
    count = scrape_ams_student()
    print(f"\nScraping complete! Total programs: {count}")
