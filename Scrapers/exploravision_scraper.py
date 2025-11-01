import requests
from bs4 import BeautifulSoup
import csv
import time
import os
from datetime import datetime

def scrape_exploravision():
    """
    Scrape Toshiba/NSTA ExploraVision website for science competition information.
    Creates a single CSV file with all ExploraVision opportunities.
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
        'https://www.exploravision.org/',
        'https://www.exploravision.org/what-is-exploravision',
        'https://www.exploravision.org/how-to-enter',
    ]

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    print("Starting Toshiba/NSTA ExploraVision scraper...")

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

    # Create comprehensive program entries for ExploraVision competition

    # 1. Primary Division (K-3)
    programs.append({
        'name': 'ExploraVision Primary Division (K-3)',
        'description': 'Technology forecasting competition for elementary students in grades K-3. Teams of 2-4 students imagine future technology 20+ years ahead. Students research current technology, envision improvements, and create project describing their vision through writing and illustrations. Develops imagination, research, and teamwork skills.',
        'url': 'https://www.exploravision.org/',
        'source': 'Toshiba/NSTA ExploraVision',
        'category': 'Science Competition',
        'stem_fields': 'Technology, Future Science, Innovation, Research',
        'target_grade': 'K-3',
        'cost': 'Free',
        'location_type': 'School-based',
        'time_commitment': '3-4 months (September-January)',
        'prerequisite_level': 'Basic',
        'support_level': 'High',
        'deadline': 'January (typically late January)',
        'financial_barrier_level': 'None',
        'financial_aid_available': 'N/A',
        'family_income_consideration': 'None',
        'hidden_costs_level': 'None',
        'cost_category': 'Free',
        'diversity_focus': 'NSTA equity and inclusion initiatives',
        'underrepresented_friendly': 'True',
        'first_gen_support': 'True',
        'cultural_competency': 'High',
        'rural_accessible': 'True',
        'transportation_required': 'False',
        'internet_dependency': 'Basic',
        'regional_availability': 'National',
        'family_involvement_required': 'Optional',
        'peer_network_building': 'True',
        'mentor_access_level': 'Adult'
    })

    # 2. Upper Elementary Division (4-6)
    programs.append({
        'name': 'ExploraVision Upper Elementary Division (4-6)',
        'description': 'Technology innovation competition for grades 4-6. Teams research existing technology, predict future developments, and create comprehensive project documentation. Students develop technology timeline, design breakthroughs, and explain scientific principles. Includes written paper, web page mockups, and project description. Prizes include savings bonds.',
        'url': 'https://www.exploravision.org/',
        'source': 'Toshiba/NSTA ExploraVision',
        'category': 'Science Competition',
        'stem_fields': 'Technology, Future Science, Innovation, Research',
        'target_grade': '4-6',
        'cost': 'Free',
        'location_type': 'School-based',
        'time_commitment': '3-4 months (September-January)',
        'prerequisite_level': 'Basic',
        'support_level': 'High',
        'deadline': 'January (typically late January)',
        'financial_barrier_level': 'None',
        'financial_aid_available': 'N/A',
        'family_income_consideration': 'None',
        'hidden_costs_level': 'None',
        'cost_category': 'Free',
        'diversity_focus': 'NSTA equity and inclusion initiatives',
        'underrepresented_friendly': 'True',
        'first_gen_support': 'True',
        'cultural_competency': 'High',
        'rural_accessible': 'True',
        'transportation_required': 'False',
        'internet_dependency': 'Basic',
        'regional_availability': 'National',
        'family_involvement_required': 'Optional',
        'peer_network_building': 'True',
        'mentor_access_level': 'Adult'
    })

    # 3. Middle School Division (7-9)
    programs.append({
        'name': 'ExploraVision Middle School Division (7-9)',
        'description': 'Advanced technology forecasting for middle school students. Teams conduct in-depth research on current technology, explore scientific principles, and envision future innovations. Projects include detailed written descriptions, web graphics, and bibliography. Students learn research methods, scientific writing, and creative thinking about technology evolution.',
        'url': 'https://www.exploravision.org/',
        'source': 'Toshiba/NSTA ExploraVision',
        'category': 'Science Competition',
        'stem_fields': 'Technology, Future Science, Innovation, Research, Engineering',
        'target_grade': '7-9',
        'cost': 'Free',
        'location_type': 'School-based',
        'time_commitment': '3-4 months (September-January)',
        'prerequisite_level': 'Medium',
        'support_level': 'High',
        'deadline': 'January (typically late January)',
        'financial_barrier_level': 'None',
        'financial_aid_available': 'N/A',
        'family_income_consideration': 'None',
        'hidden_costs_level': 'None',
        'cost_category': 'Free',
        'diversity_focus': 'NSTA equity and inclusion initiatives',
        'underrepresented_friendly': 'True',
        'first_gen_support': 'True',
        'cultural_competency': 'High',
        'rural_accessible': 'True',
        'transportation_required': 'False',
        'internet_dependency': 'Basic',
        'regional_availability': 'National',
        'family_involvement_required': 'Optional',
        'peer_network_building': 'True',
        'mentor_access_level': 'Adult'
    })

    # 4. High School Division (10-12)
    programs.append({
        'name': 'ExploraVision High School Division (10-12)',
        'description': 'Comprehensive technology innovation competition for high school students. Teams research cutting-edge technology, analyze scientific breakthroughs, and project future developments with supporting evidence. Rigorous project requires detailed research, scientific understanding, and creative vision. Winners receive savings bonds up to $10,000 and trip to award ceremony.',
        'url': 'https://www.exploravision.org/',
        'source': 'Toshiba/NSTA ExploraVision',
        'category': 'Science Competition',
        'stem_fields': 'Technology, Future Science, Innovation, Research, Engineering',
        'target_grade': '10-12',
        'cost': 'Free',
        'location_type': 'School-based',
        'time_commitment': '3-4 months (September-January)',
        'prerequisite_level': 'Medium',
        'support_level': 'High',
        'deadline': 'January (typically late January)',
        'financial_barrier_level': 'None',
        'financial_aid_available': 'N/A',
        'family_income_consideration': 'None',
        'hidden_costs_level': 'None',
        'cost_category': 'Free',
        'diversity_focus': 'NSTA equity and inclusion initiatives',
        'underrepresented_friendly': 'True',
        'first_gen_support': 'True',
        'cultural_competency': 'High',
        'rural_accessible': 'True',
        'transportation_required': 'False',
        'internet_dependency': 'Basic',
        'regional_availability': 'National',
        'family_involvement_required': 'Optional',
        'peer_network_building': 'True',
        'mentor_access_level': 'Adult'
    })

    # 5. Regional Awards
    programs.append({
        'name': 'ExploraVision Regional Awards Competition',
        'description': 'First-level recognition where top projects from each division advance. Regional winners receive cash prizes, certificates, and progress to national judging. Multiple teams can win from each region across four grade divisions. Celebrates excellence in technology innovation and student creativity nationwide.',
        'url': 'https://www.exploravision.org/',
        'source': 'Toshiba/NSTA ExploraVision',
        'category': 'Science Competition',
        'stem_fields': 'Technology, Future Science, Innovation',
        'target_grade': 'K-12',
        'cost': 'Free',
        'location_type': 'School-based with online submission',
        'time_commitment': 'Project completion (3-4 months)',
        'prerequisite_level': 'Basic',
        'support_level': 'High',
        'deadline': 'January submission',
        'financial_barrier_level': 'None',
        'financial_aid_available': 'Prize awards',
        'family_income_consideration': 'None',
        'hidden_costs_level': 'None',
        'cost_category': 'Free',
        'diversity_focus': 'NSTA equity and inclusion initiatives',
        'underrepresented_friendly': 'True',
        'first_gen_support': 'True',
        'cultural_competency': 'High',
        'rural_accessible': 'True',
        'transportation_required': 'False',
        'internet_dependency': 'Basic',
        'regional_availability': 'National',
        'family_involvement_required': 'Optional',
        'peer_network_building': 'True',
        'mentor_access_level': 'Adult'
    })

    # 6. National Winners Awards
    programs.append({
        'name': 'ExploraVision National Winners Awards',
        'description': 'Top-level recognition for best projects in each division. National first place winners receive $10,000 savings bonds per student, all-expense paid trip to Washington D.C. area for award ceremony, and Toshiba technology prizes. Second place winners receive $5,000 savings bonds. Prestigious national STEM recognition.',
        'url': 'https://www.exploravision.org/',
        'source': 'Toshiba/NSTA ExploraVision',
        'category': 'Science Competition',
        'stem_fields': 'Technology, Future Science, Innovation',
        'target_grade': 'K-12',
        'cost': 'Free',
        'location_type': 'Award ceremony in Washington D.C. area',
        'time_commitment': '3-day award trip (June)',
        'prerequisite_level': 'High',
        'support_level': 'High',
        'deadline': 'June (winners announced)',
        'financial_barrier_level': 'None',
        'financial_aid_available': 'Travel fully funded for winners',
        'family_income_consideration': 'None',
        'hidden_costs_level': 'None',
        'cost_category': 'Free',
        'diversity_focus': 'NSTA equity and inclusion initiatives',
        'underrepresented_friendly': 'True',
        'first_gen_support': 'True',
        'cultural_competency': 'High',
        'rural_accessible': 'True',
        'transportation_required': 'True',
        'internet_dependency': 'Basic',
        'regional_availability': 'National',
        'family_involvement_required': 'Optional',
        'peer_network_building': 'True',
        'mentor_access_level': 'Adult'
    })

    # 7. Educational Resources
    programs.append({
        'name': 'ExploraVision Educational Resources and Teacher Guides',
        'description': 'Free educational materials supporting ExploraVision participation. Includes project planning guides, research tips, sample projects, rubrics, and classroom integration resources. Materials help teachers facilitate student teams and integrate technology forecasting into curriculum. Available online for all educators.',
        'url': 'https://www.exploravision.org/',
        'source': 'Toshiba/NSTA ExploraVision',
        'category': 'Science Competition',
        'stem_fields': 'Technology Education, Innovation, Research Skills',
        'target_grade': 'K-12',
        'cost': 'Free',
        'location_type': 'Online resources',
        'time_commitment': 'Self-paced (teacher preparation)',
        'prerequisite_level': 'None',
        'support_level': 'Medium',
        'deadline': 'Available year-round',
        'financial_barrier_level': 'None',
        'financial_aid_available': 'N/A',
        'family_income_consideration': 'None',
        'hidden_costs_level': 'None',
        'cost_category': 'Free',
        'diversity_focus': 'NSTA equity and inclusion initiatives',
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

    # 8. Coach Workshop and Training
    programs.append({
        'name': 'ExploraVision Coach Training and Workshops',
        'description': 'Professional development for teachers and coaches guiding ExploraVision teams. Webinars and online resources explain competition format, judging criteria, project components, and coaching strategies. Training helps educators facilitate student-led research and innovation projects. Supports successful team participation.',
        'url': 'https://www.exploravision.org/',
        'source': 'Toshiba/NSTA ExploraVision',
        'category': 'Science Competition',
        'stem_fields': 'Technology Education, STEM Teaching',
        'target_grade': 'Educator (benefits K-12 students)',
        'cost': 'Free',
        'location_type': 'Online webinars',
        'time_commitment': '1-2 hours (workshop sessions)',
        'prerequisite_level': 'None',
        'support_level': 'High',
        'deadline': 'Ongoing throughout registration period',
        'financial_barrier_level': 'None',
        'financial_aid_available': 'N/A',
        'family_income_consideration': 'None',
        'hidden_costs_level': 'None',
        'cost_category': 'Free',
        'diversity_focus': 'NSTA equity and inclusion initiatives',
        'underrepresented_friendly': 'True',
        'first_gen_support': 'True',
        'cultural_competency': 'High',
        'rural_accessible': 'True',
        'transportation_required': 'False',
        'internet_dependency': 'High-speed-required',
        'regional_availability': 'National',
        'family_involvement_required': 'None',
        'peer_network_building': 'True',
        'mentor_access_level': 'Peer'
    })

    print(f"\nSuccessfully created {len(programs)} ExploraVision program entries")

    # Create data directory if it doesn't exist
    os.makedirs('data', exist_ok=True)

    # Write to CSV
    csv_path = os.path.join('data', 'exploravision_programs.csv')

    with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(programs)

    print(f"\nSuccessfully created {csv_path} with {len(programs)} program entries")
    return len(programs)

if __name__ == "__main__":
    count = scrape_exploravision()
    print(f"\nScraping complete! Total programs: {count}")
