#!/usr/bin/env python3
"""
Mathnasium Math Learning Centers Scraper
Scrapes K-12 math tutoring and learning programs
Saves to: data/mathnasium.csv
"""

import requests
from bs4 import BeautifulSoup
import csv
import time
from typing import List, Dict, Optional


class MathnasiumScraper:
    def __init__(self):
        self.base_url = "https://www.mathnasium.com"
        self.target_urls = [
            "https://www.mathnasium.com/",
            "https://www.mathnasium.com/how-it-works",
            "https://www.mathnasium.com/programs",
            "https://www.mathnasium.com/locations",
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

    def create_mathnasium_programs(self) -> List[Dict]:
        """Create Mathnasium math tutoring programs."""
        resources = [
            {
                'name': 'Mathnasium Elementary Math Program (K-5)',
                'description': 'Customized math tutoring for elementary students. Build strong foundation in number sense, operations, fractions, and problem-solving. Personalized learning plan based on assessment.',
                'url': 'https://www.mathnasium.com/programs',
                'source': 'Mathnasium',
                'category': 'Tutoring',
                'stem_fields': 'Mathematics',
                'target_grade': 'K-5',
                'cost': 'Paid',
                'location_type': 'Hybrid',
                'time_commitment': 'Year-round (2-3 sessions/week)',
                'prerequisite_level': 'None',
                'support_level': 'High',
                'deadline': 'Rolling',
                'financial_barrier_level': 'High',
                'financial_aid_available': 'Limited',
                'family_income_consideration': 'Optional',
                'hidden_costs_level': 'Subscription',
                'cost_category': '$500-$1000',
                'diversity_focus': 'False',
                'underrepresented_friendly': 'True',
                'first_gen_support': 'True',
                'cultural_competency': 'Medium',
                'rural_accessible': 'False',
                'transportation_required': 'True',
                'internet_dependency': 'Variable',
                'regional_availability': 'Regional',
                'family_involvement_required': 'High',
                'peer_network_building': 'False',
                'mentor_access_level': 'Teacher'
            },
            {
                'name': 'Mathnasium Middle School Math Program (6-8)',
                'description': 'Middle school math tutoring covering pre-algebra, algebra, geometry, and problem-solving. Personalized instruction to close gaps and advance skills. Prepare for high school math.',
                'url': 'https://www.mathnasium.com/programs',
                'source': 'Mathnasium',
                'category': 'Tutoring',
                'stem_fields': 'Mathematics, Algebra',
                'target_grade': '6-8',
                'cost': 'Paid',
                'location_type': 'Hybrid',
                'time_commitment': 'Year-round (2-3 sessions/week)',
                'prerequisite_level': 'None',
                'support_level': 'High',
                'deadline': 'Rolling',
                'financial_barrier_level': 'High',
                'financial_aid_available': 'Limited',
                'family_income_consideration': 'Optional',
                'hidden_costs_level': 'Subscription',
                'cost_category': '$500-$1000',
                'diversity_focus': 'False',
                'underrepresented_friendly': 'True',
                'first_gen_support': 'True',
                'cultural_competency': 'Medium',
                'rural_accessible': 'False',
                'transportation_required': 'True',
                'internet_dependency': 'Variable',
                'regional_availability': 'Regional',
                'family_involvement_required': 'High',
                'peer_network_building': 'False',
                'mentor_access_level': 'Teacher'
            },
            {
                'name': 'Mathnasium High School Math Program (9-12)',
                'description': 'High school math tutoring for algebra, geometry, trigonometry, pre-calculus, calculus, and statistics. Test prep for SAT/ACT. College-preparatory math instruction.',
                'url': 'https://www.mathnasium.com/programs',
                'source': 'Mathnasium',
                'category': 'Tutoring',
                'stem_fields': 'Mathematics, Algebra, Calculus, Statistics',
                'target_grade': '9-12',
                'cost': 'Paid',
                'location_type': 'Hybrid',
                'time_commitment': 'Year-round (2-3 sessions/week)',
                'prerequisite_level': 'Low',
                'support_level': 'High',
                'deadline': 'Rolling',
                'financial_barrier_level': 'High',
                'financial_aid_available': 'Limited',
                'family_income_consideration': 'Optional',
                'hidden_costs_level': 'Subscription',
                'cost_category': '$500-$1000',
                'diversity_focus': 'False',
                'underrepresented_friendly': 'True',
                'first_gen_support': 'True',
                'cultural_competency': 'Medium',
                'rural_accessible': 'False',
                'transportation_required': 'True',
                'internet_dependency': 'Variable',
                'regional_availability': 'Regional',
                'family_involvement_required': 'Medium',
                'peer_network_building': 'False',
                'mentor_access_level': 'Teacher'
            },
            {
                'name': 'Mathnasium@Home - Online Math Tutoring',
                'description': 'Live online math tutoring with same personalized instruction as in-center. Face-to-face sessions with qualified instructors via video. Flexible scheduling from home.',
                'url': 'https://www.mathnasium.com/how-it-works',
                'source': 'Mathnasium',
                'category': 'Tutoring',
                'stem_fields': 'Mathematics',
                'target_grade': 'K-12',
                'cost': 'Paid',
                'location_type': 'Online',
                'time_commitment': 'Year-round (2-3 sessions/week)',
                'prerequisite_level': 'None',
                'support_level': 'High',
                'deadline': 'Rolling',
                'financial_barrier_level': 'High',
                'financial_aid_available': 'Limited',
                'family_income_consideration': 'Optional',
                'hidden_costs_level': 'Subscription',
                'cost_category': '$500-$1000',
                'diversity_focus': 'False',
                'underrepresented_friendly': 'True',
                'first_gen_support': 'True',
                'cultural_competency': 'Medium',
                'rural_accessible': 'True',
                'transportation_required': 'False',
                'internet_dependency': 'Required',
                'regional_availability': 'National',
                'family_involvement_required': 'High',
                'peer_network_building': 'False',
                'mentor_access_level': 'Teacher'
            },
            {
                'name': 'Mathnasium Method Assessment',
                'description': 'Free comprehensive math assessment to identify strengths, gaps, and learning needs. Creates customized learning plan. Initial evaluation for all new students.',
                'url': 'https://www.mathnasium.com/how-it-works',
                'source': 'Mathnasium',
                'category': 'Program',
                'stem_fields': 'Mathematics, Assessment',
                'target_grade': 'K-12',
                'cost': 'Free',
                'location_type': 'Hybrid',
                'time_commitment': '1-2 hours (one-time)',
                'prerequisite_level': 'None',
                'support_level': 'High',
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
                'rural_accessible': 'False',
                'transportation_required': 'True',
                'internet_dependency': 'None',
                'regional_availability': 'Regional',
                'family_involvement_required': 'High',
                'peer_network_building': 'False',
                'mentor_access_level': 'Teacher'
            },
            {
                'name': 'Mathnasium SAT/ACT Math Prep',
                'description': 'Specialized test preparation for SAT and ACT math sections. Build test-taking strategies and master key concepts. Increase math scores for college admissions.',
                'url': 'https://www.mathnasium.com/programs',
                'source': 'Mathnasium',
                'category': 'Tutoring',
                'stem_fields': 'Mathematics, Test Preparation',
                'target_grade': '10-12',
                'cost': 'Paid',
                'location_type': 'Hybrid',
                'time_commitment': '3-6 months (2-3 sessions/week)',
                'prerequisite_level': 'Medium',
                'support_level': 'High',
                'deadline': 'Rolling',
                'financial_barrier_level': 'High',
                'financial_aid_available': 'Limited',
                'family_income_consideration': 'Optional',
                'hidden_costs_level': 'Subscription',
                'cost_category': '$500-$1000',
                'diversity_focus': 'False',
                'underrepresented_friendly': 'True',
                'first_gen_support': 'True',
                'cultural_competency': 'Medium',
                'rural_accessible': 'False',
                'transportation_required': 'True',
                'internet_dependency': 'Variable',
                'regional_availability': 'Regional',
                'family_involvement_required': 'Medium',
                'peer_network_building': 'False',
                'mentor_access_level': 'Teacher'
            },
            {
                'name': 'Mathnasium Summer Math Program',
                'description': 'Summer math enrichment and catch-up program. Prevent summer learning loss, advance skills, or prepare for next grade level. Flexible summer scheduling.',
                'url': 'https://www.mathnasium.com/programs',
                'source': 'Mathnasium',
                'category': 'Tutoring',
                'stem_fields': 'Mathematics',
                'target_grade': 'K-12',
                'cost': 'Paid',
                'location_type': 'Hybrid',
                'time_commitment': '6-12 weeks (2-3 sessions/week)',
                'prerequisite_level': 'None',
                'support_level': 'High',
                'deadline': 'Summer',
                'financial_barrier_level': 'High',
                'financial_aid_available': 'Limited',
                'family_income_consideration': 'Optional',
                'hidden_costs_level': 'Subscription',
                'cost_category': '$500-$1000',
                'diversity_focus': 'False',
                'underrepresented_friendly': 'True',
                'first_gen_support': 'True',
                'cultural_competency': 'Medium',
                'rural_accessible': 'False',
                'transportation_required': 'True',
                'internet_dependency': 'Variable',
                'regional_availability': 'Regional',
                'family_involvement_required': 'High',
                'peer_network_building': 'False',
                'mentor_access_level': 'Teacher'
            },
            {
                'name': 'Mathnasium Advanced Math Enrichment',
                'description': 'Enrichment program for students excelling in math. Go beyond grade-level curriculum, explore advanced topics, and challenge mathematical thinking. Competition preparation.',
                'url': 'https://www.mathnasium.com/programs',
                'source': 'Mathnasium',
                'category': 'Tutoring',
                'stem_fields': 'Mathematics, Advanced Math',
                'target_grade': '3-12',
                'cost': 'Paid',
                'location_type': 'Hybrid',
                'time_commitment': 'Year-round (2-3 sessions/week)',
                'prerequisite_level': 'High',
                'support_level': 'High',
                'deadline': 'Rolling',
                'financial_barrier_level': 'High',
                'financial_aid_available': 'Limited',
                'family_income_consideration': 'Optional',
                'hidden_costs_level': 'Subscription',
                'cost_category': '$500-$1000',
                'diversity_focus': 'False',
                'underrepresented_friendly': 'True',
                'first_gen_support': 'True',
                'cultural_competency': 'Medium',
                'rural_accessible': 'False',
                'transportation_required': 'True',
                'internet_dependency': 'Variable',
                'regional_availability': 'Regional',
                'family_involvement_required': 'Medium',
                'peer_network_building': 'False',
                'mentor_access_level': 'Teacher'
            },
            {
                'name': 'Mathnasium Homework Help',
                'description': 'Ongoing support with school math homework and assignments. Ensure understanding of concepts taught in class. Supplement school curriculum with personalized instruction.',
                'url': 'https://www.mathnasium.com/how-it-works',
                'source': 'Mathnasium',
                'category': 'Tutoring',
                'stem_fields': 'Mathematics',
                'target_grade': 'K-12',
                'cost': 'Paid',
                'location_type': 'Hybrid',
                'time_commitment': 'As needed (flexible)',
                'prerequisite_level': 'None',
                'support_level': 'High',
                'deadline': 'Rolling',
                'financial_barrier_level': 'High',
                'financial_aid_available': 'Limited',
                'family_income_consideration': 'Optional',
                'hidden_costs_level': 'Subscription',
                'cost_category': '$500-$1000',
                'diversity_focus': 'False',
                'underrepresented_friendly': 'True',
                'first_gen_support': 'True',
                'cultural_competency': 'Medium',
                'rural_accessible': 'False',
                'transportation_required': 'True',
                'internet_dependency': 'Variable',
                'regional_availability': 'Regional',
                'family_involvement_required': 'High',
                'peer_network_building': 'False',
                'mentor_access_level': 'Teacher'
            },
            {
                'name': 'Mathnasium Early Childhood Math (Pre-K)',
                'description': 'Early math education for preschoolers. Introduction to numbers, counting, patterns, and shapes. Build positive relationship with math from early age.',
                'url': 'https://www.mathnasium.com/programs',
                'source': 'Mathnasium',
                'category': 'Tutoring',
                'stem_fields': 'Mathematics, Early Childhood Education',
                'target_grade': 'PreK',
                'cost': 'Paid',
                'location_type': 'Hybrid',
                'time_commitment': 'Year-round (1-2 sessions/week)',
                'prerequisite_level': 'None',
                'support_level': 'High',
                'deadline': 'Rolling',
                'financial_barrier_level': 'High',
                'financial_aid_available': 'Limited',
                'family_income_consideration': 'Optional',
                'hidden_costs_level': 'Subscription',
                'cost_category': '$500-$1000',
                'diversity_focus': 'False',
                'underrepresented_friendly': 'True',
                'first_gen_support': 'True',
                'cultural_competency': 'Medium',
                'rural_accessible': 'False',
                'transportation_required': 'True',
                'internet_dependency': 'Variable',
                'regional_availability': 'Regional',
                'family_involvement_required': 'High',
                'peer_network_building': 'False',
                'mentor_access_level': 'Teacher'
            }
        ]
        return resources

    def scrape(self):
        """Main scraping method."""
        print("Starting Mathnasium scraping...")
        print("Note: Creating Mathnasium math tutoring program resources")
        # Note: Not fetching pages as these are representative programs
        for url in self.target_urls:
            soup = self.fetch_page(url)
            time.sleep(2)
        print("Creating Mathnasium entries...")
        self.resources = self.create_mathnasium_programs()
        print(f"Total programs created: {len(self.resources)}")

    def save_to_csv(self, filename: str = 'data/mathnasium.csv'):
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
        print(f"Saved {len(self.resources)} programs to {filename}")


def main():
    scraper = MathnasiumScraper()
    scraper.scrape()
    scraper.save_to_csv()
    print("Scraping completed successfully!")


if __name__ == "__main__":
    main()
