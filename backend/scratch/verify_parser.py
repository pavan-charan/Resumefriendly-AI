import sys
import os

# Append workspace path to system import search
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.dirname(current_dir)
sys.path.append(backend_dir)

def verify_parser_rules():
    from app.services.parser_service import ParserService
    
    parser = ParserService()
    
    # Test resume text with education, certifications, job titles in header, and package versions
    test_text = """
Senior Software Engineer
Pavan Charan
pavan.charan@gmail.com
Phone: +91 9999988888

ABOUT
Experienced engineer. Uses react@18.2.0, next@14.0.0. Contact us at info@resumefriendly.com.

EDUCATION
B.Tech in Computer Science from NIT Trichy (July 2017 - August 2021)

CERTIFICATIONS & COURSES
PG Diploma in AI, IIT Delhi, October 2022
Machine Learning, Coursera, May 2020
AWS Certified Solutions Architect (Jan 2023)
Certified Kubernetes Administrator (CKA)
"""
    
    result = parser._analyze_text(test_text, "test_resume.pdf")
    
    print("\n--- Extracted Education ---")
    for edu in result["education"]:
        print(f"Degree: {edu['degree']}")
        print(f"School: {edu['school']}")
        print(f"Start Year: {edu.get('graduation_start_year')}")
        print(f"End Year: {edu.get('graduation_end_year')}")
        print(f"Grad Year: {edu.get('grad_year')}")
        print("-" * 30)

    print("\n--- Extracted Certifications ---")
    for cert in result["certifications"]:
        print(f"- {cert}")

    # Assertions
    # 0. Name and Email Extraction Accuracy
    assert result["name"] == "Pavan Charan", f"Expected name 'Pavan Charan', got '{result['name']}'"
    assert result["email"] == "pavan.charan@gmail.com", f"Expected email 'pavan.charan@gmail.com', got '{result['email']}'"

    # 1. NIT Trichy: start 2017, end 2021
    nit_entry = next((e for e in result["education"] if "nit" in e["school"].lower()), None)
    assert nit_entry is not None, "NIT Trichy education entry missing"
    assert nit_entry["graduation_start_year"] == "2017", f"Expected 2017 start year, got {nit_entry['graduation_start_year']}"
    assert nit_entry["graduation_end_year"] == "2021", f"Expected 2021 end year, got {nit_entry['graduation_end_year']}"

    # 2. PG Diploma: end 2022, start N/A
    pg_entry = next((e for e in result["education"] if "iit" in e["school"].lower()), None)
    assert pg_entry is not None, "IIT Delhi PG Diploma education entry missing"
    assert pg_entry["graduation_start_year"] == "N/A", f"Expected N/A start year, got {pg_entry['graduation_start_year']}"
    assert pg_entry["graduation_end_year"] == "2022", f"Expected 2022 end year, got {pg_entry['graduation_end_year']}"

    # 3. Coursera: end 2020, start N/A
    coursera_entry = next((e for e in result["education"] if "coursera" in e["school"].lower()), None)
    assert coursera_entry is not None, "Coursera education entry missing"
    assert coursera_entry["graduation_start_year"] == "N/A"
    assert coursera_entry["graduation_end_year"] == "2020"

    # 4. Certifications should NOT contain:
    # - "PG Diploma in AI, IIT Delhi, 2022"
    # - "Machine Learning, Coursera, 2020"
    for cert in result["certifications"]:
        assert "iit" not in cert.lower() and "delhi" not in cert.lower(), f"Certifications contain college entry: {cert}"
        assert "coursera" not in cert.lower(), f"Certifications contain online training center: {cert}"

    # 5. Certifications SHOULD contain:
    # - "AWS Certified Solutions Architect (2023)"
    # - "Certified Kubernetes Administrator (CKA)"
    cert_texts = [c.lower() for c in result["certifications"]]
    assert any("aws" in c for c in cert_texts), "AWS certification missing from certifications"
    assert any("kubernetes" in c for c in cert_texts), "Kubernetes certification missing from certifications"

    print("\n[SUCCESS] All parsing rules and assertions passed successfully!")
    return True

if __name__ == "__main__":
    try:
        success = verify_parser_rules()
        sys.exit(0 if success else 1)
    except Exception as e:
        import traceback
        traceback.print_exc()
        sys.exit(1)
