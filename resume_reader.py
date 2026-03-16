#!/usr/bin/env python3
"""
Resume Reader Module
Extracts keywords and skills from resume PDF for job matching
"""

import re
import os
from typing import List, Dict, Set
from PyPDF2 import PdfReader
from utils.logger import setup_logger
from config import RESUME_FILE_PATH

logger = setup_logger(__name__)


class ResumeReader:
    """Extracts keywords and skills from resume PDF"""

    def __init__(self):
        self.resume_path = RESUME_FILE_PATH

    def extract_text_from_pdf(self) -> str:
        """
        Extract text content from PDF resume

        Returns:
            str: Extracted text from PDF
        """
        try:
            if not os.path.exists(self.resume_path):
                logger.error(f"Resume file not found: {self.resume_path}")
                return ""

            logger.info(f"Reading resume from: {self.resume_path}")

            reader = PdfReader(self.resume_path)
            text = ""

            for page in reader.pages:
                text += page.extract_text() + "\n"

            logger.info(f"Extracted {len(text)} characters from resume")
            return text

        except Exception as e:
            logger.error(f"Error reading PDF: {str(e)}")
            return ""

    def extract_skills_keywords(self, text: str) -> Set[str]:
        """
        Extract technical skills and keywords from resume text

        Args:
            text: Resume text content

        Returns:
            Set of extracted skills/keywords
        """
        skills = set()
        text_lower = text.lower()

        # Common technical skills patterns (case-insensitive)
        tech_skills = [
            # Programming Languages
            r'\b(python|java|javascript|typescript|c\+\+|c#|php|ruby|go|golang|rust|swift|kotlin|scala|perl|r|matlab)\b',

            # Web Technologies
            r'\b(html|css|react|angular|vue|node\.js|express|django|flask|spring|hibernate|jquery|bootstrap|sass|less)\b',

            # Databases
            r'\b(sql|mysql|postgresql|mongodb|oracle|cassandra|redis|elasticsearch|dynamodb|sqlite|firebase)\b',

            # Cloud Platforms
            r'\b(aws|azure|gcp|google cloud|heroku|digitalocean|linode|cloudflare)\b',

            # DevOps/Tools
            r'\b(docker|kubernetes|jenkins|gitlab|github|bitbucket|terraform|ansible|puppet|chef|nginx|apache)\b',

            # Data Science/ML
            r'\b(machine learning|deep learning|artificial intelligence|ai|data science|pandas|numpy|scikit-learn|tensorflow|keras|pytorch|jupyter|tableau|power bi)\b',

            # Testing
            r'\b(selenium|junit|testng|pytest|cucumber|postman|jmeter|loadrunner|appium)\b',

            # Version Control
            r'\b(git|svn|mercurial|perforce)\b',

            # Operating Systems
            r'\b(linux|ubuntu|centos|redhat|windows|macos|unix)\b',

            # Frameworks/Libraries
            r'\b(hadoop|spark|kafka|airflow|apache spark|hive|pig|flume|sqoop)\b',

            # ServiceNow specific
            r'\b(servicenow|itsm|itil|csm|ppm|change management|incident management|problem management|sla|knowledge management)\b',

            # Process Management
            r'\b(agile|scrum|kanban|waterfall|lean|six sigma|itil|iso|cobit)\b'
        ]

        # Extract skills using regex patterns
        for pattern in tech_skills:
            matches = re.findall(pattern, text_lower)
            skills.update(matches)

        # Extract from skills section specifically
        skills_section_patterns = [
            r'key skills & tools?:?(.*?)(?:professional experience|training|certifications|$)',
            r'skills?(?:\s*:|\n)(.*?)(?:\n\n|\n[A-Z]|professional experience|$)',
            r'technical skills?(?:\s*:|\n)(.*?)(?:\n\n|\n[A-Z]|professional experience|$)'
        ]

        for pattern in skills_section_patterns:
            match = re.search(pattern, text_lower, re.DOTALL)
            if match:
                section_text = match.group(1)
                logger.info(f"Found skills section: {section_text[:200]}...")

                # Extract bullet points and clean text
                bullets = re.findall(r'●\s*([^●\n]+)', section_text)
                for bullet in bullets:
                    bullet = bullet.strip()
                    if bullet:
                        # Clean up the bullet text
                        clean_bullet = re.sub(r'[^\w\s]', '', bullet).strip()
                        if len(clean_bullet) > 2:
                            skills.add(clean_bullet.lower())

        # Extract from experience sections
        experience_patterns = [
            r'(?:technology|technical)\s+process\s+specialist',
            r'sr\s+analyst',
            r'process\s+analyst',
            r'servicenow\s+administrator',
            r'itsm\s+administrator'
        ]

        for pattern in experience_patterns:
            if re.search(pattern, text_lower):
                skills.add(pattern.replace(r'\s+', ' '))

        # Manual addition of key skills found in the resume
        manual_skills = [
            'servicenow', 'itsm', 'itil', 'sla', 'knowledge management',
            'incident management', 'change management', 'service catalog',
            'business rules', 'client scripts', 'workflows', 'update sets',
            'user administration', 'access control'
        ]

        skills.update(manual_skills)

        logger.info(f"Extracted {len(skills)} unique skills/keywords: {list(skills)[:10]}...")
        return skills

    def extract_experience_years(self, text: str) -> int:
        """
        Extract years of experience from resume

        Args:
            text: Resume text content

        Returns:
            int: Years of experience
        """
        # Look for experience patterns
        experience_patterns = [
            r'(\d+)\+?\s*years?\s*(?:of\s*)?experience',
            r'experience\s*:\s*(\d+)\+?\s*years?',
            r'(\d+)\+?\s*years?\s*in\s*',
            r'total\s*experience\s*:\s*(\d+)\+?\s*years?'
        ]

        for pattern in experience_patterns:
            match = re.search(pattern, text.lower())
            if match:
                years = int(match.group(1))
                logger.info(f"Extracted {years} years of experience")
                return years

        # Default to 3 years if not found
        logger.info("Could not extract experience years, defaulting to 3")
        return 3

    def extract_job_titles(self, text: str) -> List[str]:
        """
        Extract job titles/roles from resume

        Args:
            text: Resume text content

        Returns:
            List of job titles
        """
        job_titles = []

        # Common job title patterns for this resume
        title_patterns = [
            r'(?:technology|technical)\s+process\s+specialist',
            r'sr\s+analyst',
            r'process\s+analyst',
            r'servicenow\s+itsm\s+administrator',
            r'servicenow\s+administrator'
        ]

        text_lower = text.lower()
        for pattern in title_patterns:
            if re.search(pattern, text_lower):
                # Clean up the title
                title = pattern.replace(r'\s+', ' ')
                job_titles.append(title.title())  # Title case

        # Also extract from the title field
        title_match = re.search(r'title:\s*([^\n]+)', text, re.IGNORECASE)
        if title_match:
            title = title_match.group(1).strip()
            job_titles.append(title)

        # Extract from professional experience section
        exp_pattern = r'(\w+(?:\s+\w+)*?)(?:\s*\||\s*infosys|\s*capgemini)'
        exp_matches = re.findall(exp_pattern, text, re.IGNORECASE)
        for match in exp_matches:
            match = match.strip()
            if len(match) > 3 and len(match) < 50:
                job_titles.append(match.title())

        # Remove duplicates
        unique_titles = list(set(job_titles))

        logger.info(f"Extracted {len(unique_titles)} job titles: {unique_titles}")
        return unique_titles

    def generate_job_search_keywords(self) -> List[str]:
        """
        Generate comprehensive job search keywords focused on ServiceNow Administrator

        Returns:
            List of search keywords/phrases
        """
        text = self.extract_text_from_pdf()
        if not text:
            return ["servicenow administrator", "itsm administrator", "servicenow developer"]

        skills = self.extract_skills_keywords(text)
        experience_years = self.extract_experience_years(text)

        # ServiceNow-specific search keywords
        servicenow_keywords = [
            # Core ServiceNow roles
            "servicenow administrator",
            "servicenow developer",
            "servicenow consultant",
            "itsm administrator",
            "servicenow itsm",
            "servicenow system administrator",

            # Specific modules from resume
            "servicenow incident management",
            "servicenow change management",
            "servicenow service catalog",
            "servicenow sla",
            "servicenow workflows",
            "servicenow business rules",

            # Technical skills
            "servicenow user administration",
            "servicenow access control",
            "servicenow update sets",
            "servicenow client scripts",

            # Certifications and processes
            "servicenow itil",
            "servicenow certified system administrator",
            "servicenow csa",

            # Experience levels
            f"servicenow administrator {experience_years}+ years experience",
            f"itsm administrator {experience_years}+ years",

            # Location-based (common tech hubs)
            "servicenow administrator mumbai",
            "servicenow administrator pune",
            "servicenow administrator bangalore",
            "servicenow administrator hyderabad",
            "servicenow administrator chennai",
            "servicenow administrator delhi",

            # Company types
            "servicenow administrator infosys",
            "servicenow administrator capgemini",
            "servicenow administrator tcs",
            "servicenow administrator accenture"
        ]

        # Filter keywords based on resume content
        relevant_keywords = []

        # Always include core ServiceNow keywords
        core_keywords = [
            "servicenow administrator",
            "itsm administrator",
            "servicenow developer",
            "servicenow consultant"
        ]
        relevant_keywords.extend(core_keywords)

        # Add module-specific keywords if mentioned in resume
        module_keywords = {
            "incident management": "servicenow incident management",
            "change management": "servicenow change management",
            "service catalog": "servicenow service catalog",
            "sla": "servicenow sla",
            "workflows": "servicenow workflows",
            "business rules": "servicenow business rules",
            "user administration": "servicenow user administration",
            "access control": "servicenow access control"
        }

        for skill, keyword in module_keywords.items():
            if skill in skills or skill.replace(" ", "") in text.lower():
                relevant_keywords.append(keyword)

        # Add experience-based keywords
        if experience_years >= 3:
            relevant_keywords.append(f"servicenow administrator {experience_years}+ years")
            relevant_keywords.append(f"experienced servicenow administrator")

        # Add location-based keywords (top 3 cities)
        top_cities = ["mumbai", "pune", "bangalore"]
        for city in top_cities:
            relevant_keywords.append(f"servicenow administrator {city}")

        # Remove duplicates
        unique_keywords = list(set(relevant_keywords))

        logger.info(f"Generated {len(unique_keywords)} ServiceNow-focused search keywords")
        return unique_keywords[:25]  # Limit to top 25 most relevant

    def get_resume_summary(self) -> Dict:
        """
        Get comprehensive resume summary

        Returns:
            Dict with resume information
        """
        text = self.extract_text_from_pdf()

        return {
            'skills': list(self.extract_skills_keywords(text)),
            'experience_years': self.extract_experience_years(text),
            'job_titles': self.extract_job_titles(text),
            'search_keywords': self.generate_job_search_keywords(),
            'text_length': len(text)
        }


if __name__ == "__main__":
    # Test the resume reader
    reader = ResumeReader()
    summary = reader.get_resume_summary()

    print("=== Resume Analysis ===")
    print(f"Experience: {summary['experience_years']} years")
    print(f"Skills Found: {len(summary['skills'])}")
    print(f"Job Titles: {summary['job_titles']}")
    print(f"Search Keywords: {len(summary['search_keywords'])}")
    print("\nTop Skills:")
    for skill in summary['skills'][:10]:
        print(f"  - {skill}")
    print("\nTop Search Keywords:")
    for keyword in summary['search_keywords'][:10]:
        print(f"  - {keyword}")