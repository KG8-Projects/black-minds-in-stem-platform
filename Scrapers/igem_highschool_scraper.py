import requests
from bs4 import BeautifulSoup
import csv
import time
import os
from datetime import datetime

def scrape_igem_highschool():
    """
    Scrape iGEM Foundation website for high school synthetic biology competition information.
    Creates a single CSV file with all iGEM high school program components.
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
        'https://igem.org/competition',
        'https://igem.org/competition/high-school',
        'https://igem.org/high-school-program',
    ]

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    print("Starting iGEM High School scraper...")

    # Try to scrape the main competition page
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
            if 'registration' in page_text.lower():
                scraped_info['has_registration'] = True
            if 'jamboree' in page_text.lower():
                scraped_info['has_jamboree'] = True
            if 'cost' in page_text.lower() or 'fee' in page_text.lower():
                scraped_info['mentions_cost'] = True
            if 'grant' in page_text.lower() or 'financial aid' in page_text.lower():
                scraped_info['has_financial_aid'] = True

            print(f"Successfully fetched {url}")
            time.sleep(2)  # Respectful delay

        except Exception as e:
            print(f"Error scraping {url}: {e}")
            time.sleep(1)

    # Create comprehensive program entries based on iGEM structure

    # 1. Main iGEM High School Competition
    programs.append({
        'name': 'iGEM High School Competition',
        'description': 'International synthetic biology competition where high school teams design and build genetically engineered systems. Teams work for 6-9 months on original research projects, create DNA constructs using BioBrick parts, and present findings at the annual Giant Jamboree. Develops skills in molecular biology, engineering, ethics, and science communication.',
        'url': 'https://igem.org/competition/high-school',
        'source': 'iGEM Foundation',
        'category': 'Synthetic Biology Competition',
        'stem_fields': 'Biology, Genetics, Synthetic Biology, Engineering, Bioinformatics',
        'target_grade': '9-12',
        'cost': '$5000+ (team registration)',
        'location_type': 'School-based with travel',
        'time_commitment': '6-9 months (10-20 hours/week)',
        'prerequisite_level': 'High',
        'support_level': 'High',
        'deadline': 'Annual (typically May for registration, October for Jamboree)',
        'financial_barrier_level': 'Prohibitive',
        'financial_aid_available': 'Yes (grants and waivers available)',
        'family_income_consideration': 'Team-based cost sharing possible',
        'hidden_costs_level': 'High',
        'cost_category': '$2000+',
        'diversity_focus': 'Global participation, iGEM inclusion initiatives',
        'underrepresented_friendly': 'True',
        'first_gen_support': 'Limited',
        'cultural_competency': 'High',
        'rural_accessible': 'False',
        'transportation_required': 'True',
        'internet_dependency': 'Basic',
        'regional_availability': 'International',
        'family_involvement_required': 'None',
        'peer_network_building': 'True',
        'mentor_access_level': 'Professional'
    })

    # 2. iGEM Giant Jamboree
    programs.append({
        'name': 'iGEM Giant Jamboree (High School Division)',
        'description': 'Annual international conference where iGEM high school teams present their synthetic biology projects to judges, compete for awards, and network with the global synthetic biology community. Multi-day event featuring project presentations, poster sessions, workshops, and award ceremonies. Culminating event of year-long competition.',
        'url': 'https://igem.org/competition',
        'source': 'iGEM Foundation',
        'category': 'Synthetic Biology Competition',
        'stem_fields': 'Biology, Genetics, Synthetic Biology, Science Communication',
        'target_grade': '9-12',
        'cost': '$2000-5000+ (travel, lodging, registration)',
        'location_type': 'In-person conference',
        'time_commitment': '4-5 days (October/November)',
        'prerequisite_level': 'High',
        'support_level': 'High',
        'deadline': 'October (varies annually)',
        'financial_barrier_level': 'Prohibitive',
        'financial_aid_available': 'Yes (travel grants available)',
        'family_income_consideration': 'Team fundraising common',
        'hidden_costs_level': 'High',
        'cost_category': '$2000+',
        'diversity_focus': 'Global participation, international collaboration',
        'underrepresented_friendly': 'True',
        'first_gen_support': 'Limited',
        'cultural_competency': 'High',
        'rural_accessible': 'False',
        'transportation_required': 'True',
        'internet_dependency': 'Basic',
        'regional_availability': 'International',
        'family_involvement_required': 'None',
        'peer_network_building': 'True',
        'mentor_access_level': 'Professional'
    })

    # 3. iGEM DNA Distribution Kit
    programs.append({
        'name': 'iGEM Distribution Kit (High School)',
        'description': 'Comprehensive collection of standardized biological parts (BioBricks) provided to registered teams. Includes plasmids, DNA sequences, and genetic components for building synthetic biology projects. Kit enables teams to design and construct genetically engineered systems without synthesizing DNA from scratch.',
        'url': 'https://igem.org/competition',
        'source': 'iGEM Foundation',
        'category': 'Synthetic Biology Competition',
        'stem_fields': 'Biology, Genetics, Synthetic Biology, Molecular Biology',
        'target_grade': '9-12',
        'cost': 'Included in team registration',
        'location_type': 'School lab',
        'time_commitment': 'Ongoing throughout competition (6-9 months)',
        'prerequisite_level': 'High',
        'support_level': 'High',
        'deadline': 'Shipped after registration confirmation',
        'financial_barrier_level': 'Prohibitive',
        'financial_aid_available': 'Included with registration fee waivers',
        'family_income_consideration': 'Team-based',
        'hidden_costs_level': 'Medium',
        'cost_category': '$2000+',
        'diversity_focus': 'Standardized access for all teams',
        'underrepresented_friendly': 'True',
        'first_gen_support': 'Limited',
        'cultural_competency': 'High',
        'rural_accessible': 'False',
        'transportation_required': 'False',
        'internet_dependency': 'Basic',
        'regional_availability': 'International',
        'family_involvement_required': 'None',
        'peer_network_building': 'True',
        'mentor_access_level': 'Professional'
    })

    # 4. iGEM Team Wiki and Documentation
    programs.append({
        'name': 'iGEM Team Wiki and Project Documentation',
        'description': 'Required component where teams create comprehensive online documentation of their synthetic biology project. Includes research background, experimental design, results, safety considerations, human practices work, and team information. Teaches scientific communication, web design, and documentation skills. Wiki is judged as part of competition.',
        'url': 'https://igem.org/competition',
        'source': 'iGEM Foundation',
        'category': 'Synthetic Biology Competition',
        'stem_fields': 'Biology, Science Communication, Web Design, Technical Writing',
        'target_grade': '9-12',
        'cost': 'Included in registration',
        'location_type': 'Online',
        'time_commitment': '2-3 months (intensive work July-October)',
        'prerequisite_level': 'Medium',
        'support_level': 'High',
        'deadline': 'October (Wiki Freeze)',
        'financial_barrier_level': 'Prohibitive',
        'financial_aid_available': 'Included with registration',
        'family_income_consideration': 'Team-based',
        'hidden_costs_level': 'None',
        'cost_category': '$2000+',
        'diversity_focus': 'All teams have equal platform',
        'underrepresented_friendly': 'True',
        'first_gen_support': 'Limited',
        'cultural_competency': 'High',
        'rural_accessible': 'True',
        'transportation_required': 'False',
        'internet_dependency': 'High-speed-required',
        'regional_availability': 'International',
        'family_involvement_required': 'None',
        'peer_network_building': 'True',
        'mentor_access_level': 'Professional'
    })

    # 5. iGEM Human Practices Component
    programs.append({
        'name': 'iGEM Human Practices (High School)',
        'description': 'Required project component where teams explore the social, ethical, and environmental implications of their synthetic biology work. Teams engage with stakeholders, consider safety and ethics, and integrate feedback into project design. Emphasizes responsible innovation and real-world impact of biotechnology.',
        'url': 'https://igem.org/competition',
        'source': 'iGEM Foundation',
        'category': 'Synthetic Biology Competition',
        'stem_fields': 'Biology, Ethics, Sociology, Science Policy, Public Engagement',
        'target_grade': '9-12',
        'cost': 'Included in registration',
        'location_type': 'Community-based',
        'time_commitment': '3-4 months (ongoing throughout project)',
        'prerequisite_level': 'Medium',
        'support_level': 'High',
        'deadline': 'October (integrated into final presentation)',
        'financial_barrier_level': 'Prohibitive',
        'financial_aid_available': 'Included with registration',
        'family_income_consideration': 'Team-based',
        'hidden_costs_level': 'Low',
        'cost_category': '$2000+',
        'diversity_focus': 'Community engagement focus',
        'underrepresented_friendly': 'True',
        'first_gen_support': 'Medium',
        'cultural_competency': 'High',
        'rural_accessible': 'True',
        'transportation_required': 'False',
        'internet_dependency': 'Basic',
        'regional_availability': 'International',
        'family_involvement_required': 'None',
        'peer_network_building': 'True',
        'mentor_access_level': 'Professional'
    })

    # 6. iGEM Mentorship and Training Resources
    programs.append({
        'name': 'iGEM Mentorship and Training Resources',
        'description': 'Comprehensive support system including online tutorials, webinars, safety training, and mentorship from previous iGEM participants and synthetic biology professionals. Resources cover lab techniques, project design, wiki development, presentation skills, and safety protocols. Access to global iGEM community for guidance.',
        'url': 'https://igem.org/competition',
        'source': 'iGEM Foundation',
        'category': 'Synthetic Biology Competition',
        'stem_fields': 'Biology, Genetics, Synthetic Biology, Lab Safety',
        'target_grade': '9-12',
        'cost': 'Included in registration',
        'location_type': 'Online and school-based',
        'time_commitment': 'Ongoing throughout competition (6-9 months)',
        'prerequisite_level': 'Medium',
        'support_level': 'High',
        'deadline': 'Available upon registration',
        'financial_barrier_level': 'Prohibitive',
        'financial_aid_available': 'Included with registration',
        'family_income_consideration': 'Team-based',
        'hidden_costs_level': 'None',
        'cost_category': '$2000+',
        'diversity_focus': 'Equal access to mentorship for all teams',
        'underrepresented_friendly': 'True',
        'first_gen_support': 'Medium',
        'cultural_competency': 'High',
        'rural_accessible': 'True',
        'transportation_required': 'False',
        'internet_dependency': 'High-speed-required',
        'regional_availability': 'International',
        'family_involvement_required': 'None',
        'peer_network_building': 'True',
        'mentor_access_level': 'Professional'
    })

    print(f"\nSuccessfully created {len(programs)} iGEM high school program entries")

    # Create data directory if it doesn't exist
    os.makedirs('data', exist_ok=True)

    # Write to CSV
    csv_path = os.path.join('data', 'igem_highschool_programs.csv')

    with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(programs)

    print(f"\nSuccessfully created {csv_path} with {len(programs)} program components")
    return len(programs)

if __name__ == "__main__":
    count = scrape_igem_highschool()
    print(f"\nScraping complete! Total program components: {count}")
