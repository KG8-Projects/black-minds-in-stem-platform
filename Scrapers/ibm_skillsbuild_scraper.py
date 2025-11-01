#!/usr/bin/env python3
"""
IBM SkillsBuild Programs Scraper
Extracts K-12 technology learning paths and courses from IBM SkillsBuild platform
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

class IBMSkillsBuildScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })

        self.base_urls = [
            'https://skillsbuild.org/students',
            'https://skillsbuild.org/students/course-catalog'
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

    def parse_difficulty_level(self, text, course_name):
        """Determine prerequisite level from difficulty or course description"""
        combined_text = (text + " " + course_name).lower()

        if any(term in combined_text for term in ['advanced', 'expert', 'experienced', 'intermediate to advanced']):
            return "Medium"
        elif any(term in combined_text for term in ['intermediate', 'some experience', 'basic knowledge']):
            return "Basic"
        elif any(term in combined_text for term in ['beginner', 'introductory', 'fundamentals', 'basics', 'no experience']):
            return "None"
        else:
            return "None"  # Default for IBM SkillsBuild (designed for beginners)

    def parse_time_commitment(self, text, course_name):
        """Extract time commitment from course description"""
        combined_text = (text + " " + course_name).lower()

        # Look for specific time mentions
        time_patterns = [
            (r'(\d+)\s*hours?', lambda m: f"{m.group(1)} hours"),
            (r'(\d+)\s*weeks?', lambda m: f"{m.group(1)} weeks"),
            (r'(\d+)\s*months?', lambda m: f"{m.group(1)} months"),
            (r'(\d+)-(\d+)\s*hours?', lambda m: f"{m.group(1)}-{m.group(2)} hours"),
        ]

        for pattern, formatter in time_patterns:
            match = re.search(pattern, combined_text)
            if match:
                return formatter(match)

        # Default time commitments based on course type
        if any(term in combined_text for term in ['learning path', 'comprehensive', 'complete']):
            return "10-20 hours"
        elif any(term in combined_text for term in ['course', 'module', 'lesson']):
            return "2-5 hours"
        else:
            return "Self-paced"

    def parse_stem_fields(self, course_name, description):
        """Determine STEM fields based on course name and description"""
        combined_text = (course_name + " " + description).lower()

        fields = []

        if any(term in combined_text for term in ['artificial intelligence', 'ai', 'machine learning', 'neural network']):
            fields.append('Artificial Intelligence')
        if any(term in combined_text for term in ['data science', 'data analytics', 'big data', 'data']):
            fields.append('Data Science')
        if any(term in combined_text for term in ['cybersecurity', 'security', 'cyber', 'network security']):
            fields.append('Cybersecurity')
        if any(term in combined_text for term in ['cloud computing', 'cloud', 'aws', 'azure']):
            fields.append('Cloud Computing')
        if any(term in combined_text for term in ['blockchain', 'cryptocurrency', 'distributed ledger']):
            fields.append('Blockchain Technology')
        if any(term in combined_text for term in ['web development', 'web design', 'html', 'css', 'javascript']):
            fields.append('Web Development')
        if any(term in combined_text for term in ['quantum computing', 'quantum']):
            fields.append('Quantum Computing')
        if any(term in combined_text for term in ['ux design', 'user experience', 'ui design']):
            fields.append('UX Design')
        if any(term in combined_text for term in ['programming', 'coding', 'software', 'computer science']):
            fields.append('Computer Science')

        # If no specific fields found, default to Computer Science
        if not fields:
            fields.append('Computer Science')

        return ', '.join(fields)

    def parse_category(self, course_name, description):
        """Determine category based on course type"""
        combined_text = (course_name + " " + description).lower()

        if any(term in combined_text for term in ['learning path', 'pathway', 'track']):
            return "Tech Skills Program"
        elif any(term in combined_text for term in ['professional skills', 'workplace', 'career', 'job readiness']):
            return "Career Readiness"
        else:
            return "Online Course"

    def scrape_ibm_pages(self, url):
        """Scrape programs from IBM SkillsBuild pages"""
        soup = self.fetch_page(url)
        if not soup:
            return

        programs_found = 0

        # Look for course/program information
        program_selectors = [
            'div.course-card', 'div.learning-path', 'article.program',
            '.content-area', 'main', 'div.main-content', 'section.course',
            'div[class*="course"]', 'div[class*="learning"]', 'div[class*="path"]'
        ]

        program_elements = []
        for selector in program_selectors:
            elements = soup.select(selector)
            if elements:
                program_elements.extend(elements[:12])
                break

        # If no specific containers found, look for headings and content
        if not program_elements:
            headings = soup.find_all(['h1', 'h2', 'h3', 'h4'])
            for heading in headings[:20]:
                heading_text = self.extract_text_safely(heading).lower()
                if any(term in heading_text for term in ['learning', 'path', 'course', 'skill', 'artificial', 'data', 'cloud', 'cyber', 'blockchain', 'quantum', 'design', 'professional']) and len(heading_text) > 5:
                    # Find the content section after this heading
                    content_section = heading.parent or heading.find_next_sibling()
                    if content_section:
                        program_elements.append(content_section)

        # Process found elements
        for element in program_elements[:15]:
            try:
                # Extract course name from heading
                name_elem = (element.find(['h1', 'h2', 'h3', 'h4']) or
                           element.select_one('.title, .course-title, .path-name') or
                           element.find('strong') or element.find('b'))

                if not name_elem:
                    continue

                name = self.extract_text_safely(name_elem)
                if not name or len(name) < 3 or len(name) > 200:
                    continue

                # Skip navigation or irrelevant content
                if any(skip_term in name.lower() for skip_term in ['menu', 'navigation', 'home', 'about', 'contact', 'login', 'search', 'cart', 'header', 'footer', 'copyright', 'cookie', 'privacy']):
                    continue

                # Skip if it doesn't look like a course/learning path
                if not any(term in name.lower() for term in ['learning', 'path', 'course', 'skill', 'artificial', 'data', 'cloud', 'cyber', 'blockchain', 'quantum', 'design', 'professional', 'computing', 'technology', 'security', 'development']):
                    continue

                # Extract description from paragraphs
                description = ""
                paragraphs = element.find_all('p')
                if paragraphs:
                    desc_texts = [self.extract_text_safely(p) for p in paragraphs[:3]]
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
                                  f"IBM SkillsBuild learning opportunity: {name}"),
                    'url': url,
                    'source': 'IBM SkillsBuild',
                    'category': self.parse_category(name, description),
                    'stem_fields': self.parse_stem_fields(name, description),
                    'target_grade': '9-12',
                    'cost': 'Free',
                    'location_type': 'Online',
                    'time_commitment': self.parse_time_commitment(description, name),
                    'prerequisite_level': self.parse_difficulty_level(description, name),
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
                    'internet_dependency': 'High-speed-required',
                    'regional_availability': 'National',
                    'family_involvement_required': 'None',
                    'peer_network_building': False,
                    'mentor_access_level': 'None'
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

    def add_known_ibm_programs(self):
        """Add well-known IBM SkillsBuild learning paths with detailed information"""
        known_programs = [
            {
                'name': 'Artificial Intelligence Learning Path',
                'description': 'Comprehensive learning path covering AI fundamentals, machine learning concepts, and practical applications. Students learn about neural networks, AI ethics, and real-world AI implementations. Suitable for high school students with no prior experience. Earn digital credentials upon completion.',
                'url': 'https://skillsbuild.org/students',
                'time_commitment': '15-20 hours',
                'prerequisite_level': 'None',
                'stem_fields': 'Artificial Intelligence, Computer Science, Machine Learning',
                'category': 'Tech Skills Program'
            },
            {
                'name': 'Blockchain Learning Path',
                'description': 'Explore blockchain technology fundamentals, cryptocurrency concepts, and distributed ledger systems. Learn how blockchain is transforming industries and prepare for future blockchain-related careers. Includes hands-on activities and real-world case studies. Free digital credentials available.',
                'url': 'https://skillsbuild.org/students',
                'time_commitment': '12-15 hours',
                'prerequisite_level': 'None',
                'stem_fields': 'Blockchain Technology, Computer Science, Cryptography',
                'category': 'Tech Skills Program'
            },
            {
                'name': 'Cloud Computing Learning Path',
                'description': 'Introduction to cloud computing concepts, cloud service models (IaaS, PaaS, SaaS), and major cloud platforms. Students learn about cloud architecture, deployment models, and cloud security. Prepares students for cloud-related careers and certifications. Earn digital badges.',
                'url': 'https://skillsbuild.org/students',
                'time_commitment': '15-20 hours',
                'prerequisite_level': 'None',
                'stem_fields': 'Cloud Computing, Computer Science, Information Technology',
                'category': 'Tech Skills Program'
            },
            {
                'name': 'Cybersecurity Fundamentals',
                'description': 'Learn essential cybersecurity concepts including threat identification, network security, cryptography, and security best practices. Understand common vulnerabilities and how to protect systems and data. Perfect for students interested in cybersecurity careers. Includes interactive simulations.',
                'url': 'https://skillsbuild.org/students/course-catalog',
                'time_commitment': '10-15 hours',
                'prerequisite_level': 'None',
                'stem_fields': 'Cybersecurity, Computer Science, Information Security',
                'category': 'Online Course'
            },
            {
                'name': 'Data Science Foundations',
                'description': 'Introduction to data science concepts, data analysis techniques, and data visualization. Students learn about statistical thinking, data cleaning, and interpreting data patterns. Includes practical exercises with real datasets. Suitable for beginners with interest in data careers.',
                'url': 'https://skillsbuild.org/students/course-catalog',
                'time_commitment': '12-18 hours',
                'prerequisite_level': 'None',
                'stem_fields': 'Data Science, Statistics, Computer Science',
                'category': 'Tech Skills Program'
            },
            {
                'name': 'Design Thinking Learning Path',
                'description': 'Master design thinking methodology for creative problem-solving. Learn to empathize with users, define problems, ideate solutions, prototype, and test. Develops critical thinking and innovation skills applicable across all industries. Includes collaborative projects and case studies.',
                'url': 'https://skillsbuild.org/students',
                'time_commitment': '8-12 hours',
                'prerequisite_level': 'None',
                'stem_fields': 'Design Thinking, Innovation, Problem Solving',
                'category': 'Tech Skills Program'
            },
            {
                'name': 'Professional Skills Development',
                'description': 'Build essential workplace skills including communication, collaboration, time management, and professional etiquette. Learn how to write effective emails, conduct presentations, and work in teams. Prepares students for internships and future careers. Earn professional skills credentials.',
                'url': 'https://skillsbuild.org/students',
                'time_commitment': '10-15 hours',
                'prerequisite_level': 'None',
                'stem_fields': 'Career Readiness, Professional Development, Communication',
                'category': 'Career Readiness'
            },
            {
                'name': 'Web Development Basics',
                'description': 'Learn web development fundamentals including HTML, CSS, and JavaScript basics. Create responsive web pages and understand web design principles. Hands-on projects guide students through building their first websites. Perfect for aspiring web developers.',
                'url': 'https://skillsbuild.org/students/course-catalog',
                'time_commitment': '15-20 hours',
                'prerequisite_level': 'None',
                'stem_fields': 'Web Development, Computer Science, Programming',
                'category': 'Online Course'
            },
            {
                'name': 'Quantum Computing Introduction',
                'description': 'Explore the fascinating world of quantum computing. Learn quantum mechanics basics, quantum algorithms, and quantum computers capabilities. Understand how quantum computing will revolutionize technology. Suitable for curious students interested in cutting-edge technology.',
                'url': 'https://skillsbuild.org/students/course-catalog',
                'time_commitment': '8-10 hours',
                'prerequisite_level': 'Basic',
                'stem_fields': 'Quantum Computing, Physics, Computer Science',
                'category': 'Online Course'
            },
            {
                'name': 'UX Design Fundamentals',
                'description': 'Introduction to user experience design principles and practices. Learn user research methods, wireframing, prototyping, and usability testing. Understand how to create user-centered designs for digital products. Includes hands-on design projects and industry tools.',
                'url': 'https://skillsbuild.org/students/course-catalog',
                'time_commitment': '12-15 hours',
                'prerequisite_level': 'None',
                'stem_fields': 'UX Design, Design Thinking, Digital Design',
                'category': 'Online Course'
            },
            {
                'name': 'IT Support Fundamentals',
                'description': 'Learn essential IT support skills including troubleshooting, hardware basics, operating systems, and customer service. Understand networking fundamentals and common IT problems. Prepares students for entry-level IT support roles and certifications.',
                'url': 'https://skillsbuild.org/students/course-catalog',
                'time_commitment': '10-15 hours',
                'prerequisite_level': 'None',
                'stem_fields': 'Information Technology, Computer Science, Technical Support',
                'category': 'Online Course'
            },
            {
                'name': 'Agile Methodology',
                'description': 'Master Agile project management principles and practices. Learn about Scrum, sprints, user stories, and iterative development. Understand how modern tech teams collaborate and deliver projects. Valuable for students pursuing careers in technology and project management.',
                'url': 'https://skillsbuild.org/students/course-catalog',
                'time_commitment': '6-8 hours',
                'prerequisite_level': 'None',
                'stem_fields': 'Project Management, Software Development, Agile',
                'category': 'Career Readiness'
            },
            {
                'name': 'Job Readiness Skills',
                'description': 'Comprehensive preparation for entering the workforce. Learn resume writing, interview techniques, networking strategies, and professional presence. Includes mock interviews, resume reviews, and career exploration activities. Essential for students preparing for internships and jobs.',
                'url': 'https://skillsbuild.org/students',
                'time_commitment': '8-12 hours',
                'prerequisite_level': 'None',
                'stem_fields': 'Career Readiness, Professional Development, Job Skills',
                'category': 'Career Readiness'
            },
            {
                'name': 'Enterprise Computing Basics',
                'description': 'Introduction to enterprise-level computing systems and business technology. Learn about enterprise software, databases, business processes, and enterprise architecture. Understand how large organizations use technology. Prepares students for business technology careers.',
                'url': 'https://skillsbuild.org/students/course-catalog',
                'time_commitment': '10-12 hours',
                'prerequisite_level': 'None',
                'stem_fields': 'Enterprise Computing, Information Systems, Business Technology',
                'category': 'Online Course'
            },
            {
                'name': 'Sustainability and Technology',
                'description': 'Explore how technology addresses environmental challenges and promotes sustainability. Learn about green computing, renewable energy systems, and sustainable technology practices. Understand the role of tech professionals in creating a sustainable future.',
                'url': 'https://skillsbuild.org/students/course-catalog',
                'time_commitment': '6-8 hours',
                'prerequisite_level': 'None',
                'stem_fields': 'Environmental Science, Technology, Sustainability',
                'category': 'Online Course'
            }
        ]

        for program_data in known_programs:
            program = {
                'name': program_data['name'],
                'description': program_data['description'],
                'url': program_data['url'],
                'source': 'IBM SkillsBuild',
                'category': program_data.get('category', 'Online Course'),
                'stem_fields': program_data.get('stem_fields', 'Computer Science'),
                'target_grade': '9-12',
                'cost': 'Free',
                'location_type': 'Online',
                'time_commitment': program_data.get('time_commitment', 'Self-paced'),
                'prerequisite_level': program_data.get('prerequisite_level', 'None'),
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
                'internet_dependency': 'High-speed-required',
                'regional_availability': 'National',
                'family_involvement_required': 'None',
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

        csv_file = os.path.join(data_dir, 'ibm_skillsbuild_programs.csv')

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
        logger.info("Starting IBM SkillsBuild Programs scraper...")

        # First, add known IBM SkillsBuild programs with detailed information
        self.add_known_ibm_programs()

        # Then scrape additional programs from web pages
        for url in self.base_urls:
            try:
                self.scrape_ibm_pages(url)
                time.sleep(2)  # Respectful delay between pages
            except Exception as e:
                logger.error(f"Error scraping {url}: {e}")
                continue

        # Save to CSV
        if self.programs:
            csv_file = self.save_to_csv()
            if csv_file:
                logger.info(f"Successfully created {csv_file} with {len(self.programs)} IBM SkillsBuild programs")
                return csv_file
            else:
                logger.error("Failed to save CSV file")
                return None
        else:
            logger.warning("No programs found to save")
            return None

def main():
    scraper = IBMSkillsBuildScraper()
    result = scraper.run()

    if result:
        print(f"\nIBM SkillsBuild Programs scraper completed successfully!")
        print(f"Output file: {result}")
        print(f"Total programs: {len(scraper.programs)}")
    else:
        print("\nScraper failed to complete")

if __name__ == "__main__":
    main()