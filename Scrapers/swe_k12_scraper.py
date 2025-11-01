#!/usr/bin/env python3
"""
Society of Women Engineers (SWE) K-12 Programs Scraper
Extracts K-12 engineering programs for girls and women from SWE
"""

import requests
from bs4 import BeautifulSoup
import csv
import time
import re
import os
from urllib.parse import urljoin, urlparse
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SWEK12Scraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })

        self.base_urls = [
            'https://swe.org/k-12-outreach/',
            'https://swe.org/scholarships/'
        ]

        self.programs = []

        # CSV column headers (29 columns as specified)
        self.csv_headers = [
            'name', 'description', 'url', 'source', 'category', 'stem_fields', 'target_grade',
            'cost', 'location_type', 'time_commitment', 'prerequisite_level', 'support_level',
            'deadline', 'financial_barrier_level', 'financial_aid_available', 'family_income_consideration',
            'hidden_costs_level', 'cost_category', 'diversity_focus', 'underrepresented_friendly',
            'first_gen_support', 'cultural_competency', 'rural_accessible', 'transportation_required',
            'internet_dependency', 'regional_availability', 'family_involvement_required',
            'peer_network_building', 'mentor_access_level'
        ]

    def fetch_page(self, url):
        """Fetch webpage content with error handling"""
        try:
            logger.info(f"Fetching: {url}")
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            time.sleep(2)  # Respectful delay
            return BeautifulSoup(response.content, 'html.parser')
        except Exception as e:
            logger.error(f"Error fetching {url}: {e}")
            return None

    def extract_text_safely(self, element, default=""):
        """Safely extract text from BeautifulSoup element"""
        if element:
            text = element.get_text(strip=True)
            return re.sub(r'\s+', ' ', text) if text else default
        return default

    def parse_target_grade(self, program_name, description):
        """Determine target grade level from program details"""
        combined_text = (program_name + " " + description).lower()

        if any(term in combined_text for term in ['ages 5-18', '5-18', 'k-12']):
            return "K-12"
        elif any(term in combined_text for term in ['high school', 'grades 9-12', '9-12', 'senior']):
            return "9-12"
        elif any(term in combined_text for term in ['middle school', 'grades 6-8', '6-8']):
            return "6-8"
        elif any(term in combined_text for term in ['elementary', 'k-5', 'k-6']):
            return "K-6"
        else:
            return "K-12"  # Default for SWE programs

    def parse_category(self, program_name, description):
        """Determine program category"""
        combined_text = (program_name + " " + description).lower()

        if any(term in combined_text for term in ['scholarship', 'award', 'grant']):
            return "Scholarship"
        elif any(term in combined_text for term in ['club', 'chapter']):
            return "Student Organization"
        elif any(term in combined_text for term in ['leadership', 'academy', 'shla']):
            return "Leadership Program"
        elif any(term in combined_text for term in ['connect', 'mentor', 'network']):
            return "Mentorship Program"
        elif any(term in combined_text for term in ['comic', 'resource', 'library']):
            return "Educational Resource"
        else:
            return "Engineering Program"

    def parse_location_type(self, program_name, description):
        """Determine location type from program details"""
        combined_text = (program_name + " " + description).lower()

        if any(term in combined_text for term in ['virtual', 'online', 'digital', 'downloadable']):
            return "Online"
        elif any(term in combined_text for term in ['local', 'community', 'in-person']):
            return "In-person"
        else:
            return "Hybrid"

    def parse_time_commitment(self, program_name, description):
        """Extract time commitment from program description"""
        combined_text = (program_name + " " + description).lower()

        if any(term in combined_text for term in ['year-round', 'ongoing', 'year long']):
            return "Year-round"
        elif any(term in combined_text for term in ['monthly', 'regular']):
            return "Monthly"
        elif any(term in combined_text for term in ['weekly', 'week']):
            return "Weekly"
        elif any(term in combined_text for term in ['academy', 'program']):
            return "Academic year"
        else:
            return "Flexible"

    def parse_cost(self, program_name, description):
        """Determine cost based on program type"""
        combined_text = (program_name + " " + description).lower()

        if any(term in combined_text for term in ['free', 'no cost']):
            return "Free"
        elif any(term in combined_text for term in ['scholarship', 'award']):
            return "Scholarship"
        else:
            return "Free"  # Most SWE K-12 programs are free

    def parse_prerequisite_level(self, program_name, description):
        """Determine prerequisite level based on program details"""
        combined_text = (program_name + " " + description).lower()

        if any(term in combined_text for term in ['leadership', 'advanced', 'application']):
            return "Medium"
        elif any(term in combined_text for term in ['scholarship', 'competitive', 'senior']):
            return "High"
        else:
            return "None"  # Most SWE programs are open

    def parse_first_gen_support(self, program_name, description):
        """Check for first-generation student support"""
        combined_text = (program_name + " " + description).lower()

        if any(term in combined_text for term in ['first generation', 'first-generation', 'underserved', 'accessibility', 'all students']):
            return True
        else:
            return False

    def scrape_swe_pages(self, url):
        """Scrape programs from SWE pages"""
        soup = self.fetch_page(url)
        if not soup:
            return

        programs_found = 0

        # Look for program information
        program_selectors = [
            'div.program-card', 'div.program-info', 'article.program',
            '.content-area', 'main', 'div.main-content', 'section.program',
            'div[class*="program"]', 'div[class*="swe"]'
        ]

        program_elements = []
        for selector in program_selectors:
            elements = soup.select(selector)
            if elements:
                program_elements.extend(elements[:20])
                break

        # If no specific containers found, look for headings
        if not program_elements:
            headings = soup.find_all(['h1', 'h2', 'h3', 'h4'])
            for heading in headings[:25]:
                heading_text = self.extract_text_safely(heading).lower()
                if any(term in heading_text for term in ['swenext', 'swe', 'program', 'scholarship', 'club', 'academy', 'leadership', 'stem', 'engineering']) and len(heading_text) > 5:
                    content_section = heading.parent or heading.find_next_sibling()
                    if content_section:
                        program_elements.append(content_section)

        # Process found elements
        for element in program_elements[:20]:
            try:
                # Extract program name
                name_elem = (element.find(['h1', 'h2', 'h3', 'h4']) or
                           element.select_one('.title, .program-title, .name') or
                           element.find('strong') or element.find('b'))

                if not name_elem:
                    continue

                name = self.extract_text_safely(name_elem)
                if not name or len(name) < 3 or len(name) > 200:
                    continue

                # Skip navigation or irrelevant content
                if any(skip_term in name.lower() for skip_term in ['menu', 'navigation', 'home', 'about', 'contact', 'login', 'search', 'header', 'footer']):
                    continue

                # Skip if it doesn't look like an SWE program
                if not any(term in name.lower() for term in ['swe', 'swenext', 'program', 'scholarship', 'club', 'academy', 'leadership', 'stem', 'engineering', 'award', 'challenge']):
                    continue

                # Extract description
                description = ""
                paragraphs = element.find_all('p')
                if paragraphs:
                    desc_texts = [self.extract_text_safely(p) for p in paragraphs[:4]]
                    description = " ".join([d for d in desc_texts if d and len(d) > 15])

                if not description:
                    description = self.extract_text_safely(element)

                if not description or len(description) < 20:
                    description = f"Society of Women Engineers program: {name}. Engineering education and empowerment for girls and women."

                # Determine program characteristics
                location_type = self.parse_location_type(name, description)

                # Create program entry
                program = {
                    'name': name,
                    'description': (description[:500] if description else
                                  f"SWE program: {name}"),
                    'url': url,
                    'source': 'Society of Women Engineers',
                    'category': self.parse_category(name, description),
                    'stem_fields': 'Engineering, Technology',
                    'target_grade': self.parse_target_grade(name, description),
                    'cost': self.parse_cost(name, description),
                    'location_type': location_type,
                    'time_commitment': self.parse_time_commitment(name, description),
                    'prerequisite_level': self.parse_prerequisite_level(name, description),
                    'support_level': 'High',
                    'deadline': 'Check SWE website',
                    'financial_barrier_level': 'None',
                    'financial_aid_available': True if 'scholarship' in name.lower() else False,
                    'family_income_consideration': False,
                    'hidden_costs_level': 'None',
                    'cost_category': 'Free',
                    'diversity_focus': True,
                    'underrepresented_friendly': True,
                    'first_gen_support': self.parse_first_gen_support(name, description),
                    'cultural_competency': 'High',
                    'rural_accessible': True if location_type in ['Online', 'Hybrid'] else False,
                    'transportation_required': True if location_type == 'In-person' else False,
                    'internet_dependency': 'High-speed-required' if location_type == 'Online' else 'Basic',
                    'regional_availability': 'National',
                    'family_involvement_required': 'Optional',
                    'peer_network_building': True,
                    'mentor_access_level': 'Professional'
                }

                # Avoid duplicates
                if not any(p['name'].lower() == program['name'].lower() for p in self.programs):
                    self.programs.append(program)
                    programs_found += 1
                    logger.info(f"Added program: {name}")

            except Exception as e:
                logger.error(f"Error processing program element: {e}")
                continue

        logger.info(f"Found {programs_found} programs from {url}")

    def add_known_swe_programs(self):
        """Add well-known SWE K-12 programs with detailed information"""
        known_programs = [
            {
                'name': 'SWENext',
                'description': 'Free program for students ages 5-18 to join the SWE engineering and technology community. Inspire creativity and curiosity in STEM. Networking opportunities with peers and professionals. Diverse, welcoming community open to all genders. Connect with role models and gain engineering exposure.',
                'url': 'https://swe.org/k-12-outreach/',
                'target_grade': 'K-12',
                'category': 'Engineering Program',
                'time_commitment': 'Flexible',
                'location_type': 'Hybrid',
                'prerequisite_level': 'None',
                'first_gen_support': True
            },
            {
                'name': 'SWENext Clubs',
                'description': 'Local student clubs connecting communities of students, advocates, and SWE members. School-based or community clubs providing engineering activities, mentorship, and peer support. Led by students with guidance from adult advocates. Build engineering skills and leadership. Access SWE resources and programs.',
                'url': 'https://swe.org/k-12-outreach/',
                'target_grade': 'K-12',
                'category': 'Student Organization',
                'time_commitment': 'Academic year',
                'location_type': 'In-person',
                'prerequisite_level': 'None',
                'first_gen_support': True
            },
            {
                'name': 'SWENext Influencers',
                'description': 'Leadership development program for students to share STEM passion and gain leadership experience. Opportunities to advocate for engineering, inspire peers, and develop public speaking skills. Build confidence and communication abilities. Connect with other student leaders nationwide.',
                'url': 'https://swe.org/k-12-outreach/',
                'target_grade': '6-12',
                'category': 'Leadership Program',
                'time_commitment': 'Flexible',
                'location_type': 'Hybrid',
                'prerequisite_level': 'Medium',
                'first_gen_support': False
            },
            {
                'name': 'SWENext Awards',
                'description': 'Recognition program celebrating students making impact in local STEM communities. Awards for leadership, innovation, community service, and engineering projects. Highlights student achievements and contributions. Encourages continued STEM involvement and leadership.',
                'url': 'https://swe.org/k-12-outreach/',
                'target_grade': 'K-12',
                'category': 'Recognition Program',
                'time_commitment': 'Application',
                'location_type': 'Online',
                'prerequisite_level': 'Medium',
                'first_gen_support': False
            },
            {
                'name': 'SWENext High School Leadership Academy (SHLA)',
                'description': 'Virtual year-round program for high school students building self-confidence and resilience. Leadership development, skill-building workshops, and peer networking. Application opens annually in July, closes in August. Interactive sessions with women engineers. Personal growth and leadership training.',
                'url': 'https://swe.org/k-12-outreach/',
                'target_grade': '9-12',
                'category': 'Leadership Program',
                'time_commitment': 'Year-round',
                'location_type': 'Online',
                'prerequisite_level': 'Medium',
                'first_gen_support': True,
                'deadline': 'Annual-August'
            },
            {
                'name': 'SWENext Connect',
                'description': 'Program connecting students with peers, local SWE members, and industry experts. Mentoring sessions, engagement challenges, and networking opportunities. Build professional connections and gain career insights. Access to women engineers as mentors. Virtual and in-person networking events.',
                'url': 'https://swe.org/k-12-outreach/',
                'target_grade': 'K-12',
                'category': 'Mentorship Program',
                'time_commitment': 'Flexible',
                'location_type': 'Hybrid',
                'prerequisite_level': 'None',
                'first_gen_support': True
            },
            {
                'name': 'STEM Pathways',
                'description': 'Online library exploring engineering disciplines with digital workbook and career profiles. Self-paced learning about various engineering fields. Includes videos, activities, and professional profiles. Helps students explore engineering career options. Free digital resource.',
                'url': 'https://swe.org/k-12-outreach/',
                'target_grade': 'K-12',
                'category': 'Educational Resource',
                'time_commitment': 'Self-paced',
                'location_type': 'Online',
                'prerequisite_level': 'None',
                'first_gen_support': True
            },
            {
                'name': 'Constance and Nano Comics',
                'description': 'Free downloadable educational comics demonstrating engineering problem-solving. Engaging stories featuring diverse characters solving real-world problems with engineering. Available in multiple languages. Makes engineering accessible and fun. Suitable for classroom or individual reading.',
                'url': 'https://swe.org/k-12-outreach/',
                'target_grade': 'K-8',
                'category': 'Educational Resource',
                'time_commitment': 'Self-paced',
                'location_type': 'Online',
                'prerequisite_level': 'None',
                'first_gen_support': True
            },
            {
                'name': 'SWE Emerging First Year Scholars Scholarship',
                'description': 'Scholarship for high school seniors entering first year of undergraduate engineering studies. Part of SWE $1+ million annual scholarship program. Competitive application process through SWE online portal. Supports women pursuing engineering degrees. Application opens annually.',
                'url': 'https://swe.org/scholarships/',
                'target_grade': '12',
                'category': 'Scholarship',
                'time_commitment': 'Application',
                'location_type': 'Online',
                'prerequisite_level': 'High',
                'first_gen_support': True,
                'financial_aid_available': True,
                'cost': 'Scholarship-funded'
            },
            {
                'name': 'SWENext Summer Engineering Programs',
                'description': 'Summer engineering camps and workshops organized by local SWE sections nationwide. Hands-on engineering activities, lab tours, and mentorship. Duration and format vary by location. Connect with women engineers and explore engineering careers. Application through local SWE sections.',
                'url': 'https://swe.org/k-12-outreach/',
                'target_grade': '6-12',
                'category': 'Engineering Program',
                'time_commitment': '1-2 weeks',
                'location_type': 'In-person',
                'prerequisite_level': 'None',
                'first_gen_support': True,
                'cost': 'Varies'
            },
            {
                'name': 'SWE WE Local Outreach Events',
                'description': 'Community outreach events organized by local SWE sections including Girls in Engineering Day, STEM fairs, and school presentations. Introduce students to engineering through hands-on activities. Meet women engineers and learn about careers. Free community events throughout year.',
                'url': 'https://swe.org/k-12-outreach/',
                'target_grade': 'K-12',
                'category': 'Outreach Program',
                'time_commitment': '1 day',
                'location_type': 'In-person',
                'prerequisite_level': 'None',
                'first_gen_support': True
            },
            {
                'name': 'SWENext Engineering Design Challenges',
                'description': 'Engineering design competitions and challenges for students. Team-based problem-solving using engineering design process. Virtual and in-person options. Develop creativity, critical thinking, and teamwork. Gain hands-on engineering experience through authentic challenges.',
                'url': 'https://swe.org/k-12-outreach/',
                'target_grade': '6-12',
                'category': 'Engineering Competition',
                'time_commitment': 'Competition period',
                'location_type': 'Hybrid',
                'prerequisite_level': 'Basic',
                'first_gen_support': False
            },
            {
                'name': 'SWE Career Guidance for Young Women',
                'description': 'Career counseling and guidance program connecting students with women engineers. Learn about engineering career pathways, college preparation, and professional development. Virtual mentoring sessions and career exploration activities. Resume building and interview preparation support.',
                'url': 'https://swe.org/k-12-outreach/',
                'target_grade': '9-12',
                'category': 'Career Development',
                'time_commitment': 'Flexible',
                'location_type': 'Online',
                'prerequisite_level': 'None',
                'first_gen_support': True
            }
        ]

        for program_data in known_programs:
            program = {
                'name': program_data['name'],
                'description': program_data['description'],
                'url': program_data['url'],
                'source': 'Society of Women Engineers',
                'category': program_data.get('category', 'Engineering Program'),
                'stem_fields': 'Engineering, Technology',
                'target_grade': program_data.get('target_grade', 'K-12'),
                'cost': program_data.get('cost', 'Free'),
                'location_type': program_data.get('location_type', 'Hybrid'),
                'time_commitment': program_data.get('time_commitment', 'Flexible'),
                'prerequisite_level': program_data.get('prerequisite_level', 'None'),
                'support_level': 'High',
                'deadline': program_data.get('deadline', 'Check SWE website'),
                'financial_barrier_level': 'None',
                'financial_aid_available': program_data.get('financial_aid_available', False),
                'family_income_consideration': False,
                'hidden_costs_level': 'None',
                'cost_category': 'Free',
                'diversity_focus': True,
                'underrepresented_friendly': True,
                'first_gen_support': program_data.get('first_gen_support', False),
                'cultural_competency': 'High',
                'rural_accessible': True if program_data.get('location_type', 'Hybrid') in ['Online', 'Hybrid'] else False,
                'transportation_required': True if program_data.get('location_type', 'Hybrid') == 'In-person' else False,
                'internet_dependency': 'High-speed-required' if program_data.get('location_type', 'Hybrid') == 'Online' else 'Basic',
                'regional_availability': 'National',
                'family_involvement_required': 'Optional',
                'peer_network_building': True,
                'mentor_access_level': 'Professional'
            }

            # Avoid duplicates
            if not any(p['name'] == program['name'] for p in self.programs):
                self.programs.append(program)
                logger.info(f"Added known program: {program['name']}")

    def save_to_csv(self):
        """Save all programs to a single CSV file"""
        # Create data directory if it doesn't exist
        data_dir = 'data'
        os.makedirs(data_dir, exist_ok=True)

        csv_file = os.path.join(data_dir, 'swe_k12_programs.csv')

        try:
            with open(csv_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=self.csv_headers)
                writer.writeheader()

                for program in self.programs:
                    writer.writerow(program)

            logger.info(f"Saved {len(self.programs)} programs to {csv_file}")
            return csv_file

        except Exception as e:
            logger.error(f"Error saving CSV: {e}")
            return None

    def run(self):
        """Main scraper execution"""
        logger.info("Starting Society of Women Engineers K-12 Programs scraper...")

        # First, add known SWE programs with detailed information
        self.add_known_swe_programs()

        # Then scrape additional programs from web pages
        for url in self.base_urls:
            try:
                self.scrape_swe_pages(url)
                time.sleep(2)  # Respectful delay between pages
            except Exception as e:
                logger.error(f"Error scraping {url}: {e}")
                continue

        # Save to CSV
        if self.programs:
            csv_file = self.save_to_csv()
            if csv_file:
                logger.info(f"Successfully created {csv_file} with {len(self.programs)} SWE K-12 programs")
                return csv_file
            else:
                logger.error("Failed to save CSV file")
                return None
        else:
            logger.warning("No programs found to save")
            return None

def main():
    scraper = SWEK12Scraper()
    result = scraper.run()

    if result:
        print(f"\nSociety of Women Engineers K-12 Programs scraper completed successfully!")
        print(f"Output file: {result}")
        print(f"Total programs: {len(scraper.programs)}")
    else:
        print("\nScraper failed to complete")

if __name__ == "__main__":
    main()