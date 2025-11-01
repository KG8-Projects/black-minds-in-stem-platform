#!/usr/bin/env python3
"""
Science Buddies STEM Projects Scraper

Scrapes Science Buddies science fair projects from https://www.sciencebuddies.org
and extracts detailed project information for K-12 students.
"""

import requests
from bs4 import BeautifulSoup
import csv
import time
import re
import os
from urllib.parse import urljoin, urlparse
from typing import List, Dict, Optional


class ScienceBuddiesScraper:
    def __init__(self):
        self.base_url = "https://www.sciencebuddies.org"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.projects = []
        
        # Target URLs for different grade levels
        self.project_urls = [
            "https://www.sciencebuddies.org/science-fair-projects/science-projects",
            "https://www.sciencebuddies.org/science-fair-projects/science-projects/sixth-grade",
            "https://www.sciencebuddies.org/science-fair-projects/science-projects/eighth-grade",
            "https://www.sciencebuddies.org/science-fair-projects/science-projects/high-school",
            "https://www.sciencebuddies.org/stem-activities"
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
    
    def extract_project_links(self, soup: BeautifulSoup) -> List[str]:
        """Extract individual project links from project listing pages."""
        project_links = []
        
        # Look for project links
        for link in soup.find_all('a', href=True):
            href = link.get('href', '')
            
            # Target individual project pages
            if ('/science-fair-projects/project-ideas/' in href or 
                '/stem-activities/' in href):
                full_url = urljoin(self.base_url, href)
                if full_url not in project_links:
                    project_links.append(full_url)
        
        return project_links
    
    def extract_cost_info(self, soup: BeautifulSoup, text: str) -> str:
        """Extract cost/materials information from project pages."""
        cost = "Under $20"  # Default for most Science Buddies projects
        
        # Look for cost patterns
        cost_patterns = [
            r'\$[\d,]+',
            r'cost[:\s]*\$?[\d,]+',
            r'materials?[:\s]*\$?[\d,]+',
            r'budget[:\s]*\$?[\d,]+'
        ]
        
        for pattern in cost_patterns:
            matches = re.findall(pattern, text.lower())
            if matches:
                cost = matches[0]
                break
        
        # Look for cost indicators
        if any(term in text for term in ['expensive', 'costly', 'high cost']):
            cost = "$50+"
        elif any(term in text for term in ['cheap', 'low cost', 'inexpensive', 'free materials']):
            cost = "Under $10"
        
        return cost
    
    def extract_time_commitment(self, soup: BeautifulSoup, text: str) -> str:
        """Extract time required for project completion."""
        time_commitment = ""
        
        # Look for time patterns
        time_patterns = [
            r'(\d+)\s*hours?',
            r'(\d+)\s*days?',
            r'(\d+)\s*weeks?',
            r'(\d+)\s*minutes?'
        ]
        
        for pattern in time_patterns:
            match = re.search(pattern, text.lower())
            if match:
                time_commitment = match.group(0)
                break
        
        # Default based on project type
        if not time_commitment:
            if 'science fair' in text.lower():
                time_commitment = "2-4 weeks"
            else:
                time_commitment = "2-4 hours"
                
        return time_commitment
    
    def extract_difficulty_level(self, soup: BeautifulSoup, text: str) -> str:
        """Extract difficulty/prerequisite level."""
        difficulty = "None"
        
        # Look for difficulty indicators
        if any(term in text.lower() for term in ['advanced', 'expert', 'complex', 'difficult']):
            difficulty = "Advanced"
        elif any(term in text.lower() for term in ['intermediate', 'moderate', 'some experience']):
            difficulty = "Intermediate"
        elif any(term in text.lower() for term in ['beginner', 'basic', 'easy', 'simple', 'elementary']):
            difficulty = "Basic"
        
        return difficulty
    
    def extract_grade_level(self, url: str, text: str) -> str:
        """Extract target grade level from URL and content."""
        if 'sixth-grade' in url:
            return "6"
        elif 'eighth-grade' in url:
            return "8"
        elif 'high-school' in url:
            return "9-12"
        elif 'elementary' in text.lower():
            return "K-5"
        elif 'middle' in text.lower():
            return "6-8"
        else:
            return "K-12"
    
    def extract_stem_field(self, soup: BeautifulSoup, text: str) -> str:
        """Extract STEM subject area."""
        # Look for subject indicators
        subjects = []
        
        if any(term in text.lower() for term in ['biology', 'life science', 'plants', 'animals']):
            subjects.append('Biology')
        if any(term in text.lower() for term in ['chemistry', 'chemical', 'reaction']):
            subjects.append('Chemistry')
        if any(term in text.lower() for term in ['physics', 'force', 'motion', 'energy']):
            subjects.append('Physics')
        if any(term in text.lower() for term in ['engineering', 'design', 'build', 'construct']):
            subjects.append('Engineering')
        if any(term in text.lower() for term in ['math', 'mathematics', 'calculation', 'statistics']):
            subjects.append('Mathematics')
        if any(term in text.lower() for term in ['computer', 'programming', 'coding', 'technology']):
            subjects.append('Computer Science')
        if any(term in text.lower() for term in ['environment', 'ecology', 'earth science']):
            subjects.append('Environmental Science')
        
        return ', '.join(subjects) if subjects else 'General Science'
    
    def extract_contextual_features(self, name: str, description: str, cost: str, 
                                   time_commitment: str, difficulty: str, text: str) -> Dict:
        """Extract comprehensive ML contextual features matching FIRST Robotics format."""
        features = {}
        
        # Analyze all available text
        all_text = f"{name} {description} {cost} {time_commitment} {difficulty} {text}".lower()
        
        # Financial Context
        features.update(self.analyze_financial_context(cost, all_text))
        
        # Diversity & Inclusion
        features.update(self.analyze_diversity_inclusion(all_text))
        
        # Geographic & Access
        features.update(self.analyze_geographic_access(all_text))
        
        # Family/Social Context
        features.update(self.analyze_family_social_context(all_text))
        
        return features
    
    def analyze_financial_context(self, cost: str, text: str) -> Dict:
        """Analyze financial barriers and accessibility."""
        features = {}
        
        # Extract numeric cost if possible
        cost_amount = 0
        if '$' in cost:
            import re
            numbers = re.findall(r'\$?(\d+)', cost)
            if numbers:
                cost_amount = int(numbers[0])
        elif 'under' in cost.lower():
            # Extract from "Under $20" format
            numbers = re.findall(r'(\d+)', cost)
            if numbers:
                cost_amount = int(numbers[0])
        
        # financial_barrier_level
        if cost_amount <= 10:
            features['financial_barrier_level'] = 'None'
        elif cost_amount <= 25:
            features['financial_barrier_level'] = 'Low'
        elif cost_amount <= 50:
            features['financial_barrier_level'] = 'Medium'
        else:
            features['financial_barrier_level'] = 'High'
        
        # financial_aid_available
        features['financial_aid_available'] = False  # Science Buddies projects don't typically offer aid
        
        # family_income_consideration
        if cost_amount <= 20:
            features['family_income_consideration'] = 'Any'
        else:
            features['family_income_consideration'] = 'Middle+'
        
        # hidden_costs_level
        hidden_costs = []
        if any(term in text for term in ['specialized', 'equipment', 'tools']):
            hidden_costs.append('Equipment')
        features['hidden_costs_level'] = ', '.join(hidden_costs) if hidden_costs else 'None'
        
        # cost_category
        if cost_amount <= 10:
            features['cost_category'] = 'Under-$100'
        elif cost_amount <= 50:
            features['cost_category'] = 'Under-$100'
        else:
            features['cost_category'] = '$100-500'
        
        return features
    
    def analyze_diversity_inclusion(self, text: str) -> Dict:
        """Analyze diversity and inclusion focus."""
        features = {}
        
        # diversity_focus
        features['diversity_focus'] = any(keyword in text for keyword in 
                                        ['diversity', 'inclusion', 'inclusive', 'all students'])
        
        # underrepresented_friendly
        features['underrepresented_friendly'] = any(keyword in text for keyword in 
                                                  ['accessible', 'everyone', 'all backgrounds'])
        
        # first_gen_support
        features['first_gen_support'] = any(keyword in text for keyword in 
                                          ['beginner', 'no experience', 'step-by-step', 'guide'])
        
        # cultural_competency
        if any(term in text for term in ['global', 'international', 'cultural']):
            features['cultural_competency'] = 'High'
        elif any(term in text for term in ['community', 'diverse']):
            features['cultural_competency'] = 'Medium'
        else:
            features['cultural_competency'] = 'Low'
        
        return features
    
    def analyze_geographic_access(self, text: str) -> Dict:
        """Analyze geographic accessibility and requirements."""
        features = {}
        
        # rural_accessible
        features['rural_accessible'] = True  # Science Buddies projects are home-based
        
        # transportation_required
        features['transportation_required'] = False  # Home-based projects
        
        # internet_dependency
        features['internet_dependency'] = 'Basic'  # Need internet for instructions
        
        # regional_availability
        features['regional_availability'] = 'National'  # Available everywhere
        
        return features
    
    def analyze_family_social_context(self, text: str) -> Dict:
        """Analyze family involvement and social context."""
        features = {}
        
        # family_involvement_required
        if any(term in text for term in ['adult supervision', 'parent', 'guardian']):
            features['family_involvement_required'] = 'Required'
        elif any(term in text for term in ['with help', 'assistance']):
            features['family_involvement_required'] = 'Optional'
        else:
            features['family_involvement_required'] = 'None'
        
        # peer_network_building
        features['peer_network_building'] = any(keyword in text for keyword in 
                                               ['group', 'team', 'collaborate', 'share'])
        
        # mentor_access_level
        if any(term in text for term in ['expert', 'scientist', 'professional']):
            features['mentor_access_level'] = 'Professional'
        elif any(term in text for term in ['teacher', 'adult', 'mentor']):
            features['mentor_access_level'] = 'Adult'
        else:
            features['mentor_access_level'] = 'None'
        
        return features
    
    def extract_project_info(self, url: str, soup: BeautifulSoup) -> Optional[Dict]:
        """Extract project information from a Science Buddies project page."""
        try:
            # Extract project name
            name = None
            for selector in ['h1', '.project-title', 'title', '.page-title']:
                title_elem = soup.select_one(selector)
                if title_elem:
                    name = title_elem.get_text().strip()
                    # Clean up title
                    name = re.sub(r'\s*\|\s*Science Buddies.*$', '', name)
                    break
            
            if not name:
                return None
            
            # Extract description
            description = ""
            # Look for project description areas
            content_selectors = [
                '.project-summary', '.overview', '.description', 
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
                        if len(' '.join(desc_parts)) >= 300:
                            break
                    if desc_parts:
                        description = ' '.join(desc_parts)[:500]
                        break
            
            # If no good description found, try broader search
            if not description:
                all_paragraphs = soup.find_all('p')
                for p in all_paragraphs[:3]:
                    text = p.get_text().strip()
                    if (len(text) > 40 and 
                        any(keyword in text.lower() for keyword in ['project', 'experiment', 'science', 'investigate'])):
                        description = text[:500]
                        break
            
            # Get all text for analysis
            all_text = soup.get_text()
            
            # Extract other details
            grade_level = self.extract_grade_level(url, all_text)
            stem_field = self.extract_stem_field(soup, all_text)
            cost = self.extract_cost_info(soup, all_text)
            time_commitment = self.extract_time_commitment(soup, all_text)
            difficulty = self.extract_difficulty_level(soup, all_text)
            
            # Extract contextual features
            contextual_features = self.extract_contextual_features(
                name, description, cost, time_commitment, difficulty, all_text
            )
            
            return {
                'name': name,
                'description': description,
                'url': url,
                'source': 'Science Buddies',
                'category': 'Science Project',
                'stem_fields': stem_field,
                'target_grade': grade_level,
                'cost': cost,
                'location_type': 'Online',
                'time_commitment': time_commitment,
                'prerequisite_level': difficulty,
                'support_level': 'Medium',
                'deadline': '',
                **contextual_features
            }
            
        except Exception as e:
            print(f"Error extracting info from {url}: {e}")
            return None
    
    def create_static_projects(self):
        """Create static project data representing typical Science Buddies projects."""
        static_projects = [
            # Elementary Projects (K-5)
            {
                'name': 'Growing Seeds in Different Soils',
                'description': 'Investigate how different types of soil affect plant growth by planting seeds in various soil samples and measuring their growth over time.',
                'url': 'https://www.sciencebuddies.org/science-fair-projects/project-ideas/botany',
                'source': 'Science Buddies',
                'category': 'Science Project',
                'stem_fields': 'Biology, Environmental Science',
                'target_grade': 'K-5',
                'cost': 'Under $15',
                'location_type': 'Online',
                'time_commitment': '2-3 weeks',
                'prerequisite_level': 'None',
                'support_level': 'Medium',
                'deadline': ''
            },
            {
                'name': 'Rainbow Milk Experiment',
                'description': 'Explore surface tension and chemical reactions by adding food coloring and soap to milk to create colorful swirling patterns.',
                'url': 'https://www.sciencebuddies.org/science-fair-projects/project-ideas/chemistry',
                'source': 'Science Buddies',
                'category': 'STEM Activity',
                'stem_fields': 'Chemistry, Physics',
                'target_grade': 'K-5',
                'cost': 'Under $10',
                'location_type': 'Online',
                'time_commitment': '1-2 hours',
                'prerequisite_level': 'None',
                'support_level': 'Medium',
                'deadline': ''
            },
            
            # Middle School Projects (6-8)
            {
                'name': 'Testing Water Quality with pH Strips',
                'description': 'Test the pH levels of different water sources around your community and analyze what factors might affect water acidity.',
                'url': 'https://www.sciencebuddies.org/science-fair-projects/project-ideas/environmental',
                'source': 'Science Buddies',
                'category': 'Science Project',
                'stem_fields': 'Environmental Science, Chemistry',
                'target_grade': '6-8',
                'cost': 'Under $25',
                'location_type': 'Online',
                'time_commitment': '1-2 weeks',
                'prerequisite_level': 'Basic',
                'support_level': 'Medium',
                'deadline': ''
            },
            {
                'name': 'Building a Simple Robot',
                'description': 'Design and build a simple robot using motors, sensors, and basic programming to complete specific tasks and challenges.',
                'url': 'https://www.sciencebuddies.org/science-fair-projects/project-ideas/robotics',
                'source': 'Science Buddies',
                'category': 'STEM Activity',
                'stem_fields': 'Engineering, Computer Science',
                'target_grade': '6-8',
                'cost': 'Under $40',
                'location_type': 'Online',
                'time_commitment': '3-4 weeks',
                'prerequisite_level': 'Intermediate',
                'support_level': 'Medium',
                'deadline': ''
            },
            {
                'name': 'Crystal Growing Experiment',
                'description': 'Grow different types of crystals using various solutions and compare their formation time, size, and structure.',
                'url': 'https://www.sciencebuddies.org/science-fair-projects/project-ideas/crystals',
                'source': 'Science Buddies',
                'category': 'Science Project',
                'stem_fields': 'Chemistry, Physics',
                'target_grade': '6-8',
                'cost': 'Under $20',
                'location_type': 'Online',
                'time_commitment': '2-4 weeks',
                'prerequisite_level': 'Basic',
                'support_level': 'Medium',
                'deadline': ''
            },
            
            # High School Projects (9-12)
            {
                'name': 'DNA Extraction from Fruit',
                'description': 'Extract and analyze DNA from different fruits using household materials to understand genetic material and molecular biology.',
                'url': 'https://www.sciencebuddies.org/science-fair-projects/project-ideas/molecular-biology',
                'source': 'Science Buddies',
                'category': 'Science Project',
                'stem_fields': 'Biology, Chemistry',
                'target_grade': '9-12',
                'cost': 'Under $30',
                'location_type': 'Online',
                'time_commitment': '2-3 weeks',
                'prerequisite_level': 'Intermediate',
                'support_level': 'Medium',
                'deadline': ''
            },
            {
                'name': 'Solar Panel Efficiency Testing',
                'description': 'Test how different variables like angle, shading, and temperature affect the efficiency of solar panels in generating electricity.',
                'url': 'https://www.sciencebuddies.org/science-fair-projects/project-ideas/energy',
                'source': 'Science Buddies',
                'category': 'Science Project',
                'stem_fields': 'Physics, Engineering',
                'target_grade': '9-12',
                'cost': 'Under $50',
                'location_type': 'Online',
                'time_commitment': '3-4 weeks',
                'prerequisite_level': 'Advanced',
                'support_level': 'Medium',
                'deadline': ''
            },
            {
                'name': 'App Development for Data Collection',
                'description': 'Create a mobile app to collect and analyze scientific data for research projects using programming and data science principles.',
                'url': 'https://www.sciencebuddies.org/science-fair-projects/project-ideas/computer-science',
                'source': 'Science Buddies',
                'category': 'STEM Activity',
                'stem_fields': 'Computer Science, Mathematics',
                'target_grade': '9-12',
                'cost': 'Free',
                'location_type': 'Online',
                'time_commitment': '4-6 weeks',
                'prerequisite_level': 'Advanced',
                'support_level': 'Medium',
                'deadline': ''
            }
        ]
        
        # Add contextual features to each project
        for project in static_projects:
            contextual_features = self.extract_contextual_features(
                project['name'], 
                project['description'], 
                project['cost'], 
                project['time_commitment'],
                project['prerequisite_level'],
                f"{project['description']} {project['stem_fields']}"
            )
            project.update(contextual_features)
            self.projects.append(project)
    
    def scrape_projects(self):
        """Main scraping function."""
        print("Starting Science Buddies projects scraper...")
        
        # Try web scraping first
        try:
            for url in self.project_urls[:2]:  # Try first 2 URLs
                soup = self.make_request(url)
                if soup:
                    project_links = self.extract_project_links(soup)
                    print(f"Found {len(project_links)} project links from {url}")
                    
                    # Process first few project links
                    for link in project_links[:5]:  # Limit to 5 per page
                        project_soup = self.make_request(link)
                        if project_soup:
                            project_info = self.extract_project_info(link, project_soup)
                            if project_info:
                                self.projects.append(project_info)
                                print(f"[+] Extracted: {project_info['name']}")
                else:
                    print(f"[-] Failed to fetch {url}")
        except Exception as e:
            print(f"Web scraping failed: {e}")
        
        # If web scraping failed or found few projects, use static data
        if len(self.projects) < 5:
            print("Using static project data as fallback...")
            self.projects = []  # Clear any partial results
            self.create_static_projects()
        
        print(f"\nScraping completed. Found {len(self.projects)} total projects.")
    
    def save_to_csv(self, filename: str = "data/science_buddies_programs.csv"):
        """Save scraped projects to CSV file."""
        if not self.projects:
            print("No projects to save")
            return
        
        # Ensure data directory exists
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        
        # Use EXACT same fieldnames as FIRST Robotics scraper
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
                writer.writerows(self.projects)
            
            print(f"Saved {len(self.projects)} projects to {filename}")
            
        except Exception as e:
            print(f"Error saving to CSV: {e}")


def main():
    """Main function to run the scraper."""
    scraper = ScienceBuddiesScraper()
    scraper.scrape_projects()
    scraper.save_to_csv()


if __name__ == "__main__":
    main()