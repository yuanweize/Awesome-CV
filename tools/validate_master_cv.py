#!/usr/bin/env python3
"""
Master CV Validator & Schema Checker for Awesome-CV
Ensures `meta/master_cv.yaml` is valid YAML, contains all required fields,
and maintains data integrity across education, work experience, and skills.
"""

import os
import sys
import yaml

def validate_master_cv(yaml_path):
    print(f"🔍 Validating Master CV database: {yaml_path}")
    
    if not os.path.exists(yaml_path):
        print(f"❌ ERROR: File not found at {yaml_path}")
        return False
        
    try:
        with open(yaml_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
    except Exception as e:
        print(f"❌ ERROR: Invalid YAML syntax: {e}")
        return False
        
    errors = []
    warnings = []
    
    # Required top-level keys
    required_keys = ['personal_information', 'education', 'work_experience', 'technical_skills', 'languages']
    for key in required_keys:
        if key not in data:
            errors.append(f"Missing required top-level section: '{key}'")
            
    if errors:
        for err in errors:
            print(f"❌ {err}")
        return False
        
    # Check personal info
    pi = data.get('personal_information', {})
    for field in ['full_name', 'email', 'location', 'citizenship']:
        if not pi.get(field):
            errors.append(f"Personal information missing field: '{field}'")
            
    # Check education
    edu = data.get('education', {})
    if not edu.get('institution') or not edu.get('degree'):
        errors.append("Education section missing institution or degree")
    if not edu.get('bachelor_thesis', {}).get('title'):
        warnings.append("Bachelor thesis title is empty or missing")
        
    # Check work experience
    exp = data.get('work_experience', [])
    if not isinstance(exp, list) or len(exp) == 0:
        errors.append("Work experience must be a non-empty list")
    else:
        for i, item in enumerate(exp):
            if not item.get('company') or not item.get('dates'):
                errors.append(f"Work experience item #{i+1} missing company or dates")
                
    # Check skills
    skills = data.get('technical_skills', {})
    if not isinstance(skills, dict) or len(skills) == 0:
        errors.append("Technical skills section must be a non-empty object")
        
    # Summary report
    if warnings:
        for w in warnings:
            print(f"⚠️  WARNING: {w}")
            
    if errors:
        for err in errors:
            print(f"❌ ERROR: {err}")
        return False
        
    print("✅ SUCCESS: Master CV (`master_cv.yaml`) passed all validation checks!")
    print(f"   • Personal Name: {pi.get('full_name')}")
    print(f"   • Education: {edu.get('degree')} at {edu.get('institution')}")
    print(f"   • Work Entries: {len(exp)} major employers/contracts")
    certs = data.get('certifications_and_qualifications', [])
    honors = data.get('honors_and_achievements', [])
    print(f"   • Certifications: {len(certs)}")
    print(f"   • Honors & Awards: {len(honors)}")
    if pi.get('driving_license'):
        print(f"   • Driving License: {pi.get('driving_license')}")
    return True

if __name__ == '__main__':
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    default_yaml = os.path.join(project_root, 'meta', 'master_cv.yaml')
    
    yaml_file = sys.argv[1] if len(sys.argv) > 1 else default_yaml
    success = validate_master_cv(yaml_file)
    sys.exit(0 if success else 1)
