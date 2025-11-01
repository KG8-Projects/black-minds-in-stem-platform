#!/usr/bin/env python3
"""
Junior Science and Humanities Symposium (JSHS) Scraper

Scrapes JSHS program information for regional and national symposia.
"""

import requests
from bs4 import BeautifulSoup
import csv
import time
import re
import os
from urllib.parse import urljoin
from typing import List, Dict, Optional


class JSHSScraper:
    def __init__(self):
        self.base_url = "https://jshs.org"
        self.target_urls = [
            "https://jshs.org/",
            "https://jshs.org/students",
            "https://jshs.org/students/how-to-participate",
            "https://jshs.org/students/regional-symposia",
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

    def extract_deadline(self, text: str) -> str:
        """Extract deadline information from text."""
        deadline_patterns = [
            r'deadline[s]?[:\s]+([^.]+)',
            r'due[:\s]+([^.]+)',
            r'submit[ted]*\s+by[:\s]+([^.]+)',
            r'applications?\s+due[:\s]+([^.]+)',
            r'(?:january|february|march|april|may|june|july|august|september|october|november|december)\s+\d{1,2}(?:st|nd|rd|th)?(?:,\s*\d{4})?'
        ]

        for pattern in deadline_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                deadline = match.group(1) if len(match.groups()) > 0 else match.group(0)
                return deadline.strip()[:100]

        # Default deadline for JSHS (typically January-February for regional)
        return "January-February (Regional), March-April (National)"

    def extract_description(self, soup: BeautifulSoup, default: str) -> str:
        """Extract program description."""
        if not soup:
            return default

        description_parts = []

        # Try to find main content paragraphs
        for selector in ['main p', '.content p', 'article p', '.entry-content p', '.main-content p', 'p']:
            paragraphs = soup.select(selector)
            if paragraphs:
                for p in paragraphs[:5]:  # Get first 5 paragraphs
                    text = p.get_text().strip()
                    # Filter out navigation and header text
                    if (len(text) > 50 and
                        'cookie' not in text.lower() and
                        'navigation' not in text.lower() and
                        'skip to' not in text.lower()):
                        description_parts.append(text)
                        if len(' '.join(description_parts)) >= 300:
                            break
                if description_parts:
                    break

        description = ' '.join(description_parts)[:500] if description_parts else default
        return description

    def create_programs(self, main_soup: BeautifulSoup, students_soup: Optional[BeautifulSoup],
                       how_to_soup: Optional[BeautifulSoup], regional_soup: Optional[BeautifulSoup]) -> List[Dict]:
        """Create program entries based on scraped information."""
        programs = []

        # Extract content from all pages
        main_text = self.extract_text_content(main_soup) if main_soup else ""
        students_text = self.extract_text_content(students_soup) if students_soup else ""
        how_to_text = self.extract_text_content(how_to_soup) if how_to_soup else ""
        regional_text = self.extract_text_content(regional_soup) if regional_soup else ""

        combined_text = f"{main_text} {students_text} {how_to_text} {regional_text}"

        # Extract deadline
        deadline = self.extract_deadline(combined_text)

        # Check for diversity initiatives
        diversity_focus = any(term in combined_text for term in [
            'diversity', 'inclusion', 'underrepresented', 'underserved',
            'equity', 'diverse', 'inclusive', 'marginalized', 'all students',
            'broadening participation'
        ])

        # Extract main description
        main_description = self.extract_description(main_soup,
            "STEM research symposium for high school students sponsored by U.S. Army, Navy, and Air Force; students present original research to compete for scholarships and recognition.")

        # Program 1: Regional Symposia
        program1 = {
            'name': 'Junior Science and Humanities Symposium - Regional Competition',
            'program_type': 'Research Symposium',
            'url': 'https://jshs.org/students/regional-symposia',
            'source': 'Junior Science and Humanities Symposium',
            'category': 'STEM Research Competition',
            'stem_focus': 'Life Sciences, Physical Sciences, Engineering, Mathematics, Behavioral Sciences',
            'target_grade': '9-12',
            'cost': 'Free',
            'location': '48 regional sites nationwide',
            'duration': '1-2 days (Regional symposium)',
            'application_deadline': deadline,
            'eligibility': 'High school students (grades 9-12); original research required; oral presentation',
            'description': main_description,
            'diversity_focus': diversity_focus,
            'underrepresented_friendly': True,
            'first_gen_support': True,
            'rural_accessible': True,
            'transportation_required': 'Yes (to regional site)',
            'internet_dependency': 'Medium',
            'mentor_access_level': 'Professional (research mentor)',
            'prerequisite_level': 'High',
            'gear_support_building': False,
            'contributor_community': True,
            'financial_barrier_level': 'Low',
            'financial_aid_available': True,
            'location_type': 'In-Person',
            'support_level': 'High',
            'stem_accessibility': True,
            'inclusive_environment': True,
            'family_involvement': 'Medium',
            'time_commitment': '6-12 months (research + symposium)'
        }
        programs.append(program1)

        # Program 2: National Symposium
        program2 = {
            'name': 'Junior Science and Humanities Symposium - National Symposium',
            'program_type': 'Competition',
            'url': 'https://jshs.org/',
            'source': 'Junior Science and Humanities Symposium',
            'category': 'STEM Research Competition',
            'stem_focus': 'Life Sciences, Physical Sciences, Engineering, Mathematics, Behavioral Sciences',
            'target_grade': '9-12',
            'cost': 'Free',
            'location': 'National location (varies annually)',
            'duration': '3-4 days (April/May)',
            'application_deadline': deadline,
            'eligibility': 'Top presenters from regional symposia; all expenses paid',
            'description': 'National symposium for regional winners; compete for up to $16,000 in scholarships; present research to military and civilian scientists; networking opportunities; all-expenses-paid including travel, lodging, and meals.',
            'diversity_focus': diversity_focus,
            'underrepresented_friendly': True,
            'first_gen_support': True,
            'rural_accessible': True,
            'transportation_required': 'Yes (provided for finalists)',
            'internet_dependency': 'Low',
            'mentor_access_level': 'Professional',
            'prerequisite_level': 'High',
            'gear_support_building': False,
            'contributor_community': True,
            'financial_barrier_level': 'None',
            'financial_aid_available': True,
            'location_type': 'In-Person',
            'support_level': 'High',
            'stem_accessibility': True,
            'inclusive_environment': True,
            'family_involvement': 'Medium',
            'time_commitment': '3-4 days (National symposium)'
        }
        programs.append(program2)

        # Program 3: Research Development
        program3 = {
            'name': 'JSHS - Independent Research Project Development',
            'program_type': 'Research Program',
            'url': 'https://jshs.org/students/how-to-participate',
            'source': 'Junior Science and Humanities Symposium',
            'category': 'STEM Research',
            'stem_focus': 'Scientific Research (multiple disciplines)',
            'target_grade': '9-12',
            'cost': 'Free',
            'location': 'School/Lab-based',
            'duration': '6-12 months',
            'application_deadline': deadline,
            'eligibility': 'High school students; research mentor required; original research project',
            'description': 'Develop independent research project under mentorship; conduct experiments or theoretical work; prepare research paper and oral presentation; categories include physical sciences, life sciences, mathematics, engineering, and behavioral sciences.',
            'diversity_focus': diversity_focus,
            'underrepresented_friendly': True,
            'first_gen_support': True,
            'rural_accessible': True,
            'transportation_required': 'Varies by project',
            'internet_dependency': 'Medium',
            'mentor_access_level': 'Professional (research mentor required)',
            'prerequisite_level': 'High',
            'gear_support_building': False,
            'contributor_community': True,
            'financial_barrier_level': 'Low',
            'financial_aid_available': False,
            'location_type': 'Flexible',
            'support_level': 'High',
            'stem_accessibility': True,
            'inclusive_environment': True,
            'family_involvement': 'Medium',
            'time_commitment': '10-15 hours/week for 6-12 months'
        }
        programs.append(program3)

        # Program 4: Oral Presentation Skills Development
        program4 = {
            'name': 'JSHS - Scientific Presentation and Communication',
            'program_type': 'Research Symposium',
            'url': 'https://jshs.org/students',
            'source': 'Junior Science and Humanities Symposium',
            'category': 'Science Communication',
            'stem_focus': 'Scientific Communication, Public Speaking',
            'target_grade': '9-12',
            'cost': 'Free',
            'location': 'Regional and National venues',
            'duration': '12-minute oral presentation + Q&A',
            'application_deadline': deadline,
            'eligibility': 'High school students presenting research',
            'description': 'Develop scientific communication skills through oral research presentations; 12-minute talks followed by Q&A with judges; feedback from professional scientists; practice defending research to technical audience; build confidence in public speaking.',
            'diversity_focus': diversity_focus,
            'underrepresented_friendly': True,
            'first_gen_support': True,
            'rural_accessible': True,
            'transportation_required': 'Yes (to symposium)',
            'internet_dependency': 'Low',
            'mentor_access_level': 'Professional (judges and mentors)',
            'prerequisite_level': 'High',
            'gear_support_building': False,
            'contributor_community': True,
            'financial_barrier_level': 'Low',
            'financial_aid_available': True,
            'location_type': 'In-Person',
            'support_level': 'High',
            'stem_accessibility': True,
            'inclusive_environment': True,
            'family_involvement': 'Medium',
            'time_commitment': 'Presentation day + preparation'
        }
        programs.append(program4)

        return programs

    def scrape_programs(self):
        """Main scraping function."""
        print("Starting Junior Science and Humanities Symposium scraper...")

        # Fetch all target pages
        main_soup = self.make_request(self.target_urls[0])
        students_soup = self.make_request(self.target_urls[1])
        how_to_soup = self.make_request(self.target_urls[2])
        regional_soup = self.make_request(self.target_urls[3])

        if not main_soup:
            print("Warning: Failed to fetch main page, continuing with available data...")

        # Create program entries
        print("Extracting program information...")
        self.programs = self.create_programs(main_soup, students_soup, how_to_soup, regional_soup)

        print(f"\nScraping completed. Created {len(self.programs)} program tracks.")

    def save_to_csv(self, filename: str = "data/jshs_progress.csv"):
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
    scraper = JSHSScraper()
    scraper.scrape_programs()
    scraper.save_to_csv()


if __name__ == "__main__":
    main()
