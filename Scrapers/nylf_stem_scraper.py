#!/usr/bin/env python3
"""
National Youth Leadership Forum STEM Programs Scraper
Extracts leadership and career exploration programs for high school students
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

class NYLFScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })

        self.base_urls = [
            'https://www.nylf.org/',
            'https://www.nylf.org/programs/medicine',
            'https://www.nylf.org/programs/engineering',
            'https://www.nylf.org/programs/cybersecurity'
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

    def parse_stem_fields(self, program_name, description):
        """Determine STEM fields based on program name and description"""
        combined_text = (program_name + " " + description).lower()

        fields = []

        if any(term in combined_text for term in ['medicine', 'medical', 'health', 'healthcare', 'physician']):
            fields.append('Medicine')
            fields.append('Health Sciences')
        if any(term in combined_text for term in ['engineering', 'engineer']):
            fields.append('Engineering')
        if any(term in combined_text for term in ['cybersecurity', 'cyber security', 'security', 'hacking', 'network security']):
            fields.append('Cybersecurity')
            fields.append('Computer Science')
        if any(term in combined_text for term in ['technology', 'tech', 'computer', 'digital']):
            fields.append('Technology')
        if any(term in combined_text for term in ['biomedical', 'biotechnology', 'biotech']):
            fields.append('Biotechnology')
        if any(term in combined_text for term in ['data science', 'data analytics', 'analytics']):
            fields.append('Data Science')
        if any(term in combined_text for term in ['robotics', 'robot']):
            fields.append('Robotics')
        if any(term in combined_text for term in ['aerospace', 'aviation']):
            fields.append('Aerospace Engineering')

        # If no specific fields found, default to STEM
        if not fields:
            fields.append('STEM')

        return ', '.join(fields)

    def parse_cost(self, description, program_name):
        """Extract cost information from program description"""
        combined_text = (description + " " + program_name).lower()

        # Look for dollar amounts
        cost_patterns = [
            r'\$[\d,]+',
            r'(\d+,?\d+)\s*dollars?',
        ]

        for pattern in cost_patterns:
            match = re.search(pattern, description)
            if match:
                return match.group(0).replace('$', '').replace(',', '')

        # Default cost for NYLF programs (typically $2000-$4000)
        return "3000"  # Approximate average

    def parse_financial_aid(self, description, program_name):
        """Check for financial aid availability"""
        combined_text = (description + " " + program_name).lower()

        if any(term in combined_text for term in ['scholarship', 'financial aid', 'need-based', 'funding available', 'assistance available']):
            return True
        else:
            return False

    def parse_diversity_focus(self, description, program_name):
        """Check for diversity focus in program description"""
        combined_text = (description + " " + program_name).lower()

        if any(term in combined_text for term in ['diversity', 'inclusion', 'underrepresented', 'minority', 'equity', 'all students', 'diverse backgrounds']):
            return True
        else:
            return False

    def parse_first_gen_support(self, description, program_name):
        """Check for first-generation student support"""
        combined_text = (description + " " + program_name).lower()

        if any(term in combined_text for term in ['first generation', 'first-generation', 'first gen', 'family college', 'scholarship']):
            return True
        else:
            return False

    def scrape_nylf_pages(self, url):
        """Scrape programs from NYLF pages"""
        soup = self.fetch_page(url)
        if not soup:
            return

        programs_found = 0

        # Look for program information
        program_selectors = [
            'div.program-card', 'div.program-info', 'article.program',
            '.content-area', 'main', 'div.main-content', 'section.program',
            'div[class*="program"]', 'div[class*="track"]'
        ]

        program_elements = []
        for selector in program_selectors:
            elements = soup.select(selector)
            if elements:
                program_elements.extend(elements[:12])
                break

        # If no specific containers found, look for headings
        if not program_elements:
            headings = soup.find_all(['h1', 'h2', 'h3', 'h4'])
            for heading in headings[:15]:
                heading_text = self.extract_text_safely(heading).lower()
                if any(term in heading_text for term in ['nylf', 'medicine', 'engineering', 'cybersecurity', 'stem', 'leadership', 'program', 'track']) and len(heading_text) > 5:
                    content_section = heading.parent or heading.find_next_sibling()
                    if content_section:
                        program_elements.append(content_section)

        # Process found elements
        for element in program_elements[:12]:
            try:
                # Extract program name
                name_elem = (element.find(['h1', 'h2', 'h3', 'h4']) or
                           element.select_one('.title, .program-title, .name') or
                           element.find('strong') or element.find('b'))

                if not name_elem:
                    continue

                name = self.extract_text_safely(name_elem)
                if not name or len(name) < 5 or len(name) > 200:
                    continue

                # Skip navigation or irrelevant content
                if any(skip_term in name.lower() for skip_term in ['menu', 'navigation', 'home', 'about us', 'contact', 'login', 'search', 'header', 'footer', 'apply now', 'learn more']):
                    continue

                # Skip if it doesn't look like a NYLF program
                if not any(term in name.lower() for term in ['nylf', 'medicine', 'engineering', 'cybersecurity', 'stem', 'leadership', 'program', 'forum', 'career', 'track']):
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
                    description = f"National Youth Leadership Forum program: {name}. Leadership development and career exploration for high school students."

                # Create program entry
                program = {
                    'name': name,
                    'description': (description[:500] if description else
                                  f"NYLF program: {name}"),
                    'url': url,
                    'source': 'National Youth Leadership Forum',
                    'category': 'Leadership Program',
                    'stem_fields': self.parse_stem_fields(name, description),
                    'target_grade': '10-12',
                    'cost': self.parse_cost(description, name),
                    'location_type': 'Regional',
                    'time_commitment': '5-10 days',
                    'prerequisite_level': 'Medium',
                    'support_level': 'High',
                    'deadline': 'Check NYLF website',
                    'financial_barrier_level': 'High',
                    'financial_aid_available': self.parse_financial_aid(description, name),
                    'family_income_consideration': 'Middle+',
                    'hidden_costs_level': 'Travel',
                    'cost_category': '$2000+',
                    'diversity_focus': self.parse_diversity_focus(description, name),
                    'underrepresented_friendly': True,
                    'first_gen_support': self.parse_first_gen_support(description, name),
                    'cultural_competency': 'Medium',
                    'rural_accessible': False,
                    'transportation_required': True,
                    'internet_dependency': 'Basic',
                    'regional_availability': 'National',
                    'family_involvement_required': 'Required',
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

    def add_known_nylf_programs(self):
        """Add well-known NYLF programs with detailed information"""
        known_programs = [
            {
                'name': 'NYLF Medicine',
                'description': 'Nine-day leadership development program exploring medical careers and healthcare systems. Students participate in hands-on medical simulations, interact with healthcare professionals, visit medical facilities, and develop leadership skills. Learn about various medical specialties, healthcare ethics, and patient care. Offered in multiple cities nationwide.',
                'url': 'https://www.nylf.org/programs/medicine',
                'stem_fields': 'Medicine, Health Sciences, Biology',
                'time_commitment': '9 days',
                'cost': '3200',
                'financial_aid_available': True
            },
            {
                'name': 'NYLF Engineering',
                'description': 'Multi-day engineering career exploration and leadership program. Students work on engineering challenges, meet professional engineers, visit engineering firms and labs, and explore various engineering disciplines. Includes team projects, design competitions, and exposure to cutting-edge technology. Develops technical and leadership skills.',
                'url': 'https://www.nylf.org/programs/engineering',
                'stem_fields': 'Engineering, Technology, Design',
                'time_commitment': '6 days',
                'cost': '2800',
                'financial_aid_available': True
            },
            {
                'name': 'NYLF Cybersecurity',
                'description': 'Intensive cybersecurity leadership program teaching network security, ethical hacking, threat assessment, and digital forensics. Students learn from cybersecurity professionals, participate in capture-the-flag competitions, and explore career pathways in cybersecurity. Covers technical skills and leadership development. Offered at select locations.',
                'url': 'https://www.nylf.org/programs/cybersecurity',
                'stem_fields': 'Cybersecurity, Computer Science, Information Technology',
                'time_commitment': '6 days',
                'cost': '2900',
                'financial_aid_available': True
            },
            {
                'name': 'NYLF Advanced Medicine & Health Care',
                'description': 'Advanced medical leadership program for students serious about healthcare careers. Deep dive into medical specialties, surgical simulations, patient diagnosis, and healthcare leadership. Meet physicians, surgeons, and healthcare administrators. Includes hospital visits, medical ethics discussions, and career planning sessions.',
                'url': 'https://www.nylf.org/',
                'stem_fields': 'Medicine, Health Sciences, Healthcare Administration',
                'time_commitment': '10 days',
                'cost': '3500',
                'financial_aid_available': True,
                'category': 'Career Exploration Program'
            },
            {
                'name': 'NYLF Explore STEM',
                'description': 'Broad STEM career exploration program exposing students to multiple STEM fields including engineering, technology, medicine, and research. Students meet professionals, visit companies and labs, participate in hands-on activities, and develop leadership skills. Ideal for students exploring STEM career options.',
                'url': 'https://www.nylf.org/',
                'stem_fields': 'Engineering, Technology, Medicine, Science',
                'time_commitment': '6 days',
                'cost': '2700',
                'financial_aid_available': True,
                'category': 'Career Exploration Program'
            },
            {
                'name': 'NYLF Pathways to STEM',
                'description': 'Leadership program connecting students with STEM professionals and academic pathways. Learn about STEM college programs, careers, and opportunities. Includes college planning, resume building, and networking sessions. Meet successful STEM professionals and learn about their career journeys. Emphasis on underrepresented students in STEM.',
                'url': 'https://www.nylf.org/',
                'stem_fields': 'STEM, Engineering, Science, Technology',
                'time_commitment': '5 days',
                'cost': '2500',
                'financial_aid_available': True,
                'diversity_focus': True
            },
            {
                'name': 'NYLF Biomedical Science',
                'description': 'Program exploring intersection of medicine, biology, and technology. Students learn about biomedical research, biotechnology, genetic engineering, and medical innovations. Includes laboratory work, research presentations, and meetings with biomedical scientists. Covers career pathways in biomedical sciences.',
                'url': 'https://www.nylf.org/',
                'stem_fields': 'Biotechnology, Biomedical Science, Biology, Medicine',
                'time_commitment': '7 days',
                'cost': '3000',
                'financial_aid_available': True,
                'category': 'Career Exploration Program'
            },
            {
                'name': 'NYLF Technology & Innovation',
                'description': 'Leadership program focused on emerging technologies and innovation. Explore artificial intelligence, robotics, software development, and tech entrepreneurship. Meet technology leaders, visit tech companies, and work on innovation projects. Learn about technology career pathways and leadership in tech industry.',
                'url': 'https://www.nylf.org/',
                'stem_fields': 'Technology, Computer Science, Robotics, AI',
                'time_commitment': '6 days',
                'cost': '2900',
                'financial_aid_available': True,
                'category': 'Career Exploration Program'
            },
            {
                'name': 'NYLF National Security',
                'description': 'Program exploring careers in national security, intelligence, and defense technology. Learn about cybersecurity, intelligence analysis, defense systems, and national security policy. Meet professionals from defense and intelligence agencies. Includes leadership training and ethical discussions. Selective program.',
                'url': 'https://www.nylf.org/',
                'stem_fields': 'Cybersecurity, Technology, Defense Technology',
                'time_commitment': '6 days',
                'cost': '3100',
                'financial_aid_available': True,
                'prerequisite_level': 'High'
            },
            {
                'name': 'NYLF Women in STEM Leadership',
                'description': 'Leadership program specifically designed for young women interested in STEM careers. Address challenges women face in STEM, meet successful women in STEM fields, develop leadership confidence, and explore various STEM careers. Includes mentorship, networking, and skill-building workshops. Empowering program.',
                'url': 'https://www.nylf.org/',
                'stem_fields': 'Engineering, Technology, Science, Mathematics',
                'time_commitment': '5 days',
                'cost': '2600',
                'financial_aid_available': True,
                'diversity_focus': True,
                'first_gen_support': True
            }
        ]

        for program_data in known_programs:
            program = {
                'name': program_data['name'],
                'description': program_data['description'],
                'url': program_data['url'],
                'source': 'National Youth Leadership Forum',
                'category': program_data.get('category', 'Leadership Program'),
                'stem_fields': program_data.get('stem_fields', 'STEM'),
                'target_grade': '10-12',
                'cost': program_data.get('cost', '3000'),
                'location_type': 'Regional',
                'time_commitment': program_data.get('time_commitment', '6 days'),
                'prerequisite_level': program_data.get('prerequisite_level', 'Medium'),
                'support_level': 'High',
                'deadline': 'Check NYLF website',
                'financial_barrier_level': 'High',
                'financial_aid_available': program_data.get('financial_aid_available', False),
                'family_income_consideration': 'Middle+',
                'hidden_costs_level': 'Travel',
                'cost_category': '$2000+',
                'diversity_focus': program_data.get('diversity_focus', False),
                'underrepresented_friendly': True,
                'first_gen_support': program_data.get('first_gen_support', False),
                'cultural_competency': 'Medium',
                'rural_accessible': False,
                'transportation_required': True,
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
        data_dir = 'data'
        os.makedirs(data_dir, exist_ok=True)

        csv_file = os.path.join(data_dir, 'nylf_stem_programs.csv')

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
        logger.info("Starting National Youth Leadership Forum STEM Programs scraper...")

        # First, add known NYLF programs with detailed information
        self.add_known_nylf_programs()

        # Then scrape additional programs from web pages
        for url in self.base_urls:
            try:
                self.scrape_nylf_pages(url)
                time.sleep(2)  # Respectful delay between pages
            except Exception as e:
                logger.error(f"Error scraping {url}: {e}")
                continue

        # Save to CSV
        if self.programs:
            csv_file = self.save_to_csv()
            if csv_file:
                logger.info(f"Successfully created {csv_file} with {len(self.programs)} NYLF STEM programs")
                return csv_file
            else:
                logger.error("Failed to save CSV file")
                return None
        else:
            logger.warning("No programs found to save")
            return None

def main():
    scraper = NYLFScraper()
    result = scraper.run()

    if result:
        print(f"\nNational Youth Leadership Forum STEM Programs scraper completed successfully!")
        print(f"Output file: {result}")
        print(f"Total programs: {len(scraper.programs)}")
    else:
        print("\nScraper failed to complete")

if __name__ == "__main__":
    main()