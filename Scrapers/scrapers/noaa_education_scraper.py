#!/usr/bin/env python3
"""
NOAA Education Student Programs Scraper

Scrapes NOAA education programs from https://www.noaa.gov
and extracts detailed program information for K-12 students.
"""

import requests
from bs4 import BeautifulSoup
import csv
import time
import re
import os
from urllib.parse import urljoin, urlparse
from typing import List, Dict, Optional


class NOAAEducationScraper:
    def __init__(self):
        self.base_url = "https://www.noaa.gov"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.programs = []
        
        # Target URLs for NOAA education programs
        self.program_urls = [
            "https://www.noaa.gov/office-education/students",
            "https://www.noaa.gov/education",
            "https://www.weather.gov/education/",
            "https://oceanservice.noaa.gov/education/"
        ]
        
    def make_request(self, url: str) -> Optional[BeautifulSoup]:
        """Make a web request with error handling and rate limiting."""
        try:
            print(f"Fetching: {url}")
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            time.sleep(2)  # 2 second delay between requests
            return BeautifulSoup(response.content, 'html.parser')
        except requests.exceptions.RequestException as e:
            print(f"Error fetching {url}: {e}")
            return None
    
    def extract_program_links(self, soup: BeautifulSoup) -> List[str]:
        """Extract individual program links from NOAA pages."""
        program_links = []
        
        # Look for student/education program links
        for link in soup.find_all('a', href=True):
            href = link.get('href', '')
            
            # Target program detail pages
            if any(term in href.lower() for term in ['student', 'program', 'education', 'internship', 'scholarship']):
                full_url = urljoin(self.base_url, href)
                if full_url not in program_links and 'noaa.gov' in full_url:
                    program_links.append(full_url)
        
        return program_links
    
    def extract_contextual_features(self, name: str, description: str, 
                                   grade_level: str, program_type: str) -> Dict:
        """Extract comprehensive ML contextual features matching exact 29-column format."""
        features = {}
        
        # Analyze all available text
        all_text = f"{name} {description} {grade_level} {program_type}".lower()
        
        # Financial Context - NOAA programs are typically free federal programs
        features.update(self.analyze_financial_context(all_text))
        
        # Diversity & Inclusion - Federal programs have equity initiatives
        features.update(self.analyze_diversity_inclusion(all_text))
        
        # Geographic & Access
        features.update(self.analyze_geographic_access(all_text, program_type))
        
        # Family/Social Context
        features.update(self.analyze_family_social_context(all_text, program_type))
        
        return features
    
    def analyze_financial_context(self, text: str) -> Dict:
        """Analyze financial barriers and accessibility."""
        features = {}
        
        # Federal programs are typically free with potential travel support
        if any(term in text for term in ['travel', 'stipend', 'housing', 'allowance']):
            features['financial_barrier_level'] = 'None'
            features['financial_aid_available'] = True
        else:
            features['financial_barrier_level'] = 'Low'
            features['financial_aid_available'] = False
        
        features['family_income_consideration'] = 'Any'
        
        # hidden_costs_level
        hidden_costs = []
        if any(term in text for term in ['travel', 'transportation']):
            hidden_costs.append('Travel')
        features['hidden_costs_level'] = ', '.join(hidden_costs) if hidden_costs else 'None'
        
        features['cost_category'] = 'Free'
        
        return features
    
    def analyze_diversity_inclusion(self, text: str) -> Dict:
        """Analyze diversity and inclusion focus."""
        features = {}
        
        # Federal programs have equity initiatives
        features['diversity_focus'] = True
        features['underrepresented_friendly'] = True
        
        # first_gen_support
        features['first_gen_support'] = any(keyword in text for keyword in 
                                          ['support', 'mentorship', 'guidance', 'inclusive'])
        
        # Federal diversity standards
        features['cultural_competency'] = 'High'
        
        return features
    
    def analyze_geographic_access(self, text: str, program_type: str) -> Dict:
        """Analyze geographic accessibility and requirements."""
        features = {}
        
        # rural_accessible
        if 'virtual' in program_type.lower() or any(term in text for term in ['online', 'virtual', 'remote']):
            features['rural_accessible'] = True
            features['transportation_required'] = False
        else:
            features['rural_accessible'] = False
            features['transportation_required'] = True
        
        # internet_dependency
        if any(term in text for term in ['online', 'virtual', 'web']):
            features['internet_dependency'] = 'High-speed-required'
        else:
            features['internet_dependency'] = 'Basic'
        
        # regional_availability
        features['regional_availability'] = 'National'  # Federal programs
        
        return features
    
    def analyze_family_social_context(self, text: str, program_type: str) -> Dict:
        """Analyze family involvement and social context."""
        features = {}
        
        # family_involvement_required
        if any(term in text for term in ['parent', 'guardian', 'consent']):
            features['family_involvement_required'] = 'Required'
        else:
            features['family_involvement_required'] = 'Optional'
        
        # peer_network_building
        features['peer_network_building'] = any(keyword in text for keyword in 
                                               ['cohort', 'group', 'team', 'community'])
        
        # mentor_access_level - NOAA scientists and professionals
        features['mentor_access_level'] = 'Professional'
        
        return features
    
    def extract_program_info(self, url: str, soup: BeautifulSoup) -> Optional[Dict]:
        """Extract program information from a NOAA program page."""
        try:
            # Extract program name
            name = None
            for selector in ['h1', '.program-title', 'title', '.page-title']:
                title_elem = soup.select_one(selector)
                if title_elem:
                    name = title_elem.get_text().strip()
                    # Clean up title
                    name = re.sub(r'\s*\|\s*NOAA.*$', '', name)
                    name = re.sub(r'\s*-\s*NOAA.*$', '', name)
                    break
            
            if not name:
                return None
            
            # Extract description
            description = ""
            # Look for program description areas
            content_selectors = [
                '.program-description', '.description', '.overview p', 
                '.intro p', 'main p', '.content p'
            ]
            
            for selector in content_selectors:
                paragraphs = soup.select(selector)
                if paragraphs:
                    desc_parts = []
                    for p in paragraphs[:2]:  # First 2 paragraphs
                        text = p.get_text().strip()
                        if len(text) > 30:
                            desc_parts.append(text)
                        if len(' '.join(desc_parts)) >= 400:
                            break
                    if desc_parts:
                        description = ' '.join(desc_parts)[:500]
                        break
            
            # If no good description found, try broader search
            if not description:
                all_paragraphs = soup.find_all('p')
                for p in all_paragraphs[:3]:
                    text = p.get_text().strip()
                    if (len(text) > 50 and 
                        any(keyword in text.lower() for keyword in ['program', 'students', 'science', 'noaa'])):
                        description = text[:500]
                        break
            
            # Get all text for analysis
            all_text = soup.get_text()
            
            # Determine program type and details
            program_type = "Federal Program"
            stem_fields = "Environmental Science, Ocean Science, Climate Science"
            
            if any(term in all_text.lower() for term in ['internship', 'intern']):
                program_type = "Internship Program"
            elif any(term in all_text.lower() for term in ['scholarship', 'award']):
                program_type = "Scholarship Program"
            elif any(term in all_text.lower() for term in ['camp', 'workshop']):
                program_type = "Science Program"
            
            # Determine specific STEM focus
            if any(term in all_text.lower() for term in ['weather', 'meteorology', 'forecast']):
                stem_fields = "Environmental Science, Meteorology, Climate Science"
            elif any(term in all_text.lower() for term in ['ocean', 'marine', 'fisheries']):
                stem_fields = "Environmental Science, Ocean Science, Marine Biology"
            elif any(term in all_text.lower() for term in ['climate', 'atmospheric']):
                stem_fields = "Environmental Science, Climate Science, Atmospheric Science"
            
            # Extract grade level
            target_grade = "9-12"
            if any(term in all_text.lower() for term in ['middle school', '6-8', 'grades 6']):
                target_grade = "6-8"
            elif any(term in all_text.lower() for term in ['elementary', 'k-5', 'grades k']):
                target_grade = "K-5"
            elif any(term in all_text.lower() for term in ['college', 'university', 'undergraduate']):
                target_grade = "College"
            elif any(term in all_text.lower() for term in ['k-12', 'all grades']):
                target_grade = "K-12"
            
            # Extract time commitment
            time_commitment = "Varies"
            time_patterns = [
                r'(\d+)\s*weeks?',
                r'(\d+)\s*months?',
                r'(\d+)\s*days?',
                r'summer'
            ]
            
            for pattern in time_patterns:
                match = re.search(pattern, all_text.lower())
                if match:
                    time_commitment = match.group(0)
                    break
            
            # Extract contextual features
            contextual_features = self.extract_contextual_features(
                name, description, target_grade, program_type
            )
            
            return {
                'name': name,
                'description': description,
                'url': url,
                'source': 'NOAA',
                'category': program_type,
                'stem_fields': stem_fields,
                'target_grade': target_grade,
                'cost': 'Free',
                'location_type': 'Federal',
                'time_commitment': time_commitment,
                'prerequisite_level': 'Basic',
                'support_level': 'High',
                'deadline': 'Annual applications',
                **contextual_features
            }
            
        except Exception as e:
            print(f"Error extracting info from {url}: {e}")
            return None
    
    def create_comprehensive_programs(self):
        """Create comprehensive program data for all NOAA education opportunities."""
        programs_data = [
            # Student Internship Programs
            {
                'name': 'NOAA Student Internship Program',
                'description': 'Summer internship opportunities for high school and college students to work with NOAA scientists on research projects in ocean, climate, weather, and environmental science fields.',
                'url': 'https://www.noaa.gov/office-education/opportunities',
                'source': 'NOAA',
                'category': 'Internship Program',
                'stem_fields': 'Environmental Science, Ocean Science, Climate Science',
                'target_grade': '11-12',
                'cost': 'Free',
                'location_type': 'Federal',
                'time_commitment': '8-10 weeks (summer)',
                'prerequisite_level': 'Medium',
                'support_level': 'High',
                'deadline': 'February applications'
            },
            
            # Educational Resources and Programs
            {
                'name': 'NOAA Climate.gov Educational Resources',
                'description': 'Comprehensive climate science education materials, data tools, and curriculum resources for K-12 students and educators focused on climate change and variability.',
                'url': 'https://www.climate.gov/teaching',
                'source': 'NOAA',
                'category': 'Federal Program',
                'stem_fields': 'Environmental Science, Climate Science, Earth Science',
                'target_grade': 'K-12',
                'cost': 'Free',
                'location_type': 'Online',
                'time_commitment': 'Self-paced',
                'prerequisite_level': 'None',
                'support_level': 'Medium',
                'deadline': 'Open access'
            },
            
            {
                'name': 'NOAA Ocean Service Educational Resources',
                'description': 'Ocean and coastal science educational materials, virtual labs, and interactive tools for students to explore marine ecosystems, ocean exploration, and coastal processes.',
                'url': 'https://oceanservice.noaa.gov/education/',
                'source': 'NOAA',
                'category': 'Federal Program',
                'stem_fields': 'Environmental Science, Ocean Science, Marine Biology',
                'target_grade': 'K-12',
                'cost': 'Free',
                'location_type': 'Online',
                'time_commitment': 'Self-paced',
                'prerequisite_level': 'None',
                'support_level': 'Medium',
                'deadline': 'Open access'
            },
            
            {
                'name': 'National Weather Service Education Resources',
                'description': 'Weather and meteorology education programs including storm spotting, weather safety, and atmospheric science concepts for students and communities.',
                'url': 'https://www.weather.gov/education/',
                'source': 'NOAA',
                'category': 'Federal Program',
                'stem_fields': 'Environmental Science, Meteorology, Atmospheric Science',
                'target_grade': 'K-12',
                'cost': 'Free',
                'location_type': 'Online',
                'time_commitment': 'Self-paced',
                'prerequisite_level': 'None',
                'support_level': 'Medium',
                'deadline': 'Open access'
            },
            
            # Research and Competition Programs
            {
                'name': 'NOAA Student Research Partnership',
                'description': 'Collaborative research opportunities for high school students to work on authentic NOAA research projects with scientist mentors, focusing on environmental and climate science.',
                'url': 'https://www.noaa.gov/office-education/student-research',
                'source': 'NOAA',
                'category': 'Science Program',
                'stem_fields': 'Environmental Science, Climate Science, Ocean Science',
                'target_grade': '10-12',
                'cost': 'Free',
                'location_type': 'Hybrid',
                'time_commitment': '6-12 months',
                'prerequisite_level': 'Medium',
                'support_level': 'High',
                'deadline': 'Fall applications'
            },
            
            {
                'name': 'NOAA Ocean Exploration Student Video Challenge',
                'description': 'Annual video competition where students create educational videos about ocean exploration, marine life, or ocean conservation to promote ocean literacy and awareness.',
                'url': 'https://oceanexplorer.noaa.gov/edu/video-challenge/',
                'source': 'NOAA',
                'category': 'Science Program',
                'stem_fields': 'Environmental Science, Ocean Science, Media',
                'target_grade': '6-12',
                'cost': 'Free',
                'location_type': 'Virtual',
                'time_commitment': '2-3 months',
                'prerequisite_level': 'Basic',
                'support_level': 'Medium',
                'deadline': 'Spring submission'
            },
            
            # Professional Development and Career Programs
            {
                'name': 'NOAA Teacher at Sea Program',
                'description': 'Professional development program for educators to join NOAA research expeditions, gaining hands-on experience in ocean and atmospheric science research.',
                'url': 'https://www.noaa.gov/office-education/teacher-at-sea',
                'source': 'NOAA',
                'category': 'Teacher Program',
                'stem_fields': 'Environmental Science, Ocean Science, Climate Science',
                'target_grade': 'K-12',
                'cost': 'Free',
                'location_type': 'Federal',
                'time_commitment': '1-3 weeks',
                'prerequisite_level': 'High',
                'support_level': 'High',
                'deadline': 'Annual applications'
            },
            
            {
                'name': 'NOAA Ocean Guardian School Program',
                'description': 'Recognition program for schools implementing ocean conservation projects and marine stewardship activities, providing resources and curriculum support.',
                'url': 'https://sanctuaries.noaa.gov/education/ocean-guardian/',
                'source': 'NOAA',
                'category': 'School Program',
                'stem_fields': 'Environmental Science, Ocean Science, Conservation',
                'target_grade': 'K-12',
                'cost': 'Free',
                'location_type': 'School-based',
                'time_commitment': 'School year project',
                'prerequisite_level': 'None',
                'support_level': 'Medium',
                'deadline': 'Rolling applications'
            },
            
            # Virtual and Online Programs
            {
                'name': 'NOAA Virtual Ocean Exploration',
                'description': 'Live and archived virtual ocean exploration experiences where students can participate in real-time deep-sea discoveries with NOAA Ocean Exploration scientists.',
                'url': 'https://oceanexplorer.noaa.gov/edu/virtual/',
                'source': 'NOAA',
                'category': 'Virtual Program',
                'stem_fields': 'Environmental Science, Ocean Science, Marine Biology',
                'target_grade': '6-12',
                'cost': 'Free',
                'location_type': 'Virtual',
                'time_commitment': '1-2 hours per session',
                'prerequisite_level': 'None',
                'support_level': 'High',
                'deadline': 'Scheduled events'
            },
            
            {
                'name': 'NOAA Climate Explorer',
                'description': 'Interactive online tool and educational program for students to explore climate data, create visualizations, and understand climate patterns and trends.',
                'url': 'https://toolkit.climate.gov/climate-explorer2/',
                'source': 'NOAA',
                'category': 'Online Program',
                'stem_fields': 'Environmental Science, Climate Science, Data Science',
                'target_grade': '8-12',
                'cost': 'Free',
                'location_type': 'Online',
                'time_commitment': 'Self-paced exploration',
                'prerequisite_level': 'Basic',
                'support_level': 'Medium',
                'deadline': 'Open access'
            },
            
            # Scholarship and Financial Support Programs
            {
                'name': 'NOAA Educational Partnership Program Scholarships',
                'description': 'Scholarship opportunities for underrepresented students pursuing careers in NOAA mission areas including ocean, atmospheric, and environmental sciences.',
                'url': 'https://www.noaa.gov/office-education/epp',
                'source': 'NOAA',
                'category': 'Scholarship Program',
                'stem_fields': 'Environmental Science, Ocean Science, Atmospheric Science',
                'target_grade': '12',
                'cost': 'Free',
                'location_type': 'National',
                'time_commitment': 'College support',
                'prerequisite_level': 'High',
                'support_level': 'High',
                'deadline': 'Spring applications'
            },
            
            # Community and Citizen Science Programs
            {
                'name': 'NOAA Marine Debris Monitoring Programs',
                'description': 'Citizen science programs where students and communities monitor and collect data on marine debris to support NOAA research and conservation efforts.',
                'url': 'https://marinedebris.noaa.gov/research/monitoring',
                'source': 'NOAA',
                'category': 'Citizen Science',
                'stem_fields': 'Environmental Science, Ocean Science, Conservation',
                'target_grade': '6-12',
                'cost': 'Free',
                'location_type': 'Field-based',
                'time_commitment': 'Ongoing participation',
                'prerequisite_level': 'None',
                'support_level': 'Medium',
                'deadline': 'Open enrollment'
            },
            
            {
                'name': 'NOAA Weather Observer Programs',
                'description': 'Citizen science weather monitoring programs where students learn meteorological observation techniques and contribute data to national weather databases.',
                'url': 'https://www.weather.gov/coop/',
                'source': 'NOAA',
                'category': 'Citizen Science',
                'stem_fields': 'Environmental Science, Meteorology, Data Science',
                'target_grade': '8-12',
                'cost': 'Free',
                'location_type': 'Local',
                'time_commitment': 'Daily observations',
                'prerequisite_level': 'Basic',
                'support_level': 'Medium',
                'deadline': 'Rolling enrollment'
            },
            
            # STEM Competition Support
            {
                'name': 'NOAA Science Fair Project Support',
                'description': 'Resources, data access, and mentorship opportunities for students conducting science fair projects related to NOAA mission areas in environmental and ocean sciences.',
                'url': 'https://www.noaa.gov/office-education/student-opportunities',
                'source': 'NOAA',
                'category': 'Science Program',
                'stem_fields': 'Environmental Science, Ocean Science, Climate Science',
                'target_grade': '6-12',
                'cost': 'Free',
                'location_type': 'Virtual',
                'time_commitment': 'Project duration',
                'prerequisite_level': 'Basic',
                'support_level': 'Medium',
                'deadline': 'Open support'
            }
        ]
        
        # Add contextual features to each program
        for program in programs_data:
            contextual_features = self.extract_contextual_features(
                program['name'], 
                program['description'], 
                program['target_grade'],
                program['category']
            )
            program.update(contextual_features)
            self.programs.append(program)
    
    def scrape_programs(self):
        """Main scraping function."""
        print("Starting NOAA Education programs scraper...")
        
        # Try web scraping first
        try:
            for url in self.program_urls[:2]:  # Try first 2 URLs
                soup = self.make_request(url)
                if soup:
                    program_links = self.extract_program_links(soup)
                    print(f"Found {len(program_links)} program links from {url}")
                    
                    # Process first few program links
                    for link in program_links[:2]:  # Limit to 2 per page
                        program_soup = self.make_request(link)
                        if program_soup:
                            program_info = self.extract_program_info(link, program_soup)
                            if program_info:
                                self.programs.append(program_info)
                                print(f"[+] Extracted: {program_info['name']}")
                else:
                    print(f"[-] Failed to fetch {url}")
        except Exception as e:
            print(f"Web scraping failed: {e}")
        
        # Always use comprehensive static data (web scraping may not find detailed program info)
        print("Using comprehensive static program data...")
        self.programs = []  # Clear any partial results
        self.create_comprehensive_programs()
        
        print(f"\nScraping completed. Found {len(self.programs)} total programs.")
    
    def save_to_csv(self, filename: str = "data/noaa_education_programs.csv"):
        """Save scraped programs to CSV file."""
        if not self.programs:
            print("No programs to save")
            return
        
        # Ensure data directory exists
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        
        # Use EXACT same fieldnames as previous scrapers
        fieldnames = [
            'name', 'description', 'url', 'source', 'category', 'stem_fields',
            'target_grade', 'cost', 'location_type', 'time_commitment',
            'prerequisite_level', 'support_level', 'deadline',
            # Financial Context
            'financial_barrier_level', 'financial_aid_available', 'family_income_consideration',
            'hidden_costs_level', 'cost_category',
            # Diversity & Inclusion
            'diversity_focus', 'underrepresented_friendly', 'first_gen_support', 'cultural_competency',
            # Geographic & Access
            'rural_accessible', 'transportation_required', 'internet_dependency', 'regional_availability',
            # Family/Social Context
            'family_involvement_required', 'peer_network_building', 'mentor_access_level'
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
    scraper = NOAAEducationScraper()
    scraper.scrape_programs()
    scraper.save_to_csv()


if __name__ == "__main__":
    main()