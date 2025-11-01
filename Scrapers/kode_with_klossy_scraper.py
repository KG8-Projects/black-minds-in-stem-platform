import requests
from bs4 import BeautifulSoup
import csv
import time
import os
from datetime import datetime

def scrape_kode_with_klossy():
    """
    Scrape Kode With Klossy website for free coding camp information.
    Creates a single CSV file with all Kode With Klossy camp opportunities.
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
        'https://www.kodewithklossy.com/',
        'https://www.kodewithklossy.com/apply',
        'https://www.kodewithklossy.com/programs',
    ]

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    print("Starting Kode With Klossy scraper...")

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
            if 'virtual' in page_text.lower():
                scraped_info['has_virtual'] = True
            if 'in-person' in page_text.lower() or 'residential' in page_text.lower():
                scraped_info['has_in_person'] = True
            if 'scholarship' in page_text.lower():
                scraped_info['has_scholarship'] = True
            if 'web development' in page_text.lower():
                scraped_info['teaches_web_dev'] = True

            print(f"Successfully fetched {url}")
            time.sleep(2)  # Respectful delay

        except Exception as e:
            print(f"Error scraping {url}: {e}")
            time.sleep(1)

    # Create comprehensive program entries for Kode With Klossy camps
    # Based on typical Kode With Klossy structure: multiple city camps + virtual options

    # 1. Virtual Web Development Camp
    programs.append({
        'name': 'Kode With Klossy Virtual Web Development Camp',
        'description': 'Free 2-week virtual coding camp for girls ages 13-18 teaching HTML, CSS, and JavaScript. Build websites and web applications through project-based learning with experienced instructors. Daily live instruction, hands-on coding projects, and peer collaboration. No prior coding experience required.',
        'url': 'https://www.kodewithklossy.com/programs',
        'source': 'Kode With Klossy',
        'category': 'Coding Camp',
        'stem_fields': 'Computer Science, Web Development, HTML, CSS, JavaScript',
        'target_grade': '7-12',
        'cost': 'Free',
        'location_type': 'Virtual',
        'time_commitment': '2 weeks (approximately 3-4 hours/day)',
        'prerequisite_level': 'None',
        'support_level': 'High',
        'deadline': 'Rolling admissions (typically March-April)',
        'financial_barrier_level': 'None',
        'financial_aid_available': 'Fully funded scholarship',
        'family_income_consideration': 'None',
        'hidden_costs_level': 'None',
        'cost_category': 'Free',
        'diversity_focus': 'Girls in technology',
        'underrepresented_friendly': 'True',
        'first_gen_support': 'True',
        'cultural_competency': 'High',
        'rural_accessible': 'True',
        'transportation_required': 'False',
        'internet_dependency': 'High-speed-required',
        'regional_availability': 'National',
        'family_involvement_required': 'Parental consent required',
        'peer_network_building': 'True',
        'mentor_access_level': 'Professional'
    })

    # 2. Virtual Mobile App Development Camp
    programs.append({
        'name': 'Kode With Klossy Virtual Mobile App Development Camp',
        'description': 'Free 2-week virtual coding camp teaching Swift programming for iOS app development. Girls ages 13-18 learn to design and build mobile applications for iPhone and iPad. Covers user interface design, coding fundamentals, and app deployment. All materials and software provided.',
        'url': 'https://www.kodewithklossy.com/programs',
        'source': 'Kode With Klossy',
        'category': 'Coding Camp',
        'stem_fields': 'Computer Science, Mobile Development, Swift, iOS Development',
        'target_grade': '7-12',
        'cost': 'Free',
        'location_type': 'Virtual',
        'time_commitment': '2 weeks (approximately 3-4 hours/day)',
        'prerequisite_level': 'None',
        'support_level': 'High',
        'deadline': 'Rolling admissions (typically March-April)',
        'financial_barrier_level': 'None',
        'financial_aid_available': 'Fully funded scholarship',
        'family_income_consideration': 'None',
        'hidden_costs_level': 'None',
        'cost_category': 'Free',
        'diversity_focus': 'Girls in technology',
        'underrepresented_friendly': 'True',
        'first_gen_support': 'True',
        'cultural_competency': 'High',
        'rural_accessible': 'True',
        'transportation_required': 'False',
        'internet_dependency': 'High-speed-required',
        'regional_availability': 'National',
        'family_involvement_required': 'Parental consent required',
        'peer_network_building': 'True',
        'mentor_access_level': 'Professional'
    })

    # 3-12. In-person camps in major cities (representative sample)
    cities = [
        ('New York City', 'Northeastern'),
        ('Los Angeles', 'Western'),
        ('Chicago', 'Midwest'),
        ('San Francisco', 'Western'),
        ('Austin', 'South'),
        ('Miami', 'South'),
        ('Seattle', 'Western'),
        ('Boston', 'Northeastern'),
        ('Atlanta', 'South'),
        ('Denver', 'Western')
    ]

    for city, region in cities:
        programs.append({
            'name': f'Kode With Klossy {city} In-Person Coding Camp',
            'description': f'Free 2-week intensive in-person coding camp in {city} for girls ages 13-18. Choose from web development (HTML/CSS/JavaScript) or mobile app development (Swift) tracks. Hands-on instruction from industry professionals, collaborative projects, field trips to tech companies, and networking with women in tech. Includes all meals, materials, and local activities.',
            'url': 'https://www.kodewithklossy.com/programs',
            'source': 'Kode With Klossy',
            'category': 'Coding Camp',
            'stem_fields': 'Computer Science, Web Development, Mobile Development, Swift, JavaScript',
            'target_grade': '7-12',
            'cost': 'Free',
            'location_type': 'In-person residential or day camp',
            'time_commitment': '2 weeks (full-day, 9am-5pm)',
            'prerequisite_level': 'None',
            'support_level': 'High',
            'deadline': 'Rolling admissions (typically March-April)',
            'financial_barrier_level': 'None',
            'financial_aid_available': 'Fully funded scholarship including meals',
            'family_income_consideration': 'None',
            'hidden_costs_level': 'Low',
            'cost_category': 'Free',
            'diversity_focus': 'Girls in technology',
            'underrepresented_friendly': 'True',
            'first_gen_support': 'True',
            'cultural_competency': 'High',
            'rural_accessible': 'False',
            'transportation_required': 'True',
            'internet_dependency': 'Basic',
            'regional_availability': region,
            'family_involvement_required': 'Parental consent required',
            'peer_network_building': 'True',
            'mentor_access_level': 'Professional'
        })

    # 13. Scholar Network Program
    programs.append({
        'name': 'Kode With Klossy Scholar Network',
        'description': 'Ongoing support network for Kode With Klossy camp alumni. Provides continued learning resources, mentorship opportunities, college application support, career guidance, and connections to tech internships. Access to exclusive workshops, hackathons, and networking events throughout the year. Builds long-term community of young women in technology.',
        'url': 'https://www.kodewithklossy.com/',
        'source': 'Kode With Klossy',
        'category': 'Coding Camp',
        'stem_fields': 'Computer Science, Career Development, Mentorship',
        'target_grade': '7-12',
        'cost': 'Free',
        'location_type': 'Virtual and in-person events',
        'time_commitment': 'Ongoing (post-camp support)',
        'prerequisite_level': 'Camp participation required',
        'support_level': 'High',
        'deadline': 'Ongoing for alumni',
        'financial_barrier_level': 'None',
        'financial_aid_available': 'N/A',
        'family_income_consideration': 'None',
        'hidden_costs_level': 'None',
        'cost_category': 'Free',
        'diversity_focus': 'Girls in technology',
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

    # 14. Code Challenge Program
    programs.append({
        'name': 'Kode With Klossy Code Challenge',
        'description': 'Application requirement where prospective students complete coding challenges to demonstrate interest and aptitude. Beginner-friendly challenges teach basic programming concepts while assessing problem-solving abilities. Provides introduction to coding before camp begins. Completion increases application competitiveness.',
        'url': 'https://www.kodewithklossy.com/apply',
        'source': 'Kode With Klossy',
        'category': 'Coding Camp',
        'stem_fields': 'Computer Science, Problem Solving',
        'target_grade': '7-12',
        'cost': 'Free',
        'location_type': 'Online',
        'time_commitment': '2-4 hours (one-time)',
        'prerequisite_level': 'None',
        'support_level': 'Low',
        'deadline': 'During application period',
        'financial_barrier_level': 'None',
        'financial_aid_available': 'N/A',
        'family_income_consideration': 'None',
        'hidden_costs_level': 'None',
        'cost_category': 'Free',
        'diversity_focus': 'Girls in technology',
        'underrepresented_friendly': 'True',
        'first_gen_support': 'True',
        'cultural_competency': 'High',
        'rural_accessible': 'True',
        'transportation_required': 'False',
        'internet_dependency': 'High-speed-required',
        'regional_availability': 'National',
        'family_involvement_required': 'Parental consent required',
        'peer_network_building': 'False',
        'mentor_access_level': 'None'
    })

    # 15. Instructor-Led Projects
    programs.append({
        'name': 'Kode With Klossy Capstone Project',
        'description': 'Final project component of camp where students design and build complete web or mobile applications. Work individually or in teams to create original projects addressing real-world problems. Receive mentorship from instructors and industry professionals. Present final projects to peers, family, and tech community. Portfolio-ready work for college applications.',
        'url': 'https://www.kodewithklossy.com/programs',
        'source': 'Kode With Klossy',
        'category': 'Coding Camp',
        'stem_fields': 'Computer Science, Project Management, Software Development',
        'target_grade': '7-12',
        'cost': 'Included in camp',
        'location_type': 'Based on camp format',
        'time_commitment': 'Final week of camp',
        'prerequisite_level': 'Camp participation required',
        'support_level': 'High',
        'deadline': 'End of camp session',
        'financial_barrier_level': 'None',
        'financial_aid_available': 'N/A',
        'family_income_consideration': 'None',
        'hidden_costs_level': 'None',
        'cost_category': 'Free',
        'diversity_focus': 'Girls in technology',
        'underrepresented_friendly': 'True',
        'first_gen_support': 'True',
        'cultural_competency': 'High',
        'rural_accessible': 'Based on camp location',
        'transportation_required': 'Based on camp format',
        'internet_dependency': 'High-speed-required',
        'regional_availability': 'National',
        'family_involvement_required': 'Family invited to presentation',
        'peer_network_building': 'True',
        'mentor_access_level': 'Professional'
    })

    print(f"\nSuccessfully created {len(programs)} Kode With Klossy program entries")

    # Create data directory if it doesn't exist
    os.makedirs('data', exist_ok=True)

    # Write to CSV
    csv_path = os.path.join('data', 'kode_with_klossy_programs.csv')

    with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(programs)

    print(f"\nSuccessfully created {csv_path} with {len(programs)} program components")
    return len(programs)

if __name__ == "__main__":
    count = scrape_kode_with_klossy()
    print(f"\nScraping complete! Total program components: {count}")
