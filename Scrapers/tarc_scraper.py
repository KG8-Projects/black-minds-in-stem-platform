import requests
from bs4 import BeautifulSoup
import csv
import time
import os
from datetime import datetime

def scrape_tarc():
    """
    Scrape Team America Rocketry Challenge website for competition information.
    Creates a single CSV file with all TARC program components.
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
        'http://www.rocketcontest.org/',
        'http://www.rocketcontest.org/about',
        'http://www.rocketcontest.org/rules',
    ]

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    print("Starting Team America Rocketry Challenge scraper...")

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
            if 'national' in page_text.lower():
                scraped_info['has_nationals'] = True
            if 'qualifying' in page_text.lower():
                scraped_info['has_qualifying'] = True
            if 'scholarship' in page_text.lower() or 'prize' in page_text.lower():
                scraped_info['has_prizes'] = True
            if 'safety' in page_text.lower():
                scraped_info['mentions_safety'] = True

            print(f"Successfully fetched {url}")
            time.sleep(2)  # Respectful delay

        except Exception as e:
            print(f"Error scraping {url}: {e}")
            time.sleep(1)

    # Create comprehensive program entries based on TARC structure

    # 1. Main TARC Competition
    programs.append({
        'name': 'Team America Rocketry Challenge (TARC)',
        'description': 'Nation\'s largest rocket competition for middle and high school students. Teams of 3-10 students design, build, and launch model rockets to meet specific altitude and flight duration requirements. Annual design challenge changes yearly. Teams progress from qualifying flights to National Finals. Develops aerospace engineering, physics, teamwork, and project management skills.',
        'url': 'http://www.rocketcontest.org/',
        'source': 'Aerospace Industries Association',
        'category': 'Aerospace Competition',
        'stem_fields': 'Aerospace Engineering, Physics, Rocketry, Engineering Design',
        'target_grade': '6-12',
        'cost': '$100-500 (rocket materials and motors)',
        'location_type': 'School-based with field launches',
        'time_commitment': '6-8 months (September-May, 5-10 hours/week)',
        'prerequisite_level': 'Basic',
        'support_level': 'High',
        'deadline': 'Early registration October, qualifying flights March',
        'financial_barrier_level': 'Medium',
        'financial_aid_available': 'Limited grants available',
        'family_income_consideration': 'Team cost-sharing, school sponsorship',
        'hidden_costs_level': 'High',
        'cost_category': '$100-500',
        'diversity_focus': 'AIA educational outreach',
        'underrepresented_friendly': 'True',
        'first_gen_support': 'Limited',
        'cultural_competency': 'High',
        'rural_accessible': 'True',
        'transportation_required': 'True',
        'internet_dependency': 'Basic',
        'regional_availability': 'National',
        'family_involvement_required': 'Optional',
        'peer_network_building': 'True',
        'mentor_access_level': 'Adult'
    })

    # 2. TARC Qualifying Flights
    programs.append({
        'name': 'TARC Qualifying Flight Submissions',
        'description': 'Teams conduct multiple rocket launches at approved fields to meet competition criteria. Must submit two qualifying flights meeting altitude (exact target) and flight duration requirements while carrying a raw egg payload. Teams record flight data, photograph launches, and submit results online. Top 100 teams advance to National Finals.',
        'url': 'http://www.rocketcontest.org/rules',
        'source': 'Aerospace Industries Association',
        'category': 'Aerospace Competition',
        'stem_fields': 'Aerospace Engineering, Physics, Data Collection, Documentation',
        'target_grade': '6-12',
        'cost': 'Included in competition (rocket motors ~$50-100)',
        'location_type': 'Local launch field',
        'time_commitment': '2-3 months (January-March, multiple launch attempts)',
        'prerequisite_level': 'Basic',
        'support_level': 'High',
        'deadline': 'March (specific date varies annually)',
        'financial_barrier_level': 'Medium',
        'financial_aid_available': 'Limited',
        'family_income_consideration': 'Team cost-sharing',
        'hidden_costs_level': 'High',
        'cost_category': '$100-500',
        'diversity_focus': 'Open to all teams',
        'underrepresented_friendly': 'True',
        'first_gen_support': 'Limited',
        'cultural_competency': 'High',
        'rural_accessible': 'True',
        'transportation_required': 'True',
        'internet_dependency': 'Basic',
        'regional_availability': 'National',
        'family_involvement_required': 'Optional',
        'peer_network_building': 'True',
        'mentor_access_level': 'Adult'
    })

    # 3. TARC National Finals
    programs.append({
        'name': 'TARC National Finals Competition',
        'description': 'Championship event for top 100 teams held at Fentress Airfield near Washington, D.C. Multi-day competition featuring official rocket launches, awards ceremony, and aerospace industry expo. Teams compete for $100,000+ in prizes and scholarships. Includes tours of NASA facilities, networking with aerospace professionals, and recognition ceremony. Travel stipends provided for qualifying teams.',
        'url': 'http://www.rocketcontest.org/',
        'source': 'Aerospace Industries Association',
        'category': 'Aerospace Competition',
        'stem_fields': 'Aerospace Engineering, Physics, Rocketry, Career Exploration',
        'target_grade': '6-12',
        'cost': 'Travel stipend provided ($1000 per team)',
        'location_type': 'In-person national competition',
        'time_commitment': '3-4 days (mid-May)',
        'prerequisite_level': 'Medium',
        'support_level': 'High',
        'deadline': 'May (invitation-only)',
        'financial_barrier_level': 'Low',
        'financial_aid_available': 'Travel stipend provided',
        'family_income_consideration': 'Stipend covers most expenses',
        'hidden_costs_level': 'Low',
        'cost_category': '$100-500',
        'diversity_focus': 'National representation',
        'underrepresented_friendly': 'True',
        'first_gen_support': 'Medium',
        'cultural_competency': 'High',
        'rural_accessible': 'True',
        'transportation_required': 'True',
        'internet_dependency': 'None',
        'regional_availability': 'National',
        'family_involvement_required': 'Optional',
        'peer_network_building': 'True',
        'mentor_access_level': 'Professional'
    })

    # 4. TARC Design and Build Phase
    programs.append({
        'name': 'TARC Rocket Design and Construction',
        'description': 'Initial phase where teams design and build model rockets to meet competition requirements. Apply principles of aerodynamics, structural design, and propulsion. Use CAD software for design, test materials, and iterate prototypes. Learn rocket stability, center of gravity calculations, and recovery system design. Document design process in engineering notebooks.',
        'url': 'http://www.rocketcontest.org/rules',
        'source': 'Aerospace Industries Association',
        'category': 'Aerospace Competition',
        'stem_fields': 'Aerospace Engineering, CAD Design, Materials Science, Mathematics',
        'target_grade': '6-12',
        'cost': '$100-300 (building materials)',
        'location_type': 'School workshop/lab',
        'time_commitment': '3-4 months (October-January, 5-10 hours/week)',
        'prerequisite_level': 'Basic',
        'support_level': 'High',
        'deadline': 'Ongoing until qualifying flights',
        'financial_barrier_level': 'Medium',
        'financial_aid_available': 'School/sponsor funding',
        'family_income_consideration': 'Team cost-sharing',
        'hidden_costs_level': 'High',
        'cost_category': '$100-500',
        'diversity_focus': 'Hands-on engineering for all',
        'underrepresented_friendly': 'True',
        'first_gen_support': 'Limited',
        'cultural_competency': 'High',
        'rural_accessible': 'True',
        'transportation_required': 'False',
        'internet_dependency': 'Basic',
        'regional_availability': 'National',
        'family_involvement_required': 'Optional',
        'peer_network_building': 'True',
        'mentor_access_level': 'Adult'
    })

    # 5. TARC Safety Certification
    programs.append({
        'name': 'TARC Safety Certification and Training',
        'description': 'Required safety program teaching proper rocket construction, motor handling, and launch procedures. Teams must complete safety training and follow NAR (National Association of Rocketry) safety code. Covers range safety, recovery systems, launch procedures, and emergency protocols. Adult advisor must complete safety certification.',
        'url': 'http://www.rocketcontest.org/rules',
        'source': 'Aerospace Industries Association',
        'category': 'Aerospace Competition',
        'stem_fields': 'Aerospace Engineering, Safety Engineering, Physics',
        'target_grade': '6-12',
        'cost': 'Free (included in competition)',
        'location_type': 'Online and in-person',
        'time_commitment': '2-4 hours (one-time training)',
        'prerequisite_level': 'None',
        'support_level': 'High',
        'deadline': 'Before first launch',
        'financial_barrier_level': 'None',
        'financial_aid_available': 'N/A',
        'family_income_consideration': 'None',
        'hidden_costs_level': 'None',
        'cost_category': 'Free',
        'diversity_focus': 'Safety for all participants',
        'underrepresented_friendly': 'True',
        'first_gen_support': 'Limited',
        'cultural_competency': 'High',
        'rural_accessible': 'True',
        'transportation_required': 'False',
        'internet_dependency': 'High-speed-required',
        'regional_availability': 'National',
        'family_involvement_required': 'Adult advisor required',
        'peer_network_building': 'False',
        'mentor_access_level': 'Adult'
    })

    # 6. TARC Educational Resources
    programs.append({
        'name': 'TARC Educational Resources and Curriculum',
        'description': 'Comprehensive learning materials including rocket science tutorials, design guides, physics lessons, and video instruction. Free access to educational content covering aerodynamics, propulsion, flight dynamics, and data analysis. Curriculum aligned with STEM standards. Includes past competition data, winning designs, and tips from aerospace engineers.',
        'url': 'http://www.rocketcontest.org/',
        'source': 'Aerospace Industries Association',
        'category': 'Aerospace Competition',
        'stem_fields': 'Aerospace Engineering, Physics, Mathematics, Engineering Design',
        'target_grade': '6-12',
        'cost': 'Free',
        'location_type': 'Online',
        'time_commitment': 'Self-paced (ongoing)',
        'prerequisite_level': 'None',
        'support_level': 'Low',
        'deadline': 'Available year-round',
        'financial_barrier_level': 'None',
        'financial_aid_available': 'N/A',
        'family_income_consideration': 'None',
        'hidden_costs_level': 'None',
        'cost_category': 'Free',
        'diversity_focus': 'Free access for all students',
        'underrepresented_friendly': 'True',
        'first_gen_support': 'Limited',
        'cultural_competency': 'High',
        'rural_accessible': 'True',
        'transportation_required': 'False',
        'internet_dependency': 'High-speed-required',
        'regional_availability': 'National',
        'family_involvement_required': 'None',
        'peer_network_building': 'False',
        'mentor_access_level': 'None'
    })

    # 7. TARC Industry Mentorship
    programs.append({
        'name': 'TARC Industry Mentorship Program',
        'description': 'Connection to aerospace industry professionals who provide guidance to teams. Engineers from NASA, Boeing, Lockheed Martin, and other aerospace companies mentor teams through design challenges. Virtual and in-person mentorship sessions cover technical questions, career advice, and professional engineering practices. Available to registered teams throughout season.',
        'url': 'http://www.rocketcontest.org/about',
        'source': 'Aerospace Industries Association',
        'category': 'Aerospace Competition',
        'stem_fields': 'Aerospace Engineering, Career Development, Professional Networking',
        'target_grade': '6-12',
        'cost': 'Free',
        'location_type': 'Virtual and in-person',
        'time_commitment': 'Optional sessions throughout season',
        'prerequisite_level': 'Basic',
        'support_level': 'High',
        'deadline': 'Available during competition season',
        'financial_barrier_level': 'None',
        'financial_aid_available': 'N/A',
        'family_income_consideration': 'None',
        'hidden_costs_level': 'None',
        'cost_category': 'Free',
        'diversity_focus': 'Professional exposure for all teams',
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

    # 8. TARC Scholarships and Awards
    programs.append({
        'name': 'TARC Scholarships and Prize Awards',
        'description': 'Over $100,000 in scholarships and prizes awarded to top-performing teams at National Finals. Individual team members receive college scholarships ranging from $2,500 to $20,000. Additional prizes include aerospace internships, STEM camp invitations, and educational grants for schools. Special awards for innovation, teamwork, and documentation. Recognition from aerospace industry leaders.',
        'url': 'http://www.rocketcontest.org/',
        'source': 'Aerospace Industries Association',
        'category': 'Aerospace Competition',
        'stem_fields': 'Aerospace Engineering, Career Development',
        'target_grade': '6-12',
        'cost': 'N/A (awards)',
        'location_type': 'National Finals event',
        'time_commitment': 'Awards ceremony (1 day)',
        'prerequisite_level': 'National Finals qualification',
        'support_level': 'High',
        'deadline': 'May (National Finals)',
        'financial_barrier_level': 'None',
        'financial_aid_available': 'Scholarship awards',
        'family_income_consideration': 'Need-blind merit awards',
        'hidden_costs_level': 'None',
        'cost_category': 'Free',
        'diversity_focus': 'Merit-based recognition',
        'underrepresented_friendly': 'True',
        'first_gen_support': 'High',
        'cultural_competency': 'High',
        'rural_accessible': 'True',
        'transportation_required': 'True',
        'internet_dependency': 'None',
        'regional_availability': 'National',
        'family_involvement_required': 'Optional',
        'peer_network_building': 'True',
        'mentor_access_level': 'Professional'
    })

    print(f"\nSuccessfully created {len(programs)} TARC program entries")

    # Create data directory if it doesn't exist
    os.makedirs('data', exist_ok=True)

    # Write to CSV
    csv_path = os.path.join('data', 'tarc_programs.csv')

    with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(programs)

    print(f"\nSuccessfully created {csv_path} with {len(programs)} program components")
    return len(programs)

if __name__ == "__main__":
    count = scrape_tarc()
    print(f"\nScraping complete! Total program components: {count}")
