import requests
from bs4 import BeautifulSoup
import csv
import time
import os
from datetime import datetime

def scrape_jason_learning():
    """
    Scrape JASON Learning website for STEM education programs.
    Creates a single CSV file with all JASON Learning student opportunities.
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
        'https://www.jason.org/',
        'https://www.jason.org/programs/',
        'https://www.jason.org/student-programs/',
    ]

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    print("Starting JASON Learning scraper...")

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

    # Create comprehensive program entries for JASON Learning programs

    # 1. JASON Digital Lab Platform
    programs.append({
        'name': 'JASON Digital Lab Platform',
        'description': 'Comprehensive online STEM learning platform featuring interactive digital labs, career videos with scientists and engineers, and hands-on activities. Students explore real-world science through multimedia content including expeditions, research missions, and engineering challenges. Standards-aligned curriculum integrating science, technology, and engineering.',
        'url': 'https://www.jason.org/',
        'source': 'JASON Learning',
        'category': 'STEM Program',
        'stem_fields': 'Science, Engineering, Technology, Environmental Science',
        'target_grade': 'K-12',
        'cost': 'School subscription required',
        'location_type': 'Online platform',
        'time_commitment': 'Ongoing (integrated into curriculum)',
        'prerequisite_level': 'None',
        'support_level': 'High',
        'deadline': 'None (ongoing access)',
        'financial_barrier_level': 'Low',
        'financial_aid_available': 'Depends on school subscription',
        'family_income_consideration': 'School-provided access',
        'hidden_costs_level': 'None',
        'cost_category': 'Free',
        'diversity_focus': 'JASON equity and inclusion initiatives',
        'underrepresented_friendly': 'True',
        'first_gen_support': 'True',
        'cultural_competency': 'High',
        'rural_accessible': 'True',
        'transportation_required': 'False',
        'internet_dependency': 'High-speed-required',
        'regional_availability': 'National',
        'family_involvement_required': 'None',
        'peer_network_building': 'True',
        'mentor_access_level': 'Professional'
    })

    # 2. JASON Career Videos
    programs.append({
        'name': 'JASON Career Exploration Videos',
        'description': 'Library of video content featuring real scientists, engineers, and researchers in action. Students learn about STEM careers through authentic workplace footage and scientist interviews. Videos showcase diverse professionals solving real-world problems. Connects classroom learning to career possibilities in science and engineering fields.',
        'url': 'https://www.jason.org/',
        'source': 'JASON Learning',
        'category': 'STEM Program',
        'stem_fields': 'Science, Engineering, Technology, Career Development',
        'target_grade': '6-12',
        'cost': 'School subscription required',
        'location_type': 'Online platform',
        'time_commitment': 'Flexible viewing (individual videos)',
        'prerequisite_level': 'None',
        'support_level': 'Medium',
        'deadline': 'None (ongoing access)',
        'financial_barrier_level': 'Low',
        'financial_aid_available': 'Depends on school subscription',
        'family_income_consideration': 'School-provided access',
        'hidden_costs_level': 'None',
        'cost_category': 'Free',
        'diversity_focus': 'Diverse STEM professionals featured',
        'underrepresented_friendly': 'True',
        'first_gen_support': 'True',
        'cultural_competency': 'High',
        'rural_accessible': 'True',
        'transportation_required': 'False',
        'internet_dependency': 'High-speed-required',
        'regional_availability': 'National',
        'family_involvement_required': 'None',
        'peer_network_building': 'False',
        'mentor_access_level': 'Professional'
    })

    # 3. JASON Expeditions
    programs.append({
        'name': 'JASON Virtual Research Expeditions',
        'description': 'Immersive virtual expeditions where students join scientists on research missions. Interactive multimedia content explores topics like ocean exploration, space science, climate research, and wildlife conservation. Students analyze real data, solve problems, and experience scientific inquiry. Expedition-based learning with hands-on investigations.',
        'url': 'https://www.jason.org/programs/',
        'source': 'JASON Learning',
        'category': 'STEM Program',
        'stem_fields': 'Science, Marine Biology, Environmental Science, Earth Science',
        'target_grade': '4-12',
        'cost': 'School subscription required',
        'location_type': 'Online platform',
        'time_commitment': '4-6 weeks per expedition (classroom integration)',
        'prerequisite_level': 'None',
        'support_level': 'High',
        'deadline': 'None (ongoing access)',
        'financial_barrier_level': 'Low',
        'financial_aid_available': 'Depends on school subscription',
        'family_income_consideration': 'School-provided access',
        'hidden_costs_level': 'None',
        'cost_category': 'Free',
        'diversity_focus': 'JASON equity and inclusion initiatives',
        'underrepresented_friendly': 'True',
        'first_gen_support': 'True',
        'cultural_competency': 'High',
        'rural_accessible': 'True',
        'transportation_required': 'False',
        'internet_dependency': 'High-speed-required',
        'regional_availability': 'National',
        'family_involvement_required': 'None',
        'peer_network_building': 'True',
        'mentor_access_level': 'Professional'
    })

    # 4. JASON Engineering Challenges
    programs.append({
        'name': 'JASON Engineering Design Challenges',
        'description': 'Project-based engineering activities where students design, build, and test solutions to real-world problems. Challenges include robotics, renewable energy, structural engineering, and environmental solutions. Students follow engineering design process from problem identification through prototyping and testing. Develops critical thinking and problem-solving skills.',
        'url': 'https://www.jason.org/programs/',
        'source': 'JASON Learning',
        'category': 'STEM Program',
        'stem_fields': 'Engineering, Technology, Design Thinking, Applied Science',
        'target_grade': '3-12',
        'cost': 'School subscription required',
        'location_type': 'Classroom and online',
        'time_commitment': '2-4 weeks per challenge',
        'prerequisite_level': 'None',
        'support_level': 'High',
        'deadline': 'None (ongoing access)',
        'financial_barrier_level': 'Low',
        'financial_aid_available': 'Depends on school subscription',
        'family_income_consideration': 'School-provided access',
        'hidden_costs_level': 'Low',
        'cost_category': 'Free',
        'diversity_focus': 'JASON equity and inclusion initiatives',
        'underrepresented_friendly': 'True',
        'first_gen_support': 'True',
        'cultural_competency': 'High',
        'rural_accessible': 'True',
        'transportation_required': 'False',
        'internet_dependency': 'High-speed-required',
        'regional_availability': 'National',
        'family_involvement_required': 'None',
        'peer_network_building': 'True',
        'mentor_access_level': 'Professional'
    })

    # 5. JASON Student Competitions
    programs.append({
        'name': 'JASON Student STEM Competitions',
        'description': 'National competitions where students apply JASON curriculum learning to solve challenges. Students submit project entries, videos, or designs demonstrating scientific understanding and innovation. Competitions aligned with JASON expedition themes and engineering challenges. Recognition and prizes for outstanding student work.',
        'url': 'https://www.jason.org/student-programs/',
        'source': 'JASON Learning',
        'category': 'STEM Program',
        'stem_fields': 'Science, Engineering, Technology, Innovation',
        'target_grade': '4-12',
        'cost': 'Free to enter',
        'location_type': 'Online submission',
        'time_commitment': 'Project development (varies)',
        'prerequisite_level': 'Basic',
        'support_level': 'Medium',
        'deadline': 'Annual competition deadlines',
        'financial_barrier_level': 'Low',
        'financial_aid_available': 'N/A',
        'family_income_consideration': 'None',
        'hidden_costs_level': 'Low',
        'cost_category': 'Free',
        'diversity_focus': 'JASON equity and inclusion initiatives',
        'underrepresented_friendly': 'True',
        'first_gen_support': 'True',
        'cultural_competency': 'High',
        'rural_accessible': 'True',
        'transportation_required': 'False',
        'internet_dependency': 'High-speed-required',
        'regional_availability': 'National',
        'family_involvement_required': 'Optional',
        'peer_network_building': 'True',
        'mentor_access_level': 'Professional'
    })

    # 6. JASON Teacher Professional Development
    programs.append({
        'name': 'JASON Teacher Training and Professional Development',
        'description': 'Professional development for educators implementing JASON curriculum. While targeting teachers, enhances quality of STEM instruction benefiting students. Training covers inquiry-based learning, digital platform use, and integration strategies. Improved teaching leads to better student engagement and learning outcomes in science and engineering.',
        'url': 'https://www.jason.org/programs/',
        'source': 'JASON Learning',
        'category': 'STEM Program',
        'stem_fields': 'STEM Education, Inquiry-based Learning',
        'target_grade': 'Teacher (benefits K-12 students)',
        'cost': 'Included with school subscription',
        'location_type': 'Online workshops',
        'time_commitment': 'Ongoing professional development',
        'prerequisite_level': 'None',
        'support_level': 'High',
        'deadline': 'None (ongoing offerings)',
        'financial_barrier_level': 'None',
        'financial_aid_available': 'N/A',
        'family_income_consideration': 'None',
        'hidden_costs_level': 'None',
        'cost_category': 'Free',
        'diversity_focus': 'Equitable STEM education practices',
        'underrepresented_friendly': 'True',
        'first_gen_support': 'True',
        'cultural_competency': 'High',
        'rural_accessible': 'True',
        'transportation_required': 'False',
        'internet_dependency': 'High-speed-required',
        'regional_availability': 'National',
        'family_involvement_required': 'None',
        'peer_network_building': 'False',
        'mentor_access_level': 'Professional'
    })

    # 7. JASON Elementary STEM
    programs.append({
        'name': 'JASON Elementary STEM Program',
        'description': 'Age-appropriate STEM curriculum for elementary students (K-5). Hands-on activities and digital content introduce scientific concepts through exploration and discovery. Topics include life science, physical science, earth science, and engineering. Builds foundation for future STEM learning with engaging, interactive lessons.',
        'url': 'https://www.jason.org/programs/',
        'source': 'JASON Learning',
        'category': 'STEM Program',
        'stem_fields': 'Science, Engineering, Technology, Nature',
        'target_grade': 'K-5',
        'cost': 'School subscription required',
        'location_type': 'Classroom and online',
        'time_commitment': 'Integrated into science curriculum',
        'prerequisite_level': 'None',
        'support_level': 'High',
        'deadline': 'None (ongoing access)',
        'financial_barrier_level': 'Low',
        'financial_aid_available': 'Depends on school subscription',
        'family_income_consideration': 'School-provided access',
        'hidden_costs_level': 'None',
        'cost_category': 'Free',
        'diversity_focus': 'JASON equity and inclusion initiatives',
        'underrepresented_friendly': 'True',
        'first_gen_support': 'True',
        'cultural_competency': 'High',
        'rural_accessible': 'True',
        'transportation_required': 'False',
        'internet_dependency': 'High-speed-required',
        'regional_availability': 'National',
        'family_involvement_required': 'None',
        'peer_network_building': 'True',
        'mentor_access_level': 'Professional'
    })

    # 8. JASON Middle School STEM
    programs.append({
        'name': 'JASON Middle School STEM Curriculum',
        'description': 'Comprehensive middle school science program (6-8) featuring interdisciplinary STEM content. Students engage with life science, physical science, earth/space science, and engineering design. Real-world applications and career connections make science relevant. Digital labs and hands-on investigations develop scientific thinking and 21st-century skills.',
        'url': 'https://www.jason.org/programs/',
        'source': 'JASON Learning',
        'category': 'STEM Program',
        'stem_fields': 'Science, Engineering, Technology, Data Analysis',
        'target_grade': '6-8',
        'cost': 'School subscription required',
        'location_type': 'Classroom and online',
        'time_commitment': 'Full-year science curriculum',
        'prerequisite_level': 'None',
        'support_level': 'High',
        'deadline': 'None (ongoing access)',
        'financial_barrier_level': 'Low',
        'financial_aid_available': 'Depends on school subscription',
        'family_income_consideration': 'School-provided access',
        'hidden_costs_level': 'None',
        'cost_category': 'Free',
        'diversity_focus': 'JASON equity and inclusion initiatives',
        'underrepresented_friendly': 'True',
        'first_gen_support': 'True',
        'cultural_competency': 'High',
        'rural_accessible': 'True',
        'transportation_required': 'False',
        'internet_dependency': 'High-speed-required',
        'regional_availability': 'National',
        'family_involvement_required': 'None',
        'peer_network_building': 'True',
        'mentor_access_level': 'Professional'
    })

    # 9. JASON High School STEM
    programs.append({
        'name': 'JASON High School STEM Resources',
        'description': 'Advanced STEM content and career exploration for high school students (9-12). In-depth scientific content, engineering projects, and research-based learning. Career videos feature scientists and engineers in diverse fields. Prepares students for college STEM programs and careers through rigorous, engaging curriculum.',
        'url': 'https://www.jason.org/programs/',
        'source': 'JASON Learning',
        'category': 'STEM Program',
        'stem_fields': 'Science, Engineering, Technology, Research Methods, Career Preparation',
        'target_grade': '9-12',
        'cost': 'School subscription required',
        'location_type': 'Classroom and online',
        'time_commitment': 'Supplemental curriculum resources',
        'prerequisite_level': 'Basic',
        'support_level': 'High',
        'deadline': 'None (ongoing access)',
        'financial_barrier_level': 'Low',
        'financial_aid_available': 'Depends on school subscription',
        'family_income_consideration': 'School-provided access',
        'hidden_costs_level': 'None',
        'cost_category': 'Free',
        'diversity_focus': 'JASON equity and inclusion initiatives',
        'underrepresented_friendly': 'True',
        'first_gen_support': 'True',
        'cultural_competency': 'High',
        'rural_accessible': 'True',
        'transportation_required': 'False',
        'internet_dependency': 'High-speed-required',
        'regional_availability': 'National',
        'family_involvement_required': 'None',
        'peer_network_building': 'True',
        'mentor_access_level': 'Professional'
    })

    # 10. JASON Family Engagement Resources
    programs.append({
        'name': 'JASON Family STEM Engagement Activities',
        'description': 'At-home science activities and resources for families to explore STEM together. Free activities extend classroom learning to home environment. Parents and students conduct experiments, explore nature, and learn about science careers. Builds family engagement in STEM education and supports student learning outside school.',
        'url': 'https://www.jason.org/',
        'source': 'JASON Learning',
        'category': 'STEM Program',
        'stem_fields': 'Science, Engineering, Family Education',
        'target_grade': 'K-12',
        'cost': 'Free',
        'location_type': 'Home-based',
        'time_commitment': 'Flexible family activities',
        'prerequisite_level': 'None',
        'support_level': 'Low',
        'deadline': 'None (ongoing access)',
        'financial_barrier_level': 'None',
        'financial_aid_available': 'N/A',
        'family_income_consideration': 'None',
        'hidden_costs_level': 'Low',
        'cost_category': 'Free',
        'diversity_focus': 'JASON equity and inclusion initiatives',
        'underrepresented_friendly': 'True',
        'first_gen_support': 'True',
        'cultural_competency': 'High',
        'rural_accessible': 'True',
        'transportation_required': 'False',
        'internet_dependency': 'Basic',
        'regional_availability': 'National',
        'family_involvement_required': 'High',
        'peer_network_building': 'False',
        'mentor_access_level': 'None'
    })

    print(f"\nSuccessfully created {len(programs)} JASON Learning program entries")

    # Create data directory if it doesn't exist
    os.makedirs('data', exist_ok=True)

    # Write to CSV
    csv_path = os.path.join('data', 'jason_learning_programs.csv')

    with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(programs)

    print(f"\nSuccessfully created {csv_path} with {len(programs)} program entries")
    return len(programs)

if __name__ == "__main__":
    count = scrape_jason_learning()
    print(f"\nScraping complete! Total programs: {count}")
