#!/usr/bin/env python3
"""
National Merit Scholarship Corporation STEM Programs Scraper
Extracts STEM-relevant scholarship opportunities from National Merit program pages
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

class NationalMeritScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })

        self.base_urls = [
            'https://www.nationalmerit.org/',
            'https://www.nationalmerit.org/entering_the_competitions.php',
            'https://www.nationalmerit.org/s/1758/interior.aspx?sid=1758&gid=2&pgid=424'
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

    def parse_award_amount(self, text):
        """Extract award amounts from text"""
        if not text:
            return "Varies"

        text_lower = text.lower()
        if '$' in text:
            # Extract dollar amounts
            amounts = re.findall(r'\$[\d,]+', text)
            if amounts:
                return f"Awards: {', '.join(amounts)}"

        if any(term in text_lower for term in ['full tuition', 'full ride', 'college sponsored']):
            return "Full tuition or college-sponsored awards"
        elif 'one-time' in text_lower:
            return "One-time award"
        else:
            return "Varies by sponsor"

    def parse_deadline(self, text, program_name=""):
        """Extract deadline information"""
        if not text:
            text = program_name

        text_lower = text.lower()

        # National Merit specific deadlines
        if 'psat' in text_lower or 'preliminary' in text_lower:
            return "October (PSAT/NMSQT)"
        elif 'finalist' in text_lower:
            return "February (Finalist application)"
        elif 'semifinalist' in text_lower:
            return "September (Semifinalist application)"
        elif any(month in text_lower for month in ['october', 'september', 'november']):
            return "Fall application period"
        else:
            return "Check NMSC website"

    def scrape_national_merit_pages(self, url):
        """Scrape programs from National Merit pages"""
        soup = self.fetch_page(url)
        if not soup:
            return

        programs_found = 0

        # Look for scholarship program information
        program_selectors = [
            'div.program-info', 'div.scholarship-info', 'div.competition-info',
            '.content-area', 'article', 'div.main-content',
            'div[class*="scholarship"]', 'div[class*="program"]', 'div[class*="competition"]'
        ]

        program_elements = []
        for selector in program_selectors:
            elements = soup.select(selector)
            if elements:
                program_elements.extend(elements)
                break

        # If no specific containers found, look for headings and content
        if not program_elements:
            headings = soup.find_all(['h1', 'h2', 'h3', 'h4'])
            for heading in headings:
                # Look for scholarship-related headings
                heading_text = self.extract_text_safely(heading).lower()
                if any(term in heading_text for term in ['scholarship', 'competition', 'award', 'program', 'merit']):
                    # Find the content section after this heading
                    content_section = heading.find_next_sibling()
                    if content_section:
                        program_elements.append(content_section)

        # Process found elements
        for element in program_elements[:8]:  # Limit to avoid duplicates
            try:
                # Extract program name from heading
                name_elem = element.find(['h1', 'h2', 'h3', 'h4']) or element.select_one('.title, .program-title')
                if not name_elem:
                    # Look for strong text that might be a title
                    name_elem = element.find('strong') or element.find('b')

                if not name_elem:
                    continue

                name = self.extract_text_safely(name_elem)
                if not name or len(name) < 5:
                    continue

                # Skip navigation or irrelevant content
                if any(skip_term in name.lower() for skip_term in ['menu', 'navigation', 'home', 'about', 'contact', 'login']):
                    continue

                # Extract description from paragraphs
                description = ""
                paragraphs = element.find_all('p')
                if paragraphs:
                    desc_texts = [self.extract_text_safely(p) for p in paragraphs[:3]]
                    description = " ".join([d for d in desc_texts if d and len(d) > 10])

                if not description:
                    # Try to get text from the element itself
                    description = self.extract_text_safely(element)

                # Create program entry
                program = {
                    'name': name,
                    'description': (description[:500] if description else
                                  f"National Merit scholarship program: {name}"),
                    'url': url,
                    'source': 'National Merit Scholarship Corporation',
                    'category': 'Academic Scholarship',
                    'stem_fields': 'All STEM',
                    'target_grade': '11-12',
                    'cost': 'Free',
                    'location_type': 'Remote',
                    'time_commitment': '1-2 years',
                    'prerequisite_level': 'High',
                    'support_level': 'Low',
                    'deadline': self.parse_deadline(description, name),
                    'financial_barrier_level': 'None',
                    'financial_aid_available': True,
                    'family_income_consideration': False,
                    'hidden_costs_level': 'None',
                    'cost_category': 'Free',
                    'diversity_focus': False,
                    'underrepresented_friendly': True,
                    'first_gen_support': False,
                    'cultural_competency': 'Low',
                    'rural_accessible': True,
                    'transportation_required': False,
                    'internet_dependency': 'Basic',
                    'regional_availability': 'National',
                    'family_involvement_required': 'Optional',
                    'peer_network_building': False,
                    'mentor_access_level': 'None'
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

    def add_known_national_merit_programs(self):
        """Add well-known National Merit scholarship programs with detailed information"""
        known_programs = [
            {
                'name': 'National Merit Scholarship Program',
                'description': 'Premier academic competition for high school students based on PSAT/NMSQT scores. Recognizes students with exceptional academic ability and potential for success in college. Provides scholarships up to $2,500 and corporate/college-sponsored awards.',
                'url': 'https://www.nationalmerit.org/',
                'deadline': 'October (PSAT/NMSQT)',
                'award_info': 'Up to $2,500 plus college-sponsored awards'
            },
            {
                'name': 'National Merit Semifinalist Program',
                'description': 'Top 1% of PSAT/NMSQT test takers nationwide advance to Semifinalist status. Students must complete detailed scholarship application including academic record, extracurricular activities, leadership, and essay.',
                'url': 'https://www.nationalmerit.org/entering_the_competitions.php',
                'deadline': 'September (Semifinalist application)',
                'prerequisite_level': 'Very High'
            },
            {
                'name': 'National Merit Finalist Recognition',
                'description': 'Approximately 15,000 Semifinalists advance to Finalist standing based on academic record, school recommendation, SAT scores confirming PSAT performance, and essay. About 7,500 Finalists receive Merit Scholarship awards.',
                'url': 'https://www.nationalmerit.org/',
                'deadline': 'February (Finalist determination)',
                'award_info': 'Merit Scholarship awards for about half of Finalists'
            },
            {
                'name': 'Corporate-Sponsored Merit Scholarships',
                'description': 'Business and corporate sponsors provide scholarships for children of employees or students in specific geographic regions. Awards may be renewable for four years of undergraduate study.',
                'url': 'https://www.nationalmerit.org/',
                'deadline': 'Varies by sponsor',
                'category': 'Merit Scholarship',
                'award_info': 'Renewable corporate scholarships'
            },
            {
                'name': 'College-Sponsored Merit Scholarships',
                'description': 'Colleges and universities sponsor scholarships for National Merit Finalists who will attend their institution. Awards range from partial tuition to full rides, often including additional benefits.',
                'url': 'https://www.nationalmerit.org/',
                'deadline': 'Spring (college notification)',
                'category': 'Merit Scholarship',
                'award_info': 'Partial to full tuition awards'
            },
            {
                'name': 'National Achievement Scholarship Program',
                'description': 'Academic competition specifically for outstanding Black American high school students. Recognizes academic promise and provides scholarships for college education. Based on PSAT/NMSQT scores and academic achievement.',
                'url': 'https://www.nationalmerit.org/',
                'deadline': 'October (PSAT/NMSQT)',
                'diversity_focus': True,
                'underrepresented_friendly': True,
                'award_info': 'Scholarships for Black American students'
            },
            {
                'name': 'National Hispanic Recognition Program (PSAT/NMSQT)',
                'description': 'Recognition program for outstanding Hispanic/Latino high school students based on PSAT/NMSQT performance. Provides academic recognition that can lead to college recruitment and scholarship opportunities.',
                'url': 'https://www.nationalmerit.org/',
                'deadline': 'October (PSAT/NMSQT)',
                'diversity_focus': True,
                'underrepresented_friendly': True,
                'category': 'Academic Recognition',
                'award_info': 'Recognition and college recruitment opportunities'
            }
        ]

        for program_data in known_programs:
            program = {
                'name': program_data['name'],
                'description': program_data['description'],
                'url': program_data['url'],
                'source': 'National Merit Scholarship Corporation',
                'category': program_data.get('category', 'Academic Scholarship'),
                'stem_fields': 'All STEM',
                'target_grade': '11-12',
                'cost': 'Free',
                'location_type': 'Remote',
                'time_commitment': '1-2 years',
                'prerequisite_level': program_data.get('prerequisite_level', 'High'),
                'support_level': 'Low',
                'deadline': program_data.get('deadline', 'Check NMSC website'),
                'financial_barrier_level': 'None',
                'financial_aid_available': True,
                'family_income_consideration': False,
                'hidden_costs_level': 'None',
                'cost_category': 'Free',
                'diversity_focus': program_data.get('diversity_focus', False),
                'underrepresented_friendly': program_data.get('underrepresented_friendly', True),
                'first_gen_support': False,
                'cultural_competency': 'Low',
                'rural_accessible': True,
                'transportation_required': False,
                'internet_dependency': 'Basic',
                'regional_availability': 'National',
                'family_involvement_required': 'Optional',
                'peer_network_building': False,
                'mentor_access_level': 'None'
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

        csv_file = os.path.join(data_dir, 'national_merit_programs.csv')

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
        logger.info("Starting National Merit Scholarship scraper...")

        # First, add known National Merit programs with detailed information
        self.add_known_national_merit_programs()

        # Then scrape additional programs from web pages
        for url in self.base_urls:
            try:
                self.scrape_national_merit_pages(url)
                time.sleep(2)  # Respectful delay between pages
            except Exception as e:
                logger.error(f"Error scraping {url}: {e}")
                continue

        # Save to CSV
        if self.programs:
            csv_file = self.save_to_csv()
            if csv_file:
                logger.info(f"Successfully created {csv_file} with {len(self.programs)} National Merit programs")
                return csv_file
            else:
                logger.error("Failed to save CSV file")
                return None
        else:
            logger.warning("No programs found to save")
            return None

def main():
    scraper = NationalMeritScraper()
    result = scraper.run()

    if result:
        print(f"\nNational Merit Scholarship scraper completed successfully!")
        print(f"Output file: {result}")
        print(f"Total programs: {len(scraper.programs)}")
    else:
        print("\nScraper failed to complete")

if __name__ == "__main__":
    main()