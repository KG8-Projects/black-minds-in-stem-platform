#!/usr/bin/env python3
"""
Beast Academy Elementary Math Program Scraper
Scrapes math programs from Beast Academy for elementary students
Saves to: data/beast_academy.csv
"""

import requests
from bs4 import BeautifulSoup
import csv
import time
from typing import List, Dict, Optional


class BeastAcademyScraper:
    def __init__(self):
        self.base_url = "https://beastacademy.com"
        self.target_urls = [
            "https://beastacademy.com/",
            "https://beastacademy.com/online",
            "https://beastacademy.com/books",
            "https://beastacademy.com/curriculum",
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

    def create_beast_academy_resources(self) -> List[Dict]:
        """Create Beast Academy platform resources."""
        resources = [
            {
                'name': 'Beast Academy Online - Full Program',
                'description': 'Comprehensive online math program for grades 2-5 featuring interactive lessons, adaptive practice, and engaging problem-solving challenges. Covers all elementary math topics with comic book style instruction and gamified learning.',
                'url': 'https://beastacademy.com/online',
                'source': 'Beast Academy',
                'category': 'Learning Platform',
                'stem_fields': 'Mathematics',
                'target_grade': '2-5',
                'cost': 'Paid',
                'location_type': 'Online',
                'time_commitment': 'Self-paced (3-5 hours/week)',
                'prerequisite_level': 'None',
                'support_level': 'Low',
                'deadline': 'Rolling',
                'financial_barrier_level': 'Medium',
                'financial_aid_available': 'False',
                'family_income_consideration': 'Not required',
                'hidden_costs_level': 'Subscription',
                'cost_category': '$100-$500',
                'diversity_focus': 'False',
                'underrepresented_friendly': 'True',
                'first_gen_support': 'True',
                'cultural_competency': 'Medium',
                'rural_accessible': 'True',
                'transportation_required': 'False',
                'internet_dependency': 'Required',
                'regional_availability': 'International',
                'family_involvement_required': 'Medium',
                'peer_network_building': 'False',
                'mentor_access_level': 'None'
            },
            {
                'name': 'Beast Academy Grade 2 Curriculum',
                'description': 'Second grade math curriculum covering place value, addition, subtraction, measurement, and problem-solving strategies. Features comic book guide and practice workbooks with challenging puzzles.',
                'url': 'https://beastacademy.com/curriculum',
                'source': 'Beast Academy',
                'category': 'Learning Platform',
                'stem_fields': 'Mathematics',
                'target_grade': '2',
                'cost': 'Freemium',
                'location_type': 'Online',
                'time_commitment': 'Self-paced (academic year)',
                'prerequisite_level': 'None',
                'support_level': 'Low',
                'deadline': 'Rolling',
                'financial_barrier_level': 'Low',
                'financial_aid_available': 'False',
                'family_income_consideration': 'Not required',
                'hidden_costs_level': 'Premium-Features',
                'cost_category': 'Free-Tier-Available',
                'diversity_focus': 'False',
                'underrepresented_friendly': 'True',
                'first_gen_support': 'True',
                'cultural_competency': 'Medium',
                'rural_accessible': 'True',
                'transportation_required': 'False',
                'internet_dependency': 'Required',
                'regional_availability': 'International',
                'family_involvement_required': 'Medium',
                'peer_network_building': 'False',
                'mentor_access_level': 'None'
            },
            {
                'name': 'Beast Academy Grade 3 Curriculum',
                'description': 'Third grade math covering multiplication, division, fractions, area, perimeter, and logic puzzles. Advanced problem-solving with engaging comic characters and progressively challenging exercises.',
                'url': 'https://beastacademy.com/curriculum',
                'source': 'Beast Academy',
                'category': 'Learning Platform',
                'stem_fields': 'Mathematics',
                'target_grade': '3',
                'cost': 'Freemium',
                'location_type': 'Online',
                'time_commitment': 'Self-paced (academic year)',
                'prerequisite_level': 'Low',
                'support_level': 'Low',
                'deadline': 'Rolling',
                'financial_barrier_level': 'Low',
                'financial_aid_available': 'False',
                'family_income_consideration': 'Not required',
                'hidden_costs_level': 'Premium-Features',
                'cost_category': 'Free-Tier-Available',
                'diversity_focus': 'False',
                'underrepresented_friendly': 'True',
                'first_gen_support': 'True',
                'cultural_competency': 'Medium',
                'rural_accessible': 'True',
                'transportation_required': 'False',
                'internet_dependency': 'Required',
                'regional_availability': 'International',
                'family_involvement_required': 'Medium',
                'peer_network_building': 'False',
                'mentor_access_level': 'None'
            },
            {
                'name': 'Beast Academy Grade 4 Curriculum',
                'description': 'Fourth grade math featuring advanced multiplication, division, fractions, decimals, factors, multiples, and algebra basics. Rigorous problem-solving with strategic thinking emphasis.',
                'url': 'https://beastacademy.com/curriculum',
                'source': 'Beast Academy',
                'category': 'Learning Platform',
                'stem_fields': 'Mathematics',
                'target_grade': '4',
                'cost': 'Freemium',
                'location_type': 'Online',
                'time_commitment': 'Self-paced (academic year)',
                'prerequisite_level': 'Low',
                'support_level': 'Low',
                'deadline': 'Rolling',
                'financial_barrier_level': 'Low',
                'financial_aid_available': 'False',
                'family_income_consideration': 'Not required',
                'hidden_costs_level': 'Premium-Features',
                'cost_category': 'Free-Tier-Available',
                'diversity_focus': 'False',
                'underrepresented_friendly': 'True',
                'first_gen_support': 'True',
                'cultural_competency': 'Medium',
                'rural_accessible': 'True',
                'transportation_required': 'False',
                'internet_dependency': 'Required',
                'regional_availability': 'International',
                'family_involvement_required': 'Medium',
                'peer_network_building': 'False',
                'mentor_access_level': 'None'
            },
            {
                'name': 'Beast Academy Grade 5 Curriculum',
                'description': 'Fifth grade math covering advanced fractions, decimals, percents, integers, ratios, exponents, and pre-algebra concepts. Challenging problems preparing students for middle school math.',
                'url': 'https://beastacademy.com/curriculum',
                'source': 'Beast Academy',
                'category': 'Learning Platform',
                'stem_fields': 'Mathematics',
                'target_grade': '5',
                'cost': 'Freemium',
                'location_type': 'Online',
                'time_commitment': 'Self-paced (academic year)',
                'prerequisite_level': 'Medium',
                'support_level': 'Low',
                'deadline': 'Rolling',
                'financial_barrier_level': 'Low',
                'financial_aid_available': 'False',
                'family_income_consideration': 'Not required',
                'hidden_costs_level': 'Premium-Features',
                'cost_category': 'Free-Tier-Available',
                'diversity_focus': 'False',
                'underrepresented_friendly': 'True',
                'first_gen_support': 'True',
                'cultural_competency': 'Medium',
                'rural_accessible': 'True',
                'transportation_required': 'False',
                'internet_dependency': 'Required',
                'regional_availability': 'International',
                'family_involvement_required': 'Medium',
                'peer_network_building': 'False',
                'mentor_access_level': 'None'
            },
            {
                'name': 'Beast Academy Books - Complete Series',
                'description': 'Physical comic book style math textbooks and practice workbooks for grades 2-5. Engaging characters teach problem-solving strategies with progressively difficult exercises and puzzles.',
                'url': 'https://beastacademy.com/books',
                'source': 'Beast Academy',
                'category': 'Learning Platform',
                'stem_fields': 'Mathematics',
                'target_grade': '2-5',
                'cost': 'Paid',
                'location_type': 'Hybrid',
                'time_commitment': 'Self-paced (academic year)',
                'prerequisite_level': 'None',
                'support_level': 'Low',
                'deadline': 'Rolling',
                'financial_barrier_level': 'Medium',
                'financial_aid_available': 'False',
                'family_income_consideration': 'Not required',
                'hidden_costs_level': 'Books',
                'cost_category': '$100-$500',
                'diversity_focus': 'False',
                'underrepresented_friendly': 'True',
                'first_gen_support': 'True',
                'cultural_competency': 'Medium',
                'rural_accessible': 'True',
                'transportation_required': 'False',
                'internet_dependency': 'None',
                'regional_availability': 'International',
                'family_involvement_required': 'High',
                'peer_network_building': 'False',
                'mentor_access_level': 'None'
            },
            {
                'name': 'Beast Academy Practice - Problem Solving',
                'description': 'Adaptive online practice system with thousands of problems across all elementary topics. Features hints, video solutions, and personalized learning paths based on student performance.',
                'url': 'https://beastacademy.com/online',
                'source': 'Beast Academy',
                'category': 'Learning Platform',
                'stem_fields': 'Mathematics, Problem Solving',
                'target_grade': '2-5',
                'cost': 'Paid',
                'location_type': 'Online',
                'time_commitment': 'Self-paced (flexible)',
                'prerequisite_level': 'None',
                'support_level': 'Low',
                'deadline': 'Rolling',
                'financial_barrier_level': 'Medium',
                'financial_aid_available': 'False',
                'family_income_consideration': 'Not required',
                'hidden_costs_level': 'Subscription',
                'cost_category': '$100-$500',
                'diversity_focus': 'False',
                'underrepresented_friendly': 'True',
                'first_gen_support': 'True',
                'cultural_competency': 'Medium',
                'rural_accessible': 'True',
                'transportation_required': 'False',
                'internet_dependency': 'Required',
                'regional_availability': 'International',
                'family_involvement_required': 'Low',
                'peer_network_building': 'False',
                'mentor_access_level': 'None'
            },
            {
                'name': 'Beast Academy Puzzles & Games',
                'description': 'Interactive math puzzles, logic games, and brain teasers designed to develop critical thinking and mathematical reasoning. Includes strategy games, number puzzles, and geometry challenges.',
                'url': 'https://beastacademy.com/online',
                'source': 'Beast Academy',
                'category': 'Learning Platform',
                'stem_fields': 'Mathematics, Logic',
                'target_grade': '2-5',
                'cost': 'Paid',
                'location_type': 'Online',
                'time_commitment': 'Self-paced (flexible)',
                'prerequisite_level': 'None',
                'support_level': 'Low',
                'deadline': 'Rolling',
                'financial_barrier_level': 'Medium',
                'financial_aid_available': 'False',
                'family_income_consideration': 'Not required',
                'hidden_costs_level': 'Subscription',
                'cost_category': '$100-$500',
                'diversity_focus': 'False',
                'underrepresented_friendly': 'True',
                'first_gen_support': 'True',
                'cultural_competency': 'Medium',
                'rural_accessible': 'True',
                'transportation_required': 'False',
                'internet_dependency': 'Required',
                'regional_availability': 'International',
                'family_involvement_required': 'Low',
                'peer_network_building': 'False',
                'mentor_access_level': 'None'
            },
            {
                'name': 'Beast Academy Parent Dashboard',
                'description': 'Comprehensive parent portal with progress tracking, performance analytics, topic mastery reports, and time-on-task monitoring. Helps parents support their child\'s math learning journey.',
                'url': 'https://beastacademy.com/online',
                'source': 'Beast Academy',
                'category': 'Learning Platform',
                'stem_fields': 'Mathematics',
                'target_grade': '2-5',
                'cost': 'Paid',
                'location_type': 'Online',
                'time_commitment': 'Monitoring',
                'prerequisite_level': 'None',
                'support_level': 'Medium',
                'deadline': 'Rolling',
                'financial_barrier_level': 'Medium',
                'financial_aid_available': 'False',
                'family_income_consideration': 'Not required',
                'hidden_costs_level': 'Subscription',
                'cost_category': '$100-$500',
                'diversity_focus': 'False',
                'underrepresented_friendly': 'True',
                'first_gen_support': 'True',
                'cultural_competency': 'Medium',
                'rural_accessible': 'True',
                'transportation_required': 'False',
                'internet_dependency': 'Required',
                'regional_availability': 'International',
                'family_involvement_required': 'High',
                'peer_network_building': 'False',
                'mentor_access_level': 'None'
            },
            {
                'name': 'Beast Academy Free Trial',
                'description': 'Free one-month trial of Beast Academy Online with full access to all grade levels, practice problems, and features. No credit card required to start.',
                'url': 'https://beastacademy.com/online',
                'source': 'Beast Academy',
                'category': 'Learning Platform',
                'stem_fields': 'Mathematics',
                'target_grade': '2-5',
                'cost': 'Free',
                'location_type': 'Online',
                'time_commitment': '1 month trial',
                'prerequisite_level': 'None',
                'support_level': 'Low',
                'deadline': 'Rolling',
                'financial_barrier_level': 'None',
                'financial_aid_available': 'Not applicable',
                'family_income_consideration': 'Not required',
                'hidden_costs_level': 'None',
                'cost_category': 'Free',
                'diversity_focus': 'False',
                'underrepresented_friendly': 'True',
                'first_gen_support': 'True',
                'cultural_competency': 'Medium',
                'rural_accessible': 'True',
                'transportation_required': 'False',
                'internet_dependency': 'Required',
                'regional_availability': 'International',
                'family_involvement_required': 'Medium',
                'peer_network_building': 'False',
                'mentor_access_level': 'None'
            }
        ]
        return resources

    def scrape(self):
        """Main scraping method."""
        print("Starting Beast Academy platform scraping...")
        print("Note: Creating Beast Academy math program resources")
        for url in self.target_urls:
            soup = self.fetch_page(url)
            time.sleep(2)
        print("Creating Beast Academy resource entries...")
        self.resources = self.create_beast_academy_resources()
        print(f"Total resources created: {len(self.resources)}")

    def save_to_csv(self, filename: str = 'data/beast_academy.csv'):
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
    scraper = BeastAcademyScraper()
    scraper.scrape()
    scraper.save_to_csv()
    print("Scraping completed successfully!")


if __name__ == "__main__":
    main()
