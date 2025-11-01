#!/usr/bin/env python3
"""
FIRST Robotics Programs Scraper

Scrapes FIRST Robotics programs (FRC, FTC, FLL) from https://www.firstinspires.org
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


class FIRSTRoboticsScraper:
    def __init__(self):
        self.base_url = "https://www.firstinspires.org"
        self.start_url = "https://www.firstinspires.org/robotics"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.programs = []
        
        # Known FIRST program URLs to ensure we get all major programs
        self.program_urls = [
            "https://www.firstinspires.org/robotics/frc",
            "https://www.firstinspires.org/robotics/ftc", 
            "https://www.firstinspires.org/robotics/fll"
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
        """Extract program links from the main robotics page."""
        # Focus on main program pages only, not sub-pages
        main_program_links = [
            "https://www.firstinspires.org/robotics/frc",
            "https://www.firstinspires.org/robotics/ftc", 
            "https://www.firstinspires.org/robotics/fll"
        ]
        
        return main_program_links
    
    def extract_cost_info(self, soup: BeautifulSoup) -> str:
        """Extract cost/fee information from program pages."""
        cost = "Varies"
        text = soup.get_text().lower()
        
        # Look for cost patterns
        cost_patterns = [
            r'\$[\d,]+',
            r'registration fee[:\s]*\$?[\d,]+',
            r'team fee[:\s]*\$?[\d,]+',
            r'cost[:\s]*\$?[\d,]+',
            r'fee[:\s]*\$?[\d,]+'
        ]
        
        for pattern in cost_patterns:
            matches = re.findall(pattern, text)
            if matches:
                cost = matches[0]
                break
        
        # Look for "free" mentions
        if any(term in text for term in ['free', 'no cost', 'no fee']):
            cost = "Free"
            
        return cost
    
    def extract_timeline_info(self, soup: BeautifulSoup) -> str:
        """Extract season timeline and time commitment information."""
        timeline = ""
        text = soup.get_text().lower()
        
        # Look for timeline patterns
        timeline_patterns = [
            r'(\d+)\s*weeks?',
            r'(\d+)\s*months?',
            r'season\s+runs\s+([^.]+)',
            r'timeline[:\s]*([^.]+)',
            r'duration[:\s]*([^.]+)'
        ]
        
        for pattern in timeline_patterns:
            match = re.search(pattern, text)
            if match:
                timeline = match.group(1) if len(match.groups()) == 1 else match.group(0)
                break
        
        # Look for specific season mentions
        if 'kickoff' in text and 'championship' in text:
            timeline = "Kickoff to Championship (6 months)"
        elif 'september' in text and 'april' in text:
            timeline = "September to April"
        elif 'build season' in text:
            timeline = "Build season (6-8 weeks)"
            
        return timeline
    
    def extract_deadline_info(self, soup: BeautifulSoup) -> str:
        """Extract registration deadlines."""
        deadline = ""
        text = soup.get_text().lower()
        
        # Look for deadline patterns
        deadline_patterns = [
            r'registration\s+deadline[:\s]*([^.]+)',
            r'deadline[:\s]*([^.]+)',
            r'register\s+by[:\s]*([^.]+)',
            r'registration\s+closes[:\s]*([^.]+)'
        ]
        
        for pattern in deadline_patterns:
            match = re.search(pattern, text)
            if match:
                deadline = match.group(1).strip()[:100]
                break
                
        return deadline
    
    def extract_grade_range(self, program_name: str, soup: BeautifulSoup) -> str:
        """Extract grade range based on program type and page content."""
        text = soup.get_text().lower()
        
        # Default grade ranges for known programs
        if 'fll' in program_name.lower():
            return "PreK-8"
        elif 'ftc' in program_name.lower():
            return "7-12"
        elif 'frc' in program_name.lower():
            return "9-12"
        
        # Look for grade mentions in text
        grade_patterns = [
            r'grades?\s+(\d+[\-\s]*\d*)',
            r'(\d+)[\-\s]*(\d+)\s+grade',
            r'ages?\s+(\d+[\-\s]*\d*)'
        ]
        
        for pattern in grade_patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1)
        
        return "K-12"
    
    def extract_program_info(self, url: str, soup: BeautifulSoup) -> Optional[Dict]:
        """Extract program information from a FIRST program page."""
        try:
            # Extract program name
            name = None
            for selector in ['h1', '.page-title', 'title', '.hero-title']:
                title_elem = soup.select_one(selector)
                if title_elem:
                    name = title_elem.get_text().strip()
                    # Clean up title
                    name = re.sub(r'\s*\|\s*FIRST.*$', '', name)
                    name = re.sub(r'\s*-\s*FIRST.*$', '', name)
                    break
            
            if not name:
                # Extract from URL
                if 'frc' in url:
                    name = "FIRST Robotics Competition (FRC)"
                elif 'ftc' in url:
                    name = "FIRST Tech Challenge (FTC)"
                elif 'fll' in url:
                    name = "FIRST LEGO League (FLL)"
                else:
                    return None
            
            # Extract description
            description = ""
            # Look for main content areas
            content_selectors = [
                '.hero-content p', '.main-content p', '.program-description',
                '.intro p', '.overview p', 'main p', '.content p'
            ]
            
            for selector in content_selectors:
                paragraphs = soup.select(selector)
                if paragraphs:
                    desc_parts = []
                    for p in paragraphs[:3]:  # First 3 paragraphs
                        text = p.get_text().strip()
                        if len(text) > 30:  # Skip very short paragraphs
                            desc_parts.append(text)
                        if len(' '.join(desc_parts)) >= 400:
                            break
                    if desc_parts:
                        description = ' '.join(desc_parts)[:500]
                        break
            
            # If no good description found, try broader search
            if not description:
                all_paragraphs = soup.find_all('p')
                for p in all_paragraphs[:5]:
                    text = p.get_text().strip()
                    if (len(text) > 50 and 
                        any(keyword in text.lower() for keyword in ['robot', 'team', 'competition', 'students', 'stem'])):
                        description = text[:500]
                        break
            
            # Extract other details with better defaults based on program type
            grade_range = self.extract_grade_range(name, soup)
            cost = self.extract_cost_info(soup)
            timeline = self.extract_timeline_info(soup)
            deadline = self.extract_deadline_info(soup)
            
            # Set better defaults based on program type
            if 'frc' in name.lower():
                if not timeline:
                    timeline = "January-April (Build season + competitions)"
                if not deadline:
                    deadline = "December (team registration)"
                cost = cost if cost != "Varies" else "$6,000-$15,000"
                grade_range = "9-12"
            elif 'ftc' in name.lower():
                if not timeline:
                    timeline = "September-April (Season + championships)"
                if not deadline:
                    deadline = "August-September (team registration)"
                cost = cost if cost != "Varies" else "$275 registration + materials"
                grade_range = "7-12"
            elif 'fll' in name.lower():
                if not timeline:
                    timeline = "August-February (Season + tournaments)"
                if not deadline:
                    deadline = "October (team registration)"
                cost = cost if cost != "Varies" else "$225 + robot kit"
                grade_range = "K-8"
            
            # Extract comprehensive ML contextual features
            contextual_features = self.extract_contextual_features(name, description, cost, timeline, soup)
            
            return {
                'name': name,
                'description': description,
                'url': url,
                'source': 'FIRST Robotics',
                'category': 'Robotics Competition',
                'stem_fields': 'Engineering, Programming, Design',
                'target_grade': grade_range,
                'cost': cost,
                'location_type': 'Regional',
                'time_commitment': timeline,
                'prerequisite_level': 'None',
                'support_level': 'High',
                'deadline': deadline,
                **contextual_features
            }
            
        except Exception as e:
            print(f"Error extracting info from {url}: {e}")
            return None
    
    def extract_contextual_features(self, name: str, description: str, cost: str, timeline: str, soup: Optional[BeautifulSoup]) -> Dict:
        """Extract comprehensive ML contextual features for the program."""
        features = {}
        
        # Analyze all available text
        all_text = f"{name} {description} {cost} {timeline}".lower()
        if soup:
            all_text += " " + soup.get_text().lower()
        
        # Financial Context
        features.update(self.analyze_financial_context(cost, all_text))
        
        # Diversity & Inclusion
        features.update(self.analyze_diversity_inclusion(all_text))
        
        # Geographic & Access
        features.update(self.analyze_geographic_access(all_text, name))
        
        # Family/Social Context
        features.update(self.analyze_family_social_context(all_text, name))
        
        return features
    
    def analyze_financial_context(self, cost: str, text: str) -> Dict:
        """Analyze financial barriers and accessibility."""
        features = {}
        
        # Extract numeric cost if possible
        cost_amount = 0
        if '$' in cost:
            import re
            numbers = re.findall(r'\$[\d,]+', cost)
            if numbers:
                cost_amount = int(numbers[0].replace('$', '').replace(',', ''))
        
        # financial_barrier_level
        if 'free' in cost.lower() or cost_amount == 0:
            features['financial_barrier_level'] = 'None'
        elif cost_amount <= 200:
            features['financial_barrier_level'] = 'Low'
        elif cost_amount <= 1000:
            features['financial_barrier_level'] = 'Medium'
        elif cost_amount <= 5000:
            features['financial_barrier_level'] = 'High'
        else:
            features['financial_barrier_level'] = 'Prohibitive'
        
        # financial_aid_available
        aid_keywords = ['scholarship', 'grant', 'financial aid', 'need-based', 'assistance', 'funding']
        features['financial_aid_available'] = any(keyword in text for keyword in aid_keywords)
        
        # family_income_consideration
        if cost_amount <= 300 or 'free' in cost.lower():
            features['family_income_consideration'] = 'Any'
        elif any(term in text for term in ['low-income', 'need-based', 'financial assistance']):
            features['family_income_consideration'] = 'Low-income-focus'
        else:
            features['family_income_consideration'] = 'Middle+'
        
        # hidden_costs_level
        hidden_costs = []
        if any(term in text for term in ['travel', 'transportation', 'hotel', 'flight']):
            hidden_costs.append('Travel')
        if any(term in text for term in ['equipment', 'materials', 'parts', 'tools']):
            hidden_costs.append('Equipment')
        if any(term in text for term in ['gas', 'driving', 'bus', 'transport']):
            hidden_costs.append('Transportation')
        
        features['hidden_costs_level'] = ', '.join(hidden_costs) if hidden_costs else 'None'
        
        # cost_category
        if cost_amount == 0 or 'free' in cost.lower():
            features['cost_category'] = 'Free'
        elif cost_amount <= 100:
            features['cost_category'] = 'Under-$100'
        elif cost_amount <= 500:
            features['cost_category'] = '$100-500'
        elif cost_amount <= 2000:
            features['cost_category'] = '$500-2000'
        else:
            features['cost_category'] = '$2000+'
        
        return features
    
    def analyze_diversity_inclusion(self, text: str) -> Dict:
        """Analyze diversity and inclusion focus."""
        features = {}
        
        # diversity_focus
        diversity_keywords = ['diversity', 'inclusion', 'inclusive', 'underrepresented', 'minority', 'equity']
        features['diversity_focus'] = any(keyword in text for keyword in diversity_keywords)
        
        # underrepresented_friendly
        welcoming_keywords = ['welcoming', 'all backgrounds', 'everyone', 'accessible', 'supportive', 'inclusive']
        features['underrepresented_friendly'] = any(keyword in text for keyword in welcoming_keywords)
        
        # first_gen_support
        beginner_keywords = ['no experience', 'beginner', 'newcomer', 'first time', 'mentorship', 'guidance']
        features['first_gen_support'] = any(keyword in text for keyword in beginner_keywords)
        
        # cultural_competency
        if any(term in text for term in ['cultural', 'multicultural', 'global', 'international']):
            features['cultural_competency'] = 'High'
        elif any(term in text for term in ['diverse', 'inclusive', 'community']):
            features['cultural_competency'] = 'Medium'
        else:
            features['cultural_competency'] = 'Low'
        
        return features
    
    def analyze_geographic_access(self, text: str, name: str) -> Dict:
        """Analyze geographic accessibility and requirements."""
        features = {}
        
        # rural_accessible
        online_keywords = ['online', 'virtual', 'remote', 'digital']
        urban_keywords = ['city', 'urban', 'metropolitan', 'downtown']
        features['rural_accessible'] = any(keyword in text for keyword in online_keywords) or not any(keyword in text for keyword in urban_keywords)
        
        # transportation_required
        travel_keywords = ['travel', 'event', 'competition', 'tournament', 'championship']
        features['transportation_required'] = any(keyword in text for keyword in travel_keywords)
        
        # internet_dependency
        if any(term in text for term in ['programming', 'coding', 'software', 'app']):
            features['internet_dependency'] = 'Basic'
        elif any(term in text for term in ['streaming', 'video', 'cloud', 'online platform']):
            features['internet_dependency'] = 'High-speed-required'
        else:
            features['internet_dependency'] = 'None'
        
        # regional_availability
        if 'championship' in name.lower() or 'world' in name.lower():
            features['regional_availability'] = 'Select-regions'
        elif any(term in text for term in ['national', 'worldwide', 'global']):
            features['regional_availability'] = 'National'
        else:
            features['regional_availability'] = 'National'
        
        return features
    
    def analyze_family_social_context(self, text: str, name: str) -> Dict:
        """Analyze family involvement and social context."""
        features = {}
        
        # family_involvement_required
        if any(term in text for term in ['parent', 'guardian', 'family', 'caregiver']):
            features['family_involvement_required'] = 'Required'
        elif any(term in text for term in ['encourage', 'welcome', 'invite']):
            features['family_involvement_required'] = 'Optional'
        else:
            features['family_involvement_required'] = 'None'
        
        # peer_network_building
        team_keywords = ['team', 'collaboration', 'partnership', 'community', 'network', 'alliance']
        features['peer_network_building'] = any(keyword in text for keyword in team_keywords)
        
        # mentor_access_level
        if any(term in text for term in ['professional', 'industry', 'expert', 'specialist']):
            features['mentor_access_level'] = 'Professional'
        elif any(term in text for term in ['mentor', 'coach', 'advisor', 'adult']):
            features['mentor_access_level'] = 'Adult'
        elif any(term in text for term in ['peer', 'student', 'teammate']):
            features['mentor_access_level'] = 'Peer'
        else:
            features['mentor_access_level'] = 'None'
        
        return features
    
    def extract_additional_opportunities(self, soup: BeautifulSoup, base_program: Dict) -> List[Dict]:
        """Extract additional opportunities from program pages (events, regional variations, etc.)."""
        opportunities = []
        
        # Create detailed variations for different aspects of each program
        if 'frc' in base_program['name'].lower():
            # FRC Season variations
            opportunities.extend([
                {
                    **base_program,
                    'name': 'FIRST Robotics Competition - Build Season',
                    'description': 'Six-week robot build period where FRC teams design, prototype, and build their competition robot using the Kit of Parts and additional materials.',
                    'time_commitment': '6 weeks (January-February)',
                    'target_grade': '9-12',
                    'cost': '$6,000-$15,000 (team registration + materials)'
                },
                {
                    **base_program,
                    'name': 'FIRST Robotics Competition - Regional Events',
                    'description': 'Regional competition events where FRC teams compete with their robots in alliance-based matches to qualify for championship.',
                    'time_commitment': '2-3 weekends (March-April)',
                    'target_grade': '9-12',
                    'deadline': 'Team registration by December'
                },
                {
                    **base_program,
                    'name': 'FIRST Robotics Competition - Championship',
                    'description': 'Annual world championship event in Houston and Detroit for qualifying FRC teams. The ultimate robotics competition experience.',
                    'time_commitment': '1 week (April)',
                    'target_grade': '9-12',
                    'cost': 'Qualification required + travel expenses'
                }
            ])
            
        elif 'ftc' in base_program['name'].lower():
            # FTC Season variations  
            opportunities.extend([
                {
                    **base_program,
                    'name': 'FIRST Tech Challenge - League Tournaments',
                    'description': 'Local league tournaments where FTC teams compete throughout the season. Teams earn ranking points to advance to championship events.',
                    'time_commitment': 'October-February (multiple events)',
                    'target_grade': '7-12',
                    'cost': '$275 team registration fee'
                },
                {
                    **base_program,
                    'name': 'FIRST Tech Challenge - Super Regional Championships',
                    'description': 'Regional championship events where top FTC teams compete for advancement to the World Championship.',
                    'time_commitment': 'February-March',
                    'target_grade': '7-12',
                    'cost': 'Qualification required'
                },
                {
                    **base_program,
                    'name': 'FIRST Tech Challenge - World Championship',
                    'description': 'Global championship event in Houston where the best FTC teams from around the world compete.',
                    'time_commitment': '4 days (April)',
                    'target_grade': '7-12',
                    'cost': 'Qualification + travel required'
                }
            ])
            
        elif 'fll' in base_program['name'].lower():
            # FLL Program variations by age group
            opportunities.extend([
                {
                    **base_program,
                    'name': 'FIRST LEGO League Discover (Ages 4-6)',
                    'description': 'Introductory STEM program for youngest learners using LEGO DUPLO. Children explore science and engineering concepts through play.',
                    'time_commitment': '8-12 weeks',
                    'target_grade': 'PreK-K',
                    'cost': '$100-200 per team'
                },
                {
                    **base_program,
                    'name': 'FIRST LEGO League Explore (Ages 6-10)', 
                    'description': 'Hands-on STEM program where teams build motorized models using LEGO WeDo 2.0 and create a poster to share their learning.',
                    'time_commitment': '12-16 weeks',
                    'target_grade': '1-4',
                    'cost': '$200-300 per team'
                },
                {
                    **base_program,
                    'name': 'FIRST LEGO League Challenge (Ages 9-16)',
                    'description': 'Competitive robotics program where teams design and program autonomous LEGO robots and complete an innovation project.',
                    'time_commitment': '12-16 weeks + tournaments',
                    'target_grade': '4-8',
                    'cost': '$225 team registration + robot kit'
                },
                {
                    **base_program,
                    'name': 'FIRST LEGO League - Regional Tournaments',
                    'description': 'Regional tournament competitions where FLL Challenge teams compete with their robots and present innovation projects.',
                    'time_commitment': '1-2 days (December-February)',
                    'target_grade': '4-8',
                    'deadline': 'Team registration by October'
                }
            ])
        
        return opportunities
    
    def create_static_programs(self):
        """Create static program data when web scraping fails."""
        static_programs = [
            # Base FIRST Programs
            {
                'name': 'FIRST Robotics Competition (FRC)',
                'description': 'High school robotics competition where teams design, build, and program industrial-sized robots to compete in alliance-based matches. Teams receive a kit of parts and have 6 weeks to build their robot.',
                'url': 'https://www.firstinspires.org/robotics/frc',
                'source': 'FIRST Robotics',
                'category': 'Robotics Competition',
                'stem_fields': 'Engineering, Programming, Design',
                'target_grade': '9-12',
                'cost': '$6,000-$15,000',
                'location_type': 'Regional',
                'time_commitment': 'January-April (Build season + competitions)',
                'prerequisite_level': 'None',
                'support_level': 'High',
                'deadline': 'December (team registration)'
            },
            {
                'name': 'FIRST Tech Challenge (FTC)',
                'description': 'Middle and high school robotics program where teams design and build robots using reusable parts to compete in head-to-head challenges with a sports-like atmosphere.',
                'url': 'https://www.firstinspires.org/robotics/ftc',
                'source': 'FIRST Robotics',
                'category': 'Robotics Competition',
                'stem_fields': 'Engineering, Programming, Design',
                'target_grade': '7-12',
                'cost': '$275 registration + materials',
                'location_type': 'Regional',
                'time_commitment': 'September-April (Season + championships)',
                'prerequisite_level': 'None',
                'support_level': 'High',
                'deadline': 'August-September (team registration)'
            },
            {
                'name': 'FIRST LEGO League (FLL)',
                'description': 'Elementary and middle school program introducing STEM concepts through hands-on robotics and research projects using LEGO technology.',
                'url': 'https://www.firstinspires.org/robotics/fll',
                'source': 'FIRST Robotics',
                'category': 'Robotics Competition',
                'stem_fields': 'Engineering, Programming, Design',
                'target_grade': 'K-8',
                'cost': '$225 + robot kit',
                'location_type': 'Regional',
                'time_commitment': 'August-February (Season + tournaments)',
                'prerequisite_level': 'None',
                'support_level': 'High',
                'deadline': 'October (team registration)'
            }
        ]
        
        # Add detailed opportunities for each program with contextual features
        for base_program in static_programs:
            # Add contextual features to base program
            contextual_features = self.extract_contextual_features(
                base_program['name'], 
                base_program['description'], 
                base_program['cost'], 
                base_program['time_commitment'], 
                None
            )
            base_program.update(contextual_features)
            self.programs.append(base_program)
            
            # Add contextual features to additional opportunities
            additional_opportunities = self.extract_additional_opportunities(None, base_program)
            for opp in additional_opportunities:
                opp_contextual = self.extract_contextual_features(
                    opp['name'], 
                    opp['description'], 
                    opp['cost'], 
                    opp['time_commitment'], 
                    None
                )
                opp.update(opp_contextual)
            self.programs.extend(additional_opportunities)
    
    def scrape_programs(self):
        """Main scraping function."""
        print("Starting FIRST Robotics programs scraper...")
        
        # Try web scraping first
        try:
            soup = self.make_request(self.start_url)
            if soup:
                program_links = self.extract_program_links(soup)
                print(f"Found {len(program_links)} program links")
                
                # Process each program link
                for i, link in enumerate(program_links, 1):
                    print(f"Processing program {i}/{len(program_links)}: {link}")
                    
                    program_soup = self.make_request(link)
                    if program_soup:
                        program_info = self.extract_program_info(link, program_soup)
                        if program_info:
                            self.programs.append(program_info)
                            print(f"[+] Extracted: {program_info['name']}")
                            
                            # Extract additional opportunities from this program page
                            additional_opportunities = self.extract_additional_opportunities(program_soup, program_info)
                            if additional_opportunities:
                                self.programs.extend(additional_opportunities)
                                print(f"[+] Added {len(additional_opportunities)} additional opportunities")
                        else:
                            print(f"[-] No valid program info found")
                    else:
                        print(f"[-] Failed to fetch page")
        except Exception as e:
            print(f"Web scraping failed: {e}")
        
        # If web scraping failed or found no programs, use static data
        if len(self.programs) == 0:
            print("Using static program data as fallback...")
            self.create_static_programs()
        
        print(f"\nScraping completed. Found {len(self.programs)} total programs/opportunities.")
    
    def save_to_csv(self, filename: str = "data/first_robotics_programs.csv"):
        """Save scraped programs to CSV file."""
        if not self.programs:
            print("No programs to save")
            return
        
        # Ensure data directory exists
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        
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
    scraper = FIRSTRoboticsScraper()
    scraper.scrape_programs()
    scraper.save_to_csv()


if __name__ == "__main__":
    main()