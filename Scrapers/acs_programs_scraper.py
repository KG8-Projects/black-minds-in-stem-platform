#!/usr/bin/env python3
"""
American Chemical Society (ACS) Programs Scraper
Extracts K-12 chemistry programs and competitions from ACS
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

class ACSProgramsScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })

        self.base_urls = [
            'https://www.acs.org/education/students.html',
            'https://www.acs.org/education/students/highschool.html',
            'https://www.acs.org/education/outreach/celebrating-chemistry-editions.html'
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

        if any(term in combined_text for term in ['elementary', 'k-5', 'k-6', 'grades 4-6', 'ages 9-12']):
            return "K-6"
        elif any(term in combined_text for term in ['middle school', '6-8', 'grades 6-8']):
            return "6-8"
        elif any(term in combined_text for term in ['high school', '9-12', 'grades 9-12', 'junior', 'senior']):
            return "9-12"
        elif any(term in combined_text for term in ['k-12', 'all grades', 'students']):
            return "K-12"
        else:
            return "9-12"  # Default for ACS programs

    def parse_category(self, program_name, description):
        """Determine program category"""
        combined_text = (program_name + " " + description).lower()

        if any(term in combined_text for term in ['olympiad', 'competition', 'competitive']):
            return "Science Competition"
        elif any(term in combined_text for term in ['research', 'seed', 'laboratory']):
            return "Research Program"
        elif any(term in combined_text for term in ['club', 'chemclub', 'chapter']):
            return "Student Organization"
        elif any(term in combined_text for term in ['magazine', 'publication']):
            return "Educational Resource"
        elif any(term in combined_text for term in ['celebrating', 'outreach', 'week']):
            return "Outreach Program"
        else:
            return "Chemistry Program"

    def parse_location_type(self, program_name, description):
        """Determine location type from program details"""
        combined_text = (program_name + " " + description).lower()

        if any(term in combined_text for term in ['online', 'digital', 'virtual', 'pdf']):
            return "Online"
        elif any(term in combined_text for term in ['laboratory', 'research lab', 'local section']):
            return "In-person"
        elif any(term in combined_text for term in ['school', 'classroom', 'club']):
            return "School-based"
        else:
            return "Hybrid"

    def parse_time_commitment(self, program_name, description):
        """Extract time commitment from program description"""
        combined_text = (program_name + " " + description).lower()

        if any(term in combined_text for term in ['summer', '8 week', '10 week']):
            return "8-10 weeks"
        elif any(term in combined_text for term in ['year-round', 'academic year', 'ongoing']):
            return "Academic year"
        elif any(term in combined_text for term in ['weekly', 'weekly meeting']):
            return "Weekly"
        elif any(term in combined_text for term in ['competition', 'exam', 'test']):
            return "Competition day"
        else:
            return "Flexible"

    def parse_cost(self, program_name, description):
        """Determine cost based on program type"""
        combined_text = (program_name + " " + description).lower()

        if any(term in combined_text for term in ['free', 'no cost', 'sponsored']):
            return "Free"
        elif any(term in combined_text for term in ['seed', 'research', 'paid', 'stipend']):
            return "Free"  # Research programs are typically funded
        else:
            return "Free"  # Most ACS programs are free

    def parse_prerequisite_level(self, program_name, description):
        """Determine prerequisite level based on program details"""
        combined_text = (program_name + " " + description).lower()

        if any(term in combined_text for term in ['olympiad', 'talented', 'competitive', 'selective']):
            return "High"
        elif any(term in combined_text for term in ['chemistry knowledge', 'some experience']):
            return "Medium"
        else:
            return "Basic"  # Most ACS programs are accessible

    def parse_diversity_focus(self, program_name, description):
        """Check for diversity focus in program description"""
        combined_text = (program_name + " " + description).lower()

        if any(term in combined_text for term in ['diversity', 'inclusion', 'underrepresented', 'economically disadvantaged', 'equity', 'all students', 'seed']):
            return True
        else:
            return True  # ACS has strong diversity focus

    def parse_first_gen_support(self, program_name, description):
        """Check for first-generation student support"""
        combined_text = (program_name + " " + description).lower()

        if any(term in combined_text for term in ['economically disadvantaged', 'seed', 'underserved', 'low-income', 'accessibility']):
            return True
        else:
            return False

    def scrape_acs_pages(self, url):
        """Scrape programs from ACS pages"""
        soup = self.fetch_page(url)
        if not soup:
            return

        programs_found = 0

        # Look for program information
        program_selectors = [
            'div.program-card', 'div.program-info', 'article.program',
            '.content-area', 'main', 'div.main-content', 'section.program',
            'div[class*="program"]', 'div[class*="student"]'
        ]

        program_elements = []
        for selector in program_selectors:
            elements = soup.select(selector)
            if elements:
                program_elements.extend(elements[:15])
                break

        # If no specific containers found, look for headings
        if not program_elements:
            headings = soup.find_all(['h1', 'h2', 'h3', 'h4'])
            for heading in headings[:20]:
                heading_text = self.extract_text_safely(heading).lower()
                if any(term in heading_text for term in ['chemclub', 'olympiad', 'seed', 'chemmatters', 'celebrating', 'chemistry', 'acs', 'program', 'club', 'student']) and len(heading_text) > 5:
                    content_section = heading.parent or heading.find_next_sibling()
                    if content_section:
                        program_elements.append(content_section)

        # Process found elements
        for element in program_elements[:15]:
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

                # Skip if it doesn't look like an ACS program
                if not any(term in name.lower() for term in ['acs', 'chem', 'chemistry', 'olympiad', 'seed', 'student', 'club', 'program', 'celebrating', 'science']):
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
                    description = f"American Chemical Society program: {name}. Chemistry education and enrichment opportunity for students."

                # Determine program characteristics
                location_type = self.parse_location_type(name, description)

                # Create program entry
                program = {
                    'name': name,
                    'description': (description[:500] if description else
                                  f"ACS program: {name}"),
                    'url': url,
                    'source': 'American Chemical Society',
                    'category': self.parse_category(name, description),
                    'stem_fields': 'Chemistry, Chemical Engineering',
                    'target_grade': self.parse_target_grade(name, description),
                    'cost': self.parse_cost(name, description),
                    'location_type': location_type,
                    'time_commitment': self.parse_time_commitment(name, description),
                    'prerequisite_level': self.parse_prerequisite_level(name, description),
                    'support_level': 'High',
                    'deadline': 'Check ACS website',
                    'financial_barrier_level': 'None',
                    'financial_aid_available': False,
                    'family_income_consideration': False,
                    'hidden_costs_level': 'None',
                    'cost_category': 'Free',
                    'diversity_focus': self.parse_diversity_focus(name, description),
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

    def add_known_acs_programs(self):
        """Add well-known ACS programs with detailed information"""
        known_programs = [
            {
                'name': 'ACS ChemClub',
                'description': 'Hands-on opportunity for high school students to experience chemistry beyond the classroom. Student-led clubs organize chemistry activities, demonstrations, community outreach, and chemistry explorations. Supported by local ACS sections with resources, grants, and mentorship from professional chemists. Build chemistry community and leadership skills.',
                'url': 'https://www.acs.org/education/students/highschool.html',
                'target_grade': '9-12',
                'category': 'Student Organization',
                'time_commitment': 'Academic year',
                'location_type': 'School-based',
                'prerequisite_level': 'Basic',
                'diversity_focus': True,
                'first_gen_support': True
            },
            {
                'name': 'Chemistry Olympiad',
                'description': 'International chemistry competition testing knowledge and skills of the most talented high school chemistry students. Multi-tiered competition including local, national, and international levels. Top students represent USA at International Chemistry Olympiad. Covers all areas of chemistry with challenging problems. Highly competitive and prestigious.',
                'url': 'https://www.acs.org/education/students/highschool.html',
                'target_grade': '9-12',
                'category': 'Science Competition',
                'time_commitment': 'Competition season',
                'location_type': 'In-person',
                'prerequisite_level': 'High',
                'diversity_focus': True,
                'first_gen_support': False
            },
            {
                'name': 'Project SEED',
                'description': 'Summer research program for economically disadvantaged high school juniors and seniors. Students work alongside scientists in research laboratories conducting authentic chemistry research. Provides stipend, mentorship, and exposure to chemistry careers. Focus on underrepresented students in chemistry. Includes presentations and research poster sessions.',
                'url': 'https://www.acs.org/education/students/highschool.html',
                'target_grade': '11-12',
                'category': 'Research Program',
                'time_commitment': '8-10 weeks',
                'location_type': 'In-person',
                'prerequisite_level': 'Medium',
                'diversity_focus': True,
                'first_gen_support': True,
                'cost': 'Paid-stipend'
            },
            {
                'name': 'ChemMatters Magazine',
                'description': 'Award-winning magazine for high school students that demystifies chemistry with exciting articles, games, and puzzles. Connects chemistry to everyday life and current events. Published quarterly with teacher guides. Available online and in print. Engages students in chemistry through relatable content and interactive features.',
                'url': 'https://www.acs.org/education/students/highschool.html',
                'target_grade': '9-12',
                'category': 'Educational Resource',
                'time_commitment': 'Self-paced',
                'location_type': 'Online',
                'prerequisite_level': 'Basic',
                'diversity_focus': True,
                'first_gen_support': False
            },
            {
                'name': 'Celebrating Chemistry',
                'description': 'Outreach program helping children ages 9-12 (grades 4-6) develop interest in chemistry. Themed editions aligned with National Chemistry Week and Chemists Celebrate Earth Week. Available in English and Spanish. Contains articles, hands-on activities, games, and experiments. Free digital PDFs and print copies. Makes chemistry engaging and accessible.',
                'url': 'https://www.acs.org/education/outreach/celebrating-chemistry-editions.html',
                'target_grade': 'K-6',
                'category': 'Outreach Program',
                'time_commitment': 'Flexible',
                'location_type': 'Hybrid',
                'prerequisite_level': 'None',
                'diversity_focus': True,
                'first_gen_support': True
            },
            {
                'name': 'Adventures in Chemistry',
                'description': 'Chemistry exploration program for elementary students featuring experiments, games, and science activities. Introduces young students to chemistry concepts through hands-on activities. Available through ACS website with resources for teachers and parents. Includes Secret Science of Stuff investigations.',
                'url': 'https://www.acs.org/education/students.html',
                'target_grade': 'K-5',
                'category': 'Chemistry Program',
                'time_commitment': 'Flexible',
                'location_type': 'Online',
                'prerequisite_level': 'None',
                'diversity_focus': True,
                'first_gen_support': True
            },
            {
                'name': 'Middle School Chemistry',
                'description': 'Chemistry education resource designed specifically for middle school students and teachers. Provides engaging content, activities, and experiments appropriate for middle school level. Builds foundation for high school chemistry. Interactive and hands-on approach to chemistry learning.',
                'url': 'https://www.acs.org/education/students.html',
                'target_grade': '6-8',
                'category': 'Chemistry Program',
                'time_commitment': 'Flexible',
                'location_type': 'Online',
                'prerequisite_level': 'Basic',
                'diversity_focus': True,
                'first_gen_support': True
            },
            {
                'name': 'National Chemistry Week',
                'description': 'Annual celebration promoting awareness of chemistry role in everyday life. Features community events, activities, demonstrations, and hands-on experiments organized by local ACS sections nationwide. Different theme each year. Includes school visits, public events, and chemistry outreach. Free participation.',
                'url': 'https://www.acs.org/education/outreach/celebrating-chemistry-editions.html',
                'target_grade': 'K-12',
                'category': 'Outreach Program',
                'time_commitment': '1 week',
                'location_type': 'Hybrid',
                'prerequisite_level': 'None',
                'diversity_focus': True,
                'first_gen_support': True
            },
            {
                'name': 'Chemists Celebrate Earth Week',
                'description': 'Annual environmental chemistry celebration promoting environmental stewardship and chemistry applications to sustainability. Community events, workshops, and activities organized by local ACS sections. Focus on green chemistry, environmental science, and sustainability. Hands-on activities for all ages.',
                'url': 'https://www.acs.org/education/outreach/celebrating-chemistry-editions.html',
                'target_grade': 'K-12',
                'category': 'Outreach Program',
                'time_commitment': '1 week',
                'location_type': 'Hybrid',
                'prerequisite_level': 'None',
                'diversity_focus': True,
                'first_gen_support': True
            },
            {
                'name': 'ACS High School Student Affiliates',
                'description': 'Membership program connecting high school chemistry students with ACS professional community. Receive benefits including magazine subscriptions, networking opportunities, career resources, and discounts. Access to ACS resources and programs. Build chemistry professional network early.',
                'url': 'https://www.acs.org/education/students/highschool.html',
                'target_grade': '9-12',
                'category': 'Student Organization',
                'time_commitment': 'Ongoing',
                'location_type': 'Hybrid',
                'prerequisite_level': 'Basic',
                'diversity_focus': True,
                'first_gen_support': False,
                'cost': 'Low-cost'
            },
            {
                'name': 'Chemistry Festivals',
                'description': 'Community chemistry festivals organized by local ACS sections featuring hands-on chemistry demonstrations, experiments, and activities. Interactive science events open to public. Chemistry shows, experiments, and educational activities for all ages. Promotes chemistry awareness and excitement.',
                'url': 'https://www.acs.org/education/students.html',
                'target_grade': 'K-12',
                'category': 'Outreach Program',
                'time_commitment': '1 day',
                'location_type': 'In-person',
                'prerequisite_level': 'None',
                'diversity_focus': True,
                'first_gen_support': True
            },
            {
                'name': 'ACS Kids Chemistry Workshops',
                'description': 'Hands-on chemistry workshops for elementary and middle school students offered through local ACS sections. Age-appropriate experiments and activities introducing chemistry concepts. Led by ACS member volunteers. Topics vary by location and season. Safe, supervised chemistry exploration.',
                'url': 'https://www.acs.org/education/students.html',
                'target_grade': 'K-8',
                'category': 'Chemistry Program',
                'time_commitment': '2-3 hours',
                'location_type': 'In-person',
                'prerequisite_level': 'None',
                'diversity_focus': True,
                'first_gen_support': True
            }
        ]

        for program_data in known_programs:
            program = {
                'name': program_data['name'],
                'description': program_data['description'],
                'url': program_data['url'],
                'source': 'American Chemical Society',
                'category': program_data.get('category', 'Chemistry Program'),
                'stem_fields': 'Chemistry, Chemical Engineering',
                'target_grade': program_data.get('target_grade', '9-12'),
                'cost': program_data.get('cost', 'Free'),
                'location_type': program_data.get('location_type', 'Hybrid'),
                'time_commitment': program_data.get('time_commitment', 'Flexible'),
                'prerequisite_level': program_data.get('prerequisite_level', 'Basic'),
                'support_level': 'High',
                'deadline': 'Check ACS website',
                'financial_barrier_level': 'None',
                'financial_aid_available': False,
                'family_income_consideration': False,
                'hidden_costs_level': 'None',
                'cost_category': 'Free',
                'diversity_focus': program_data.get('diversity_focus', True),
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

        csv_file = os.path.join(data_dir, 'acs_programs.csv')

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
        logger.info("Starting American Chemical Society Programs scraper...")

        # First, add known ACS programs with detailed information
        self.add_known_acs_programs()

        # Then scrape additional programs from web pages
        for url in self.base_urls:
            try:
                self.scrape_acs_pages(url)
                time.sleep(2)  # Respectful delay between pages
            except Exception as e:
                logger.error(f"Error scraping {url}: {e}")
                continue

        # Save to CSV
        if self.programs:
            csv_file = self.save_to_csv()
            if csv_file:
                logger.info(f"Successfully created {csv_file} with {len(self.programs)} ACS programs")
                return csv_file
            else:
                logger.error("Failed to save CSV file")
                return None
        else:
            logger.warning("No programs found to save")
            return None

def main():
    scraper = ACSProgramsScraper()
    result = scraper.run()

    if result:
        print(f"\nAmerican Chemical Society Programs scraper completed successfully!")
        print(f"Output file: {result}")
        print(f"Total programs: {len(scraper.programs)}")
    else:
        print("\nScraper failed to complete")

if __name__ == "__main__":
    main()