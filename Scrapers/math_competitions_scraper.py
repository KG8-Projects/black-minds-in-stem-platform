#!/usr/bin/env python3
"""
Math Competitions Scraper
Extracts K-12 mathematics competitions from various organizations
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

class MathCompetitionsScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })

        self.base_urls = [
            'https://www.maa.org/math-competitions',
            'https://www.mathleague.com/',
            'https://www.artofproblemsolving.com/wiki/index.php/Mathematics_competitions'
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

    def parse_source(self, url, competition_name):
        """Determine source organization"""
        if 'maa.org' in url or any(term in competition_name.lower() for term in ['amc', 'aime', 'usamo', 'usajmo']):
            return 'Mathematical Association of America'
        elif 'mathleague.com' in url or 'math league' in competition_name.lower():
            return 'Math League'
        elif 'mathcounts' in competition_name.lower():
            return 'MATHCOUNTS'
        elif 'moems' in competition_name.lower() or 'olympiad' in competition_name.lower():
            return 'Math Olympiads'
        else:
            return 'Mathematics Competitions'

    def parse_target_grade(self, competition_name, description):
        """Determine target grade level"""
        combined_text = (competition_name + " " + description).lower()

        if any(term in combined_text for term in ['grade 8', '8th grade', 'middle school only', 'amc 8']):
            return "6-8"
        elif any(term in combined_text for term in ['grade 10', '10th grade', 'amc 10', 'usajmo']):
            return "9-10"
        elif any(term in combined_text for term in ['grade 12', '12th grade', 'amc 12', 'usamo']):
            return "9-12"
        elif any(term in combined_text for term in ['grades 10, 11, and 12', 'high school']):
            return "10-12"
        elif any(term in combined_text for term in ['grades 8 and 9', 'grade 9']):
            return "8-9"
        elif any(term in combined_text for term in ['grade 7', '7th grade']):
            return "7"
        elif any(term in combined_text for term in ['grade 6', '6th grade']):
            return "6"
        elif any(term in combined_text for term in ['grade 5', '5th grade']):
            return "5"
        elif any(term in combined_text for term in ['grade 4', '4th grade']):
            return "4"
        elif any(term in combined_text for term in ['grade 3', '3rd grade']):
            return "3"
        elif any(term in combined_text for term in ['elementary', 'k-5']):
            return "K-5"
        else:
            return "6-12"  # Default

    def parse_cost(self, competition_name, description):
        """Extract cost information"""
        combined_text = (competition_name + " " + description).lower()

        # Look for dollar amounts
        cost_patterns = [
            r'\$(\d+)',
            r'(\d+)\s*dollars?'
        ]

        for pattern in cost_patterns:
            match = re.search(pattern, description)
            if match:
                return match.group(1)

        if any(term in combined_text for term in ['free', 'no cost', 'no fee']):
            return "Free"
        else:
            return "30"  # Typical competition registration fee

    def parse_prerequisite_level(self, competition_name, description):
        """Determine prerequisite level"""
        combined_text = (competition_name + " " + description).lower()

        if any(term in combined_text for term in ['usamo', 'usajmo', 'aime', 'invitation', 'qualify', 'top scorer']):
            return "High"
        elif any(term in combined_text for term in ['amc 12', 'advanced', 'challenging']):
            return "High"
        elif any(term in combined_text for term in ['amc 10', 'intermediate']):
            return "Medium"
        else:
            return "Medium"  # Math competitions require preparation

    def parse_time_commitment(self, competition_name, description):
        """Extract time commitment"""
        combined_text = (competition_name + " " + description).lower()

        if any(term in combined_text for term in ['75 minutes', '75-minute']):
            return "75 minutes"
        elif any(term in combined_text for term in ['60 minutes', '60-minute', '1 hour']):
            return "60 minutes"
        elif any(term in combined_text for term in ['45 minutes', '45-minute']):
            return "45 minutes"
        elif any(term in combined_text for term in ['4.5 hours', '4.5-hour', 'two day', '2-day']):
            return "2 days"
        else:
            return "Competition day"

    def scrape_math_pages(self, url):
        """Scrape competitions from math pages"""
        soup = self.fetch_page(url)
        if not soup:
            return

        programs_found = 0

        # Look for competition information
        competition_selectors = [
            'div.competition-card', 'div.competition', 'article.competition',
            '.content-area', 'main', 'div.main-content',
            'div[class*="competition"]', 'div[class*="contest"]'
        ]

        competition_elements = []
        for selector in competition_selectors:
            elements = soup.select(selector)
            if elements:
                competition_elements.extend(elements[:20])
                break

        # If no specific containers found, look for headings
        if not competition_elements:
            headings = soup.find_all(['h1', 'h2', 'h3', 'h4'])
            for heading in headings[:25]:
                heading_text = self.extract_text_safely(heading).lower()
                if any(term in heading_text for term in ['amc', 'aime', 'usamo', 'math', 'competition', 'contest', 'olympiad', 'league', 'grade']) and len(heading_text) > 3:
                    content_section = heading.parent or heading.find_next_sibling()
                    if content_section:
                        competition_elements.append(content_section)

        # Process found elements
        for element in competition_elements[:20]:
            try:
                # Extract competition name
                name_elem = (element.find(['h1', 'h2', 'h3', 'h4']) or
                           element.select_one('.title, .competition-title, .name') or
                           element.find('strong') or element.find('b'))

                if not name_elem:
                    continue

                name = self.extract_text_safely(name_elem)
                if not name or len(name) < 3 or len(name) > 200:
                    continue

                # Skip navigation or irrelevant content
                if any(skip_term in name.lower() for skip_term in ['menu', 'navigation', 'home', 'about', 'contact', 'login', 'search', 'header', 'footer']):
                    continue

                # Skip if it doesn't look like a math competition
                if not any(term in name.lower() for term in ['amc', 'aime', 'usamo', 'math', 'competition', 'contest', 'olympiad', 'league', 'grade', 'challenge']):
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
                    description = f"Mathematics competition: {name}. Test mathematical problem-solving skills."

                # Create program entry
                program = {
                    'name': name,
                    'description': (description[:500] if description else
                                  f"Math competition: {name}"),
                    'url': url,
                    'source': self.parse_source(url, name),
                    'category': 'Math Competition',
                    'stem_fields': 'Mathematics',
                    'target_grade': self.parse_target_grade(name, description),
                    'cost': self.parse_cost(name, description),
                    'location_type': 'School-based',
                    'time_commitment': self.parse_time_commitment(name, description),
                    'prerequisite_level': self.parse_prerequisite_level(name, description),
                    'support_level': 'Medium',
                    'deadline': 'Check competition website',
                    'financial_barrier_level': 'Low',
                    'financial_aid_available': False,
                    'family_income_consideration': False,
                    'hidden_costs_level': 'Low',
                    'cost_category': 'Free',
                    'diversity_focus': False,
                    'underrepresented_friendly': True,
                    'first_gen_support': False,
                    'cultural_competency': 'Medium',
                    'rural_accessible': True,
                    'transportation_required': False,
                    'internet_dependency': 'Basic',
                    'regional_availability': 'National',
                    'family_involvement_required': 'Optional',
                    'peer_network_building': True,
                    'mentor_access_level': 'Adult'
                }

                # Avoid duplicates
                if not any(p['name'].lower() == program['name'].lower() for p in self.programs):
                    self.programs.append(program)
                    programs_found += 1
                    logger.info(f"Added program: {name}")

            except Exception as e:
                logger.error(f"Error processing competition element: {e}")
                continue

        logger.info(f"Found {programs_found} programs from {url}")

    def add_known_math_competitions(self):
        """Add well-known math competitions with detailed information"""
        known_programs = [
            {
                'name': 'AMC 8',
                'description': '25-question, 40-minute multiple choice examination in middle school mathematics designed to promote development of problem-solving skills. Open to students in grade 8 and below. Covers topics from Pre-Algebra curriculum. Administered in November. No calculator permitted.',
                'url': 'https://www.maa.org/math-competitions',
                'source': 'Mathematical Association of America',
                'target_grade': '6-8',
                'cost': '20',
                'time_commitment': '40 minutes',
                'prerequisite_level': 'Medium'
            },
            {
                'name': 'AMC 10',
                'description': '25-question, 75-minute multiple choice examination covering topics from a typical pre-calculus curriculum. For students in grade 10 and below. Administered in February. Tests mathematical problem-solving with applications of secondary school competencies. No calculator permitted.',
                'url': 'https://www.maa.org/math-competitions',
                'source': 'Mathematical Association of America',
                'target_grade': '9-10',
                'cost': '30',
                'time_commitment': '75 minutes',
                'prerequisite_level': 'Medium'
            },
            {
                'name': 'AMC 12',
                'description': '25-question, 75-minute multiple choice examination in secondary school mathematics containing problems which can be understood and solved with pre-calculus concepts. For students in grade 12 and below. Administered in February. Top scorers invited to AIME. No calculator permitted.',
                'url': 'https://www.maa.org/math-competitions',
                'source': 'Mathematical Association of America',
                'target_grade': '9-12',
                'cost': '30',
                'time_commitment': '75 minutes',
                'prerequisite_level': 'High'
            },
            {
                'name': 'AIME (American Invitational Mathematics Examination)',
                'description': '15-question, 3-hour examination where each answer is an integer from 0 to 999. Invitation-only for top scorers on AMC 10/12. Covers topics through pre-calculus. Administered in March. Gateway to USAMO/USAJMO. Significantly more challenging than AMC.',
                'url': 'https://www.maa.org/math-competitions',
                'source': 'Mathematical Association of America',
                'target_grade': '9-12',
                'cost': '20',
                'time_commitment': '3 hours',
                'prerequisite_level': 'High'
            },
            {
                'name': 'USAMO (United States of America Mathematical Olympiad)',
                'description': 'Premier mathematics competition for high school students. 6-question, 9-hour proof-based examination over two days. Invitation-only for top AIME performers. Extremely challenging problems requiring creative solutions. Top performers invited to Mathematical Olympiad Program.',
                'url': 'https://www.maa.org/math-competitions',
                'source': 'Mathematical Association of America',
                'target_grade': '9-12',
                'cost': 'Free',
                'time_commitment': '2 days',
                'prerequisite_level': 'High'
            },
            {
                'name': 'USAJMO (United States of America Junior Mathematical Olympiad)',
                'description': 'Proof-based mathematics competition for top middle school and early high school students. 6-question, 9-hour examination over two days. Invitation-only for top AMC 10 performers. Challenging problems requiring rigorous mathematical reasoning and proof writing.',
                'url': 'https://www.maa.org/math-competitions',
                'source': 'Mathematical Association of America',
                'target_grade': '9-10',
                'cost': 'Free',
                'time_commitment': '2 days',
                'prerequisite_level': 'High'
            },
            {
                'name': 'Math League High School Contest',
                'description': 'Annual series of 6 contests for high school students. Each contest consists of 6 questions, 30 minutes. Short answer format testing problem-solving and mathematical reasoning. School-based competition with individual and team scoring. Results compiled nationally.',
                'url': 'https://www.mathleague.com/',
                'source': 'Math League',
                'target_grade': '9-12',
                'cost': '66',
                'time_commitment': '30 minutes per contest',
                'prerequisite_level': 'Medium'
            },
            {
                'name': 'Math League Middle School Contest',
                'description': 'Contest series for grades 6-8 featuring problem-solving challenges. Multiple rounds throughout academic year. Short answer format with individual and team competitions. Develops mathematical thinking and competition skills. School-based administration.',
                'url': 'https://www.mathleague.com/',
                'source': 'Math League',
                'target_grade': '6-8',
                'cost': '66',
                'time_commitment': '45 minutes per contest',
                'prerequisite_level': 'Medium'
            },
            {
                'name': 'Math League Elementary Contests',
                'description': 'Mathematics competitions for elementary students in grades 3-6. Age-appropriate problem-solving challenges. Multiple contests per year. Builds mathematical confidence and competition experience. Individual and team scoring formats.',
                'url': 'https://www.mathleague.com/',
                'source': 'Math League',
                'target_grade': '3-6',
                'cost': '66',
                'time_commitment': '30 minutes per contest',
                'prerequisite_level': 'Basic'
            },
            {
                'name': 'MOEMS (Math Olympiads for Elementary and Middle Schools)',
                'description': 'Contest program for students in grades 4-8 featuring 5 monthly contests. Each contest has 5 non-routine problems, 30 minutes. Promotes mathematical problem-solving and fosters enthusiasm for mathematics. School or homeschool team participation.',
                'url': 'https://www.moems.org/',
                'source': 'Math Olympiads',
                'target_grade': '4-8',
                'cost': '99',
                'time_commitment': '30 minutes monthly',
                'prerequisite_level': 'Medium'
            },
            {
                'name': 'Purple Comet Math Meet',
                'description': 'Free online international mathematics competition for middle and high school teams. 25 problems, 60 minutes. Team-based problem solving. Held annually in April. Teams of up to 6 students collaborate. Results posted online immediately after competition.',
                'url': 'https://purplecomet.org/',
                'source': 'Purple Comet',
                'target_grade': '6-12',
                'cost': 'Free',
                'time_commitment': '60 minutes',
                'prerequisite_level': 'Medium',
                'location_type': 'Online'
            },
            {
                'name': 'ARML (American Regions Mathematics League)',
                'description': 'Annual team mathematics competition with regional and national competitions. Teams of 15 students. Individual, relay, team, and power rounds. Challenging problems requiring collaboration. Regional qualifying competitions leading to national championship.',
                'url': 'https://www.arml.com/',
                'source': 'ARML',
                'target_grade': '9-12',
                'cost': 'Varies',
                'time_commitment': '1 day',
                'prerequisite_level': 'High',
                'location_type': 'In-person'
            },
            {
                'name': 'Mathlete',
                'description': 'Individual mathematics coaching and competition program. Online practice problems and competitions. Personalized problem sets adapting to student level. Monthly competitions with instant results. Develops problem-solving skills through regular practice.',
                'url': 'https://www.mathlete.com/',
                'source': 'Mathlete',
                'target_grade': 'K-12',
                'cost': '50',
                'time_commitment': 'Monthly competitions',
                'prerequisite_level': 'Basic',
                'location_type': 'Online'
            },
            {
                'name': 'Math Kangaroo',
                'description': 'International mathematics competition with over 6 million participants worldwide. Multiple choice format, 75 minutes. Levels from grades 1-12. Encourages mathematical thinking for students of all ability levels. Administered annually in March.',
                'url': 'https://www.mathkangaroo.org/',
                'source': 'Math Kangaroo',
                'target_grade': 'K-12',
                'cost': '20',
                'time_commitment': '75 minutes',
                'prerequisite_level': 'Basic'
            },
            {
                'name': 'MathPath Summer Program',
                'description': 'Intensive 4-week residential summer mathematics program for talented middle school students. Proof-based mathematics, problem-solving, and mathematical exploration. Small seminar-style classes. Guest lectures and mathematical activities. Highly selective.',
                'url': 'https://mathpath.org/',
                'source': 'MathPath',
                'target_grade': '6-8',
                'cost': '4500',
                'time_commitment': '4 weeks',
                'prerequisite_level': 'High',
                'location_type': 'Residential',
                'category': 'Math Program'
            }
        ]

        for program_data in known_programs:
            program = {
                'name': program_data['name'],
                'description': program_data['description'],
                'url': program_data['url'],
                'source': program_data.get('source', 'Mathematics Competitions'),
                'category': program_data.get('category', 'Math Competition'),
                'stem_fields': 'Mathematics',
                'target_grade': program_data.get('target_grade', '6-12'),
                'cost': program_data.get('cost', '30'),
                'location_type': program_data.get('location_type', 'School-based'),
                'time_commitment': program_data.get('time_commitment', 'Competition day'),
                'prerequisite_level': program_data.get('prerequisite_level', 'Medium'),
                'support_level': 'Medium',
                'deadline': 'Check competition website',
                'financial_barrier_level': 'Low',
                'financial_aid_available': False,
                'family_income_consideration': False,
                'hidden_costs_level': 'Low',
                'cost_category': 'Free',
                'diversity_focus': False,
                'underrepresented_friendly': True,
                'first_gen_support': False,
                'cultural_competency': 'Medium',
                'rural_accessible': True,
                'transportation_required': False if program_data.get('location_type', 'School-based') in ['School-based', 'Online'] else True,
                'internet_dependency': 'High-speed-required' if program_data.get('location_type', 'School-based') == 'Online' else 'Basic',
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
        data_dir = 'data'
        os.makedirs(data_dir, exist_ok=True)

        csv_file = os.path.join(data_dir, 'math_competitions.csv')

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
        logger.info("Starting Math Competitions scraper...")

        # First, add known math competitions with detailed information
        self.add_known_math_competitions()

        # Then scrape additional programs from web pages
        for url in self.base_urls:
            try:
                self.scrape_math_pages(url)
                time.sleep(2)  # Respectful delay between pages
            except Exception as e:
                logger.error(f"Error scraping {url}: {e}")
                continue

        # Save to CSV
        if self.programs:
            csv_file = self.save_to_csv()
            if csv_file:
                logger.info(f"Successfully created {csv_file} with {len(self.programs)} math competitions")
                return csv_file
            else:
                logger.error("Failed to save CSV file")
                return None
        else:
            logger.warning("No programs found to save")
            return None

def main():
    scraper = MathCompetitionsScraper()
    result = scraper.run()

    if result:
        print(f"\nMath Competitions scraper completed successfully!")
        print(f"Output file: {result}")
        print(f"Total competitions: {len(scraper.programs)}")
    else:
        print("\nScraper failed to complete")

if __name__ == "__main__":
    main()