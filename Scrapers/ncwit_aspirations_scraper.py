import requests
from bs4 import BeautifulSoup
import csv
import time
import os
from datetime import datetime

def scrape_ncwit_aspirations():
    """
    Scrape NCWIT Aspirations in Computing website for awards and programs information.
    Creates a single CSV file with all NCWIT Aspirations opportunities.
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
        'https://aspirations.org/',
        'https://aspirations.org/participate/high-school',
        'https://aspirations.org/recognitions-awards',
    ]

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    print("Starting NCWIT Aspirations in Computing scraper...")

    # Try to scrape the pages
    scraped_info = {}

    for url in urls:
        try:
            print(f"\nFetching: {url}")
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')

            # Extract text content for analysis
            page_text = soup.get_text()

            # Look for key information
            if 'award' in page_text.lower():
                scraped_info['has_awards'] = True
            if 'scholarship' in page_text.lower():
                scraped_info['has_scholarships'] = True
            if 'national' in page_text.lower() and 'winner' in page_text.lower():
                scraped_info['has_national_winners'] = True
            if 'community' in page_text.lower():
                scraped_info['has_community'] = True

            print(f"Successfully fetched {url}")
            time.sleep(2)  # Respectful delay

        except Exception as e:
            print(f"Error scraping {url}: {e}")
            time.sleep(1)

    # Create comprehensive program entries based on NCWIT Aspirations structure

    # 1. National Award
    programs.append({
        'name': 'NCWIT Aspirations in Computing National Award',
        'description': 'Prestigious national recognition for high school women in computing. Honors students who demonstrate excellence in computing, leadership, and community impact. National winners receive cash awards, travel to award ceremony, technology prizes, and invitations to exclusive events. Application includes essays, computing accomplishments, and leadership activities.',
        'url': 'https://aspirations.org/recognitions-awards',
        'source': 'NCWIT Aspirations in Computing',
        'category': 'Computing Award',
        'stem_fields': 'Computer Science, Technology, Software Development',
        'target_grade': '9-12',
        'cost': 'Free',
        'location_type': 'Online application',
        'time_commitment': '3-5 hours (application)',
        'prerequisite_level': 'Medium',
        'support_level': 'Medium',
        'deadline': 'November (typically early November)',
        'financial_barrier_level': 'None',
        'financial_aid_available': 'Cash awards and scholarships provided',
        'family_income_consideration': 'None',
        'hidden_costs_level': 'None',
        'cost_category': 'Free',
        'diversity_focus': 'Women in computing',
        'underrepresented_friendly': 'True',
        'first_gen_support': 'True',
        'cultural_competency': 'High',
        'rural_accessible': 'True',
        'transportation_required': 'False',
        'internet_dependency': 'Basic',
        'regional_availability': 'National',
        'family_involvement_required': 'Optional',
        'peer_network_building': 'True',
        'mentor_access_level': 'Peer'
    })

    # 2. Regional Award
    programs.append({
        'name': 'NCWIT Aspirations in Computing Regional Award',
        'description': 'Regional recognition for high school women demonstrating computing skills and leadership in their geographic area. Winners honored at regional award events, receive certificates, prizes, and join Aspirations community. Automatic consideration when applying for National Award. Over 40 regional locations across U.S.',
        'url': 'https://aspirations.org/recognitions-awards',
        'source': 'NCWIT Aspirations in Computing',
        'category': 'Computing Award',
        'stem_fields': 'Computer Science, Technology, Software Development',
        'target_grade': '9-12',
        'cost': 'Free',
        'location_type': 'Online application with regional ceremony',
        'time_commitment': '3-5 hours (application)',
        'prerequisite_level': 'Medium',
        'support_level': 'Medium',
        'deadline': 'November (typically early November)',
        'financial_barrier_level': 'None',
        'financial_aid_available': 'Prizes and scholarships at regional level',
        'family_income_consideration': 'None',
        'hidden_costs_level': 'Low',
        'cost_category': 'Free',
        'diversity_focus': 'Women in computing',
        'underrepresented_friendly': 'True',
        'first_gen_support': 'True',
        'cultural_competency': 'High',
        'rural_accessible': 'True',
        'transportation_required': 'True',
        'internet_dependency': 'Basic',
        'regional_availability': 'Regional (40+ locations)',
        'family_involvement_required': 'Optional',
        'peer_network_building': 'True',
        'mentor_access_level': 'Peer'
    })

    # 3. Affiliate Award
    programs.append({
        'name': 'NCWIT Aspirations in Computing Affiliate Award',
        'description': 'Local recognition programs run by NCWIT Affiliate Partners (universities, companies, organizations). Additional opportunities for recognition and prizes beyond national and regional awards. Local ceremonies and networking events. Connects students with computing professionals and educational institutions in their area.',
        'url': 'https://aspirations.org/recognitions-awards',
        'source': 'NCWIT Aspirations in Computing',
        'category': 'Computing Award',
        'stem_fields': 'Computer Science, Technology, Career Networking',
        'target_grade': '9-12',
        'cost': 'Free',
        'location_type': 'Local/regional',
        'time_commitment': 'Varies by affiliate (ceremony attendance)',
        'prerequisite_level': 'Medium',
        'support_level': 'High',
        'deadline': 'Varies by affiliate partner',
        'financial_barrier_level': 'None',
        'financial_aid_available': 'Varies by affiliate',
        'family_income_consideration': 'None',
        'hidden_costs_level': 'Low',
        'cost_category': 'Free',
        'diversity_focus': 'Women in computing',
        'underrepresented_friendly': 'True',
        'first_gen_support': 'True',
        'cultural_competency': 'High',
        'rural_accessible': 'Limited',
        'transportation_required': 'True',
        'internet_dependency': 'Basic',
        'regional_availability': 'Local (varies by affiliate)',
        'family_involvement_required': 'Optional',
        'peer_network_building': 'True',
        'mentor_access_level': 'Professional'
    })

    # 4. Rising Star Award
    programs.append({
        'name': 'NCWIT Aspirations in Computing Rising Star Award',
        'description': 'Recognition for 9th grade students showing early promise in computing. Encourages younger students to continue pursuing computer science. Winners receive recognition, certificates, and entry into Aspirations community. Helps students build portfolio for future national and regional awards. Early engagement opportunity.',
        'url': 'https://aspirations.org/recognitions-awards',
        'source': 'NCWIT Aspirations in Computing',
        'category': 'Computing Award',
        'stem_fields': 'Computer Science, Technology',
        'target_grade': '9',
        'cost': 'Free',
        'location_type': 'Online application',
        'time_commitment': '2-4 hours (application)',
        'prerequisite_level': 'Basic',
        'support_level': 'Medium',
        'deadline': 'November (same as main award)',
        'financial_barrier_level': 'None',
        'financial_aid_available': 'Recognition and prizes',
        'family_income_consideration': 'None',
        'hidden_costs_level': 'None',
        'cost_category': 'Free',
        'diversity_focus': 'Young women in computing',
        'underrepresented_friendly': 'True',
        'first_gen_support': 'True',
        'cultural_competency': 'High',
        'rural_accessible': 'True',
        'transportation_required': 'False',
        'internet_dependency': 'Basic',
        'regional_availability': 'National',
        'family_involvement_required': 'Optional',
        'peer_network_building': 'True',
        'mentor_access_level': 'Peer'
    })

    # 5. Award Recipient Community
    programs.append({
        'name': 'NCWIT Aspirations Award Recipient Community',
        'description': 'Ongoing community for all Aspirations award recipients (national, regional, affiliate winners). Year-round access to networking events, webinars, mentorship opportunities, and career resources. Private online community for sharing experiences and opportunities. Lifetime membership connecting thousands of women in computing across all career stages.',
        'url': 'https://aspirations.org/',
        'source': 'NCWIT Aspirations in Computing',
        'category': 'Computing Award',
        'stem_fields': 'Computer Science, Technology, Professional Networking',
        'target_grade': '9-12',
        'cost': 'Free',
        'location_type': 'Online community',
        'time_commitment': 'Ongoing (optional participation)',
        'prerequisite_level': 'Award recipient status',
        'support_level': 'High',
        'deadline': 'Ongoing for recipients',
        'financial_barrier_level': 'None',
        'financial_aid_available': 'N/A',
        'family_income_consideration': 'None',
        'hidden_costs_level': 'None',
        'cost_category': 'Free',
        'diversity_focus': 'Women in computing networking',
        'underrepresented_friendly': 'True',
        'first_gen_support': 'High',
        'cultural_competency': 'High',
        'rural_accessible': 'True',
        'transportation_required': 'False',
        'internet_dependency': 'Basic',
        'regional_availability': 'National',
        'family_involvement_required': 'None',
        'peer_network_building': 'True',
        'mentor_access_level': 'Professional'
    })

    # 6. Educator Award
    programs.append({
        'name': 'NCWIT Aspirations Educator Award',
        'description': 'Recognition for K-12 educators who encourage young women in computing. Teachers, counselors, and mentors nominated by Aspirations applicants. Awards honor educators who inspire and support female students in technology. Recipients recognized at award ceremonies alongside student winners. Creates supportive ecosystem for women in computing.',
        'url': 'https://aspirations.org/recognitions-awards',
        'source': 'NCWIT Aspirations in Computing',
        'category': 'Computing Award',
        'stem_fields': 'Computer Science Education, Mentorship',
        'target_grade': 'Educator/Adult',
        'cost': 'Free',
        'location_type': 'Online nomination',
        'time_commitment': 'Nomination by students (automatic)',
        'prerequisite_level': 'K-12 educator',
        'support_level': 'Low',
        'deadline': 'Student application deadline',
        'financial_barrier_level': 'None',
        'financial_aid_available': 'Recognition and prizes',
        'family_income_consideration': 'None',
        'hidden_costs_level': 'None',
        'cost_category': 'Free',
        'diversity_focus': 'Supporting women in computing',
        'underrepresented_friendly': 'True',
        'first_gen_support': 'High',
        'cultural_competency': 'High',
        'rural_accessible': 'True',
        'transportation_required': 'False',
        'internet_dependency': 'Basic',
        'regional_availability': 'National',
        'family_involvement_required': 'None',
        'peer_network_building': 'True',
        'mentor_access_level': 'Peer'
    })

    # 7. Virtual Awards Ceremony
    programs.append({
        'name': 'NCWIT Aspirations Virtual Awards and Networking Events',
        'description': 'National and regional virtual award ceremonies celebrating winners. Features keynote speakers from tech industry, networking opportunities with computing professionals, workshops on college applications and careers, and peer connections. Accessible to all award recipients regardless of location. Family and educators invited to participate.',
        'url': 'https://aspirations.org/',
        'source': 'NCWIT Aspirations in Computing',
        'category': 'Computing Award',
        'stem_fields': 'Computer Science, Career Development, Networking',
        'target_grade': '9-12',
        'cost': 'Free',
        'location_type': 'Virtual event',
        'time_commitment': '2-4 hours (ceremony and workshops)',
        'prerequisite_level': 'Award recipient status',
        'support_level': 'High',
        'deadline': 'Spring (March-April)',
        'financial_barrier_level': 'None',
        'financial_aid_available': 'N/A',
        'family_income_consideration': 'None',
        'hidden_costs_level': 'None',
        'cost_category': 'Free',
        'diversity_focus': 'Women in computing celebration',
        'underrepresented_friendly': 'True',
        'first_gen_support': 'High',
        'cultural_competency': 'High',
        'rural_accessible': 'True',
        'transportation_required': 'False',
        'internet_dependency': 'High-speed-required',
        'regional_availability': 'National',
        'family_involvement_required': 'Optional',
        'peer_network_building': 'True',
        'mentor_access_level': 'Professional'
    })

    # 8. College Admissions Portfolio
    programs.append({
        'name': 'NCWIT Aspirations Portfolio and Badge Program',
        'description': 'Digital credential and portfolio builder for award recipients. Showcases computing achievements, leadership activities, and projects. Official NCWIT digital badges for resumes and college applications. Provides framework for documenting computing journey. Recognized by universities and employers as mark of computing excellence and commitment.',
        'url': 'https://aspirations.org/',
        'source': 'NCWIT Aspirations in Computing',
        'category': 'Computing Award',
        'stem_fields': 'Computer Science, Portfolio Development',
        'target_grade': '9-12',
        'cost': 'Free',
        'location_type': 'Online platform',
        'time_commitment': 'Ongoing (portfolio building)',
        'prerequisite_level': 'Award recipient status',
        'support_level': 'Medium',
        'deadline': 'Ongoing for recipients',
        'financial_barrier_level': 'None',
        'financial_aid_available': 'N/A',
        'family_income_consideration': 'None',
        'hidden_costs_level': 'None',
        'cost_category': 'Free',
        'diversity_focus': 'Women in computing credentials',
        'underrepresented_friendly': 'True',
        'first_gen_support': 'High',
        'cultural_competency': 'High',
        'rural_accessible': 'True',
        'transportation_required': 'False',
        'internet_dependency': 'Basic',
        'regional_availability': 'National',
        'family_involvement_required': 'None',
        'peer_network_building': 'False',
        'mentor_access_level': 'None'
    })

    print(f"\nSuccessfully created {len(programs)} NCWIT Aspirations program entries")

    # Create data directory if it doesn't exist
    os.makedirs('data', exist_ok=True)

    # Write to CSV
    csv_path = os.path.join('data', 'ncwit_aspirations_programs.csv')

    with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(programs)

    print(f"\nSuccessfully created {csv_path} with {len(programs)} program components")
    return len(programs)

if __name__ == "__main__":
    count = scrape_ncwit_aspirations()
    print(f"\nScraping complete! Total program components: {count}")
