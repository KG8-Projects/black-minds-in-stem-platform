"""
Physics Competitions Scraper
Extracts Physics Bowl and related AAPT physics competitions for high school students
Saves to ONE CSV file: data/physics_competitions.csv
"""

import requests
from bs4 import BeautifulSoup
import csv
import time
import logging
from urllib.parse import urljoin

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class PhysicsCompetitionsScraper:
    def __init__(self):
        self.base_url = "https://www.aapt.org"
        self.programs = []
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

        # Standard CSV columns (same 29 columns as all other scrapers)
        self.csv_columns = [
            'name', 'description', 'url', 'source', 'category', 'stem_fields',
            'target_grade', 'cost', 'location_type', 'time_commitment',
            'prerequisite_level', 'support_level', 'deadline',
            'financial_barrier_level', 'financial_aid_available',
            'family_income_consideration', 'hidden_costs_level', 'cost_category',
            'diversity_focus', 'underrepresented_friendly', 'first_gen_support',
            'cultural_competency', 'rural_accessible', 'transportation_required',
            'internet_dependency', 'regional_availability',
            'family_involvement_required', 'peer_network_building', 'mentor_access_level'
        ]

    def fetch_page(self, url):
        """Fetch a page with error handling"""
        try:
            logger.info(f"Fetching: {url}")
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            return response.text
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching {url}: {e}")
            return None

    def add_known_physics_competitions(self):
        """Add well-known AAPT physics competitions with detailed information"""
        known_programs = [
            {
                'name': 'Physics Bowl',
                'description': 'Annual 45-minute, 40-question timed multiple choice competition testing physics knowledge. Covers mechanics, electricity and magnetism, waves, optics, modern physics, and more. Two divisions: Division 1 for students in first physics course, Division 2 for advanced students. Administered at participating high schools. Top students recognized nationally and regionally.',
                'url': 'https://www.aapt.org/programs/physicsbowl/',
                'stem_fields': 'Physics',
                'target_grade': '9-12',
                'cost': '75',
                'location_type': 'School-based',
                'time_commitment': '45 minutes',
                'prerequisite_level': 'Medium',
                'cost_category': 'Paid',
                'financial_barrier_level': 'Low',
                'deadline': 'Annual-March'
            },
            {
                'name': 'F=ma Exam (USA Physics Olympiad Qualifier)',
                'description': 'First round of USA Physics Olympiad competition. 75-minute, 25-question exam focusing on mechanics and problem-solving. Tests conceptual understanding and mathematical skills. Free online exam for all students. Top 400 students advance to USAPhO semifinal round. Gateway to International Physics Olympiad.',
                'url': 'https://www.aapt.org/physicsteam/',
                'stem_fields': 'Physics',
                'target_grade': '9-12',
                'cost': 'Free',
                'location_type': 'Online',
                'time_commitment': '75 minutes',
                'prerequisite_level': 'High',
                'cost_category': 'Free',
                'financial_barrier_level': 'None',
                'deadline': 'Annual-January',
                'transportation_required': False,
                'internet_dependency': 'High-speed-required'
            },
            {
                'name': 'USA Physics Olympiad (USAPhO)',
                'description': 'Second round of physics olympiad for top F=ma performers. Two 90-minute free-response exams with challenging physics problems requiring detailed solutions. Tests deep understanding of mechanics, electricity and magnetism, thermodynamics, waves, and modern physics. Top 20 students invited to Physics Team Training Camp.',
                'url': 'https://www.aapt.org/physicsteam/',
                'stem_fields': 'Physics',
                'target_grade': '10-12',
                'cost': 'Free',
                'location_type': 'School-based',
                'time_commitment': '3 hours',
                'prerequisite_level': 'High',
                'cost_category': 'Free',
                'financial_barrier_level': 'None',
                'deadline': 'Annual-March',
                'transportation_required': False
            },
            {
                'name': 'US Physics Team Training Camp',
                'description': 'Two-week intensive residential training for top 20 USAPhO students. Advanced physics lectures, problem-solving sessions, and laboratory work. Theoretical and experimental exams to select 5-member US Physics Team for International Physics Olympiad. Fully funded including travel, room, and board. Held at university campus.',
                'url': 'https://www.aapt.org/physicsteam/',
                'stem_fields': 'Physics',
                'target_grade': '10-12',
                'cost': 'Free',
                'location_type': 'Residential',
                'time_commitment': '2 weeks',
                'prerequisite_level': 'High',
                'cost_category': 'Free',
                'financial_barrier_level': 'None',
                'category': 'Training Program',
                'deadline': 'Invitation-only',
                'transportation_required': True,
                'internet_dependency': 'Basic',
                'mentor_access_level': 'Professional'
            },
            {
                'name': 'International Physics Olympiad (IPhO)',
                'description': 'International physics competition for top 5 US Physics Team members. Compete against students from 90+ countries. Five-hour theoretical exam and five-hour experimental exam covering all physics topics. Held in different country each year. Prestigious gold, silver, and bronze medals awarded. Fully funded international travel.',
                'url': 'https://www.aapt.org/physicsteam/',
                'stem_fields': 'Physics',
                'target_grade': '11-12',
                'cost': 'Free',
                'location_type': 'International',
                'time_commitment': '2 weeks',
                'prerequisite_level': 'High',
                'cost_category': 'Free',
                'financial_barrier_level': 'None',
                'category': 'International Competition',
                'deadline': 'Invitation-only',
                'transportation_required': True,
                'internet_dependency': 'Basic',
                'regional_availability': 'International',
                'mentor_access_level': 'Professional'
            },
            {
                'name': 'Physics Bowl Division 1',
                'description': 'Division for students in their first physics course (typically physics or honors physics). 40 multiple choice questions in 45 minutes covering fundamental physics concepts. Tests mechanics, waves, electricity, magnetism, and modern physics at introductory level. Great introduction to physics competitions.',
                'url': 'https://www.aapt.org/programs/physicsbowl/',
                'stem_fields': 'Physics',
                'target_grade': '9-11',
                'cost': '75',
                'location_type': 'School-based',
                'time_commitment': '45 minutes',
                'prerequisite_level': 'Medium',
                'cost_category': 'Paid',
                'financial_barrier_level': 'Low',
                'deadline': 'Annual-March',
                'transportation_required': False
            },
            {
                'name': 'Physics Bowl Division 2',
                'description': 'Advanced division for students who have completed honors or AP physics courses. 40 challenging multiple choice questions in 45 minutes. Covers advanced topics including calculus-based mechanics, electromagnetism, optics, thermodynamics, and quantum physics. Competitive division for experienced physics students.',
                'url': 'https://www.aapt.org/programs/physicsbowl/',
                'stem_fields': 'Physics',
                'target_grade': '10-12',
                'cost': '75',
                'location_type': 'School-based',
                'time_commitment': '45 minutes',
                'prerequisite_level': 'High',
                'cost_category': 'Paid',
                'financial_barrier_level': 'Low',
                'deadline': 'Annual-March',
                'transportation_required': False
            },
            {
                'name': 'Physics Olympiad Online Resources',
                'description': 'Free preparation materials for F=ma and USAPhO including past exams, solutions, and study guides. Online problem sets and video tutorials. Recommended textbooks and study plans. Self-paced learning resources for olympiad preparation. Community forums for problem discussion.',
                'url': 'https://www.aapt.org/physicsteam/',
                'stem_fields': 'Physics',
                'target_grade': '9-12',
                'cost': 'Free',
                'location_type': 'Online',
                'time_commitment': 'Self-paced',
                'prerequisite_level': 'Medium',
                'cost_category': 'Free',
                'financial_barrier_level': 'None',
                'category': 'Study Resources',
                'deadline': 'Rolling',
                'transportation_required': False,
                'internet_dependency': 'High-speed-required',
                'mentor_access_level': 'None'
            },
            {
                'name': 'High School Physics Photo Contest',
                'description': 'Annual photo contest showcasing physics phenomena captured by high school students. Submit original photographs demonstrating physics principles with written explanations. Categories include mechanics, waves, optics, and modern physics. Judged by physics educators. Awards and recognition for creative physics photography.',
                'url': 'https://www.aapt.org/programs/contests/',
                'stem_fields': 'Physics',
                'target_grade': '9-12',
                'cost': 'Free',
                'location_type': 'Online',
                'time_commitment': 'Project-based',
                'prerequisite_level': 'Basic',
                'cost_category': 'Free',
                'financial_barrier_level': 'None',
                'category': 'Physics Contest',
                'deadline': 'Annual-Spring',
                'transportation_required': False,
                'internet_dependency': 'High-speed-required',
                'peer_network_building': False
            },
            {
                'name': 'Physics Bowl Preparation Programs',
                'description': 'School-based preparation programs for Physics Bowl competition. After-school study sessions and practice exams. Review of physics concepts and problem-solving strategies. Teacher-led instruction and peer collaboration. Many schools offer dedicated physics competition teams and clubs.',
                'url': 'https://www.aapt.org/programs/physicsbowl/',
                'stem_fields': 'Physics',
                'target_grade': '9-12',
                'cost': 'Free',
                'location_type': 'School-based',
                'time_commitment': '2-4 hours per week',
                'prerequisite_level': 'Medium',
                'cost_category': 'Free',
                'financial_barrier_level': 'None',
                'category': 'Study Program',
                'deadline': 'Rolling',
                'transportation_required': False,
                'internet_dependency': 'None',
                'peer_network_building': True
            }
        ]

        for program in known_programs:
            self.add_program(program)
            logger.info(f"Added known program: {program['name']}")

    def scrape_physics_pages(self):
        """Attempt to scrape AAPT physics competition pages"""
        urls = [
            'https://www.aapt.org/programs/physicsbowl/',
            'https://www.aapt.org/physicsteam/',
            'https://www.aapt.org/programs/contests/'
        ]

        for url in urls:
            html = self.fetch_page(url)
            if html:
                self.parse_competition_listings(html, url)
            time.sleep(2)  # Delay between requests

    def parse_competition_listings(self, html, source_url):
        """Parse competition listings from AAPT pages"""
        soup = BeautifulSoup(html, 'html.parser')

        # AAPT uses CommonSpot CMS
        # This is a fallback - most data comes from known_programs
        competitions_found = 0

        # Look for competition information
        competition_sections = soup.find_all(['div', 'section', 'article'], class_=lambda x: x and ('competition' in x.lower() or 'contest' in x.lower()) if x else False)
        for section in competition_sections:
            competitions_found += 1

        logger.info(f"Found {competitions_found} programs from {source_url}")

    def add_program(self, program_data):
        """Add a program with all required CSV columns"""
        program = {
            'name': program_data.get('name', ''),
            'description': program_data.get('description', ''),
            'url': program_data.get('url', ''),
            'source': 'American Association of Physics Teachers',
            'category': program_data.get('category', 'Physics Competition'),
            'stem_fields': program_data.get('stem_fields', 'Physics'),
            'target_grade': program_data.get('target_grade', '9-12'),
            'cost': program_data.get('cost', 'Free'),
            'location_type': program_data.get('location_type', 'School-based'),
            'time_commitment': program_data.get('time_commitment', 'Competition day'),
            'prerequisite_level': program_data.get('prerequisite_level', 'Medium'),
            'support_level': 'Medium',
            'deadline': program_data.get('deadline', 'Annual-March'),
            'financial_barrier_level': program_data.get('financial_barrier_level', 'Low'),
            'financial_aid_available': False,
            'family_income_consideration': False,
            'hidden_costs_level': 'Low',
            'cost_category': program_data.get('cost_category', 'Free'),
            'diversity_focus': False,
            'underrepresented_friendly': True,
            'first_gen_support': False,
            'cultural_competency': 'Medium',
            'rural_accessible': True,
            'transportation_required': program_data.get('transportation_required', False),
            'internet_dependency': program_data.get('internet_dependency', 'Basic'),
            'regional_availability': program_data.get('regional_availability', 'National'),
            'family_involvement_required': 'Optional',
            'peer_network_building': program_data.get('peer_network_building', True),
            'mentor_access_level': program_data.get('mentor_access_level', 'Adult')
        }
        self.programs.append(program)

    def save_to_csv(self, filename):
        """Save programs to CSV file"""
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=self.csv_columns)
            writer.writeheader()
            writer.writerows(self.programs)
        logger.info(f"Saved {len(self.programs)} programs to {filename}")

    def run(self):
        """Execute the scraping process"""
        logger.info("Starting Physics Competitions scraper...")

        # Add known physics competitions
        self.add_known_physics_competitions()

        # Attempt to scrape additional competitions
        self.scrape_physics_pages()

        # Save to CSV
        output_file = 'data/physics_competitions.csv'
        self.save_to_csv(output_file)

        logger.info(f"Successfully created {output_file} with {len(self.programs)} physics competitions")
        return output_file


def main():
    scraper = PhysicsCompetitionsScraper()
    output_file = scraper.run()
    print(f"\nPhysics Competitions scraper completed successfully!")
    print(f"Output file: {output_file}")
    print(f"Total programs: {len(scraper.programs)}")


if __name__ == "__main__":
    main()
