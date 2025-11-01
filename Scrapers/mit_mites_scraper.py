#!/usr/bin/env python3
"""
MIT MITES Programs Scraper
Extracts diversity and outreach STEM programs from MIT MITES for underrepresented students
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

class MITMITESScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })

        self.base_urls = [
            'https://mites.mit.edu/',
            'https://oeop.mit.edu/programs/'
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

        if any(term in combined_text for term in ['7th', '7-12', '7th-12th', '7th–12th']):
            return "7-12"
        elif any(term in combined_text for term in ['middle school', '6-8', '6th-8th']):
            return "6-8"
        elif any(term in combined_text for term in ['rising senior', 'high school senior', '12th grade']):
            return "11-12"
        elif any(term in combined_text for term in ['high school', '9-12', '9th-12th']):
            return "9-12"
        else:
            return "11-12"  # Default for MITES programs

    def parse_location_type(self, program_name, description):
        """Determine location type from program details"""
        combined_text = (program_name + " " + description).lower()

        if any(term in combined_text for term in ['residential', 'on campus', 'live', 'housing']):
            return "Residential"
        elif any(term in combined_text for term in ['virtual', 'online', 'remote']):
            return "Virtual"
        elif any(term in combined_text for term in ['hybrid', 'blended']):
            return "Hybrid"
        elif any(term in combined_text for term in ['saturday', 'weekend', 'academy']):
            return "In-person"
        else:
            return "Residential"  # Default for MITES Summer

    def parse_time_commitment(self, program_name, description):
        """Extract time commitment from program description"""
        combined_text = (program_name + " " + description).lower()

        if any(term in combined_text for term in ['six week', '6 week', '6-week', 'six-week']):
            return "6 weeks"
        elif any(term in combined_text for term in ['six month', '6 month', '6-month', 'six-month', 'june through december']):
            return "6 months"
        elif any(term in combined_text for term in ['multi-year', 'multiyear', 'multi year']):
            return "Multi-year"
        elif any(term in combined_text for term in ['saturday', 'weekend']):
            return "Weekly sessions"
        else:
            return "6 weeks"  # Default

    def parse_regional_availability(self, program_name, description):
        """Determine regional availability based on program details"""
        combined_text = (program_name + " " + description).lower()

        if any(term in combined_text for term in ['boston', 'cambridge', 'lawrence', 'massachusetts', 'ma public school']):
            return "Massachusetts"
        elif any(term in combined_text for term in ['national', 'nationwide', 'united states', 'any state']):
            return "National"
        else:
            return "National"  # Default for MITES Summer/Semester

    def parse_transportation_required(self, program_name, location_type):
        """Determine if transportation is required"""
        if location_type in ['Virtual', 'Online']:
            return False
        elif location_type == 'Residential':
            return True
        else:
            return True  # Default for in-person programs

    def parse_internet_dependency(self, location_type):
        """Determine internet dependency based on location type"""
        if location_type == 'Virtual':
            return "High-speed-required"
        else:
            return "Basic"  # For application and communication

    def parse_prerequisite_level(self, program_name, description):
        """Determine prerequisite level based on program details"""
        combined_text = (program_name + " " + description).lower()

        if any(term in combined_text for term in ['competitive', 'selective', 'strong academic', 'advanced']):
            return "High"
        elif any(term in combined_text for term in ['motivated', 'interest', 'passion']):
            return "Medium"
        else:
            return "Medium"  # Default for MITES programs

    def scrape_mites_pages(self, url):
        """Scrape programs from MIT MITES pages"""
        soup = self.fetch_page(url)
        if not soup:
            return

        programs_found = 0

        # Look for program information
        program_selectors = [
            'div.program-card', 'div.program-info', 'article.program',
            '.content-area', 'main', 'div.main-content', 'section.program',
            'div[class*="program"]', 'div[class*="mites"]'
        ]

        program_elements = []
        for selector in program_selectors:
            elements = soup.select(selector)
            if elements:
                program_elements.extend(elements[:10])
                break

        # If no specific containers found, look for headings
        if not program_elements:
            headings = soup.find_all(['h1', 'h2', 'h3', 'h4'])
            for heading in headings[:15]:
                heading_text = self.extract_text_safely(heading).lower()
                if any(term in heading_text for term in ['mites', 'program', 'semester', 'summer', 'saturday', 'seed', 'mostec', 'think']) and len(heading_text) > 3:
                    content_section = heading.parent or heading.find_next_sibling()
                    if content_section:
                        program_elements.append(content_section)

        # Process found elements
        for element in program_elements[:10]:
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
                if any(skip_term in name.lower() for skip_term in ['menu', 'navigation', 'home', 'about us', 'contact', 'login', 'search', 'header', 'footer', 'apply now', 'learn more']):
                    continue

                # Skip if it doesn't look like a MITES program
                if not any(term in name.lower() for term in ['mites', 'program', 'semester', 'summer', 'saturday', 'seed', 'mostec', 'think', 'stem', 'academy']):
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
                    description = f"MIT MITES diversity program: {name}. Free STEM program for underrepresented students."

                # Create program entry
                location_type = self.parse_location_type(name, description)

                program = {
                    'name': name,
                    'description': (description[:500] if description else
                                  f"MIT MITES program: {name}"),
                    'url': url,
                    'source': 'MIT MITES',
                    'category': 'Diversity Program',
                    'stem_fields': 'Engineering, Science, Technology, Mathematics',
                    'target_grade': self.parse_target_grade(name, description),
                    'cost': 'Free',
                    'location_type': location_type,
                    'time_commitment': self.parse_time_commitment(name, description),
                    'prerequisite_level': self.parse_prerequisite_level(name, description),
                    'support_level': 'High',
                    'deadline': 'Check MITES website',
                    'financial_barrier_level': 'None',
                    'financial_aid_available': True,
                    'family_income_consideration': 'Low-income-focus',
                    'hidden_costs_level': 'None',
                    'cost_category': 'Free',
                    'diversity_focus': True,
                    'underrepresented_friendly': True,
                    'first_gen_support': True,
                    'cultural_competency': 'High',
                    'rural_accessible': True,
                    'transportation_required': self.parse_transportation_required(name, location_type),
                    'internet_dependency': self.parse_internet_dependency(location_type),
                    'regional_availability': self.parse_regional_availability(name, description),
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

    def add_known_mites_programs(self):
        """Add well-known MIT MITES programs with detailed information"""
        known_programs = [
            {
                'name': 'MITES Summer',
                'description': 'Six-week residential STEM intensive for rising high school seniors from underrepresented backgrounds. Live on MIT campus, take rigorous math and science courses, conduct research projects, and build community. All costs covered including travel, housing, meals, and educational materials. Program bolsters confidence and sense of belonging in STEM fields. Highly selective.',
                'url': 'https://mites.mit.edu/',
                'target_grade': '11-12',
                'time_commitment': '6 weeks',
                'location_type': 'Residential',
                'prerequisite_level': 'High',
                'regional_availability': 'National',
                'transportation_required': True,
                'internet_dependency': 'Basic'
            },
            {
                'name': 'MITES Semester',
                'description': 'Six-month online STEM experience for rising high school seniors from diverse backgrounds. Runs from June through December. Students complete challenging coursework, participate in enrichment activities, and connect with MITES community. Travel scholarships available for in-person events. Creates new pathways for underrepresented students. Free program.',
                'url': 'https://mites.mit.edu/',
                'target_grade': '11-12',
                'time_commitment': '6 months',
                'location_type': 'Virtual',
                'prerequisite_level': 'Medium',
                'regional_availability': 'National',
                'transportation_required': False,
                'internet_dependency': 'High-speed-required'
            },
            {
                'name': 'MITES Saturdays',
                'description': 'Multi-year STEM academy for 7th-12th grade students from Boston, Cambridge, and Lawrence MA public schools. Weekly programming focused on advancing access and equity in STEM. Build skills, confidence, and community over multiple years. Serves students from diverse and underrepresented backgrounds. Free of cost to all participants.',
                'url': 'https://mites.mit.edu/',
                'target_grade': '7-12',
                'time_commitment': 'Multi-year',
                'location_type': 'In-person',
                'prerequisite_level': 'Medium',
                'regional_availability': 'Massachusetts',
                'transportation_required': True,
                'internet_dependency': 'Basic'
            },
            {
                'name': 'MIT THINK Scholars Program',
                'description': 'Project-based program supporting students developing innovative STEM projects addressing real-world problems. Students receive mentorship, project funding, and support to bring their ideas to life. Focus on encouraging creativity, innovation, and social impact. Open to high school students nationwide. Emphasizes diversity and inclusion.',
                'url': 'https://mites.mit.edu/',
                'target_grade': '9-12',
                'time_commitment': '4-6 months',
                'location_type': 'Virtual',
                'prerequisite_level': 'Medium',
                'regional_availability': 'National',
                'transportation_required': False,
                'internet_dependency': 'High-speed-required',
                'category': 'STEM Pipeline Program'
            },
            {
                'name': 'MITES Summer Plus',
                'description': 'Extended MITES experience for alumni providing additional enrichment, mentorship, and academic support. Maintains connection with MITES community after summer program. Includes college preparation, career guidance, and continued STEM skill development. Supports students through high school and college transition.',
                'url': 'https://mites.mit.edu/',
                'target_grade': '12',
                'time_commitment': '1 year',
                'location_type': 'Hybrid',
                'prerequisite_level': 'Medium',
                'regional_availability': 'National',
                'transportation_required': False,
                'internet_dependency': 'Basic',
                'category': 'STEM Pipeline Program'
            },
            {
                'name': 'MITES Shadow Program',
                'description': 'One-day campus visit program for prospective MITES applicants. Experience MIT campus, meet current MITES students and staff, attend information sessions, and explore STEM opportunities. Helps students understand MITES programs and prepare applications. Particularly targets students from underrepresented backgrounds. Free program.',
                'url': 'https://mites.mit.edu/',
                'target_grade': '10-11',
                'time_commitment': '1 day',
                'location_type': 'In-person',
                'prerequisite_level': 'None',
                'regional_availability': 'Regional',
                'transportation_required': True,
                'internet_dependency': 'Basic'
            },
            {
                'name': 'MITES Alumni Network',
                'description': 'Lifelong community network for MITES program alumni. Provides continued mentorship, professional networking, career support, and opportunities to give back. Connects thousands of MITES alumni working in STEM fields. Includes regional meetups, online community, and mentorship programs. Free membership.',
                'url': 'https://mites.mit.edu/',
                'target_grade': 'Alumni',
                'time_commitment': 'Ongoing',
                'location_type': 'Hybrid',
                'prerequisite_level': 'None',
                'regional_availability': 'National',
                'transportation_required': False,
                'internet_dependency': 'Basic',
                'category': 'STEM Pipeline Program'
            },
            {
                'name': 'MITES Application Workshops',
                'description': 'Free workshops helping students prepare strong MITES applications. Cover essay writing, recommendation letters, showcasing STEM interests, and understanding eligibility. Offered virtually and in-person in select cities. Particularly supports first-generation college students and students from underrepresented backgrounds.',
                'url': 'https://mites.mit.edu/',
                'target_grade': '10-11',
                'time_commitment': '2-3 hours',
                'location_type': 'Hybrid',
                'prerequisite_level': 'None',
                'regional_availability': 'National',
                'transportation_required': False,
                'internet_dependency': 'Basic'
            }
        ]

        for program_data in known_programs:
            program = {
                'name': program_data['name'],
                'description': program_data['description'],
                'url': program_data['url'],
                'source': 'MIT MITES',
                'category': program_data.get('category', 'Diversity Program'),
                'stem_fields': 'Engineering, Science, Technology, Mathematics',
                'target_grade': program_data.get('target_grade', '11-12'),
                'cost': 'Free',
                'location_type': program_data.get('location_type', 'Residential'),
                'time_commitment': program_data.get('time_commitment', '6 weeks'),
                'prerequisite_level': program_data.get('prerequisite_level', 'Medium'),
                'support_level': 'High',
                'deadline': 'Check MITES website',
                'financial_barrier_level': 'None',
                'financial_aid_available': True,
                'family_income_consideration': 'Low-income-focus',
                'hidden_costs_level': 'None',
                'cost_category': 'Free',
                'diversity_focus': True,
                'underrepresented_friendly': True,
                'first_gen_support': True,
                'cultural_competency': 'High',
                'rural_accessible': True,
                'transportation_required': program_data.get('transportation_required', True),
                'internet_dependency': program_data.get('internet_dependency', 'Basic'),
                'regional_availability': program_data.get('regional_availability', 'National'),
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

        csv_file = os.path.join(data_dir, 'mit_mites_programs.csv')

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
        logger.info("Starting MIT MITES Programs scraper...")

        # First, add known MITES programs with detailed information
        self.add_known_mites_programs()

        # Then scrape additional programs from web pages
        for url in self.base_urls:
            try:
                self.scrape_mites_pages(url)
                time.sleep(2)  # Respectful delay between pages
            except Exception as e:
                logger.error(f"Error scraping {url}: {e}")
                continue

        # Save to CSV
        if self.programs:
            csv_file = self.save_to_csv()
            if csv_file:
                logger.info(f"Successfully created {csv_file} with {len(self.programs)} MIT MITES programs")
                return csv_file
            else:
                logger.error("Failed to save CSV file")
                return None
        else:
            logger.warning("No programs found to save")
            return None

def main():
    scraper = MITMITESScraper()
    result = scraper.run()

    if result:
        print(f"\nMIT MITES Programs scraper completed successfully!")
        print(f"Output file: {result}")
        print(f"Total programs: {len(scraper.programs)}")
    else:
        print("\nScraper failed to complete")

if __name__ == "__main__":
    main()