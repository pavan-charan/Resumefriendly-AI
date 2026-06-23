import re
import os
from typing import Dict, List, Any
import pypdf
import docx

class ParserService:
    # Common industry skills list
    SKILLS_DATABASE = [
        "Python", "FastAPI", "React", "TypeScript", "JavaScript", "HTML", "CSS", "Tailwind", 
        "SQL", "PostgreSQL", "MongoDB", "Docker", "Kubernetes", "AWS", "GCP", "Git", "GitHub", 
        "Java", "C++", "C#", "Go", "Rust", "Node.js", "Express", "Next.js", "Django", "Flask", 
        "GraphQL", "Redux", "CI/CD", "Machine Learning", "AI", "NLP", "ChromaDB", "Linux", 
        "Scrum", "Agile", "PyTorch", "TensorFlow", "Pandas", "NumPy", "Jira", "Figma", "Firebase"
    ]

    def parse_file(self, file_path: str) -> Dict[str, Any]:
        """
        Determines file extension and extracts text.
        Then extracts key fields: name, contact, skills, education, and experience.
        """
        ext = os.path.splitext(file_path)[1].lower()
        raw_text = ""
        
        if ext == ".pdf":
            raw_text = self._extract_text_from_pdf(file_path)
        elif ext == ".docx":
            raw_text = self._extract_text_from_docx(file_path)
        else:
            raise ValueError("Unsupported file format. Please upload PDF or DOCX.")
            
        return {
            "raw_text": raw_text,
            "parsed_content": self._analyze_text(raw_text, file_path)
        }

    def _extract_text_from_pdf(self, file_path: str) -> str:
        text = ""
        try:
            reader = pypdf.PdfReader(file_path)
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        except Exception as e:
            text = f"Error reading PDF: {str(e)}"
        return text

    def _extract_text_from_docx(self, file_path: str) -> str:
        text = ""
        try:
            doc = docx.Document(file_path)
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
        except Exception as e:
            text = f"Error reading DOCX: {str(e)}"
        return text

    def _is_education_line(self, line: str) -> bool:
        line_lower = line.lower()
        # Look for indicators of colleges, universities, or training institutes
        has_inst = any(x in line_lower for x in ["university", "college", "institute", "school", "academy", "iit", "iiit", "bits", "nit", "learning center", "training center", "coursera", "udemy", "simplilearn", "udacity"])
        # Look for degree, diploma, course, or certification keywords
        has_deg = any(x in line_lower for x in ["bachelor", "master", "phd", "degree", "diploma", "course", "b.tech", "m.tech", "bca", "mca", "mba", "pgdm", "certifications", "certificate"])
        # Look for passout/graduation year (4 digit year)
        years = re.findall(r"\b(?:19|20)\d{2}\b", line)
        has_year = len(years) > 0
        
        # Capture as education if it mentions an institute and either a course/degree or a year
        # Or if it explicitly mentions a standard tech degree (b.tech/mca/mba/etc) alongside a year
        if (has_inst and (has_deg or has_year)) or (any(d in line_lower for d in ["b.tech", "m.tech", "bca", "mca", "mba", "pgdm"]) and has_year):
            return True
        return False

    def _analyze_text(self, text: str, file_path: str) -> Dict[str, Any]:
        """
        Runs regex and heuristics to structure resume data.
        """
        lines = [line.strip() for line in text.split("\n") if line.strip()]
        
        # 1. Name heuristic (first non-empty line that isn't too long or doesn't have common formatting tags/job titles)
        name = "Unknown Candidate"
        title_keywords = ["engineer", "developer", "architect", "manager", "lead", "consultant", "analyst", "specialist", "designer", "programmer", "intern", "student", "professional", "resume", "cv", "vitae", "portfolio", "page", "summary", "profile", "contact", "about", "experience", "education", "skills"]
        for line in lines[:8]:
            line_clean = line.strip()
            line_lower = line_clean.lower()
            if (3 < len(line_clean) < 35 
                and not any(x in line_lower for x in ["email", "phone", "resume", "curriculum", "page", "contact"])
                and not any(r == line_lower or f" {r}" in line_lower or f"{r} " in line_lower for r in title_keywords)
                and re.match(r"^[A-Za-z\s\.\-\']+$", line_clean)):
                name = line_clean
                break
        
        # Fallback name from file_path if name extraction resolves to Unknown
        if name == "Unknown Candidate" and file_path:
            base = os.path.basename(file_path)
            clean_base = os.path.splitext(base)[0].replace("_", " ").replace("-", " ")
            # strip trailing UUID if any
            clean_base = re.sub(r"[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}", "", clean_base).strip()
            if clean_base:
                name = clean_base

        # 2. Email parsing
        email_regex = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
        emails_found = re.findall(email_regex, text)
        filtered_emails = []
        for e in emails_found:
            e_lower = e.lower()
            # Skip system/tool/github/placeholder emails
            if any(x in e_lower for x in ["git@github", "info@", "support@", "sales@", "contact@", "jobs@", "careers@", "noreply@", "example.com"]):
                continue
            # Skip package version false positives (having numbers in domain or after domain dot)
            if re.search(r"@\d", e) or re.search(r"\.\d", e):
                continue
            filtered_emails.append(e)
            
        email = None
        if filtered_emails:
            # Prioritize email found in the first 15 lines of text
            first_lines_text = "\n".join(lines[:15]).lower()
            for fe in filtered_emails:
                if fe.lower() in first_lines_text:
                    email = fe
                    break
            if not email:
                email = filtered_emails[0]

        # 3. Phone parsing
        phone_regex = r"(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}"
        phones = re.findall(phone_regex, text)
        phone = phones[0] if phones else None

        # 4. Skills extraction
        skills_matched = []
        for skill in self.SKILLS_DATABASE:
            # Match word boundary to avoid substrings (e.g., 'Go' in 'Google')
            pattern = r"\b" + re.escape(skill) + r"\b"
            if re.search(pattern, text, re.IGNORECASE):
                skills_matched.append(skill)

        # 5. Education heuristic (scan globally to capture formal degrees, diplomas, and courses from colleges/institutes)
        education = []
        for line in lines:
            if self._is_education_line(line):
                line_lower = line.lower()
                degree = "Degree"
                if "bachelor" in line_lower or "b.s" in line_lower or "b.tech" in line_lower or "bca" in line_lower:
                    degree = "Bachelor's Degree"
                elif "master" in line_lower or "m.s" in line_lower or "m.tech" in line_lower or "mca" in line_lower or "mba" in line_lower:
                    degree = "Master's Degree"
                elif "diploma" in line_lower or "pgdm" in line_lower:
                    degree = "Diploma"
                elif "phd" in line_lower:
                    degree = "PhD"
                elif "course" in line_lower or "certification" in line_lower or "certificate" in line_lower:
                    degree = "Course / Certification"

                # Major/Specialization heuristic
                major = "General Studies"
                if "computer" in line_lower or "software" in line_lower or "tech" in line_lower or "it " in line_lower or "information technology" in line_lower:
                    major = "Computer Science / IT"
                elif "engineering" in line_lower:
                    major = "Engineering"
                elif "data science" in line_lower or "analytics" in line_lower:
                    major = "Data Science"
                elif "business" in line_lower or "management" in line_lower or "mba" in line_lower:
                    major = "Business Administration"

                # Extract years: first is start date, second is end date. If only one is present, it is end date.
                years = re.findall(r"\b(?:19|20)\d{2}\b", line)
                graduation_start_year = "N/A"
                graduation_end_year = "N/A"
                grad_year = "N/A"
                
                if len(years) >= 2:
                    sorted_years = sorted([int(y) for y in years[:2]])
                    graduation_start_year = str(sorted_years[0])
                    graduation_end_year = str(sorted_years[1])
                    grad_year = str(sorted_years[1])
                elif len(years) == 1:
                    graduation_end_year = years[0]
                    grad_year = years[0]

                # Extract and clean school/center name
                school = line
                for y in years:
                    school = school.replace(y, "")
                
                # Replace common punctuation with spaces to avoid words joining together
                school = re.sub(r"[\(\)\-\:\,]", " ", school)
                
                for phrase in [
                    "bachelor", "master", "phd", "degree", "diploma", "course", "b.s", "m.s", "b.tech", "m.tech", "bca", "mca", "mba", "pgdm", "in computer science", "in software", "in engineering", "from", "at",
                    "january", "february", "march", "april", "may", "june", "july", "august", "september", "october", "november", "december",
                    "jan", "feb", "mar", "apr", "jun", "jul", "aug", "sep", "sept", "oct", "nov", "dec"
                ]:
                    school = re.sub(r"\b" + re.escape(phrase) + r"\b", "", school, flags=re.IGNORECASE)
                
                school = " ".join(school.split()).strip()

                # Add to list and de-duplicate by school/center name and degree
                if school and not any(e["school"].lower() == school.lower() and e["degree"].lower() == degree.lower() for e in education):
                    education.append({
                        "degree": degree,
                        "major": major,
                        "school": school or "Accredited Institution/Center",
                        "grad_year": grad_year,
                        "graduation_start_year": graduation_start_year,
                        "graduation_end_year": graduation_end_year
                    })
        
        # Fallback default if no education lines parsed
        if not education:
            education.append({
                "degree": "Degree",
                "major": "Computer Science / Engineering",
                "school": "Accredited University / Institute",
                "grad_year": "N/A",
                "graduation_start_year": "N/A",
                "graduation_end_year": "N/A"
            })

        # 6. Experience heuristic
        experience = []
        exp_keywords = ["experience", "employment", "work history", "work experience", "career history"]
        exp_started = False
        current_exp = None

        for i, line in enumerate(lines):
            line_lower = line.lower()
            if any(k == line_lower or k in line_lower for k in exp_keywords) and len(line) < 25:
                exp_started = True
                continue
            if exp_started:
                if any(h in line_lower for h in ["education", "skills", "projects", "certifications", "interests"]):
                    exp_started = False
                    if current_exp:
                        experience.append(current_exp)
                        current_exp = None
                    continue
                
                # Check for role/company formatting e.g., "Software Engineer at Tech Corp" or date ranges
                # Date ranges like "2022 - Present", "2020 - 2022", "Jan 2021"
                has_date = re.search(r"\b(19|20)\d{2}\b", line) or "present" in line_lower
                
                if has_date and (len(line) < 80) and (not current_exp or len(current_exp["description"]) > 10):
                    if current_exp:
                        experience.append(current_exp)
                    
                    role = line
                    company = "Innovative Software LLC"
                    duration = "2-5 Years"
                    
                    # Try to separate company, role, duration
                    duration_match = re.search(r"\b(19|20)\d{2}.*", line)
                    if duration_match:
                        duration = duration_match.group(0)
                        role = line.replace(duration, "").strip()
                    
                    parts = re.split(r"\bat\b|\bat\s+the\b|,\s*", role, flags=re.IGNORECASE)
                    if len(parts) > 1:
                        role = parts[0].strip()
                        company = parts[1].strip()
                    
                    current_exp = {
                        "role": role,
                        "company": company,
                        "duration": duration,
                        "description": ""
                    }
                elif current_exp:
                    current_exp["description"] += line + " "

        if current_exp:
            experience.append(current_exp)
            
        # Clean experience descriptions
        for exp in experience:
            exp["description"] = exp["description"].strip()
            # Truncate descriptions if too long
            if len(exp["description"]) > 400:
                exp["description"] = exp["description"][:397] + "..."

        # If no experience found, add a placeholder
        if not experience:
            experience.append({
                "role": "Professional Consultant / Specialist",
                "company": "Enterprise Corporation",
                "duration": "1-3 Years",
                "description": "General professional duties and contributions matching skills profile."
            })

        # 7. Projects heuristic
        projects = []
        proj_started = False
        for line in lines:
            line_lower = line.lower()
            if any(k in line_lower for k in ["projects", "personal projects", "portfolio"]):
                proj_started = True
                continue
            if proj_started:
                if any(h in line_lower for h in ["experience", "education", "skills", "certifications"]):
                    proj_started = False
                    continue
                if len(line) > 10 and len(line) < 150:
                    projects.append(line.strip())
                    if len(projects) >= 5:
                        proj_started = False

        # 8. Certifications heuristic
        certifications = []
        cert_started = False
        for line in lines:
            line_lower = line.lower()
            if any(k in line_lower for k in ["certifications", "certificates", "courses", "credentials", "licenses"]):
                cert_started = True
                continue
            if cert_started:
                if any(h in line_lower for h in ["experience", "education", "skills", "projects"]):
                    cert_started = False
                    continue
                # Skip any lines that represent formal education or courses from colleges/institutes
                if self._is_education_line(line):
                    continue
                if len(line) > 5 and len(line) < 100:
                    certifications.append(line.strip())
                    if len(certifications) >= 5:
                        cert_started = False

        return {
            "name": name,
            "email": email,
            "phone": phone,
            "skills": skills_matched,
            "experience": experience,
            "education": education,
            "projects": projects,
            "certifications": certifications
        }
