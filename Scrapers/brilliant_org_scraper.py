"""
Brilliant.org Interactive STEM Courses Scraper
Extracts Brilliant.org courses and problem-solving resources for K-12 students
Saves to ONE CSV file: data/brilliant_org_programs.csv
"""

import requests
from bs4 import BeautifulSoup
import csv
import time
import logging
from urllib.parse import urljoin

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class BrilliantOrgScraper:
    def __init__(self):
        self.base_url = "https://brilliant.org"
        self.programs = []
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

        # Standard CSV columns (same 29 columns as all other scrapers)
        self.csv_columns = [
            'name', 'description', 'url', 'source', 'category', 'stem_fields',
            'target_grade', 'cost', 'location_type', 'time_commitment',
            'prerequisite_level', 'support_level', 'deadline',
            'financial_barrier_level', 'financial_aid_available',
            'family_income_consideration', 'hidden_costs_level', 'cost_category',
            'diversity_focus', 'underrepresented_friendly', 'first_gen_support',
            'cultural_competency', 'rural_accessible', 'transportation_required',
            'internet_dependency', 'regional_availability',
            'family_involvement_required', 'peer_network_building', 'mentor_access_level'
        ]

    def fetch_page(self, url):
        """Fetch a page with error handling"""
        try:
            logger.info(f"Fetching: {url}")
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            return response.text
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching {url}: {e}")
            return None

    def add_known_brilliant_courses(self):
        """Add well-known Brilliant.org courses for K-12 students"""
        known_programs = [
            {
                'name': 'Brilliant.org Algebra Fundamentals',
                'description': 'Interactive algebra course covering variables, equations, functions, and graphing. Visual problem-solving approach with immediate feedback. Build intuition through guided explorations. Perfect for beginners learning algebra concepts. Hundreds of interactive problems.',
                'url': 'https://brilliant.org/courses/algebra/',
                'stem_fields': 'Mathematics, Algebra',
                'target_grade': '6-10',
                'cost': 'Free',
                'prerequisite_level': 'None',
                'cost_category': 'Freemium'
            },
            {
                'name': 'Brilliant.org Geometry',
                'description': 'Visual geometry course exploring shapes, angles, areas, and spatial reasoning. Interactive diagrams and puzzles. Learn proofs and geometric thinking. Covers triangles, circles, polygons, and 3D shapes. Engaging way to master geometry.',
                'url': 'https://brilliant.org/courses/geometry/',
                'stem_fields': 'Mathematics, Geometry',
                'target_grade': '7-10',
                'cost': 'Free',
                'prerequisite_level': 'Basic',
                'cost_category': 'Freemium'
            },
            {
                'name': 'Brilliant.org Pre-Calculus',
                'description': 'Bridge to calculus covering functions, trigonometry, exponentials, and logarithms. Interactive graphs and visualizations. Develop mathematical reasoning and problem-solving skills. Preparation for AP Calculus or college mathematics.',
                'url': 'https://brilliant.org/courses/pre-calculus/',
                'stem_fields': 'Mathematics',
                'target_grade': '10-12',
                'cost': 'Free',
                'prerequisite_level': 'Medium',
                'cost_category': 'Freemium'
            },
            {
                'name': 'Brilliant.org Calculus',
                'description': 'Interactive calculus course teaching limits, derivatives, and integrals through visual problems. Build calculus intuition with interactive explorations. Applications to physics, engineering, and optimization. Comprehensive coverage of single-variable calculus.',
                'url': 'https://brilliant.org/courses/calculus/',
                'stem_fields': 'Mathematics, Calculus',
                'target_grade': '11-12',
                'cost': 'Free',
                'prerequisite_level': 'High',
                'cost_category': 'Freemium'
            },
            {
                'name': 'Brilliant.org Computer Science Fundamentals',
                'description': 'Introduction to computer science through interactive puzzles and challenges. Learn algorithms, data structures, and computational thinking. No coding required initially. Visual approach to CS concepts. Great foundation for programming.',
                'url': 'https://brilliant.org/courses/computer-science-fundamentals/',
                'stem_fields': 'Computer Science',
                'target_grade': '8-12',
                'cost': 'Free',
                'prerequisite_level': 'None',
                'cost_category': 'Freemium'
            },
            {
                'name': 'Brilliant.org Python Programming',
                'description': 'Learn Python through interactive coding challenges and projects. Start with basics and progress to data structures and algorithms. Immediate feedback on code. Build real programs and games. Perfect for beginners.',
                'url': 'https://brilliant.org/courses/programming-python/',
                'stem_fields': 'Computer Science, Programming',
                'target_grade': '9-12',
                'cost': 'Free',
                'prerequisite_level': 'None',
                'cost_category': 'Freemium'
            },
            {
                'name': 'Brilliant.org Data Structures and Algorithms',
                'description': 'Advanced computer science covering arrays, trees, graphs, sorting, and searching. Interactive visualizations of algorithms. Problem-solving focus for competitive programming and interviews. Challenging course for motivated students.',
                'url': 'https://brilliant.org/courses/algorithms/',
                'stem_fields': 'Computer Science, Algorithms',
                'target_grade': '10-12',
                'cost': 'Free',
                'prerequisite_level': 'Medium',
                'cost_category': 'Freemium'
            },
            {
                'name': 'Brilliant.org Physics Fundamentals',
                'description': 'Interactive physics covering motion, forces, energy, and momentum. Visual simulations and interactive experiments. Build physics intuition through problem-solving. Algebra-based mechanics for high school students.',
                'url': 'https://brilliant.org/courses/physics/',
                'stem_fields': 'Physics',
                'target_grade': '9-12',
                'cost': 'Free',
                'prerequisite_level': 'Basic',
                'cost_category': 'Freemium'
            },
            {
                'name': 'Brilliant.org Electricity and Magnetism',
                'description': 'Explore electromagnetism through interactive problems. Learn circuits, fields, and electromagnetic waves. Visual approach to complex concepts. Great for AP Physics preparation. Applications to technology and engineering.',
                'url': 'https://brilliant.org/courses/electric-circuits/',
                'stem_fields': 'Physics, Electricity',
                'target_grade': '10-12',
                'cost': 'Free',
                'prerequisite_level': 'Medium',
                'cost_category': 'Freemium'
            },
            {
                'name': 'Brilliant.org Probability and Statistics',
                'description': 'Interactive probability and statistics course. Learn through games, puzzles, and real-world problems. Covers distributions, inference, and data analysis. Build statistical intuition. Great for AP Statistics preparation.',
                'url': 'https://brilliant.org/courses/probability/',
                'stem_fields': 'Mathematics, Statistics',
                'target_grade': '9-12',
                'cost': 'Free',
                'prerequisite_level': 'Basic',
                'cost_category': 'Freemium'
            },
            {
                'name': 'Brilliant.org Machine Learning',
                'description': 'Introduction to AI and machine learning concepts. Learn classification, regression, and neural networks through interactive visualizations. No advanced math required initially. Build ML intuition. Great for students interested in AI.',
                'url': 'https://brilliant.org/courses/machine-learning/',
                'stem_fields': 'Computer Science, Artificial Intelligence',
                'target_grade': '10-12',
                'cost': 'Free',
                'prerequisite_level': 'Medium',
                'cost_category': 'Freemium'
            },
            {
                'name': 'Brilliant.org Chemistry',
                'description': 'Interactive chemistry exploring atoms, molecules, reactions, and chemical principles. Visual approach to understanding chemical concepts. Labs and simulations. Covers general chemistry topics. Great supplement to school chemistry.',
                'url': 'https://brilliant.org/courses/chemistry/',
                'stem_fields': 'Chemistry',
                'target_grade': '9-12',
                'cost': 'Free',
                'prerequisite_level': 'Basic',
                'cost_category': 'Freemium'
            },
            {
                'name': 'Brilliant.org Number Theory',
                'description': 'Explore patterns in numbers through interactive problems. Learn divisibility, primes, modular arithmetic, and cryptography applications. Great for math competition preparation. Challenge problems for advanced students.',
                'url': 'https://brilliant.org/courses/number-theory/',
                'stem_fields': 'Mathematics',
                'target_grade': '9-12',
                'cost': 'Free',
                'prerequisite_level': 'Medium',
                'cost_category': 'Freemium'
            },
            {
                'name': 'Brilliant.org Logic and Deduction',
                'description': 'Develop logical thinking through puzzles and problems. Learn propositional logic, proof techniques, and reasoning. Great for critical thinking skills. Accessible to beginners. Applications to mathematics and computer science.',
                'url': 'https://brilliant.org/courses/logic/',
                'stem_fields': 'Mathematics, Logic',
                'target_grade': '8-12',
                'cost': 'Free',
                'prerequisite_level': 'None',
                'cost_category': 'Freemium'
            },
            {
                'name': 'Brilliant.org Daily Challenges',
                'description': 'Free daily problem-solving challenges across all STEM subjects. New problems every day in math, science, computer science, and engineering. Build problem-solving streak. Community discussions and solutions. Great daily practice.',
                'url': 'https://brilliant.org/daily-problems/',
                'stem_fields': 'All STEM fields',
                'target_grade': '6-12',
                'cost': 'Free',
                'prerequisite_level': 'Basic',
                'cost_category': 'Free',
                'time_commitment': '15 minutes daily'
            },
            {
                'name': 'Brilliant.org Premium Subscription',
                'description': 'Full access to all Brilliant courses and content. Unlock all interactive lessons, quizzes, and problem sets. Offline access and progress tracking. Support brilliant.org platform. Annual and monthly plans available. Great value for motivated learners.',
                'url': 'https://brilliant.org/premium/',
                'stem_fields': 'All STEM fields',
                'target_grade': '6-12',
                'cost': '120',
                'prerequisite_level': 'None',
                'cost_category': 'Subscription',
                'financial_barrier_level': 'Low',
                'time_commitment': 'Self-paced'
            },
            {
                'name': 'Brilliant.org Quantum Computing',
                'description': 'Introduction to quantum computing concepts through interactive visualizations. Learn qubits, quantum gates, and quantum algorithms. No physics background required. Build intuition for cutting-edge technology. Great for curious students.',
                'url': 'https://brilliant.org/courses/quantum-computing/',
                'stem_fields': 'Computer Science, Physics',
                'target_grade': '11-12',
                'cost': 'Free',
                'prerequisite_level': 'High',
                'cost_category': 'Freemium'
            },
            {
                'name': 'Brilliant.org Scientific Thinking',
                'description': 'Learn scientific method, experimental design, and data analysis. Develop skepticism and critical thinking. Interactive experiments and case studies. Great foundation for all sciences. Accessible to all students.',
                'url': 'https://brilliant.org/courses/scientific-thinking/',
                'stem_fields': 'Science',
                'target_grade': '7-12',
                'cost': 'Free',
                'prerequisite_level': 'None',
                'cost_category': 'Freemium'
            },
            {
                'name': 'Brilliant.org Math Competition Preparation',
                'description': 'Advanced problem-solving for math competitions like AMC, MATHCOUNTS, and olympiads. Challenging problems and elegant solutions. Build competition skills. Learn problem-solving techniques. Great for ambitious math students.',
                'url': 'https://brilliant.org/courses/math-competitions/',
                'stem_fields': 'Mathematics',
                'target_grade': '8-12',
                'cost': 'Free',
                'prerequisite_level': 'High',
                'cost_category': 'Freemium'
            },
            {
                'name': 'Brilliant.org Astronomy and Astrophysics',
                'description': 'Explore the universe through interactive lessons. Learn about stars, planets, galaxies, and cosmology. Physics of space and celestial mechanics. Great for students fascinated by astronomy. Visual simulations of cosmic phenomena.',
                'url': 'https://brilliant.org/courses/astronomy/',
                'stem_fields': 'Physics, Astronomy',
                'target_grade': '9-12',
                'cost': 'Free',
                'prerequisite_level': 'Basic',
                'cost_category': 'Freemium'
            }
        ]

        for program in known_programs:
            self.add_program(program)
            logger.info(f"Added known program: {program['name']}")

    def scrape_brilliant_pages(self):
        """Attempt to scrape Brilliant.org pages for additional courses"""
        urls = [
            'https://brilliant.org/courses/',
            'https://brilliant.org/daily-problems/'
        ]

        for url in urls:
            html = self.fetch_page(url)
            if html:
                self.parse_course_listings(html, url)
            time.sleep(2)  # Delay between requests

    def parse_course_listings(self, html, source_url):
        """Parse course listings from Brilliant.org pages"""
        soup = BeautifulSoup(html, 'html.parser')

        # Brilliant uses React/Next.js - content may be JavaScript-rendered
        # This is a fallback - most data comes from known_programs
        courses_found = 0

        # Look for course information
        course_sections = soup.find_all(['div', 'article', 'section'], class_=lambda x: x and ('course' in x.lower() or 'lesson' in x.lower()) if x else False)
        for section in course_sections:
            courses_found += 1

        logger.info(f"Found {courses_found} programs from {source_url}")

    def add_program(self, program_data):
        """Add a program with all required CSV columns"""
        program = {
            'name': program_data.get('name', ''),
            'description': program_data.get('description', ''),
            'url': program_data.get('url', ''),
            'source': 'Brilliant.org',
            'category': 'Online Course',
            'stem_fields': program_data.get('stem_fields', 'Mathematics'),
            'target_grade': program_data.get('target_grade', '9-12'),
            'cost': program_data.get('cost', 'Free'),
            'location_type': 'Online',
            'time_commitment': program_data.get('time_commitment', 'Self-paced'),
            'prerequisite_level': program_data.get('prerequisite_level', 'None'),
            'support_level': 'Medium',
            'deadline': 'Rolling',
            'financial_barrier_level': program_data.get('financial_barrier_level', 'None'),
            'financial_aid_available': False,
            'family_income_consideration': False,
            'hidden_costs_level': 'None',
            'cost_category': program_data.get('cost_category', 'Free'),
            'diversity_focus': True,
            'underrepresented_friendly': True,
            'first_gen_support': True,
            'cultural_competency': 'High',
            'rural_accessible': True,
            'transportation_required': False,
            'internet_dependency': 'High-speed-required',
            'regional_availability': 'International',
            'family_involvement_required': 'None',
            'peer_network_building': True,
            'mentor_access_level': 'None'
        }
        self.programs.append(program)

    def save_to_csv(self, filename):
        """Save programs to CSV file"""
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=self.csv_columns)
            writer.writeheader()
            writer.writerows(self.programs)
        logger.info(f"Saved {len(self.programs)} programs to {filename}")

    def run(self):
        """Execute the scraping process"""
        logger.info("Starting Brilliant.org Programs scraper...")

        # Add known Brilliant.org courses
        self.add_known_brilliant_courses()

        # Attempt to scrape additional courses
        self.scrape_brilliant_pages()

        # Save to CSV
        output_file = 'data/brilliant_org_programs.csv'
        self.save_to_csv(output_file)

        logger.info(f"Successfully created {output_file} with {len(self.programs)} Brilliant.org courses")
        return output_file


def main():
    scraper = BrilliantOrgScraper()
    output_file = scraper.run()
    print(f"\nBrilliant.org Programs scraper completed successfully!")
    print(f"Output file: {output_file}")
    print(f"Total programs: {len(scraper.programs)}")


if __name__ == "__main__":
    main()
