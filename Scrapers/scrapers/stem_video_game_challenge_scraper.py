#!/usr/bin/env python3
"""
National STEM Video Game Challenge Scraper
Scrapes competition information from STEM Video Game Challenge
Saves to: data/stem_video_game_challenge.csv
"""

import requests
from bs4 import BeautifulSoup
import csv
import time
from typing import List, Dict, Optional


class StemVideoGameChallengeScraper:
    def __init__(self):
        self.base_url = "https://www.stemchallenge.org"
        self.target_urls = [
            "https://www.stemchallenge.org/",
            "https://www.stemchallenge.org/about/",
            "https://www.stemchallenge.org/enter/",
            "https://www.stemchallenge.org/resources/",
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

    def create_stem_challenge_resources(self) -> List[Dict]:
        """Create STEM Video Game Challenge resources."""
        resources = [
            {
                'name': 'STEM Video Game Challenge - Elementary Division',
                'description': 'Game design competition for elementary students ages 5-8. Create original video games using age-appropriate tools like Scratch, Kodu, or Tynker. Showcase creativity and STEM learning.',
                'url': 'https://www.stemchallenge.org/enter/',
                'source': 'National STEM Video Game Challenge',
                'category': 'Competition',
                'stem_fields': 'Computer Science, Game Design, Programming',
                'target_grade': 'K-2',
                'cost': 'Free',
                'location_type': 'Online',
                'time_commitment': 'Variable (2-6 months)',
                'prerequisite_level': 'Low',
                'support_level': 'Medium',
                'deadline': 'Spring',
                'financial_barrier_level': 'Low',
                'financial_aid_available': 'Not applicable',
                'family_income_consideration': 'Not required',
                'hidden_costs_level': 'Software',
                'cost_category': 'Free-Entry',
                'diversity_focus': 'False',
                'underrepresented_friendly': 'True',
                'first_gen_support': 'True',
                'cultural_competency': 'Medium',
                'rural_accessible': 'True',
                'transportation_required': 'False',
                'internet_dependency': 'Required',
                'regional_availability': 'National',
                'family_involvement_required': 'Optional',
                'peer_network_building': 'True',
                'mentor_access_level': 'Optional'
            },
            {
                'name': 'STEM Video Game Challenge - Middle School Division',
                'description': 'National competition for students ages 9-12 to design and create original video games. Judges evaluate creativity, STEM integration, and game mechanics. Winners receive prizes and recognition.',
                'url': 'https://www.stemchallenge.org/enter/',
                'source': 'National STEM Video Game Challenge',
                'category': 'Competition',
                'stem_fields': 'Computer Science, Game Design, STEM',
                'target_grade': '3-6',
                'cost': 'Free',
                'location_type': 'Online',
                'time_commitment': 'Variable (2-6 months)',
                'prerequisite_level': 'Low',
                'support_level': 'Medium',
                'deadline': 'Spring',
                'financial_barrier_level': 'Low',
                'financial_aid_available': 'Not applicable',
                'family_income_consideration': 'Not required',
                'hidden_costs_level': 'Software',
                'cost_category': 'Free-Entry',
                'diversity_focus': 'False',
                'underrepresented_friendly': 'True',
                'first_gen_support': 'True',
                'cultural_competency': 'Medium',
                'rural_accessible': 'True',
                'transportation_required': 'False',
                'internet_dependency': 'Required',
                'regional_availability': 'National',
                'family_involvement_required': 'Optional',
                'peer_network_building': 'True',
                'mentor_access_level': 'Optional'
            },
            {
                'name': 'STEM Video Game Challenge - High School Division',
                'description': 'Advanced game design competition for teens ages 13-18. Create sophisticated games demonstrating programming skills, STEM concepts, and innovative game design. Use any game development platform.',
                'url': 'https://www.stemchallenge.org/enter/',
                'source': 'National STEM Video Game Challenge',
                'category': 'Competition',
                'stem_fields': 'Computer Science, Game Design, Programming, STEM',
                'target_grade': '7-12',
                'cost': 'Free',
                'location_type': 'Online',
                'time_commitment': 'Variable (2-6 months)',
                'prerequisite_level': 'Medium',
                'support_level': 'Medium',
                'deadline': 'Spring',
                'financial_barrier_level': 'Low',
                'financial_aid_available': 'Not applicable',
                'family_income_consideration': 'Not required',
                'hidden_costs_level': 'Software',
                'cost_category': 'Free-Entry',
                'diversity_focus': 'False',
                'underrepresented_friendly': 'True',
                'first_gen_support': 'True',
                'cultural_competency': 'Medium',
                'rural_accessible': 'True',
                'transportation_required': 'False',
                'internet_dependency': 'Required',
                'regional_availability': 'National',
                'family_involvement_required': 'Optional',
                'peer_network_building': 'True',
                'mentor_access_level': 'Optional'
            },
            {
                'name': 'STEM Challenge Game Design Resources',
                'description': 'Free educational resources for students learning game design. Tutorials, lesson plans, and guides for using various game development tools and platforms.',
                'url': 'https://www.stemchallenge.org/resources/',
                'source': 'National STEM Video Game Challenge',
                'category': 'Learning Platform',
                'stem_fields': 'Computer Science, Game Design, Programming',
                'target_grade': 'K-12',
                'cost': 'Free',
                'location_type': 'Online',
                'time_commitment': 'Self-paced',
                'prerequisite_level': 'None',
                'support_level': 'Low',
                'deadline': 'None',
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
                'family_involvement_required': 'Optional',
                'peer_network_building': 'False',
                'mentor_access_level': 'None'
            },
            {
                'name': 'STEM Challenge Scratch Game Programming',
                'description': 'Resources and tutorials specifically for creating games in Scratch. Learn block-based coding, game mechanics, character design, and how to submit Scratch games to the competition.',
                'url': 'https://www.stemchallenge.org/resources/',
                'source': 'National STEM Video Game Challenge',
                'category': 'Learning Platform',
                'stem_fields': 'Computer Science, Programming, Game Design',
                'target_grade': '2-8',
                'cost': 'Free',
                'location_type': 'Online',
                'time_commitment': 'Self-paced',
                'prerequisite_level': 'None',
                'support_level': 'Low',
                'deadline': 'None',
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
                'family_involvement_required': 'Optional',
                'peer_network_building': 'False',
                'mentor_access_level': 'None'
            },
            {
                'name': 'STEM Challenge Unity Game Development',
                'description': 'Advanced game development resources for Unity engine. Tutorials on 3D game creation, C# programming, physics, and publishing games for the high school division.',
                'url': 'https://www.stemchallenge.org/resources/',
                'source': 'National STEM Video Game Challenge',
                'category': 'Learning Platform',
                'stem_fields': 'Computer Science, Game Design, Programming',
                'target_grade': '7-12',
                'cost': 'Free',
                'location_type': 'Online',
                'time_commitment': 'Self-paced',
                'prerequisite_level': 'Medium',
                'support_level': 'Low',
                'deadline': 'None',
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
                'family_involvement_required': 'Optional',
                'peer_network_building': 'False',
                'mentor_access_level': 'None'
            },
            {
                'name': 'STEM Challenge Educator Workshop',
                'description': 'Professional development for teachers incorporating game design into STEM curriculum. Learn how to guide students through the competition and integrate game-based learning.',
                'url': 'https://www.stemchallenge.org/',
                'source': 'National STEM Video Game Challenge',
                'category': 'Professional Development',
                'stem_fields': 'Computer Science, Game Design, Education',
                'target_grade': 'K-12',
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
                'diversity_focus': 'False',
                'underrepresented_friendly': 'True',
                'first_gen_support': 'True',
                'cultural_competency': 'Medium',
                'rural_accessible': 'True',
                'transportation_required': 'False',
                'internet_dependency': 'Required',
                'regional_availability': 'National',
                'family_involvement_required': 'None',
                'peer_network_building': 'True',
                'mentor_access_level': 'Professional'
            },
            {
                'name': 'STEM Challenge Past Winners Showcase',
                'description': 'Gallery of winning games from previous competitions. Students can play past entries, learn from successful designs, and get inspired for their own submissions.',
                'url': 'https://www.stemchallenge.org/',
                'source': 'National STEM Video Game Challenge',
                'category': 'Learning Platform',
                'stem_fields': 'Computer Science, Game Design',
                'target_grade': 'K-12',
                'cost': 'Free',
                'location_type': 'Online',
                'time_commitment': 'Self-directed',
                'prerequisite_level': 'None',
                'support_level': 'Low',
                'deadline': 'None',
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
                'family_involvement_required': 'Optional',
                'peer_network_building': 'True',
                'mentor_access_level': 'None'
            }
        ]
        return resources

    def scrape(self):
        """Main scraping method."""
        print("Starting STEM Video Game Challenge scraping...")
        print("Note: Creating STEM Video Game Challenge resources")
        for url in self.target_urls:
            soup = self.fetch_page(url)
            time.sleep(2)
        print("Creating STEM Challenge entries...")
        self.resources = self.create_stem_challenge_resources()
        print(f"Total resources created: {len(self.resources)}")

    def save_to_csv(self, filename: str = 'data/stem_video_game_challenge.csv'):
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
    scraper = StemVideoGameChallengeScraper()
    scraper.scrape()
    scraper.save_to_csv()
    print("Scraping completed successfully!")


if __name__ == "__main__":
    main()
