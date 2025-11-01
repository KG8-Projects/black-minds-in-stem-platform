#!/usr/bin/env python3
"""
Khan Academy STEM Courses Scraper
Extracts K-12 STEM courses from Khan Academy
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

class KhanAcademyScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })

        self.base_urls = [
            'https://www.khanacademy.org/math',
            'https://www.khanacademy.org/science',
            'https://www.khanacademy.org/computing'
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

    def parse_stem_fields(self, course_name, url):
        """Determine STEM field from course name and URL"""
        combined_text = (course_name + " " + url).lower()

        if 'math' in url or any(term in combined_text for term in ['arithmetic', 'algebra', 'geometry', 'calculus', 'trigonometry', 'statistics']):
            return 'Mathematics'
        elif 'science' in url or any(term in combined_text for term in ['biology', 'chemistry', 'physics', 'science']):
            if 'biology' in combined_text:
                return 'Biology'
            elif 'chemistry' in combined_text:
                return 'Chemistry'
            elif 'physics' in combined_text:
                return 'Physics'
            else:
                return 'Science'
        elif 'computing' in url or any(term in combined_text for term in ['programming', 'computer', 'coding', 'javascript', 'python', 'sql']):
            return 'Computer Science'
        else:
            return 'STEM'

    def parse_target_grade(self, course_name, description):
        """Determine target grade level from course name and description"""
        combined_text = (course_name + " " + description).lower()

        if any(term in combined_text for term in ['kindergarten', 'early math', 'basic']):
            return "K-2"
        elif any(term in combined_text for term in ['elementary', 'grade 3', 'grade 4', 'grade 5', '3rd', '4th', '5th']):
            return "3-5"
        elif any(term in combined_text for term in ['middle school', 'grade 6', 'grade 7', 'grade 8', '6th', '7th', '8th', 'pre-algebra']):
            return "6-8"
        elif any(term in combined_text for term in ['algebra 1', 'geometry', 'algebra 2', 'high school']):
            return "9-10"
        elif any(term in combined_text for term in ['precalculus', 'calculus', 'ap', 'advanced']):
            return "11-12"
        elif any(term in combined_text for term in ['sat', 'college', 'university']):
            return "11-12"
        else:
            return "K-12"

    def parse_prerequisite_level(self, course_name, description):
        """Determine prerequisite level from course details"""
        combined_text = (course_name + " " + description).lower()

        if any(term in combined_text for term in ['advanced', 'calculus', 'ap', 'differential']):
            return "High"
        elif any(term in combined_text for term in ['intermediate', 'algebra', 'geometry', 'chemistry', 'physics']):
            return "Medium"
        elif any(term in combined_text for term in ['basic', 'intro', 'elementary', 'beginner', 'fundamentals']):
            return "None"
        else:
            return "Basic"

    def scrape_khan_pages(self, url):
        """Scrape courses from Khan Academy pages"""
        soup = self.fetch_page(url)
        if not soup:
            return

        programs_found = 0

        # Look for course information
        course_selectors = [
            'div.course-card', 'div.course', 'article.course',
            'a[class*="course"]', 'div[class*="link"]',
            '.content-area', 'main'
        ]

        course_elements = []
        for selector in course_selectors:
            elements = soup.select(selector)
            if elements:
                course_elements.extend(elements[:30])
                break

        # If no specific containers found, look for headings and links
        if not course_elements:
            links = soup.find_all('a', href=True)
            for link in links[:50]:
                link_text = self.extract_text_safely(link)
                href = link.get('href', '')
                if len(link_text) > 5 and any(term in href for term in ['/math/', '/science/', '/computing/']):
                    course_elements.append(link)

        # Process found elements
        for element in course_elements[:30]:
            try:
                # Extract course name
                if element.name == 'a':
                    name = self.extract_text_safely(element)
                    href = element.get('href', '')
                else:
                    name_elem = (element.find('a') or
                               element.find(['h1', 'h2', 'h3', 'h4']) or
                               element.find('strong'))
                    if not name_elem:
                        continue
                    name = self.extract_text_safely(name_elem)
                    href = element.get('href', '') or (name_elem.get('href', '') if name_elem.name == 'a' else '')

                if not name or len(name) < 3 or len(name) > 200:
                    continue

                # Skip navigation or irrelevant content
                if any(skip_term in name.lower() for skip_term in ['menu', 'navigation', 'login', 'sign up', 'donate', 'help', 'about', 'contact']):
                    continue

                # Skip if it doesn't look like a Khan Academy course
                if not any(term in name.lower() for term in ['math', 'algebra', 'geometry', 'calculus', 'science', 'biology', 'chemistry', 'physics', 'programming', 'computer', 'grade', 'elementary', 'statistics', 'trigonometry', 'arithmetic']):
                    continue

                # Extract description
                description = ""
                if element.name != 'a':
                    paragraphs = element.find_all('p')
                    if paragraphs:
                        desc_texts = [self.extract_text_safely(p) for p in paragraphs[:2]]
                        description = " ".join([d for d in desc_texts if d and len(d) > 15])

                if not description:
                    description = f"Khan Academy course: {name}. Free online learning with videos, exercises, and practice problems."

                # Construct full URL
                course_url = urljoin(url, href) if href else url

                # Create program entry
                program = {
                    'name': name,
                    'description': (description[:500] if description else
                                  f"Khan Academy: {name}"),
                    'url': course_url,
                    'source': 'Khan Academy',
                    'category': 'Online Course',
                    'stem_fields': self.parse_stem_fields(name, url),
                    'target_grade': self.parse_target_grade(name, description),
                    'cost': 'Free',
                    'location_type': 'Online',
                    'time_commitment': 'Self-paced',
                    'prerequisite_level': self.parse_prerequisite_level(name, description),
                    'support_level': 'Medium',
                    'deadline': 'None',
                    'financial_barrier_level': 'None',
                    'financial_aid_available': False,
                    'family_income_consideration': False,
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
                    'family_involvement_required': 'Optional',
                    'peer_network_building': False,
                    'mentor_access_level': 'None'
                }

                # Avoid duplicates
                if not any(p['name'].lower() == program['name'].lower() for p in self.programs):
                    self.programs.append(program)
                    programs_found += 1
                    logger.info(f"Added program: {name}")

            except Exception as e:
                logger.error(f"Error processing course element: {e}")
                continue

        logger.info(f"Found {programs_found} programs from {url}")

    def add_known_khan_courses(self):
        """Add well-known Khan Academy courses with detailed information"""
        known_programs = [
            # Math Courses
            {
                'name': 'Khan Academy Early Math',
                'description': 'Foundational math skills for young learners including counting, addition, subtraction, shapes, and measurement. Interactive exercises and videos. Builds number sense and mathematical thinking. Kindergarten through 2nd grade content.',
                'url': 'https://www.khanacademy.org/math',
                'stem_fields': 'Mathematics',
                'target_grade': 'K-2',
                'prerequisite_level': 'None'
            },
            {
                'name': 'Khan Academy Arithmetic',
                'description': 'Core arithmetic skills including addition, subtraction, multiplication, division, fractions, and decimals. Practice exercises with instant feedback. Mastery-based progression. Elementary and middle school mathematics fundamentals.',
                'url': 'https://www.khanacademy.org/math',
                'stem_fields': 'Mathematics',
                'target_grade': '3-6',
                'prerequisite_level': 'Basic'
            },
            {
                'name': 'Khan Academy Pre-Algebra',
                'description': 'Pre-algebra topics including negative numbers, exponents, order of operations, variables, and equations. Prepares students for algebra. Interactive practice and instructional videos. Middle school mathematics.',
                'url': 'https://www.khanacademy.org/math',
                'stem_fields': 'Mathematics',
                'target_grade': '7-8',
                'prerequisite_level': 'Basic'
            },
            {
                'name': 'Khan Academy Algebra 1',
                'description': 'Complete Algebra 1 curriculum including linear equations, inequalities, functions, polynomials, and quadratic equations. Aligned with Common Core standards. Videos, practice problems, and assessments. High school mathematics.',
                'url': 'https://www.khanacademy.org/math',
                'stem_fields': 'Mathematics',
                'target_grade': '9-10',
                'prerequisite_level': 'Medium'
            },
            {
                'name': 'Khan Academy Geometry',
                'description': 'Comprehensive geometry course covering angles, triangles, circles, polygons, coordinate geometry, and geometric proofs. Interactive constructions and problem-solving. Aligned with high school geometry standards.',
                'url': 'https://www.khanacademy.org/math',
                'stem_fields': 'Mathematics',
                'target_grade': '9-10',
                'prerequisite_level': 'Medium'
            },
            {
                'name': 'Khan Academy Algebra 2',
                'description': 'Advanced algebra topics including polynomials, rational expressions, exponential and logarithmic functions, trigonometry, and complex numbers. Prepares for precalculus. High school mathematics.',
                'url': 'https://www.khanacademy.org/math',
                'stem_fields': 'Mathematics',
                'target_grade': '10-11',
                'prerequisite_level': 'High'
            },
            {
                'name': 'Khan Academy Trigonometry',
                'description': 'Trigonometric functions, identities, equations, and applications. Right triangle trigonometry, unit circle, graphs, and laws of sines and cosines. Essential for calculus preparation.',
                'url': 'https://www.khanacademy.org/math',
                'stem_fields': 'Mathematics',
                'target_grade': '10-11',
                'prerequisite_level': 'High'
            },
            {
                'name': 'Khan Academy Precalculus',
                'description': 'Pre-calculus topics including functions, conic sections, vectors, matrices, series, and limits. Prepares students for AP Calculus. Advanced high school mathematics.',
                'url': 'https://www.khanacademy.org/math',
                'stem_fields': 'Mathematics',
                'target_grade': '11-12',
                'prerequisite_level': 'High'
            },
            {
                'name': 'Khan Academy AP Calculus AB',
                'description': 'Complete AP Calculus AB curriculum including limits, derivatives, integrals, and Fundamental Theorem of Calculus. Practice problems aligned with AP exam. Video lessons and test preparation.',
                'url': 'https://www.khanacademy.org/math',
                'stem_fields': 'Mathematics',
                'target_grade': '11-12',
                'prerequisite_level': 'High'
            },
            {
                'name': 'Khan Academy AP Calculus BC',
                'description': 'Advanced calculus topics including series, parametric equations, polar coordinates, and advanced integration techniques. Full AP Calculus BC curriculum. College-level mathematics.',
                'url': 'https://www.khanacademy.org/math',
                'stem_fields': 'Mathematics',
                'target_grade': '11-12',
                'prerequisite_level': 'High'
            },
            {
                'name': 'Khan Academy Statistics and Probability',
                'description': 'Introduction to statistics and probability including data analysis, probability theory, distributions, inference, and hypothesis testing. Real-world applications and data interpretation.',
                'url': 'https://www.khanacademy.org/math',
                'stem_fields': 'Mathematics',
                'target_grade': '9-12',
                'prerequisite_level': 'Medium'
            },
            # Science Courses
            {
                'name': 'Khan Academy Biology',
                'description': 'Comprehensive biology course covering cells, genetics, evolution, ecology, human biology, and biochemistry. Aligned with high school and AP Biology standards. Interactive diagrams and practice.',
                'url': 'https://www.khanacademy.org/science',
                'stem_fields': 'Biology',
                'target_grade': '9-12',
                'prerequisite_level': 'Basic'
            },
            {
                'name': 'Khan Academy Chemistry',
                'description': 'High school chemistry covering atoms, molecules, chemical reactions, stoichiometry, thermodynamics, and equilibrium. Laboratory concepts and problem-solving. Aligned with chemistry standards.',
                'url': 'https://www.khanacademy.org/science',
                'stem_fields': 'Chemistry',
                'target_grade': '10-12',
                'prerequisite_level': 'Medium'
            },
            {
                'name': 'Khan Academy Physics',
                'description': 'Physics fundamentals including motion, forces, energy, waves, electricity, and magnetism. Problem-solving with real-world applications. Aligned with high school physics standards.',
                'url': 'https://www.khanacademy.org/science',
                'stem_fields': 'Physics',
                'target_grade': '10-12',
                'prerequisite_level': 'Medium'
            },
            # Computing Courses
            {
                'name': 'Khan Academy Computer Programming',
                'description': 'Introduction to programming using JavaScript. Learn coding fundamentals including variables, functions, loops, and arrays through interactive projects. Create drawings, animations, and games.',
                'url': 'https://www.khanacademy.org/computing',
                'stem_fields': 'Computer Science',
                'target_grade': '6-12',
                'prerequisite_level': 'None'
            },
            {
                'name': 'Khan Academy HTML/CSS',
                'description': 'Web development basics covering HTML structure, CSS styling, and responsive design. Build webpages and understand web technologies. Hands-on projects creating websites.',
                'url': 'https://www.khanacademy.org/computing',
                'stem_fields': 'Computer Science',
                'target_grade': '6-12',
                'prerequisite_level': 'None'
            },
            {
                'name': 'Khan Academy SQL',
                'description': 'Database fundamentals and SQL programming. Learn to query, manipulate, and manage data. Relational database concepts and practical database skills.',
                'url': 'https://www.khanacademy.org/computing',
                'stem_fields': 'Computer Science',
                'target_grade': '9-12',
                'prerequisite_level': 'Basic'
            },
            {
                'name': 'Khan Academy Computer Science Principles',
                'description': 'AP Computer Science Principles curriculum covering programming, internet, data, and impacts of computing. Aligned with AP CSP exam. Develops computational thinking.',
                'url': 'https://www.khanacademy.org/computing',
                'stem_fields': 'Computer Science',
                'target_grade': '9-12',
                'prerequisite_level': 'Basic'
            },
            {
                'name': 'Khan Academy Algorithms',
                'description': 'Introduction to algorithms including sorting, searching, graph algorithms, and algorithm analysis. Computational problem-solving and efficiency. Computer science fundamentals.',
                'url': 'https://www.khanacademy.org/computing',
                'stem_fields': 'Computer Science',
                'target_grade': '10-12',
                'prerequisite_level': 'Medium'
            },
            {
                'name': 'Khan Academy Cryptography',
                'description': 'Introduction to cryptography covering encryption, decryption, ciphers, and cryptographic protocols. Historical and modern cryptography. Internet security concepts.',
                'url': 'https://www.khanacademy.org/computing',
                'stem_fields': 'Computer Science',
                'target_grade': '9-12',
                'prerequisite_level': 'Medium'
            }
        ]

        for program_data in known_programs:
            program = {
                'name': program_data['name'],
                'description': program_data['description'],
                'url': program_data['url'],
                'source': 'Khan Academy',
                'category': 'Online Course',
                'stem_fields': program_data.get('stem_fields', 'STEM'),
                'target_grade': program_data.get('target_grade', 'K-12'),
                'cost': 'Free',
                'location_type': 'Online',
                'time_commitment': 'Self-paced',
                'prerequisite_level': program_data.get('prerequisite_level', 'Basic'),
                'support_level': 'Medium',
                'deadline': 'None',
                'financial_barrier_level': 'None',
                'financial_aid_available': False,
                'family_income_consideration': False,
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
        data_dir = 'data'
        os.makedirs(data_dir, exist_ok=True)

        csv_file = os.path.join(data_dir, 'khan_academy_programs.csv')

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
        logger.info("Starting Khan Academy STEM Courses scraper...")

        # First, add known Khan Academy courses with detailed information
        self.add_known_khan_courses()

        # Then scrape additional programs from web pages
        for url in self.base_urls:
            try:
                self.scrape_khan_pages(url)
                time.sleep(2)  # Respectful delay between pages
            except Exception as e:
                logger.error(f"Error scraping {url}: {e}")
                continue

        # Save to CSV
        if self.programs:
            csv_file = self.save_to_csv()
            if csv_file:
                logger.info(f"Successfully created {csv_file} with {len(self.programs)} Khan Academy courses")
                return csv_file
            else:
                logger.error("Failed to save CSV file")
                return None
        else:
            logger.warning("No programs found to save")
            return None

def main():
    scraper = KhanAcademyScraper()
    result = scraper.run()

    if result:
        print(f"\nKhan Academy STEM Courses scraper completed successfully!")
        print(f"Output file: {result}")
        print(f"Total courses: {len(scraper.programs)}")
    else:
        print("\nScraper failed to complete")

if __name__ == "__main__":
    main()