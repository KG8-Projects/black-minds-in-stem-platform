#!/usr/bin/env python3
"""
Science Olympiad Competition Programs Scraper
Extracts K-12 science competition events from Science Olympiad program pages
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

class ScienceOlympiadScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })

        self.base_urls = [
            'https://www.soinc.org/',
            'https://www.soinc.org/elementary-events-2024',
            'https://www.soinc.org/middle-school-events-2024',
            'https://www.soinc.org/high-school-events-2024',
            'https://www.soinc.org/tournaments-results'
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

    def parse_grade_level(self, text, url, event_name):
        """Determine target grade level from text, URL, and event name"""
        combined_text = (text + " " + url + " " + event_name).lower()

        if any(term in combined_text for term in ['elementary', 'elem', 'k-6', 'grades k-6']):
            return "K-6"
        elif any(term in combined_text for term in ['middle school', 'middle-school', '6-9', 'grades 6-9']):
            return "6-9"
        elif any(term in combined_text for term in ['high school', 'high-school', '9-12', 'grades 9-12']):
            return "9-12"
        else:
            return "6-12"  # Default for Science Olympiad

    def parse_stem_fields(self, event_name, description):
        """Determine STEM fields based on event name and description"""
        combined_text = (event_name + " " + description).lower()

        # Biology-related events
        if any(term in combined_text for term in ['anatomy', 'physiology', 'ornithology', 'entomology', 'botany', 'ecology', 'disease', 'bio', 'genetics', 'evolution', 'cell']):
            return "Biology, Life Sciences"

        # Chemistry-related events
        elif any(term in combined_text for term in ['chemistry', 'chem lab', 'forensics', 'materials', 'polymer', 'chemical']):
            return "Chemistry"

        # Physics-related events
        elif any(term in combined_text for term in ['physics', 'optics', 'sounds', 'waves', 'thermodynamics', 'mechanics', 'electric']):
            return "Physics"

        # Engineering/Technology events
        elif any(term in combined_text for term in ['engineering', 'robot', 'machine', 'structure', 'bridge', 'tower', 'car', 'plane', 'vehicle', 'design', 'build']):
            return "Engineering, Technology"

        # Earth Science events
        elif any(term in combined_text for term in ['astronomy', 'meteorology', 'geology', 'earth', 'rocks', 'minerals', 'weather', 'climate']):
            return "Earth Science, Astronomy"

        # Math/Computer Science events
        elif any(term in combined_text for term in ['math', 'computation', 'computer', 'coding', 'algorithm', 'statistics']):
            return "Mathematics, Computer Science"

        else:
            return "General Science"

    def parse_prerequisite_level(self, event_name, description):
        """Determine prerequisite level based on event complexity"""
        combined_text = (event_name + " " + description).lower()

        if any(term in combined_text for term in ['advanced', 'college level', 'complex', 'specialized', 'expert']):
            return "High"
        elif any(term in combined_text for term in ['intermediate', 'prior knowledge', 'some experience', 'familiar']):
            return "Medium"
        elif any(term in combined_text for term in ['beginner', 'intro', 'basic', 'elementary', 'simple']):
            return "Basic"
        else:
            return "Basic"  # Default for educational competitions

    def parse_hidden_costs(self, event_name, description):
        """Determine hidden costs based on event requirements"""
        combined_text = (event_name + " " + description).lower()

        if any(term in combined_text for term in ['build', 'construct', 'materials', 'supplies', 'equipment', 'kit', 'device']):
            return "Equipment"
        elif any(term in combined_text for term in ['travel', 'transport', 'venue', 'location']):
            return "Travel"
        else:
            return "Low"

    def scrape_science_olympiad_pages(self, url):
        """Scrape events from Science Olympiad pages"""
        soup = self.fetch_page(url)
        if not soup:
            return

        events_found = 0

        # Look for event information
        event_selectors = [
            'div.event-info', 'div.event-details', 'article.event',
            '.content-area', 'main', 'div.main-content', 'section.event',
            'div[class*="event"]', 'li', 'tr', 'div.field-item'
        ]

        event_elements = []
        for selector in event_selectors:
            elements = soup.select(selector)
            if elements:
                event_elements.extend(elements[:15])  # Limit per selector
                break

        # If no specific containers found, look for headings and content
        if not event_elements:
            headings = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5'])
            for heading in headings[:20]:
                heading_text = self.extract_text_safely(heading).lower()
                if any(term in heading_text for term in ['event', 'competition', 'test', 'lab', 'build']) and len(heading_text) > 3:
                    # Find the content section after this heading
                    content_section = heading.parent or heading.find_next_sibling()
                    if content_section:
                        event_elements.append(content_section)

        # Process found elements
        for element in event_elements[:25]:  # Limit to avoid duplicates
            try:
                # Extract event name from heading or link
                name_elem = (element.find(['h1', 'h2', 'h3', 'h4', 'h5']) or
                           element.select_one('.title, .event-title, .field-name-title') or
                           element.find('a') or element.find('strong') or element.find('b'))

                if not name_elem:
                    # Try to get text content directly if it looks like an event
                    text_content = self.extract_text_safely(element)
                    if text_content and len(text_content) > 5 and len(text_content) < 100:
                        name = text_content
                    else:
                        continue
                else:
                    name = self.extract_text_safely(name_elem)

                if not name or len(name) < 3 or len(name) > 200:
                    continue

                # Skip navigation or irrelevant content
                if any(skip_term in name.lower() for skip_term in ['menu', 'navigation', 'home', 'about', 'contact', 'login', 'search', 'cart', 'header', 'footer']):
                    continue

                # Skip if it doesn't look like a Science Olympiad event
                if not any(term in name.lower() for term in ['anatomy', 'chemistry', 'physics', 'biology', 'engineering', 'astronomy', 'geology', 'botany', 'ecology', 'forensics', 'optics', 'disease', 'ornithology', 'entomology', 'materials', 'structures', 'machines', 'experimental', 'inquiry', 'invitational', 'tournament', 'test', 'lab', 'detector', 'bridge', 'tower', 'car', 'plane']):
                    continue

                # Extract description from paragraphs or surrounding text
                description = ""
                paragraphs = element.find_all('p')
                if paragraphs:
                    desc_texts = [self.extract_text_safely(p) for p in paragraphs[:3]]
                    description = " ".join([d for d in desc_texts if d and len(d) > 10])

                if not description:
                    # Try to get text from divs or other elements
                    content_divs = element.find_all('div', string=True)
                    if content_divs:
                        description = " ".join([self.extract_text_safely(d) for d in content_divs[:2] if len(self.extract_text_safely(d)) > 10])

                if not description:
                    description = self.extract_text_safely(element)

                # Clean up the name
                name = re.sub(r'^[0-9\.\-\s]*', '', name)  # Remove leading numbers
                name = name.strip()

                # Create event entry
                program = {
                    'name': name,
                    'description': (description[:500] if description else
                                  f"Science Olympiad competition event: {name}"),
                    'url': url,
                    'source': 'Science Olympiad',
                    'category': 'Science Competition',
                    'stem_fields': self.parse_stem_fields(name, description),
                    'target_grade': self.parse_grade_level(description, url, name),
                    'cost': 'Low-cost',
                    'location_type': 'In-person',
                    'time_commitment': '6-8 months',
                    'prerequisite_level': self.parse_prerequisite_level(name, description),
                    'support_level': 'High',
                    'deadline': 'Regional tournament dates',
                    'financial_barrier_level': 'Low',
                    'financial_aid_available': False,
                    'family_income_consideration': False,
                    'hidden_costs_level': self.parse_hidden_costs(name, description),
                    'cost_category': 'Under-$100',
                    'diversity_focus': False,
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
                if not any(p['name'].lower() == program['name'].lower() for p in self.programs):
                    self.programs.append(program)
                    events_found += 1
                    logger.info(f"Added event: {name}")

            except Exception as e:
                logger.error(f"Error processing event element: {e}")
                continue

        logger.info(f"Found {events_found} events from {url}")

    def add_known_science_olympiad_events(self):
        """Add well-known Science Olympiad events with detailed information"""
        known_events = [
            # Elementary Division (K-6)
            {
                'name': 'Elementary Metric Mastery',
                'description': 'Students demonstrate understanding of metric units through measurement activities and conversions. Tests practical application of metric system in real-world scenarios.',
                'url': 'https://www.soinc.org/elementary-events-2024',
                'target_grade': 'K-6',
                'stem_fields': 'Mathematics',
                'prerequisite_level': 'Basic'
            },
            {
                'name': 'Elementary Solar System',
                'description': 'Students answer questions about the solar system, planets, moons, and space exploration. Includes identification of celestial objects and understanding of astronomical concepts.',
                'url': 'https://www.soinc.org/elementary-events-2024',
                'target_grade': 'K-6',
                'stem_fields': 'Earth Science, Astronomy',
                'prerequisite_level': 'Basic'
            },
            {
                'name': 'Elementary Crime Busters',
                'description': 'Students use scientific investigation techniques to solve mock crimes. Involves observation, evidence analysis, and basic forensic science principles.',
                'url': 'https://www.soinc.org/elementary-events-2024',
                'target_grade': 'K-6',
                'stem_fields': 'Chemistry, Forensic Science',
                'prerequisite_level': 'Basic'
            },

            # Middle School Division (6-9)
            {
                'name': 'Anatomy and Physiology',
                'description': 'Students demonstrate understanding of human body systems through written tests and practical identification. Covers major organ systems and their functions.',
                'url': 'https://www.soinc.org/middle-school-events-2024',
                'target_grade': '6-9',
                'stem_fields': 'Biology, Life Sciences',
                'prerequisite_level': 'Medium'
            },
            {
                'name': 'Disease Detectives',
                'description': 'Students investigate disease outbreaks, analyze epidemiological data, and understand public health principles. Includes case studies and data interpretation.',
                'url': 'https://www.soinc.org/middle-school-events-2024',
                'target_grade': '6-9',
                'stem_fields': 'Biology, Public Health',
                'prerequisite_level': 'Medium'
            },
            {
                'name': 'Experimental Design',
                'description': 'Students design and conduct experiments to answer scientific questions. Emphasizes scientific method, controls, variables, and data analysis.',
                'url': 'https://www.soinc.org/middle-school-events-2024',
                'target_grade': '6-9',
                'stem_fields': 'General Science, Research Methods',
                'prerequisite_level': 'Medium'
            },
            {
                'name': 'Fossils',
                'description': 'Students identify fossils, understand geological time periods, and interpret paleontological evidence. Includes hands-on fossil identification and evolution concepts.',
                'url': 'https://www.soinc.org/middle-school-events-2024',
                'target_grade': '6-9',
                'stem_fields': 'Earth Science, Biology',
                'prerequisite_level': 'Medium'
            },
            {
                'name': 'Mission Possible',
                'description': 'Students build Rube Goldberg-style device to accomplish specific tasks through chain reactions. Tests engineering design and physics principles.',
                'url': 'https://www.soinc.org/middle-school-events-2024',
                'target_grade': '6-9',
                'stem_fields': 'Engineering, Physics',
                'prerequisite_level': 'Medium',
                'hidden_costs_level': 'Equipment'
            },
            {
                'name': 'Road Scholar',
                'description': 'Students answer questions about maps, navigation, and geographic features. Includes topographic map reading and spatial reasoning skills.',
                'url': 'https://www.soinc.org/middle-school-events-2024',
                'target_grade': '6-9',
                'stem_fields': 'Earth Science, Geography',
                'prerequisite_level': 'Basic'
            },

            # High School Division (9-12)
            {
                'name': 'Anatomy and Physiology',
                'description': 'Advanced study of human body systems with detailed knowledge of structure and function. Includes microscopic identification and physiological processes.',
                'url': 'https://www.soinc.org/high-school-events-2024',
                'target_grade': '9-12',
                'stem_fields': 'Biology, Life Sciences',
                'prerequisite_level': 'High'
            },
            {
                'name': 'Astronomy',
                'description': 'Students demonstrate knowledge of stellar evolution, galaxies, cosmology, and astronomical objects. Includes calculations and deep space phenomena.',
                'url': 'https://www.soinc.org/high-school-events-2024',
                'target_grade': '9-12',
                'stem_fields': 'Earth Science, Astronomy, Physics',
                'prerequisite_level': 'High'
            },
            {
                'name': 'Chemistry Lab',
                'description': 'Hands-on chemistry laboratory event testing practical skills in chemical analysis, synthesis, and safety procedures. Includes qualitative and quantitative analysis.',
                'url': 'https://www.soinc.org/high-school-events-2024',
                'target_grade': '9-12',
                'stem_fields': 'Chemistry',
                'prerequisite_level': 'High'
            },
            {
                'name': 'Codebusters',
                'description': 'Students solve various types of codes and ciphers, including historical and modern cryptographic methods. Tests pattern recognition and logical thinking.',
                'url': 'https://www.soinc.org/high-school-events-2024',
                'target_grade': '9-12',
                'stem_fields': 'Mathematics, Computer Science',
                'prerequisite_level': 'Medium'
            },
            {
                'name': 'Detector Building',
                'description': 'Students build device to detect and measure electromagnetic radiation. Tests understanding of electronics, sensors, and measurement principles.',
                'url': 'https://www.soinc.org/high-school-events-2024',
                'target_grade': '9-12',
                'stem_fields': 'Engineering, Physics',
                'prerequisite_level': 'High',
                'hidden_costs_level': 'Equipment'
            },
            {
                'name': 'Environmental Chemistry',
                'description': 'Students analyze environmental samples and understand chemical processes in ecosystems. Includes water quality testing and pollution analysis.',
                'url': 'https://www.soinc.org/high-school-events-2024',
                'target_grade': '9-12',
                'stem_fields': 'Chemistry, Environmental Science',
                'prerequisite_level': 'High'
            },
            {
                'name': 'Forensics',
                'description': 'Students analyze physical evidence from mock crime scenes using scientific techniques. Includes fingerprinting, DNA analysis, and trace evidence.',
                'url': 'https://www.soinc.org/high-school-events-2024',
                'target_grade': '9-12',
                'stem_fields': 'Chemistry, Forensic Science',
                'prerequisite_level': 'High'
            },
            {
                'name': 'Geologic Mapping',
                'description': 'Students interpret geologic maps, cross-sections, and understand Earth processes. Includes structural geology and mineral identification.',
                'url': 'https://www.soinc.org/high-school-events-2024',
                'target_grade': '9-12',
                'stem_fields': 'Earth Science, Geology',
                'prerequisite_level': 'High'
            },
            {
                'name': 'Ornithology',
                'description': 'Students identify birds, understand bird behavior, ecology, and conservation. Includes anatomy, migration patterns, and habitat requirements.',
                'url': 'https://www.soinc.org/high-school-events-2024',
                'target_grade': '9-12',
                'stem_fields': 'Biology, Ecology',
                'prerequisite_level': 'High'
            },
            {
                'name': 'Physics Lab',
                'description': 'Hands-on physics laboratory event testing experimental skills and understanding of physical principles. Includes mechanics, waves, and thermodynamics.',
                'url': 'https://www.soinc.org/high-school-events-2024',
                'target_grade': '9-12',
                'stem_fields': 'Physics',
                'prerequisite_level': 'High'
            },
            {
                'name': 'Robot Tour',
                'description': 'Students build autonomous robot to navigate course and complete tasks. Tests programming, sensors, and mechanical design skills.',
                'url': 'https://www.soinc.org/high-school-events-2024',
                'target_grade': '9-12',
                'stem_fields': 'Engineering, Computer Science',
                'prerequisite_level': 'High',
                'hidden_costs_level': 'Equipment'
            },
            {
                'name': 'Wind Power',
                'description': 'Students build wind-powered device to lift maximum weight. Tests understanding of aerodynamics, mechanical advantage, and energy conversion.',
                'url': 'https://www.soinc.org/high-school-events-2024',
                'target_grade': '9-12',
                'stem_fields': 'Engineering, Physics',
                'prerequisite_level': 'Medium',
                'hidden_costs_level': 'Equipment'
            }
        ]

        for event_data in known_events:
            program = {
                'name': event_data['name'],
                'description': event_data['description'],
                'url': event_data['url'],
                'source': 'Science Olympiad',
                'category': 'Science Competition',
                'stem_fields': event_data.get('stem_fields', 'General Science'),
                'target_grade': event_data.get('target_grade', '6-12'),
                'cost': 'Low-cost',
                'location_type': 'In-person',
                'time_commitment': '6-8 months',
                'prerequisite_level': event_data.get('prerequisite_level', 'Basic'),
                'support_level': 'High',
                'deadline': 'Regional tournament dates',
                'financial_barrier_level': 'Low',
                'financial_aid_available': False,
                'family_income_consideration': False,
                'hidden_costs_level': event_data.get('hidden_costs_level', 'Low'),
                'cost_category': 'Under-$100',
                'diversity_focus': False,
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
                logger.info(f"Added known event: {program['name']}")

    def save_to_csv(self):
        """Save all programs to a single CSV file"""
        # Create data directory if it doesn't exist
        data_dir = os.path.join('scrapers', 'data')
        os.makedirs(data_dir, exist_ok=True)

        csv_file = os.path.join(data_dir, 'science_olympiad_programs.csv')

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
        logger.info("Starting Science Olympiad Competition scraper...")

        # First, add known Science Olympiad events with detailed information
        self.add_known_science_olympiad_events()

        # Then scrape additional events from web pages
        for url in self.base_urls:
            try:
                self.scrape_science_olympiad_pages(url)
                time.sleep(2)  # Respectful delay between pages
            except Exception as e:
                logger.error(f"Error scraping {url}: {e}")
                continue

        # Save to CSV
        if self.programs:
            csv_file = self.save_to_csv()
            if csv_file:
                logger.info(f"Successfully created {csv_file} with {len(self.programs)} Science Olympiad events")
                return csv_file
            else:
                logger.error("Failed to save CSV file")
                return None
        else:
            logger.warning("No events found to save")
            return None

def main():
    scraper = ScienceOlympiadScraper()
    result = scraper.run()

    if result:
        print(f"\nScience Olympiad Competition scraper completed successfully!")
        print(f"Output file: {result}")
        print(f"Total events: {len(scraper.programs)}")
    else:
        print("\nScraper failed to complete")

if __name__ == "__main__":
    main()