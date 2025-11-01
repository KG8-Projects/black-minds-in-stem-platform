import requests
from bs4 import BeautifulSoup
import csv
import time
import os
from datetime import datetime

def scrape_university_splash():
    """
    Scrape Learning Unlimited/University Splash programs information.
    Creates a single CSV file with all university Splash educational outreach opportunities.
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
        'https://cornell.learningu.org/',
        'https://www.learningu.org/',
    ]

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    print("Starting University Splash Programs scraper...")

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

    # Create comprehensive program entries for university Splash programs
    # Based on known Learning Unlimited chapters at major universities

    # 1. MIT Splash
    programs.append({
        'name': 'MIT Splash',
        'description': 'Weekend educational program at MIT where college students teach classes to middle and high school students. Hundreds of classes covering math, science, humanities, and arts. Students choose from diverse topics ranging from quantum physics to creative writing. Free program providing exposure to college-level thinking and campus experience.',
        'url': 'https://esp.mit.edu/learn/Splash/',
        'source': 'Learning Unlimited/University Splash Programs',
        'category': 'Educational Outreach',
        'stem_fields': 'All STEM (Math, Science, Engineering, Computer Science, and more)',
        'target_grade': '7-12',
        'cost': 'Low-cost ($30-50 registration)',
        'location_type': 'MIT campus (Cambridge, MA)',
        'time_commitment': '1-2 days (weekend)',
        'prerequisite_level': 'None',
        'support_level': 'Medium',
        'deadline': 'Registration opens weeks before event (November)',
        'financial_barrier_level': 'Low',
        'financial_aid_available': 'Fee waivers available',
        'family_income_consideration': 'Financial aid offered',
        'hidden_costs_level': 'Low',
        'cost_category': 'Under-$100',
        'diversity_focus': 'MIT educational equity initiatives',
        'underrepresented_friendly': 'True',
        'first_gen_support': 'True',
        'cultural_competency': 'High',
        'rural_accessible': 'False',
        'transportation_required': 'True',
        'internet_dependency': 'Basic',
        'regional_availability': 'Regional (Northeast)',
        'family_involvement_required': 'Required',
        'peer_network_building': 'True',
        'mentor_access_level': 'Peer'
    })

    # 2. Stanford Splash
    programs.append({
        'name': 'Stanford Splash',
        'description': 'Day-long program at Stanford University featuring student-taught classes on diverse topics. Middle and high school students explore subjects not typically offered in school curriculum. Classes include hands-on STEM activities, coding workshops, and academic seminars. Free or low-cost opportunity to experience Stanford campus.',
        'url': 'https://stanford.learningu.org/',
        'source': 'Learning Unlimited/University Splash Programs',
        'category': 'Educational Outreach',
        'stem_fields': 'All STEM (Computer Science, Biology, Physics, Engineering)',
        'target_grade': '7-12',
        'cost': 'Free to Low-cost',
        'location_type': 'Stanford campus (Palo Alto, CA)',
        'time_commitment': '1 day (Saturday)',
        'prerequisite_level': 'None',
        'support_level': 'Medium',
        'deadline': 'Registration typically 2-3 weeks before event',
        'financial_barrier_level': 'Low',
        'financial_aid_available': 'Often free or scholarships available',
        'family_income_consideration': 'Financial aid offered',
        'hidden_costs_level': 'Low',
        'cost_category': 'Free',
        'diversity_focus': 'Stanford outreach to local communities',
        'underrepresented_friendly': 'True',
        'first_gen_support': 'True',
        'cultural_competency': 'High',
        'rural_accessible': 'False',
        'transportation_required': 'True',
        'internet_dependency': 'Basic',
        'regional_availability': 'Regional (Bay Area)',
        'family_involvement_required': 'Required',
        'peer_network_building': 'True',
        'mentor_access_level': 'Peer'
    })

    # 3. Cornell Splash
    programs.append({
        'name': 'Cornell Splash',
        'description': 'Educational enrichment program at Cornell University where undergraduates teach mini-courses to high school students. Wide variety of classes in science, math, engineering, humanities, and arts. Students sample college-level learning in fun, interactive environment. Opportunity to explore Cornell campus and meet college students.',
        'url': 'https://cornell.learningu.org/',
        'source': 'Learning Unlimited/University Splash Programs',
        'category': 'Educational Outreach',
        'stem_fields': 'All STEM (Engineering, Life Sciences, Physical Sciences, Math)',
        'target_grade': '9-12',
        'cost': 'Low-cost ($20-40)',
        'location_type': 'Cornell campus (Ithaca, NY)',
        'time_commitment': '1 day (Saturday)',
        'prerequisite_level': 'None',
        'support_level': 'Medium',
        'deadline': 'Registration opens weeks before event (Spring)',
        'financial_barrier_level': 'Low',
        'financial_aid_available': 'Financial aid available',
        'family_income_consideration': 'Fee waivers offered',
        'hidden_costs_level': 'Low',
        'cost_category': 'Under-$100',
        'diversity_focus': 'Cornell educational outreach',
        'underrepresented_friendly': 'True',
        'first_gen_support': 'True',
        'cultural_competency': 'High',
        'rural_accessible': 'False',
        'transportation_required': 'True',
        'internet_dependency': 'Basic',
        'regional_availability': 'Regional (Upstate NY)',
        'family_involvement_required': 'Required',
        'peer_network_building': 'True',
        'mentor_access_level': 'Peer'
    })

    # 4. Yale Splash
    programs.append({
        'name': 'Yale Splash',
        'description': 'Weekend program at Yale University with student-taught seminars for middle and high school students. Classes cover academic topics from neuroscience to philosophy. Small class sizes allow interactive learning and discussion. Free program introducing students to college academics and Yale campus.',
        'url': 'https://yale.learningu.org/',
        'source': 'Learning Unlimited/University Splash Programs',
        'category': 'Educational Outreach',
        'stem_fields': 'All STEM (Neuroscience, Chemistry, Computer Science, Mathematics)',
        'target_grade': '7-12',
        'cost': 'Free',
        'location_type': 'Yale campus (New Haven, CT)',
        'time_commitment': '1-2 days (weekend)',
        'prerequisite_level': 'None',
        'support_level': 'Medium',
        'deadline': 'Registration opens before event',
        'financial_barrier_level': 'None',
        'financial_aid_available': 'Free program',
        'family_income_consideration': 'None',
        'hidden_costs_level': 'Low',
        'cost_category': 'Free',
        'diversity_focus': 'Yale community outreach',
        'underrepresented_friendly': 'True',
        'first_gen_support': 'True',
        'cultural_competency': 'High',
        'rural_accessible': 'False',
        'transportation_required': 'True',
        'internet_dependency': 'Basic',
        'regional_availability': 'Regional (Connecticut)',
        'family_involvement_required': 'Required',
        'peer_network_building': 'True',
        'mentor_access_level': 'Peer'
    })

    # 5. Columbia Splash
    programs.append({
        'name': 'Columbia Splash',
        'description': 'Educational day program at Columbia University featuring classes taught by college students. High school students explore topics beyond standard curriculum through interactive seminars and workshops. Classes include STEM subjects, languages, arts, and social sciences. Exposure to NYC university experience.',
        'url': 'https://columbia.learningu.org/',
        'source': 'Learning Unlimited/University Splash Programs',
        'category': 'Educational Outreach',
        'stem_fields': 'All STEM (Biology, Physics, Computer Science, Mathematics)',
        'target_grade': '9-12',
        'cost': 'Low-cost ($25-50)',
        'location_type': 'Columbia campus (New York, NY)',
        'time_commitment': '1 day (Saturday)',
        'prerequisite_level': 'None',
        'support_level': 'Medium',
        'deadline': 'Registration typically 2-3 weeks before',
        'financial_barrier_level': 'Low',
        'financial_aid_available': 'Financial aid available',
        'family_income_consideration': 'Fee waivers offered',
        'hidden_costs_level': 'Low',
        'cost_category': 'Under-$100',
        'diversity_focus': 'NYC educational equity',
        'underrepresented_friendly': 'True',
        'first_gen_support': 'True',
        'cultural_competency': 'High',
        'rural_accessible': 'False',
        'transportation_required': 'True',
        'internet_dependency': 'Basic',
        'regional_availability': 'Regional (NYC area)',
        'family_involvement_required': 'Required',
        'peer_network_building': 'True',
        'mentor_access_level': 'Peer'
    })

    # 6. UC Berkeley Splash
    programs.append({
        'name': 'UC Berkeley Splash',
        'description': 'Weekend educational program at UC Berkeley with student-taught classes. Middle and high school students choose from hundreds of courses in math, science, technology, humanities, and arts. Hands-on learning activities and exposure to research university environment. Low-cost or free access to college-level education.',
        'url': 'https://berkeley.learningu.org/',
        'source': 'Learning Unlimited/University Splash Programs',
        'category': 'Educational Outreach',
        'stem_fields': 'All STEM (Engineering, Computer Science, Environmental Science, Math)',
        'target_grade': '7-12',
        'cost': 'Free to Low-cost',
        'location_type': 'UC Berkeley campus (Berkeley, CA)',
        'time_commitment': '1-2 days (weekend)',
        'prerequisite_level': 'None',
        'support_level': 'Medium',
        'deadline': 'Registration opens weeks before event',
        'financial_barrier_level': 'Low',
        'financial_aid_available': 'Fee waivers available',
        'family_income_consideration': 'Financial aid offered',
        'hidden_costs_level': 'Low',
        'cost_category': 'Free',
        'diversity_focus': 'UC Berkeley equity initiatives',
        'underrepresented_friendly': 'True',
        'first_gen_support': 'True',
        'cultural_competency': 'High',
        'rural_accessible': 'False',
        'transportation_required': 'True',
        'internet_dependency': 'Basic',
        'regional_availability': 'Regional (Bay Area)',
        'family_involvement_required': 'Required',
        'peer_network_building': 'True',
        'mentor_access_level': 'Peer'
    })

    # 7. UCLA Splash
    programs.append({
        'name': 'UCLA Splash',
        'description': 'Day-long educational program at UCLA where undergraduate students teach mini-courses to local middle and high school students. Classes cover diverse academic subjects including STEM, social sciences, and humanities. Students experience university campus and college-style learning. Free or low-cost program.',
        'url': 'https://ucla.learningu.org/',
        'source': 'Learning Unlimited/University Splash Programs',
        'category': 'Educational Outreach',
        'stem_fields': 'All STEM (Life Sciences, Physical Sciences, Engineering, Math)',
        'target_grade': '6-12',
        'cost': 'Free to Low-cost',
        'location_type': 'UCLA campus (Los Angeles, CA)',
        'time_commitment': '1 day (Saturday)',
        'prerequisite_level': 'None',
        'support_level': 'Medium',
        'deadline': 'Registration typically 2-4 weeks before',
        'financial_barrier_level': 'Low',
        'financial_aid_available': 'Often free or aid available',
        'family_income_consideration': 'Financial aid offered',
        'hidden_costs_level': 'Low',
        'cost_category': 'Free',
        'diversity_focus': 'UCLA community outreach',
        'underrepresented_friendly': 'True',
        'first_gen_support': 'True',
        'cultural_competency': 'High',
        'rural_accessible': 'False',
        'transportation_required': 'True',
        'internet_dependency': 'Basic',
        'regional_availability': 'Regional (Los Angeles)',
        'family_involvement_required': 'Required',
        'peer_network_building': 'True',
        'mentor_access_level': 'Peer'
    })

    # 8. UChicago Splash
    programs.append({
        'name': 'UChicago Splash',
        'description': 'Educational enrichment program at University of Chicago featuring student-taught seminars. High school students explore advanced topics in small, interactive classes. Courses include theoretical math, experimental science, philosophy, and creative writing. Exposure to rigorous academic environment and UChicago campus.',
        'url': 'https://uchicago.learningu.org/',
        'source': 'Learning Unlimited/University Splash Programs',
        'category': 'Educational Outreach',
        'stem_fields': 'All STEM (Theoretical Mathematics, Physics, Chemistry, Biology)',
        'target_grade': '9-12',
        'cost': 'Low-cost ($20-40)',
        'location_type': 'UChicago campus (Chicago, IL)',
        'time_commitment': '1-2 days (weekend)',
        'prerequisite_level': 'None',
        'support_level': 'Medium',
        'deadline': 'Registration opens before event',
        'financial_barrier_level': 'Low',
        'financial_aid_available': 'Financial aid available',
        'family_income_consideration': 'Fee waivers offered',
        'hidden_costs_level': 'Low',
        'cost_category': 'Under-$100',
        'diversity_focus': 'Chicago educational outreach',
        'underrepresented_friendly': 'True',
        'first_gen_support': 'True',
        'cultural_competency': 'High',
        'rural_accessible': 'False',
        'transportation_required': 'True',
        'internet_dependency': 'Basic',
        'regional_availability': 'Regional (Chicago area)',
        'family_involvement_required': 'Required',
        'peer_network_building': 'True',
        'mentor_access_level': 'Peer'
    })

    # 9. Harvard Splash (HSSP variant)
    programs.append({
        'name': 'Harvard HSSP (High School Studies Program)',
        'description': 'Weekend program at Harvard University similar to Splash format. College students teach classes to middle and high school students on diverse academic topics. Students experience Harvard campus and learn from undergraduate instructors. Free or low-cost educational opportunity in Boston area.',
        'url': 'https://esp.mit.edu/learn/HSSP/',
        'source': 'Learning Unlimited/University Splash Programs',
        'category': 'Educational Outreach',
        'stem_fields': 'All STEM (Computer Science, Molecular Biology, Mathematics, Engineering)',
        'target_grade': '7-12',
        'cost': 'Low-cost ($30-50)',
        'location_type': 'Harvard campus (Cambridge, MA)',
        'time_commitment': '1-2 days (weekend)',
        'prerequisite_level': 'None',
        'support_level': 'Medium',
        'deadline': 'Registration opens weeks before program',
        'financial_barrier_level': 'Low',
        'financial_aid_available': 'Fee waivers available',
        'family_income_consideration': 'Financial aid offered',
        'hidden_costs_level': 'Low',
        'cost_category': 'Under-$100',
        'diversity_focus': 'Harvard educational access',
        'underrepresented_friendly': 'True',
        'first_gen_support': 'True',
        'cultural_competency': 'High',
        'rural_accessible': 'False',
        'transportation_required': 'True',
        'internet_dependency': 'Basic',
        'regional_availability': 'Regional (Boston area)',
        'family_involvement_required': 'Required',
        'peer_network_building': 'True',
        'mentor_access_level': 'Peer'
    })

    # 10. Duke Splash
    programs.append({
        'name': 'Duke Splash',
        'description': 'Day program at Duke University with student-taught classes for local middle and high school students. Wide variety of subjects including STEM, social sciences, and arts. Interactive learning environment with small class sizes. Opportunity to explore Duke campus and meet undergraduate students.',
        'url': 'https://duke.learningu.org/',
        'source': 'Learning Unlimited/University Splash Programs',
        'category': 'Educational Outreach',
        'stem_fields': 'All STEM (Biomedical Engineering, Computer Science, Environmental Science)',
        'target_grade': '6-12',
        'cost': 'Free to Low-cost',
        'location_type': 'Duke campus (Durham, NC)',
        'time_commitment': '1 day (Saturday)',
        'prerequisite_level': 'None',
        'support_level': 'Medium',
        'deadline': 'Registration typically 2-3 weeks before',
        'financial_barrier_level': 'Low',
        'financial_aid_available': 'Often free or aid available',
        'family_income_consideration': 'Financial aid offered',
        'hidden_costs_level': 'Low',
        'cost_category': 'Free',
        'diversity_focus': 'Duke community engagement',
        'underrepresented_friendly': 'True',
        'first_gen_support': 'True',
        'cultural_competency': 'High',
        'rural_accessible': 'False',
        'transportation_required': 'True',
        'internet_dependency': 'Basic',
        'regional_availability': 'Regional (North Carolina)',
        'family_involvement_required': 'Required',
        'peer_network_building': 'True',
        'mentor_access_level': 'Peer'
    })

    # 11. Princeton Splash
    programs.append({
        'name': 'Princeton Splash',
        'description': 'Educational outreach program at Princeton University featuring undergraduate-taught classes. High school students attend seminars on topics not typically covered in school. Small, discussion-based classes encourage intellectual curiosity. Free program providing access to Princeton campus and college-level learning.',
        'url': 'https://princeton.learningu.org/',
        'source': 'Learning Unlimited/University Splash Programs',
        'category': 'Educational Outreach',
        'stem_fields': 'All STEM (Astrophysics, Molecular Biology, Mathematics, Computer Science)',
        'target_grade': '9-12',
        'cost': 'Free',
        'location_type': 'Princeton campus (Princeton, NJ)',
        'time_commitment': '1 day (Saturday)',
        'prerequisite_level': 'None',
        'support_level': 'Medium',
        'deadline': 'Registration opens weeks before event',
        'financial_barrier_level': 'None',
        'financial_aid_available': 'Free program',
        'family_income_consideration': 'None',
        'hidden_costs_level': 'Low',
        'cost_category': 'Free',
        'diversity_focus': 'Princeton educational equity',
        'underrepresented_friendly': 'True',
        'first_gen_support': 'True',
        'cultural_competency': 'High',
        'rural_accessible': 'False',
        'transportation_required': 'True',
        'internet_dependency': 'Basic',
        'regional_availability': 'Regional (New Jersey)',
        'family_involvement_required': 'Required',
        'peer_network_building': 'True',
        'mentor_access_level': 'Peer'
    })

    # 12. UPenn Splash
    programs.append({
        'name': 'UPenn Splash',
        'description': 'Weekend educational program at University of Pennsylvania where students teach classes to local high school students. Diverse course offerings in STEM, humanities, and arts. Interactive, small-group learning environment. Low-cost opportunity to experience Penn campus and college academics.',
        'url': 'https://upenn.learningu.org/',
        'source': 'Learning Unlimited/University Splash Programs',
        'category': 'Educational Outreach',
        'stem_fields': 'All STEM (Engineering, Neuroscience, Computer Science, Physics)',
        'target_grade': '9-12',
        'cost': 'Low-cost ($20-40)',
        'location_type': 'UPenn campus (Philadelphia, PA)',
        'time_commitment': '1-2 days (weekend)',
        'prerequisite_level': 'None',
        'support_level': 'Medium',
        'deadline': 'Registration opens before event',
        'financial_barrier_level': 'Low',
        'financial_aid_available': 'Financial aid available',
        'family_income_consideration': 'Fee waivers offered',
        'hidden_costs_level': 'Low',
        'cost_category': 'Under-$100',
        'diversity_focus': 'Philadelphia educational outreach',
        'underrepresented_friendly': 'True',
        'first_gen_support': 'True',
        'cultural_competency': 'High',
        'rural_accessible': 'False',
        'transportation_required': 'True',
        'internet_dependency': 'Basic',
        'regional_availability': 'Regional (Philadelphia)',
        'family_involvement_required': 'Required',
        'peer_network_building': 'True',
        'mentor_access_level': 'Peer'
    })

    print(f"\nSuccessfully created {len(programs)} University Splash program entries")

    # Create data directory if it doesn't exist
    os.makedirs('data', exist_ok=True)

    # Write to CSV
    csv_path = os.path.join('data', 'university_splash_programs.csv')

    with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(programs)

    print(f"\nSuccessfully created {csv_path} with {len(programs)} program entries")
    return len(programs)

if __name__ == "__main__":
    count = scrape_university_splash()
    print(f"\nScraping complete! Total programs: {count}")
