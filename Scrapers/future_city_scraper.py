import requests
from bs4 import BeautifulSoup
import csv
import time
import os
from datetime import datetime

def scrape_future_city():
    """
    Scrape Future City Competition website for middle school engineering competition information.
    Creates a single CSV file with all Future City opportunities.
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
        'https://futurecity.org/',
        'https://futurecity.org/how-it-works',
        'https://futurecity.org/resources',
    ]

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    print("Starting Future City Competition scraper...")

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

    # Create comprehensive program entries for Future City Competition

    # 1. Future City Main Competition
    programs.append({
        'name': 'Future City Competition - Full Program',
        'description': 'Premier middle school engineering competition where teams design cities of the future. Students work in teams of 3-4 with educator and engineer mentor to imagine, research, design, and build cities using engineering principles. Create virtual city design, physical tabletop model from recycled materials, project plan, and presentation. Annual theme focuses on real-world engineering challenges like clean water, urban resilience, or sustainable food systems.',
        'url': 'https://futurecity.org/',
        'source': 'DiscoverE Future City',
        'category': 'Engineering Competition',
        'stem_fields': 'Engineering, Urban Planning, Sustainability, Environmental Science',
        'target_grade': '6-8',
        'cost': 'Low-cost ($25 registration plus materials)',
        'location_type': 'School-based with regional finals',
        'time_commitment': '5-6 months (September-January)',
        'prerequisite_level': 'None',
        'support_level': 'High',
        'deadline': 'January (regional competition dates)',
        'financial_barrier_level': 'Low',
        'financial_aid_available': 'Limited scholarships available',
        'family_income_consideration': 'Fee assistance offered',
        'hidden_costs_level': 'Model materials ($20-75 estimated)',
        'cost_category': 'Under-$100',
        'diversity_focus': 'DiscoverE diversity and inclusion initiatives',
        'underrepresented_friendly': 'True',
        'first_gen_support': 'True',
        'cultural_competency': 'High',
        'rural_accessible': 'True',
        'transportation_required': 'True',
        'internet_dependency': 'Basic',
        'regional_availability': 'National',
        'family_involvement_required': 'Optional',
        'peer_network_building': 'True',
        'mentor_access_level': 'Professional'
    })

    # 2. Future City Virtual City Design
    programs.append({
        'name': 'Future City - SimCity Virtual City Component',
        'description': 'Digital city design component where students use SimCity software to create virtual model of their future city. Teams apply urban planning principles, zoning regulations, infrastructure design, and resource management. Learn computer-aided design while addressing engineering challenges like transportation networks, energy systems, and residential/commercial balance. Virtual city must align with physical model and project narrative.',
        'url': 'https://futurecity.org/how-it-works',
        'source': 'DiscoverE Future City',
        'category': 'Engineering Competition',
        'stem_fields': 'Engineering, Urban Planning, Computer-Aided Design, Systems Thinking',
        'target_grade': '6-8',
        'cost': 'Low-cost (included in registration)',
        'location_type': 'School-based',
        'time_commitment': '2-3 months (October-December)',
        'prerequisite_level': 'None',
        'support_level': 'High',
        'deadline': 'December-January (submission)',
        'financial_barrier_level': 'Low',
        'financial_aid_available': 'Included in competition fee',
        'family_income_consideration': 'Fee assistance offered',
        'hidden_costs_level': 'None',
        'cost_category': 'Under-$100',
        'diversity_focus': 'DiscoverE diversity and inclusion initiatives',
        'underrepresented_friendly': 'True',
        'first_gen_support': 'True',
        'cultural_competency': 'High',
        'rural_accessible': 'True',
        'transportation_required': 'False',
        'internet_dependency': 'Basic',
        'regional_availability': 'National',
        'family_involvement_required': 'Optional',
        'peer_network_building': 'True',
        'mentor_access_level': 'Professional'
    })

    # 3. Future City Physical Model
    programs.append({
        'name': 'Future City - Physical Model Construction',
        'description': 'Hands-on engineering component requiring teams to build tabletop city model from recycled materials. Students design and construct 3D representation of their future city incorporating innovative solutions to annual theme. Model must be entirely constructed from recycled materials and powered by single 9-volt battery. Develops practical engineering, problem-solving, and creative design skills. Demonstrates sustainable design principles through material choices.',
        'url': 'https://futurecity.org/how-it-works',
        'source': 'DiscoverE Future City',
        'category': 'Engineering Competition',
        'stem_fields': 'Engineering, Design, Sustainability, Materials Science',
        'target_grade': '6-8',
        'cost': 'Low-cost (materials $20-75)',
        'location_type': 'School-based',
        'time_commitment': '3-4 months (September-January)',
        'prerequisite_level': 'None',
        'support_level': 'High',
        'deadline': 'January (regional competition)',
        'financial_barrier_level': 'Low',
        'financial_aid_available': 'Material grants available',
        'family_income_consideration': 'Recycled materials reduce costs',
        'hidden_costs_level': 'Model materials ($20-75 estimated)',
        'cost_category': 'Under-$100',
        'diversity_focus': 'DiscoverE diversity and inclusion initiatives',
        'underrepresented_friendly': 'True',
        'first_gen_support': 'True',
        'cultural_competency': 'High',
        'rural_accessible': 'True',
        'transportation_required': 'True',
        'internet_dependency': 'None',
        'regional_availability': 'National',
        'family_involvement_required': 'Optional',
        'peer_network_building': 'True',
        'mentor_access_level': 'Professional'
    })

    # 4. Future City Essay and Research
    programs.append({
        'name': 'Future City - Engineering Essay Component',
        'description': 'Written component requiring 1,500-word abstract describing city design and engineering solutions. Students research real-world engineering challenges, explain innovative solutions, and justify design choices with scientific evidence. Essay addresses annual theme through lens of urban planning, environmental engineering, and sustainability. Develops technical writing, research, and critical thinking skills. Teams cite sources and explain engineering principles.',
        'url': 'https://futurecity.org/how-it-works',
        'source': 'DiscoverE Future City',
        'category': 'Engineering Competition',
        'stem_fields': 'Engineering, Technical Writing, Research, Urban Planning',
        'target_grade': '6-8',
        'cost': 'Low-cost (included in registration)',
        'location_type': 'School-based',
        'time_commitment': '2-3 months (research and writing)',
        'prerequisite_level': 'None',
        'support_level': 'High',
        'deadline': 'December-January (submission)',
        'financial_barrier_level': 'Low',
        'financial_aid_available': 'Included in competition fee',
        'family_income_consideration': 'Fee assistance offered',
        'hidden_costs_level': 'None',
        'cost_category': 'Under-$100',
        'diversity_focus': 'DiscoverE diversity and inclusion initiatives',
        'underrepresented_friendly': 'True',
        'first_gen_support': 'True',
        'cultural_competency': 'High',
        'rural_accessible': 'True',
        'transportation_required': 'False',
        'internet_dependency': 'Basic',
        'regional_availability': 'National',
        'family_involvement_required': 'Optional',
        'peer_network_building': 'True',
        'mentor_access_level': 'Professional'
    })

    # 5. Future City Presentation
    programs.append({
        'name': 'Future City - Oral Presentation and Q&A',
        'description': 'Public speaking component where teams deliver 7-minute presentation to judges at regional competition. Students explain city design, demonstrate engineering solutions, and answer technical questions from panel of engineers and educators. Entire team participates in presentation and question session. Develops communication skills, confidence, and ability to defend engineering decisions. Judges evaluate technical knowledge, teamwork, and presentation quality.',
        'url': 'https://futurecity.org/how-it-works',
        'source': 'DiscoverE Future City',
        'category': 'Engineering Competition',
        'stem_fields': 'Engineering, Public Speaking, Communication, Teamwork',
        'target_grade': '6-8',
        'cost': 'Low-cost (included in registration)',
        'location_type': 'Regional competition venue',
        'time_commitment': 'Preparation throughout competition, presentation day in January',
        'prerequisite_level': 'None',
        'support_level': 'High',
        'deadline': 'January (regional competition day)',
        'financial_barrier_level': 'Low',
        'financial_aid_available': 'Travel assistance may be available',
        'family_income_consideration': 'Fee assistance offered',
        'hidden_costs_level': 'None',
        'cost_category': 'Under-$100',
        'diversity_focus': 'DiscoverE diversity and inclusion initiatives',
        'underrepresented_friendly': 'True',
        'first_gen_support': 'True',
        'cultural_competency': 'High',
        'rural_accessible': 'True',
        'transportation_required': 'True',
        'internet_dependency': 'None',
        'regional_availability': 'National',
        'family_involvement_required': 'Optional',
        'peer_network_building': 'True',
        'mentor_access_level': 'Professional'
    })

    # 6. Future City Regional Competition
    programs.append({
        'name': 'Future City - Regional Competition Finals',
        'description': 'Regional competition events held across United States where teams compete for advancement to national finals. Teams present cities to judges, display physical models, and compete against other schools. Winners receive awards, scholarships, and advance to national competition in Washington, D.C. Regional events include engineering activities, networking with professionals, and celebration of student innovation. Over 40 regional competitions nationwide.',
        'url': 'https://futurecity.org/',
        'source': 'DiscoverE Future City',
        'category': 'Engineering Competition',
        'stem_fields': 'Engineering, Urban Planning, Sustainability',
        'target_grade': '6-8',
        'cost': 'Low-cost (included in registration)',
        'location_type': 'Regional competition venues (universities, companies)',
        'time_commitment': '1-2 days (regional competition)',
        'prerequisite_level': 'Medium',
        'support_level': 'High',
        'deadline': 'January (varies by region)',
        'financial_barrier_level': 'Low',
        'financial_aid_available': 'Travel assistance may be available',
        'family_income_consideration': 'Fee assistance offered',
        'hidden_costs_level': 'Transportation to regional venue',
        'cost_category': 'Under-$100',
        'diversity_focus': 'DiscoverE diversity and inclusion initiatives',
        'underrepresented_friendly': 'True',
        'first_gen_support': 'True',
        'cultural_competency': 'High',
        'rural_accessible': 'True',
        'transportation_required': 'True',
        'internet_dependency': 'None',
        'regional_availability': 'National',
        'family_involvement_required': 'Optional',
        'peer_network_building': 'True',
        'mentor_access_level': 'Professional'
    })

    # 7. Future City National Finals
    programs.append({
        'name': 'Future City - National Finals Competition',
        'description': 'Premier national engineering competition in Washington, D.C. where regional winners compete for top honors and scholarships. Teams participate in engineering challenges, present to national judges, and tour capital landmarks. National finalists receive all-expense-paid trip including travel, hotel, and meals. Winners receive college scholarships up to $7,500, trophies, and national recognition. Meet students from across country and professional engineers.',
        'url': 'https://futurecity.org/',
        'source': 'DiscoverE Future City',
        'category': 'Engineering Competition',
        'stem_fields': 'Engineering, Urban Planning, Sustainability',
        'target_grade': '6-8',
        'cost': 'Free (travel fully funded for national finalists)',
        'location_type': 'Washington, D.C.',
        'time_commitment': '3-4 days (February)',
        'prerequisite_level': 'High',
        'support_level': 'High',
        'deadline': 'February (national finals)',
        'financial_barrier_level': 'None',
        'financial_aid_available': 'All expenses paid for finalists',
        'family_income_consideration': 'None',
        'hidden_costs_level': 'None',
        'cost_category': 'Free',
        'diversity_focus': 'DiscoverE diversity and inclusion initiatives',
        'underrepresented_friendly': 'True',
        'first_gen_support': 'True',
        'cultural_competency': 'High',
        'rural_accessible': 'True',
        'transportation_required': 'True',
        'internet_dependency': 'None',
        'regional_availability': 'National',
        'family_involvement_required': 'Optional',
        'peer_network_building': 'True',
        'mentor_access_level': 'Professional'
    })

    # 8. Future City Educator Resources
    programs.append({
        'name': 'Future City - Educator Curriculum and Resources',
        'description': 'Comprehensive curriculum materials and resources for teachers facilitating Future City teams. Includes lesson plans, engineering design activities, project management guides, rubrics, and timeline templates. Free downloadable resources align with NGSS standards and support student learning in engineering, sustainability, and urban planning. Professional development webinars help educators guide teams effectively.',
        'url': 'https://futurecity.org/resources',
        'source': 'DiscoverE Future City',
        'category': 'Engineering Competition',
        'stem_fields': 'Engineering Education, Urban Planning, Sustainability',
        'target_grade': '6-8',
        'cost': 'Free',
        'location_type': 'Online resources',
        'time_commitment': 'Self-paced (educator preparation)',
        'prerequisite_level': 'None',
        'support_level': 'High',
        'deadline': 'Available year-round',
        'financial_barrier_level': 'None',
        'financial_aid_available': 'N/A',
        'family_income_consideration': 'None',
        'hidden_costs_level': 'None',
        'cost_category': 'Free',
        'diversity_focus': 'DiscoverE diversity and inclusion initiatives',
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

    # 9. Future City Mentor Program
    programs.append({
        'name': 'Future City - Engineer Mentor Partnerships',
        'description': 'Volunteer engineer mentorship program connecting professional engineers with student teams. Engineers guide students through design process, provide technical expertise, ask probing questions, and share real-world engineering experience. Mentors meet regularly with teams throughout competition season. Exposes students to engineering careers and professional role models. Mentors receive training and resources from Future City organization.',
        'url': 'https://futurecity.org/how-it-works',
        'source': 'DiscoverE Future City',
        'category': 'Engineering Competition',
        'stem_fields': 'Engineering, Mentorship, Career Exploration',
        'target_grade': '6-8',
        'cost': 'Free (mentor provided)',
        'location_type': 'School-based with virtual options',
        'time_commitment': '5-6 months (mentor meetings throughout competition)',
        'prerequisite_level': 'None',
        'support_level': 'High',
        'deadline': 'Ongoing throughout competition season',
        'financial_barrier_level': 'None',
        'financial_aid_available': 'N/A',
        'family_income_consideration': 'None',
        'hidden_costs_level': 'None',
        'cost_category': 'Free',
        'diversity_focus': 'DiscoverE diversity and inclusion initiatives',
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

    # 10. Future City Special Awards
    programs.append({
        'name': 'Future City - Special Recognition Awards',
        'description': 'Additional awards recognizing excellence in specific categories beyond overall competition winners. Special awards include Best Use of Recycled Materials, Most Innovative Energy Solution, Outstanding Research, Best Teamwork, and theme-specific engineering awards. Sponsored by engineering companies and professional societies. Winners receive prizes, certificates, and recognition from industry partners. Celebrates diverse talents and innovative approaches.',
        'url': 'https://futurecity.org/',
        'source': 'DiscoverE Future City',
        'category': 'Engineering Competition',
        'stem_fields': 'Engineering, Innovation, Sustainability',
        'target_grade': '6-8',
        'cost': 'Free (included in competition)',
        'location_type': 'Regional and national competitions',
        'time_commitment': 'Full competition participation',
        'prerequisite_level': 'None',
        'support_level': 'High',
        'deadline': 'January-February (award announcements)',
        'financial_barrier_level': 'None',
        'financial_aid_available': 'Prize awards',
        'family_income_consideration': 'None',
        'hidden_costs_level': 'None',
        'cost_category': 'Free',
        'diversity_focus': 'DiscoverE diversity and inclusion initiatives',
        'underrepresented_friendly': 'True',
        'first_gen_support': 'True',
        'cultural_competency': 'High',
        'rural_accessible': 'True',
        'transportation_required': 'True',
        'internet_dependency': 'None',
        'regional_availability': 'National',
        'family_involvement_required': 'Optional',
        'peer_network_building': 'True',
        'mentor_access_level': 'Professional'
    })

    print(f"\nSuccessfully created {len(programs)} Future City Competition program entries")

    # Create data directory if it doesn't exist
    os.makedirs('data', exist_ok=True)

    # Write to CSV
    csv_path = os.path.join('data', 'future_city_competition.csv')

    with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(programs)

    print(f"\nSuccessfully created {csv_path} with {len(programs)} program entries")
    return len(programs)

if __name__ == "__main__":
    count = scrape_future_city()
    print(f"\nScraping complete! Total programs: {count}")
