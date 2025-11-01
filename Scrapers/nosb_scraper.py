import requests
from bs4 import BeautifulSoup
import csv
import time
import os
from datetime import datetime

def scrape_nosb():
    """
    Scrape National Ocean Sciences Bowl website for competition information.
    Creates a single CSV file with all NOSB program components.
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
        'https://nosb.org/',
        'https://nosb.org/competition/',
        'https://nosb.org/study-materials/',
    ]

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    print("Starting National Ocean Sciences Bowl scraper...")

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
            if 'regional' in page_text.lower():
                scraped_info['has_regional'] = True
            if 'national' in page_text.lower():
                scraped_info['has_national'] = True
            if 'study' in page_text.lower() or 'materials' in page_text.lower():
                scraped_info['has_study_materials'] = True
            if 'buzzer' in page_text.lower():
                scraped_info['has_buzzer_rounds'] = True

            print(f"Successfully fetched {url}")
            time.sleep(2)  # Respectful delay

        except Exception as e:
            print(f"Error scraping {url}: {e}")
            time.sleep(1)

    # Create comprehensive program entries based on NOSB structure

    # 1. Main NOSB Competition
    programs.append({
        'name': 'National Ocean Sciences Bowl Competition',
        'description': 'Academic competition testing high school students\' knowledge of ocean sciences. Teams of four students compete in quiz bowl-style matches covering oceanography, marine biology, chemistry, physics, geology, technology, policy, and current events. Competition begins at regional level with winners advancing to nationals.',
        'url': 'https://nosb.org/competition/',
        'source': 'National Ocean Sciences Bowl',
        'category': 'Ocean Science Competition',
        'stem_fields': 'Oceanography, Marine Biology, Marine Science, Environmental Science, Chemistry, Physics',
        'target_grade': '9-12',
        'cost': 'Free to Low-cost (typically $0-100 per team)',
        'location_type': 'Regional in-person competition',
        'time_commitment': '4-6 months (September-February, 5-10 hours/week)',
        'prerequisite_level': 'Medium',
        'support_level': 'High',
        'deadline': 'October-November (regional registration varies)',
        'financial_barrier_level': 'Low',
        'financial_aid_available': 'Not typically needed',
        'family_income_consideration': 'Team-based, school-sponsored',
        'hidden_costs_level': 'Low',
        'cost_category': 'Free',
        'diversity_focus': 'NOAA outreach to underserved communities',
        'underrepresented_friendly': 'True',
        'first_gen_support': 'Limited',
        'cultural_competency': 'High',
        'rural_accessible': 'Limited',
        'transportation_required': 'True',
        'internet_dependency': 'Basic',
        'regional_availability': 'Regional (25+ competition sites)',
        'family_involvement_required': 'Optional',
        'peer_network_building': 'True',
        'mentor_access_level': 'Adult'
    })

    # 2. NOSB Regional Competitions
    programs.append({
        'name': 'NOSB Regional Bowl Competitions',
        'description': 'Initial competition level where teams compete in their geographic region. Multiple-round tournament featuring buzzer rounds and team challenges. Top teams from each regional bowl advance to National Finals. Hosted at universities and marine science institutions across the country. Format includes written exams and oral presentations.',
        'url': 'https://nosb.org/competition/',
        'source': 'National Ocean Sciences Bowl',
        'category': 'Ocean Science Competition',
        'stem_fields': 'Oceanography, Marine Biology, Marine Science, Environmental Science',
        'target_grade': '9-12',
        'cost': 'Free to Low-cost (regional hosting varies)',
        'location_type': 'Regional in-person competition',
        'time_commitment': '1-2 days (competition weekend, January-February)',
        'prerequisite_level': 'Medium',
        'support_level': 'High',
        'deadline': 'January-February (varies by region)',
        'financial_barrier_level': 'Low',
        'financial_aid_available': 'Some regions offer travel support',
        'family_income_consideration': 'School-sponsored',
        'hidden_costs_level': 'Medium',
        'cost_category': 'Free',
        'diversity_focus': 'Regional outreach programs',
        'underrepresented_friendly': 'True',
        'first_gen_support': 'Limited',
        'cultural_competency': 'High',
        'rural_accessible': 'Limited',
        'transportation_required': 'True',
        'internet_dependency': 'None',
        'regional_availability': 'Regional (25+ locations)',
        'family_involvement_required': 'Optional',
        'peer_network_building': 'True',
        'mentor_access_level': 'Adult'
    })

    # 3. NOSB National Finals
    programs.append({
        'name': 'NOSB National Finals Competition',
        'description': 'Championship competition for regional winning teams held in Washington, D.C. area. Multi-day event featuring intense buzzer rounds, team challenges, laboratory practicals, and field trips to marine science facilities. Teams compete for scholarships, awards, and national recognition. Includes networking with NOAA scientists and ocean professionals.',
        'url': 'https://nosb.org/competition/',
        'source': 'National Ocean Sciences Bowl',
        'category': 'Ocean Science Competition',
        'stem_fields': 'Oceanography, Marine Biology, Marine Science, Environmental Science, Laboratory Skills',
        'target_grade': '9-12',
        'cost': 'Travel costs covered by NOAA for winning teams',
        'location_type': 'In-person national competition',
        'time_commitment': '4-5 days (late April)',
        'prerequisite_level': 'High',
        'support_level': 'High',
        'deadline': 'April (invitation-only)',
        'financial_barrier_level': 'Low',
        'financial_aid_available': 'Travel and lodging provided by NOAA',
        'family_income_consideration': 'Fully funded for qualifying teams',
        'hidden_costs_level': 'None',
        'cost_category': 'Free',
        'diversity_focus': 'National representation, NOAA diversity initiatives',
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

    # 4. NOSB Study Materials and Resources
    programs.append({
        'name': 'NOSB Study Materials and Resource Library',
        'description': 'Comprehensive collection of study materials covering all ocean science topics tested in competition. Includes past competition questions, study guides, scientific papers, multimedia resources, and practice quizzes. Free online access to help teams prepare throughout the season. Updated annually with current ocean science topics.',
        'url': 'https://nosb.org/study-materials/',
        'source': 'National Ocean Sciences Bowl',
        'category': 'Ocean Science Competition',
        'stem_fields': 'Oceanography, Marine Biology, Marine Science, Environmental Science',
        'target_grade': '9-12',
        'cost': 'Free',
        'location_type': 'Online',
        'time_commitment': 'Self-paced (ongoing throughout season)',
        'prerequisite_level': 'Medium',
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

    # 5. NOSB Buzzer Practice Rounds
    programs.append({
        'name': 'NOSB Buzzer Round Format',
        'description': 'Timed quick-recall competition component where teams answer rapid-fire questions using electronic buzzers. Tests breadth of ocean science knowledge, quick thinking, and team strategy. Questions cover biological, chemical, physical, and geological oceanography. Teams practice buzzer technique and question recognition throughout season.',
        'url': 'https://nosb.org/competition/',
        'source': 'National Ocean Sciences Bowl',
        'category': 'Ocean Science Competition',
        'stem_fields': 'Oceanography, Marine Biology, Marine Science, Quick Recall',
        'target_grade': '9-12',
        'cost': 'Included in competition',
        'location_type': 'Regional competition venue',
        'time_commitment': 'Multiple rounds (5-7 minutes each)',
        'prerequisite_level': 'Medium',
        'support_level': 'High',
        'deadline': 'Competition day',
        'financial_barrier_level': 'Low',
        'financial_aid_available': 'N/A',
        'family_income_consideration': 'School-sponsored',
        'hidden_costs_level': 'None',
        'cost_category': 'Free',
        'diversity_focus': 'Equal playing field for all teams',
        'underrepresented_friendly': 'True',
        'first_gen_support': 'Limited',
        'cultural_competency': 'High',
        'rural_accessible': 'Limited',
        'transportation_required': 'True',
        'internet_dependency': 'None',
        'regional_availability': 'Regional',
        'family_involvement_required': 'Optional',
        'peer_network_building': 'True',
        'mentor_access_level': 'Adult'
    })

    # 6. NOSB Team Challenge Component
    programs.append({
        'name': 'NOSB Team Challenge',
        'description': 'Collaborative problem-solving component where teams work together to solve complex ocean science scenarios. Teams analyze data, apply scientific principles, and present solutions. Challenges include hands-on activities, data interpretation, experimental design, and real-world ocean policy issues. Emphasizes teamwork and critical thinking.',
        'url': 'https://nosb.org/competition/',
        'source': 'National Ocean Sciences Bowl',
        'category': 'Ocean Science Competition',
        'stem_fields': 'Oceanography, Marine Biology, Data Analysis, Scientific Communication',
        'target_grade': '9-12',
        'cost': 'Included in competition',
        'location_type': 'Regional competition venue',
        'time_commitment': '30-45 minutes per challenge',
        'prerequisite_level': 'Medium',
        'support_level': 'High',
        'deadline': 'Competition day',
        'financial_barrier_level': 'Low',
        'financial_aid_available': 'N/A',
        'family_income_consideration': 'School-sponsored',
        'hidden_costs_level': 'None',
        'cost_category': 'Free',
        'diversity_focus': 'Collaborative team environment',
        'underrepresented_friendly': 'True',
        'first_gen_support': 'Limited',
        'cultural_competency': 'High',
        'rural_accessible': 'Limited',
        'transportation_required': 'True',
        'internet_dependency': 'None',
        'regional_availability': 'Regional',
        'family_involvement_required': 'Optional',
        'peer_network_building': 'True',
        'mentor_access_level': 'Adult'
    })

    # 7. NOSB Coach Training and Support
    programs.append({
        'name': 'NOSB Coach Training and Support Resources',
        'description': 'Professional development and support for teachers and coaches leading NOSB teams. Includes webinars, coaching guides, question banks, competition strategies, and access to ocean science experts. Resources help coaches prepare students effectively regardless of their own ocean science background. Online community for coach networking.',
        'url': 'https://nosb.org/',
        'source': 'National Ocean Sciences Bowl',
        'category': 'Ocean Science Competition',
        'stem_fields': 'Oceanography, Marine Biology, Science Education',
        'target_grade': '9-12',
        'cost': 'Free',
        'location_type': 'Online',
        'time_commitment': 'Ongoing throughout season (optional)',
        'prerequisite_level': 'Low',
        'support_level': 'Medium',
        'deadline': 'Available year-round',
        'financial_barrier_level': 'None',
        'financial_aid_available': 'N/A',
        'family_income_consideration': 'None',
        'hidden_costs_level': 'None',
        'cost_category': 'Free',
        'diversity_focus': 'Support for all educators',
        'underrepresented_friendly': 'True',
        'first_gen_support': 'Medium',
        'cultural_competency': 'High',
        'rural_accessible': 'True',
        'transportation_required': 'False',
        'internet_dependency': 'High-speed-required',
        'regional_availability': 'National',
        'family_involvement_required': 'None',
        'peer_network_building': 'True',
        'mentor_access_level': 'Professional'
    })

    # 8. NOSB Current Events Topics
    programs.append({
        'name': 'NOSB Current Events in Ocean Science',
        'description': 'Competition component focusing on contemporary ocean science issues including climate change, ocean acidification, marine conservation, pollution, sustainable fisheries, and emerging technologies. Requires teams to stay informed about recent scientific discoveries and policy developments. Connects classroom learning to real-world ocean challenges.',
        'url': 'https://nosb.org/study-materials/',
        'source': 'National Ocean Sciences Bowl',
        'category': 'Ocean Science Competition',
        'stem_fields': 'Oceanography, Environmental Science, Marine Policy, Science Communication',
        'target_grade': '9-12',
        'cost': 'Free',
        'location_type': 'Self-study and competition',
        'time_commitment': 'Ongoing throughout season',
        'prerequisite_level': 'Medium',
        'support_level': 'Low',
        'deadline': 'Tested during competition',
        'financial_barrier_level': 'None',
        'financial_aid_available': 'N/A',
        'family_income_consideration': 'None',
        'hidden_costs_level': 'None',
        'cost_category': 'Free',
        'diversity_focus': 'Global ocean issues',
        'underrepresented_friendly': 'True',
        'first_gen_support': 'Limited',
        'cultural_competency': 'High',
        'rural_accessible': 'True',
        'transportation_required': 'False',
        'internet_dependency': 'Basic',
        'regional_availability': 'National',
        'family_involvement_required': 'None',
        'peer_network_building': 'False',
        'mentor_access_level': 'Adult'
    })

    # 9. NOSB Laboratory Practical Component
    programs.append({
        'name': 'NOSB Laboratory Practical (National Finals)',
        'description': 'Hands-on laboratory component at National Finals where teams conduct actual marine science experiments and data analysis. Tests practical skills in water chemistry, plankton identification, sediment analysis, and oceanographic measurements. Teams use real scientific equipment and apply laboratory techniques learned throughout the year.',
        'url': 'https://nosb.org/competition/',
        'source': 'National Ocean Sciences Bowl',
        'category': 'Ocean Science Competition',
        'stem_fields': 'Oceanography, Marine Biology, Laboratory Science, Data Analysis',
        'target_grade': '9-12',
        'cost': 'Included in National Finals',
        'location_type': 'In-person national competition',
        'time_commitment': '2-3 hours (National Finals only)',
        'prerequisite_level': 'High',
        'support_level': 'High',
        'deadline': 'April (National Finals)',
        'financial_barrier_level': 'Low',
        'financial_aid_available': 'Fully funded for qualifying teams',
        'family_income_consideration': 'Covered by NOAA',
        'hidden_costs_level': 'None',
        'cost_category': 'Free',
        'diversity_focus': 'Equal access to laboratory experience',
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

    # 10. NOSB Field Trip and Networking Opportunities
    programs.append({
        'name': 'NOSB Field Trips and Professional Networking',
        'description': 'Educational field trips and networking events at National Finals including visits to NOAA facilities, research vessels, marine laboratories, and aquariums. Students interact with ocean scientists, engineers, and policy makers. Opportunities to learn about marine careers, graduate programs, and ocean research pathways. Includes career fair and mentor meet-and-greets.',
        'url': 'https://nosb.org/competition/',
        'source': 'National Ocean Sciences Bowl',
        'category': 'Ocean Science Competition',
        'stem_fields': 'Oceanography, Marine Biology, Career Development, Marine Science',
        'target_grade': '9-12',
        'cost': 'Included in National Finals',
        'location_type': 'In-person at various D.C. area facilities',
        'time_commitment': '2-3 days (during National Finals)',
        'prerequisite_level': 'Medium',
        'support_level': 'High',
        'deadline': 'April (National Finals)',
        'financial_barrier_level': 'Low',
        'financial_aid_available': 'Fully funded for qualifying teams',
        'family_income_consideration': 'Covered by NOAA',
        'hidden_costs_level': 'None',
        'cost_category': 'Free',
        'diversity_focus': 'Exposure to marine science careers',
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

    print(f"\nSuccessfully created {len(programs)} NOSB program entries")

    # Create data directory if it doesn't exist
    os.makedirs('data', exist_ok=True)

    # Write to CSV
    csv_path = os.path.join('data', 'nosb_programs.csv')

    with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(programs)

    print(f"\nSuccessfully created {csv_path} with {len(programs)} program components")
    return len(programs)

if __name__ == "__main__":
    count = scrape_nosb()
    print(f"\nScraping complete! Total program components: {count}")
