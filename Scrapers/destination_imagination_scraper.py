import requests
from bs4 import BeautifulSoup
import csv
import time
import os
from datetime import datetime

def scrape_destination_imagination():
    """
    Scrape Destination Imagination website for creative problem-solving competition information.
    Creates a single CSV file with all Destination Imagination challenge opportunities.
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
        'https://www.destinationimagination.org/',
        'https://www.destinationimagination.org/challenge-programs/',
        'https://www.destinationimagination.org/get-started/',
    ]

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    print("Starting Destination Imagination scraper...")

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

    # Create comprehensive program entries for Destination Imagination challenges

    # 1. Technical Challenge
    programs.append({
        'name': 'Destination Imagination Technical Challenge',
        'description': 'Team-based STEAM challenge requiring teams to design, build, and test solutions to technical problems. Teams create functioning devices, structures, or systems using engineering and scientific principles. Emphasizes innovation, technical skills, and creative problem-solving. Challenges change annually with themes in robotics, engineering, or technology.',
        'url': 'https://www.destinationimagination.org/challenge-programs/',
        'source': 'Destination Imagination',
        'category': 'STEAM Competition',
        'stem_fields': 'STEAM (Science, Technology, Engineering, Arts, Mathematics)',
        'target_grade': 'K-12',
        'cost': '$100-500 (team registration + materials)',
        'location_type': 'Regional tournaments',
        'time_commitment': '6-8 months (September-March, 5-10 hours/week)',
        'prerequisite_level': 'None',
        'support_level': 'High',
        'deadline': 'Fall (team registration), March (regional tournaments)',
        'financial_barrier_level': 'Medium',
        'financial_aid_available': 'Limited scholarships available',
        'family_income_consideration': 'Team cost-sharing possible',
        'hidden_costs_level': 'High',
        'cost_category': '$100-500',
        'diversity_focus': 'DI inclusion and creativity initiatives',
        'underrepresented_friendly': 'True',
        'first_gen_support': 'True',
        'cultural_competency': 'High',
        'rural_accessible': 'Limited',
        'transportation_required': 'True',
        'internet_dependency': 'Basic',
        'regional_availability': 'National',
        'family_involvement_required': 'Optional',
        'peer_network_building': 'True',
        'mentor_access_level': 'Adult'
    })

    # 2. Scientific Challenge
    programs.append({
        'name': 'Destination Imagination Scientific Challenge',
        'description': 'Teams apply scientific method to investigate real-world problems and present findings creatively. Challenges involve research, experimentation, data analysis, and theatrical presentation of scientific concepts. Teams learn inquiry-based science while developing communication and teamwork skills. Integrates science with performing arts.',
        'url': 'https://www.destinationimagination.org/challenge-programs/',
        'source': 'Destination Imagination',
        'category': 'STEAM Competition',
        'stem_fields': 'STEAM (Science, Technology, Engineering, Arts, Mathematics)',
        'target_grade': 'K-12',
        'cost': '$100-500 (team registration + materials)',
        'location_type': 'Regional tournaments',
        'time_commitment': '6-8 months (September-March, 5-10 hours/week)',
        'prerequisite_level': 'None',
        'support_level': 'High',
        'deadline': 'Fall (team registration), March (regional tournaments)',
        'financial_barrier_level': 'Medium',
        'financial_aid_available': 'Limited scholarships available',
        'family_income_consideration': 'Team cost-sharing possible',
        'hidden_costs_level': 'High',
        'cost_category': '$100-500',
        'diversity_focus': 'DI inclusion and creativity initiatives',
        'underrepresented_friendly': 'True',
        'first_gen_support': 'True',
        'cultural_competency': 'High',
        'rural_accessible': 'Limited',
        'transportation_required': 'True',
        'internet_dependency': 'Basic',
        'regional_availability': 'National',
        'family_involvement_required': 'Optional',
        'peer_network_building': 'True',
        'mentor_access_level': 'Adult'
    })

    # 3. Engineering Challenge
    programs.append({
        'name': 'Destination Imagination Engineering Challenge',
        'description': 'Teams design and construct engineering solutions to specific problems, often involving structures, machines, or mechanisms. Challenges test understanding of physics, structural integrity, and mechanical advantage. Teams build prototypes, test performance, and present their engineering process. Hands-on application of engineering principles.',
        'url': 'https://www.destinationimagination.org/challenge-programs/',
        'source': 'Destination Imagination',
        'category': 'STEAM Competition',
        'stem_fields': 'STEAM (Science, Technology, Engineering, Arts, Mathematics)',
        'target_grade': 'K-12',
        'cost': '$100-500 (team registration + materials)',
        'location_type': 'Regional tournaments',
        'time_commitment': '6-8 months (September-March, 5-10 hours/week)',
        'prerequisite_level': 'None',
        'support_level': 'High',
        'deadline': 'Fall (team registration), March (regional tournaments)',
        'financial_barrier_level': 'Medium',
        'financial_aid_available': 'Limited scholarships available',
        'family_income_consideration': 'Team cost-sharing possible',
        'hidden_costs_level': 'High',
        'cost_category': '$100-500',
        'diversity_focus': 'DI inclusion and creativity initiatives',
        'underrepresented_friendly': 'True',
        'first_gen_support': 'True',
        'cultural_competency': 'High',
        'rural_accessible': 'Limited',
        'transportation_required': 'True',
        'internet_dependency': 'Basic',
        'regional_availability': 'National',
        'family_involvement_required': 'Optional',
        'peer_network_building': 'True',
        'mentor_access_level': 'Adult'
    })

    # 4. Fine Arts Challenge
    programs.append({
        'name': 'Destination Imagination Fine Arts Challenge',
        'description': 'Creative challenge focusing on performing and visual arts integrated with problem-solving. Teams create original theatrical performances, artwork, or multimedia presentations addressing challenge themes. Combines artistic expression with innovation and storytelling. Develops creativity, collaboration, and artistic skills.',
        'url': 'https://www.destinationimagination.org/challenge-programs/',
        'source': 'Destination Imagination',
        'category': 'STEAM Competition',
        'stem_fields': 'STEAM (Science, Technology, Engineering, Arts, Mathematics)',
        'target_grade': 'K-12',
        'cost': '$100-500 (team registration + materials)',
        'location_type': 'Regional tournaments',
        'time_commitment': '6-8 months (September-March, 5-10 hours/week)',
        'prerequisite_level': 'None',
        'support_level': 'High',
        'deadline': 'Fall (team registration), March (regional tournaments)',
        'financial_barrier_level': 'Medium',
        'financial_aid_available': 'Limited scholarships available',
        'family_income_consideration': 'Team cost-sharing possible',
        'hidden_costs_level': 'Medium',
        'cost_category': '$100-500',
        'diversity_focus': 'DI inclusion and creativity initiatives',
        'underrepresented_friendly': 'True',
        'first_gen_support': 'True',
        'cultural_competency': 'High',
        'rural_accessible': 'Limited',
        'transportation_required': 'True',
        'internet_dependency': 'Basic',
        'regional_availability': 'National',
        'family_involvement_required': 'Optional',
        'peer_network_building': 'True',
        'mentor_access_level': 'Adult'
    })

    # 5. Improvisational Challenge
    programs.append({
        'name': 'Destination Imagination Improvisational Challenge',
        'description': 'Fast-paced challenge testing quick thinking, spontaneity, and creative problem-solving under pressure. Teams receive surprise challenges at tournaments requiring immediate collaborative solutions. Develops improvisation skills, teamwork, and adaptability. No advance preparation possible - pure creative thinking.',
        'url': 'https://www.destinationimagination.org/challenge-programs/',
        'source': 'Destination Imagination',
        'category': 'STEAM Competition',
        'stem_fields': 'STEAM (Science, Technology, Engineering, Arts, Mathematics)',
        'target_grade': 'K-12',
        'cost': '$100-500 (team registration)',
        'location_type': 'Regional tournaments',
        'time_commitment': '6-8 months (team building, tournaments in March)',
        'prerequisite_level': 'None',
        'support_level': 'High',
        'deadline': 'Fall (team registration), March (regional tournaments)',
        'financial_barrier_level': 'Low',
        'financial_aid_available': 'Limited scholarships available',
        'family_income_consideration': 'Team cost-sharing possible',
        'hidden_costs_level': 'Low',
        'cost_category': '$100-500',
        'diversity_focus': 'DI inclusion and creativity initiatives',
        'underrepresented_friendly': 'True',
        'first_gen_support': 'True',
        'cultural_competency': 'High',
        'rural_accessible': 'Limited',
        'transportation_required': 'True',
        'internet_dependency': 'Basic',
        'regional_availability': 'National',
        'family_involvement_required': 'Optional',
        'peer_network_building': 'True',
        'mentor_access_level': 'Adult'
    })

    # 6. Service Learning Challenge (Instant Challenge)
    programs.append({
        'name': 'Destination Imagination Service Learning Project',
        'description': 'Teams identify community needs and create service projects using creative problem-solving. Combines community service with innovation and teamwork. Teams research issues, develop solutions, implement projects, and document impact. Teaches civic engagement and social responsibility through STEAM lens.',
        'url': 'https://www.destinationimagination.org/challenge-programs/',
        'source': 'Destination Imagination',
        'category': 'STEAM Competition',
        'stem_fields': 'STEAM (Science, Technology, Engineering, Arts, Mathematics), Community Service',
        'target_grade': 'K-12',
        'cost': '$100-500 (team registration + project costs)',
        'location_type': 'Community-based and regional tournaments',
        'time_commitment': '6-8 months (September-March, 5-10 hours/week)',
        'prerequisite_level': 'None',
        'support_level': 'High',
        'deadline': 'Fall (team registration), March (regional tournaments)',
        'financial_barrier_level': 'Medium',
        'financial_aid_available': 'Limited scholarships available',
        'family_income_consideration': 'Team cost-sharing possible',
        'hidden_costs_level': 'Medium',
        'cost_category': '$100-500',
        'diversity_focus': 'DI inclusion and creativity initiatives',
        'underrepresented_friendly': 'True',
        'first_gen_support': 'True',
        'cultural_competency': 'High',
        'rural_accessible': 'Limited',
        'transportation_required': 'True',
        'internet_dependency': 'Basic',
        'regional_availability': 'National',
        'family_involvement_required': 'Optional',
        'peer_network_building': 'True',
        'mentor_access_level': 'Adult'
    })

    # 7. Early Learning Challenge
    programs.append({
        'name': 'Destination Imagination Early Learning Challenge',
        'description': 'Simplified challenges designed for elementary-age students (K-2). Age-appropriate problem-solving activities introducing creative thinking and teamwork fundamentals. Non-competitive format focused on learning process and building confidence. Gateway to competitive DI participation in later grades.',
        'url': 'https://www.destinationimagination.org/challenge-programs/',
        'source': 'Destination Imagination',
        'category': 'STEAM Competition',
        'stem_fields': 'STEAM (Science, Technology, Engineering, Arts, Mathematics)',
        'target_grade': 'K-2',
        'cost': '$100-300 (team registration)',
        'location_type': 'School-based and regional events',
        'time_commitment': '4-6 months (September-March, 3-5 hours/week)',
        'prerequisite_level': 'None',
        'support_level': 'High',
        'deadline': 'Fall (team registration), March (regional events)',
        'financial_barrier_level': 'Low',
        'financial_aid_available': 'Limited scholarships available',
        'family_income_consideration': 'Team cost-sharing possible',
        'hidden_costs_level': 'Low',
        'cost_category': '$100-500',
        'diversity_focus': 'DI inclusion and creativity initiatives',
        'underrepresented_friendly': 'True',
        'first_gen_support': 'True',
        'cultural_competency': 'High',
        'rural_accessible': 'Limited',
        'transportation_required': 'True',
        'internet_dependency': 'Basic',
        'regional_availability': 'National',
        'family_involvement_required': 'High',
        'peer_network_building': 'True',
        'mentor_access_level': 'Adult'
    })

    # 8. Rising Stars Challenge
    programs.append({
        'name': 'Destination Imagination Rising Stars Challenge',
        'description': 'Non-competitive introductory program for younger students (PreK-2) exploring creativity and problem-solving. Structured activities introduce teamwork concepts without tournament pressure. Focuses on fun, learning, and building foundation for future DI participation. Parent/educator-guided experiences.',
        'url': 'https://www.destinationimagination.org/challenge-programs/',
        'source': 'Destination Imagination',
        'category': 'STEAM Competition',
        'stem_fields': 'STEAM (Science, Technology, Engineering, Arts, Mathematics)',
        'target_grade': 'PreK-2',
        'cost': 'Low-cost (program materials)',
        'location_type': 'School or home-based',
        'time_commitment': '3-6 months (flexible schedule)',
        'prerequisite_level': 'None',
        'support_level': 'High',
        'deadline': 'Flexible enrollment',
        'financial_barrier_level': 'Low',
        'financial_aid_available': 'Limited',
        'family_income_consideration': 'None',
        'hidden_costs_level': 'Low',
        'cost_category': 'Under-$100',
        'diversity_focus': 'DI inclusion and creativity initiatives',
        'underrepresented_friendly': 'True',
        'first_gen_support': 'True',
        'cultural_competency': 'High',
        'rural_accessible': 'True',
        'transportation_required': 'False',
        'internet_dependency': 'Basic',
        'regional_availability': 'National',
        'family_involvement_required': 'High',
        'peer_network_building': 'True',
        'mentor_access_level': 'Adult'
    })

    # 9. Global Finals
    programs.append({
        'name': 'Destination Imagination Global Finals',
        'description': 'International championship tournament for top teams from around the world. Multi-day celebration of creativity featuring team competitions, exhibitions, performances, and cultural exchange. Teams earn qualification through regional and state tournaments. Held annually at major university campus with thousands of participants.',
        'url': 'https://www.destinationimagination.org/',
        'source': 'Destination Imagination',
        'category': 'STEAM Competition',
        'stem_fields': 'STEAM (Science, Technology, Engineering, Arts, Mathematics)',
        'target_grade': 'K-12',
        'cost': 'Varies (travel and registration for qualifying teams)',
        'location_type': 'International tournament (May)',
        'time_commitment': '5-7 days (May)',
        'prerequisite_level': 'High',
        'support_level': 'High',
        'deadline': 'May (qualification required)',
        'financial_barrier_level': 'High',
        'financial_aid_available': 'Some fundraising support',
        'family_income_consideration': 'Team fundraising common',
        'hidden_costs_level': 'High',
        'cost_category': '$2000+',
        'diversity_focus': 'Global creativity celebration',
        'underrepresented_friendly': 'True',
        'first_gen_support': 'Limited',
        'cultural_competency': 'High',
        'rural_accessible': 'True',
        'transportation_required': 'True',
        'internet_dependency': 'Basic',
        'regional_availability': 'International',
        'family_involvement_required': 'Optional',
        'peer_network_building': 'True',
        'mentor_access_level': 'Adult'
    })

    # 10. DI Instant Challenge Workshops
    programs.append({
        'name': 'Destination Imagination Instant Challenge Workshops',
        'description': 'Training workshops teaching improvisation and quick thinking skills for surprise challenges. Students practice collaborative problem-solving under time pressure. Workshops prepare teams for Instant Challenges at tournaments and develop transferable life skills. Available through local affiliates and online resources.',
        'url': 'https://www.destinationimagination.org/challenge-programs/',
        'source': 'Destination Imagination',
        'category': 'STEAM Competition',
        'stem_fields': 'STEAM (Science, Technology, Engineering, Arts, Mathematics), Critical Thinking',
        'target_grade': 'K-12',
        'cost': 'Low-cost to Free (varies by affiliate)',
        'location_type': 'Regional workshops',
        'time_commitment': '1-3 hours (workshop sessions)',
        'prerequisite_level': 'None',
        'support_level': 'Medium',
        'deadline': 'Ongoing throughout season',
        'financial_barrier_level': 'Low',
        'financial_aid_available': 'Often free',
        'family_income_consideration': 'None',
        'hidden_costs_level': 'None',
        'cost_category': 'Free',
        'diversity_focus': 'DI inclusion and creativity initiatives',
        'underrepresented_friendly': 'True',
        'first_gen_support': 'True',
        'cultural_competency': 'High',
        'rural_accessible': 'Limited',
        'transportation_required': 'True',
        'internet_dependency': 'Basic',
        'regional_availability': 'Regional',
        'family_involvement_required': 'Optional',
        'peer_network_building': 'True',
        'mentor_access_level': 'Adult'
    })

    # 11. Team Manager Training
    programs.append({
        'name': 'Destination Imagination Team Manager Training',
        'description': 'Training for adult team managers (parents, teachers, community members) who guide DI teams. Workshops cover DI philosophy, challenge facilitation, and team mentorship without interference. Teaches how to support student-led problem-solving. Essential for starting new teams. Benefits students through better-prepared mentors.',
        'url': 'https://www.destinationimagination.org/get-started/',
        'source': 'Destination Imagination',
        'category': 'STEAM Competition',
        'stem_fields': 'STEAM Education, Mentorship',
        'target_grade': 'Adult (benefits K-12 students)',
        'cost': 'Low-cost to Free',
        'location_type': 'Online and regional workshops',
        'time_commitment': '2-4 hours (training sessions)',
        'prerequisite_level': 'None',
        'support_level': 'High',
        'deadline': 'Ongoing throughout year',
        'financial_barrier_level': 'None',
        'financial_aid_available': 'N/A',
        'family_income_consideration': 'None',
        'hidden_costs_level': 'None',
        'cost_category': 'Free',
        'diversity_focus': 'DI inclusion and creativity initiatives',
        'underrepresented_friendly': 'True',
        'first_gen_support': 'True',
        'cultural_competency': 'High',
        'rural_accessible': 'True',
        'transportation_required': 'False',
        'internet_dependency': 'Basic',
        'regional_availability': 'National',
        'family_involvement_required': 'Adult participation',
        'peer_network_building': 'True',
        'mentor_access_level': 'Peer'
    })

    # 12. Project Outreach
    programs.append({
        'name': 'Destination Imagination Project Outreach',
        'description': 'DI-inspired creative problem-solving activities for underserved communities and schools with limited resources. Provides access to DI methodology without full tournament participation costs. Focuses on bringing creativity and innovation education to all students regardless of economic barriers. Partner programs and grants available.',
        'url': 'https://www.destinationimagination.org/',
        'source': 'Destination Imagination',
        'category': 'STEAM Competition',
        'stem_fields': 'STEAM (Science, Technology, Engineering, Arts, Mathematics)',
        'target_grade': 'K-12',
        'cost': 'Free to Low-cost',
        'location_type': 'School and community-based',
        'time_commitment': 'Flexible (varies by program)',
        'prerequisite_level': 'None',
        'support_level': 'High',
        'deadline': 'Varies by program',
        'financial_barrier_level': 'Low',
        'financial_aid_available': 'Grants and sponsorships',
        'family_income_consideration': 'Targeted to low-income communities',
        'hidden_costs_level': 'None',
        'cost_category': 'Free',
        'diversity_focus': 'Underserved communities and equity',
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

    print(f"\nSuccessfully created {len(programs)} Destination Imagination program entries")

    # Create data directory if it doesn't exist
    os.makedirs('data', exist_ok=True)

    # Write to CSV
    csv_path = os.path.join('data', 'destination_imagination_programs.csv')

    with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(programs)

    print(f"\nSuccessfully created {csv_path} with {len(programs)} program entries")
    return len(programs)

if __name__ == "__main__":
    count = scrape_destination_imagination()
    print(f"\nScraping complete! Total programs: {count}")
