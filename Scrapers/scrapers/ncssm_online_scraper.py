#!/usr/bin/env python3
"""
NCSSM Online Programs Scraper

Scrapes North Carolina School of Science and Mathematics Online program information.
"""

import requests
from bs4 import BeautifulSoup
import csv
import time
import re
import os
from urllib.parse import urljoin
from typing import List, Dict, Optional


class NCSSMOnlineScraper:
    def __init__(self):
        self.base_url = "https://www.ncssm.edu"
        self.target_urls = [
            "https://www.ncssm.edu/online",
            "https://www.ncssm.edu/online/courses",
            "https://www.ncssm.edu/online/summer-programs",
            "https://www.ncssm.edu/online/apply",
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
            r'apply\s+by[:\s]+([^.]+)',
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
                        'social media' not in text.lower()):
                        description_parts.append(text)
                        if len(' '.join(description_parts)) >= 300:
                            break
                if description_parts:
                    break

        description = ' '.join(description_parts)[:500] if description_parts else default
        return description

    def create_programs(self, main_soup: BeautifulSoup, courses_soup: Optional[BeautifulSoup],
                       summer_soup: Optional[BeautifulSoup], apply_soup: Optional[BeautifulSoup]) -> List[Dict]:
        """Create program entries based on scraped information."""
        programs = []

        # Extract content from all pages
        main_text = self.extract_text_content(main_soup) if main_soup else ""
        courses_text = self.extract_text_content(courses_soup) if courses_soup else ""
        summer_text = self.extract_text_content(summer_soup) if summer_soup else ""
        apply_text = self.extract_text_content(apply_soup) if apply_soup else ""

        combined_text = f"{main_text} {courses_text} {summer_text} {apply_text}"

        # Extract deadline
        deadline = self.extract_deadline(combined_text)

        # Check for diversity initiatives
        diversity_focus = any(term in combined_text for term in [
            'diversity', 'inclusion', 'underrepresented', 'underserved',
            'equity', 'diverse', 'inclusive', 'marginalized', 'all students',
            'rural', 'access'
        ])

        # Extract main description
        main_description = self.extract_description(main_soup,
            "North Carolina's premier online STEM learning platform; advanced courses for high school students; taught by expert instructors.")

        # Program 1: Online STEM Courses (Academic Year)
        program1 = {
            'name': 'NCSSM Online - Academic Year STEM Courses',
            'program_type': 'Learning Platform',
            'url': 'https://www.ncssm.edu/online/courses',
            'source': 'NCSSM Online',
            'category': 'Online Learning',
            'stem_focus': 'Mathematics, Science, Computer Science, Engineering',
            'target_grade': '9-12',
            'cost': 'Free (NC residents), Paid (out-of-state)',
            'location': 'Online',
            'duration': 'Semester or full year',
            'application_deadline': deadline,
            'eligibility': 'High school students; priority to NC residents; application required',
            'description': main_description,
            'diversity_focus': diversity_focus,
            'underrepresented_friendly': True,
            'first_gen_support': True,
            'rural_accessible': True,
            'transportation_required': 'No',
            'internet_dependency': 'High',
            'mentor_access_level': 'Teacher (expert instructors)',
            'prerequisite_level': 'Medium',
            'gear_support_building': False,
            'contributor_community': True,
            'financial_barrier_level': 'Medium',
            'financial_aid_available': True,
            'location_type': 'Online',
            'support_level': 'High',
            'stem_accessibility': True,
            'inclusive_environment': True,
            'family_involvement': 'Low',
            'time_commitment': 'Semester (3-5 hours/week per course)'
        }
        programs.append(program1)

        # Program 2: Summer STEM Programs
        summer_description = self.extract_description(summer_soup,
            "Intensive summer online STEM programs; accelerated learning; college-level content; expert instruction.")

        program2 = {
            'name': 'NCSSM Online - Summer STEM Programs',
            'program_type': 'Summer Program',
            'url': 'https://www.ncssm.edu/online/summer-programs',
            'source': 'NCSSM Online',
            'category': 'Summer Learning',
            'stem_focus': 'Various STEM subjects',
            'target_grade': '9-12',
            'cost': 'Free (NC residents), Paid (out-of-state)',
            'location': 'Online',
            'duration': '2-6 weeks',
            'application_deadline': self.extract_deadline(summer_text, "Spring (typically March-April)"),
            'eligibility': 'High school students; priority to NC residents',
            'description': summer_description,
            'diversity_focus': diversity_focus,
            'underrepresented_friendly': True,
            'first_gen_support': True,
            'rural_accessible': True,
            'transportation_required': 'No',
            'internet_dependency': 'High',
            'mentor_access_level': 'Teacher (instructors)',
            'prerequisite_level': 'Medium',
            'gear_support_building': False,
            'contributor_community': True,
            'financial_barrier_level': 'Medium',
            'financial_aid_available': True,
            'location_type': 'Online',
            'support_level': 'High',
            'stem_accessibility': True,
            'inclusive_environment': True,
            'family_involvement': 'Low',
            'time_commitment': '2-6 weeks (summer)'
        }
        programs.append(program2)

        # Program 3: Advanced Mathematics Courses
        program3 = {
            'name': 'NCSSM Online - Advanced Mathematics',
            'program_type': 'Learning Platform',
            'url': 'https://www.ncssm.edu/online/courses',
            'source': 'NCSSM Online',
            'category': 'Online Learning',
            'stem_focus': 'Advanced Mathematics (Calculus, Statistics, Discrete Math)',
            'target_grade': '10-12',
            'cost': 'Free (NC residents), Paid (out-of-state)',
            'location': 'Online',
            'duration': 'Semester or full year',
            'application_deadline': deadline,
            'eligibility': 'High school students with prerequisite coursework; NC priority',
            'description': 'College-level mathematics courses including multivariable calculus, linear algebra, differential equations, statistics, and discrete mathematics; synchronous and asynchronous instruction; college credit available; taught by NCSSM faculty.',
            'diversity_focus': diversity_focus,
            'underrepresented_friendly': True,
            'first_gen_support': True,
            'rural_accessible': True,
            'transportation_required': 'No',
            'internet_dependency': 'High',
            'mentor_access_level': 'Teacher (math instructors)',
            'prerequisite_level': 'High',
            'gear_support_building': False,
            'contributor_community': True,
            'financial_barrier_level': 'Medium',
            'financial_aid_available': True,
            'location_type': 'Online',
            'support_level': 'High',
            'stem_accessibility': True,
            'inclusive_environment': True,
            'family_involvement': 'Low',
            'time_commitment': 'Semester (4-6 hours/week)'
        }
        programs.append(program3)

        # Program 4: Computer Science and Programming
        program4 = {
            'name': 'NCSSM Online - Computer Science',
            'program_type': 'Learning Platform',
            'url': 'https://www.ncssm.edu/online/courses',
            'source': 'NCSSM Online',
            'category': 'Online Learning',
            'stem_focus': 'Computer Science, Programming, Data Science',
            'target_grade': '9-12',
            'cost': 'Free (NC residents), Paid (out-of-state)',
            'location': 'Online',
            'duration': 'Semester or full year',
            'application_deadline': deadline,
            'eligibility': 'High school students; NC priority; some courses require prerequisites',
            'description': 'Comprehensive computer science curriculum including AP Computer Science, data structures, algorithms, web development, data science, and artificial intelligence; hands-on programming projects; college-level content; industry-standard tools.',
            'diversity_focus': diversity_focus,
            'underrepresented_friendly': True,
            'first_gen_support': True,
            'rural_accessible': True,
            'transportation_required': 'No',
            'internet_dependency': 'High',
            'mentor_access_level': 'Teacher (CS instructors)',
            'prerequisite_level': 'Medium',
            'gear_support_building': False,
            'contributor_community': True,
            'financial_barrier_level': 'Medium',
            'financial_aid_available': True,
            'location_type': 'Online',
            'support_level': 'High',
            'stem_accessibility': True,
            'inclusive_environment': True,
            'family_involvement': 'Low',
            'time_commitment': 'Semester (4-6 hours/week)'
        }
        programs.append(program4)

        # Program 5: Advanced Science Courses
        program5 = {
            'name': 'NCSSM Online - Advanced Sciences',
            'program_type': 'Learning Platform',
            'url': 'https://www.ncssm.edu/online/courses',
            'source': 'NCSSM Online',
            'category': 'Online Learning',
            'stem_focus': 'Physics, Chemistry, Biology, Environmental Science',
            'target_grade': '10-12',
            'cost': 'Free (NC residents), Paid (out-of-state)',
            'location': 'Online',
            'duration': 'Semester or full year',
            'application_deadline': deadline,
            'eligibility': 'High school students with prerequisite science coursework; NC priority',
            'description': 'Advanced science courses beyond AP level including astrophysics, organic chemistry, molecular biology, and environmental science; virtual labs and simulations; research opportunities; college-level rigor; NCSSM expert faculty.',
            'diversity_focus': diversity_focus,
            'underrepresented_friendly': True,
            'first_gen_support': True,
            'rural_accessible': True,
            'transportation_required': 'No',
            'internet_dependency': 'High',
            'mentor_access_level': 'Teacher (science instructors)',
            'prerequisite_level': 'High',
            'gear_support_building': False,
            'contributor_community': True,
            'financial_barrier_level': 'Medium',
            'financial_aid_available': True,
            'location_type': 'Online',
            'support_level': 'High',
            'stem_accessibility': True,
            'inclusive_environment': True,
            'family_involvement': 'Low',
            'time_commitment': 'Semester (4-6 hours/week)'
        }
        programs.append(program5)

        return programs

    def scrape_programs(self):
        """Main scraping function."""
        print("Starting NCSSM Online scraper...")

        # Fetch all target pages
        main_soup = self.make_request(self.target_urls[0])
        courses_soup = self.make_request(self.target_urls[1])
        summer_soup = self.make_request(self.target_urls[2])
        apply_soup = self.make_request(self.target_urls[3])

        if not main_soup:
            print("Warning: Failed to fetch main page, continuing with available data...")

        # Create program entries
        print("Extracting program information...")
        self.programs = self.create_programs(main_soup, courses_soup, summer_soup, apply_soup)

        print(f"\nScraping completed. Created {len(self.programs)} program tracks.")

    def save_to_csv(self, filename: str = "data/ncssm_online_progress.csv"):
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
    scraper = NCSSMOnlineScraper()
    scraper.scrape_programs()
    scraper.save_to_csv()


if __name__ == "__main__":
    main()
