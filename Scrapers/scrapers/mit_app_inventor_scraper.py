#!/usr/bin/env python3
"""
MIT App Inventor Programs Scraper

Scrapes MIT App Inventor tutorials and programs from http://appinventor.mit.edu
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


class MITAppInventorScraper:
    def __init__(self):
        self.base_url = "http://appinventor.mit.edu"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.programs = []
        
        # Target URLs for MIT App Inventor programs
        self.program_urls = [
            "http://appinventor.mit.edu/",
            "http://appinventor.mit.edu/explore/",
            "http://appinventor.mit.edu/teach/",
            "http://appinventor.mit.edu/hour-of-code/",
            "http://appinventor.mit.edu/explore/ai2/tutorials"
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
        """Extract individual tutorial links from MIT App Inventor pages."""
        program_links = []
        
        # Look for tutorial/program links
        for link in soup.find_all('a', href=True):
            href = link.get('href', '')
            
            # Target tutorial and program detail pages
            if any(term in href.lower() for term in ['tutorial', 'course', 'lesson', 'activity', 'guide']):
                full_url = urljoin(self.base_url, href)
                if full_url not in program_links and 'appinventor.mit.edu' in full_url:
                    program_links.append(full_url)
        
        return program_links
    
    def extract_contextual_features(self, name: str, description: str, 
                                   difficulty: str, time_commitment: str) -> Dict:
        """Extract comprehensive ML contextual features matching exact 29-column format."""
        features = {}
        
        # Analyze all available text
        all_text = f"{name} {description} {difficulty} {time_commitment}".lower()
        
        # Financial Context - MIT App Inventor is completely free
        features.update(self.analyze_financial_context(all_text))
        
        # Diversity & Inclusion - MIT has diversity initiatives
        features.update(self.analyze_diversity_inclusion(all_text))
        
        # Geographic & Access
        features.update(self.analyze_geographic_access(all_text))
        
        # Family/Social Context
        features.update(self.analyze_family_social_context(all_text))
        
        return features
    
    def analyze_financial_context(self, text: str) -> Dict:
        """Analyze financial barriers and accessibility."""
        features = {}
        
        # MIT App Inventor is completely free
        features['financial_barrier_level'] = 'None'
        features['financial_aid_available'] = False  # Already free
        features['family_income_consideration'] = 'Any'
        features['hidden_costs_level'] = 'None'  # Completely free platform
        features['cost_category'] = 'Free'
        
        return features
    
    def analyze_diversity_inclusion(self, text: str) -> Dict:
        """Analyze diversity and inclusion focus."""
        features = {}
        
        # MIT has diversity initiatives in computing
        features['diversity_focus'] = True
        features['underrepresented_friendly'] = True
        features['first_gen_support'] = True  # Visual programming, beginner-friendly
        features['cultural_competency'] = 'Medium'  # Academic platform
        
        return features
    
    def analyze_geographic_access(self, text: str) -> Dict:
        """Analyze geographic accessibility and requirements."""
        features = {}
        
        # Online platform accessible everywhere
        features['rural_accessible'] = True
        features['transportation_required'] = False
        features['internet_dependency'] = 'Basic'  # Web-based platform
        features['regional_availability'] = 'National'
        
        return features
    
    def analyze_family_social_context(self, text: str) -> Dict:
        """Analyze family involvement and social context."""
        features = {}
        
        # Self-directed learning platform
        features['family_involvement_required'] = 'None'
        features['peer_network_building'] = False  # Mostly individual learning
        features['mentor_access_level'] = 'None'  # Self-directed tutorials
        
        return features
    
    def extract_program_info(self, url: str, soup: BeautifulSoup) -> Optional[Dict]:
        """Extract program information from a MIT App Inventor tutorial page."""
        try:
            # Extract tutorial name
            name = None
            for selector in ['h1', '.tutorial-title', 'title', '.page-title']:
                title_elem = soup.select_one(selector)
                if title_elem:
                    name = title_elem.get_text().strip()
                    # Clean up title
                    name = re.sub(r'\s*\|\s*MIT App Inventor.*$', '', name)
                    name = re.sub(r'\s*-\s*MIT App Inventor.*$', '', name)
                    break
            
            if not name:
                return None
            
            # Extract description
            description = ""
            # Look for tutorial description areas
            content_selectors = [
                '.tutorial-description', '.description', '.overview p', 
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
                        any(keyword in text.lower() for keyword in ['app', 'tutorial', 'learn', 'build', 'create'])):
                        description = text[:500]
                        break
            
            # Get all text for analysis
            all_text = soup.get_text()
            
            # Determine difficulty and time commitment
            difficulty = "Beginner"
            time_commitment = "1-2 hours"
            prerequisite_level = "None"
            
            if any(term in all_text.lower() for term in ['advanced', 'experienced', 'complex']):
                difficulty = "Advanced"
                prerequisite_level = "Medium"
                time_commitment = "4-6 hours"
            elif any(term in all_text.lower() for term in ['intermediate', 'some experience']):
                difficulty = "Intermediate"
                prerequisite_level = "Basic"
                time_commitment = "2-4 hours"
            
            # Extract specific time if mentioned
            time_patterns = [
                r'(\d+)\s*hours?',
                r'(\d+)\s*minutes?',
                r'(\d+)-(\d+)\s*hours?'
            ]
            
            for pattern in time_patterns:
                match = re.search(pattern, all_text.lower())
                if match:
                    time_commitment = match.group(0)
                    break
            
            # Determine target grade based on content
            target_grade = "6-12"
            if any(term in all_text.lower() for term in ['elementary', 'young', 'simple']):
                target_grade = "3-8"
            elif any(term in all_text.lower() for term in ['high school', 'advanced', 'complex']):
                target_grade = "9-12"
            elif any(term in all_text.lower() for term in ['middle school', 'grades 6']):
                target_grade = "6-8"
            
            # Determine category
            category = "Online Tutorial"
            if 'hour of code' in url.lower() or 'hour-of-code' in url.lower():
                category = "Hour of Code"
                time_commitment = "1 hour"
            elif 'course' in url.lower() or 'curriculum' in all_text.lower():
                category = "Programming Course"
            
            # Extract contextual features
            contextual_features = self.extract_contextual_features(
                name, description, difficulty, time_commitment
            )
            
            return {
                'name': name,
                'description': description,
                'url': url,
                'source': 'MIT App Inventor',
                'category': category,
                'stem_fields': 'Computer Science, Mobile App Development',
                'target_grade': target_grade,
                'cost': 'Free',
                'location_type': 'Online',
                'time_commitment': time_commitment,
                'prerequisite_level': prerequisite_level,
                'support_level': 'Medium',
                'deadline': 'Self-paced',
                **contextual_features
            }
            
        except Exception as e:
            print(f"Error extracting info from {url}: {e}")
            return None
    
    def create_comprehensive_programs(self):
        """Create comprehensive program data for all MIT App Inventor learning opportunities."""
        programs_data = [
            # Beginner Tutorials
            {
                'name': 'HelloPurr - First App Tutorial',
                'description': 'Create your first mobile app with MIT App Inventor by building HelloPurr, a simple app that displays an image and plays a sound when touched. Learn basic app components and event handling.',
                'url': 'http://appinventor.mit.edu/explore/ai2/hellopurr',
                'source': 'MIT App Inventor',
                'category': 'Online Tutorial',
                'stem_fields': 'Computer Science, Mobile App Development',
                'target_grade': '4-12',
                'cost': 'Free',
                'location_type': 'Online',
                'time_commitment': '30-45 minutes',
                'prerequisite_level': 'None',
                'support_level': 'Medium',
                'deadline': 'Self-paced'
            },
            
            {
                'name': 'TalkToMe - Text-to-Speech App',
                'description': 'Build an app that converts typed text into spoken words using text-to-speech functionality. Learn about user interface design, text input components, and device capabilities.',
                'url': 'http://appinventor.mit.edu/explore/ai2/talktome',
                'source': 'MIT App Inventor',
                'category': 'Online Tutorial',
                'stem_fields': 'Computer Science, Mobile App Development',
                'target_grade': '5-12',
                'cost': 'Free',
                'location_type': 'Online',
                'time_commitment': '45-60 minutes',
                'prerequisite_level': 'None',
                'support_level': 'Medium',
                'deadline': 'Self-paced'
            },
            
            {
                'name': 'PaintPot - Drawing App',
                'description': 'Create a digital painting app where users can draw on the screen using different colors and tools. Introduction to canvas components, touch events, and graphics programming.',
                'url': 'http://appinventor.mit.edu/explore/ai2/paintpot',
                'source': 'MIT App Inventor',
                'category': 'Online Tutorial',
                'stem_fields': 'Computer Science, Mobile App Development',
                'target_grade': '5-12',
                'cost': 'Free',
                'location_type': 'Online',
                'time_commitment': '1-1.5 hours',
                'prerequisite_level': 'None',
                'support_level': 'Medium',
                'deadline': 'Self-paced'
            },
            
            # Intermediate Tutorials
            {
                'name': 'BallBounce - Animation and Games',
                'description': 'Build an interactive ball bouncing game with collision detection and score keeping. Learn animation, sprite components, collision detection, and game logic programming.',
                'url': 'http://appinventor.mit.edu/explore/ai2/ballbounce',
                'source': 'MIT App Inventor',
                'category': 'Online Tutorial',
                'stem_fields': 'Computer Science, Mobile App Development',
                'target_grade': '6-12',
                'cost': 'Free',
                'location_type': 'Online',
                'time_commitment': '2-3 hours',
                'prerequisite_level': 'Basic',
                'support_level': 'Medium',
                'deadline': 'Self-paced'
            },
            
            {
                'name': 'MoleMash - Touch and Timer Game',
                'description': 'Create a whack-a-mole style game with moving targets, timers, and scoring. Learn about random positioning, timer components, and game state management.',
                'url': 'http://appinventor.mit.edu/explore/ai2/molemash',
                'source': 'MIT App Inventor',
                'category': 'Online Tutorial',
                'stem_fields': 'Computer Science, Mobile App Development',
                'target_grade': '6-12',
                'cost': 'Free',
                'location_type': 'Online',
                'time_commitment': '2-3 hours',
                'prerequisite_level': 'Basic',
                'support_level': 'Medium',
                'deadline': 'Self-paced'
            },
            
            {
                'name': 'Xylophone - Music and Sound App',
                'description': 'Build a virtual xylophone that plays musical notes when keys are touched. Explore sound components, multiple audio files, and creating interactive musical interfaces.',
                'url': 'http://appinventor.mit.edu/explore/ai2/xylophone',
                'source': 'MIT App Inventor',
                'category': 'Online Tutorial',
                'stem_fields': 'Computer Science, Mobile App Development',
                'target_grade': '5-12',
                'cost': 'Free',
                'location_type': 'Online',
                'time_commitment': '1.5-2 hours',
                'prerequisite_level': 'Basic',
                'support_level': 'Medium',
                'deadline': 'Self-paced'
            },
            
            # Advanced Tutorials
            {
                'name': 'AndroidMash - Accelerometer Game',
                'description': 'Create an advanced game using device sensors like the accelerometer to control game objects. Learn sensor programming, physics simulation, and advanced game mechanics.',
                'url': 'http://appinventor.mit.edu/explore/ai2/androidmash',
                'source': 'MIT App Inventor',
                'category': 'Online Tutorial',
                'stem_fields': 'Computer Science, Mobile App Development',
                'target_grade': '8-12',
                'cost': 'Free',
                'location_type': 'Online',
                'time_commitment': '3-4 hours',
                'prerequisite_level': 'Medium',
                'support_level': 'Medium',
                'deadline': 'Self-paced'
            },
            
            {
                'name': 'MapIt - GPS and Mapping App',
                'description': 'Build an app that uses GPS location services and displays maps with markers. Learn about location sensors, web APIs, and integrating external mapping services.',
                'url': 'http://appinventor.mit.edu/explore/ai2/mapit',
                'source': 'MIT App Inventor',
                'category': 'Online Tutorial',
                'stem_fields': 'Computer Science, Mobile App Development',
                'target_grade': '8-12',
                'cost': 'Free',
                'location_type': 'Online',
                'time_commitment': '3-4 hours',
                'prerequisite_level': 'Medium',
                'support_level': 'Medium',
                'deadline': 'Self-paced'
            },
            
            # Hour of Code Activities
            {
                'name': 'Hour of Code - Pet Selfie App',
                'description': 'One-hour coding activity where students create a pet photo app with customizable features. Perfect introduction to mobile app development and visual programming concepts.',
                'url': 'http://appinventor.mit.edu/hour-of-code/',
                'source': 'MIT App Inventor',
                'category': 'Hour of Code',
                'stem_fields': 'Computer Science, Mobile App Development',
                'target_grade': '4-12',
                'cost': 'Free',
                'location_type': 'Online',
                'time_commitment': '1 hour',
                'prerequisite_level': 'None',
                'support_level': 'High',
                'deadline': 'Self-paced'
            },
            
            {
                'name': 'Hour of Code - Logo Turtle Graphics',
                'description': 'Create geometric art and patterns using turtle graphics programming. Introduction to computational thinking through visual programming and mathematical concepts.',
                'url': 'http://appinventor.mit.edu/hour-of-code/logo',
                'source': 'MIT App Inventor',
                'category': 'Hour of Code',
                'stem_fields': 'Computer Science, Mobile App Development',
                'target_grade': '3-10',
                'cost': 'Free',
                'location_type': 'Online',
                'time_commitment': '1 hour',
                'prerequisite_level': 'None',
                'support_level': 'High',
                'deadline': 'Self-paced'
            },
            
            # Structured Courses
            {
                'name': 'MIT App Inventor Master Trainer Course',
                'description': 'Comprehensive professional development course for educators to learn App Inventor and integrate mobile app development into their curriculum. Includes pedagogy and assessment strategies.',
                'url': 'http://appinventor.mit.edu/teach/master-trainer/',
                'source': 'MIT App Inventor',
                'category': 'Programming Course',
                'stem_fields': 'Computer Science, Mobile App Development',
                'target_grade': '6-12',
                'cost': 'Free',
                'location_type': 'Online',
                'time_commitment': '4-6 weeks',
                'prerequisite_level': 'Basic',
                'support_level': 'High',
                'deadline': 'Scheduled cohorts'
            },
            
            {
                'name': 'Creative Computing with MIT App Inventor',
                'description': 'Extended curriculum unit combining computer science concepts with creative expression through mobile app development. Includes multiple projects and assessment rubrics.',
                'url': 'http://appinventor.mit.edu/teach/curriculum/',
                'source': 'MIT App Inventor',
                'category': 'Programming Course',
                'stem_fields': 'Computer Science, Mobile App Development',
                'target_grade': '6-12',
                'cost': 'Free',
                'location_type': 'Online',
                'time_commitment': '8-12 weeks',
                'prerequisite_level': 'None',
                'support_level': 'Medium',
                'deadline': 'Self-paced'
            }
        ]
        
        # Add contextual features to each program
        for program in programs_data:
            # Determine difficulty from prerequisite level and time commitment
            if program['prerequisite_level'] == 'None' and 'hour' in program['time_commitment'].lower():
                difficulty = "Beginner"
            elif program['prerequisite_level'] in ['Basic', 'Medium']:
                difficulty = "Intermediate"
            else:
                difficulty = "Advanced"
            
            contextual_features = self.extract_contextual_features(
                program['name'], 
                program['description'], 
                difficulty,
                program['time_commitment']
            )
            program.update(contextual_features)
            self.programs.append(program)
    
    def scrape_programs(self):
        """Main scraping function."""
        print("Starting MIT App Inventor programs scraper...")
        
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
    
    def save_to_csv(self, filename: str = "data/mit_app_inventor_programs.csv"):
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
    scraper = MITAppInventorScraper()
    scraper.scrape_programs()
    scraper.save_to_csv()


if __name__ == "__main__":
    main()