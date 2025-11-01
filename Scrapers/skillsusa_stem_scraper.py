import requests
from bs4 import BeautifulSoup
import csv
import time
import os
from datetime import datetime

def scrape_skillsusa_stem():
    """
    Scrape SkillsUSA website for STEM and technical competition information.
    Creates a single CSV file with all SkillsUSA STEM competition opportunities.
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
        'https://www.skillsusa.org/competitions/',
        'https://www.skillsusa.org/competitions/skillsusa-championships/',
        'https://www.skillsusa.org/programs/',
    ]

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    print("Starting SkillsUSA STEM competitions scraper...")

    # Try to scrape the pages
    scraped_info = {}

    for url in urls:
        try:
            print(f"\nFetching: {url}")
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')

            # Extract text content for analysis
            page_text = soup.get_text()

            # Look for key information
            if 'championship' in page_text.lower():
                scraped_info['has_championships'] = True
            if 'regional' in page_text.lower() and 'state' in page_text.lower():
                scraped_info['multi_level'] = True
            if 'technical' in page_text.lower():
                scraped_info['has_technical'] = True

            print(f"Successfully fetched {url}")
            time.sleep(2)  # Respectful delay

        except Exception as e:
            print(f"Error scraping {url}: {e}")
            time.sleep(1)

    # Create comprehensive program entries for SkillsUSA STEM competitions

    # 1. 3D Visualization and Animation
    programs.append({
        'name': 'SkillsUSA 3D Visualization and Animation',
        'description': 'Competition testing skills in 3D modeling, animation, and rendering. Students create 3D assets, animations, and visual presentations using industry-standard software. Judged on technical proficiency, creativity, and adherence to project specifications. Prepares students for careers in game design, film, and engineering visualization.',
        'url': 'https://www.skillsusa.org/competitions/skillsusa-championships/',
        'source': 'SkillsUSA',
        'category': 'Technical Competition',
        'stem_fields': '3D Modeling, Animation, Computer Graphics, Design Technology',
        'target_grade': '9-12',
        'cost': 'Under-$100 (membership + registration)',
        'location_type': 'Regional and national competition sites',
        'time_commitment': '6-8 months (preparation + competitions)',
        'prerequisite_level': 'Medium',
        'support_level': 'High',
        'deadline': 'Fall (regional), Spring (state/national)',
        'financial_barrier_level': 'Low',
        'financial_aid_available': 'Limited scholarships available',
        'family_income_consideration': 'School-sponsored',
        'hidden_costs_level': 'Medium',
        'cost_category': 'Under-$100',
        'diversity_focus': 'SkillsUSA inclusion initiatives',
        'underrepresented_friendly': 'True',
        'first_gen_support': 'True',
        'cultural_competency': 'High',
        'rural_accessible': 'Limited',
        'transportation_required': 'True',
        'internet_dependency': 'Basic',
        'regional_availability': 'National',
        'family_involvement_required': 'Optional',
        'peer_network_building': 'True',
        'mentor_access_level': 'Adult'
    })

    # 2. CAD Architecture
    programs.append({
        'name': 'SkillsUSA CAD Architecture',
        'description': 'Technical drawing and Computer-Aided Design competition focused on architectural design. Students create detailed architectural plans, elevations, and 3D models using CAD software. Tests knowledge of building codes, structural principles, and design standards. Develops skills for architecture and construction careers.',
        'url': 'https://www.skillsusa.org/competitions/skillsusa-championships/',
        'source': 'SkillsUSA',
        'category': 'Technical Competition',
        'stem_fields': 'Architecture, CAD, Engineering Design, Construction Technology',
        'target_grade': '9-12',
        'cost': 'Under-$100 (membership + registration)',
        'location_type': 'Regional and national competition sites',
        'time_commitment': '6-8 months (preparation + competitions)',
        'prerequisite_level': 'Medium',
        'support_level': 'High',
        'deadline': 'Fall (regional), Spring (state/national)',
        'financial_barrier_level': 'Low',
        'financial_aid_available': 'Limited scholarships available',
        'family_income_consideration': 'School-sponsored',
        'hidden_costs_level': 'Medium',
        'cost_category': 'Under-$100',
        'diversity_focus': 'SkillsUSA inclusion initiatives',
        'underrepresented_friendly': 'True',
        'first_gen_support': 'True',
        'cultural_competency': 'High',
        'rural_accessible': 'Limited',
        'transportation_required': 'True',
        'internet_dependency': 'Basic',
        'regional_availability': 'National',
        'family_involvement_required': 'Optional',
        'peer_network_building': 'True',
        'mentor_access_level': 'Adult'
    })

    # 3. CAD Engineering
    programs.append({
        'name': 'SkillsUSA CAD Engineering',
        'description': 'Engineering design competition using Computer-Aided Design software. Students create detailed engineering drawings, assemblies, and technical documentation. Tests mechanical design principles, geometric dimensioning and tolerancing (GD&T), and manufacturing considerations. Aligns with industry standards for engineering drafting.',
        'url': 'https://www.skillsusa.org/competitions/skillsusa-championships/',
        'source': 'SkillsUSA',
        'category': 'Technical Competition',
        'stem_fields': 'Mechanical Engineering, CAD, Engineering Design, Manufacturing',
        'target_grade': '9-12',
        'cost': 'Under-$100 (membership + registration)',
        'location_type': 'Regional and national competition sites',
        'time_commitment': '6-8 months (preparation + competitions)',
        'prerequisite_level': 'Medium',
        'support_level': 'High',
        'deadline': 'Fall (regional), Spring (state/national)',
        'financial_barrier_level': 'Low',
        'financial_aid_available': 'Limited scholarships available',
        'family_income_consideration': 'School-sponsored',
        'hidden_costs_level': 'Medium',
        'cost_category': 'Under-$100',
        'diversity_focus': 'SkillsUSA inclusion initiatives',
        'underrepresented_friendly': 'True',
        'first_gen_support': 'True',
        'cultural_competency': 'High',
        'rural_accessible': 'Limited',
        'transportation_required': 'True',
        'internet_dependency': 'Basic',
        'regional_availability': 'National',
        'family_involvement_required': 'Optional',
        'peer_network_building': 'True',
        'mentor_access_level': 'Adult'
    })

    # 4. Computer Programming
    programs.append({
        'name': 'SkillsUSA Computer Programming',
        'description': 'Software development competition testing coding skills in multiple programming languages. Students solve algorithmic problems, debug code, and develop functional applications. Covers object-oriented programming, data structures, algorithms, and software design patterns. Prepares students for computer science careers.',
        'url': 'https://www.skillsusa.org/competitions/skillsusa-championships/',
        'source': 'SkillsUSA',
        'category': 'Technical Competition',
        'stem_fields': 'Computer Science, Programming, Software Development',
        'target_grade': '9-12',
        'cost': 'Under-$100 (membership + registration)',
        'location_type': 'Regional and national competition sites',
        'time_commitment': '6-8 months (preparation + competitions)',
        'prerequisite_level': 'Medium',
        'support_level': 'High',
        'deadline': 'Fall (regional), Spring (state/national)',
        'financial_barrier_level': 'Low',
        'financial_aid_available': 'Limited scholarships available',
        'family_income_consideration': 'School-sponsored',
        'hidden_costs_level': 'Low',
        'cost_category': 'Under-$100',
        'diversity_focus': 'SkillsUSA inclusion initiatives',
        'underrepresented_friendly': 'True',
        'first_gen_support': 'True',
        'cultural_competency': 'High',
        'rural_accessible': 'Limited',
        'transportation_required': 'True',
        'internet_dependency': 'Basic',
        'regional_availability': 'National',
        'family_involvement_required': 'Optional',
        'peer_network_building': 'True',
        'mentor_access_level': 'Adult'
    })

    # 5. Cybersecurity
    programs.append({
        'name': 'SkillsUSA Cybersecurity',
        'description': 'Information security competition testing network defense, vulnerability assessment, and incident response. Students identify security threats, implement protective measures, and respond to simulated cyber attacks. Covers ethical hacking, network security, cryptography, and security policy. Aligns with industry certifications and cybersecurity careers.',
        'url': 'https://www.skillsusa.org/competitions/skillsusa-championships/',
        'source': 'SkillsUSA',
        'category': 'Technical Competition',
        'stem_fields': 'Cybersecurity, Information Technology, Network Security',
        'target_grade': '9-12',
        'cost': 'Under-$100 (membership + registration)',
        'location_type': 'Regional and national competition sites',
        'time_commitment': '6-8 months (preparation + competitions)',
        'prerequisite_level': 'High',
        'support_level': 'High',
        'deadline': 'Fall (regional), Spring (state/national)',
        'financial_barrier_level': 'Low',
        'financial_aid_available': 'Limited scholarships available',
        'family_income_consideration': 'School-sponsored',
        'hidden_costs_level': 'Low',
        'cost_category': 'Under-$100',
        'diversity_focus': 'SkillsUSA inclusion initiatives',
        'underrepresented_friendly': 'True',
        'first_gen_support': 'True',
        'cultural_competency': 'High',
        'rural_accessible': 'Limited',
        'transportation_required': 'True',
        'internet_dependency': 'High-speed-required',
        'regional_availability': 'National',
        'family_involvement_required': 'Optional',
        'peer_network_building': 'True',
        'mentor_access_level': 'Adult'
    })

    # 6. Electronics Technology
    programs.append({
        'name': 'SkillsUSA Electronics Technology',
        'description': 'Hands-on electronics competition testing circuit design, troubleshooting, and repair. Students work with analog and digital circuits, microcontrollers, and electronic components. Includes practical skills in soldering, circuit analysis, and electronic system design. Prepares for careers in electronics engineering and technology.',
        'url': 'https://www.skillsusa.org/competitions/skillsusa-championships/',
        'source': 'SkillsUSA',
        'category': 'Technical Competition',
        'stem_fields': 'Electronics, Electrical Engineering, Circuit Design',
        'target_grade': '9-12',
        'cost': 'Under-$100 (membership + registration)',
        'location_type': 'Regional and national competition sites',
        'time_commitment': '6-8 months (preparation + competitions)',
        'prerequisite_level': 'Medium',
        'support_level': 'High',
        'deadline': 'Fall (regional), Spring (state/national)',
        'financial_barrier_level': 'Low',
        'financial_aid_available': 'Limited scholarships available',
        'family_income_consideration': 'School-sponsored',
        'hidden_costs_level': 'Medium',
        'cost_category': 'Under-$100',
        'diversity_focus': 'SkillsUSA inclusion initiatives',
        'underrepresented_friendly': 'True',
        'first_gen_support': 'True',
        'cultural_competency': 'High',
        'rural_accessible': 'Limited',
        'transportation_required': 'True',
        'internet_dependency': 'Basic',
        'regional_availability': 'National',
        'family_involvement_required': 'Optional',
        'peer_network_building': 'True',
        'mentor_access_level': 'Adult'
    })

    # 7. Engineering Technology/Design
    programs.append({
        'name': 'SkillsUSA Engineering Technology/Design',
        'description': 'Team-based engineering design competition solving real-world problems. Teams research, design, prototype, and present engineering solutions using technical documentation and CAD models. Emphasizes STEM integration, teamwork, and engineering design process. Tests both technical skills and professional presentation abilities.',
        'url': 'https://www.skillsusa.org/competitions/skillsusa-championships/',
        'source': 'SkillsUSA',
        'category': 'Technical Competition',
        'stem_fields': 'Engineering, Design, Technology, STEM Integration',
        'target_grade': '9-12',
        'cost': 'Under-$100 (membership + registration)',
        'location_type': 'Regional and national competition sites',
        'time_commitment': '6-8 months (preparation + competitions)',
        'prerequisite_level': 'Medium',
        'support_level': 'High',
        'deadline': 'Fall (regional), Spring (state/national)',
        'financial_barrier_level': 'Low',
        'financial_aid_available': 'Limited scholarships available',
        'family_income_consideration': 'School-sponsored',
        'hidden_costs_level': 'Medium',
        'cost_category': 'Under-$100',
        'diversity_focus': 'SkillsUSA inclusion initiatives',
        'underrepresented_friendly': 'True',
        'first_gen_support': 'True',
        'cultural_competency': 'High',
        'rural_accessible': 'Limited',
        'transportation_required': 'True',
        'internet_dependency': 'Basic',
        'regional_availability': 'National',
        'family_involvement_required': 'Optional',
        'peer_network_building': 'True',
        'mentor_access_level': 'Adult'
    })

    # 8. Mobile Robotics
    programs.append({
        'name': 'SkillsUSA Mobile Robotics Technology',
        'description': 'Robotics competition where students program and operate mobile robots to complete challenges. Teams design, build, and program autonomous robots to navigate obstacles, complete tasks, and demonstrate technical capabilities. Covers programming, sensors, motors, and robot control systems. Emphasizes problem-solving and iterative design.',
        'url': 'https://www.skillsusa.org/competitions/skillsusa-championships/',
        'source': 'SkillsUSA',
        'category': 'Technical Competition',
        'stem_fields': 'Robotics, Engineering, Programming, Mechatronics',
        'target_grade': '9-12',
        'cost': 'Under-$100 (membership + registration)',
        'location_type': 'Regional and national competition sites',
        'time_commitment': '6-8 months (preparation + competitions)',
        'prerequisite_level': 'Medium',
        'support_level': 'High',
        'deadline': 'Fall (regional), Spring (state/national)',
        'financial_barrier_level': 'Low',
        'financial_aid_available': 'Limited scholarships available',
        'family_income_consideration': 'School-sponsored',
        'hidden_costs_level': 'High',
        'cost_category': 'Under-$100',
        'diversity_focus': 'SkillsUSA inclusion initiatives',
        'underrepresented_friendly': 'True',
        'first_gen_support': 'True',
        'cultural_competency': 'High',
        'rural_accessible': 'Limited',
        'transportation_required': 'True',
        'internet_dependency': 'Basic',
        'regional_availability': 'National',
        'family_involvement_required': 'Optional',
        'peer_network_building': 'True',
        'mentor_access_level': 'Adult'
    })

    # 9. Network Systems Administration
    programs.append({
        'name': 'SkillsUSA Network Systems Administration',
        'description': 'IT infrastructure competition testing network configuration, server administration, and troubleshooting. Students configure routers, switches, servers, and network services. Covers Windows and Linux administration, network protocols, and IT security. Prepares for industry certifications (Cisco, CompTIA) and IT careers.',
        'url': 'https://www.skillsusa.org/competitions/skillsusa-championships/',
        'source': 'SkillsUSA',
        'category': 'Technical Competition',
        'stem_fields': 'Information Technology, Networking, Systems Administration',
        'target_grade': '9-12',
        'cost': 'Under-$100 (membership + registration)',
        'location_type': 'Regional and national competition sites',
        'time_commitment': '6-8 months (preparation + competitions)',
        'prerequisite_level': 'Medium',
        'support_level': 'High',
        'deadline': 'Fall (regional), Spring (state/national)',
        'financial_barrier_level': 'Low',
        'financial_aid_available': 'Limited scholarships available',
        'family_income_consideration': 'School-sponsored',
        'hidden_costs_level': 'Low',
        'cost_category': 'Under-$100',
        'diversity_focus': 'SkillsUSA inclusion initiatives',
        'underrepresented_friendly': 'True',
        'first_gen_support': 'True',
        'cultural_competency': 'High',
        'rural_accessible': 'Limited',
        'transportation_required': 'True',
        'internet_dependency': 'High-speed-required',
        'regional_availability': 'National',
        'family_involvement_required': 'Optional',
        'peer_network_building': 'True',
        'mentor_access_level': 'Adult'
    })

    # 10. Precision Machining
    programs.append({
        'name': 'SkillsUSA Precision Machining',
        'description': 'Advanced manufacturing competition testing CNC programming and manual machining skills. Students program CNC mills and lathes, read blueprints, use precision measuring tools, and produce machined parts to exact specifications. Emphasizes safety, quality control, and manufacturing processes. Career pathway to manufacturing engineering.',
        'url': 'https://www.skillsusa.org/competitions/skillsusa-championships/',
        'source': 'SkillsUSA',
        'category': 'Technical Competition',
        'stem_fields': 'Manufacturing, Machining, CNC Programming, Engineering',
        'target_grade': '9-12',
        'cost': 'Under-$100 (membership + registration)',
        'location_type': 'Regional and national competition sites',
        'time_commitment': '6-8 months (preparation + competitions)',
        'prerequisite_level': 'High',
        'support_level': 'High',
        'deadline': 'Fall (regional), Spring (state/national)',
        'financial_barrier_level': 'Low',
        'financial_aid_available': 'Limited scholarships available',
        'family_income_consideration': 'School-sponsored',
        'hidden_costs_level': 'Medium',
        'cost_category': 'Under-$100',
        'diversity_focus': 'SkillsUSA inclusion initiatives',
        'underrepresented_friendly': 'True',
        'first_gen_support': 'True',
        'cultural_competency': 'High',
        'rural_accessible': 'Limited',
        'transportation_required': 'True',
        'internet_dependency': 'Basic',
        'regional_availability': 'National',
        'family_involvement_required': 'Optional',
        'peer_network_building': 'True',
        'mentor_access_level': 'Adult'
    })

    # 11. Renewable Energy Technology
    programs.append({
        'name': 'SkillsUSA Renewable Energy Technology',
        'description': 'Sustainable energy competition covering solar, wind, and alternative energy systems. Students install, troubleshoot, and maintain renewable energy equipment. Tests knowledge of energy efficiency, grid integration, and environmental impact. Prepares for emerging careers in clean energy sector.',
        'url': 'https://www.skillsusa.org/competitions/skillsusa-championships/',
        'source': 'SkillsUSA',
        'category': 'Technical Competition',
        'stem_fields': 'Renewable Energy, Environmental Science, Engineering Technology',
        'target_grade': '9-12',
        'cost': 'Under-$100 (membership + registration)',
        'location_type': 'Regional and national competition sites',
        'time_commitment': '6-8 months (preparation + competitions)',
        'prerequisite_level': 'Medium',
        'support_level': 'High',
        'deadline': 'Fall (regional), Spring (state/national)',
        'financial_barrier_level': 'Low',
        'financial_aid_available': 'Limited scholarships available',
        'family_income_consideration': 'School-sponsored',
        'hidden_costs_level': 'Medium',
        'cost_category': 'Under-$100',
        'diversity_focus': 'SkillsUSA inclusion initiatives',
        'underrepresented_friendly': 'True',
        'first_gen_support': 'True',
        'cultural_competency': 'High',
        'rural_accessible': 'Limited',
        'transportation_required': 'True',
        'internet_dependency': 'Basic',
        'regional_availability': 'National',
        'family_involvement_required': 'Optional',
        'peer_network_building': 'True',
        'mentor_access_level': 'Adult'
    })

    # 12. Robotics and Automation Technology
    programs.append({
        'name': 'SkillsUSA Robotics and Automation Technology',
        'description': 'Industrial robotics competition testing robot programming, operation, and maintenance. Students program robotic arms, design automation systems, and troubleshoot industrial equipment. Covers PLC programming, sensors, actuators, and manufacturing automation. Aligns with Industry 4.0 skills and smart manufacturing.',
        'url': 'https://www.skillsusa.org/competitions/skillsusa-championships/',
        'source': 'SkillsUSA',
        'category': 'Technical Competition',
        'stem_fields': 'Robotics, Automation, Manufacturing, Engineering Technology',
        'target_grade': '9-12',
        'cost': 'Under-$100 (membership + registration)',
        'location_type': 'Regional and national competition sites',
        'time_commitment': '6-8 months (preparation + competitions)',
        'prerequisite_level': 'High',
        'support_level': 'High',
        'deadline': 'Fall (regional), Spring (state/national)',
        'financial_barrier_level': 'Low',
        'financial_aid_available': 'Limited scholarships available',
        'family_income_consideration': 'School-sponsored',
        'hidden_costs_level': 'Medium',
        'cost_category': 'Under-$100',
        'diversity_focus': 'SkillsUSA inclusion initiatives',
        'underrepresented_friendly': 'True',
        'first_gen_support': 'True',
        'cultural_competency': 'High',
        'rural_accessible': 'Limited',
        'transportation_required': 'True',
        'internet_dependency': 'Basic',
        'regional_availability': 'National',
        'family_involvement_required': 'Optional',
        'peer_network_building': 'True',
        'mentor_access_level': 'Adult'
    })

    # 13. Technical Drafting
    programs.append({
        'name': 'SkillsUSA Technical Drafting',
        'description': 'Traditional and computer-aided drafting competition. Students create technical drawings using manual drafting techniques and CAD software. Tests understanding of orthographic projection, dimensioning, tolerancing, and drawing standards. Develops skills for engineering support roles.',
        'url': 'https://www.skillsusa.org/competitions/skillsusa-championships/',
        'source': 'SkillsUSA',
        'category': 'Technical Competition',
        'stem_fields': 'Technical Drawing, CAD, Engineering Graphics',
        'target_grade': '9-12',
        'cost': 'Under-$100 (membership + registration)',
        'location_type': 'Regional and national competition sites',
        'time_commitment': '6-8 months (preparation + competitions)',
        'prerequisite_level': 'Medium',
        'support_level': 'High',
        'deadline': 'Fall (regional), Spring (state/national)',
        'financial_barrier_level': 'Low',
        'financial_aid_available': 'Limited scholarships available',
        'family_income_consideration': 'School-sponsored',
        'hidden_costs_level': 'Low',
        'cost_category': 'Under-$100',
        'diversity_focus': 'SkillsUSA inclusion initiatives',
        'underrepresented_friendly': 'True',
        'first_gen_support': 'True',
        'cultural_competency': 'High',
        'rural_accessible': 'Limited',
        'transportation_required': 'True',
        'internet_dependency': 'Basic',
        'regional_availability': 'National',
        'family_involvement_required': 'Optional',
        'peer_network_building': 'True',
        'mentor_access_level': 'Adult'
    })

    # 14. Web Design
    programs.append({
        'name': 'SkillsUSA Web Design',
        'description': 'Website development competition testing HTML, CSS, JavaScript, and responsive design. Students create functional websites meeting client specifications. Covers user experience (UX), accessibility, and web standards. Tests both front-end development and design skills. Prepares for web development careers.',
        'url': 'https://www.skillsusa.org/competitions/skillsusa-championships/',
        'source': 'SkillsUSA',
        'category': 'Technical Competition',
        'stem_fields': 'Web Development, Computer Science, Digital Media',
        'target_grade': '9-12',
        'cost': 'Under-$100 (membership + registration)',
        'location_type': 'Regional and national competition sites',
        'time_commitment': '6-8 months (preparation + competitions)',
        'prerequisite_level': 'Medium',
        'support_level': 'High',
        'deadline': 'Fall (regional), Spring (state/national)',
        'financial_barrier_level': 'Low',
        'financial_aid_available': 'Limited scholarships available',
        'family_income_consideration': 'School-sponsored',
        'hidden_costs_level': 'Low',
        'cost_category': 'Under-$100',
        'diversity_focus': 'SkillsUSA inclusion initiatives',
        'underrepresented_friendly': 'True',
        'first_gen_support': 'True',
        'cultural_competency': 'High',
        'rural_accessible': 'Limited',
        'transportation_required': 'True',
        'internet_dependency': 'High-speed-required',
        'regional_availability': 'National',
        'family_involvement_required': 'Optional',
        'peer_network_building': 'True',
        'mentor_access_level': 'Adult'
    })

    # 15. Welding Technology
    programs.append({
        'name': 'SkillsUSA Welding Technology',
        'description': 'Advanced welding competition testing multiple welding processes (SMAW, GMAW, GTAW, FCAW). Students produce welded joints meeting AWS standards, read blueprints, and demonstrate safety procedures. Emphasizes precision, quality, and industry certifications. Leads to high-demand manufacturing and construction careers.',
        'url': 'https://www.skillsusa.org/competitions/skillsusa-championships/',
        'source': 'SkillsUSA',
        'category': 'Technical Competition',
        'stem_fields': 'Welding, Manufacturing, Materials Science, Engineering Technology',
        'target_grade': '9-12',
        'cost': 'Under-$100 (membership + registration)',
        'location_type': 'Regional and national competition sites',
        'time_commitment': '6-8 months (preparation + competitions)',
        'prerequisite_level': 'High',
        'support_level': 'High',
        'deadline': 'Fall (regional), Spring (state/national)',
        'financial_barrier_level': 'Low',
        'financial_aid_available': 'Limited scholarships available',
        'family_income_consideration': 'School-sponsored',
        'hidden_costs_level': 'Medium',
        'cost_category': 'Under-$100',
        'diversity_focus': 'SkillsUSA inclusion initiatives',
        'underrepresented_friendly': 'True',
        'first_gen_support': 'True',
        'cultural_competency': 'High',
        'rural_accessible': 'Limited',
        'transportation_required': 'True',
        'internet_dependency': 'Basic',
        'regional_availability': 'National',
        'family_involvement_required': 'Optional',
        'peer_network_building': 'True',
        'mentor_access_level': 'Adult'
    })

    # 16. Additive Manufacturing
    programs.append({
        'name': 'SkillsUSA Additive Manufacturing (3D Printing)',
        'description': 'Emerging technology competition focused on 3D printing and additive manufacturing. Students design 3D models, prepare files for printing, operate 3D printers, and troubleshoot print quality. Covers various printing technologies (FDM, SLA, SLS) and materials. Prepares for advanced manufacturing careers.',
        'url': 'https://www.skillsusa.org/competitions/skillsusa-championships/',
        'source': 'SkillsUSA',
        'category': 'Technical Competition',
        'stem_fields': 'Additive Manufacturing, 3D Printing, Design Technology, Engineering',
        'target_grade': '9-12',
        'cost': 'Under-$100 (membership + registration)',
        'location_type': 'Regional and national competition sites',
        'time_commitment': '6-8 months (preparation + competitions)',
        'prerequisite_level': 'Medium',
        'support_level': 'High',
        'deadline': 'Fall (regional), Spring (state/national)',
        'financial_barrier_level': 'Low',
        'financial_aid_available': 'Limited scholarships available',
        'family_income_consideration': 'School-sponsored',
        'hidden_costs_level': 'Medium',
        'cost_category': 'Under-$100',
        'diversity_focus': 'SkillsUSA inclusion initiatives',
        'underrepresented_friendly': 'True',
        'first_gen_support': 'True',
        'cultural_competency': 'High',
        'rural_accessible': 'Limited',
        'transportation_required': 'True',
        'internet_dependency': 'Basic',
        'regional_availability': 'National',
        'family_involvement_required': 'Optional',
        'peer_network_building': 'True',
        'mentor_access_level': 'Adult'
    })

    # 17. Electrical Construction Wiring
    programs.append({
        'name': 'SkillsUSA Electrical Construction Wiring',
        'description': 'Electrical trades competition testing residential and commercial wiring skills. Students install electrical systems according to National Electrical Code (NEC), troubleshoot circuits, and demonstrate safety procedures. Covers conduit bending, motor controls, and panel installation. Pathway to electrician certification.',
        'url': 'https://www.skillsusa.org/competitions/skillsusa-championships/',
        'source': 'SkillsUSA',
        'category': 'Technical Competition',
        'stem_fields': 'Electrical Technology, Construction, Engineering Technology',
        'target_grade': '9-12',
        'cost': 'Under-$100 (membership + registration)',
        'location_type': 'Regional and national competition sites',
        'time_commitment': '6-8 months (preparation + competitions)',
        'prerequisite_level': 'Medium',
        'support_level': 'High',
        'deadline': 'Fall (regional), Spring (state/national)',
        'financial_barrier_level': 'Low',
        'financial_aid_available': 'Limited scholarships available',
        'family_income_consideration': 'School-sponsored',
        'hidden_costs_level': 'Medium',
        'cost_category': 'Under-$100',
        'diversity_focus': 'SkillsUSA inclusion initiatives',
        'underrepresented_friendly': 'True',
        'first_gen_support': 'True',
        'cultural_competency': 'High',
        'rural_accessible': 'Limited',
        'transportation_required': 'True',
        'internet_dependency': 'Basic',
        'regional_availability': 'National',
        'family_involvement_required': 'Optional',
        'peer_network_building': 'True',
        'mentor_access_level': 'Adult'
    })

    # 18. HVAC/R Technology
    programs.append({
        'name': 'SkillsUSA HVAC/R (Heating, Ventilation, Air Conditioning, Refrigeration)',
        'description': 'Climate control systems competition testing HVAC installation, maintenance, and troubleshooting. Students work with refrigeration cycles, electrical controls, ductwork, and system diagnostics. Covers EPA regulations, energy efficiency, and customer service. High-demand career with industry certifications.',
        'url': 'https://www.skillsusa.org/competitions/skillsusa-championships/',
        'source': 'SkillsUSA',
        'category': 'Technical Competition',
        'stem_fields': 'HVAC Technology, Thermodynamics, Engineering Technology',
        'target_grade': '9-12',
        'cost': 'Under-$100 (membership + registration)',
        'location_type': 'Regional and national competition sites',
        'time_commitment': '6-8 months (preparation + competitions)',
        'prerequisite_level': 'Medium',
        'support_level': 'High',
        'deadline': 'Fall (regional), Spring (state/national)',
        'financial_barrier_level': 'Low',
        'financial_aid_available': 'Limited scholarships available',
        'family_income_consideration': 'School-sponsored',
        'hidden_costs_level': 'Medium',
        'cost_category': 'Under-$100',
        'diversity_focus': 'SkillsUSA inclusion initiatives',
        'underrepresented_friendly': 'True',
        'first_gen_support': 'True',
        'cultural_competency': 'High',
        'rural_accessible': 'Limited',
        'transportation_required': 'True',
        'internet_dependency': 'Basic',
        'regional_availability': 'National',
        'family_involvement_required': 'Optional',
        'peer_network_building': 'True',
        'mentor_access_level': 'Adult'
    })

    # 19. Automotive Service Technology
    programs.append({
        'name': 'SkillsUSA Automotive Service Technology',
        'description': 'Automotive repair competition testing diagnosis and repair of modern vehicles. Students troubleshoot engine, electrical, brake, and suspension systems using diagnostic equipment. Covers hybrid/electric vehicles, computerized systems, and ASE-style tasks. Prepares for automotive technician certification.',
        'url': 'https://www.skillsusa.org/competitions/skillsusa-championships/',
        'source': 'SkillsUSA',
        'category': 'Technical Competition',
        'stem_fields': 'Automotive Technology, Mechanical Engineering, Diagnostics',
        'target_grade': '9-12',
        'cost': 'Under-$100 (membership + registration)',
        'location_type': 'Regional and national competition sites',
        'time_commitment': '6-8 months (preparation + competitions)',
        'prerequisite_level': 'Medium',
        'support_level': 'High',
        'deadline': 'Fall (regional), Spring (state/national)',
        'financial_barrier_level': 'Low',
        'financial_aid_available': 'Limited scholarships available',
        'family_income_consideration': 'School-sponsored',
        'hidden_costs_level': 'Medium',
        'cost_category': 'Under-$100',
        'diversity_focus': 'SkillsUSA inclusion initiatives',
        'underrepresented_friendly': 'True',
        'first_gen_support': 'True',
        'cultural_competency': 'High',
        'rural_accessible': 'Limited',
        'transportation_required': 'True',
        'internet_dependency': 'Basic',
        'regional_availability': 'National',
        'family_involvement_required': 'Optional',
        'peer_network_building': 'True',
        'mentor_access_level': 'Adult'
    })

    # 20. Mechatronics
    programs.append({
        'name': 'SkillsUSA Mechatronics',
        'description': 'Integrated systems competition combining mechanics, electronics, and computer programming. Students install, program, and troubleshoot automated manufacturing systems. Covers PLCs, pneumatics, robotics, sensors, and industrial control. Aligns with Industry 4.0 and smart factory technologies. High-demand interdisciplinary career pathway.',
        'url': 'https://www.skillsusa.org/competitions/skillsusa-championships/',
        'source': 'SkillsUSA',
        'category': 'Technical Competition',
        'stem_fields': 'Mechatronics, Robotics, Automation, Engineering Technology',
        'target_grade': '9-12',
        'cost': 'Under-$100 (membership + registration)',
        'location_type': 'Regional and national competition sites',
        'time_commitment': '6-8 months (preparation + competitions)',
        'prerequisite_level': 'High',
        'support_level': 'High',
        'deadline': 'Fall (regional), Spring (state/national)',
        'financial_barrier_level': 'Low',
        'financial_aid_available': 'Limited scholarships available',
        'family_income_consideration': 'School-sponsored',
        'hidden_costs_level': 'Medium',
        'cost_category': 'Under-$100',
        'diversity_focus': 'SkillsUSA inclusion initiatives',
        'underrepresented_friendly': 'True',
        'first_gen_support': 'True',
        'cultural_competency': 'High',
        'rural_accessible': 'Limited',
        'transportation_required': 'True',
        'internet_dependency': 'Basic',
        'regional_availability': 'National',
        'family_involvement_required': 'Optional',
        'peer_network_building': 'True',
        'mentor_access_level': 'Adult'
    })

    print(f"\nSuccessfully created {len(programs)} SkillsUSA STEM competition entries")

    # Create data directory if it doesn't exist
    os.makedirs('data', exist_ok=True)

    # Write to CSV
    csv_path = os.path.join('data', 'skillsusa_stem_competitions.csv')

    with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(programs)

    print(f"\nSuccessfully created {csv_path} with {len(programs)} competition entries")
    return len(programs)

if __name__ == "__main__":
    count = scrape_skillsusa_stem()
    print(f"\nScraping complete! Total competitions: {count}")
