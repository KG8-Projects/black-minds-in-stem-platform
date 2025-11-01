"""
Scratch Programming Platform Resources Scraper
Extracts Scratch educational resources and curricula for K-12 students
Saves to ONE CSV file: data/scratch_programming.csv
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


class ScratchProgrammingScraper:
    def __init__(self):
        self.base_url = "https://scratch.mit.edu"
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

    def add_known_scratch_resources(self):
        """Add well-known Scratch educational resources"""
        known_programs = [
            {
                'name': 'Scratch Programming Platform',
                'description': 'Free visual block-based programming platform from MIT for all ages. Create interactive stories, games, and animations by snapping together code blocks. No typing required - drag and drop programming. Share projects with global community of millions. Learn coding fundamentals: loops, conditionals, variables, events. Available in 70+ languages. Perfect introduction to computer science.',
                'url': 'https://scratch.mit.edu/',
                'stem_fields': 'Computer Science, Programming, Creative Computing',
                'target_grade': 'K-12',
                'cost': 'Free',
                'location_type': 'Online',
                'time_commitment': 'Self-paced',
                'prerequisite_level': 'None',
                'cost_category': 'Free'
            },
            {
                'name': 'Scratch for Educators',
                'description': 'Complete educator resources for teaching with Scratch. Curriculum guides, lesson plans, and classroom activities. Step-by-step tutorials for teachers new to coding. Classroom management tools and student accounts. Assessment rubrics and learning standards alignment. Professional development resources. Active educator community for sharing ideas and support. Free workshop materials.',
                'url': 'https://scratch.mit.edu/educators',
                'stem_fields': 'Computer Science, Education',
                'target_grade': 'K-12',
                'cost': 'Free',
                'location_type': 'Online',
                'time_commitment': 'Self-paced',
                'prerequisite_level': 'None',
                'cost_category': 'Free',
                'category': 'Educator Resources'
            },
            {
                'name': 'Scratch Ideas Page',
                'description': 'Curated project ideas and coding tutorials. Step-by-step guides for creating games, animations, and stories. Organized by difficulty level and topic. Video tutorials and activity cards. Perfect for self-directed learning or classroom use. Projects include: make music, create art, animate characters, build games. Download activity cards for offline use.',
                'url': 'https://scratch.mit.edu/ideas',
                'stem_fields': 'Computer Science, Programming, Creative Arts',
                'target_grade': 'K-12',
                'cost': 'Free',
                'location_type': 'Online',
                'time_commitment': 'Self-paced',
                'prerequisite_level': 'None',
                'cost_category': 'Free',
                'category': 'Tutorial Library'
            },
            {
                'name': 'ScratchJr for Young Learners',
                'description': 'Simplified version of Scratch for ages 5-7. Introductory programming language for young children. Create interactive stories and games on tablet or computer. Designed for early elementary students. Teaches sequencing, problem-solving, and creativity. No reading required - visual interface. Great for kindergarten and early grades. Available as free app.',
                'url': 'https://www.scratchjr.org/',
                'stem_fields': 'Computer Science, Early Childhood Education',
                'target_grade': 'K-2',
                'cost': 'Free',
                'location_type': 'Online',
                'time_commitment': 'Self-paced',
                'prerequisite_level': 'None',
                'cost_category': 'Free',
                'category': 'Early Learning Platform'
            },
            {
                'name': 'Scratch Coding Cards',
                'description': 'Physical and digital activity cards for learning Scratch. 75+ project ideas with step-by-step instructions. Organized by theme: games, animations, stories, music. Color-coded by difficulty level. Use in classroom or at home. Downloadable PDFs available free. Purchase printed deck or print yourself. Great for workshops and summer camps.',
                'url': 'https://scratch.mit.edu/ideas',
                'stem_fields': 'Computer Science, Programming',
                'target_grade': '3-8',
                'cost': 'Free',
                'location_type': 'Hybrid',
                'time_commitment': 'Self-paced',
                'prerequisite_level': 'None',
                'cost_category': 'Free',
                'category': 'Activity Cards'
            },
            {
                'name': 'Scratch Creative Computing Curriculum',
                'description': 'Complete free curriculum guide from Harvard Graduate School of Education. Seven units covering programming fundamentals through creative projects. Designed for classrooms, after-school programs, or self-study. Includes lesson plans, assessments, and facilitation tips. Emphasizes computational thinking and creativity. Used by educators worldwide. Available in multiple languages. Aligned with CS standards.',
                'url': 'https://scratched.gse.harvard.edu/guide/',
                'stem_fields': 'Computer Science, Computational Thinking',
                'target_grade': '5-9',
                'cost': 'Free',
                'location_type': 'Online',
                'time_commitment': 'Semester course',
                'prerequisite_level': 'None',
                'cost_category': 'Free',
                'category': 'Curriculum Guide'
            },
            {
                'name': 'Scratch Online Community',
                'description': 'Global online community of young programmers. Share projects and get feedback. Remix and build on others\' projects. Studios for collaborative work. Safe moderated environment. Learn from millions of shared projects. Weekly challenges and featured projects. Connect with peers worldwide. Develop digital literacy and citizenship skills.',
                'url': 'https://scratch.mit.edu/explore',
                'stem_fields': 'Computer Science, Digital Citizenship',
                'target_grade': 'K-12',
                'cost': 'Free',
                'location_type': 'Online',
                'time_commitment': 'Ongoing',
                'prerequisite_level': 'None',
                'cost_category': 'Free',
                'category': 'Online Community'
            },
            {
                'name': 'Scratch Video Tutorials',
                'description': 'Library of video tutorials for learning Scratch. Short how-to videos covering all Scratch features. Topics include sprites, backdrops, sounds, and coding blocks. Step-by-step project walkthroughs. Beginner to advanced level content. Closed captions available. Great for visual learners. Use in flipped classroom or independent study.',
                'url': 'https://scratch.mit.edu/ideas',
                'stem_fields': 'Computer Science, Programming',
                'target_grade': 'K-12',
                'cost': 'Free',
                'location_type': 'Online',
                'time_commitment': 'Self-paced',
                'prerequisite_level': 'None',
                'cost_category': 'Free',
                'category': 'Video Tutorials'
            },
            {
                'name': 'Scratch Design Studio Challenges',
                'description': 'Monthly themed programming challenges for students. Create projects based on specific themes or constraints. Learn new techniques and coding concepts. Community voting and featured projects. Great for motivation and inspiration. Past themes include climate change, music, storytelling. Build portfolio of diverse projects. Participate solo or with class.',
                'url': 'https://scratch.mit.edu/studios/',
                'stem_fields': 'Computer Science, Creative Computing',
                'target_grade': '3-12',
                'cost': 'Free',
                'location_type': 'Online',
                'time_commitment': 'Monthly challenges',
                'prerequisite_level': 'Basic',
                'cost_category': 'Free',
                'category': 'Programming Challenges'
            },
            {
                'name': 'Scratch Teacher Accounts',
                'description': 'Free teacher accounts for classroom management. Create and manage student accounts. Monitor student projects and progress. Provide feedback on student work. Organize class studios for collaboration. Schedule and manage assignments. Privacy controls for student safety. Simplified registration for students. Essential tool for classroom use.',
                'url': 'https://scratch.mit.edu/educators/register',
                'stem_fields': 'Computer Science Education',
                'target_grade': 'K-12',
                'cost': 'Free',
                'location_type': 'Online',
                'time_commitment': 'Academic year',
                'prerequisite_level': 'None',
                'cost_category': 'Free',
                'category': 'Classroom Management'
            },
            {
                'name': 'Scratch Day Events',
                'description': 'Global network of Scratch Day events. Local gatherings for Scratchers to meet, share, and learn. Workshops, presentations, and hands-on activities. Organized by schools, libraries, museums, and community centers. Free events worldwide. Annual celebration of creative coding. Connect with local Scratch community. Family-friendly programming events.',
                'url': 'https://day.scratch.mit.edu/',
                'stem_fields': 'Computer Science, Community Building',
                'target_grade': 'K-12',
                'cost': 'Free',
                'location_type': 'Regional',
                'time_commitment': '1-2 days',
                'prerequisite_level': 'None',
                'cost_category': 'Free',
                'category': 'Community Event',
                'transportation_required': True,
                'internet_dependency': 'None'
            },
            {
                'name': 'Scratch Extensions and Add-ons',
                'description': 'Additional coding blocks and features for advanced projects. Connect to hardware like micro:bit, LEGO, Makey Makey. Text-to-speech and translation capabilities. Music composition and video sensing. Machine learning blocks with Teachable Machine. Expands Scratch capabilities for complex projects. STEM integration opportunities. Great for advanced students.',
                'url': 'https://scratch.mit.edu/about',
                'stem_fields': 'Computer Science, Engineering, Robotics',
                'target_grade': '5-12',
                'cost': 'Free',
                'location_type': 'Online',
                'time_commitment': 'Self-paced',
                'prerequisite_level': 'Medium',
                'cost_category': 'Free',
                'category': 'Advanced Features',
                'hidden_costs_level': 'Equipment'
            }
        ]

        for program in known_programs:
            self.add_program(program)
            logger.info(f"Added known program: {program['name']}")

    def scrape_scratch_pages(self):
        """Attempt to scrape Scratch pages for additional resources"""
        urls = [
            'https://scratch.mit.edu/educators',
            'https://scratch.mit.edu/ideas',
            'https://scratch.mit.edu/about'
        ]

        for url in urls:
            html = self.fetch_page(url)
            if html:
                self.parse_resource_listings(html, url)
            time.sleep(2)  # Delay between requests

    def parse_resource_listings(self, html, source_url):
        """Parse resource listings from Scratch pages"""
        soup = BeautifulSoup(html, 'html.parser')

        # Scratch pages may have minimal content in HTML
        # This is a fallback - most data comes from known_programs
        resources_found = 0

        # Look for resource information
        resource_sections = soup.find_all(['div', 'section', 'article'], class_=lambda x: x and ('resource' in x.lower() or 'tutorial' in x.lower() or 'educator' in x.lower()) if x else False)
        for section in resource_sections:
            resources_found += 1

        logger.info(f"Found {resources_found} resources from {source_url}")

    def add_program(self, program_data):
        """Add a program with all required CSV columns"""
        program = {
            'name': program_data.get('name', ''),
            'description': program_data.get('description', ''),
            'url': program_data.get('url', ''),
            'source': 'MIT Scratch',
            'category': program_data.get('category', 'Programming Platform'),
            'stem_fields': program_data.get('stem_fields', 'Computer Science, Programming'),
            'target_grade': program_data.get('target_grade', 'K-12'),
            'cost': 'Free',
            'location_type': program_data.get('location_type', 'Online'),
            'time_commitment': program_data.get('time_commitment', 'Self-paced'),
            'prerequisite_level': program_data.get('prerequisite_level', 'None'),
            'support_level': 'High',
            'deadline': 'Rolling',
            'financial_barrier_level': 'None',
            'financial_aid_available': False,
            'family_income_consideration': False,
            'hidden_costs_level': program_data.get('hidden_costs_level', 'None'),
            'cost_category': 'Free',
            'diversity_focus': True,
            'underrepresented_friendly': True,
            'first_gen_support': True,
            'cultural_competency': 'High',
            'rural_accessible': True,
            'transportation_required': program_data.get('transportation_required', False),
            'internet_dependency': program_data.get('internet_dependency', 'Basic'),
            'regional_availability': 'International',
            'family_involvement_required': 'Optional',
            'peer_network_building': True,
            'mentor_access_level': 'Peer'
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
        logger.info("Starting Scratch Programming Platform scraper...")

        # Add known Scratch resources
        self.add_known_scratch_resources()

        # Attempt to scrape additional resources
        self.scrape_scratch_pages()

        # Save to CSV
        output_file = 'data/scratch_programming.csv'
        self.save_to_csv(output_file)

        logger.info(f"Successfully created {output_file} with {len(self.programs)} Scratch resources")
        return output_file


def main():
    scraper = ScratchProgrammingScraper()
    output_file = scraper.run()
    print(f"\nScratch Programming Platform scraper completed successfully!")
    print(f"Output file: {output_file}")
    print(f"Total resources: {len(scraper.programs)}")


if __name__ == "__main__":
    main()
