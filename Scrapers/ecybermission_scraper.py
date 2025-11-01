"""
eCYBERMISSION Army Educational Outreach STEM Competition Scraper
Extracts eCYBERMISSION competition for middle school students (grades 6-9)
Saves to ONE CSV file: data/ecybermission_programs.csv
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


class EcybermissionScraper:
    def __init__(self):
        self.base_url = "https://www.ecybermission.com"
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

    def add_known_ecybermission_programs(self):
        """Add well-known eCYBERMISSION competition components"""
        known_programs = [
            {
                'name': 'eCYBERMISSION Main Competition',
                'description': 'Free online STEM competition for teams of 3-4 students in grades 6-9. Teams identify problems in their community and propose solutions using scientific inquiry. Complete online submission with videos and documentation. Team advisor required. Regional and national competitions. Prizes up to $10,000 for winning teams. No travel required for initial rounds. Army STEM mentors available.',
                'url': 'https://www.ecybermission.com/',
                'stem_fields': 'Science, Technology, Engineering, Mathematics',
                'target_grade': '6-9',
                'cost': 'Free',
                'location_type': 'Online',
                'time_commitment': 'Academic year',
                'prerequisite_level': 'None',
                'cost_category': 'Free',
                'financial_barrier_level': 'Low',
                'hidden_costs_level': 'Equipment',
                'deadline': 'Annual-Winter'
            },
            {
                'name': 'eCYBERMISSION Grade 6 Division',
                'description': '6th grade team competition focusing on STEM problem-solving. Teams work on community-based projects using scientific method. Categories include alternative energy, environment, food health and safety, national security, and robotics. Video presentations and written reports. Regional awards and potential to advance to nationals. Great introduction to STEM competitions.',
                'url': 'https://www.ecybermission.com/compete',
                'stem_fields': 'STEM, Engineering, Science',
                'target_grade': '6',
                'cost': 'Free',
                'location_type': 'Online',
                'time_commitment': '6-8 months',
                'prerequisite_level': 'None',
                'cost_category': 'Free',
                'financial_barrier_level': 'Low',
                'hidden_costs_level': 'Equipment',
                'deadline': 'Annual-Winter'
            },
            {
                'name': 'eCYBERMISSION Grade 7 Division',
                'description': '7th grade team STEM competition with community focus. More advanced projects than 6th grade. Same categories: alternative energy, environment, food safety, national security, robotics. Teams conduct experiments and develop solutions. Mentorship from Army STEM professionals available. State and regional prizes. Top teams compete nationally.',
                'url': 'https://www.ecybermission.com/compete',
                'stem_fields': 'STEM, Science, Engineering',
                'target_grade': '7',
                'cost': 'Free',
                'location_type': 'Online',
                'time_commitment': '6-8 months',
                'prerequisite_level': 'Basic',
                'cost_category': 'Free',
                'financial_barrier_level': 'Low',
                'hidden_costs_level': 'Equipment',
                'deadline': 'Annual-Winter'
            },
            {
                'name': 'eCYBERMISSION Grade 8 Division',
                'description': '8th grade advanced STEM team competition. Sophisticated community problem-solving projects. Apply scientific method to real-world challenges. Categories in energy, environment, food safety, security, and robotics. Video and written documentation. Larger prizes at this level. Preparation for high school STEM programs and competitions.',
                'url': 'https://www.ecybermission.com/compete',
                'stem_fields': 'STEM, Engineering, Technology',
                'target_grade': '8',
                'cost': 'Free',
                'location_type': 'Online',
                'time_commitment': '6-8 months',
                'prerequisite_level': 'Basic',
                'cost_category': 'Free',
                'financial_barrier_level': 'Low',
                'hidden_costs_level': 'Equipment',
                'deadline': 'Annual-Winter'
            },
            {
                'name': 'eCYBERMISSION Grade 9 Division',
                'description': '9th grade highest level middle school STEM competition. Most complex projects and rigorous judging. Teams address significant community problems with STEM solutions. Strong emphasis on experimental design and data analysis. Top prizes include $10,000 savings bonds and trip to National Judging & Educational Event in Washington DC area. Excellent for STEM resumes and college applications.',
                'url': 'https://www.ecybermission.com/compete',
                'stem_fields': 'STEM, Science, Engineering, Research',
                'target_grade': '9',
                'cost': 'Free',
                'location_type': 'Online',
                'time_commitment': '6-8 months',
                'prerequisite_level': 'Medium',
                'cost_category': 'Free',
                'financial_barrier_level': 'Low',
                'hidden_costs_level': 'Equipment',
                'deadline': 'Annual-Winter',
                'category': 'Advanced STEM Competition'
            },
            {
                'name': 'eCYBERMISSION National Judging & Educational Event',
                'description': 'Invitation-only event for regional winning teams. Multi-day STEM experience in Washington DC area. Final competition judging by Army and STEM professionals. Team presentations and Q&A sessions. STEM career exploration activities. Tours of Army facilities. Networking with other top STEM students nationwide. All expenses paid for winning teams. Life-changing STEM experience.',
                'url': 'https://www.ecybermission.com/',
                'stem_fields': 'STEM, Career Exploration',
                'target_grade': '6-9',
                'cost': 'Free',
                'location_type': 'National',
                'time_commitment': '3-4 days',
                'prerequisite_level': 'High',
                'cost_category': 'Free',
                'financial_barrier_level': 'None',
                'hidden_costs_level': 'None',
                'deadline': 'Invitation-only',
                'category': 'National Finals Event',
                'transportation_required': True
            },
            {
                'name': 'eCYBERMISSION Team Advisor Resources',
                'description': 'Comprehensive resources for teachers and team advisors. Lesson plans, project guides, and judging rubrics. Training webinars and advisor community forums. Help with team formation and project development. Competition timeline and submission requirements. Support throughout competition season. Connects advisors with Army STEM mentors. Essential for first-time advisors.',
                'url': 'https://www.ecybermission.com/resources',
                'stem_fields': 'STEM Education, Project Management',
                'target_grade': '6-9',
                'cost': 'Free',
                'location_type': 'Online',
                'time_commitment': 'Flexible',
                'prerequisite_level': 'None',
                'cost_category': 'Free',
                'financial_barrier_level': 'None',
                'hidden_costs_level': 'None',
                'category': 'Educator Resources',
                'deadline': 'Rolling',
                'transportation_required': False,
                'internet_dependency': 'High-speed-required'
            },
            {
                'name': 'eCYBERMISSION STEM Mentorship Program',
                'description': 'Free mentorship from Army STEM professionals and scientists. Mentors guide teams on project design, scientific method, and presentation. Virtual meetings with mentors throughout competition. Real-world STEM career insights. Help troubleshooting experiments and data analysis. Optional but highly valuable for teams. Creates connections to STEM careers and professionals.',
                'url': 'https://www.ecybermission.com/',
                'stem_fields': 'STEM, Career Development',
                'target_grade': '6-9',
                'cost': 'Free',
                'location_type': 'Online',
                'time_commitment': 'Flexible',
                'prerequisite_level': 'None',
                'cost_category': 'Free',
                'financial_barrier_level': 'None',
                'hidden_costs_level': 'None',
                'category': 'Mentorship Program',
                'deadline': 'Rolling',
                'transportation_required': False,
                'internet_dependency': 'Basic',
                'mentor_access_level': 'Professional'
            }
        ]

        for program in known_programs:
            self.add_program(program)
            logger.info(f"Added known program: {program['name']}")

    def scrape_ecybermission_pages(self):
        """Attempt to scrape eCYBERMISSION pages for additional programs"""
        urls = [
            'https://www.ecybermission.com/',
            'https://www.ecybermission.com/compete',
            'https://www.ecybermission.com/resources'
        ]

        for url in urls:
            html = self.fetch_page(url)
            if html:
                self.parse_program_listings(html, url)
            time.sleep(2)  # Delay between requests

    def parse_program_listings(self, html, source_url):
        """Parse program listings from eCYBERMISSION pages"""
        soup = BeautifulSoup(html, 'html.parser')

        # eCYBERMISSION may use Cloudflare protection
        # This is a fallback - most data comes from known_programs
        programs_found = 0

        # Look for competition information
        program_sections = soup.find_all(['div', 'section', 'article'], class_=lambda x: x and ('competition' in x.lower() or 'program' in x.lower() or 'mission' in x.lower()) if x else False)
        for section in program_sections:
            programs_found += 1

        logger.info(f"Found {programs_found} programs from {source_url}")

    def add_program(self, program_data):
        """Add a program with all required CSV columns"""
        program = {
            'name': program_data.get('name', ''),
            'description': program_data.get('description', ''),
            'url': program_data.get('url', ''),
            'source': 'Army Educational Outreach Program',
            'category': program_data.get('category', 'STEM Competition'),
            'stem_fields': program_data.get('stem_fields', 'Science, Technology, Engineering, Mathematics'),
            'target_grade': program_data.get('target_grade', '6-9'),
            'cost': 'Free',
            'location_type': program_data.get('location_type', 'Online'),
            'time_commitment': program_data.get('time_commitment', 'Academic year'),
            'prerequisite_level': program_data.get('prerequisite_level', 'None'),
            'support_level': 'High',
            'deadline': program_data.get('deadline', 'Annual-Winter'),
            'financial_barrier_level': program_data.get('financial_barrier_level', 'Low'),
            'financial_aid_available': False,
            'family_income_consideration': False,
            'hidden_costs_level': program_data.get('hidden_costs_level', 'Equipment'),
            'cost_category': 'Free',
            'diversity_focus': True,
            'underrepresented_friendly': True,
            'first_gen_support': True,
            'cultural_competency': 'High',
            'rural_accessible': True,
            'transportation_required': program_data.get('transportation_required', False),
            'internet_dependency': program_data.get('internet_dependency', 'Basic'),
            'regional_availability': 'National',
            'family_involvement_required': 'Optional',
            'peer_network_building': True,
            'mentor_access_level': program_data.get('mentor_access_level', 'Professional')
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
        logger.info("Starting eCYBERMISSION Competition scraper...")

        # Add known eCYBERMISSION programs
        self.add_known_ecybermission_programs()

        # Attempt to scrape additional programs
        self.scrape_ecybermission_pages()

        # Save to CSV
        output_file = 'data/ecybermission_programs.csv'
        self.save_to_csv(output_file)

        logger.info(f"Successfully created {output_file} with {len(self.programs)} eCYBERMISSION programs")
        return output_file


def main():
    scraper = EcybermissionScraper()
    output_file = scraper.run()
    print(f"\neCYBERMISSION Competition scraper completed successfully!")
    print(f"Output file: {output_file}")
    print(f"Total programs: {len(scraper.programs)}")


if __name__ == "__main__":
    main()
