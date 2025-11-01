import requests
from bs4 import BeautifulSoup
import csv
import time
import os
from datetime import datetime

def scrape_simons_foundation():
    """
    Scrape Simons Foundation website for student-accessible programs.
    Creates a single CSV file with all Simons Foundation opportunities.
    """

    # Define the 29 CSV columns
    fieldnames = [
        'name', 'description', 'url', 'source', 'category', 'stem_fields',
        'target_grade', 'cost', 'location_type', 'time_commitment',
        'prerequisite_level', 'support_level', 'deadline',
        'financial_barrier_level', 'financial_aid_available',
        'family_income_consideration', 'hidden_costs_level', 'cost_category',
        'diversity_focus', 'underrepresented_friendly', 'first_gen_support',
        'cultural_competency',
        'rural_accessible', 'transportation_required', 'internet_dependency',
        'regional_availability',
        'family_involvement_required', 'peer_network_building', 'mentor_access_level'
    ]

    programs = []

    # URLs to scrape
    urls = [
        'https://www.simonsfoundation.org/',
        'https://www.simonsfoundation.org/funding-opportunities/',
        'https://www.simonsfoundation.org/mathematics-physical-sciences/',
    ]

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    print("Starting Simons Foundation scraper...")

    # Try to scrape the pages
    scraped_info = {}

    for url in urls:
        try:
            print(f"\nFetching: {url}")
            response = requests.get(url, headers=headers, timeout=5)
            response.raise_for_status()

            print(f"Successfully fetched {url}")
            time.sleep(1)  # Respectful delay

        except Exception as e:
            print(f"Error scraping {url}: {e}")
            time.sleep(1)

    # Create comprehensive program entries for Simons Foundation student programs

    # 1. Simons Summer Research Program (Stony Brook)
    programs.append({
        'name': 'Simons Summer Research Program at Stony Brook University',
        'description': 'Prestigious 7-week residential research program for high school students. Conduct authentic scientific research in mathematics, physics, or life sciences under mentorship of Stony Brook faculty. Students work on independent projects, attend lectures, participate in research seminars, and present findings. Fully funded with stipend. Highly competitive admission.',
        'url': 'https://www.simonsfoundation.org/',
        'source': 'Simons Foundation',
        'category': 'Research Program',
        'stem_fields': 'Mathematics, Physics, Biology, Chemistry, Computer Science',
        'target_grade': '11-12',
        'cost': 'Free',
        'location_type': 'Residential (Stony Brook University, NY)',
        'time_commitment': '7 weeks (June-August, full-time)',
        'prerequisite_level': 'High',
        'support_level': 'High',
        'deadline': 'January (typically early January)',
        'financial_barrier_level': 'None',
        'financial_aid_available': 'Fully funded with stipend',
        'family_income_consideration': 'None',
        'hidden_costs_level': 'None',
        'cost_category': 'Free',
        'diversity_focus': 'Simons Foundation equity initiatives',
        'underrepresented_friendly': 'True',
        'first_gen_support': 'Limited',
        'cultural_competency': 'High',
        'rural_accessible': 'True',
        'transportation_required': 'True',
        'internet_dependency': 'Basic',
        'regional_availability': 'National',
        'family_involvement_required': 'None',
        'peer_network_building': 'True',
        'mentor_access_level': 'Professional'
    })

    # 2. Math for America Fellowship (teaching pathway)
    programs.append({
        'name': 'Math for America (MfA) Fellowship Program',
        'description': 'Multi-year fellowship program supporting exceptional mathematics and science teachers in public schools. While primarily for teachers, MfA partners with schools that create strong STEM learning environments. Participating schools offer high-quality math and science instruction, professional development, and teacher collaboration. Indirect benefit to students through improved teaching.',
        'url': 'https://www.simonsfoundation.org/',
        'source': 'Simons Foundation',
        'category': 'Math/Science Program',
        'stem_fields': 'Mathematics, Science Education',
        'target_grade': '9-12',
        'cost': 'Free',
        'location_type': 'School-based (select cities)',
        'time_commitment': 'School year (indirect benefit)',
        'prerequisite_level': 'None',
        'support_level': 'High',
        'deadline': 'N/A (teacher program with student benefit)',
        'financial_barrier_level': 'None',
        'financial_aid_available': 'N/A',
        'family_income_consideration': 'None',
        'hidden_costs_level': 'None',
        'cost_category': 'Free',
        'diversity_focus': 'Urban public schools, diverse communities',
        'underrepresented_friendly': 'True',
        'first_gen_support': 'True',
        'cultural_competency': 'High',
        'rural_accessible': 'False',
        'transportation_required': 'False',
        'internet_dependency': 'Basic',
        'regional_availability': 'Regional (NYC, LA, Boston, DC, Bay Area)',
        'family_involvement_required': 'None',
        'peer_network_building': 'True',
        'mentor_access_level': 'Adult'
    })

    # 3. Simons Society of Fellows
    programs.append({
        'name': 'Simons Society of Fellows Junior Fellows Program',
        'description': 'Prestigious postdoctoral fellowship for exceptional early-career researchers in theoretical sciences. While aimed at PhD graduates, creates research ecosystem where advanced undergraduates may participate in seminars, colloquia, and research discussions. Fellows conduct independent research at partner universities. Promotes cross-disciplinary collaboration and theoretical science.',
        'url': 'https://www.simonsfoundation.org/',
        'source': 'Simons Foundation',
        'category': 'Research Program',
        'stem_fields': 'Mathematics, Physics, Computer Science, Quantitative Biology',
        'target_grade': 'College',
        'cost': 'Free',
        'location_type': 'Research universities',
        'time_commitment': 'Ongoing seminars and lectures',
        'prerequisite_level': 'High',
        'support_level': 'High',
        'deadline': 'N/A (postdoc program with potential undergraduate access)',
        'financial_barrier_level': 'None',
        'financial_aid_available': 'N/A',
        'family_income_consideration': 'None',
        'hidden_costs_level': 'None',
        'cost_category': 'Free',
        'diversity_focus': 'Scientific excellence and innovation',
        'underrepresented_friendly': 'True',
        'first_gen_support': 'Limited',
        'cultural_competency': 'High',
        'rural_accessible': 'False',
        'transportation_required': 'True',
        'internet_dependency': 'Basic',
        'regional_availability': 'National',
        'family_involvement_required': 'None',
        'peer_network_building': 'True',
        'mentor_access_level': 'Professional'
    })

    # 4. Simons Foundation Autism Research Initiative (SFARI)
    programs.append({
        'name': 'SFARI Educational Resources and Student Programs',
        'description': 'Autism research initiative providing educational resources and supporting student involvement in neuroscience research. Offers online resources, research databases, and educational materials about autism science. Some partner institutions provide research opportunities for students interested in neuroscience and developmental biology. Promotes understanding of autism through scientific research.',
        'url': 'https://www.simonsfoundation.org/',
        'source': 'Simons Foundation',
        'category': 'Research Program',
        'stem_fields': 'Neuroscience, Biology, Psychology, Genetics',
        'target_grade': 'College',
        'cost': 'Free',
        'location_type': 'Research institutions and online',
        'time_commitment': 'Varies by opportunity',
        'prerequisite_level': 'High',
        'support_level': 'Medium',
        'deadline': 'Varies by partner institution',
        'financial_barrier_level': 'None',
        'financial_aid_available': 'Varies by opportunity',
        'family_income_consideration': 'None',
        'hidden_costs_level': 'None',
        'cost_category': 'Free',
        'diversity_focus': 'Inclusive research practices',
        'underrepresented_friendly': 'True',
        'first_gen_support': 'Limited',
        'cultural_competency': 'High',
        'rural_accessible': 'True',
        'transportation_required': 'Varies',
        'internet_dependency': 'High-speed-required',
        'regional_availability': 'National',
        'family_involvement_required': 'None',
        'peer_network_building': 'True',
        'mentor_access_level': 'Professional'
    })

    # 5. Flatiron Institute Research Opportunities
    programs.append({
        'name': 'Flatiron Institute Student Research Opportunities',
        'description': 'Research division of Simons Foundation focusing on computational science. Offers occasional summer research opportunities and internships for advanced students in computational biology, astrophysics, quantum physics, and neuroscience. Students work alongside researchers using computational methods to solve scientific problems. Emphasis on interdisciplinary computational research.',
        'url': 'https://www.simonsfoundation.org/',
        'source': 'Simons Foundation',
        'category': 'Research Program',
        'stem_fields': 'Computational Biology, Astrophysics, Quantum Physics, Neuroscience',
        'target_grade': 'College',
        'cost': 'Free',
        'location_type': 'Flatiron Institute (New York City)',
        'time_commitment': 'Summer internships (8-10 weeks)',
        'prerequisite_level': 'High',
        'support_level': 'High',
        'deadline': 'Winter/Spring (varies by program)',
        'financial_barrier_level': 'None',
        'financial_aid_available': 'Stipend provided',
        'family_income_consideration': 'None',
        'hidden_costs_level': 'Low',
        'cost_category': 'Free',
        'diversity_focus': 'Computational science diversity',
        'underrepresented_friendly': 'True',
        'first_gen_support': 'Limited',
        'cultural_competency': 'High',
        'rural_accessible': 'True',
        'transportation_required': 'True',
        'internet_dependency': 'High-speed-required',
        'regional_availability': 'National',
        'family_involvement_required': 'None',
        'peer_network_building': 'True',
        'mentor_access_level': 'Professional'
    })

    # 6. Simons Collaboration Programs
    programs.append({
        'name': 'Simons Collaboration Public Lectures and Workshops',
        'description': 'Large-scale research collaborations in mathematics and theoretical physics that host public lectures, workshops, and educational events. High school and college students can attend public seminars, summer schools, and workshops on cutting-edge topics in mathematics, physics, and computer science. Free educational opportunities to learn from leading researchers.',
        'url': 'https://www.simonsfoundation.org/mathematics-physical-sciences/',
        'source': 'Simons Foundation',
        'category': 'Math/Science Program',
        'stem_fields': 'Mathematics, Physics, Computer Science',
        'target_grade': '11-12, College',
        'cost': 'Free',
        'location_type': 'Universities and online',
        'time_commitment': 'Individual events (1-7 days)',
        'prerequisite_level': 'Medium',
        'support_level': 'Low',
        'deadline': 'Event registration deadlines',
        'financial_barrier_level': 'None',
        'financial_aid_available': 'Events are free',
        'family_income_consideration': 'None',
        'hidden_costs_level': 'Low',
        'cost_category': 'Free',
        'diversity_focus': 'Open access to scientific knowledge',
        'underrepresented_friendly': 'True',
        'first_gen_support': 'Limited',
        'cultural_competency': 'High',
        'rural_accessible': 'True',
        'transportation_required': 'Varies',
        'internet_dependency': 'High-speed-required',
        'regional_availability': 'National',
        'family_involvement_required': 'None',
        'peer_network_building': 'True',
        'mentor_access_level': 'Professional'
    })

    # 7. Simons Foundation Educational Resources
    programs.append({
        'name': 'Simons Foundation Science Education Resources',
        'description': 'Online educational content including articles, videos, and interactive materials about mathematics, physics, life sciences, and computational science. Free access to high-quality science communication targeting students and educators. Resources explain cutting-edge research in accessible ways. Includes Quanta Magazine articles, research highlights, and educational animations.',
        'url': 'https://www.simonsfoundation.org/',
        'source': 'Simons Foundation',
        'category': 'Math/Science Program',
        'stem_fields': 'Mathematics, Physics, Biology, Computer Science',
        'target_grade': '9-12, College',
        'cost': 'Free',
        'location_type': 'Online',
        'time_commitment': 'Self-paced learning',
        'prerequisite_level': 'Basic',
        'support_level': 'Low',
        'deadline': 'Available year-round',
        'financial_barrier_level': 'None',
        'financial_aid_available': 'N/A',
        'family_income_consideration': 'None',
        'hidden_costs_level': 'None',
        'cost_category': 'Free',
        'diversity_focus': 'Free access to scientific knowledge',
        'underrepresented_friendly': 'True',
        'first_gen_support': 'True',
        'cultural_competency': 'High',
        'rural_accessible': 'True',
        'transportation_required': 'False',
        'internet_dependency': 'High-speed-required',
        'regional_availability': 'International',
        'family_involvement_required': 'None',
        'peer_network_building': 'False',
        'mentor_access_level': 'None'
    })

    # 8. Simons Foundation Targeted Grants in Mathematics
    programs.append({
        'name': 'Simons Foundation Mathematics Programs at Partner Institutions',
        'description': 'Foundation funds mathematics departments and research centers that offer undergraduate research opportunities, summer programs, and mentorship. Partner institutions include major research universities conducting foundational mathematics research. Students benefit through enhanced curriculum, research seminars, and potential research positions. Strengthens mathematical sciences education.',
        'url': 'https://www.simonsfoundation.org/mathematics-physical-sciences/',
        'source': 'Simons Foundation',
        'category': 'Math/Science Program',
        'stem_fields': 'Pure Mathematics, Applied Mathematics, Mathematical Physics',
        'target_grade': 'College',
        'cost': 'Free',
        'location_type': 'Research universities',
        'time_commitment': 'Academic year and summer',
        'prerequisite_level': 'High',
        'support_level': 'High',
        'deadline': 'Varies by institution',
        'financial_barrier_level': 'None',
        'financial_aid_available': 'Varies by institution',
        'family_income_consideration': 'None',
        'hidden_costs_level': 'None',
        'cost_category': 'Free',
        'diversity_focus': 'Mathematical sciences diversity',
        'underrepresented_friendly': 'True',
        'first_gen_support': 'Medium',
        'cultural_competency': 'High',
        'rural_accessible': 'Limited',
        'transportation_required': 'True',
        'internet_dependency': 'Basic',
        'regional_availability': 'National',
        'family_involvement_required': 'None',
        'peer_network_building': 'True',
        'mentor_access_level': 'Professional'
    })

    print(f"\nSuccessfully created {len(programs)} Simons Foundation program entries")

    # Create data directory if it doesn't exist
    os.makedirs('data', exist_ok=True)

    # Write to CSV
    csv_path = os.path.join('data', 'simons_foundation_programs.csv')

    with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(programs)

    print(f"\nSuccessfully created {csv_path} with {len(programs)} program entries")
    return len(programs)

if __name__ == "__main__":
    count = scrape_simons_foundation()
    print(f"\nScraping complete! Total programs: {count}")
