#!/usr/bin/env python3
"""
NIH Student Programs Scraper
Extracts high school and undergraduate research opportunities from NIH training pages
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

class NIHStudentScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })

        self.base_urls = [
            'https://www.training.nih.gov/programs/hs',
            'https://www.training.nih.gov/programs/sip',
            'https://www.nih.gov/research-training/training-opportunities',
            'https://irp.nih.gov/our-research/training-opportunities'
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

    def parse_duration(self, text):
        """Extract duration from text"""
        if not text:
            return "Unknown"

        text_lower = text.lower()
        if any(term in text_lower for term in ['summer', '8 week', '10 week', '12 week']):
            return "8-12 weeks"
        elif any(term in text_lower for term in ['semester', '4 month', '6 month']):
            return "4-6 months"
        elif 'year' in text_lower:
            return "1 year"
        else:
            return "Varies"

    def parse_grade_level(self, text, url):
        """Determine target grade level from text and URL"""
        if not text:
            text = ""

        text_lower = text.lower()
        url_lower = url.lower()

        if any(term in text_lower + url_lower for term in ['high school', '/hs', 'grades 9', 'grades 10', 'grades 11', 'grades 12']):
            return "11-12"
        elif any(term in text_lower for term in ['undergraduate', 'college', 'university', 'bachelor']):
            return "College"
        elif 'graduate' in text_lower:
            return "Graduate"
        else:
            return "11-12"  # Default for NIH student programs

    def parse_deadline(self, text):
        """Extract deadline information"""
        if not text:
            return "Check website"

        text_lower = text.lower()
        if any(month in text_lower for month in ['january', 'february', 'march', 'april']):
            return "Spring application"
        elif any(month in text_lower for month in ['may', 'june', 'july', 'august']):
            return "Summer application"
        elif any(month in text_lower for month in ['september', 'october', 'november', 'december']):
            return "Fall application"
        else:
            return "Check website"

    def scrape_nih_training_programs(self, url):
        """Scrape programs from NIH training pages"""
        soup = self.fetch_page(url)
        if not soup:
            return

        programs_found = 0

        # Look for program containers - multiple selectors for different page structures
        program_selectors = [
            'div.program-item', 'div.training-program', 'div.opportunity',
            '.view-content .views-row', 'article', 'div.field-content',
            'div[class*="program"]', 'div[class*="training"]'
        ]

        program_elements = []
        for selector in program_selectors:
            elements = soup.select(selector)
            if elements:
                program_elements.extend(elements)
                break

        # If no specific program containers found, look for general content sections
        if not program_elements:
            program_elements = soup.select('div.content, div.main-content, main')

        # Try to extract individual programs
        for element in program_elements[:10]:  # Limit to avoid duplicates
            try:
                # Extract program name
                name_elem = element.select_one('h1, h2, h3, h4, .title, .program-title, .field-name-title')
                if not name_elem:
                    # Try to find any heading in the element
                    name_elem = element.find(['h1', 'h2', 'h3', 'h4'])

                if not name_elem:
                    continue

                name = self.extract_text_safely(name_elem)
                if not name or len(name) < 3:
                    continue

                # Skip if this looks like a navigation or header element
                if any(skip_term in name.lower() for skip_term in ['menu', 'navigation', 'home', 'about', 'contact']):
                    continue

                # Extract description
                desc_selectors = ['.description', '.summary', '.field-name-body', '.content', 'p']
                description = ""
                for desc_sel in desc_selectors:
                    desc_elem = element.select_one(desc_sel)
                    if desc_elem:
                        description = self.extract_text_safely(desc_elem)
                        if description and len(description) > 50:
                            break

                if not description:
                    # Try to get any paragraph text
                    paragraphs = element.find_all('p')
                    if paragraphs:
                        description = self.extract_text_safely(paragraphs[0])

                # Create program entry
                program = {
                    'name': name,
                    'description': description[:500] if description else "NIH research training program for students",
                    'url': url,
                    'source': 'National Institute of Health',
                    'category': 'Research Program',
                    'stem_fields': 'Biology, Medicine, Biomedical Research, Neuroscience',
                    'target_grade': self.parse_grade_level(name + " " + description, url),
                    'cost': 'Free',
                    'location_type': 'In-person',
                    'time_commitment': self.parse_duration(description),
                    'prerequisite_level': 'Medium',
                    'support_level': 'High',
                    'deadline': self.parse_deadline(description),
                    'financial_barrier_level': 'None',
                    'financial_aid_available': True,
                    'family_income_consideration': False,
                    'hidden_costs_level': 'Low',
                    'cost_category': 'Free',
                    'diversity_focus': True,
                    'underrepresented_friendly': True,
                    'first_gen_support': True,
                    'cultural_competency': 'High',
                    'rural_accessible': False,
                    'transportation_required': True,
                    'internet_dependency': 'Basic',
                    'regional_availability': 'Select-regions',
                    'family_involvement_required': 'None',
                    'peer_network_building': True,
                    'mentor_access_level': 'Professional'
                }

                # Avoid duplicates
                if not any(p['name'] == program['name'] for p in self.programs):
                    self.programs.append(program)
                    programs_found += 1
                    logger.info(f"Added program: {name}")

            except Exception as e:
                logger.error(f"Error processing program element: {e}")
                continue

        logger.info(f"Found {programs_found} programs from {url}")

    def add_known_nih_programs(self):
        """Add well-known NIH student programs with detailed information"""
        known_programs = [
            {
                'name': 'NIH Summer Internship Program (SIP)',
                'description': 'Competitive 8-10 week summer research internship for high school and college students to conduct biomedical research alongside NIH scientists. Students work in laboratories across all NIH institutes and centers.',
                'url': 'https://www.training.nih.gov/programs/sip',
                'target_grade': '11-12',
                'time_commitment': '8-10 weeks',
                'deadline': 'March application',
                'prerequisite_level': 'High'
            },
            {
                'name': 'NIH High School Scientific Training Program',
                'description': 'Intensive research training program for academically talented high school students. Participants conduct independent research projects under mentorship of NIH scientists.',
                'url': 'https://www.training.nih.gov/programs/hs',
                'target_grade': '11-12',
                'time_commitment': '8 weeks',
                'deadline': 'February application',
                'prerequisite_level': 'High'
            },
            {
                'name': 'NIH Undergraduate Scholarship Program',
                'description': 'Scholarship program for undergraduate students from disadvantaged backgrounds committed to careers in biomedical research. Includes summer research at NIH.',
                'url': 'https://www.training.nih.gov/programs/ugsp',
                'target_grade': 'College',
                'time_commitment': '10 weeks',
                'deadline': 'February application',
                'prerequisite_level': 'Medium'
            },
            {
                'name': 'National Institute of Mental Health Research Training',
                'description': 'Research training opportunities in mental health and neuroscience for high school and undergraduate students. Focus on brain research and behavioral sciences.',
                'url': 'https://www.nimh.nih.gov/funding/training',
                'target_grade': '11-12',
                'time_commitment': '8-12 weeks',
                'deadline': 'Spring application',
                'stem_fields': 'Neuroscience, Psychology, Mental Health Research'
            },
            {
                'name': 'National Cancer Institute Student Training Program',
                'description': 'Summer research program focusing on cancer research and oncology. Students work with leading cancer researchers on cutting-edge projects.',
                'url': 'https://www.cancer.gov/grants-training/training',
                'target_grade': 'College',
                'time_commitment': '10 weeks',
                'deadline': 'February application',
                'stem_fields': 'Oncology, Cancer Research, Biology'
            },
            {
                'name': 'National Human Genome Research Institute Training',
                'description': 'Genomics and bioinformatics research training for students interested in human genetics and computational biology.',
                'url': 'https://www.genome.gov/careers-training',
                'target_grade': '11-12',
                'time_commitment': '8-10 weeks',
                'deadline': 'March application',
                'stem_fields': 'Genetics, Bioinformatics, Computational Biology'
            }
        ]

        for program_data in known_programs:
            program = {
                'name': program_data['name'],
                'description': program_data['description'],
                'url': program_data['url'],
                'source': 'National Institute of Health',
                'category': 'Research Program',
                'stem_fields': program_data.get('stem_fields', 'Biology, Medicine, Biomedical Research, Neuroscience'),
                'target_grade': program_data.get('target_grade', '11-12'),
                'cost': 'Free',
                'location_type': 'In-person',
                'time_commitment': program_data.get('time_commitment', '8-10 weeks'),
                'prerequisite_level': program_data.get('prerequisite_level', 'Medium'),
                'support_level': 'High',
                'deadline': program_data.get('deadline', 'Check website'),
                'financial_barrier_level': 'None',
                'financial_aid_available': True,
                'family_income_consideration': False,
                'hidden_costs_level': 'Low',
                'cost_category': 'Free',
                'diversity_focus': True,
                'underrepresented_friendly': True,
                'first_gen_support': True,
                'cultural_competency': 'High',
                'rural_accessible': False,
                'transportation_required': True,
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

        csv_file = os.path.join(data_dir, 'nih_student_programs.csv')

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
        logger.info("Starting NIH Student Programs scraper...")

        # First, add known NIH programs with detailed information
        self.add_known_nih_programs()

        # Then scrape additional programs from web pages
        for url in self.base_urls:
            try:
                self.scrape_nih_training_programs(url)
                time.sleep(2)  # Respectful delay between pages
            except Exception as e:
                logger.error(f"Error scraping {url}: {e}")
                continue

        # Save to CSV
        if self.programs:
            csv_file = self.save_to_csv()
            if csv_file:
                logger.info(f"Successfully created {csv_file} with {len(self.programs)} NIH student programs")
                return csv_file
            else:
                logger.error("Failed to save CSV file")
                return None
        else:
            logger.warning("No programs found to save")
            return None

def main():
    scraper = NIHStudentScraper()
    result = scraper.run()

    if result:
        print(f"\nNIH Student Programs scraper completed successfully!")
        print(f"Output file: {result}")
        print(f"Total programs: {len(scraper.programs)}")
    else:
        print("\nScraper failed to complete")

if __name__ == "__main__":
    main()