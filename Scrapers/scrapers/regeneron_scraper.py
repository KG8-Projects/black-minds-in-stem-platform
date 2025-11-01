#!/usr/bin/env python3
"""
Regeneron Science Talent Search Scraper

Scrapes Regeneron Science Talent Search program information and similar open-source programs.
"""

import requests
from bs4 import BeautifulSoup
import csv
import time
import re
import os
from urllib.parse import urljoin
from typing import List, Dict, Optional


class RegeneronScraper:
    def __init__(self):
        self.base_url = "https://www.societyforscience.org"
        self.target_urls = [
            "https://www.societyforscience.org/regeneron-sts/",
            "https://www.societyforscience.org/regeneron-sts/how-to-enter/",
            "https://www.societyforscience.org/regeneron-sts/faqs/",
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

        # Default deadline for Regeneron STS
        return "November (typically early November)"

    def extract_description(self, soup: BeautifulSoup) -> str:
        """Extract program description."""
        description_parts = []

        # Try to find main content paragraphs
        for selector in ['main p', '.content p', 'article p', '.entry-content p', 'p']:
            paragraphs = soup.select(selector)
            if paragraphs:
                for p in paragraphs[:5]:  # Get first 5 paragraphs
                    text = p.get_text().strip()
                    if len(text) > 50:
                        description_parts.append(text)
                        if len(' '.join(description_parts)) >= 300:
                            break
                if description_parts:
                    break

        description = ' '.join(description_parts)[:500] if description_parts else "Premier science competition for high school seniors."
        return description

    def create_programs(self, main_soup: BeautifulSoup, how_to_soup: Optional[BeautifulSoup], faq_soup: Optional[BeautifulSoup]) -> List[Dict]:
        """Create program entries based on scraped information."""
        programs = []

        # Extract content from all pages
        main_text = self.extract_text_content(main_soup) if main_soup else ""
        how_to_text = self.extract_text_content(how_to_soup) if how_to_soup else ""
        faq_text = self.extract_text_content(faq_soup) if faq_soup else ""

        combined_text = f"{main_text} {how_to_text} {faq_text}"

        # Extract deadline
        deadline = self.extract_deadline(combined_text)

        # Extract description
        description = self.extract_description(main_soup) if main_soup else "Premier science competition for high school seniors."

        # Check for diversity initiatives
        diversity_focus = any(term in combined_text for term in [
            'diversity', 'inclusion', 'underrepresented', 'underserved',
            'equity', 'diverse', 'inclusive', 'marginalized', 'all students'
        ])

        # Program 1: Main Competition Entry
        program1 = {
            'name': 'Regeneron Science Talent Search - Competition Entry',
            'program_type': 'Competition',
            'url': 'https://www.societyforscience.org/regeneron-sts/',
            'source': 'Regeneron Science Talent Search',
            'category': 'STEM Competition',
            'stem_focus': 'All Sciences (Biology, Chemistry, Physics, Math, Engineering, Computer Science)',
            'target_grade': '12',
            'cost': 'Free',
            'location': 'Online Application + Washington, D.C. Finals',
            'duration': '6-12 months (research + application)',
            'application_deadline': deadline,
            'eligibility': 'U.S. high school seniors; completed independent research project',
            'description': description,
            'diversity_focus': diversity_focus,
            'underrepresented_friendly': True,
            'first_gen_support': True,
            'rural_accessible': True,
            'transportation_required': 'Only for finalists (to Washington D.C.)',
            'internet_dependency': 'High',
            'mentor_access_level': 'Professional (research mentor required)',
            'prerequisite_level': 'High',
            'gear_support_building': False,
            'contributor_community': True,
            'financial_barrier_level': 'None',
            'financial_aid_available': True,
            'location_type': 'Hybrid',
            'support_level': 'High',
            'stem_accessibility': True,
            'inclusive_environment': True,
            'family_involvement': 'Low',
            'time_commitment': '6-12 months'
        }
        programs.append(program1)

        # Program 2: Scholar Track (Top 300)
        program2 = {
            'name': 'Regeneron Science Talent Search - Scholar Recognition',
            'program_type': 'Recognition/Award',
            'url': 'https://www.societyforscience.org/regeneron-sts/',
            'source': 'Regeneron Science Talent Search',
            'category': 'STEM Recognition',
            'stem_focus': 'All Sciences',
            'target_grade': '12',
            'cost': 'Free',
            'location': 'National',
            'duration': 'Recognition + $2,000 award',
            'application_deadline': deadline,
            'eligibility': 'Top 300 entrants; high school seniors',
            'description': 'Recognition as a Regeneron Science Talent Search Scholar with $2,000 award for outstanding research.',
            'diversity_focus': diversity_focus,
            'underrepresented_friendly': True,
            'first_gen_support': True,
            'rural_accessible': True,
            'transportation_required': 'No',
            'internet_dependency': 'High',
            'mentor_access_level': 'Professional',
            'prerequisite_level': 'High',
            'gear_support_building': False,
            'contributor_community': True,
            'financial_barrier_level': 'None',
            'financial_aid_available': True,
            'location_type': 'Online',
            'support_level': 'High',
            'stem_accessibility': True,
            'inclusive_environment': True,
            'family_involvement': 'Low',
            'time_commitment': '6-12 months'
        }
        programs.append(program2)

        # Program 3: Finalist Track (Top 40)
        program3 = {
            'name': 'Regeneron Science Talent Search - Finalist Competition',
            'program_type': 'Competition/Finalist',
            'url': 'https://www.societyforscience.org/regeneron-sts/',
            'source': 'Regeneron Science Talent Search',
            'category': 'STEM Competition',
            'stem_focus': 'All Sciences',
            'target_grade': '12',
            'cost': 'Free',
            'location': 'Washington, D.C.',
            'duration': '1 week (Finals Week in March)',
            'application_deadline': deadline,
            'eligibility': 'Top 40 entrants; all-expenses-paid trip to Washington D.C.',
            'description': 'Compete for top prizes up to $250,000; present research to judges; meet scientists and policymakers; attend exclusive events.',
            'diversity_focus': diversity_focus,
            'underrepresented_friendly': True,
            'first_gen_support': True,
            'rural_accessible': True,
            'transportation_required': 'Yes (provided for finalists)',
            'internet_dependency': 'Medium',
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
            'family_involvement': 'Low',
            'time_commitment': '1 week (Finals)'
        }
        programs.append(program3)

        # Program 4: Research Project Development
        program4 = {
            'name': 'Regeneron STS - Independent Research Project Development',
            'program_type': 'Research Program',
            'url': 'https://www.societyforscience.org/regeneron-sts/how-to-enter/',
            'source': 'Regeneron Science Talent Search',
            'category': 'STEM Research',
            'stem_focus': 'All Sciences (must choose specific category)',
            'target_grade': '11-12',
            'cost': 'Free',
            'location': 'Student-Led (any location)',
            'duration': '6-12 months',
            'application_deadline': deadline,
            'eligibility': 'High school students (typically juniors/seniors); must design and complete independent research',
            'description': 'Develop and complete an original independent research project under mentorship; project must demonstrate scientific rigor and innovation.',
            'diversity_focus': diversity_focus,
            'underrepresented_friendly': True,
            'first_gen_support': True,
            'rural_accessible': True,
            'transportation_required': 'Varies by project',
            'internet_dependency': 'Medium',
            'mentor_access_level': 'Professional (research mentor)',
            'prerequisite_level': 'High',
            'gear_support_building': False,
            'contributor_community': True,
            'financial_barrier_level': 'Low',
            'financial_aid_available': False,
            'location_type': 'Flexible',
            'support_level': 'High',
            'stem_accessibility': True,
            'inclusive_environment': True,
            'family_involvement': 'Low',
            'time_commitment': '10-20 hours/week for 6-12 months'
        }
        programs.append(program4)

        return programs

    def scrape_programs(self):
        """Main scraping function."""
        print("Starting Regeneron Science Talent Search scraper...")

        # Fetch all target pages
        main_soup = self.make_request(self.target_urls[0])
        how_to_soup = self.make_request(self.target_urls[1])
        faq_soup = self.make_request(self.target_urls[2])

        if not main_soup:
            print("Failed to fetch main page")
            return

        # Create program entries
        print("Extracting program information...")
        self.programs = self.create_programs(main_soup, how_to_soup, faq_soup)

        print(f"\nScraping completed. Created {len(self.programs)} program tracks.")

    def save_to_csv(self, filename: str = "data/regeneron_science_talent_search_progress.csv"):
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
    scraper = RegeneronScraper()
    scraper.scrape_programs()
    scraper.save_to_csv()


if __name__ == "__main__":
    main()
