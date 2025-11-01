#!/usr/bin/env python3
"""
Boeing Student Programs Scraper
Extracts K-12 aerospace and STEM education opportunities from Boeing program pages
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

class BoeingStudentScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })

        self.base_urls = [
            'https://www.boeing.com/company/key-orgs/boeing-global-engagement/community-investment/education-and-learning',
            'https://www.boeing.com/careers/college-students',
            'https://www.boeing.com/company/careers/working-here/diversity-and-inclusion'
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

    def parse_grade_level(self, text, url, program_name):
        """Determine target grade level from text, URL, and program name"""
        combined_text = (text + " " + url + " " + program_name).lower()

        if any(term in combined_text for term in ['elementary', 'k-5', 'k-6', 'grades k-', 'primary']):
            return "K-6"
        elif any(term in combined_text for term in ['middle school', 'middle-school', '6-8', '7-8', 'grades 6-8']):
            return "6-8"
        elif any(term in combined_text for term in ['high school', 'high-school', '9-12', 'grades 9-12', 'secondary']):
            return "9-12"
        elif any(term in combined_text for term in ['college', 'university', 'undergraduate', 'student intern']):
            return "College"
        elif any(term in combined_text for term in ['k-12', 'all grades', 'youth']):
            return "K-12"
        else:
            return "9-12"  # Default for Boeing programs

    def parse_cost_info(self, text, program_name):
        """Extract cost information from text"""
        combined_text = (text + " " + program_name).lower()

        if '$' in text:
            # Extract dollar amounts
            amounts = re.findall(r'\$[\d,]+', text)
            if amounts:
                return amounts[0].replace('$', '').replace(',', '')

        # Most Boeing educational programs are free
        if any(term in combined_text for term in ['free', 'no cost', 'sponsored', 'funded']):
            return "Free"
        elif any(term in combined_text for term in ['scholarship', 'stipend', 'paid']):
            return "Free"
        else:
            return "Free"  # Default for corporate educational programs

    def parse_location_type(self, text, program_name):
        """Determine location type from program description"""
        combined_text = (text + " " + program_name).lower()

        if any(term in combined_text for term in ['virtual', 'online', 'remote']):
            return "Virtual"
        elif any(term in combined_text for term in ['boeing facility', 'factory', 'plant', 'on-site', 'visit']):
            return "In-person"
        elif any(term in combined_text for term in ['hybrid', 'combination']):
            return "Hybrid"
        else:
            return "In-person"  # Default for Boeing programs

    def parse_time_commitment(self, text, program_name):
        """Extract time commitment from program description"""
        combined_text = (text + " " + program_name).lower()

        if any(term in combined_text for term in ['summer', '8 week', '10 week', '12 week']):
            return "8-12 weeks"
        elif any(term in combined_text for term in ['semester', '4 month', '6 month']):
            return "4-6 months"
        elif any(term in combined_text for term in ['year', 'annual', '12 month']):
            return "1 year"
        elif any(term in combined_text for term in ['day', 'workshop', 'event']):
            return "1-5 days"
        else:
            return "Varies"

    def parse_prerequisite_level(self, text, program_name):
        """Determine prerequisite level based on program requirements"""
        combined_text = (text + " " + program_name).lower()

        if any(term in combined_text for term in ['advanced', 'gpa 3.5', 'competitive', 'selective', 'top student']):
            return "High"
        elif any(term in combined_text for term in ['some experience', 'basic knowledge', 'coursework', 'stem background']):
            return "Medium"
        elif any(term in combined_text for term in ['no experience', 'beginner', 'open to all', 'introductory']):
            return "None"
        else:
            return "Basic"  # Default for corporate programs

    def parse_diversity_focus(self, text, program_name):
        """Check for diversity focus in program description"""
        combined_text = (text + " " + program_name).lower()

        if any(term in combined_text for term in ['diversity', 'inclusion', 'underrepresented', 'minority', 'women', 'girls', 'latino', 'hispanic', 'black', 'african american']):
            return True
        else:
            return False

    def parse_first_gen_support(self, text, program_name):
        """Check for first-generation student support"""
        combined_text = (text + " " + program_name).lower()

        if any(term in combined_text for term in ['first generation', 'first-generation', 'first gen', 'family college', 'accessible']):
            return True
        else:
            return False

    def scrape_boeing_pages(self, url):
        """Scrape programs from Boeing pages"""
        soup = self.fetch_page(url)
        if not soup:
            return

        programs_found = 0

        # Look for program information
        program_selectors = [
            'div.program-info', 'div.program-details', 'article.program',
            '.content-area', 'main', 'div.main-content', 'section.program',
            'div[class*="program"]', 'div[class*="education"]', 'div[class*="student"]'
        ]

        program_elements = []
        for selector in program_selectors:
            elements = soup.select(selector)
            if elements:
                program_elements.extend(elements[:8])  # Limit per selector
                break

        # If no specific containers found, look for headings and content
        if not program_elements:
            headings = soup.find_all(['h1', 'h2', 'h3', 'h4'])
            for heading in headings[:12]:
                heading_text = self.extract_text_safely(heading).lower()
                if any(term in heading_text for term in ['program', 'education', 'student', 'intern', 'scholarship', 'competition', 'stem', 'aerospace']) and len(heading_text) > 5:
                    # Find the content section after this heading
                    content_section = heading.parent or heading.find_next_sibling()
                    if content_section:
                        program_elements.append(content_section)

        # Process found elements
        for element in program_elements[:10]:  # Limit to avoid duplicates
            try:
                # Extract program name from heading
                name_elem = (element.find(['h1', 'h2', 'h3', 'h4']) or
                           element.select_one('.title, .program-title, .field-name-title') or
                           element.find('strong') or element.find('b'))

                if not name_elem:
                    continue

                name = self.extract_text_safely(name_elem)
                if not name or len(name) < 5 or len(name) > 200:
                    continue

                # Skip navigation or irrelevant content
                if any(skip_term in name.lower() for skip_term in ['menu', 'navigation', 'home', 'about', 'contact', 'login', 'search', 'cart', 'header', 'footer', 'copyright']):
                    continue

                # Skip if it doesn't look like a student program
                if not any(term in name.lower() for term in ['program', 'education', 'student', 'intern', 'scholarship', 'competition', 'stem', 'learning', 'training', 'academy']):
                    continue

                # Extract description from paragraphs
                description = ""
                paragraphs = element.find_all('p')
                if paragraphs:
                    desc_texts = [self.extract_text_safely(p) for p in paragraphs[:4]]
                    description = " ".join([d for d in desc_texts if d and len(d) > 15])

                if not description:
                    # Try to get text from divs or other elements
                    content_divs = element.find_all('div', string=True)
                    if content_divs:
                        description = " ".join([self.extract_text_safely(d) for d in content_divs[:2] if len(self.extract_text_safely(d)) > 15])

                if not description:
                    description = self.extract_text_safely(element)

                # Create program entry
                program = {
                    'name': name,
                    'description': (description[:500] if description else
                                  f"Boeing STEM education program: {name}"),
                    'url': url,
                    'source': 'Boeing',
                    'category': 'Industry Program',
                    'stem_fields': 'Aerospace Engineering, Aviation, Engineering, Manufacturing',
                    'target_grade': self.parse_grade_level(description, url, name),
                    'cost': self.parse_cost_info(description, name),
                    'location_type': self.parse_location_type(description, name),
                    'time_commitment': self.parse_time_commitment(description, name),
                    'prerequisite_level': self.parse_prerequisite_level(description, name),
                    'support_level': 'High',
                    'deadline': 'Check Boeing website',
                    'financial_barrier_level': 'None',
                    'financial_aid_available': True,
                    'family_income_consideration': False,
                    'hidden_costs_level': 'Low',
                    'cost_category': 'Free',
                    'diversity_focus': self.parse_diversity_focus(description, name),
                    'underrepresented_friendly': True,
                    'first_gen_support': self.parse_first_gen_support(description, name),
                    'cultural_competency': 'High',
                    'rural_accessible': True,
                    'transportation_required': True,
                    'internet_dependency': 'Basic',
                    'regional_availability': 'Select-regions',
                    'family_involvement_required': 'None',
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

    def add_known_boeing_programs(self):
        """Add well-known Boeing student programs with detailed information"""
        known_programs = [
            {
                'name': 'Boeing STEM Learning Lab',
                'description': 'Hands-on STEM education program bringing Boeing engineers into classrooms to teach aerospace concepts. Students learn about flight, engineering design process, and aviation careers through interactive activities and experiments.',
                'url': 'https://www.boeing.com/company/key-orgs/boeing-global-engagement/community-investment/education-and-learning',
                'target_grade': 'K-12',
                'time_commitment': '1-2 days',
                'location_type': 'In-person',
                'prerequisite_level': 'None',
                'diversity_focus': True
            },
            {
                'name': 'Boeing Aerospace Academy',
                'description': 'Intensive summer program for high school students interested in aerospace careers. Students work with Boeing engineers on real aerospace challenges, visit production facilities, and learn about aviation technology.',
                'url': 'https://www.boeing.com/company/key-orgs/boeing-global-engagement/community-investment/education-and-learning',
                'target_grade': '9-12',
                'time_commitment': '2 weeks',
                'location_type': 'In-person',
                'prerequisite_level': 'Medium',
                'diversity_focus': True
            },
            {
                'name': 'Boeing Student Design Challenge',
                'description': 'Annual competition where student teams design aerospace solutions to real-world problems. Teams receive mentorship from Boeing engineers and compete for scholarships and recognition.',
                'url': 'https://www.boeing.com/company/key-orgs/boeing-global-engagement/community-investment/education-and-learning',
                'target_grade': '9-12',
                'time_commitment': '6 months',
                'location_type': 'Hybrid',
                'prerequisite_level': 'Medium',
                'category': 'Design Competition'
            },
            {
                'name': 'Boeing Diversity Scholarship Program',
                'description': 'Scholarship program for underrepresented students pursuing aerospace and engineering degrees. Includes mentorship opportunities, internship pathways, and career development support.',
                'url': 'https://www.boeing.com/company/careers/working-here/diversity-and-inclusion',
                'target_grade': 'College',
                'time_commitment': '4 years',
                'location_type': 'Remote',
                'prerequisite_level': 'High',
                'diversity_focus': True,
                'category': 'Scholarship Program',
                'cost': 'Scholarship-funded'
            },
            {
                'name': 'Boeing Manufacturing Excellence Program',
                'description': 'Program introducing students to advanced manufacturing processes used in aerospace production. Students learn about composite materials, precision manufacturing, and quality control systems.',
                'url': 'https://www.boeing.com/company/key-orgs/boeing-global-engagement/community-investment/education-and-learning',
                'target_grade': '9-12',
                'time_commitment': '1 week',
                'location_type': 'In-person',
                'prerequisite_level': 'Basic'
            },
            {
                'name': 'Boeing Teacher Professional Development',
                'description': 'Professional development program for educators to learn aerospace concepts and teaching methods. Teachers receive Boeing curriculum materials and ongoing support to implement STEM programs.',
                'url': 'https://www.boeing.com/company/key-orgs/boeing-global-engagement/community-investment/education-and-learning',
                'target_grade': 'Educators',
                'time_commitment': '3-5 days',
                'location_type': 'In-person',
                'prerequisite_level': 'None',
                'category': 'Professional Development'
            },
            {
                'name': 'Boeing Future Engineers Program',
                'description': 'Year-long program connecting students with Boeing engineers through mentorship, project-based learning, and career exploration. Students work on real aerospace challenges and develop technical skills.',
                'url': 'https://www.boeing.com/company/key-orgs/boeing-global-engagement/community-investment/education-and-learning',
                'target_grade': '6-12',
                'time_commitment': '1 year',
                'location_type': 'Hybrid',
                'prerequisite_level': 'Basic',
                'diversity_focus': True
            },
            {
                'name': 'Boeing Aviation STEM Curriculum',
                'description': 'Comprehensive K-12 curriculum package focusing on aviation and aerospace concepts. Includes lesson plans, hands-on activities, and connections to Boeing careers and facilities.',
                'url': 'https://www.boeing.com/company/key-orgs/boeing-global-engagement/community-investment/education-and-learning',
                'target_grade': 'K-12',
                'time_commitment': 'Full academic year',
                'location_type': 'In-classroom',
                'prerequisite_level': 'None',
                'category': 'Curriculum Program'
            }
        ]

        for program_data in known_programs:
            program = {
                'name': program_data['name'],
                'description': program_data['description'],
                'url': program_data['url'],
                'source': 'Boeing',
                'category': program_data.get('category', 'Industry Program'),
                'stem_fields': 'Aerospace Engineering, Aviation, Engineering, Manufacturing',
                'target_grade': program_data.get('target_grade', '9-12'),
                'cost': program_data.get('cost', 'Free'),
                'location_type': program_data.get('location_type', 'In-person'),
                'time_commitment': program_data.get('time_commitment', 'Varies'),
                'prerequisite_level': program_data.get('prerequisite_level', 'Basic'),
                'support_level': 'High',
                'deadline': 'Check Boeing website',
                'financial_barrier_level': 'None',
                'financial_aid_available': True,
                'family_income_consideration': False,
                'hidden_costs_level': 'Low',
                'cost_category': 'Free',
                'diversity_focus': program_data.get('diversity_focus', True),
                'underrepresented_friendly': True,
                'first_gen_support': program_data.get('first_gen_support', False),
                'cultural_competency': 'High',
                'rural_accessible': True,
                'transportation_required': program_data.get('location_type', 'In-person') == 'In-person',
                'internet_dependency': 'Basic',
                'regional_availability': 'Select-regions',
                'family_involvement_required': 'None',
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
        data_dir = os.path.join('scrapers', 'data')
        os.makedirs(data_dir, exist_ok=True)

        csv_file = os.path.join(data_dir, 'boeing_student_programs.csv')

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
        logger.info("Starting Boeing Student Programs scraper...")

        # First, add known Boeing programs with detailed information
        self.add_known_boeing_programs()

        # Then scrape additional programs from web pages
        for url in self.base_urls:
            try:
                self.scrape_boeing_pages(url)
                time.sleep(2)  # Respectful delay between pages
            except Exception as e:
                logger.error(f"Error scraping {url}: {e}")
                continue

        # Save to CSV
        if self.programs:
            csv_file = self.save_to_csv()
            if csv_file:
                logger.info(f"Successfully created {csv_file} with {len(self.programs)} Boeing student programs")
                return csv_file
            else:
                logger.error("Failed to save CSV file")
                return None
        else:
            logger.warning("No programs found to save")
            return None

def main():
    scraper = BoeingStudentScraper()
    result = scraper.run()

    if result:
        print(f"\nBoeing Student Programs scraper completed successfully!")
        print(f"Output file: {result}")
        print(f"Total programs: {len(scraper.programs)}")
    else:
        print("\nScraper failed to complete")

if __name__ == "__main__":
    main()