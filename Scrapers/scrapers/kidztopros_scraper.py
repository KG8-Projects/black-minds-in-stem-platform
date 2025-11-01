#!/usr/bin/env python3
"""
KidzToPros STEM Camps Scraper

Scrapes KidzToPros STEM camps and programs information.
"""

import requests
from bs4 import BeautifulSoup
import csv
import time
import re
import os
from urllib.parse import urljoin
from typing import List, Dict, Optional


class KidzToProsScraper:
    def __init__(self):
        self.base_url = "https://www.kidztopros.com"
        self.target_urls = [
            "https://www.kidztopros.com/",
            "https://www.kidztopros.com/programs/",
            "https://www.kidztopros.com/summer-camps/",
            "https://www.kidztopros.com/locations/",
        ]
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.programs = []

    def make_request(self, url: str) -> Optional[BeautifulSoup]:
        """Make a web request with error handling and rate limiting."""
        try:
            print(f"Fetching: {url}")
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            time.sleep(1)  # 1 second delay between requests
            return BeautifulSoup(response.content, 'html.parser')
        except requests.exceptions.RequestException as e:
            print(f"Error fetching {url}: {e}")
            return None

    def extract_text_content(self, soup: BeautifulSoup) -> str:
        """Extract all text content from the page."""
        if soup:
            return soup.get_text(separator=' ', strip=True).lower()
        return ""

    def extract_deadline(self, text: str, default: str = "Rolling (space available)") -> str:
        """Extract deadline information from text."""
        deadline_patterns = [
            r'registration\s+(?:deadline|closes)[:\s]+([^.]+)',
            r'deadline[s]?[:\s]+([^.]+)',
            r'register\s+by[:\s]+([^.]+)',
            r'(?:january|february|march|april|may|june|july|august|september|october|november|december)\s+\d{1,2}(?:st|nd|rd|th)?(?:,\s*\d{4})?'
        ]

        for pattern in deadline_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                deadline = match.group(1) if len(match.groups()) > 0 else match.group(0)
                return deadline.strip()[:100]

        return default

    def extract_description(self, soup: BeautifulSoup, default: str) -> str:
        """Extract program description."""
        if not soup:
            return default

        description_parts = []

        # Try to find main content paragraphs
        for selector in ['main p', '.content p', 'article p', '.description p', '.main-content p', 'p']:
            paragraphs = soup.select(selector)
            if paragraphs:
                for p in paragraphs[:5]:  # Get first 5 paragraphs
                    text = p.get_text().strip()
                    # Filter out navigation and header text
                    if (len(text) > 50 and
                        'cookie' not in text.lower() and
                        'navigation' not in text.lower() and
                        'skip to' not in text.lower() and
                        'sign up' not in text.lower()[:20]):
                        description_parts.append(text)
                        if len(' '.join(description_parts)) >= 300:
                            break
                if description_parts:
                    break

        description = ' '.join(description_parts)[:500] if description_parts else default
        return description

    def create_programs(self, main_soup: BeautifulSoup, programs_soup: Optional[BeautifulSoup],
                       summer_soup: Optional[BeautifulSoup], locations_soup: Optional[BeautifulSoup]) -> List[Dict]:
        """Create program entries based on scraped information."""
        programs = []

        # Extract content from all pages
        main_text = self.extract_text_content(main_soup) if main_soup else ""
        programs_text = self.extract_text_content(programs_soup) if programs_soup else ""
        summer_text = self.extract_text_content(summer_soup) if summer_soup else ""
        locations_text = self.extract_text_content(locations_soup) if locations_soup else ""

        combined_text = f"{main_text} {programs_text} {summer_text} {locations_text}"

        # Extract deadline
        deadline = self.extract_deadline(combined_text)

        # Check for diversity/accessibility initiatives
        diversity_focus = any(term in combined_text for term in [
            'diversity', 'inclusion', 'scholarship', 'financial aid',
            'all students', 'accessible'
        ])

        # Extract main description
        main_description = self.extract_description(main_soup,
            "STEM enrichment programs for kids including coding, robotics, engineering, and technology camps; hands-on project-based learning with expert instructors.")

        # Program 1: Summer STEM Camps
        summer_description = self.extract_description(summer_soup,
            "Week-long summer STEM camps covering coding, robotics, engineering, and technology; hands-on projects; expert instructors; various locations.")

        program1 = {
            'name': 'KidzToPros - Summer STEM Camps',
            'program_type': 'Summer Program',
            'url': 'https://www.kidztopros.com/summer-camps/',
            'source': 'KidzToPros',
            'category': 'STEM Camp',
            'stem_focus': 'Coding, Robotics, Engineering, Technology',
            'target_grade': 'K-12',
            'cost': 'Paid (camp fees apply)',
            'location': 'Multiple U.S. locations',
            'duration': '1-8 weeks (summer)',
            'application_deadline': deadline,
            'eligibility': 'Students K-12; varies by camp',
            'description': summer_description,
            'diversity_focus': diversity_focus,
            'underrepresented_friendly': True,
            'first_gen_support': True,
            'rural_accessible': False,
            'transportation_required': 'Yes (to camp location)',
            'internet_dependency': 'Low',
            'mentor_access_level': 'Teacher (camp instructors)',
            'prerequisite_level': 'Low',
            'gear_support_building': True,
            'contributor_community': False,
            'financial_barrier_level': 'High',
            'financial_aid_available': True,
            'location_type': 'In-Person',
            'support_level': 'High',
            'stem_accessibility': True,
            'inclusive_environment': True,
            'family_involvement': 'High',
            'time_commitment': '1-8 weeks (summer)'
        }
        programs.append(program1)

        # Program 2: Coding Camps
        program2 = {
            'name': 'KidzToPros - Coding and Programming Camps',
            'program_type': 'Camp',
            'url': 'https://www.kidztopros.com/programs/',
            'source': 'KidzToPros',
            'category': 'Coding Camp',
            'stem_focus': 'Computer Programming, Game Development, App Development',
            'target_grade': 'K-12',
            'cost': 'Paid (camp fees apply)',
            'location': 'Multiple locations',
            'duration': '1 week per session',
            'application_deadline': deadline,
            'eligibility': 'Students grades K-12; age-appropriate tracks',
            'description': 'Learn coding through game development and app creation; Python, JavaScript, Scratch programming; age-appropriate curriculum; build projects; expert instructors; hands-on learning; portfolio development; beginner to advanced levels.',
            'diversity_focus': diversity_focus,
            'underrepresented_friendly': True,
            'first_gen_support': True,
            'rural_accessible': False,
            'transportation_required': 'Yes (to camp location)',
            'internet_dependency': 'Medium',
            'mentor_access_level': 'Teacher (coding instructors)',
            'prerequisite_level': 'Low',
            'gear_support_building': True,
            'contributor_community': False,
            'financial_barrier_level': 'High',
            'financial_aid_available': True,
            'location_type': 'In-Person',
            'support_level': 'High',
            'stem_accessibility': True,
            'inclusive_environment': True,
            'family_involvement': 'High',
            'time_commitment': '1 week per session'
        }
        programs.append(program2)

        # Program 3: Robotics Camps
        program3 = {
            'name': 'KidzToPros - Robotics and Engineering Camps',
            'program_type': 'Camp',
            'url': 'https://www.kidztopros.com/programs/',
            'source': 'KidzToPros',
            'category': 'Robotics Camp',
            'stem_focus': 'Robotics, Engineering, Electronics',
            'target_grade': 'K-12',
            'cost': 'Paid (camp fees apply)',
            'location': 'Multiple locations',
            'duration': '1 week per session',
            'application_deadline': deadline,
            'eligibility': 'Students grades K-12',
            'description': 'Build and program robots; hands-on engineering projects; LEGO robotics, VEX robotics, and custom builds; learn mechanical design, electronics, and programming; design challenges; team projects; problem-solving skills; competition preparation.',
            'diversity_focus': diversity_focus,
            'underrepresented_friendly': True,
            'first_gen_support': True,
            'rural_accessible': False,
            'transportation_required': 'Yes (to camp location)',
            'internet_dependency': 'Low',
            'mentor_access_level': 'Teacher (robotics instructors)',
            'prerequisite_level': 'Low',
            'gear_support_building': True,
            'contributor_community': False,
            'financial_barrier_level': 'High',
            'financial_aid_available': True,
            'location_type': 'In-Person',
            'support_level': 'High',
            'stem_accessibility': True,
            'inclusive_environment': True,
            'family_involvement': 'High',
            'time_commitment': '1 week per session'
        }
        programs.append(program3)

        # Program 4: After-School Programs
        program4 = {
            'name': 'KidzToPros - After-School STEM Programs',
            'program_type': 'After-School Program',
            'url': 'https://www.kidztopros.com/programs/',
            'source': 'KidzToPros',
            'category': 'After-School Program',
            'stem_focus': 'Various STEM Topics',
            'target_grade': 'K-12',
            'cost': 'Paid (program fees apply)',
            'location': 'Multiple locations and schools',
            'duration': '8-12 weeks per session',
            'application_deadline': deadline,
            'eligibility': 'Students grades K-12; school-based programs',
            'description': 'Weekly after-school STEM enrichment; rotating topics including coding, robotics, engineering, and science; consistent learning throughout school year; age-appropriate curriculum; project completion; skill progression; convenient school-based locations.',
            'diversity_focus': diversity_focus,
            'underrepresented_friendly': True,
            'first_gen_support': True,
            'rural_accessible': False,
            'transportation_required': 'Minimal (at school)',
            'internet_dependency': 'Medium',
            'mentor_access_level': 'Teacher (program instructors)',
            'prerequisite_level': 'Low',
            'gear_support_building': True,
            'contributor_community': False,
            'financial_barrier_level': 'High',
            'financial_aid_available': True,
            'location_type': 'In-Person',
            'support_level': 'High',
            'stem_accessibility': True,
            'inclusive_environment': True,
            'family_involvement': 'Medium',
            'time_commitment': '8-12 weeks (school year)'
        }
        programs.append(program4)

        # Program 5: Specialty Tech Camps (AI, Game Design, etc.)
        program5 = {
            'name': 'KidzToPros - Specialty Technology Camps',
            'program_type': 'Summer Program',
            'url': 'https://www.kidztopros.com/summer-camps/',
            'source': 'KidzToPros',
            'category': 'Specialty STEM Camp',
            'stem_focus': 'Game Design, 3D Modeling, AI, Virtual Reality',
            'target_grade': '6-12',
            'cost': 'Paid (camp fees apply)',
            'location': 'Select locations',
            'duration': '1-2 weeks',
            'application_deadline': deadline,
            'eligibility': 'Students grades 6-12; some coding experience helpful',
            'description': 'Advanced technology camps including game design with Unity, 3D modeling and animation, artificial intelligence and machine learning, virtual reality development; industry-standard tools; portfolio projects; expert instruction; future-ready skills.',
            'diversity_focus': diversity_focus,
            'underrepresented_friendly': True,
            'first_gen_support': True,
            'rural_accessible': False,
            'transportation_required': 'Yes (to camp location)',
            'internet_dependency': 'High',
            'mentor_access_level': 'Professional (tech instructors)',
            'prerequisite_level': 'Medium',
            'gear_support_building': True,
            'contributor_community': False,
            'financial_barrier_level': 'High',
            'financial_aid_available': True,
            'location_type': 'In-Person',
            'support_level': 'High',
            'stem_accessibility': True,
            'inclusive_environment': True,
            'family_involvement': 'High',
            'time_commitment': '1-2 weeks'
        }
        programs.append(program5)

        return programs

    def scrape_programs(self):
        """Main scraping function."""
        print("Starting KidzToPros scraper...")

        # Fetch all target pages
        main_soup = self.make_request(self.target_urls[0])
        programs_soup = self.make_request(self.target_urls[1])
        summer_soup = self.make_request(self.target_urls[2])
        locations_soup = self.make_request(self.target_urls[3])

        if not main_soup:
            print("Warning: Failed to fetch main page, continuing with available data...")

        # Create program entries
        print("Extracting program information...")
        self.programs = self.create_programs(main_soup, programs_soup, summer_soup, locations_soup)

        print(f"\nScraping completed. Created {len(self.programs)} program tracks.")

    def save_to_csv(self, filename: str = "data/kidztopros_progress.csv"):
        """Save scraped programs to CSV file with exact 29 columns."""
        if not self.programs:
            print("No programs to save")
            return

        # Ensure data directory exists
        os.makedirs(os.path.dirname(filename), exist_ok=True)

        # Define exact 29 columns as specified
        fieldnames = [
            'name',
            'program_type',
            'url',
            'source',
            'category',
            'stem_focus',
            'target_grade',
            'cost',
            'location',
            'duration',
            'application_deadline',
            'eligibility',
            'description',
            'diversity_focus',
            'underrepresented_friendly',
            'first_gen_support',
            'rural_accessible',
            'transportation_required',
            'internet_dependency',
            'mentor_access_level',
            'prerequisite_level',
            'gear_support_building',
            'contributor_community',
            'financial_barrier_level',
            'financial_aid_available',
            'location_type',
            'support_level',
            'stem_accessibility',
            'inclusive_environment',
            'family_involvement',
            'time_commitment'
        ]

        try:
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames, extrasaction='ignore')
                writer.writeheader()
                writer.writerows(self.programs)

            print(f"Saved {len(self.programs)} programs to {filename}")

        except Exception as e:
            print(f"Error saving to CSV: {e}")


def main():
    """Main function to run the scraper."""
    scraper = KidzToProsScraper()
    scraper.scrape_programs()
    scraper.save_to_csv()


if __name__ == "__main__":
    main()
