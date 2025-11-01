#!/usr/bin/env python3
"""
NSF STEM Programs Scraper

Scrapes NSF education funding programs from https://www.nsf.gov/edu/programs
and extracts detailed program information by following program links.
"""

import requests
from bs4 import BeautifulSoup
import csv
import time
import re
import os
from urllib.parse import urljoin, urlparse
from typing import List, Dict, Optional


class NSFScraper:
    def __init__(self):
        self.base_url = "https://www.nsf.gov"
        self.start_url = "https://www.nsf.gov/edu/programs"
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
    
    def extract_program_links(self, soup: BeautifulSoup) -> List[str]:
        """Extract program funding opportunity links from the main education page."""
        program_links = []
        
        # Look for links to funding opportunities
        for link in soup.find_all('a', href=True):
            href = link.get('href', '')
            
            # Target funding opportunity pages
            if ('/funding/opportunities/' in href or 
                '/funding/pgm_summ.jsp' in href or
                'nsf.gov/pubs' in href):
                
                # Convert relative URLs to absolute
                full_url = urljoin(self.base_url, href)
                if full_url not in program_links:
                    program_links.append(full_url)
        
        return program_links
    
    def extract_program_info(self, url: str, soup: BeautifulSoup) -> Optional[Dict]:
        """Extract program information from a program page."""
        try:
            # Extract program name (try multiple selectors)
            name = None
            for selector in ['h1', '.pageTitle', 'title', '.programTitle']:
                title_elem = soup.select_one(selector)
                if title_elem:
                    name = title_elem.get_text().strip()
                    # Clean up title
                    name = re.sub(r'\s*\|\s*NSF.*$', '', name)
                    name = re.sub(r'\s*-\s*National Science Foundation.*$', '', name)
                    break
            
            if not name:
                return None
            
            # Extract description (first few paragraphs, skip header content)
            description = ""
            # Look for main content areas, avoiding headers and navigation
            content_selectors = [
                '#main-content p', '.content-body p', '.program-description p',
                '.summary p', '.overview p', 'main p', '.description p'
            ]
            
            for selector in content_selectors:
                paragraphs = soup.select(selector)
                if paragraphs:
                    desc_parts = []
                    for p in paragraphs:
                        text = p.get_text().strip()
                        # Skip common header/footer text
                        if (len(text) > 30 and 
                            'official website' not in text.lower() and
                            'government organization' not in text.lower() and
                            '.gov website' not in text.lower() and
                            'national science foundation' not in text.lower() and
                            'skip to main content' not in text.lower()):
                            desc_parts.append(text)
                        if len(' '.join(desc_parts)) >= 400:  # Stop at ~400 chars
                            break
                    if desc_parts:
                        description = ' '.join(desc_parts)[:500]  # Limit to 500 chars
                        break
            
            # If still no good description, try broader search
            if not description:
                all_paragraphs = soup.find_all('p')
                for p in all_paragraphs:
                    text = p.get_text().strip()
                    if (len(text) > 50 and 
                        'official website' not in text.lower() and
                        'government organization' not in text.lower() and
                        '.gov website' not in text.lower() and
                        any(keyword in text.lower() for keyword in ['program', 'research', 'education', 'student', 'funding'])):
                        description = text[:500]
                        break
            
            # Extract deadline information
            deadline = ""
            deadline_text = soup.get_text().lower()
            deadline_patterns = [
                r'deadline[s]?[:\s]+([^.]+)',
                r'due date[s]?[:\s]+([^.]+)',
                r'application[s]?\s+due[:\s]+([^.]+)',
                r'proposals?\s+due[:\s]+([^.]+)',
                r'submit[ted]*\s+by[:\s]+([^.]+)'
            ]
            
            for pattern in deadline_patterns:
                match = re.search(pattern, deadline_text)
                if match:
                    deadline = match.group(1).strip()[:100]  # Limit length
                    break
            
            # Extract target audience - FILTER FOR K-12 ONLY
            target_audience = ""
            audience_text = soup.get_text().lower()
            
            # Check if this program is for K-12 students (not teachers, researchers, or institutions)
            has_k12_mention = any(term in audience_text for term in [
                'k-12', 'k12', 'prek-12', 'pre-k', 'prekindergarten', 
                'elementary', 'secondary', 'middle school', 'high school'
            ])
            
            has_student_focus = any(term in audience_text for term in [
                'student', 'students', 'youth', 'children', 'kids'
            ])
            
            # Exclude teacher/educator/researcher focused programs
            is_teacher_focused = any(term in audience_text for term in [
                'teacher', 'educator', 'faculty', 'instructor', 'teaching',
                'teacher scholarship', 'teacher training', 'teacher preparation',
                'teacher development', 'teacher education', 'teacher corps',
                'postdoctoral', 'graduate', 'undergraduate', 'fellowship',
                'researcher', 'research training', 'faculty development'
            ])
            
            # Exclude institutional/research programs
            is_institutional = any(term in audience_text for term in [
                'institution', 'university', 'college', 'research project',
                'principal investigator', 'curriculum development'
            ])
            
            # Only include if it mentions K-12 AND students AND is not teacher/research focused
            if not (has_k12_mention and has_student_focus and not is_teacher_focused and not is_institutional):
                return None
            
            target_audience = 'K-12'
            
            # Extract contextual fields
            full_text = soup.get_text().lower()
            
            # Prerequisite level
            prerequisite_level = "None"
            if any(term in full_text for term in ['advanced', 'expert', 'prior experience required']):
                prerequisite_level = "Advanced"
            elif any(term in full_text for term in ['intermediate', 'some experience', 'basic knowledge']):
                prerequisite_level = "Intermediate"
            elif any(term in full_text for term in ['beginner', 'basic', 'introductory']):
                prerequisite_level = "Basic"
            
            # Time commitment
            time_commitment = ""
            time_patterns = [
                r'(\d+)\s*hours?\s*per\s*week',
                r'(\d+)\s*weeks?',
                r'(\d+)\s*months?',
                r'(\d+)\s*years?',
                r'(\d+)\s*days?',
                r'full-time',
                r'part-time'
            ]
            for pattern in time_patterns:
                match = re.search(pattern, full_text)
                if match:
                    if pattern == r'full-time':
                        time_commitment = "Full-time"
                    elif pattern == r'part-time':
                        time_commitment = "Part-time"
                    else:
                        time_commitment = match.group(0)
                    break
            
            # Support level
            support_level = "Medium"
            if any(term in full_text for term in ['mentorship', 'mentor', 'guidance', 'supervision', 'coaching']):
                support_level = "High"
            elif any(term in full_text for term in ['independent', 'self-directed', 'autonomous']):
                support_level = "Low"
            
            # Geographic scope
            geographic_scope = "National"
            if any(term in full_text for term in ['online only', 'virtual', 'remote only']):
                geographic_scope = "Online-Only"
            elif any(term in full_text for term in ['regional', 'state', 'multi-state']):
                geographic_scope = "Regional"
            elif any(term in full_text for term in ['local', 'district', 'community']):
                geographic_scope = "Local"
            
            # First-generation friendly
            first_gen_friendly = any(term in full_text for term in [
                'first-generation', 'first generation', 'first-gen', 'first gen',
                'family college history', 'parents without college'
            ])
            
            # Underrepresented focus
            underrepresented_focus = any(term in full_text for term in [
                'diversity', 'inclusion', 'underrepresented', 'underserved',
                'historically excluded', 'minority', 'equity', 'diverse',
                'broadening participation', 'inclusive', 'marginalized'
            ])
            
            return {
                'program_name': name,
                'description': description,
                'url': url,
                'deadline': deadline,
                'target_audience': target_audience,
                'source': 'NSF',
                'category': 'Federal Program',
                'stem_fields': 'All STEM',
                'cost': 'Free',
                'location_type': 'National',
                'prerequisite_level': prerequisite_level,
                'time_commitment': time_commitment,
                'support_level': support_level,
                'geographic_scope': geographic_scope,
                'first_gen_friendly': first_gen_friendly,
                'underrepresented_focus': underrepresented_focus
            }
            
        except Exception as e:
            print(f"Error extracting info from {url}: {e}")
            return None
    
    def scrape_programs(self):
        """Main scraping function."""
        print("Starting NSF STEM programs scraper...")
        
        # Get the main education programs page
        soup = self.make_request(self.start_url)
        if not soup:
            print("Failed to fetch main page")
            return
        
        # Extract program links
        print("Extracting program links...")
        program_links = self.extract_program_links(soup)
        print(f"Found {len(program_links)} potential program links")
        
        # Process each program link
        for i, link in enumerate(program_links[:20], 1):  # Limit to first 20 for testing
            print(f"Processing program {i}/{min(20, len(program_links))}: {link}")
            
            program_soup = self.make_request(link)
            if program_soup:
                program_info = self.extract_program_info(link, program_soup)
                if program_info:
                    self.programs.append(program_info)
                    print(f" Extracted: {program_info['program_name']}")
                else:
                    print(f" No valid program info found")
            
        print(f"\nScraping completed. Found {len(self.programs)} programs.")
    
    def save_to_csv(self, filename: str = "data/nsf_programs_students_only.csv"):
        """Save scraped programs to CSV file."""
        if not self.programs:
            print("No programs to save")
            return
        
        # Ensure data directory exists
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        
        fieldnames = [
            'program_name', 'description', 'url', 'deadline', 'target_audience',
            'source', 'category', 'stem_fields', 'cost', 'location_type',
            'prerequisite_level', 'time_commitment', 'support_level', 
            'geographic_scope', 'first_gen_friendly', 'underrepresented_focus'
        ]
        
        try:
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(self.programs)
            
            print(f"Saved {len(self.programs)} programs to {filename}")
            
        except Exception as e:
            print(f"Error saving to CSV: {e}")


def main():
    """Main function to run the scraper."""
    scraper = NSFScraper()
    scraper.scrape_programs()
    scraper.save_to_csv()


if __name__ == "__main__":
    main()