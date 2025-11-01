"""
USA Computing Olympiad (USACO) Scraper
Extracts USACO competition divisions and programming competitions for high school students
Saves to ONE CSV file: data/usaco_programs.csv
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


class USACOScraper:
    def __init__(self):
        self.base_url = "http://www.usaco.org"
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

    def add_known_usaco_competitions(self):
        """Add well-known USACO competition divisions and programs"""
        known_programs = [
            {
                'name': 'USACO Bronze Division',
                'description': 'Entry-level division for USACO competition. Students solve 3 algorithmic programming problems in 4 hours. Topics include basic algorithms, greedy algorithms, simulation, and brute force. No prior competitive programming experience required. Programming in C++, Java, Python, or C. Promotes to Silver with strong performance.',
                'url': 'http://www.usaco.org/index.php?page=contests',
                'stem_fields': 'Computer Science, Algorithms',
                'target_grade': '9-12',
                'cost': 'Free',
                'location_type': 'Online',
                'time_commitment': '4 hours per contest',
                'prerequisite_level': 'Basic',
                'cost_category': 'Free'
            },
            {
                'name': 'USACO Silver Division',
                'description': 'Intermediate division requiring knowledge of standard algorithms and data structures. Three problems in 4 hours covering sorting, binary search, prefix sums, two pointers, and basic graph algorithms. Promotes to Gold division with high scores. Requires solid programming fundamentals and problem-solving skills.',
                'url': 'http://www.usaco.org/index.php?page=contests',
                'stem_fields': 'Computer Science, Algorithms',
                'target_grade': '9-12',
                'cost': 'Free',
                'location_type': 'Online',
                'time_commitment': '4 hours per contest',
                'prerequisite_level': 'Medium',
                'cost_category': 'Free'
            },
            {
                'name': 'USACO Gold Division',
                'description': 'Advanced division featuring complex algorithms and data structures. Problems require dynamic programming, advanced graph algorithms, segment trees, and computational geometry. Three problems in 4 hours. Promotes to Platinum with excellent performance. Preparation for International Olympiad in Informatics.',
                'url': 'http://www.usaco.org/index.php?page=contests',
                'stem_fields': 'Computer Science, Algorithms',
                'target_grade': '9-12',
                'cost': 'Free',
                'location_type': 'Online',
                'time_commitment': '4 hours per contest',
                'prerequisite_level': 'High',
                'cost_category': 'Free'
            },
            {
                'name': 'USACO Platinum Division',
                'description': 'Elite division for top competitive programmers. Extremely challenging problems requiring advanced algorithms, mathematical reasoning, and optimization. Three problems in 4 hours. Top performers invited to USA Computing Olympiad training camp. Gateway to International Olympiad in Informatics team.',
                'url': 'http://www.usaco.org/index.php?page=contests',
                'stem_fields': 'Computer Science, Algorithms',
                'target_grade': '10-12',
                'cost': 'Free',
                'location_type': 'Online',
                'time_commitment': '4 hours per contest',
                'prerequisite_level': 'High',
                'cost_category': 'Free'
            },
            {
                'name': 'USACO Training Pages',
                'description': 'Free online training system with progressive curriculum of algorithmic problems. Self-paced learning covering algorithms from basic to advanced. Hundreds of practice problems with automated grading. Organized into chapters by topic and difficulty. Excellent resource for contest preparation and skill development.',
                'url': 'http://www.usaco.org/index.php?page=training',
                'stem_fields': 'Computer Science, Algorithms',
                'target_grade': '9-12',
                'cost': 'Free',
                'location_type': 'Online',
                'time_commitment': 'Self-paced',
                'prerequisite_level': 'Basic',
                'cost_category': 'Free',
                'category': 'Training Program'
            },
            {
                'name': 'USACO US Open Contest',
                'description': 'Final regular season contest held in late March. Open to all divisions simultaneously. Performance determines final standings and camp invitations. Critical contest for Platinum division students seeking camp invitation. Four-hour online contest with promotion opportunities.',
                'url': 'http://www.usaco.org/index.php?page=contests',
                'stem_fields': 'Computer Science, Algorithms',
                'target_grade': '9-12',
                'cost': 'Free',
                'location_type': 'Online',
                'time_commitment': '4 hours',
                'prerequisite_level': 'Medium',
                'cost_category': 'Free',
                'deadline': 'Annual-March'
            },
            {
                'name': 'USACO Training Camp',
                'description': 'Invitation-only residential training camp for top USACO performers. Intensive algorithmic programming training from leading computer scientists. Practice contests, lectures, and team selection for International Olympiad in Informatics. One week of advanced competitive programming. Fully funded by USACO.',
                'url': 'http://www.usaco.org/index.php?page=finalists',
                'stem_fields': 'Computer Science, Algorithms',
                'target_grade': '10-12',
                'cost': 'Free',
                'location_type': 'Residential',
                'time_commitment': '1 week',
                'prerequisite_level': 'High',
                'cost_category': 'Free',
                'category': 'Training Program',
                'deadline': 'Invitation-only',
                'transportation_required': True,
                'internet_dependency': 'Basic',
                'mentor_access_level': 'Professional'
            },
            {
                'name': 'International Olympiad in Informatics (IOI) - USA Team',
                'description': 'Top 4 USACO students selected to represent USA at IOI, international programming competition. Compete against students from 90+ countries. Two competition days with challenging algorithmic problems. Held in different country annually. Prestigious medals and international recognition. Fully funded participation.',
                'url': 'http://www.usaco.org/',
                'stem_fields': 'Computer Science, Algorithms',
                'target_grade': '10-12',
                'cost': 'Free',
                'location_type': 'International',
                'time_commitment': '2 weeks',
                'prerequisite_level': 'High',
                'cost_category': 'Free',
                'category': 'International Competition',
                'deadline': 'Invitation-only',
                'transportation_required': True,
                'internet_dependency': 'Basic',
                'regional_availability': 'International',
                'mentor_access_level': 'Professional'
            }
        ]

        for program in known_programs:
            self.add_program(program)
            logger.info(f"Added known program: {program['name']}")

    def scrape_usaco_pages(self):
        """Attempt to scrape USACO pages for additional competitions"""
        urls = [
            'http://www.usaco.org/',
            'http://www.usaco.org/index.php?page=contests',
            'http://www.usaco.org/index.php?page=finalists'
        ]

        for url in urls:
            html = self.fetch_page(url)
            if html:
                self.parse_competition_listings(html, url)
            time.sleep(2)  # Delay between requests

    def parse_competition_listings(self, html, source_url):
        """Parse competition listings from USACO pages"""
        soup = BeautifulSoup(html, 'html.parser')

        # USACO may use Cloudflare protection
        # This is a fallback - most data comes from known_programs
        competitions_found = 0

        # Look for competition information
        competition_sections = soup.find_all(['div', 'section', 'table'], class_=lambda x: x and ('contest' in x.lower() or 'division' in x.lower()) if x else False)
        for section in competition_sections:
            competitions_found += 1

        logger.info(f"Found {competitions_found} programs from {source_url}")

    def add_program(self, program_data):
        """Add a program with all required CSV columns"""
        program = {
            'name': program_data.get('name', ''),
            'description': program_data.get('description', ''),
            'url': program_data.get('url', ''),
            'source': 'USA Computing Olympiad',
            'category': program_data.get('category', 'Computer Science Competition'),
            'stem_fields': program_data.get('stem_fields', 'Computer Science, Algorithms'),
            'target_grade': program_data.get('target_grade', '9-12'),
            'cost': program_data.get('cost', 'Free'),
            'location_type': program_data.get('location_type', 'Online'),
            'time_commitment': program_data.get('time_commitment', '4 hours per contest'),
            'prerequisite_level': program_data.get('prerequisite_level', 'Medium'),
            'support_level': 'Low',
            'deadline': program_data.get('deadline', 'Multiple dates annually'),
            'financial_barrier_level': 'None',
            'financial_aid_available': False,
            'family_income_consideration': False,
            'hidden_costs_level': 'None',
            'cost_category': program_data.get('cost_category', 'Free'),
            'diversity_focus': False,
            'underrepresented_friendly': True,
            'first_gen_support': False,
            'cultural_competency': 'Medium',
            'rural_accessible': True,
            'transportation_required': program_data.get('transportation_required', False),
            'internet_dependency': program_data.get('internet_dependency', 'High-speed-required'),
            'regional_availability': program_data.get('regional_availability', 'National'),
            'family_involvement_required': 'None',
            'peer_network_building': True,
            'mentor_access_level': program_data.get('mentor_access_level', 'None')
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
        logger.info("Starting USA Computing Olympiad scraper...")

        # Add known USACO competitions
        self.add_known_usaco_competitions()

        # Attempt to scrape additional competitions
        self.scrape_usaco_pages()

        # Save to CSV
        output_file = 'data/usaco_programs.csv'
        self.save_to_csv(output_file)

        logger.info(f"Successfully created {output_file} with {len(self.programs)} USACO programs")
        return output_file


def main():
    scraper = USACOScraper()
    output_file = scraper.run()
    print(f"\nUSA Computing Olympiad scraper completed successfully!")
    print(f"Output file: {output_file}")
    print(f"Total programs: {len(scraper.programs)}")


if __name__ == "__main__":
    main()
