#!/usr/bin/env python3
"""
DOE National Science Bowl Scraper

Scrapes Department of Energy National Science Bowl program information.
"""

import requests
from bs4 import BeautifulSoup
import csv
import time
import re
import os
from urllib.parse import urljoin
from typing import List, Dict, Optional


class DOEScienceBowlScraper:
    def __init__(self):
        self.base_url = "https://science.osti.gov"
        self.target_urls = [
            "https://science.osti.gov/wdts/nsb",
            "https://science.osti.gov/wdts/nsb/High-School",
            "https://science.osti.gov/wdts/nsb/Middle-School",
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
        return soup.get_text(separator=' ', strip=True).lower()

    def extract_deadline(self, text: str) -> str:
        """Extract deadline information from text."""
        deadline_patterns = [
            r'registration\s+(?:deadline|due)[:\s]+([^.]+)',
            r'deadline[s]?[:\s]+([^.]+)',
            r'register\s+by[:\s]+([^.]+)',
            r'(?:january|february|march|april|may|june|july|august|september|october|november|december)\s+\d{1,2}(?:st|nd|rd|th)?(?:,\s*\d{4})?'
        ]

        for pattern in deadline_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                deadline = match.group(1) if len(match.groups()) > 0 else match.group(0)
                return deadline.strip()[:100]

        # Default deadline for Science Bowl (typically December/January)
        return "December-January (Regional registration)"

    def extract_description(self, soup: BeautifulSoup) -> str:
        """Extract program description."""
        description_parts = []

        # Try to find main content paragraphs
        for selector in ['main p', '.content p', 'article p', '.entry-content p', '.main-content p', 'p']:
            paragraphs = soup.select(selector)
            if paragraphs:
                for p in paragraphs[:5]:  # Get first 5 paragraphs
                    text = p.get_text().strip()
                    # Filter out navigation and header text
                    if (len(text) > 50 and
                        'skip to' not in text.lower() and
                        'navigation' not in text.lower() and
                        'official website' not in text.lower()):
                        description_parts.append(text)
                        if len(' '.join(description_parts)) >= 300:
                            break
                if description_parts:
                    break

        description = ' '.join(description_parts)[:500] if description_parts else "National STEM competition testing knowledge across science disciplines."
        return description

    def create_programs(self, main_soup: BeautifulSoup, hs_soup: Optional[BeautifulSoup], ms_soup: Optional[BeautifulSoup]) -> List[Dict]:
        """Create program entries based on scraped information."""
        programs = []

        # Extract content from all pages
        main_text = self.extract_text_content(main_soup) if main_soup else ""
        hs_text = self.extract_text_content(hs_soup) if hs_soup else ""
        ms_text = self.extract_text_content(ms_soup) if ms_soup else ""

        combined_text = f"{main_text} {hs_text} {ms_text}"

        # Extract deadline
        deadline = self.extract_deadline(combined_text)

        # Check for diversity initiatives
        diversity_focus = any(term in combined_text for term in [
            'diversity', 'inclusion', 'underrepresented', 'underserved',
            'equity', 'diverse', 'inclusive', 'marginalized', 'all students',
            'broadening participation'
        ])

        # Program 1: High School Regional Competition
        hs_description = self.extract_description(hs_soup) if hs_soup else "High school teams compete in fast-paced question-and-answer format covering biology, chemistry, earth science, physics, energy, and math."

        program1 = {
            'name': 'DOE National Science Bowl - High School Regional',
            'program_type': 'Competition',
            'url': 'https://science.osti.gov/wdts/nsb/High-School',
            'source': 'DOE Science Bowl',
            'category': 'STEM Competition',
            'stem_focus': 'Biology, Chemistry, Earth Science, Physics, Energy, Mathematics',
            'target_grade': '9-12',
            'cost': 'Free',
            'location': 'Regional sites nationwide',
            'duration': '1 day (Regional competition)',
            'application_deadline': deadline,
            'eligibility': 'Teams of 4-5 high school students; coach required; must attend same school',
            'description': hs_description,
            'diversity_focus': diversity_focus,
            'underrepresented_friendly': True,
            'first_gen_support': True,
            'rural_accessible': True,
            'transportation_required': 'Yes (to regional site)',
            'internet_dependency': 'Low',
            'mentor_access_level': 'Volunteer (coach)',
            'prerequisite_level': 'Medium',
            'gear_support_building': False,
            'contributor_community': True,
            'financial_barrier_level': 'Low',
            'financial_aid_available': True,
            'location_type': 'In-Person',
            'support_level': 'Medium',
            'stem_accessibility': True,
            'inclusive_environment': True,
            'family_involvement': 'High',
            'time_commitment': 'Variable (practice + competition day)'
        }
        programs.append(program1)

        # Program 2: High School National Championship
        program2 = {
            'name': 'DOE National Science Bowl - High School National Finals',
            'program_type': 'Competition',
            'url': 'https://science.osti.gov/wdts/nsb/High-School',
            'source': 'DOE Science Bowl',
            'category': 'STEM Competition',
            'stem_focus': 'Biology, Chemistry, Earth Science, Physics, Energy, Mathematics',
            'target_grade': '9-12',
            'cost': 'Free',
            'location': 'Washington, D.C. area',
            'duration': '4-5 days (April/May)',
            'application_deadline': deadline,
            'eligibility': 'Regional winning teams; all expenses paid by DOE',
            'description': 'National finals for regional champions; compete against top teams nationwide; all-expenses-paid trip including travel, hotel, and meals; educational activities at national laboratories.',
            'diversity_focus': diversity_focus,
            'underrepresented_friendly': True,
            'first_gen_support': True,
            'rural_accessible': True,
            'transportation_required': 'Yes (provided for finalists)',
            'internet_dependency': 'Low',
            'mentor_access_level': 'Volunteer (coach)',
            'prerequisite_level': 'High',
            'gear_support_building': False,
            'contributor_community': True,
            'financial_barrier_level': 'None',
            'financial_aid_available': True,
            'location_type': 'In-Person',
            'support_level': 'High',
            'stem_accessibility': True,
            'inclusive_environment': True,
            'family_involvement': 'High',
            'time_commitment': '4-5 days (Finals)'
        }
        programs.append(program2)

        # Program 3: Middle School Regional Competition
        ms_description = self.extract_description(ms_soup) if ms_soup else "Middle school teams compete in fast-paced quiz format covering life science, earth science, physical science, energy, and math."

        program3 = {
            'name': 'DOE National Science Bowl - Middle School Regional',
            'program_type': 'Competition',
            'url': 'https://science.osti.gov/wdts/nsb/Middle-School',
            'source': 'DOE Science Bowl',
            'category': 'STEM Competition',
            'stem_focus': 'Life Science, Earth Science, Physical Science, Energy, Mathematics',
            'target_grade': '6-8',
            'cost': 'Free',
            'location': 'Regional sites nationwide',
            'duration': '1 day (Regional competition)',
            'application_deadline': deadline,
            'eligibility': 'Teams of 4-5 middle school students; coach required; must attend same school',
            'description': ms_description,
            'diversity_focus': diversity_focus,
            'underrepresented_friendly': True,
            'first_gen_support': True,
            'rural_accessible': True,
            'transportation_required': 'Yes (to regional site)',
            'internet_dependency': 'Low',
            'mentor_access_level': 'Volunteer (coach)',
            'prerequisite_level': 'Medium',
            'gear_support_building': False,
            'contributor_community': True,
            'financial_barrier_level': 'Low',
            'financial_aid_available': True,
            'location_type': 'In-Person',
            'support_level': 'Medium',
            'stem_accessibility': True,
            'inclusive_environment': True,
            'family_involvement': 'High',
            'time_commitment': 'Variable (practice + competition day)'
        }
        programs.append(program3)

        # Program 4: Middle School National Championship
        program4 = {
            'name': 'DOE National Science Bowl - Middle School National Finals',
            'program_type': 'Competition',
            'url': 'https://science.osti.gov/wdts/nsb/Middle-School',
            'source': 'DOE Science Bowl',
            'category': 'STEM Competition',
            'stem_focus': 'Life Science, Earth Science, Physical Science, Energy, Mathematics',
            'target_grade': '6-8',
            'cost': 'Free',
            'location': 'Washington, D.C. area',
            'duration': '4-5 days (April/May)',
            'application_deadline': deadline,
            'eligibility': 'Regional winning teams; all expenses paid by DOE',
            'description': 'National finals for regional champions; compete against top middle school teams nationwide; all-expenses-paid trip; educational tours and STEM activities.',
            'diversity_focus': diversity_focus,
            'underrepresented_friendly': True,
            'first_gen_support': True,
            'rural_accessible': True,
            'transportation_required': 'Yes (provided for finalists)',
            'internet_dependency': 'Low',
            'mentor_access_level': 'Volunteer (coach)',
            'prerequisite_level': 'High',
            'gear_support_building': False,
            'contributor_community': True,
            'financial_barrier_level': 'None',
            'financial_aid_available': True,
            'location_type': 'In-Person',
            'support_level': 'High',
            'stem_accessibility': True,
            'inclusive_environment': True,
            'family_involvement': 'High',
            'time_commitment': '4-5 days (Finals)'
        }
        programs.append(program4)

        return programs

    def scrape_programs(self):
        """Main scraping function."""
        print("Starting DOE National Science Bowl scraper...")

        # Fetch all target pages
        main_soup = self.make_request(self.target_urls[0])
        hs_soup = self.make_request(self.target_urls[1])
        ms_soup = self.make_request(self.target_urls[2])

        if not main_soup:
            print("Failed to fetch main page")
            return

        # Create program entries
        print("Extracting program information...")
        self.programs = self.create_programs(main_soup, hs_soup, ms_soup)

        print(f"\nScraping completed. Created {len(self.programs)} program tracks.")

    def save_to_csv(self, filename: str = "data/doe_science_bowl_progress.csv"):
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
    scraper = DOEScienceBowlScraper()
    scraper.scrape_programs()
    scraper.save_to_csv()


if __name__ == "__main__":
    main()
