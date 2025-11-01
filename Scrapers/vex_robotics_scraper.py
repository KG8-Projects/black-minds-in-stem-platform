#!/usr/bin/env python3
"""
VEX Robotics Competition Programs Scraper
Extracts K-12 robotics competition opportunities from VEX Robotics program pages
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

class VEXRoboticsScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })

        self.base_urls = [
            'https://www.vexrobotics.com/competition',
            'https://www.vexrobotics.com/vexiq/competition',
            'https://www.vexrobotics.com/v5/competition/vrc-competition',
            'https://www.vexrobotics.com/competition/teams'
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

        if any(term in combined_text for term in ['elementary', 'k-5', 'ages 8-11', 'ages 6-11']):
            return "K-5"
        elif any(term in combined_text for term in ['vex iq', 'iq', 'middle school', 'ages 8-14', 'grades 4-8']):
            return "4-8"
        elif any(term in combined_text for term in ['vex v5', 'vrc', 'high school', 'ages 11-18', 'grades 6-12']):
            return "6-12"
        elif any(term in combined_text for term in ['university', 'college', 'vexu']):
            return "College"
        else:
            return "6-12"  # Default for VEX programs

    def parse_cost_info(self, text, program_name):
        """Extract cost information from text"""
        combined_text = (text + " " + program_name).lower()

        if '$' in text:
            # Extract dollar amounts
            amounts = re.findall(r'\$[\d,]+', text)
            if amounts:
                return amounts[0].replace('$', '').replace(',', '')

        # VEX IQ typically less expensive than V5
        if 'iq' in combined_text:
            return "300-800"
        elif any(term in combined_text for term in ['v5', 'vrc']):
            return "800-2000"
        else:
            return "500-1500"

    def parse_deadline(self, text, program_name=""):
        """Extract deadline/season information"""
        combined_text = (text + " " + program_name).lower()

        if any(term in combined_text for term in ['august', 'september', 'fall']):
            return "August-September (season start)"
        elif any(term in combined_text for term in ['april', 'may', 'worlds', 'championship']):
            return "April-May (championships)"
        elif 'season' in combined_text:
            return "August-May (competition season)"
        else:
            return "Check VEX website for season dates"

    def parse_financial_aid(self, text, program_name):
        """Check for financial aid or scholarship mentions"""
        combined_text = (text + " " + program_name).lower()

        if any(term in combined_text for term in ['scholarship', 'grant', 'financial aid', 'sponsor', 'funding']):
            return True
        else:
            return False

    def parse_diversity_focus(self, text, program_name):
        """Check for diversity initiative mentions"""
        combined_text = (text + " " + program_name).lower()

        if any(term in combined_text for term in ['diversity', 'inclusion', 'girls', 'underrepresented', 'minority']):
            return True
        else:
            return False

    def scrape_vex_pages(self, url):
        """Scrape programs from VEX Robotics pages"""
        soup = self.fetch_page(url)
        if not soup:
            return

        programs_found = 0

        # Look for competition program information
        program_selectors = [
            'div.competition-info', 'div.program-details', 'article.competition',
            '.content-area', 'main', 'div.main-content', 'section.competition',
            'div[class*="competition"]', 'div[class*="program"]', 'div[class*="division"]'
        ]

        program_elements = []
        for selector in program_selectors:
            elements = soup.select(selector)
            if elements:
                program_elements.extend(elements[:5])  # Limit per selector
                break

        # If no specific containers found, look for headings and content
        if not program_elements:
            headings = soup.find_all(['h1', 'h2', 'h3', 'h4'])
            for heading in headings[:8]:
                heading_text = self.extract_text_safely(heading).lower()
                if any(term in heading_text for term in ['competition', 'vex', 'robotics', 'iq', 'v5', 'vrc', 'division']):
                    # Find the content section after this heading
                    content_section = heading.parent or heading.find_next_sibling()
                    if content_section:
                        program_elements.append(content_section)

        # Process found elements
        for element in program_elements[:12]:  # Limit to avoid duplicates
            try:
                # Extract program name from heading
                name_elem = element.find(['h1', 'h2', 'h3', 'h4']) or element.select_one('.title, .competition-title, .program-title')
                if not name_elem:
                    # Look for strong text that might be a title
                    name_elem = element.find('strong') or element.find('b')

                if not name_elem:
                    continue

                name = self.extract_text_safely(name_elem)
                if not name or len(name) < 5:
                    continue

                # Skip navigation or irrelevant content
                if any(skip_term in name.lower() for skip_term in ['menu', 'navigation', 'home', 'about', 'contact', 'login', 'search', 'cart']):
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
                                  f"VEX Robotics competition program: {name}"),
                    'url': url,
                    'source': 'VEX Robotics',
                    'category': 'Robotics Competition',
                    'stem_fields': 'Engineering, Programming, Design, Mathematics',
                    'target_grade': self.parse_grade_level(description, url, name),
                    'cost': self.parse_cost_info(description, name),
                    'location_type': 'In-person',
                    'time_commitment': '4-6 months',
                    'prerequisite_level': 'None',
                    'support_level': 'High',
                    'deadline': self.parse_deadline(description, name),
                    'financial_barrier_level': 'Medium',
                    'financial_aid_available': self.parse_financial_aid(description, name),
                    'family_income_consideration': False,
                    'hidden_costs_level': 'Travel',
                    'cost_category': '$500-2000',
                    'diversity_focus': self.parse_diversity_focus(description, name),
                    'underrepresented_friendly': True,
                    'first_gen_support': True,
                    'cultural_competency': 'Medium',
                    'rural_accessible': True,
                    'transportation_required': True,
                    'internet_dependency': 'Basic',
                    'regional_availability': 'National',
                    'family_involvement_required': 'Optional',
                    'peer_network_building': True,
                    'mentor_access_level': 'Adult'
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

    def add_known_vex_programs(self):
        """Add well-known VEX Robotics competition programs with detailed information"""
        known_programs = [
            {
                'name': 'VEX IQ Competition',
                'description': 'Elementary and middle school robotics competition for ages 8-14. Teams design and build robots using VEX IQ system to compete in game-based challenges. Includes teamwork, robot skills, and STEM research project components.',
                'url': 'https://www.vexrobotics.com/vexiq/competition',
                'target_grade': '4-8',
                'cost': '300-800',
                'cost_category': '$300-800',
                'prerequisite_level': 'None',
                'time_commitment': '4-6 months'
            },
            {
                'name': 'VEX Robotics Competition (VRC)',
                'description': 'High school robotics competition for ages 14-18. Teams build robots using VEX V5 system to compete in strategic game challenges. Features alliance matches, skills challenges, and design awards at local, regional, and world championship levels.',
                'url': 'https://www.vexrobotics.com/v5/competition/vrc-competition',
                'target_grade': '9-12',
                'cost': '800-2000',
                'cost_category': '$800-2000',
                'prerequisite_level': 'Basic',
                'time_commitment': '6-8 months'
            },
            {
                'name': 'VEX U Competition',
                'description': 'University-level robotics competition for college students. Teams design custom robots with fewer restrictions than high school competition. Emphasizes advanced engineering design and autonomous programming capabilities.',
                'url': 'https://www.vexrobotics.com/competition/vexu',
                'target_grade': 'College',
                'cost': '1000-2500',
                'cost_category': '$1000-2500',
                'prerequisite_level': 'Medium',
                'time_commitment': '6-8 months'
            },
            {
                'name': 'VEX IQ Cooperative Competition',
                'description': 'Modified VEX IQ competition format emphasizing collaboration over competition. Teams work together to achieve common goals, promoting STEM learning and teamwork for younger students aged 6-11.',
                'url': 'https://www.vexrobotics.com/vexiq/competition',
                'target_grade': 'K-5',
                'cost': '200-500',
                'cost_category': '$200-500',
                'prerequisite_level': 'None',
                'time_commitment': '3-4 months',
                'diversity_focus': True
            },
            {
                'name': 'VEX Robotics World Championship',
                'description': 'Premier international robotics competition bringing together top VEX teams from around the world. Features VEX IQ, VRC, and VEX U divisions with over 1,600 teams competing in Louisville, Kentucky.',
                'url': 'https://www.vexrobotics.com/competition/worlds',
                'target_grade': '4-12',
                'cost': '2000-5000',
                'cost_category': '$2000-5000',
                'prerequisite_level': 'High',
                'time_commitment': '8+ months',
                'hidden_costs_level': 'High-travel'
            },
            {
                'name': 'VEX Robotics Skills Challenge',
                'description': 'Individual team skills competition component of VEX competitions. Teams compete in driver skills and autonomous skills challenges to qualify for championship events and earn recognition.',
                'url': 'https://www.vexrobotics.com/competition',
                'target_grade': '4-12',
                'cost': '0-100',
                'cost_category': 'Free-$100',
                'prerequisite_level': 'Basic',
                'time_commitment': '2-3 months'
            },
            {
                'name': 'VEX IQ STEM Research Project',
                'description': 'Research component of VEX IQ competition where teams investigate real-world STEM problems related to the game theme. Teams present their findings to judges, developing presentation and research skills.',
                'url': 'https://www.vexrobotics.com/vexiq/competition',
                'target_grade': '4-8',
                'cost': '50-200',
                'cost_category': '$50-200',
                'prerequisite_level': 'None',
                'time_commitment': '2-4 months',
                'stem_fields': 'Research, Communication, STEM Investigation'
            },
            {
                'name': 'VEX Robotics Design Award Competition',
                'description': 'Engineering design documentation and presentation competition within VEX events. Teams maintain engineering notebooks and present their design process to judges, emphasizing STEM learning over robot performance.',
                'url': 'https://www.vexrobotics.com/competition',
                'target_grade': '4-12',
                'cost': '25-100',
                'cost_category': '$25-100',
                'prerequisite_level': 'Basic',
                'time_commitment': '4-6 months',
                'stem_fields': 'Engineering Design, Documentation, Communication'
            },
            {
                'name': 'VEX Girls Powered Program',
                'description': 'Initiative to encourage girls participation in VEX Robotics through mentorship, all-girls teams, and special recognition. Provides resources and support for female students in STEM robotics.',
                'url': 'https://www.vexrobotics.com/girls-powered',
                'target_grade': '4-12',
                'cost': '0-50',
                'cost_category': 'Free-$50',
                'prerequisite_level': 'None',
                'time_commitment': '1-2 months',
                'diversity_focus': True,
                'financial_aid_available': True
            },
            {
                'name': 'VEX Robotics Signature Events',
                'description': 'Premium regional competitions with enhanced awards, recognition, and qualification opportunities for VEX Worlds. Features top-tier competition experience with additional STEM activities and networking.',
                'url': 'https://www.vexrobotics.com/competition/signature-events',
                'target_grade': '6-12',
                'cost': '500-1500',
                'cost_category': '$500-1500',
                'prerequisite_level': 'Medium',
                'time_commitment': '6-8 months'
            }
        ]

        for program_data in known_programs:
            program = {
                'name': program_data['name'],
                'description': program_data['description'],
                'url': program_data['url'],
                'source': 'VEX Robotics',
                'category': 'Robotics Competition',
                'stem_fields': program_data.get('stem_fields', 'Engineering, Programming, Design, Mathematics'),
                'target_grade': program_data.get('target_grade', '6-12'),
                'cost': program_data.get('cost', '500-1500'),
                'location_type': 'In-person',
                'time_commitment': program_data.get('time_commitment', '4-6 months'),
                'prerequisite_level': program_data.get('prerequisite_level', 'None'),
                'support_level': 'High',
                'deadline': 'August-May (competition season)',
                'financial_barrier_level': 'Medium',
                'financial_aid_available': program_data.get('financial_aid_available', False),
                'family_income_consideration': False,
                'hidden_costs_level': program_data.get('hidden_costs_level', 'Travel'),
                'cost_category': program_data.get('cost_category', '$500-1500'),
                'diversity_focus': program_data.get('diversity_focus', False),
                'underrepresented_friendly': True,
                'first_gen_support': True,
                'cultural_competency': 'Medium',
                'rural_accessible': True,
                'transportation_required': True,
                'internet_dependency': 'Basic',
                'regional_availability': 'National',
                'family_involvement_required': 'Optional',
                'peer_network_building': True,
                'mentor_access_level': 'Adult'
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

        csv_file = os.path.join(data_dir, 'vex_robotics_programs.csv')

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
        logger.info("Starting VEX Robotics Competition scraper...")

        # First, add known VEX programs with detailed information
        self.add_known_vex_programs()

        # Then scrape additional programs from web pages
        for url in self.base_urls:
            try:
                self.scrape_vex_pages(url)
                time.sleep(2)  # Respectful delay between pages
            except Exception as e:
                logger.error(f"Error scraping {url}: {e}")
                continue

        # Save to CSV
        if self.programs:
            csv_file = self.save_to_csv()
            if csv_file:
                logger.info(f"Successfully created {csv_file} with {len(self.programs)} VEX Robotics programs")
                return csv_file
            else:
                logger.error("Failed to save CSV file")
                return None
        else:
            logger.warning("No programs found to save")
            return None

def main():
    scraper = VEXRoboticsScraper()
    result = scraper.run()

    if result:
        print(f"\nVEX Robotics Competition scraper completed successfully!")
        print(f"Output file: {result}")
        print(f"Total programs: {len(scraper.programs)}")
    else:
        print("\nScraper failed to complete")

if __name__ == "__main__":
    main()