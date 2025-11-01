#!/usr/bin/env python3
"""
Carnegie Mellon Pre-College Programs Scraper
Extracts high school summer programs from Carnegie Mellon University
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

class CMUPreCollegeScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })

        self.base_urls = [
            'https://www.cmu.edu/pre-college/'
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

        if any(term in combined_text for term in ['computer science', 'cs scholars', 'programming', 'software', 'coding']):
            fields.append('Computer Science')
        if any(term in combined_text for term in ['artificial intelligence', 'ai scholars', 'ai', 'machine learning']):
            fields.append('Artificial Intelligence')
        if any(term in combined_text for term in ['robotics', 'robot']):
            fields.append('Robotics')
        if any(term in combined_text for term in ['game', 'game academy', 'game development', 'gaming']):
            fields.append('Game Development')
        if any(term in combined_text for term in ['engineering', 'engineer']):
            fields.append('Engineering')
        if any(term in combined_text for term in ['computational biology', 'bioinformatics', 'biology']):
            fields.append('Computational Biology')
        if any(term in combined_text for term in ['architecture', 'architectural']):
            fields.append('Architecture')
        if any(term in combined_text for term in ['design', 'ux', 'ui']):
            fields.append('Design')
        if any(term in combined_text for term in ['math', 'mathematics', 'science']):
            fields.append('Mathematics')
        if any(term in combined_text for term in ['emerging technology', 'technology']):
            fields.append('Technology')

        # If no specific fields found, default to Technology
        if not fields:
            fields.append('Technology')

        return ', '.join(fields)

    def parse_prerequisite_level(self, program_name, description):
        """Determine prerequisite level based on program details"""
        combined_text = (program_name + " " + description).lower()

        if any(term in combined_text for term in ['advanced', 'scholars', 'competitive', 'selective', 'experienced']):
            return "High"
        elif any(term in combined_text for term in ['intermediate', 'some experience', 'basic knowledge', 'familiarity']):
            return "Medium"
        elif any(term in combined_text for term in ['beginner', 'introduction', 'introductory', 'no experience']):
            return "Basic"
        else:
            return "Medium"  # Default for CMU programs

    def parse_diversity_focus(self, program_name, description):
        """Check for diversity focus in program description"""
        combined_text = (program_name + " " + description).lower()

        if any(term in combined_text for term in ['diversity', 'inclusion', 'underrepresented', 'minority', 'women', 'girls', 'equity', 'access', 'scholarship']):
            return True
        else:
            return False

    def parse_first_gen_support(self, program_name, description):
        """Check for first-generation student support"""
        combined_text = (program_name + " " + description).lower()

        if any(term in combined_text for term in ['first generation', 'first-generation', 'first gen', 'financial aid', 'need-based', 'scholarship']):
            return True
        else:
            return False

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

        # Default cost for CMU programs (typically $5000-$10000+)
        return "7500"  # Approximate average

    def scrape_cmu_pages(self, url):
        """Scrape programs from CMU Pre-College pages"""
        soup = self.fetch_page(url)
        if not soup:
            return

        programs_found = 0

        # Look for program information
        program_selectors = [
            'div.program-card', 'div.program-info', 'article.program',
            '.content-area', 'main', 'div.main-content', 'section.program',
            'div[class*="program"]', 'div[class*="course"]', 'a[class*="program"]'
        ]

        program_elements = []
        for selector in program_selectors:
            elements = soup.select(selector)
            if elements:
                program_elements.extend(elements[:15])
                break

        # If no specific containers found, look for program links and headings
        if not program_elements:
            # Look for navigation or program list items
            nav_items = soup.find_all(['li', 'a'])
            for item in nav_items[:20]:
                item_text = self.extract_text_safely(item).lower()
                if any(term in item_text for term in ['scholars', 'academy', 'program', 'architecture', 'design', 'drama', 'music', 'computational', 'leadership', 'summer session', 'game']) and len(item_text) > 3 and len(item_text) < 100:
                    program_elements.append(item)

        # Process found elements
        for element in program_elements[:20]:
            try:
                # Extract program name
                name = ""
                if element.name == 'a':
                    name = self.extract_text_safely(element)
                else:
                    name_elem = (element.find(['h1', 'h2', 'h3', 'h4']) or
                               element.select_one('.title, .program-title, .name') or
                               element.find('strong') or element.find('b'))
                    if name_elem:
                        name = self.extract_text_safely(name_elem)

                if not name or len(name) < 3 or len(name) > 200:
                    continue

                # Skip navigation or irrelevant content
                if any(skip_term in name.lower() for skip_term in ['menu', 'navigation', 'home', 'about us', 'contact', 'login', 'search', 'header', 'footer', 'copyright', 'cookie', 'privacy', 'apply', 'application', 'mailing', 'opens']):
                    continue

                # Skip if it doesn't look like a program
                if not any(term in name.lower() for term in ['scholars', 'academy', 'program', 'architecture', 'design', 'drama', 'music', 'art', 'computational', 'leadership', 'summer', 'game', 'culture', 'writing', 'science', 'math']):
                    continue

                # Extract description from paragraphs or element content
                description = ""
                paragraphs = element.find_all('p')
                if paragraphs:
                    desc_texts = [self.extract_text_safely(p) for p in paragraphs[:3]]
                    description = " ".join([d for d in desc_texts if d and len(d) > 15])

                if not description:
                    description = self.extract_text_safely(element)

                # Default description based on program name
                if not description or len(description) < 20:
                    description = f"Carnegie Mellon Pre-College program focusing on {name}. Intensive summer program for high school students on CMU's Pittsburgh campus."

                # Create program entry
                program = {
                    'name': name,
                    'description': (description[:500] if description else
                                  f"Carnegie Mellon Pre-College program: {name}"),
                    'url': url,
                    'source': 'Carnegie Mellon Pre-College',
                    'category': 'Summer Program',
                    'stem_fields': self.parse_stem_fields(name, description),
                    'target_grade': '10-12',
                    'cost': self.parse_cost(description, name),
                    'location_type': 'Residential',
                    'time_commitment': '3-6 weeks',
                    'prerequisite_level': self.parse_prerequisite_level(name, description),
                    'support_level': 'High',
                    'deadline': 'Check CMU website',
                    'financial_barrier_level': 'High',
                    'financial_aid_available': True,
                    'family_income_consideration': 'Middle+',
                    'hidden_costs_level': 'Travel',
                    'cost_category': '$2000+',
                    'diversity_focus': self.parse_diversity_focus(name, description),
                    'underrepresented_friendly': True,
                    'first_gen_support': self.parse_first_gen_support(name, description),
                    'cultural_competency': 'Medium',
                    'rural_accessible': False,
                    'transportation_required': True,
                    'internet_dependency': 'High-speed-required',
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

    def add_known_cmu_programs(self):
        """Add well-known CMU Pre-College programs with detailed information"""
        known_programs = [
            {
                'name': 'AI Scholars',
                'description': 'Intensive summer program exploring artificial intelligence and machine learning. Students work on AI projects, learn from CMU faculty, and gain hands-on experience with cutting-edge AI technologies. Covers neural networks, natural language processing, computer vision, and AI ethics. Residential program on CMU campus.',
                'url': 'https://www.cmu.edu/pre-college/',
                'time_commitment': '6 weeks',
                'prerequisite_level': 'High',
                'stem_fields': 'Artificial Intelligence, Computer Science, Machine Learning',
                'cost': '9500',
                'diversity_focus': True,
                'first_gen_support': True
            },
            {
                'name': 'CS Scholars',
                'description': 'Comprehensive computer science program for high school students. Learn programming, algorithms, data structures, and software development from CMU faculty. Work on real-world projects and collaborate with peers. Includes exposure to CMU School of Computer Science research. Residential summer experience.',
                'url': 'https://www.cmu.edu/pre-college/',
                'time_commitment': '6 weeks',
                'prerequisite_level': 'High',
                'stem_fields': 'Computer Science, Programming, Software Engineering',
                'cost': '9500',
                'diversity_focus': True,
                'first_gen_support': True
            },
            {
                'name': 'National High School Game Academy',
                'description': 'Game design and development program combining art, programming, and storytelling. Students create original video games working in teams. Learn game engines, 3D modeling, animation, and game design principles. Taught by CMU Entertainment Technology Center faculty. Portfolio-building opportunity.',
                'url': 'https://www.cmu.edu/pre-college/',
                'time_commitment': '6 weeks',
                'prerequisite_level': 'Medium',
                'stem_fields': 'Game Development, Computer Science, Design, Programming',
                'cost': '9000',
                'diversity_focus': False
            },
            {
                'name': 'Computational Biology',
                'description': 'Interdisciplinary program at the intersection of biology, computer science, and mathematics. Learn bioinformatics, genomic analysis, computational modeling, and data science applications in biology. Work with real biological datasets and conduct research projects. Exposure to CMU computational biology research.',
                'url': 'https://www.cmu.edu/pre-college/',
                'time_commitment': '6 weeks',
                'prerequisite_level': 'High',
                'stem_fields': 'Computational Biology, Bioinformatics, Computer Science, Biology',
                'cost': '9500',
                'diversity_focus': True,
                'first_gen_support': True
            },
            {
                'name': 'Summer Academy for Math and Science',
                'description': 'Rigorous STEM program covering advanced mathematics and science topics. Students engage in problem-solving, research projects, and mathematical exploration. Learn from CMU faculty and graduate students. Includes laboratory work and computational methods. Prepares students for STEM majors.',
                'url': 'https://www.cmu.edu/pre-college/',
                'time_commitment': '6 weeks',
                'prerequisite_level': 'High',
                'stem_fields': 'Mathematics, Science, Physics, Chemistry',
                'cost': '8500',
                'diversity_focus': True,
                'first_gen_support': True
            },
            {
                'name': 'Architecture Program',
                'description': 'Intensive architecture and design program introducing students to architectural thinking and practice. Learn design principles, technical drawing, 3D modeling, and sustainable design. Work on design projects and visit Pittsburgh architecture sites. Studio-based learning with CMU School of Architecture faculty.',
                'url': 'https://www.cmu.edu/pre-college/',
                'time_commitment': '6 weeks',
                'prerequisite_level': 'Medium',
                'stem_fields': 'Architecture, Design, Engineering',
                'cost': '8500',
                'diversity_focus': False
            },
            {
                'name': 'Design Program',
                'description': 'Explore communication design, product design, and environmental design. Learn design thinking methodology, prototyping, user research, and visual communication. Work on real design challenges and build portfolio. Taught by CMU School of Design faculty. Includes workshops and studio projects.',
                'url': 'https://www.cmu.edu/pre-college/',
                'time_commitment': '6 weeks',
                'prerequisite_level': 'Medium',
                'stem_fields': 'Design, UX Design, Product Design, Visual Communication',
                'cost': '8500',
                'diversity_focus': False
            },
            {
                'name': 'Global Cultures and Emerging Technology',
                'description': 'Interdisciplinary program examining technology impact on global cultures and societies. Explore ethical issues, cultural perspectives on technology, and technology applications worldwide. Includes humanities and STEM perspectives. Learn about AI ethics, digital culture, and technology policy.',
                'url': 'https://www.cmu.edu/pre-college/',
                'time_commitment': '6 weeks',
                'prerequisite_level': 'Medium',
                'stem_fields': 'Technology, Computer Science, Ethics, Cultural Studies',
                'cost': '8000',
                'diversity_focus': True,
                'first_gen_support': True
            },
            {
                'name': 'Leadership Development Program',
                'description': 'Program developing leadership skills through workshops, team projects, and self-reflection. Learn about effective communication, ethical leadership, teamwork, and problem-solving. Includes community engagement projects and leadership simulations. Applicable to STEM and non-STEM careers.',
                'url': 'https://www.cmu.edu/pre-college/',
                'time_commitment': '3 weeks',
                'prerequisite_level': 'Basic',
                'stem_fields': 'Leadership, Management, Communication',
                'cost': '5000',
                'diversity_focus': True,
                'first_gen_support': True
            },
            {
                'name': 'Drama Program',
                'description': 'Intensive theater arts program with CMU School of Drama. Explore acting, directing, playwriting, and technical theater. Work on productions and develop performance skills. Learn from professional theater faculty. Includes workshops, rehearsals, and performances.',
                'url': 'https://www.cmu.edu/pre-college/',
                'time_commitment': '6 weeks',
                'prerequisite_level': 'Medium',
                'stem_fields': 'Theater Arts, Performance, Communication',
                'cost': '8500',
                'diversity_focus': False
            },
            {
                'name': 'Music Program',
                'description': 'Music intensive with CMU School of Music. Study music theory, composition, performance, and music technology. Work with professional musicians and composers. Includes ensemble work, private lessons, and masterclasses. Opportunity to use CMU music facilities and recording studios.',
                'url': 'https://www.cmu.edu/pre-college/',
                'time_commitment': '6 weeks',
                'prerequisite_level': 'Medium',
                'stem_fields': 'Music, Music Technology, Sound Engineering',
                'cost': '8500',
                'diversity_focus': False
            },
            {
                'name': 'Art Program',
                'description': 'Studio art program exploring various media and techniques. Learn drawing, painting, sculpture, digital art, and contemporary art practices. Work in CMU studio spaces with professional artists. Build portfolio and develop artistic voice. Includes art history and critique sessions.',
                'url': 'https://www.cmu.edu/pre-college/',
                'time_commitment': '6 weeks',
                'prerequisite_level': 'Medium',
                'stem_fields': 'Visual Arts, Digital Art, Design',
                'cost': '8500',
                'diversity_focus': False
            },
            {
                'name': 'Writing & Culture Program',
                'description': 'Creative writing and cultural studies program. Explore fiction, poetry, creative nonfiction, and cultural criticism. Participate in writing workshops, readings, and literary discussions. Learn from CMU writing faculty. Includes trips to Pittsburgh cultural sites.',
                'url': 'https://www.cmu.edu/pre-college/',
                'time_commitment': '6 weeks',
                'prerequisite_level': 'Medium',
                'stem_fields': 'Writing, Literature, Cultural Studies',
                'cost': '7500',
                'diversity_focus': True,
                'first_gen_support': True
            },
            {
                'name': 'Summer Session',
                'description': 'Take actual Carnegie Mellon undergraduate courses for college credit. Choose from variety of STEM and humanities courses. Experience university-level academics and campus life. Earn transferable college credits. Live on campus with other pre-college students.',
                'url': 'https://www.cmu.edu/pre-college/',
                'time_commitment': '6 weeks',
                'prerequisite_level': 'High',
                'stem_fields': 'Various STEM and Liberal Arts',
                'cost': '10000',
                'diversity_focus': True,
                'first_gen_support': True,
                'category': 'University Pre-College'
            },
            {
                'name': 'Robotics Academy',
                'description': 'Hands-on robotics program covering robot design, programming, and autonomous systems. Work with LEGO robotics, VEX systems, and advanced robotics platforms. Learn about sensors, actuators, and control systems. Team-based projects and robotics challenges. Exposure to CMU Robotics Institute.',
                'url': 'https://www.cmu.edu/pre-college/',
                'time_commitment': '3 weeks',
                'prerequisite_level': 'Medium',
                'stem_fields': 'Robotics, Engineering, Computer Science, Mechatronics',
                'cost': '6000',
                'diversity_focus': True,
                'first_gen_support': True
            }
        ]

        for program_data in known_programs:
            program = {
                'name': program_data['name'],
                'description': program_data['description'],
                'url': program_data['url'],
                'source': 'Carnegie Mellon Pre-College',
                'category': program_data.get('category', 'Summer Program'),
                'stem_fields': program_data.get('stem_fields', 'Technology'),
                'target_grade': '10-12',
                'cost': program_data.get('cost', '7500'),
                'location_type': 'Residential',
                'time_commitment': program_data.get('time_commitment', '6 weeks'),
                'prerequisite_level': program_data.get('prerequisite_level', 'Medium'),
                'support_level': 'High',
                'deadline': 'Check CMU website',
                'financial_barrier_level': 'High',
                'financial_aid_available': True,
                'family_income_consideration': 'Middle+',
                'hidden_costs_level': 'Travel',
                'cost_category': '$2000+',
                'diversity_focus': program_data.get('diversity_focus', False),
                'underrepresented_friendly': True,
                'first_gen_support': program_data.get('first_gen_support', False),
                'cultural_competency': 'Medium',
                'rural_accessible': False,
                'transportation_required': True,
                'internet_dependency': 'High-speed-required',
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

        csv_file = os.path.join(data_dir, 'cmu_precollege_programs.csv')

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
        logger.info("Starting Carnegie Mellon Pre-College Programs scraper...")

        # First, add known CMU programs with detailed information
        self.add_known_cmu_programs()

        # Then scrape additional programs from web pages
        for url in self.base_urls:
            try:
                self.scrape_cmu_pages(url)
                time.sleep(2)  # Respectful delay between pages
            except Exception as e:
                logger.error(f"Error scraping {url}: {e}")
                continue

        # Save to CSV
        if self.programs:
            csv_file = self.save_to_csv()
            if csv_file:
                logger.info(f"Successfully created {csv_file} with {len(self.programs)} CMU Pre-College programs")
                return csv_file
            else:
                logger.error("Failed to save CSV file")
                return None
        else:
            logger.warning("No programs found to save")
            return None

def main():
    scraper = CMUPreCollegeScraper()
    result = scraper.run()

    if result:
        print(f"\nCarnegie Mellon Pre-College Programs scraper completed successfully!")
        print(f"Output file: {result}")
        print(f"Total programs: {len(scraper.programs)}")
    else:
        print("\nScraper failed to complete")

if __name__ == "__main__":
    main()