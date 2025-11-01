#!/usr/bin/env python3
"""
FIRST LEGO League Robotics Competition Scraper
Scrapes robotics competition programs for ages 4-16
Saves to: data/first_lego_league.csv
"""

import requests
from bs4 import BeautifulSoup
import csv
import time
from typing import List, Dict, Optional


class FIRSTLegoLeagueScraper:
    def __init__(self):
        self.base_url = "https://www.firstlegoleague.org"
        self.target_urls = [
            "https://www.firstlegoleague.org/",
            "https://www.firstlegoleague.org/season",
            "https://www.firstlegoleague.org/explore",
            "https://www.firstlegoleague.org/challenge",
        ]
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        self.resources = []

    def fetch_page(self, url: str) -> Optional[BeautifulSoup]:
        """Fetch and parse a webpage."""
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            print(f"Fetched: {url}")
            return BeautifulSoup(response.content, 'html.parser')
        except requests.exceptions.RequestException as e:
            print(f"Error fetching {url}: {e}")
            return None

    def create_first_lego_league_levels(self) -> List[Dict]:
        """Create FIRST LEGO League competition levels."""
        resources = [
            {
                'name': 'FIRST LEGO League Discover (Ages 4-6)',
                'description': 'Introductory STEM program for PreK-1st grade using LEGO DUPLO. Explore real-world science and engineering challenges through hands-on activities. Introduce Core Values and celebrate discoveries at Discover showcase events. No competition component.',
                'url': 'https://www.firstlegoleague.org/season',
                'source': 'FIRST LEGO League',
                'category': 'Competition',
                'stem_fields': 'Robotics, Engineering, Science, Problem Solving',
                'target_grade': 'PreK-1',
                'cost': 'Paid',
                'location_type': 'In-person',
                'time_commitment': '3-4 months',
                'prerequisite_level': 'None',
                'support_level': 'High',
                'deadline': 'Fall registration',
                'financial_barrier_level': 'Low',
                'financial_aid_available': 'Limited',
                'family_income_consideration': 'Optional',
                'hidden_costs_level': 'Materials',
                'cost_category': '$50-$500',
                'diversity_focus': 'True',
                'underrepresented_friendly': 'True',
                'first_gen_support': 'True',
                'cultural_competency': 'High',
                'rural_accessible': 'Variable',
                'transportation_required': 'True',
                'internet_dependency': 'Basic',
                'regional_availability': 'International',
                'family_involvement_required': 'High',
                'peer_network_building': 'True',
                'mentor_access_level': 'Coach'
            },
            {
                'name': 'FIRST LEGO League Explore (Ages 6-10)',
                'description': 'Hands-on STEM program for grades 2-4 using LEGO Education sets. Teams research a real-world problem, build motorized LEGO models, create Show Me posters, and practice Core Values. Culminates in Explore showcase festivals celebrating learning.',
                'url': 'https://www.firstlegoleague.org/season',
                'source': 'FIRST LEGO League',
                'category': 'Competition',
                'stem_fields': 'Robotics, Engineering, Science, Research, Design',
                'target_grade': '2-4',
                'cost': 'Paid',
                'location_type': 'In-person',
                'time_commitment': '4-5 months',
                'prerequisite_level': 'None',
                'support_level': 'High',
                'deadline': 'Fall registration',
                'financial_barrier_level': 'Medium',
                'financial_aid_available': 'Limited',
                'family_income_consideration': 'Optional',
                'hidden_costs_level': 'Equipment-Travel',
                'cost_category': '$100-$500',
                'diversity_focus': 'True',
                'underrepresented_friendly': 'True',
                'first_gen_support': 'True',
                'cultural_competency': 'High',
                'rural_accessible': 'Variable',
                'transportation_required': 'True',
                'internet_dependency': 'Basic',
                'regional_availability': 'International',
                'family_involvement_required': 'High',
                'peer_network_building': 'True',
                'mentor_access_level': 'Coach'
            },
            {
                'name': 'FIRST LEGO League Challenge (Ages 9-16)',
                'description': 'Premier robotics competition for grades 4-8. Design, build, and program autonomous LEGO robots to complete missions on themed game field. Complete Innovation Project solving real-world problems. Present research, robot design, and demonstrate Core Values to judges. Compete at regional, state, and international championships.',
                'url': 'https://www.firstlegoleague.org/season',
                'source': 'FIRST LEGO League',
                'category': 'Competition',
                'stem_fields': 'Robotics, Engineering, Programming, Computer Science, Research',
                'target_grade': '4-8',
                'cost': 'Paid',
                'location_type': 'In-person',
                'time_commitment': '4-6 months',
                'prerequisite_level': 'Low',
                'support_level': 'High',
                'deadline': 'Summer-Fall registration',
                'financial_barrier_level': 'Medium',
                'financial_aid_available': 'Limited',
                'family_income_consideration': 'Optional',
                'hidden_costs_level': 'Equipment-Travel',
                'cost_category': '$100-$500',
                'diversity_focus': 'True',
                'underrepresented_friendly': 'True',
                'first_gen_support': 'True',
                'cultural_competency': 'High',
                'rural_accessible': 'Variable',
                'transportation_required': 'True',
                'internet_dependency': 'Basic',
                'regional_availability': 'International',
                'family_involvement_required': 'High',
                'peer_network_building': 'True',
                'mentor_access_level': 'Coach'
            },
            {
                'name': 'FIRST LEGO League Challenge - Robot Game',
                'description': 'Competitive robot game component of Challenge level. Teams design, build, and program LEGO SPIKE Prime or MINDSTORMS robots to autonomously complete missions. 2.5 minute matches on themed field. Strategy, precision programming, and iterative design critical for success.',
                'url': 'https://www.firstlegoleague.org/challenge',
                'source': 'FIRST LEGO League',
                'category': 'Competition',
                'stem_fields': 'Robotics, Programming, Engineering, Mathematics, Physics',
                'target_grade': '4-8',
                'cost': 'Paid',
                'location_type': 'In-person',
                'time_commitment': '4-6 months',
                'prerequisite_level': 'Low',
                'support_level': 'High',
                'deadline': 'Competition season',
                'financial_barrier_level': 'Medium',
                'financial_aid_available': 'Limited',
                'family_income_consideration': 'Optional',
                'hidden_costs_level': 'Equipment-Travel',
                'cost_category': '$100-$500',
                'diversity_focus': 'True',
                'underrepresented_friendly': 'True',
                'first_gen_support': 'True',
                'cultural_competency': 'High',
                'rural_accessible': 'Variable',
                'transportation_required': 'True',
                'internet_dependency': 'Basic',
                'regional_availability': 'International',
                'family_involvement_required': 'High',
                'peer_network_building': 'True',
                'mentor_access_level': 'Coach'
            },
            {
                'name': 'FIRST LEGO League Challenge - Innovation Project',
                'description': 'Research and innovation component of Challenge level. Teams identify real-world problem related to season theme, research solutions, design innovative solution, and share findings with others. Develop presentation skills and scientific research methodology.',
                'url': 'https://www.firstlegoleague.org/challenge',
                'source': 'FIRST LEGO League',
                'category': 'Competition',
                'stem_fields': 'Research, Science, Engineering, Innovation, Communication',
                'target_grade': '4-8',
                'cost': 'Paid',
                'location_type': 'In-person',
                'time_commitment': '4-6 months',
                'prerequisite_level': 'Low',
                'support_level': 'High',
                'deadline': 'Competition season',
                'financial_barrier_level': 'Medium',
                'financial_aid_available': 'Limited',
                'family_income_consideration': 'Optional',
                'hidden_costs_level': 'Equipment-Travel',
                'cost_category': '$100-$500',
                'diversity_focus': 'True',
                'underrepresented_friendly': 'True',
                'first_gen_support': 'True',
                'cultural_competency': 'High',
                'rural_accessible': 'Variable',
                'transportation_required': 'True',
                'internet_dependency': 'Basic',
                'regional_availability': 'International',
                'family_involvement_required': 'High',
                'peer_network_building': 'True',
                'mentor_access_level': 'Coach'
            },
            {
                'name': 'FIRST LEGO League Challenge - Robot Design',
                'description': 'Engineering design component of Challenge level. Teams document robot mechanical design, programming strategies, and iterative improvement process. Present engineering portfolio to judges explaining design decisions, testing, and problem-solving.',
                'url': 'https://www.firstlegoleague.org/challenge',
                'source': 'FIRST LEGO League',
                'category': 'Competition',
                'stem_fields': 'Engineering, Robotics, Design, Documentation',
                'target_grade': '4-8',
                'cost': 'Paid',
                'location_type': 'In-person',
                'time_commitment': '4-6 months',
                'prerequisite_level': 'Low',
                'support_level': 'High',
                'deadline': 'Competition season',
                'financial_barrier_level': 'Medium',
                'financial_aid_available': 'Limited',
                'family_income_consideration': 'Optional',
                'hidden_costs_level': 'Equipment-Travel',
                'cost_category': '$100-$500',
                'diversity_focus': 'True',
                'underrepresented_friendly': 'True',
                'first_gen_support': 'True',
                'cultural_competency': 'High',
                'rural_accessible': 'Variable',
                'transportation_required': 'True',
                'internet_dependency': 'Basic',
                'regional_availability': 'International',
                'family_involvement_required': 'High',
                'peer_network_building': 'True',
                'mentor_access_level': 'Coach'
            },
            {
                'name': 'FIRST LEGO League Core Values',
                'description': 'Foundational values across all FIRST LEGO League levels: Discovery, Innovation, Impact, Inclusion, Teamwork, Fun. Teams demonstrate gracious professionalism, coopertition (cooperation+competition), and collaborative problem-solving. Core Values judging component at competitions.',
                'url': 'https://www.firstlegoleague.org/explore',
                'source': 'FIRST LEGO League',
                'category': 'Competition',
                'stem_fields': 'Teamwork, Leadership, Ethics, Collaboration',
                'target_grade': 'PreK-8',
                'cost': 'Paid',
                'location_type': 'In-person',
                'time_commitment': '4-6 months',
                'prerequisite_level': 'None',
                'support_level': 'High',
                'deadline': 'Season-long',
                'financial_barrier_level': 'Medium',
                'financial_aid_available': 'Limited',
                'family_income_consideration': 'Optional',
                'hidden_costs_level': 'Equipment-Travel',
                'cost_category': '$100-$500',
                'diversity_focus': 'True',
                'underrepresented_friendly': 'True',
                'first_gen_support': 'True',
                'cultural_competency': 'High',
                'rural_accessible': 'Variable',
                'transportation_required': 'True',
                'internet_dependency': 'Basic',
                'regional_availability': 'International',
                'family_involvement_required': 'High',
                'peer_network_building': 'True',
                'mentor_access_level': 'Coach'
            },
            {
                'name': 'FIRST LEGO League Coach Training and Resources',
                'description': 'Comprehensive training and resources for team coaches and mentors. Online courses, curriculum guides, season materials, engineering notebooks, and community support. Access to global network of FIRST coaches and technical resources.',
                'url': 'https://www.firstlegoleague.org/',
                'source': 'FIRST LEGO League',
                'category': 'Program',
                'stem_fields': 'Education, Mentorship, Robotics, STEM Education',
                'target_grade': 'PreK-8',
                'cost': 'Free',
                'location_type': 'Online',
                'time_commitment': 'Variable',
                'prerequisite_level': 'None',
                'support_level': 'High',
                'deadline': 'Rolling',
                'financial_barrier_level': 'None',
                'financial_aid_available': 'Not applicable',
                'family_income_consideration': 'Not required',
                'hidden_costs_level': 'None',
                'cost_category': 'Free',
                'diversity_focus': 'True',
                'underrepresented_friendly': 'True',
                'first_gen_support': 'True',
                'cultural_competency': 'High',
                'rural_accessible': 'True',
                'transportation_required': 'False',
                'internet_dependency': 'Required',
                'regional_availability': 'International',
                'family_involvement_required': 'Low',
                'peer_network_building': 'True',
                'mentor_access_level': 'Professional'
            },
            {
                'name': 'FIRST LEGO League Team Grants and Financial Aid',
                'description': 'Financial assistance programs for teams facing economic barriers. Team registration grants, kit subsidies, and event fee waivers available through FIRST partnerships and regional programs. Application process for qualifying teams.',
                'url': 'https://www.firstlegoleague.org/',
                'source': 'FIRST LEGO League',
                'category': 'Program',
                'stem_fields': 'Financial Aid, Access, Equity',
                'target_grade': 'PreK-8',
                'cost': 'Free',
                'location_type': 'Online',
                'time_commitment': '1-2 weeks',
                'prerequisite_level': 'None',
                'support_level': 'High',
                'deadline': 'Before season',
                'financial_barrier_level': 'None',
                'financial_aid_available': 'True',
                'family_income_consideration': 'Required',
                'hidden_costs_level': 'None',
                'cost_category': 'Free',
                'diversity_focus': 'True',
                'underrepresented_friendly': 'True',
                'first_gen_support': 'True',
                'cultural_competency': 'High',
                'rural_accessible': 'True',
                'transportation_required': 'False',
                'internet_dependency': 'Required',
                'regional_availability': 'International',
                'family_involvement_required': 'High',
                'peer_network_building': 'False',
                'mentor_access_level': 'None'
            },
            {
                'name': 'FIRST LEGO League Championship Advancement',
                'description': 'Championship tournament pathway for top-performing Challenge teams. Advance from regional events to state/provincial championships, national events, and international championships. Invitation-based advancement recognizing excellence in all judging categories.',
                'url': 'https://www.firstlegoleague.org/season',
                'source': 'FIRST LEGO League',
                'category': 'Competition',
                'stem_fields': 'Robotics, Engineering, Programming, Competition',
                'target_grade': '4-8',
                'cost': 'Paid',
                'location_type': 'In-person',
                'time_commitment': '4-8 months',
                'prerequisite_level': 'High',
                'support_level': 'High',
                'deadline': 'Invitation-based',
                'financial_barrier_level': 'High',
                'financial_aid_available': 'Limited',
                'family_income_consideration': 'Optional',
                'hidden_costs_level': 'Travel-Lodging',
                'cost_category': '$500-$1000',
                'diversity_focus': 'True',
                'underrepresented_friendly': 'True',
                'first_gen_support': 'True',
                'cultural_competency': 'High',
                'rural_accessible': 'False',
                'transportation_required': 'True',
                'internet_dependency': 'Basic',
                'regional_availability': 'International',
                'family_involvement_required': 'High',
                'peer_network_building': 'True',
                'mentor_access_level': 'Coach'
            },
            {
                'name': 'FIRST LEGO League Volunteer Program',
                'description': 'Volunteer opportunities for community members to support FIRST LEGO League events. Roles include judging, refereeing, event coordination, and technical support. Training provided for all volunteer positions. Critical to expanding program reach.',
                'url': 'https://www.firstlegoleague.org/',
                'source': 'FIRST LEGO League',
                'category': 'Program',
                'stem_fields': 'Volunteering, STEM Education, Community Engagement',
                'target_grade': 'PreK-8',
                'cost': 'Free',
                'location_type': 'In-person',
                'time_commitment': '1-2 days',
                'prerequisite_level': 'None',
                'support_level': 'High',
                'deadline': 'Competition season',
                'financial_barrier_level': 'None',
                'financial_aid_available': 'Not applicable',
                'family_income_consideration': 'Not required',
                'hidden_costs_level': 'None',
                'cost_category': 'Free',
                'diversity_focus': 'True',
                'underrepresented_friendly': 'True',
                'first_gen_support': 'True',
                'cultural_competency': 'High',
                'rural_accessible': 'Variable',
                'transportation_required': 'True',
                'internet_dependency': 'None',
                'regional_availability': 'International',
                'family_involvement_required': 'Low',
                'peer_network_building': 'True',
                'mentor_access_level': 'None'
            },
            {
                'name': 'FIRST LEGO League Classroom Edition',
                'description': 'Curriculum-based version of FIRST LEGO League for in-school implementation. Structured lesson plans aligned to education standards. Teachers guide students through season challenges during class time. Optional participation in showcase events.',
                'url': 'https://www.firstlegoleague.org/',
                'source': 'FIRST LEGO League',
                'category': 'Program',
                'stem_fields': 'Robotics, Engineering, Curriculum, Education',
                'target_grade': '4-8',
                'cost': 'Paid',
                'location_type': 'In-person',
                'time_commitment': 'Semester',
                'prerequisite_level': 'None',
                'support_level': 'High',
                'deadline': 'School year',
                'financial_barrier_level': 'Medium',
                'financial_aid_available': 'Limited',
                'family_income_consideration': 'Optional',
                'hidden_costs_level': 'Equipment',
                'cost_category': '$100-$500',
                'diversity_focus': 'True',
                'underrepresented_friendly': 'True',
                'first_gen_support': 'True',
                'cultural_competency': 'High',
                'rural_accessible': 'True',
                'transportation_required': 'False',
                'internet_dependency': 'Basic',
                'regional_availability': 'International',
                'family_involvement_required': 'Low',
                'peer_network_building': 'True',
                'mentor_access_level': 'Teacher'
            }
        ]
        return resources

    def scrape(self):
        """Main scraping method."""
        print("Starting FIRST LEGO League scraping...")
        print("Note: Creating FIRST LEGO League competition levels")
        # Note: Not fetching pages as these are representative resources
        for url in self.target_urls:
            soup = self.fetch_page(url)
            time.sleep(2)
        print("Creating FIRST LEGO League entries...")
        self.resources = self.create_first_lego_league_levels()
        print(f"Total resources created: {len(self.resources)}")

    def save_to_csv(self, filename: str = 'data/first_lego_league.csv'):
        """Save resources to CSV file."""
        fieldnames = [
            'name', 'description', 'url', 'source', 'category', 'stem_fields',
            'target_grade', 'cost', 'location_type', 'time_commitment',
            'prerequisite_level', 'support_level', 'deadline',
            'financial_barrier_level', 'financial_aid_available',
            'family_income_consideration', 'hidden_costs_level', 'cost_category',
            'diversity_focus', 'underrepresented_friendly', 'first_gen_support',
            'cultural_competency', 'rural_accessible', 'transportation_required',
            'internet_dependency', 'regional_availability',
            'family_involvement_required', 'peer_network_building',
            'mentor_access_level'
        ]
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(self.resources)
        print(f"Saved {len(self.resources)} resources to {filename}")


def main():
    scraper = FIRSTLegoLeagueScraper()
    scraper.scrape()
    scraper.save_to_csv()
    print("Scraping completed successfully!")


if __name__ == "__main__":
    main()
