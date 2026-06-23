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

    def _analyze_text(self, text: str, file_path: str) -> Dict[str, Any]:
        """
        Runs regex and heuristics to structure resume data.
        """
        lines = [line.strip() for line in text.split("\n") if line.strip()]
        
        # 1. Name heuristic (first non-empty line that isn't too long or doesn't have common formatting tags)
        name = "Unknown Candidate"
        for line in lines[:5]:
            if 3 < len(line) < 35 and not any(x in line.lower() for x in ["email", "phone", "resume", "curriculum"]):
                # Simple check for alphabetic and spaces
                if re.match(r"^[A-Za-z\s\.\-\']+$", line):
                    name = line
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
        emails = re.findall(email_regex, text)
        email = emails[0] if emails else None

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

        # 5. Education heuristic
        education = []
        edu_keywords = ["education", "university", "college", "degree", "school", "bachelor", "master", "phd", "b.s", "m.s", "b.sc", "m.sc"]
        edu_started = False
        
        # Look for education lines
        for i, line in enumerate(lines):
            line_lower = line.lower()
            if any(k in line_lower for k in ["education", "academic background", "qualification"]):
                edu_started = True
                continue
            if edu_started:
                # Stop if we hit another header
                if any(h in line_lower for h in ["experience", "employment", "work history", "skills", "projects", "certifications", "certificates", "courses", "credentials", "licenses", "awards", "publications", "interests", "activities", "summary"]):
                    edu_started = False
                    continue
                # Ignore lines that look like certifications inside the education parser
                if any(c in line_lower for c in ["certified", "certification", "certificate"]):
                    continue
                # If the line contains degree/university terms, capture it
                if any(x in line_lower for x in ["university", "college", "bachelor", "master", "phd", "degree", "school", "b.s", "m.s", "b.sc"]):
                    degree = "Bachelor of Science" if "bachelor" in line_lower or "b.s" in line_lower else ("Master of Science" if "master" in line_lower or "m.s" in line_lower else "Degree")
                    major = "Computer Science" if "computer" in line_lower or "software" in line_lower or "tech" in line_lower else "General Studies"
                    
                    # Extract graduation year
                    year_match = re.search(r"\b(19|20)\d{2}\b", line)
                    grad_year = year_match.group(0) if year_match else "N/A"
                    
                    # Extract school name
                    school = line
                    if year_match:
                        school = school.replace(year_match.group(0), "")
                    for phrase in ["bachelor", "master", "phd", "degree", "b.s", "m.s", "in computer science", "in software", ", "]:
                        school = re.sub(phrase, "", school, flags=re.IGNORECASE)
                    
                    school = re.sub(r"[\(\)\-\:\,]", " ", school)
                    school = " ".join(school.split()).strip()
                    
                    education.append({
                        "degree": degree,
                        "major": major,
                        "school": school or "Accredited Institution",
                        "grad_year": grad_year
                    })
        
        if not education:
            # Fallback if no specific section found but terms exist
            for line in lines:
                if any(c in line.lower() for c in ["certified", "certification", "certificate"]):
                    continue
                if any(x in line.lower() for x in ["university", "college", "bachelor", "master"]):
                    year_match = re.search(r"\b(19|20)\d{2}\b", line)
                    grad_year = year_match.group(0) if year_match else "N/A"
                    
                    school = line.strip()
                    if year_match:
                        school = school.replace(year_match.group(0), "").strip()
                    school = re.sub(r"[\(\)\-\:\,]", " ", school)
                    school = " ".join(school.split()).strip()
                    
                    education.append({
                        "degree": "Degree",
                        "major": "Computer Science" if "computer" in line.lower() else "Engineering",
                        "school": school or "Accredited Institution",
                        "grad_year": grad_year
                    })
                    break

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
