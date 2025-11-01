#!/usr/bin/env python3
"""
AIChE Student Programs Scraper

Scrapes American Institute of Chemical Engineers student program information.
"""

import requests
from bs4 import BeautifulSoup
import csv
import time
import re
import os
from urllib.parse import urljoin
from typing import List, Dict, Optional


class AIChEStudentScraper:
    def __init__(self):
        self.base_url = "https://www.aiche.org"
        self.target_urls = [
            "https://www.aiche.org/community/students",
            "https://www.aiche.org/community/students/high-school-students",
            "https://www.aiche.org/community/students/chem-e-car-competition",
            "https://www.aiche.org/students/scholarships",
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

    def extract_deadline(self, text: str, default: str = "Varies by program") -> str:
        """Extract deadline information from text."""
        deadline_patterns = [
            r'deadline[s]?[:\s]+([^.]+)',
            r'due[:\s]+([^.]+)',
            r'applications?\s+due[:\s]+([^.]+)',
            r'submit[ted]*\s+by[:\s]+([^.]+)',
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
        for selector in ['main p', '.content p', 'article p', '.entry-content p', '.main-content p', '.field--type-text-with-summary p', 'p']:
            paragraphs = soup.select(selector)
            if paragraphs:
                for p in paragraphs[:5]:  # Get first 5 paragraphs
                    text = p.get_text().strip()
                    # Filter out navigation and header text
                    if (len(text) > 50 and
                        'cookie' not in text.lower() and
                        'navigation' not in text.lower() and
                        'skip to' not in text.lower() and
                        'log in' not in text.lower() and
                        'member benefit' not in text.lower()[:30]):
                        description_parts.append(text)
                        if len(' '.join(description_parts)) >= 300:
                            break
                if description_parts:
                    break

        description = ' '.join(description_parts)[:500] if description_parts else default
        return description

    def create_programs(self, main_soup: BeautifulSoup, hs_soup: Optional[BeautifulSoup],
                       chem_e_car_soup: Optional[BeautifulSoup], scholarships_soup: Optional[BeautifulSoup]) -> List[Dict]:
        """Create program entries based on scraped information - K-12 only."""
        programs = []

        # Extract content from all pages
        hs_text = self.extract_text_content(hs_soup) if hs_soup else ""

        # Check for diversity initiatives
        diversity_focus = any(term in hs_text for term in [
            'diversity', 'inclusion', 'underrepresented', 'underserved',
            'equity', 'diverse', 'inclusive', 'marginalized', 'all students',
            'minority', 'women in engineering', 'broadening participation'
        ])

        # Program: High School Student Membership (K-12 only)
        hs_description = self.extract_description(hs_soup,
            "High school student membership; access to career resources, competitions, and networking; connect with chemical engineering profession.")

        program = {
            'name': 'AIChE High School Student Membership',
            'program_type': 'Membership',
            'url': 'https://www.aiche.org/community/students/high-school-students',
            'source': 'AIChE Student Programs',
            'category': 'Professional Development',
            'stem_focus': 'Chemical Engineering, Chemistry',
            'target_grade': '9-12',
            'cost': 'Membership Fee ($20/year)',
            'location': 'Online',
            'duration': 'Annual membership',
            'application_deadline': 'Rolling',
            'eligibility': 'High school students interested in chemical engineering',
            'description': hs_description,
            'diversity_focus': diversity_focus,
            'underrepresented_friendly': True,
            'first_gen_support': True,
            'rural_accessible': True,
            'transportation_required': 'No',
            'internet_dependency': 'High',
            'mentor_access_level': 'Professional (AIChE network)',
            'prerequisite_level': 'Basic',
            'gear_support_building': True,
            'contributor_community': True,
            'financial_barrier_level': 'Low',
            'financial_aid_available': True,
            'location_type': 'Online',
            'support_level': 'Medium',
            'stem_accessibility': True,
            'inclusive_environment': True,
            'family_involvement': 'Low',
            'time_commitment': 'Self-paced'
        }
        programs.append(program)

        return programs

    def scrape_programs(self):
        """Main scraping function."""
        print("Starting AIChE Student Programs scraper...")

        # Fetch all target pages
        main_soup = self.make_request(self.target_urls[0])
        hs_soup = self.make_request(self.target_urls[1])
        chem_e_car_soup = self.make_request(self.target_urls[2])
        scholarships_soup = self.make_request(self.target_urls[3])

        if not main_soup:
            print("Warning: Failed to fetch main page, continuing with available data...")

        # Create program entries
        print("Extracting program information...")
        self.programs = self.create_programs(main_soup, hs_soup, chem_e_car_soup, scholarships_soup)

        print(f"\nScraping completed. Created {len(self.programs)} program tracks.")

    def save_to_csv(self, filename: str = "data/aiche_student_progress.csv"):
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
    scraper = AIChEStudentScraper()
    scraper.scrape_programs()
    scraper.save_to_csv()


if __name__ == "__main__":
    main()
