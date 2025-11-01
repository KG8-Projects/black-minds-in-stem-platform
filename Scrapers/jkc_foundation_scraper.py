#!/usr/bin/env python3
"""
Jack Kent Cooke Foundation Scholarships Scraper
Extracts K-12 scholarship opportunities from JKC Foundation program pages
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

class JKCFoundationScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })

        self.base_urls = [
            'https://www.jkcf.org/our-scholarships/',
            'https://www.jkcf.org/our-scholarships/college-scholarship/',
            'https://www.jkcf.org/our-scholarships/undergraduate-transfer/',
            'https://www.jkcf.org/our-scholarships/young-scholars/'
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

        if any(term in combined_text for term in ['young scholar', 'middle school', 'grade 7', 'grade 8', '7th', '8th']):
            return "7-8"
        elif any(term in combined_text for term in ['high school', 'grade 9', 'grade 10', 'grade 11', 'grade 12', '9th', '10th', '11th', '12th']):
            return "9-12"
        elif any(term in combined_text for term in ['college', 'undergraduate', 'transfer', 'sophomore', 'junior']):
            return "College"
        elif any(term in combined_text for term in ['graduate', 'grad school']):
            return "Graduate"
        else:
            return "9-12"  # Default for JKC programs

    def parse_award_amount(self, text):
        """Extract award amounts from text"""
        if not text:
            return "Up to full tuition"

        text_lower = text.lower()
        if '$' in text:
            # Extract dollar amounts
            amounts = re.findall(r'\$[\d,]+', text)
            if amounts:
                return f"Awards: {', '.join(amounts)}"

        if any(term in text_lower for term in ['full tuition', 'full cost', 'comprehensive']):
            return "Up to full tuition and expenses"
        elif 'transfer' in text_lower:
            return "Up to $40,000 per year"
        elif 'college' in text_lower:
            return "Up to $40,000 per year"
        elif 'young scholar' in text_lower:
            return "Educational support and enrichment"
        else:
            return "Substantial scholarship support"

    def parse_deadline(self, text, program_name=""):
        """Extract deadline information"""
        combined_text = (text + " " + program_name).lower()

        if any(term in combined_text for term in ['november', 'december']):
            return "Fall application period"
        elif any(term in combined_text for term in ['january', 'february', 'march']):
            return "Winter/Spring application"
        elif any(term in combined_text for term in ['april', 'may', 'june']):
            return "Spring application period"
        else:
            return "Check JKC Foundation website"

    def parse_prerequisite_level(self, text, program_name):
        """Determine prerequisite level based on program requirements"""
        combined_text = (text + " " + program_name).lower()

        if any(term in combined_text for term in ['exceptional', 'outstanding', 'top 5%', 'highest academic', 'superior']):
            return "Very High"
        elif any(term in combined_text for term in ['high academic', 'excellent', 'strong academic', 'academic excellence']):
            return "High"
        elif any(term in combined_text for term in ['good academic', 'solid academic']):
            return "Medium"
        else:
            return "High"  # Default for competitive JKC programs

    def scrape_jkc_pages(self, url):
        """Scrape programs from JKC Foundation pages"""
        soup = self.fetch_page(url)
        if not soup:
            return

        programs_found = 0

        # Look for scholarship program information
        program_selectors = [
            'div.scholarship-info', 'div.program-details', 'article.scholarship',
            '.content-area', 'main', 'div.main-content',
            'div[class*="scholarship"]', 'div[class*="program"]', 'section'
        ]

        program_elements = []
        for selector in program_selectors:
            elements = soup.select(selector)
            if elements:
                program_elements.extend(elements[:3])  # Limit per selector
                break

        # If no specific containers found, look for headings and content
        if not program_elements:
            headings = soup.find_all(['h1', 'h2', 'h3'])
            for heading in headings[:5]:
                heading_text = self.extract_text_safely(heading).lower()
                if any(term in heading_text for term in ['scholarship', 'program', 'scholar', 'award']):
                    # Find the content section after this heading
                    content_section = heading.parent or heading.find_next_sibling()
                    if content_section:
                        program_elements.append(content_section)

        # Process found elements
        for element in program_elements[:5]:  # Limit to avoid duplicates
            try:
                # Extract program name from heading
                name_elem = element.find(['h1', 'h2', 'h3', 'h4']) or element.select_one('.title, .program-title, .scholarship-title')
                if not name_elem:
                    # Look for strong text that might be a title
                    name_elem = element.find('strong') or element.find('b')

                if not name_elem:
                    continue

                name = self.extract_text_safely(name_elem)
                if not name or len(name) < 5:
                    continue

                # Skip navigation or irrelevant content
                if any(skip_term in name.lower() for skip_term in ['menu', 'navigation', 'home', 'about', 'contact', 'login', 'search']):
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
                                  f"Jack Kent Cooke Foundation scholarship program: {name}"),
                    'url': url,
                    'source': 'Jack Kent Cooke Foundation',
                    'category': 'Need-Based Scholarship',
                    'stem_fields': 'All STEM',
                    'target_grade': self.parse_grade_level(description, url, name),
                    'cost': 'Free',
                    'location_type': 'Remote',
                    'time_commitment': 'Multi-year',
                    'prerequisite_level': self.parse_prerequisite_level(description, name),
                    'support_level': 'High',
                    'deadline': self.parse_deadline(description, name),
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
                    'transportation_required': False,
                    'internet_dependency': 'Basic',
                    'regional_availability': 'National',
                    'family_involvement_required': 'Required',
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

    def add_known_jkc_programs(self):
        """Add well-known JKC Foundation scholarship programs with detailed information"""
        known_programs = [
            {
                'name': 'Jack Kent Cooke Young Scholars Program',
                'description': 'Comprehensive five-year pre-college scholarship for exceptional middle school students with financial need. Provides academic advising, summer programs, internships, and up to $40,000 per year for high school. Serves students in 7th or 8th grade.',
                'url': 'https://www.jkcf.org/our-scholarships/young-scholars/',
                'target_grade': '7-8',
                'time_commitment': '5 years',
                'prerequisite_level': 'Very High',
                'deadline': 'April application',
                'award_info': 'Up to $40,000 per year'
            },
            {
                'name': 'Jack Kent Cooke College Scholarship',
                'description': 'Highly selective scholarship for high-achieving high school seniors with financial need. Covers up to $40,000 per year for undergraduate study at accredited four-year institutions. Includes comprehensive academic and personal support.',
                'url': 'https://www.jkcf.org/our-scholarships/college-scholarship/',
                'target_grade': '12',
                'time_commitment': '4 years',
                'prerequisite_level': 'Very High',
                'deadline': 'November application',
                'award_info': 'Up to $40,000 per year'
            },
            {
                'name': 'Jack Kent Cooke Undergraduate Transfer Scholarship',
                'description': 'Prestigious scholarship for community college students transferring to four-year institutions. Supports high-achieving students with significant financial need. Provides up to $40,000 per year and comprehensive academic support services.',
                'url': 'https://www.jkcf.org/our-scholarships/undergraduate-transfer/',
                'target_grade': 'College',
                'time_commitment': '2-3 years',
                'prerequisite_level': 'Very High',
                'deadline': 'December application',
                'award_info': 'Up to $40,000 per year'
            },
            {
                'name': 'Jack Kent Cooke Graduate Arts Award',
                'description': 'Support for graduate students pursuing MFA degrees in creative writing, theater, or visual arts. Recognizes exceptional artistic talent and financial need. Provides funding for graduate study at accredited institutions.',
                'url': 'https://www.jkcf.org/our-scholarships/',
                'target_grade': 'Graduate',
                'time_commitment': '2-3 years',
                'prerequisite_level': 'Very High',
                'deadline': 'January application',
                'category': 'Academic Scholarship',
                'stem_fields': 'Arts (limited STEM relevance)',
                'award_info': 'Graduate study funding'
            }
        ]

        for program_data in known_programs:
            program = {
                'name': program_data['name'],
                'description': program_data['description'],
                'url': program_data['url'],
                'source': 'Jack Kent Cooke Foundation',
                'category': program_data.get('category', 'Need-Based Scholarship'),
                'stem_fields': program_data.get('stem_fields', 'All STEM'),
                'target_grade': program_data.get('target_grade', '9-12'),
                'cost': 'Free',
                'location_type': 'Remote',
                'time_commitment': program_data.get('time_commitment', 'Multi-year'),
                'prerequisite_level': program_data.get('prerequisite_level', 'High'),
                'support_level': 'High',
                'deadline': program_data.get('deadline', 'Check JKC Foundation website'),
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
                'transportation_required': False,
                'internet_dependency': 'Basic',
                'regional_availability': 'National',
                'family_involvement_required': 'Required',
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

        csv_file = os.path.join(data_dir, 'jkc_foundation_programs.csv')

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
        logger.info("Starting Jack Kent Cooke Foundation scraper...")

        # First, add known JKC programs with detailed information
        self.add_known_jkc_programs()

        # Then scrape additional programs from web pages
        for url in self.base_urls:
            try:
                self.scrape_jkc_pages(url)
                time.sleep(2)  # Respectful delay between pages
            except Exception as e:
                logger.error(f"Error scraping {url}: {e}")
                continue

        # Save to CSV
        if self.programs:
            csv_file = self.save_to_csv()
            if csv_file:
                logger.info(f"Successfully created {csv_file} with {len(self.programs)} JKC Foundation programs")
                return csv_file
            else:
                logger.error("Failed to save CSV file")
                return None
        else:
            logger.warning("No programs found to save")
            return None

def main():
    scraper = JKCFoundationScraper()
    result = scraper.run()

    if result:
        print(f"\nJack Kent Cooke Foundation scraper completed successfully!")
        print(f"Output file: {result}")
        print(f"Total programs: {len(scraper.programs)}")
    else:
        print("\nScraper failed to complete")

if __name__ == "__main__":
    main()