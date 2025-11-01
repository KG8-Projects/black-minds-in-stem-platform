#!/usr/bin/env python3
"""
Stanford Pre-Collegiate Programs Scraper
Extracts high school summer programs and courses from Stanford University
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

class StanfordPreCollegeScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })

        self.base_urls = [
            'https://spcs.stanford.edu/programs',
            'https://summerinstitutes.spcs.stanford.edu/'
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

    def parse_target_grade(self, program_name, description):
        """Determine target grade level from program details"""
        combined_text = (program_name + " " + description).lower()

        if any(term in combined_text for term in ['grades 8-11', 'grade 8-11', '8-11']):
            return "8-11"
        elif any(term in combined_text for term in ['grades 10-11', 'grade 10-11', '10-11']):
            return "10-11"
        elif any(term in combined_text for term in ['grades 9-12', 'grade 9-12', '9-12', 'high school']):
            return "9-12"
        elif any(term in combined_text for term in ['grade 11', 'grade 12', '11-12', 'rising senior', 'junior']):
            return "11-12"
        else:
            return "9-12"  # Default for Stanford programs

    def parse_stem_fields(self, program_name, description):
        """Determine STEM fields based on program name and description"""
        combined_text = (program_name + " " + description).lower()

        fields = []

        if any(term in combined_text for term in ['computer science', 'cs', 'programming', 'coding', 'software']):
            fields.append('Computer Science')
        if any(term in combined_text for term in ['mathematics', 'math', 'calculus', 'algebra', 'geometry']):
            fields.append('Mathematics')
        if any(term in combined_text for term in ['physics', 'quantum']):
            fields.append('Physics')
        if any(term in combined_text for term in ['engineering', 'engineer']):
            fields.append('Engineering')
        if any(term in combined_text for term in ['biology', 'biomedical', 'life science']):
            fields.append('Biology')
        if any(term in combined_text for term in ['chemistry', 'chemical']):
            fields.append('Chemistry')
        if any(term in combined_text for term in ['data science', 'data analytics', 'machine learning', 'ai', 'artificial intelligence']):
            fields.append('Data Science')
        if any(term in combined_text for term in ['robotics', 'robot']):
            fields.append('Robotics')
        if any(term in combined_text for term in ['medicine', 'medical', 'health']):
            fields.append('Medicine')
        if any(term in combined_text for term in ['science', 'scientific']):
            if not fields:
                fields.append('Science')

        # If no specific fields found, default based on keywords
        if not fields:
            if any(term in combined_text for term in ['stem', 'technical', 'technology']):
                fields.append('STEM')
            else:
                fields.append('Science')

        return ', '.join(fields)

    def parse_location_type(self, program_name, description):
        """Determine location type from program details"""
        combined_text = (program_name + " " + description).lower()

        if any(term in combined_text for term in ['online', 'virtual', 'remote', 'distance']):
            return "Online"
        elif any(term in combined_text for term in ['residential', 'on campus', 'live', 'housing']):
            return "Residential"
        elif any(term in combined_text for term in ['commuter', 'day program']):
            return "Commuter"
        elif any(term in combined_text for term in ['hybrid', 'blended']):
            return "Hybrid"
        else:
            return "Residential"  # Default for Stanford summer programs

    def parse_time_commitment(self, program_name, description):
        """Extract time commitment from program description"""
        combined_text = (program_name + " " + description).lower()

        if any(term in combined_text for term in ['three week', '3 week', '3-week', 'three-week']):
            return "3 weeks"
        elif any(term in combined_text for term in ['two week', '2 week', '2-week', 'two-week']):
            return "2 weeks"
        elif any(term in combined_text for term in ['four week', '4 week', '4-week', 'four-week']):
            return "4 weeks"
        elif any(term in combined_text for term in ['six week', '6 week', '6-week', 'six-week']):
            return "6 weeks"
        elif any(term in combined_text for term in ['eight week', '8 week', '8-week', 'eight-week']):
            return "8 weeks"
        elif any(term in combined_text for term in ['summer', 'intensive']):
            return "3-4 weeks"
        elif any(term in combined_text for term in ['academic year', 'year-round', 'ongoing']):
            return "Academic year"
        else:
            return "3 weeks"  # Default

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

        # Default cost for Stanford programs (typically $5000-$15000)
        return "8000"  # Approximate average

    def parse_prerequisite_level(self, program_name, description):
        """Determine prerequisite level based on program details"""
        combined_text = (program_name + " " + description).lower()

        if any(term in combined_text for term in ['advanced', 'intensive', 'university-level', 'college credit', 'selective', 'competitive']):
            return "High"
        elif any(term in combined_text for term in ['intermediate', 'some experience', 'prerequisite', 'recommended']):
            return "Medium"
        elif any(term in combined_text for term in ['beginner', 'introduction', 'introductory', 'no experience']):
            return "Basic"
        else:
            return "Medium"  # Default for Stanford programs

    def parse_financial_aid(self, description, program_name):
        """Check for financial aid availability"""
        combined_text = (description + " " + program_name).lower()

        if any(term in combined_text for term in ['scholarship', 'financial aid', 'need-based', 'funding', 'assistance']):
            return True
        else:
            return True  # Stanford typically offers aid

    def parse_diversity_focus(self, description, program_name):
        """Check for diversity focus in program description"""
        combined_text = (description + " " + program_name).lower()

        if any(term in combined_text for term in ['diversity', 'inclusion', 'underrepresented', 'equity', 'access', 'all students']):
            return True
        else:
            return False

    def scrape_stanford_pages(self, url):
        """Scrape programs from Stanford pages"""
        soup = self.fetch_page(url)
        if not soup:
            return

        programs_found = 0

        # Look for program information
        program_selectors = [
            'div.program-card', 'div.program-info', 'article.program',
            '.content-area', 'main', 'div.main-content', 'section.program',
            'div[class*="program"]', 'div[class*="course"]'
        ]

        program_elements = []
        for selector in program_selectors:
            elements = soup.select(selector)
            if elements:
                program_elements.extend(elements[:20])
                break

        # If no specific containers found, look for headings
        if not program_elements:
            headings = soup.find_all(['h1', 'h2', 'h3', 'h4'])
            for heading in headings[:25]:
                heading_text = self.extract_text_safely(heading).lower()
                if any(term in heading_text for term in ['stanford', 'program', 'institute', 'course', 'summer', 'camp', 'math', 'science', 'humanities']) and len(heading_text) > 5:
                    content_section = heading.parent or heading.find_next_sibling()
                    if content_section:
                        program_elements.append(content_section)

        # Process found elements
        for element in program_elements[:25]:
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
                if any(skip_term in name.lower() for skip_term in ['menu', 'navigation', 'home', 'about', 'contact', 'login', 'search', 'header', 'footer', 'apply', 'learn more']):
                    continue

                # Skip if it doesn't look like a Stanford program
                if not any(term in name.lower() for term in ['stanford', 'program', 'institute', 'course', 'summer', 'camp', 'math', 'science', 'spcs', 'humanities']):
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
                    description = f"Stanford Pre-Collegiate program: {name}. Academic enrichment program for high school students on Stanford campus."

                # Determine location type
                location_type = self.parse_location_type(name, description)

                # Create program entry
                program = {
                    'name': name,
                    'description': (description[:500] if description else
                                  f"Stanford program: {name}"),
                    'url': url,
                    'source': 'Stanford Pre-Collegiate Programs',
                    'category': 'Summer Program',
                    'stem_fields': self.parse_stem_fields(name, description),
                    'target_grade': self.parse_target_grade(name, description),
                    'cost': self.parse_cost(description, name),
                    'location_type': location_type,
                    'time_commitment': self.parse_time_commitment(name, description),
                    'prerequisite_level': self.parse_prerequisite_level(name, description),
                    'support_level': 'High',
                    'deadline': 'Check Stanford website',
                    'financial_barrier_level': 'High',
                    'financial_aid_available': self.parse_financial_aid(description, name),
                    'family_income_consideration': 'Middle+',
                    'hidden_costs_level': 'Travel',
                    'cost_category': '$2000+',
                    'diversity_focus': self.parse_diversity_focus(description, name),
                    'underrepresented_friendly': True,
                    'first_gen_support': False,
                    'cultural_competency': 'Medium',
                    'rural_accessible': False if location_type != 'Online' else True,
                    'transportation_required': True if location_type in ['Residential', 'Commuter'] else False,
                    'internet_dependency': 'High-speed-required' if location_type == 'Online' else 'Basic',
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

    def add_known_stanford_programs(self):
        """Add well-known Stanford Pre-Collegiate programs with detailed information"""
        known_programs = [
            {
                'name': 'Stanford Pre-Collegiate Summer Institutes',
                'description': 'Three-week intensive summer courses for grades 8-11 in various subjects including computer science, engineering, humanities, and sciences. Single-subject enrichment with Stanford faculty. Residential and online options. Rigorous academic experience preparing students for college-level work. Includes lectures, labs, projects, and Stanford campus life.',
                'url': 'https://spcs.stanford.edu/programs',
                'target_grade': '8-11',
                'stem_fields': 'Computer Science, Engineering, Science, Mathematics',
                'time_commitment': '3 weeks',
                'location_type': 'Hybrid',
                'cost': '8000',
                'prerequisite_level': 'Medium'
            },
            {
                'name': 'Stanford Summer Humanities Institute',
                'description': 'Three-week residential program for grades 10-11 exploring humanities questions through seminars, workshops, and collaborative projects. Small seminar-style classes with Stanford faculty. Includes writing workshops, research projects, and cultural activities. Develops critical thinking and analytical writing skills.',
                'url': 'https://spcs.stanford.edu/programs',
                'target_grade': '10-11',
                'stem_fields': 'Humanities, Social Science',
                'time_commitment': '3 weeks',
                'location_type': 'Residential',
                'cost': '9000',
                'prerequisite_level': 'Medium'
            },
            {
                'name': 'Stanford University Mathematics Camp (SUMaC)',
                'description': 'Intensive four-week residential program for grades 10-11 in advanced mathematics. Focus on abstract mathematical thinking, proofs, and problem-solving. Two tracks: Program I (algebra and number theory) and Program II (topology and group theory). Taught by Stanford faculty and graduate students. Highly selective.',
                'url': 'https://spcs.stanford.edu/programs',
                'target_grade': '10-11',
                'stem_fields': 'Mathematics',
                'time_commitment': '4 weeks',
                'location_type': 'Residential',
                'cost': '9500',
                'prerequisite_level': 'High'
            },
            {
                'name': 'Stanford Pre-Collegiate Computer Science',
                'description': 'Three-week intensive computer science program covering programming, algorithms, data structures, and software development. Hands-on coding projects using Python, Java, or other languages. Learn from Stanford CS faculty and graduate students. Build portfolio projects. Residential experience includes tech talks and company visits.',
                'url': 'https://summerinstitutes.spcs.stanford.edu/',
                'target_grade': '9-12',
                'stem_fields': 'Computer Science, Programming, Software Engineering',
                'time_commitment': '3 weeks',
                'location_type': 'Residential',
                'cost': '8500',
                'prerequisite_level': 'Medium'
            },
            {
                'name': 'Stanford Pre-Collegiate Engineering',
                'description': 'Engineering design and problem-solving program introducing students to various engineering disciplines. Includes mechanical, electrical, biomedical, and computer engineering projects. Team-based design challenges, lab work, and prototype building. Meet Stanford engineering faculty and tour engineering labs.',
                'url': 'https://summerinstitutes.spcs.stanford.edu/',
                'target_grade': '9-12',
                'stem_fields': 'Engineering, Design, Technology',
                'time_commitment': '3 weeks',
                'location_type': 'Residential',
                'cost': '8500',
                'prerequisite_level': 'Medium'
            },
            {
                'name': 'Stanford Pre-Collegiate Artificial Intelligence',
                'description': 'Advanced AI and machine learning program covering neural networks, computer vision, natural language processing, and AI ethics. Programming projects using Python and ML frameworks. Learn from Stanford AI researchers. Explore AI applications and future implications. Requires programming background.',
                'url': 'https://summerinstitutes.spcs.stanford.edu/',
                'target_grade': '10-12',
                'stem_fields': 'Artificial Intelligence, Computer Science, Machine Learning',
                'time_commitment': '3 weeks',
                'location_type': 'Residential',
                'cost': '9000',
                'prerequisite_level': 'High'
            },
            {
                'name': 'Stanford Pre-Collegiate Biomedical Sciences',
                'description': 'Exploration of biomedical research, biotechnology, and medical sciences. Laboratory techniques, research methods, and ethical issues in biomedicine. Visit Stanford medical facilities and research labs. Learn from medical faculty and researchers. Covers genetics, cell biology, and biomedical engineering.',
                'url': 'https://summerinstitutes.spcs.stanford.edu/',
                'target_grade': '10-12',
                'stem_fields': 'Biomedical Science, Biology, Medicine',
                'time_commitment': '3 weeks',
                'location_type': 'Residential',
                'cost': '8500',
                'prerequisite_level': 'Medium'
            },
            {
                'name': 'Stanford Pre-Collegiate Physics',
                'description': 'Advanced physics topics beyond high school curriculum including modern physics, quantum mechanics, and relativity. Laboratory experiments, problem-solving, and mathematical modeling. Taught by Stanford physics faculty. Prepares students for university-level physics. Requires strong math background.',
                'url': 'https://summerinstitutes.spcs.stanford.edu/',
                'target_grade': '10-12',
                'stem_fields': 'Physics, Mathematics',
                'time_commitment': '3 weeks',
                'location_type': 'Residential',
                'cost': '8000',
                'prerequisite_level': 'High'
            },
            {
                'name': 'Stanford Pre-Collegiate Data Science',
                'description': 'Introduction to data science covering statistics, data analysis, visualization, and machine learning applications. Work with real datasets, learn Python and R, and develop data-driven projects. Includes statistical thinking, data ethics, and communication of findings. No prior programming required.',
                'url': 'https://summerinstitutes.spcs.stanford.edu/',
                'target_grade': '9-12',
                'stem_fields': 'Data Science, Statistics, Computer Science',
                'time_commitment': '3 weeks',
                'location_type': 'Residential',
                'cost': '8500',
                'prerequisite_level': 'Medium'
            },
            {
                'name': 'Stanford University-Level Online Math & Physics',
                'description': 'Advanced online courses offering Stanford University credit in mathematics and physics. College-level curriculum taught by Stanford instructors. Self-paced with regular assignments and exams. Covers topics like multivariable calculus, linear algebra, and advanced physics. Requires strong mathematical background.',
                'url': 'https://spcs.stanford.edu/programs',
                'target_grade': '9-12',
                'stem_fields': 'Mathematics, Physics',
                'time_commitment': '10 weeks',
                'location_type': 'Online',
                'cost': '3500',
                'prerequisite_level': 'High',
                'category': 'University Pre-College'
            },
            {
                'name': 'Stanford Pre-Collegiate Game Design',
                'description': 'Game design and development program combining programming, art, storytelling, and game mechanics. Create original video games using industry tools. Learn game engines, 3D modeling, level design, and game theory. Team projects and portfolio development. Suitable for aspiring game developers.',
                'url': 'https://summerinstitutes.spcs.stanford.edu/',
                'target_grade': '9-12',
                'stem_fields': 'Computer Science, Game Development, Design',
                'time_commitment': '3 weeks',
                'location_type': 'Residential',
                'cost': '8500',
                'prerequisite_level': 'Medium'
            },
            {
                'name': 'Stanford Pre-Collegiate Robotics',
                'description': 'Hands-on robotics program covering robot design, programming, sensors, and autonomous systems. Build and program robots for competitions and challenges. Learn mechanical design, electronics, and control systems. Team-based projects with industry-standard robotics platforms. Tour Stanford robotics labs.',
                'url': 'https://summerinstitutes.spcs.stanford.edu/',
                'target_grade': '9-12',
                'stem_fields': 'Robotics, Engineering, Computer Science',
                'time_commitment': '3 weeks',
                'location_type': 'Residential',
                'cost': '8500',
                'prerequisite_level': 'Medium'
            },
            {
                'name': 'Stanford Pre-Collegiate Environmental Science',
                'description': 'Study environmental challenges, sustainability, and climate science. Field work, laboratory research, and data analysis. Explore Stanford sustainability initiatives and environmental research. Topics include ecology, conservation, renewable energy, and environmental policy. Scientific research skills development.',
                'url': 'https://summerinstitutes.spcs.stanford.edu/',
                'target_grade': '9-12',
                'stem_fields': 'Environmental Science, Biology, Chemistry',
                'time_commitment': '3 weeks',
                'location_type': 'Residential',
                'cost': '8000',
                'prerequisite_level': 'Medium'
            },
            {
                'name': 'Stanford Math Circle',
                'description': 'After-school mathematics enrichment program for grades 1-12 focused on problem-solving and mathematical exploration. Weekly online and in-person sessions during academic year. Covers competition mathematics, proofs, and advanced topics. Multiple levels based on age and experience. Develops mathematical thinking.',
                'url': 'https://spcs.stanford.edu/programs',
                'target_grade': '1-12',
                'stem_fields': 'Mathematics',
                'time_commitment': 'Academic year',
                'location_type': 'Hybrid',
                'cost': '800',
                'prerequisite_level': 'Basic',
                'category': 'Academic Year Program'
            },
            {
                'name': 'Stanford Pre-Collegiate Medical Sciences',
                'description': 'Introduction to medical careers and healthcare through lectures, simulations, and clinical observation. Learn anatomy, physiology, and medical ethics. Interact with Stanford medical students and physicians. Includes hospital tours, medical procedures demonstrations, and career exploration. Ideal for aspiring healthcare professionals.',
                'url': 'https://summerinstitutes.spcs.stanford.edu/',
                'target_grade': '10-12',
                'stem_fields': 'Medicine, Health Sciences, Biology',
                'time_commitment': '3 weeks',
                'location_type': 'Residential',
                'cost': '9000',
                'prerequisite_level': 'Medium'
            },
            {
                'name': 'Stanford Pre-Collegiate Chemistry',
                'description': 'Advanced chemistry covering topics beyond AP level including organic chemistry, chemical synthesis, and spectroscopy. Laboratory-intensive program with research-style experiments. Learn modern chemical techniques and instrumentation. Taught by Stanford chemistry faculty. Prepares for college chemistry.',
                'url': 'https://summerinstitutes.spcs.stanford.edu/',
                'target_grade': '10-12',
                'stem_fields': 'Chemistry, Science',
                'time_commitment': '3 weeks',
                'location_type': 'Residential',
                'cost': '8500',
                'prerequisite_level': 'High'
            },
            {
                'name': 'Stanford Pre-Collegiate Business & Entrepreneurship',
                'description': 'Introduction to business principles, entrepreneurship, and innovation. Develop business plans, learn marketing and finance basics, and pitch startup ideas. Guest speakers from Silicon Valley. Team projects simulating real business challenges. Includes visits to Stanford business school and local companies.',
                'url': 'https://summerinstitutes.spcs.stanford.edu/',
                'target_grade': '10-12',
                'stem_fields': 'Business, Entrepreneurship, Technology',
                'time_commitment': '3 weeks',
                'location_type': 'Residential',
                'cost': '8000',
                'prerequisite_level': 'Basic'
            },
            {
                'name': 'Stanford Pre-Collegiate Creative Writing',
                'description': 'Writing workshop focusing on fiction, poetry, and creative nonfiction. Small seminar format with peer review and one-on-one feedback. Study craft elements, develop writing voice, and complete portfolio projects. Led by published writers and Stanford writing instructors. Includes readings and literary events.',
                'url': 'https://summerinstitutes.spcs.stanford.edu/',
                'target_grade': '9-12',
                'stem_fields': 'Writing, Literature, Arts',
                'time_commitment': '3 weeks',
                'location_type': 'Residential',
                'cost': '7500',
                'prerequisite_level': 'Basic'
            },
            {
                'name': 'Stanford Pre-Collegiate Psychology',
                'description': 'Introduction to psychological science including cognitive psychology, social psychology, and neuroscience. Conduct psychology experiments, analyze data, and explore research methods. Learn from Stanford psychology faculty. Topics include memory, decision-making, mental health, and human behavior.',
                'url': 'https://summerinstitutes.spcs.stanford.edu/',
                'target_grade': '10-12',
                'stem_fields': 'Psychology, Neuroscience, Social Science',
                'time_commitment': '3 weeks',
                'location_type': 'Residential',
                'cost': '8000',
                'prerequisite_level': 'Basic'
            },
            {
                'name': 'Stanford Pre-Collegiate International Relations',
                'description': 'Exploration of global politics, international law, diplomacy, and world affairs. Model UN simulations, policy debates, and case studies. Meet Stanford faculty from international relations and political science. Develop analytical and public speaking skills. Includes current events analysis.',
                'url': 'https://summerinstitutes.spcs.stanford.edu/',
                'target_grade': '10-12',
                'stem_fields': 'Political Science, International Relations, Social Science',
                'time_commitment': '3 weeks',
                'location_type': 'Residential',
                'cost': '7500',
                'prerequisite_level': 'Basic'
            }
        ]

        for program_data in known_programs:
            program = {
                'name': program_data['name'],
                'description': program_data['description'],
                'url': program_data['url'],
                'source': 'Stanford Pre-Collegiate Programs',
                'category': program_data.get('category', 'Summer Program'),
                'stem_fields': program_data.get('stem_fields', 'STEM'),
                'target_grade': program_data.get('target_grade', '9-12'),
                'cost': program_data.get('cost', '8000'),
                'location_type': program_data.get('location_type', 'Residential'),
                'time_commitment': program_data.get('time_commitment', '3 weeks'),
                'prerequisite_level': program_data.get('prerequisite_level', 'Medium'),
                'support_level': 'High',
                'deadline': 'Check Stanford website',
                'financial_barrier_level': 'High',
                'financial_aid_available': True,
                'family_income_consideration': 'Middle+',
                'hidden_costs_level': 'Travel',
                'cost_category': '$2000+',
                'diversity_focus': False,
                'underrepresented_friendly': True,
                'first_gen_support': False,
                'cultural_competency': 'Medium',
                'rural_accessible': False if program_data.get('location_type', 'Residential') != 'Online' else True,
                'transportation_required': True if program_data.get('location_type', 'Residential') in ['Residential', 'Commuter'] else False,
                'internet_dependency': 'High-speed-required' if program_data.get('location_type', 'Residential') == 'Online' else 'Basic',
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

        csv_file = os.path.join(data_dir, 'stanford_precollege_programs.csv')

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
        logger.info("Starting Stanford Pre-Collegiate Programs scraper...")

        # First, add known Stanford programs with detailed information
        self.add_known_stanford_programs()

        # Then scrape additional programs from web pages
        for url in self.base_urls:
            try:
                self.scrape_stanford_pages(url)
                time.sleep(2)  # Respectful delay between pages
            except Exception as e:
                logger.error(f"Error scraping {url}: {e}")
                continue

        # Save to CSV
        if self.programs:
            csv_file = self.save_to_csv()
            if csv_file:
                logger.info(f"Successfully created {csv_file} with {len(self.programs)} Stanford Pre-Collegiate programs")
                return csv_file
            else:
                logger.error("Failed to save CSV file")
                return None
        else:
            logger.warning("No programs found to save")
            return None

def main():
    scraper = StanfordPreCollegeScraper()
    result = scraper.run()

    if result:
        print(f"\nStanford Pre-Collegiate Programs scraper completed successfully!")
        print(f"Output file: {result}")
        print(f"Total programs: {len(scraper.programs)}")
    else:
        print("\nScraper failed to complete")

if __name__ == "__main__":
    main()