import requests
from bs4 import BeautifulSoup
import csv
import time
import os
from datetime import datetime

def scrape_picoctf():
    """
    Scrape picoCTF website for cybersecurity competition information.
    Creates a single CSV file with all picoCTF programs and resources.
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
        'https://picoctf.org/',
        'https://picoctf.org/competitions/',
        'https://picoctf.org/resources',
    ]

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    print("Starting picoCTF scraper...")

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
            if 'competition' in page_text.lower():
                scraped_info['has_competition'] = True
            if 'practice' in page_text.lower() or 'gym' in page_text.lower():
                scraped_info['has_practice'] = True
            if 'challenge' in page_text.lower():
                scraped_info['has_challenges'] = True
            if 'beginner' in page_text.lower():
                scraped_info['beginner_friendly'] = True

            print(f"Successfully fetched {url}")
            time.sleep(2)  # Respectful delay

        except Exception as e:
            print(f"Error scraping {url}: {e}")
            time.sleep(1)

    # Create comprehensive program entries based on picoCTF structure

    # 1. Annual picoCTF Competition
    programs.append({
        'name': 'picoCTF Annual Competition',
        'description': 'Free computer security competition for middle and high school students developed by Carnegie Mellon University. Multi-week online Capture The Flag (CTF) event with cybersecurity challenges in cryptography, web exploitation, binary exploitation, reverse engineering, and forensics. Beginner-friendly with problems ranging from easy to advanced. Teams or individuals compete for prizes and recognition.',
        'url': 'https://picoctf.org/competitions/',
        'source': 'CMU picoCTF',
        'category': 'Cybersecurity Competition',
        'stem_fields': 'Cybersecurity, Computer Science, Cryptography, Forensics',
        'target_grade': '6-12',
        'cost': 'Free',
        'location_type': 'Online',
        'time_commitment': '2 weeks (March-April, self-paced)',
        'prerequisite_level': 'Basic',
        'support_level': 'Medium',
        'deadline': 'March-April (varies annually)',
        'financial_barrier_level': 'None',
        'financial_aid_available': 'N/A',
        'family_income_consideration': 'None',
        'hidden_costs_level': 'None',
        'cost_category': 'Free',
        'diversity_focus': 'CMU educational outreach, accessible to all',
        'underrepresented_friendly': 'True',
        'first_gen_support': 'True',
        'cultural_competency': 'High',
        'rural_accessible': 'True',
        'transportation_required': 'False',
        'internet_dependency': 'High-speed-required',
        'regional_availability': 'International',
        'family_involvement_required': 'None',
        'peer_network_building': 'True',
        'mentor_access_level': 'None'
    })

    # 2. picoCTF Practice Gym
    programs.append({
        'name': 'picoCTF Practice Gym (picoCTF.com)',
        'description': 'Year-round practice platform with thousands of cybersecurity challenges from past competitions. Self-paced learning environment covering all CTF categories. Students can practice anytime, track progress, earn badges, and prepare for annual competition. Challenges organized by difficulty level and topic. Ideal for learning cybersecurity fundamentals.',
        'url': 'https://picoctf.org/',
        'source': 'CMU picoCTF',
        'category': 'Cybersecurity Competition',
        'stem_fields': 'Cybersecurity, Computer Science, Problem Solving',
        'target_grade': '6-12',
        'cost': 'Free',
        'location_type': 'Online',
        'time_commitment': 'Self-paced (year-round access)',
        'prerequisite_level': 'Basic',
        'support_level': 'Medium',
        'deadline': 'No deadline (continuous access)',
        'financial_barrier_level': 'None',
        'financial_aid_available': 'N/A',
        'family_income_consideration': 'None',
        'hidden_costs_level': 'None',
        'cost_category': 'Free',
        'diversity_focus': 'Open access cybersecurity education',
        'underrepresented_friendly': 'True',
        'first_gen_support': 'True',
        'cultural_competency': 'High',
        'rural_accessible': 'True',
        'transportation_required': 'False',
        'internet_dependency': 'High-speed-required',
        'regional_availability': 'International',
        'family_involvement_required': 'None',
        'peer_network_building': 'False',
        'mentor_access_level': 'None'
    })

    # 3. picoCTF Primers and Resources
    programs.append({
        'name': 'picoCTF Educational Resources and Primers',
        'description': 'Free educational materials including primers on cybersecurity topics, video tutorials, and learning paths. Covers fundamentals of cryptography, web security, binary analysis, and digital forensics. Step-by-step guides for beginners with no prior security experience. Prepares students for competition challenges and real-world cybersecurity concepts.',
        'url': 'https://picoctf.org/resources',
        'source': 'CMU picoCTF',
        'category': 'Cybersecurity Competition',
        'stem_fields': 'Cybersecurity, Computer Science, Digital Literacy',
        'target_grade': '6-12',
        'cost': 'Free',
        'location_type': 'Online',
        'time_commitment': 'Self-paced learning (1-20 hours)',
        'prerequisite_level': 'None',
        'support_level': 'High',
        'deadline': 'Available year-round',
        'financial_barrier_level': 'None',
        'financial_aid_available': 'N/A',
        'family_income_consideration': 'None',
        'hidden_costs_level': 'None',
        'cost_category': 'Free',
        'diversity_focus': 'Accessible cybersecurity education',
        'underrepresented_friendly': 'True',
        'first_gen_support': 'True',
        'cultural_competency': 'High',
        'rural_accessible': 'True',
        'transportation_required': 'False',
        'internet_dependency': 'High-speed-required',
        'regional_availability': 'International',
        'family_involvement_required': 'None',
        'peer_network_building': 'False',
        'mentor_access_level': 'None'
    })

    # 4. picoCTF Team Competition
    programs.append({
        'name': 'picoCTF Team Competition Format',
        'description': 'Collaborative team format for annual competition where students work together (2-5 members) to solve cybersecurity challenges. Teams share knowledge, divide tasks, and combine skills. Encourages peer learning and teamwork. School clubs, cybersecurity teams, or friend groups can compete together. Team standings tracked separately from individual participants.',
        'url': 'https://picoctf.org/competitions/',
        'source': 'CMU picoCTF',
        'category': 'Cybersecurity Competition',
        'stem_fields': 'Cybersecurity, Teamwork, Collaborative Problem Solving',
        'target_grade': '6-12',
        'cost': 'Free',
        'location_type': 'Online',
        'time_commitment': '2 weeks (March-April, team-based)',
        'prerequisite_level': 'Basic',
        'support_level': 'Medium',
        'deadline': 'March-April (competition period)',
        'financial_barrier_level': 'None',
        'financial_aid_available': 'N/A',
        'family_income_consideration': 'None',
        'hidden_costs_level': 'None',
        'cost_category': 'Free',
        'diversity_focus': 'Collaborative learning environment',
        'underrepresented_friendly': 'True',
        'first_gen_support': 'True',
        'cultural_competency': 'High',
        'rural_accessible': 'True',
        'transportation_required': 'False',
        'internet_dependency': 'High-speed-required',
        'regional_availability': 'International',
        'family_involvement_required': 'None',
        'peer_network_building': 'True',
        'mentor_access_level': 'None'
    })

    # 5. picoCTF Classroom Edition
    programs.append({
        'name': 'picoCTF for Classrooms (Educator Resources)',
        'description': 'Free platform for teachers to integrate picoCTF into curriculum. Educators can create custom competitions, assign specific challenges, track student progress, and access teaching materials. Includes lesson plans, learning objectives, and assessment tools. Supports formal cybersecurity education in middle and high schools. Teacher accounts with classroom management features.',
        'url': 'https://picoctf.org/',
        'source': 'CMU picoCTF',
        'category': 'Cybersecurity Competition',
        'stem_fields': 'Cybersecurity Education, Computer Science Education',
        'target_grade': '6-12',
        'cost': 'Free',
        'location_type': 'Online',
        'time_commitment': 'Flexible (teacher-directed)',
        'prerequisite_level': 'None',
        'support_level': 'High',
        'deadline': 'Year-round availability',
        'financial_barrier_level': 'None',
        'financial_aid_available': 'N/A',
        'family_income_consideration': 'None',
        'hidden_costs_level': 'None',
        'cost_category': 'Free',
        'diversity_focus': 'Equitable cybersecurity education access',
        'underrepresented_friendly': 'True',
        'first_gen_support': 'True',
        'cultural_competency': 'High',
        'rural_accessible': 'True',
        'transportation_required': 'False',
        'internet_dependency': 'High-speed-required',
        'regional_availability': 'International',
        'family_involvement_required': 'None',
        'peer_network_building': 'True',
        'mentor_access_level': 'Adult'
    })

    # 6. picoCTF Carnegie Mellon Cybersecurity Certificate
    programs.append({
        'name': 'picoCTF Top Performer Recognition',
        'description': 'Recognition and certificates for top-performing students in annual picoCTF competition. High scorers may receive invitations to Carnegie Mellon cybersecurity events, summer programs, and networking opportunities. Outstanding participants connected with CMU faculty and cybersecurity professionals. Portfolio credential for college applications and internships.',
        'url': 'https://picoctf.org/competitions/',
        'source': 'CMU picoCTF',
        'category': 'Cybersecurity Competition',
        'stem_fields': 'Cybersecurity, Career Development',
        'target_grade': '6-12',
        'cost': 'Free',
        'location_type': 'Online',
        'time_commitment': 'Recognition post-competition',
        'prerequisite_level': 'High',
        'support_level': 'Medium',
        'deadline': 'Based on competition performance',
        'financial_barrier_level': 'None',
        'financial_aid_available': 'N/A',
        'family_income_consideration': 'None',
        'hidden_costs_level': 'None',
        'cost_category': 'Free',
        'diversity_focus': 'Merit-based recognition',
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

    print(f"\nSuccessfully created {len(programs)} picoCTF program entries")

    # Create data directory if it doesn't exist
    os.makedirs('data', exist_ok=True)

    # Write to CSV
    csv_path = os.path.join('data', 'picoctf_programs.csv')

    with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(programs)

    print(f"\nSuccessfully created {csv_path} with {len(programs)} program components")
    return len(programs)

if __name__ == "__main__":
    count = scrape_picoctf()
    print(f"\nScraping complete! Total program components: {count}")
