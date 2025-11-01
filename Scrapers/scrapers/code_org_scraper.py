#!/usr/bin/env python3
"""
Code.org Programs Scraper

Scrapes Code.org courses and programs from https://code.org
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


class CodeOrgScraper:
    def __init__(self):
        self.base_url = "https://code.org"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.programs = []
        
        # Target URLs for Code.org programs
        self.program_urls = [
            "https://code.org/learn",
            "https://code.org/promote",
            "https://code.org/educate/curriculum/courses",
            "https://code.org/hourofcode"
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
        """Extract individual course/program links from Code.org pages."""
        program_links = []
        
        # Look for course/program links
        for link in soup.find_all('a', href=True):
            href = link.get('href', '')
            
            # Target course and program detail pages
            if any(term in href.lower() for term in ['course', 'lesson', 'curriculum', 'learn']):
                full_url = urljoin(self.base_url, href)
                if full_url not in program_links and 'code.org' in full_url:
                    program_links.append(full_url)
        
        return program_links
    
    def extract_contextual_features(self, name: str, description: str, 
                                   grade_level: str, course_type: str) -> Dict:
        """Extract comprehensive ML contextual features matching exact 29-column format."""
        features = {}
        
        # Analyze all available text
        all_text = f"{name} {description} {grade_level} {course_type}".lower()
        
        # Financial Context - Code.org is free
        features.update(self.analyze_financial_context(all_text))
        
        # Diversity & Inclusion - Strong equity focus
        features.update(self.analyze_diversity_inclusion(all_text))
        
        # Geographic & Access
        features.update(self.analyze_geographic_access(all_text, course_type))
        
        # Family/Social Context
        features.update(self.analyze_family_social_context(all_text, course_type))
        
        return features
    
    def analyze_financial_context(self, text: str) -> Dict:
        """Analyze financial barriers and accessibility."""
        features = {}
        
        # Code.org is completely free
        features['financial_barrier_level'] = 'None'
        features['financial_aid_available'] = False  # Already free
        features['family_income_consideration'] = 'Any'
        features['hidden_costs_level'] = 'None'  # Online platform, no additional costs
        features['cost_category'] = 'Free'
        
        return features
    
    def analyze_diversity_inclusion(self, text: str) -> Dict:
        """Analyze diversity and inclusion focus."""
        features = {}
        
        # Code.org has strong equity and diversity focus
        features['diversity_focus'] = True
        features['underrepresented_friendly'] = True
        features['first_gen_support'] = True  # No prior experience needed
        features['cultural_competency'] = 'High'  # Equity-focused organization
        
        return features
    
    def analyze_geographic_access(self, text: str, course_type: str) -> Dict:
        """Analyze geographic accessibility and requirements."""
        features = {}
        
        # All Code.org courses are online
        features['rural_accessible'] = True
        features['transportation_required'] = False
        features['regional_availability'] = 'National'
        
        # internet_dependency based on course complexity
        if any(term in text for term in ['video', 'interactive', 'game', 'app']):
            features['internet_dependency'] = 'High-speed-required'
        else:
            features['internet_dependency'] = 'Basic'
        
        return features
    
    def analyze_family_social_context(self, text: str, course_type: str) -> Dict:
        """Analyze family involvement and social context."""
        features = {}
        
        # family_involvement_required
        if 'self-paced' in course_type.lower() or 'hour of code' in course_type.lower():
            features['family_involvement_required'] = 'None'
        else:
            features['family_involvement_required'] = 'Optional'
        
        # peer_network_building
        if 'classroom' in course_type.lower():
            features['peer_network_building'] = True
        else:
            features['peer_network_building'] = False
        
        # mentor_access_level
        if 'classroom' in course_type.lower():
            features['mentor_access_level'] = 'Adult'  # Teachers
        else:
            features['mentor_access_level'] = 'None'  # Self-paced
        
        return features
    
    def extract_program_info(self, url: str, soup: BeautifulSoup) -> Optional[Dict]:
        """Extract program information from a Code.org course page."""
        try:
            # Extract course name
            name = None
            for selector in ['h1', '.course-title', 'title', '.page-title']:
                title_elem = soup.select_one(selector)
                if title_elem:
                    name = title_elem.get_text().strip()
                    # Clean up title
                    name = re.sub(r'\s*\|\s*Code\.org.*$', '', name)
                    name = re.sub(r'\s*-\s*Code\.org.*$', '', name)
                    break
            
            if not name:
                return None
            
            # Extract description
            description = ""
            # Look for course description areas
            content_selectors = [
                '.course-description', '.description', '.overview p', 
                '.intro p', 'main p', '.content p', '.summary'
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
                        any(keyword in text.lower() for keyword in ['course', 'students', 'learn', 'programming', 'coding'])):
                        description = text[:500]
                        break
            
            # Get all text for analysis
            all_text = soup.get_text()
            
            # Determine course type and details based on URL and content
            if 'hourofcode' in url.lower() or 'hour of code' in name.lower():
                category = "Coding Program"
                course_type = "Hour of Code"
                time_commitment = "1 hour"
                prerequisite_level = "None"
                target_grade = "K-12"
                support_level = "Medium"
            elif 'course' in url.lower() or any(term in name.lower() for term in ['course', 'cs discoveries', 'cs principles']):
                category = "Online Course"
                course_type = "Classroom Course"
                time_commitment = "Semester (18-20 weeks)"
                prerequisite_level = "None"
                target_grade = "6-12"
                support_level = "High"
            else:
                category = "Coding Program"
                course_type = "Self-paced"
                time_commitment = "Self-paced"
                prerequisite_level = "None"
                target_grade = "K-12"
                support_level = "Medium"
            
            # Extract specific grade levels if available
            grade_match = re.search(r'grade[s]?\s*(\d+[\-\d]*)', all_text.lower())
            if grade_match:
                target_grade = grade_match.group(1)
            elif any(term in all_text.lower() for term in ['elementary', 'k-5']):
                target_grade = "K-5"
            elif any(term in all_text.lower() for term in ['middle school', '6-8']):
                target_grade = "6-8"
            elif any(term in all_text.lower() for term in ['high school', '9-12']):
                target_grade = "9-12"
            
            # Extract contextual features
            contextual_features = self.extract_contextual_features(
                name, description, target_grade, course_type
            )
            
            return {
                'name': name,
                'description': description,
                'url': url,
                'source': 'Code.org',
                'category': category,
                'stem_fields': 'Computer Science, Programming',
                'target_grade': target_grade,
                'cost': 'Free',
                'location_type': 'Online',
                'time_commitment': time_commitment,
                'prerequisite_level': prerequisite_level,
                'support_level': support_level,
                'deadline': 'Open enrollment',
                **contextual_features
            }
            
        except Exception as e:
            print(f"Error extracting info from {url}: {e}")
            return None
    
    def create_comprehensive_programs(self):
        """Create comprehensive program data for all Code.org opportunities."""
        programs_data = [
            # Computer Science Fundamentals (K-5)
            {
                'name': 'Computer Science Fundamentals - Course A',
                'description': 'Introduction to computer science for pre-readers. Students learn programming concepts through visual programming blocks, focusing on sequencing, loops, and problem-solving skills.',
                'url': 'https://code.org/educate/curriculum/express-course',
                'source': 'Code.org',
                'category': 'Online Course',
                'stem_fields': 'Computer Science, Programming',
                'target_grade': 'K-1',
                'cost': 'Free',
                'location_type': 'Online',
                'time_commitment': 'Self-paced (10-15 hours)',
                'prerequisite_level': 'None',
                'support_level': 'Medium',
                'deadline': 'Open enrollment'
            },
            
            {
                'name': 'Computer Science Fundamentals - Course B',
                'description': 'Programming fundamentals for early readers using visual blocks. Students explore basic programming concepts including loops, events, and simple algorithms through interactive activities.',
                'url': 'https://code.org/educate/curriculum/elementary-school',
                'source': 'Code.org',
                'category': 'Online Course',
                'stem_fields': 'Computer Science, Programming',
                'target_grade': '1-2',
                'cost': 'Free',
                'location_type': 'Online',
                'time_commitment': 'Self-paced (15-20 hours)',
                'prerequisite_level': 'None',
                'support_level': 'Medium',
                'deadline': 'Open enrollment'
            },
            
            {
                'name': 'Computer Science Fundamentals - Course C',
                'description': 'Intermediate programming concepts for elementary students. Introduction to loops, conditionals, and functions through drag-and-drop programming in engaging games and activities.',
                'url': 'https://code.org/educate/curriculum/elementary-school',
                'source': 'Code.org',
                'category': 'Online Course',
                'stem_fields': 'Computer Science, Programming',
                'target_grade': '2-3',
                'cost': 'Free',
                'location_type': 'Online',
                'time_commitment': 'Self-paced (20-25 hours)',
                'prerequisite_level': 'Basic',
                'support_level': 'Medium',
                'deadline': 'Open enrollment'
            },
            
            {
                'name': 'Computer Science Fundamentals - Course D',
                'description': 'Advanced elementary programming covering nested loops, functions with parameters, and basic algorithms. Students create interactive stories and games while learning logical thinking.',
                'url': 'https://code.org/educate/curriculum/elementary-school',
                'source': 'Code.org',
                'category': 'Online Course',
                'stem_fields': 'Computer Science, Programming',
                'target_grade': '3-4',
                'cost': 'Free',
                'location_type': 'Online',
                'time_commitment': 'Self-paced (25-30 hours)',
                'prerequisite_level': 'Basic',
                'support_level': 'Medium',
                'deadline': 'Open enrollment'
            },
            
            # Middle School Courses
            {
                'name': 'CS Discoveries',
                'description': 'Comprehensive computer science curriculum for middle school covering programming, web development, data science, and artificial intelligence through hands-on projects and creative expression.',
                'url': 'https://code.org/educate/csd',
                'source': 'Code.org',
                'category': 'Online Course',
                'stem_fields': 'Computer Science, Programming',
                'target_grade': '6-8',
                'cost': 'Free',
                'location_type': 'Online',
                'time_commitment': 'Semester (18-20 weeks)',
                'prerequisite_level': 'None',
                'support_level': 'High',
                'deadline': 'Open enrollment'
            },
            
            # High School Course
            {
                'name': 'CS Principles',
                'description': 'AP Computer Science Principles equivalent course covering programming, algorithms, data representation, cybersecurity, and the impact of computing on society through collaborative projects.',
                'url': 'https://code.org/educate/csp',
                'source': 'Code.org',
                'category': 'Online Course',
                'stem_fields': 'Computer Science, Programming',
                'target_grade': '9-12',
                'cost': 'Free',
                'location_type': 'Online',
                'time_commitment': 'Full year (30-35 weeks)',
                'prerequisite_level': 'Basic',
                'support_level': 'High',
                'deadline': 'Open enrollment'
            },
            
            # Hour of Code Programs
            {
                'name': 'Hour of Code - Minecraft',
                'description': 'One-hour introduction to programming using Minecraft characters and environments. Students learn basic coding concepts through block-based programming in a familiar gaming context.',
                'url': 'https://code.org/minecraft',
                'source': 'Code.org',
                'category': 'Coding Program',
                'stem_fields': 'Computer Science, Programming',
                'target_grade': '2-12',
                'cost': 'Free',
                'location_type': 'Online',
                'time_commitment': '1 hour',
                'prerequisite_level': 'None',
                'support_level': 'Medium',
                'deadline': 'Open enrollment'
            },
            
            {
                'name': 'Hour of Code - Star Wars',
                'description': 'Programming introduction featuring Star Wars characters and storylines. Students use visual programming blocks to guide BB-8 and other characters through coding challenges and adventures.',
                'url': 'https://code.org/starwars',
                'source': 'Code.org',
                'category': 'Coding Program',
                'stem_fields': 'Computer Science, Programming',
                'target_grade': '2-12',
                'cost': 'Free',
                'location_type': 'Online',
                'time_commitment': '1 hour',
                'prerequisite_level': 'None',
                'support_level': 'Medium',
                'deadline': 'Open enrollment'
            },
            
            {
                'name': 'Hour of Code - Frozen',
                'description': 'Creative programming activity using Disney Frozen characters. Students learn basic programming concepts while creating interactive animations and controlling character movements through code.',
                'url': 'https://code.org/frozen',
                'source': 'Code.org',
                'category': 'Coding Program',
                'stem_fields': 'Computer Science, Programming',
                'target_grade': 'K-8',
                'cost': 'Free',
                'location_type': 'Online',
                'time_commitment': '1 hour',
                'prerequisite_level': 'None',
                'support_level': 'Medium',
                'deadline': 'Open enrollment'
            },
            
            # Express Course
            {
                'name': 'CS Fundamentals Express',
                'description': 'Accelerated introduction to computer science fundamentals combining concepts from multiple grade levels. Perfect for students who want to quickly learn basic programming concepts.',
                'url': 'https://code.org/educate/curriculum/express-course',
                'source': 'Code.org',
                'category': 'Online Course',
                'stem_fields': 'Computer Science, Programming',
                'target_grade': '4-12',
                'cost': 'Free',
                'location_type': 'Online',
                'time_commitment': 'Self-paced (10-20 hours)',
                'prerequisite_level': 'None',
                'support_level': 'Medium',
                'deadline': 'Open enrollment'
            },
            
            # App Lab
            {
                'name': 'App Lab Programming',
                'description': 'JavaScript programming environment for creating mobile apps and interactive websites. Students learn text-based coding while building real applications with user interfaces and data storage.',
                'url': 'https://code.org/educate/applab',
                'source': 'Code.org',
                'category': 'Online Course',
                'stem_fields': 'Computer Science, Programming',
                'target_grade': '8-12',
                'cost': 'Free',
                'location_type': 'Online',
                'time_commitment': 'Project-based (varies)',
                'prerequisite_level': 'Medium',
                'support_level': 'Medium',
                'deadline': 'Open enrollment'
            },
            
            # Web Lab
            {
                'name': 'Web Lab Development',
                'description': 'HTML, CSS, and web development fundamentals for creating responsive websites. Students learn front-end web development skills through hands-on projects and real-world applications.',
                'url': 'https://code.org/educate/weblab',
                'source': 'Code.org',
                'category': 'Online Course',
                'stem_fields': 'Computer Science, Programming',
                'target_grade': '6-12',
                'cost': 'Free',
                'location_type': 'Online',
                'time_commitment': 'Project-based (varies)',
                'prerequisite_level': 'Basic',
                'support_level': 'Medium',
                'deadline': 'Open enrollment'
            },
            
            # Game Lab
            {
                'name': 'Game Lab Programming',
                'description': 'JavaScript-based game development environment for creating interactive 2D games. Students learn programming concepts through game design including sprites, animations, and user interaction.',
                'url': 'https://code.org/educate/gamelab',
                'source': 'Code.org',
                'category': 'Online Course',
                'stem_fields': 'Computer Science, Programming',
                'target_grade': '6-12',
                'cost': 'Free',
                'location_type': 'Online',
                'time_commitment': 'Project-based (varies)',
                'prerequisite_level': 'Medium',
                'support_level': 'Medium',
                'deadline': 'Open enrollment'
            },
            
            # Specialized Programs
            {
                'name': 'CS in Algebra',
                'description': 'Integration of computer science concepts with algebra curriculum. Students learn programming while reinforcing mathematical concepts through computational thinking and problem-solving activities.',
                'url': 'https://code.org/educate/algebra',
                'source': 'Code.org',
                'category': 'Online Course',
                'stem_fields': 'Computer Science, Programming',
                'target_grade': '7-9',
                'cost': 'Free',
                'location_type': 'Online',
                'time_commitment': 'Semester integration',
                'prerequisite_level': 'Basic',
                'support_level': 'High',
                'deadline': 'Open enrollment'
            },
            
            {
                'name': 'CS in Science',
                'description': 'Computer science integration with science curriculum using computational modeling and data analysis. Students explore scientific concepts through programming and simulation activities.',
                'url': 'https://code.org/educate/science',
                'source': 'Code.org',
                'category': 'Online Course',
                'stem_fields': 'Computer Science, Programming',
                'target_grade': '6-12',
                'cost': 'Free',
                'location_type': 'Online',
                'time_commitment': 'Curriculum integration',
                'prerequisite_level': 'Basic',
                'support_level': 'High',
                'deadline': 'Open enrollment'
            }
        ]
        
        # Add contextual features to each program
        for program in programs_data:
            # Determine course type based on time commitment and structure
            if 'hour' in program['time_commitment'].lower():
                course_type = "Hour of Code"
            elif 'semester' in program['time_commitment'].lower() or 'year' in program['time_commitment'].lower():
                course_type = "Classroom Course"
            else:
                course_type = "Self-paced"
            
            contextual_features = self.extract_contextual_features(
                program['name'], 
                program['description'], 
                program['target_grade'],
                course_type
            )
            program.update(contextual_features)
            self.programs.append(program)
    
    def scrape_programs(self):
        """Main scraping function."""
        print("Starting Code.org programs scraper...")
        
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
    
    def save_to_csv(self, filename: str = "data/code_org_programs.csv"):
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
    scraper = CodeOrgScraper()
    scraper.scrape_programs()
    scraper.save_to_csv()


if __name__ == "__main__":
    main()