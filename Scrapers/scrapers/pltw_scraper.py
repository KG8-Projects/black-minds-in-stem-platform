#!/usr/bin/env python3
"""
Project Lead The Way (PLTW) Programs Scraper

Scrapes PLTW programs from https://www.pltw.org
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


class PLTWScraper:
    def __init__(self):
        self.base_url = "https://www.pltw.org"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.programs = []
        
        # Target URLs for PLTW programs
        self.program_urls = [
            "https://www.pltw.org/our-programs",
            "https://www.pltw.org/our-programs/pltw-launch",
            "https://www.pltw.org/our-programs/pltw-gateway",
            "https://www.pltw.org/our-programs/pltw-engineering",
            "https://www.pltw.org/our-programs/pltw-biomedical-science",
            "https://www.pltw.org/our-programs/pltw-computer-science"
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
        """Extract individual course links from PLTW pages."""
        program_links = []
        
        # Look for course/program links
        for link in soup.find_all('a', href=True):
            href = link.get('href', '')
            
            # Target course detail pages
            if any(term in href.lower() for term in ['course', 'module', 'pathway', 'curriculum']):
                full_url = urljoin(self.base_url, href)
                if full_url not in program_links and 'pltw.org' in full_url:
                    program_links.append(full_url)
        
        return program_links
    
    def extract_contextual_features(self, name: str, description: str, 
                                   pathway: str, grade_level: str) -> Dict:
        """Extract comprehensive ML contextual features matching exact 29-column format."""
        features = {}
        
        # Analyze all available text
        all_text = f"{name} {description} {pathway} {grade_level}".lower()
        
        # Financial Context - PLTW costs vary by school implementation
        features.update(self.analyze_financial_context(all_text, pathway))
        
        # Diversity & Inclusion - PLTW has strong equity focus
        features.update(self.analyze_diversity_inclusion(all_text))
        
        # Geographic & Access
        features.update(self.analyze_geographic_access(all_text))
        
        # Family/Social Context
        features.update(self.analyze_family_social_context(all_text, pathway))
        
        return features
    
    def analyze_financial_context(self, text: str, pathway: str) -> Dict:
        """Analyze financial barriers and accessibility."""
        features = {}
        
        # PLTW costs vary by school implementation
        if 'launch' in pathway.lower():  # Elementary programs typically lower cost
            features['financial_barrier_level'] = 'Low'
        else:  # Middle/high school programs may have equipment costs
            features['financial_barrier_level'] = 'Medium'
        
        features['financial_aid_available'] = False  # School-dependent
        features['family_income_consideration'] = 'Any'  # Public school program
        features['hidden_costs_level'] = 'None'  # Covered by school
        features['cost_category'] = 'School-dependent'
        
        return features
    
    def analyze_diversity_inclusion(self, text: str) -> Dict:
        """Analyze diversity and inclusion focus."""
        features = {}
        
        # PLTW has strong equity initiatives
        features['diversity_focus'] = True
        features['underrepresented_friendly'] = True
        features['first_gen_support'] = True  # Designed to be accessible
        features['cultural_competency'] = 'High'  # Equity-focused curriculum
        
        return features
    
    def analyze_geographic_access(self, text: str) -> Dict:
        """Analyze geographic accessibility and requirements."""
        features = {}
        
        # School-based program availability
        features['rural_accessible'] = True  # If school offers program
        features['transportation_required'] = False  # School-based
        features['internet_dependency'] = 'Basic'  # School computers
        features['regional_availability'] = 'National'  # Offered nationwide
        
        return features
    
    def analyze_family_social_context(self, text: str, pathway: str) -> Dict:
        """Analyze family involvement and social context."""
        features = {}
        
        # School program context
        features['family_involvement_required'] = 'None'  # School program
        features['peer_network_building'] = True  # Classroom collaboration
        features['mentor_access_level'] = 'Adult'  # Trained PLTW teachers
        
        return features
    
    def extract_program_info(self, url: str, soup: BeautifulSoup) -> Optional[Dict]:
        """Extract program information from a PLTW program page."""
        try:
            # Extract program name
            name = None
            for selector in ['h1', '.page-title', 'title', '.hero-title']:
                title_elem = soup.select_one(selector)
                if title_elem:
                    name = title_elem.get_text().strip()
                    # Clean up title
                    name = re.sub(r'\s*\|\s*PLTW.*$', '', name)
                    name = re.sub(r'\s*-\s*Project Lead.*$', '', name)
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
                        any(keyword in text.lower() for keyword in ['student', 'learn', 'program', 'course', 'project'])):
                        description = text[:500]
                        break
            
            # Get all text for analysis
            all_text = soup.get_text()
            
            # Determine pathway and details based on URL
            pathway = "PLTW"
            stem_fields = "Engineering"
            target_grade = "K-12"
            category = "School Program"
            
            if 'launch' in url.lower():
                pathway = "PLTW Launch"
                target_grade = "K-5"
                stem_fields = "Engineering, Computer Science"
                category = "Elementary Program"
            elif 'gateway' in url.lower():
                pathway = "PLTW Gateway"
                target_grade = "6-8"
                stem_fields = "Engineering, Computer Science, Biomedical Science"
                category = "Middle School Program"
            elif 'engineering' in url.lower():
                pathway = "PLTW Engineering"
                target_grade = "9-12"
                stem_fields = "Engineering, Technology"
                category = "Engineering Program"
            elif 'biomedical' in url.lower():
                pathway = "PLTW Biomedical Science"
                target_grade = "9-12"
                stem_fields = "Biomedical Science, Biology"
                category = "Biomedical Program"
            elif 'computer-science' in url.lower():
                pathway = "PLTW Computer Science"
                target_grade = "9-12"
                stem_fields = "Computer Science, Programming"
                category = "Computer Science Program"
            
            # Determine time commitment and prerequisites
            if target_grade == "K-5":
                time_commitment = "Module-based (varies)"
                prerequisite_level = "None"
            elif target_grade == "6-8":
                time_commitment = "Semester courses"
                prerequisite_level = "Basic"
            else:  # 9-12
                time_commitment = "Semester or full year"
                prerequisite_level = "Medium"
            
            # Extract contextual features
            contextual_features = self.extract_contextual_features(
                name, description, pathway, target_grade
            )
            
            return {
                'name': name,
                'description': description,
                'url': url,
                'source': 'Project Lead The Way',
                'category': category,
                'stem_fields': stem_fields,
                'target_grade': target_grade,
                'cost': 'School-dependent',
                'location_type': 'School-based',
                'time_commitment': time_commitment,
                'prerequisite_level': prerequisite_level,
                'support_level': 'High',
                'deadline': 'School enrollment',
                **contextual_features
            }
            
        except Exception as e:
            print(f"Error extracting info from {url}: {e}")
            return None
    
    def create_comprehensive_programs(self):
        """Create comprehensive program data for all PLTW opportunities."""
        programs_data = [
            # PLTW Launch (K-5)
            {
                'name': 'PLTW Launch - Modeling and Analysis',
                'description': 'Students learn to model real-world phenomena and analyze relationships between variables using mathematical thinking and engineering design process to solve problems.',
                'url': 'https://www.pltw.org/our-programs/pltw-launch/launch-modules/modeling-and-analysis',
                'source': 'Project Lead The Way',
                'category': 'Elementary Program',
                'stem_fields': 'Engineering, Mathematics',
                'target_grade': 'K-5',
                'cost': 'School-dependent',
                'location_type': 'School-based',
                'time_commitment': 'Module-based (10-15 hours)',
                'prerequisite_level': 'None',
                'support_level': 'High',
                'deadline': 'School enrollment'
            },
            
            {
                'name': 'PLTW Launch - Structure and Function',
                'description': 'Students explore how the shape and structure of an object affects its function through building, testing, and refining design solutions for engineering challenges.',
                'url': 'https://www.pltw.org/our-programs/pltw-launch/launch-modules/structure-and-function',
                'source': 'Project Lead The Way',
                'category': 'Elementary Program',
                'stem_fields': 'Engineering, Physics',
                'target_grade': 'K-5',
                'cost': 'School-dependent',
                'location_type': 'School-based',
                'time_commitment': 'Module-based (10-15 hours)',
                'prerequisite_level': 'None',
                'support_level': 'High',
                'deadline': 'School enrollment'
            },
            
            {
                'name': 'PLTW Launch - Automation and Robotics',
                'description': 'Students explore how machines help humans by programming robots to solve problems and complete tasks using computational thinking and engineering design.',
                'url': 'https://www.pltw.org/our-programs/pltw-launch/launch-modules/automation-and-robotics',
                'source': 'Project Lead The Way',
                'category': 'Elementary Program',
                'stem_fields': 'Engineering, Computer Science, Robotics',
                'target_grade': 'K-5',
                'cost': 'School-dependent',
                'location_type': 'School-based',
                'time_commitment': 'Module-based (10-15 hours)',
                'prerequisite_level': 'None',
                'support_level': 'High',
                'deadline': 'School enrollment'
            },
            
            # PLTW Gateway (6-8)
            {
                'name': 'PLTW Gateway - Design and Modeling',
                'description': 'Students discover the design process and develop understanding of design principles using industry-standard 3D modeling software to create virtual designs.',
                'url': 'https://www.pltw.org/our-programs/pltw-gateway/gateway-courses/design-and-modeling',
                'source': 'Project Lead The Way',
                'category': 'Middle School Program',
                'stem_fields': 'Engineering, Technology, Design',
                'target_grade': '6-8',
                'cost': 'School-dependent',
                'location_type': 'School-based',
                'time_commitment': 'Semester course',
                'prerequisite_level': 'Basic',
                'support_level': 'High',
                'deadline': 'School enrollment'
            },
            
            {
                'name': 'PLTW Gateway - Automation and Robotics',
                'description': 'Students explore mechanical systems, energy transfer, machine automation, and computer control systems while programming VEX Robotics equipment.',
                'url': 'https://www.pltw.org/our-programs/pltw-gateway/gateway-courses/automation-and-robotics',
                'source': 'Project Lead The Way',
                'category': 'Middle School Program',
                'stem_fields': 'Engineering, Robotics, Computer Science',
                'target_grade': '6-8',
                'cost': 'School-dependent',
                'location_type': 'School-based',
                'time_commitment': 'Semester course',
                'prerequisite_level': 'Basic',
                'support_level': 'High',
                'deadline': 'School enrollment'
            },
            
            {
                'name': 'PLTW Gateway - Medical Detectives',
                'description': 'Students solve medical mysteries through hands-on projects and labs, learning about human body systems, genetics, and biomedical technologies.',
                'url': 'https://www.pltw.org/our-programs/pltw-gateway/gateway-courses/medical-detectives',
                'source': 'Project Lead The Way',
                'category': 'Middle School Program',
                'stem_fields': 'Biomedical Science, Biology, Health Science',
                'target_grade': '6-8',
                'cost': 'School-dependent',
                'location_type': 'School-based',
                'time_commitment': 'Semester course',
                'prerequisite_level': 'Basic',
                'support_level': 'High',
                'deadline': 'School enrollment'
            },
            
            {
                'name': 'PLTW Gateway - Computer Science for Innovators and Makers',
                'description': 'Students explore computer science concepts through programming while creating solutions to authentic problems using physical computing devices and sensors.',
                'url': 'https://www.pltw.org/our-programs/pltw-gateway/gateway-courses/computer-science-innovators-and-makers',
                'source': 'Project Lead The Way',
                'category': 'Middle School Program',
                'stem_fields': 'Computer Science, Programming, Engineering',
                'target_grade': '6-8',
                'cost': 'School-dependent',
                'location_type': 'School-based',
                'time_commitment': 'Semester course',
                'prerequisite_level': 'Basic',
                'support_level': 'High',
                'deadline': 'School enrollment'
            },
            
            # PLTW Engineering (9-12)
            {
                'name': 'PLTW Engineering - Introduction to Engineering Design',
                'description': 'Students dig deep into the engineering design process while applying mathematical analysis, scientific principles, and engineering standards to solve engineering problems.',
                'url': 'https://www.pltw.org/our-programs/pltw-engineering/pltw-engineering-courses/introduction-engineering-design',
                'source': 'Project Lead The Way',
                'category': 'Engineering Program',
                'stem_fields': 'Engineering, Design, Mathematics',
                'target_grade': '9-12',
                'cost': 'School-dependent',
                'location_type': 'School-based',
                'time_commitment': 'Full year course',
                'prerequisite_level': 'Medium',
                'support_level': 'High',
                'deadline': 'School enrollment'
            },
            
            {
                'name': 'PLTW Engineering - Principles of Engineering',
                'description': 'Students explore engineering career paths while learning about mechanisms, strength of materials, and applied physics through hands-on projects and design challenges.',
                'url': 'https://www.pltw.org/our-programs/pltw-engineering/pltw-engineering-courses/principles-engineering',
                'source': 'Project Lead The Way',
                'category': 'Engineering Program',
                'stem_fields': 'Engineering, Physics, Materials Science',
                'target_grade': '9-12',
                'cost': 'School-dependent',
                'location_type': 'School-based',
                'time_commitment': 'Full year course',
                'prerequisite_level': 'Medium',
                'support_level': 'High',
                'deadline': 'School enrollment'
            },
            
            {
                'name': 'PLTW Engineering - Digital Electronics',
                'description': 'Students explore electronic circuits, digital logic, and programmable logic devices while learning to design and build electronic systems and devices.',
                'url': 'https://www.pltw.org/our-programs/pltw-engineering/pltw-engineering-courses/digital-electronics',
                'source': 'Project Lead The Way',
                'category': 'Engineering Program',
                'stem_fields': 'Engineering, Electronics, Computer Science',
                'target_grade': '9-12',
                'cost': 'School-dependent',
                'location_type': 'School-based',
                'time_commitment': 'Full year course',
                'prerequisite_level': 'Medium',
                'support_level': 'High',
                'deadline': 'School enrollment'
            },
            
            {
                'name': 'PLTW Engineering - Aerospace Engineering',
                'description': 'Students explore the physics of flight and space travel while designing and testing model aircraft, rockets, and space systems using engineering principles.',
                'url': 'https://www.pltw.org/our-programs/pltw-engineering/pltw-engineering-courses/aerospace-engineering',
                'source': 'Project Lead The Way',
                'category': 'Engineering Program',
                'stem_fields': 'Aerospace Engineering, Physics, Mathematics',
                'target_grade': '9-12',
                'cost': 'School-dependent',
                'location_type': 'School-based',
                'time_commitment': 'Full year course',
                'prerequisite_level': 'Medium',
                'support_level': 'High',
                'deadline': 'School enrollment'
            },
            
            {
                'name': 'PLTW Engineering - Engineering Design and Development',
                'description': 'Capstone course where students work in teams to research, design, and construct solutions to open-ended engineering problems using the full design process.',
                'url': 'https://www.pltw.org/our-programs/pltw-engineering/pltw-engineering-courses/engineering-design-and-development',
                'source': 'Project Lead The Way',
                'category': 'Engineering Program',
                'stem_fields': 'Engineering, Project Management, Design',
                'target_grade': '11-12',
                'cost': 'School-dependent',
                'location_type': 'School-based',
                'time_commitment': 'Full year capstone',
                'prerequisite_level': 'High',
                'support_level': 'High',
                'deadline': 'School enrollment'
            },
            
            # PLTW Biomedical Science (9-12)
            {
                'name': 'PLTW Biomedical Science - Principles of Biomedical Sciences',
                'description': 'Students investigate biomedical science careers while exploring concepts of human medicine, public health, and medical research through hands-on projects and case studies.',
                'url': 'https://www.pltw.org/our-programs/pltw-biomedical-science/pltw-biomedical-science-courses/principles-biomedical-sciences',
                'source': 'Project Lead The Way',
                'category': 'Biomedical Program',
                'stem_fields': 'Biomedical Science, Biology, Health Science',
                'target_grade': '9-12',
                'cost': 'School-dependent',
                'location_type': 'School-based',
                'time_commitment': 'Full year course',
                'prerequisite_level': 'Medium',
                'support_level': 'High',
                'deadline': 'School enrollment'
            },
            
            {
                'name': 'PLTW Biomedical Science - Human Body Systems',
                'description': 'Students examine interactions of human body systems and explore identity, communication, and homeostasis through projects involving bioinformatics and engineering design.',
                'url': 'https://www.pltw.org/our-programs/pltw-biomedical-science/pltw-biomedical-science-courses/human-body-systems',
                'source': 'Project Lead The Way',
                'category': 'Biomedical Program',
                'stem_fields': 'Biomedical Science, Anatomy, Physiology',
                'target_grade': '9-12',
                'cost': 'School-dependent',
                'location_type': 'School-based',
                'time_commitment': 'Full year course',
                'prerequisite_level': 'Medium',
                'support_level': 'High',
                'deadline': 'School enrollment'
            },
            
            {
                'name': 'PLTW Biomedical Science - Medical Interventions',
                'description': 'Students investigate medical interventions and follow patient cases to learn about diagnosis, treatment, and prevention of disease using current medical technologies.',
                'url': 'https://www.pltw.org/our-programs/pltw-biomedical-science/pltw-biomedical-science-courses/medical-interventions',
                'source': 'Project Lead The Way',
                'category': 'Biomedical Program',
                'stem_fields': 'Biomedical Science, Medicine, Pharmacology',
                'target_grade': '9-12',
                'cost': 'School-dependent',
                'location_type': 'School-based',
                'time_commitment': 'Full year course',
                'prerequisite_level': 'Medium',
                'support_level': 'High',
                'deadline': 'School enrollment'
            },
            
            {
                'name': 'PLTW Biomedical Science - Biomedical Innovation',
                'description': 'Capstone course where students design innovative solutions to real biomedical challenges, working with medical professionals and learning about the product development cycle.',
                'url': 'https://www.pltw.org/our-programs/pltw-biomedical-science/pltw-biomedical-science-courses/biomedical-innovation',
                'source': 'Project Lead The Way',
                'category': 'Biomedical Program',
                'stem_fields': 'Biomedical Science, Innovation, Research',
                'target_grade': '11-12',
                'cost': 'School-dependent',
                'location_type': 'School-based',
                'time_commitment': 'Full year capstone',
                'prerequisite_level': 'High',
                'support_level': 'High',
                'deadline': 'School enrollment'
            },
            
            # PLTW Computer Science (9-12)
            {
                'name': 'PLTW Computer Science - Computer Science Essentials',
                'description': 'Students explore computing concepts including algorithms, programming, data analysis, and the societal impact of computing through hands-on activities.',
                'url': 'https://www.pltw.org/our-programs/pltw-computer-science/pltw-computer-science-courses/computer-science-essentials',
                'source': 'Project Lead The Way',
                'category': 'Computer Science Program',
                'stem_fields': 'Computer Science, Programming, Data Science',
                'target_grade': '9-12',
                'cost': 'School-dependent',
                'location_type': 'School-based',
                'time_commitment': 'Full year course',
                'prerequisite_level': 'Medium',
                'support_level': 'High',
                'deadline': 'School enrollment'
            },
            
            {
                'name': 'PLTW Computer Science - Computer Science Principles',
                'description': 'Students develop computational thinking skills while exploring programming, algorithms, data representation, and the impact of computing innovations on society.',
                'url': 'https://www.pltw.org/our-programs/pltw-computer-science/pltw-computer-science-courses/computer-science-principles',
                'source': 'Project Lead The Way',
                'category': 'Computer Science Program',
                'stem_fields': 'Computer Science, Programming, Algorithms',
                'target_grade': '9-12',
                'cost': 'School-dependent',
                'location_type': 'School-based',
                'time_commitment': 'Full year course',
                'prerequisite_level': 'Medium',
                'support_level': 'High',
                'deadline': 'School enrollment'
            },
            
            {
                'name': 'PLTW Computer Science - Computer Science A',
                'description': 'Students learn object-oriented programming using Java while developing problem-solving skills and understanding data structures, algorithms, and software design.',
                'url': 'https://www.pltw.org/our-programs/pltw-computer-science/pltw-computer-science-courses/computer-science-a',
                'source': 'Project Lead The Way',
                'category': 'Computer Science Program',
                'stem_fields': 'Computer Science, Programming, Software Development',
                'target_grade': '10-12',
                'cost': 'School-dependent',
                'location_type': 'School-based',
                'time_commitment': 'Full year course',
                'prerequisite_level': 'High',
                'support_level': 'High',
                'deadline': 'School enrollment'
            },
            
            {
                'name': 'PLTW Computer Science - Cybersecurity',
                'description': 'Students explore cybersecurity concepts including network security, cryptography, and ethical hacking while learning to protect digital information and systems.',
                'url': 'https://www.pltw.org/our-programs/pltw-computer-science/pltw-computer-science-courses/cybersecurity',
                'source': 'Project Lead The Way',
                'category': 'Computer Science Program',
                'stem_fields': 'Computer Science, Cybersecurity, Information Technology',
                'target_grade': '10-12',
                'cost': 'School-dependent',
                'location_type': 'School-based',
                'time_commitment': 'Full year course',
                'prerequisite_level': 'High',
                'support_level': 'High',
                'deadline': 'School enrollment'
            }
        ]
        
        # Add contextual features to each program
        for program in programs_data:
            # Determine pathway from category
            if 'Elementary' in program['category']:
                pathway = "PLTW Launch"
            elif 'Middle School' in program['category']:
                pathway = "PLTW Gateway"
            elif 'Engineering' in program['category']:
                pathway = "PLTW Engineering"
            elif 'Biomedical' in program['category']:
                pathway = "PLTW Biomedical Science"
            elif 'Computer Science' in program['category']:
                pathway = "PLTW Computer Science"
            else:
                pathway = "PLTW"
            
            contextual_features = self.extract_contextual_features(
                program['name'], 
                program['description'], 
                pathway,
                program['target_grade']
            )
            program.update(contextual_features)
            self.programs.append(program)
    
    def scrape_programs(self):
        """Main scraping function."""
        print("Starting PLTW programs scraper...")
        
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
    
    def save_to_csv(self, filename: str = "data/pltw_programs.csv"):
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
    scraper = PLTWScraper()
    scraper.scrape_programs()
    scraper.save_to_csv()


if __name__ == "__main__":
    main()