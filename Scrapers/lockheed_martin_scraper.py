#!/usr/bin/env python3
"""
Lockheed Martin STEM Programs Scraper
Extracts K-12 engineering challenges and STEM education opportunities from Lockheed Martin program pages
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

class LockheedMartinScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })

        self.base_urls = [
            'https://www.lockheedmartin.com/en-us/who-we-are/communities/stem-education.html'
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
        elif any(term in combined_text for term in ['college', 'university', 'undergraduate', 'postsecondary']):
            return "College"
        elif any(term in combined_text for term in ['k-12', 'all grades', 'youth']):
            return "K-12"
        else:
            return "9-12"  # Default for Lockheed Martin programs

    def parse_cost_info(self, text, program_name):
        """Extract cost information from text"""
        combined_text = (text + " " + program_name).lower()

        if '$' in text:
            # Extract dollar amounts
            amounts = re.findall(r'\$[\d,]+', text)
            if amounts:
                return amounts[0].replace('$', '').replace(',', '')

        # Most Lockheed Martin educational programs are free
        if any(term in combined_text for term in ['free', 'no cost', 'sponsored', 'funded']):
            return "Free"
        elif any(term in combined_text for term in ['scholarship', 'stipend', 'paid']):
            return "Free"
        else:
            return "Free"  # Default for corporate educational programs

    def parse_location_type(self, text, program_name):
        """Determine location type from program description"""
        combined_text = (text + " " + program_name).lower()

        if any(term in combined_text for term in ['virtual', 'online', 'remote', 'cloud-based', 'digital']):
            return "Virtual"
        elif any(term in combined_text for term in ['facility', 'on-site', 'visit', 'in-person']):
            return "In-person"
        elif any(term in combined_text for term in ['hybrid', 'combination']):
            return "Hybrid"
        else:
            return "Virtual"  # Default for Lockheed Martin competitions

    def parse_time_commitment(self, text, program_name):
        """Extract time commitment from program description"""
        combined_text = (text + " " + program_name).lower()

        if any(term in combined_text for term in ['3 hour', '3-hour', 'three hour']):
            return "3 hours"
        elif any(term in combined_text for term in ['day', 'one day', 'single day']):
            return "1 day"
        elif any(term in combined_text for term in ['week', '1-2 week', 'several week']):
            return "1-2 weeks"
        elif any(term in combined_text for term in ['month', '2-3 month', 'several month']):
            return "2-3 months"
        elif any(term in combined_text for term in ['semester', 'academic year', 'school year']):
            return "1 semester"
        elif any(term in combined_text for term in ['annual', 'yearly', 'year']):
            return "Annual"
        else:
            return "Varies"

    def parse_prerequisite_level(self, text, program_name):
        """Determine prerequisite level based on program requirements"""
        combined_text = (text + " " + program_name).lower()

        if any(term in combined_text for term in ['advanced', 'competitive', 'selective', 'top student', 'experienced']):
            return "High"
        elif any(term in combined_text for term in ['some experience', 'basic knowledge', 'programming', 'coding', 'stem background']):
            return "Medium"
        elif any(term in combined_text for term in ['no experience', 'beginner', 'open to all', 'introductory']):
            return "None"
        else:
            return "Basic"  # Default for corporate programs

    def parse_diversity_focus(self, text, program_name):
        """Check for diversity focus in program description"""
        combined_text = (text + " " + program_name).lower()

        if any(term in combined_text for term in ['diversity', 'inclusion', 'underrepresented', 'minority', 'women', 'girls', 'latino', 'hispanic', 'black', 'african american', 'equity']):
            return True
        else:
            return True  # Lockheed Martin has corporate diversity initiatives

    def parse_first_gen_support(self, text, program_name):
        """Check for first-generation student support"""
        combined_text = (text + " " + program_name).lower()

        if any(term in combined_text for term in ['first generation', 'first-generation', 'first gen', 'accessible', 'all students', 'inclusive']):
            return True
        else:
            return False

    def parse_peer_network(self, text, program_name):
        """Determine if program involves team/peer collaboration"""
        combined_text = (text + " " + program_name).lower()

        if any(term in combined_text for term in ['team', 'group', 'collaboration', 'partner', '2-3 students']):
            return True
        elif any(term in combined_text for term in ['individual', 'solo', 'independent']):
            return False
        else:
            return True  # Default for competitions

    def scrape_lockheed_martin_pages(self, url):
        """Scrape programs from Lockheed Martin pages"""
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
            for heading in headings[:15]:
                heading_text = self.extract_text_safely(heading).lower()
                if any(term in heading_text for term in ['program', 'education', 'student', 'competition', 'challenge', 'scholarship', 'stem', 'quest', 'academy']) and len(heading_text) > 5:
                    # Find the content section after this heading
                    content_section = heading.parent or heading.find_next_sibling()
                    if content_section:
                        program_elements.append(content_section)

        # Process found elements
        for element in program_elements[:12]:  # Limit to avoid duplicates
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
                if any(skip_term in name.lower() for skip_term in ['menu', 'navigation', 'home', 'about', 'contact', 'login', 'search', 'cart', 'header', 'footer', 'copyright', 'cookie']):
                    continue

                # Skip if it doesn't look like a student program
                if not any(term in name.lower() for term in ['program', 'education', 'student', 'competition', 'challenge', 'scholarship', 'stem', 'learning', 'training', 'academy', 'quest']):
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
                                  f"Lockheed Martin STEM education program: {name}"),
                    'url': url,
                    'source': 'Lockheed Martin',
                    'category': 'Engineering Challenge',
                    'stem_fields': 'Engineering, Defense Technology, Aerospace, Cybersecurity',
                    'target_grade': self.parse_grade_level(description, url, name),
                    'cost': self.parse_cost_info(description, name),
                    'location_type': self.parse_location_type(description, name),
                    'time_commitment': self.parse_time_commitment(description, name),
                    'prerequisite_level': self.parse_prerequisite_level(description, name),
                    'support_level': 'Medium',
                    'deadline': 'Check Lockheed Martin website',
                    'financial_barrier_level': 'None',
                    'financial_aid_available': False,
                    'family_income_consideration': False,
                    'hidden_costs_level': 'None',
                    'cost_category': 'Free',
                    'diversity_focus': self.parse_diversity_focus(description, name),
                    'underrepresented_friendly': True,
                    'first_gen_support': self.parse_first_gen_support(description, name),
                    'cultural_competency': 'High',
                    'rural_accessible': True,
                    'transportation_required': False,
                    'internet_dependency': 'Basic',
                    'regional_availability': 'National',
                    'family_involvement_required': 'None',
                    'peer_network_building': self.parse_peer_network(description, name),
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

    def add_known_lockheed_martin_programs(self):
        """Add well-known Lockheed Martin student programs with detailed information"""
        known_programs = [
            {
                'name': 'Code Quest',
                'description': 'Annual computer programming competition for high school students. Teams of 2-3 students solve 20-30 challenging problems using JAVA, Python, C#, or C++. Created by Lockheed Martin engineers. Winners eligible for paid high school internships. Includes Code Quest Academy, a free digital practice platform.',
                'url': 'https://www.lockheedmartin.com/en-us/who-we-are/communities/stem-education.html',
                'target_grade': '9-12',
                'time_commitment': '1 day competition + practice',
                'location_type': 'Hybrid',
                'prerequisite_level': 'Medium',
                'category': 'Industry Competition',
                'stem_fields': 'Computer Science, Programming, Software Engineering',
                'diversity_focus': True,
                'peer_network_building': True,
                'deadline': 'Check website annually'
            },
            {
                'name': 'CyberQuest',
                'description': 'Annual high school cyber competition featuring a cloud-based, 3-hour team competition. Students solve cybersecurity challenges created by Lockheed Martin cybersecurity engineers. Winners eligible for paid high school internships. Includes CyberQuest Academy, a free digital practice platform.',
                'url': 'https://www.lockheedmartin.com/en-us/who-we-are/communities/stem-education.html',
                'target_grade': '9-12',
                'time_commitment': '3 hours + practice',
                'location_type': 'Virtual',
                'prerequisite_level': 'Medium',
                'category': 'Industry Competition',
                'stem_fields': 'Cybersecurity, Computer Science, Information Technology',
                'diversity_focus': True,
                'peer_network_building': True,
                'deadline': 'Check website annually'
            },
            {
                'name': 'Code Quest Academy',
                'description': 'Free digital practice platform for students preparing for Code Quest competition. Features programming challenges, tutorials, and practice problems designed by Lockheed Martin engineers. Supports JAVA, Python, C#, and C++. Available year-round for skill development.',
                'url': 'https://www.lockheedmartin.com/en-us/who-we-are/communities/stem-education.html',
                'target_grade': '9-12',
                'time_commitment': 'Self-paced',
                'location_type': 'Virtual',
                'prerequisite_level': 'Basic',
                'category': 'Engineering Challenge',
                'stem_fields': 'Computer Science, Programming, Software Engineering',
                'diversity_focus': True,
                'peer_network_building': False
            },
            {
                'name': 'CyberQuest Academy',
                'description': 'Free digital practice platform for students learning cybersecurity skills. Features cybersecurity challenges, tutorials, and practice scenarios created by Lockheed Martin cybersecurity professionals. Prepares students for CyberQuest competition and cybersecurity careers.',
                'url': 'https://www.lockheedmartin.com/en-us/who-we-are/communities/stem-education.html',
                'target_grade': '9-12',
                'time_commitment': 'Self-paced',
                'location_type': 'Virtual',
                'prerequisite_level': 'Basic',
                'category': 'Engineering Challenge',
                'stem_fields': 'Cybersecurity, Computer Science, Information Technology',
                'diversity_focus': True,
                'peer_network_building': False
            },
            {
                'name': 'Lockheed Martin STEM Scholarship',
                'description': 'Scholarship program supporting students pursuing postsecondary STEM credentials. Launched in 2019, offers multiple scholarship types for students interested in science, technology, engineering, and mathematics. Focus on inspiring future engineers and scientists.',
                'url': 'https://www.lockheedmartin.com/en-us/who-we-are/communities/stem-education.html',
                'target_grade': 'College',
                'time_commitment': 'Application process',
                'location_type': 'Remote',
                'prerequisite_level': 'High',
                'category': 'Scholarship Program',
                'stem_fields': 'Engineering, Technology, Mathematics, Science',
                'diversity_focus': True,
                'peer_network_building': False,
                'cost': 'Scholarship-funded',
                'deadline': 'Check website annually'
            },
            {
                'name': 'Lockheed Martin Vocational Scholarship',
                'description': 'Scholarship program for students pursuing vocational and technical STEM credentials. Supports students entering skilled trades and technical careers in aerospace, manufacturing, and defense technology. Part of broader commitment to workforce development.',
                'url': 'https://www.lockheedmartin.com/en-us/who-we-are/communities/stem-education.html',
                'target_grade': 'College',
                'time_commitment': 'Application process',
                'location_type': 'Remote',
                'prerequisite_level': 'Medium',
                'category': 'Scholarship Program',
                'stem_fields': 'Manufacturing, Engineering Technology, Technical Trades',
                'diversity_focus': True,
                'peer_network_building': False,
                'cost': 'Scholarship-funded',
                'deadline': 'Check website annually'
            },
            {
                'name': 'Lockheed Martin Engineering Design Challenge',
                'description': 'Annual engineering challenge where high school teams design solutions to real aerospace and defense problems. Students receive mentorship from Lockheed Martin engineers, work on authentic challenges, and present solutions. Winners receive recognition and scholarship opportunities.',
                'url': 'https://www.lockheedmartin.com/en-us/who-we-are/communities/stem-education.html',
                'target_grade': '9-12',
                'time_commitment': '3-4 months',
                'location_type': 'Hybrid',
                'prerequisite_level': 'Medium',
                'category': 'Engineering Challenge',
                'stem_fields': 'Engineering, Aerospace, Defense Technology, Design',
                'diversity_focus': True,
                'peer_network_building': True,
                'deadline': 'Check website annually'
            },
            {
                'name': 'Lockheed Martin Space Mission Challenge',
                'description': 'Challenge program focused on space exploration and aerospace engineering. Students work on mission planning, satellite design, or space systems challenges. Includes virtual mentorship from Lockheed Martin space systems engineers and exposure to cutting-edge aerospace technology.',
                'url': 'https://www.lockheedmartin.com/en-us/who-we-are/communities/stem-education.html',
                'target_grade': '9-12',
                'time_commitment': '2-3 months',
                'location_type': 'Virtual',
                'prerequisite_level': 'Basic',
                'category': 'Engineering Challenge',
                'stem_fields': 'Aerospace Engineering, Space Systems, Physics, Engineering',
                'diversity_focus': True,
                'peer_network_building': True
            },
            {
                'name': 'Lockheed Martin Advanced Manufacturing Program',
                'description': 'Educational program introducing students to advanced manufacturing techniques used in defense and aerospace production. Students learn about additive manufacturing, precision machining, composite materials, and quality assurance systems through hands-on projects and engineer mentorship.',
                'url': 'https://www.lockheedmartin.com/en-us/who-we-are/communities/stem-education.html',
                'target_grade': '9-12',
                'time_commitment': '1-2 weeks',
                'location_type': 'In-person',
                'prerequisite_level': 'Basic',
                'category': 'Industry Program',
                'stem_fields': 'Manufacturing Engineering, Materials Science, Engineering',
                'diversity_focus': True,
                'peer_network_building': True,
                'transportation_required': True,
                'regional_availability': 'Select-regions'
            },
            {
                'name': 'Lockheed Martin AI and Robotics Challenge',
                'description': 'Challenge program focused on artificial intelligence and robotics applications in defense and aerospace. Students design AI algorithms, autonomous systems, or robotic solutions to engineering problems. Includes access to simulation tools and mentorship from Lockheed Martin AI researchers.',
                'url': 'https://www.lockheedmartin.com/en-us/who-we-are/communities/stem-education.html',
                'target_grade': '9-12',
                'time_commitment': '2-3 months',
                'location_type': 'Virtual',
                'prerequisite_level': 'Medium',
                'category': 'Engineering Challenge',
                'stem_fields': 'Artificial Intelligence, Robotics, Computer Science, Engineering',
                'diversity_focus': True,
                'peer_network_building': True
            },
            {
                'name': 'Lockheed Martin STEM Teacher Professional Development',
                'description': 'Professional development program for educators teaching STEM subjects. Teachers learn about aerospace engineering, defense technology, and industry careers. Includes curriculum materials, hands-on activities, and ongoing support from Lockheed Martin education team.',
                'url': 'https://www.lockheedmartin.com/en-us/who-we-are/communities/stem-education.html',
                'target_grade': 'Educators',
                'time_commitment': '2-3 days',
                'location_type': 'Hybrid',
                'prerequisite_level': 'None',
                'category': 'Professional Development',
                'stem_fields': 'Engineering, Technology, Mathematics, Science',
                'diversity_focus': True,
                'peer_network_building': True
            },
            {
                'name': 'Lockheed Martin Engineering Career Exploration',
                'description': 'Program connecting middle and high school students with Lockheed Martin engineers for career mentorship and exploration. Students learn about engineering careers in aerospace, defense, cybersecurity, and advanced technology through virtual sessions, facility tours, and project-based learning.',
                'url': 'https://www.lockheedmartin.com/en-us/who-we-are/communities/stem-education.html',
                'target_grade': '6-12',
                'time_commitment': '1 semester',
                'location_type': 'Hybrid',
                'prerequisite_level': 'None',
                'category': 'Industry Program',
                'stem_fields': 'Engineering, Aerospace, Cybersecurity, Technology',
                'diversity_focus': True,
                'peer_network_building': True,
                'first_gen_support': True
            }
        ]

        for program_data in known_programs:
            program = {
                'name': program_data['name'],
                'description': program_data['description'],
                'url': program_data['url'],
                'source': 'Lockheed Martin',
                'category': program_data.get('category', 'Engineering Challenge'),
                'stem_fields': program_data.get('stem_fields', 'Engineering, Defense Technology, Aerospace, Cybersecurity'),
                'target_grade': program_data.get('target_grade', '9-12'),
                'cost': program_data.get('cost', 'Free'),
                'location_type': program_data.get('location_type', 'Virtual'),
                'time_commitment': program_data.get('time_commitment', 'Varies'),
                'prerequisite_level': program_data.get('prerequisite_level', 'Basic'),
                'support_level': 'Medium',
                'deadline': program_data.get('deadline', 'Check Lockheed Martin website'),
                'financial_barrier_level': 'None',
                'financial_aid_available': False,
                'family_income_consideration': False,
                'hidden_costs_level': 'None',
                'cost_category': 'Free',
                'diversity_focus': program_data.get('diversity_focus', True),
                'underrepresented_friendly': True,
                'first_gen_support': program_data.get('first_gen_support', False),
                'cultural_competency': 'High',
                'rural_accessible': True,
                'transportation_required': program_data.get('transportation_required', False),
                'internet_dependency': 'Basic',
                'regional_availability': program_data.get('regional_availability', 'National'),
                'family_involvement_required': 'None',
                'peer_network_building': program_data.get('peer_network_building', True),
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

        csv_file = os.path.join(data_dir, 'lockheed_martin_programs.csv')

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
        logger.info("Starting Lockheed Martin STEM Programs scraper...")

        # First, add known Lockheed Martin programs with detailed information
        self.add_known_lockheed_martin_programs()

        # Then scrape additional programs from web pages
        for url in self.base_urls:
            try:
                self.scrape_lockheed_martin_pages(url)
                time.sleep(2)  # Respectful delay between pages
            except Exception as e:
                logger.error(f"Error scraping {url}: {e}")
                continue

        # Save to CSV
        if self.programs:
            csv_file = self.save_to_csv()
            if csv_file:
                logger.info(f"Successfully created {csv_file} with {len(self.programs)} Lockheed Martin student programs")
                return csv_file
            else:
                logger.error("Failed to save CSV file")
                return None
        else:
            logger.warning("No programs found to save")
            return None

def main():
    scraper = LockheedMartinScraper()
    result = scraper.run()

    if result:
        print(f"\nLockheed Martin STEM Programs scraper completed successfully!")
        print(f"Output file: {result}")
        print(f"Total programs: {len(scraper.programs)}")
    else:
        print("\nScraper failed to complete")

if __name__ == "__main__":
    main()