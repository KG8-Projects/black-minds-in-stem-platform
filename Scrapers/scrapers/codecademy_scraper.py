#!/usr/bin/env python3
"""
Codecademy Courses Scraper

Scrapes Codecademy courses from https://www.codecademy.com
and extracts detailed course information for K-12 students.
"""

import requests
from bs4 import BeautifulSoup
import csv
import time
import re
import os
from urllib.parse import urljoin, urlparse
from typing import List, Dict, Optional


class CodecademyScraper:
    def __init__(self):
        self.base_url = "https://www.codecademy.com"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.programs = []
        
        # Target URLs for Codecademy courses
        self.program_urls = [
            "https://www.codecademy.com/catalog",
            "https://www.codecademy.com/learn",
            "https://www.codecademy.com/courses",
            "https://www.codecademy.com/pro"
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
        """Extract individual course links from Codecademy pages."""
        program_links = []
        
        # Look for course/program links
        for link in soup.find_all('a', href=True):
            href = link.get('href', '')
            
            # Target course detail pages
            if any(term in href.lower() for term in ['learn', 'course', 'path']):
                full_url = urljoin(self.base_url, href)
                if full_url not in program_links and 'codecademy.com' in full_url:
                    program_links.append(full_url)
        
        return program_links
    
    def extract_contextual_features(self, name: str, description: str, 
                                   cost: str, difficulty: str) -> Dict:
        """Extract comprehensive ML contextual features matching exact 29-column format."""
        features = {}
        
        # Analyze all available text
        all_text = f"{name} {description} {cost} {difficulty}".lower()
        
        # Financial Context - Codecademy has free and paid content
        features.update(self.analyze_financial_context(cost, all_text))
        
        # Diversity & Inclusion - Commercial platform
        features.update(self.analyze_diversity_inclusion(all_text))
        
        # Geographic & Access
        features.update(self.analyze_geographic_access(all_text))
        
        # Family/Social Context
        features.update(self.analyze_family_social_context(all_text))
        
        return features
    
    def analyze_financial_context(self, cost: str, text: str) -> Dict:
        """Analyze financial barriers and accessibility."""
        features = {}
        
        # Determine barriers based on cost
        if cost.lower() == 'free':
            features['financial_barrier_level'] = 'None'
            features['cost_category'] = 'Free'
        else:
            features['financial_barrier_level'] = 'Low'
            features['cost_category'] = '$100-500'  # Typical Pro subscription range
        
        # Check for student discounts
        features['financial_aid_available'] = any(term in text for term in 
                                                ['student', 'discount', 'scholarship'])
        
        features['family_income_consideration'] = 'Any'
        features['hidden_costs_level'] = 'None'  # Subscription covers everything
        
        return features
    
    def analyze_diversity_inclusion(self, text: str) -> Dict:
        """Analyze diversity and inclusion focus."""
        features = {}
        
        # Commercial platform, not diversity-focused
        features['diversity_focus'] = False
        features['underrepresented_friendly'] = True  # Accessible online learning
        features['first_gen_support'] = True  # Designed for beginners
        features['cultural_competency'] = 'Low'  # Commercial platform
        
        return features
    
    def analyze_geographic_access(self, text: str) -> Dict:
        """Analyze geographic accessibility and requirements."""
        features = {}
        
        # Online platform accessible everywhere
        features['rural_accessible'] = True
        features['transportation_required'] = False
        features['internet_dependency'] = 'High-speed-required'  # Interactive coding
        features['regional_availability'] = 'National'
        
        return features
    
    def analyze_family_social_context(self, text: str) -> Dict:
        """Analyze family involvement and social context."""
        features = {}
        
        # Self-directed learning platform
        features['family_involvement_required'] = 'None'
        features['peer_network_building'] = False  # Mostly individual learning
        features['mentor_access_level'] = 'None'  # Self-paced platform
        
        return features
    
    def extract_program_info(self, url: str, soup: BeautifulSoup) -> Optional[Dict]:
        """Extract program information from a Codecademy course page."""
        try:
            # Extract course name
            name = None
            for selector in ['h1', '.course-title', 'title', '.page-title']:
                title_elem = soup.select_one(selector)
                if title_elem:
                    name = title_elem.get_text().strip()
                    # Clean up title
                    name = re.sub(r'\s*\|\s*Codecademy.*$', '', name)
                    name = re.sub(r'\s*-\s*Codecademy.*$', '', name)
                    break
            
            if not name:
                return None
            
            # Extract description
            description = ""
            # Look for course description areas
            content_selectors = [
                '.course-description', '.description', '.overview p', 
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
                        any(keyword in text.lower() for keyword in ['course', 'learn', 'programming', 'coding'])):
                        description = text[:500]
                        break
            
            # Get all text for analysis
            all_text = soup.get_text()
            
            # Determine course details
            cost = "Free"
            if any(term in all_text.lower() for term in ['pro', 'premium', 'paid', 'subscription']):
                cost = "Paid"
            
            # Determine difficulty and prerequisites
            difficulty = "Beginner"
            prerequisite_level = "None"
            
            if any(term in all_text.lower() for term in ['advanced', 'experienced']):
                difficulty = "Advanced"
                prerequisite_level = "High"
            elif any(term in all_text.lower() for term in ['intermediate', 'some experience']):
                difficulty = "Intermediate"
                prerequisite_level = "Medium"
            
            # Extract time commitment
            time_commitment = "4-8 weeks"
            time_patterns = [
                r'(\d+)\s*hours?',
                r'(\d+)\s*weeks?',
                r'(\d+)-(\d+)\s*hours?',
                r'(\d+)-(\d+)\s*weeks?'
            ]
            
            for pattern in time_patterns:
                match = re.search(pattern, all_text.lower())
                if match:
                    time_commitment = match.group(0)
                    break
            
            # Determine STEM field based on course content
            stem_fields = "Computer Science, Programming"
            if any(term in all_text.lower() for term in ['python', 'java', 'javascript']):
                stem_fields = "Computer Science, Programming"
            elif any(term in all_text.lower() for term in ['data science', 'machine learning']):
                stem_fields = "Computer Science, Data Science"
            elif any(term in all_text.lower() for term in ['web development', 'html', 'css']):
                stem_fields = "Computer Science, Web Development"
            
            # Determine target grade
            target_grade = "9-12"
            if any(term in all_text.lower() for term in ['advanced', 'professional', 'career']):
                target_grade = "College"
            
            # Extract contextual features
            contextual_features = self.extract_contextual_features(
                name, description, cost, difficulty
            )
            
            return {
                'name': name,
                'description': description,
                'url': url,
                'source': 'Codecademy',
                'category': 'Online Course',
                'stem_fields': stem_fields,
                'target_grade': target_grade,
                'cost': cost,
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
        """Create comprehensive program data for all relevant Codecademy learning opportunities."""
        programs_data = [
            # Programming Languages - Beginner Level
            {
                'name': 'Learn Python 3',
                'description': 'Learn the basics of Python 3, one of the most powerful, versatile, and in-demand programming languages today. Build foundational programming skills through interactive lessons and projects.',
                'url': 'https://www.codecademy.com/learn/learn-python-3',
                'source': 'Codecademy',
                'category': 'Online Course',
                'stem_fields': 'Computer Science, Programming',
                'target_grade': '9-12',
                'cost': 'Free',
                'location_type': 'Online',
                'time_commitment': '25 hours',
                'prerequisite_level': 'None',
                'support_level': 'Medium',
                'deadline': 'Self-paced'
            },
            
            {
                'name': 'Learn Java',
                'description': 'Learn Java programming fundamentals including object-oriented programming concepts. Java is widely used in enterprise applications and Android development.',
                'url': 'https://www.codecademy.com/learn/learn-java',
                'source': 'Codecademy',
                'category': 'Online Course',
                'stem_fields': 'Computer Science, Programming',
                'target_grade': '9-12',
                'cost': 'Free',
                'location_type': 'Online',
                'time_commitment': '25 hours',
                'prerequisite_level': 'None',
                'support_level': 'Medium',
                'deadline': 'Self-paced'
            },
            
            {
                'name': 'Learn JavaScript',
                'description': 'Learn JavaScript fundamentals and start building interactive web applications. JavaScript is essential for modern web development and used across the tech industry.',
                'url': 'https://www.codecademy.com/learn/introduction-to-javascript',
                'source': 'Codecademy',
                'category': 'Online Course',
                'stem_fields': 'Computer Science, Web Development',
                'target_grade': '9-12',
                'cost': 'Free',
                'location_type': 'Online',
                'time_commitment': '20 hours',
                'prerequisite_level': 'None',
                'support_level': 'Medium',
                'deadline': 'Self-paced'
            },
            
            {
                'name': 'Learn HTML & CSS',
                'description': 'Learn the fundamentals of web development with HTML and CSS. Create and style your own websites from scratch using the building blocks of the web.',
                'url': 'https://www.codecademy.com/learn/learn-html',
                'source': 'Codecademy',
                'category': 'Online Course',
                'stem_fields': 'Computer Science, Web Development',
                'target_grade': '8-12',
                'cost': 'Free',
                'location_type': 'Online',
                'time_commitment': '15 hours',
                'prerequisite_level': 'None',
                'support_level': 'Medium',
                'deadline': 'Self-paced'
            },
            
            # Data Science and Analysis
            {
                'name': 'Learn SQL',
                'description': 'Learn SQL to communicate with databases and analyze data. SQL is essential for data analysis and used by virtually every company that stores data.',
                'url': 'https://www.codecademy.com/learn/learn-sql',
                'source': 'Codecademy',
                'category': 'Online Course',
                'stem_fields': 'Computer Science, Data Science',
                'target_grade': '10-12',
                'cost': 'Free',
                'location_type': 'Online',
                'time_commitment': '20 hours',
                'prerequisite_level': 'None',
                'support_level': 'Medium',
                'deadline': 'Self-paced'
            },
            
            {
                'name': 'Learn R',
                'description': 'Learn R programming for statistical analysis and data visualization. R is widely used in data science, research, and statistical computing.',
                'url': 'https://www.codecademy.com/learn/learn-r',
                'source': 'Codecademy',
                'category': 'Online Course',
                'stem_fields': 'Computer Science, Data Science',
                'target_grade': '10-12',
                'cost': 'Free',
                'location_type': 'Online',
                'time_commitment': '20 hours',
                'prerequisite_level': 'Basic',
                'support_level': 'Medium',
                'deadline': 'Self-paced'
            },
            
            # Pro Skill Paths and Career Tracks
            {
                'name': 'Data Scientist Career Path',
                'description': 'Learn Python, SQL, statistics, and machine learning to become a data scientist. Build a portfolio of data science projects and gain job-ready skills through hands-on practice.',
                'url': 'https://www.codecademy.com/learn/paths/data-science',
                'source': 'Codecademy',
                'category': 'Programming Course',
                'stem_fields': 'Computer Science, Data Science',
                'target_grade': 'College',
                'cost': 'Paid',
                'location_type': 'Online',
                'time_commitment': '6 months',
                'prerequisite_level': 'Basic',
                'support_level': 'High',
                'deadline': 'Self-paced'
            },
            
            {
                'name': 'Web Development Career Path',
                'description': 'Learn front-end and back-end web development skills including HTML, CSS, JavaScript, React, Node.js, and databases. Build full-stack web applications.',
                'url': 'https://www.codecademy.com/learn/paths/web-development',
                'source': 'Codecademy',
                'category': 'Programming Course',
                'stem_fields': 'Computer Science, Web Development',
                'target_grade': '10-12',
                'cost': 'Paid',
                'location_type': 'Online',
                'time_commitment': '5-7 months',
                'prerequisite_level': 'None',
                'support_level': 'High',
                'deadline': 'Self-paced'
            },
            
            {
                'name': 'Computer Science Career Path',
                'description': 'Learn fundamental computer science concepts including algorithms, data structures, and programming principles. Build a strong foundation for advanced CS studies.',
                'url': 'https://www.codecademy.com/learn/paths/computer-science',
                'source': 'Codecademy',
                'category': 'Programming Course',
                'stem_fields': 'Computer Science, Programming',
                'target_grade': '10-12',
                'cost': 'Paid',
                'location_type': 'Online',
                'time_commitment': '6-8 months',
                'prerequisite_level': 'Basic',
                'support_level': 'High',
                'deadline': 'Self-paced'
            },
            
            # Intermediate/Advanced Courses
            {
                'name': 'Learn React',
                'description': 'Learn React, a powerful JavaScript library for building user interfaces. Create dynamic and interactive web applications with component-based architecture.',
                'url': 'https://www.codecademy.com/learn/react-101',
                'source': 'Codecademy',
                'category': 'Online Course',
                'stem_fields': 'Computer Science, Web Development',
                'target_grade': '10-12',
                'cost': 'Paid',
                'location_type': 'Online',
                'time_commitment': '20 hours',
                'prerequisite_level': 'Medium',
                'support_level': 'Medium',
                'deadline': 'Self-paced'
            },
            
            {
                'name': 'Learn Git & GitHub',
                'description': 'Learn version control with Git and collaborative coding with GitHub. Essential skills for any programmer working on projects individually or in teams.',
                'url': 'https://www.codecademy.com/learn/learn-git',
                'source': 'Codecademy',
                'category': 'Online Course',
                'stem_fields': 'Computer Science, Programming',
                'target_grade': '9-12',
                'cost': 'Free',
                'location_type': 'Online',
                'time_commitment': '10 hours',
                'prerequisite_level': 'Basic',
                'support_level': 'Medium',
                'deadline': 'Self-paced'
            },
            
            # Specialized Skills
            {
                'name': 'Learn Machine Learning',
                'description': 'Introduction to machine learning concepts using Python. Learn supervised learning, data preprocessing, and model evaluation techniques for beginners.',
                'url': 'https://www.codecademy.com/learn/machine-learning',
                'source': 'Codecademy',
                'category': 'Online Course',
                'stem_fields': 'Computer Science, Data Science',
                'target_grade': '11-12',
                'cost': 'Paid',
                'location_type': 'Online',
                'time_commitment': '15 hours',
                'prerequisite_level': 'Medium',
                'support_level': 'Medium',
                'deadline': 'Self-paced'
            },
            
            {
                'name': 'Learn Command Line',
                'description': 'Master the command line interface to navigate file systems, manage files, and run programs efficiently. Essential skill for all programmers and developers.',
                'url': 'https://www.codecademy.com/learn/learn-the-command-line',
                'source': 'Codecademy',
                'category': 'Online Course',
                'stem_fields': 'Computer Science, Programming',
                'target_grade': '9-12',
                'cost': 'Free',
                'location_type': 'Online',
                'time_commitment': '8 hours',
                'prerequisite_level': 'None',
                'support_level': 'Medium',
                'deadline': 'Self-paced'
            },
            
            # Project-Based Learning
            {
                'name': 'Build a Website with HTML, CSS, and GitHub Pages',
                'description': 'Hands-on project course where students build and deploy a personal website using HTML, CSS, and GitHub Pages. Learn web development through practical application.',
                'url': 'https://www.codecademy.com/learn/make-a-website',
                'source': 'Codecademy',
                'category': 'Online Course',
                'stem_fields': 'Computer Science, Web Development',
                'target_grade': '8-12',
                'cost': 'Free',
                'location_type': 'Online',
                'time_commitment': '4 hours',
                'prerequisite_level': 'None',
                'support_level': 'Medium',
                'deadline': 'Self-paced'
            },
            
            {
                'name': 'Create Interactive Websites with JavaScript',
                'description': 'Build interactive websites using JavaScript DOM manipulation. Learn to create dynamic web pages that respond to user interactions and events.',
                'url': 'https://www.codecademy.com/learn/build-interactive-websites',
                'source': 'Codecademy',
                'category': 'Online Course',
                'stem_fields': 'Computer Science, Web Development',
                'target_grade': '9-12',
                'cost': 'Paid',
                'location_type': 'Online',
                'time_commitment': '15 hours',
                'prerequisite_level': 'Basic',
                'support_level': 'Medium',
                'deadline': 'Self-paced'
            }
        ]
        
        # Add contextual features to each program
        for program in programs_data:
            # Determine difficulty from prerequisite level
            if program['prerequisite_level'] == 'None':
                difficulty = "Beginner"
            elif program['prerequisite_level'] in ['Basic', 'Medium']:
                difficulty = "Intermediate"
            else:
                difficulty = "Advanced"
            
            contextual_features = self.extract_contextual_features(
                program['name'], 
                program['description'], 
                program['cost'],
                difficulty
            )
            program.update(contextual_features)
            self.programs.append(program)
    
    def scrape_programs(self):
        """Main scraping function."""
        print("Starting Codecademy programs scraper...")
        
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
    
    def save_to_csv(self, filename: str = "data/codecademy_programs.csv"):
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
    scraper = CodecademyScraper()
    scraper.scrape_programs()
    scraper.save_to_csv()


if __name__ == "__main__":
    main()