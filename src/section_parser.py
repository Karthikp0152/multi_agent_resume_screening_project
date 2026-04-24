"""
Section Parser component for the Smart Resume Screening System.

This module provides pattern-based section detection to divide resume text
into logical sections (Skills, Experience, Education, Projects).
"""

import re
from typing import Dict, List
from src.models import ResumeSections


class SectionParser:
    """Parser for identifying and extracting resume sections using regex patterns.
    
    This class uses case-insensitive regex patterns to detect common section headers
    in resumes and extract the content of each section.
    
    Attributes:
        section_patterns: Dictionary mapping section names to compiled regex patterns
    """
    
    def __init__(self, section_patterns: Dict[str, List[str]] = None):
        """Initialize SectionParser with regex patterns for section headers.
        
        Args:
            section_patterns: Optional dictionary mapping section names to lists of
                            regex pattern strings. If not provided, uses default patterns.
        """
        if section_patterns is None:
            # Default patterns for common resume sections
            section_patterns = {
                'skills': [r"(?i)(skills?|technical skills?|core competencies)"],
                'experience': [r"(?i)(experience|work history|employment)"],
                'education': [r"(?i)(education|academic background|qualifications)"],
                'projects': [r"(?i)(projects?|portfolio)"]
            }
        
        # Compile regex patterns for efficiency
        self.section_patterns: Dict[str, List[re.Pattern]] = {}
        for section_name, patterns in section_patterns.items():
            self.section_patterns[section_name] = [
                re.compile(pattern) for pattern in patterns
            ]
    
    def parse_sections(self, text: str) -> ResumeSections:
        """Identify and extract all resume sections from text.
        
        This method scans the resume text for section headers and extracts the content
        between headers. If a section is not found, an empty string is returned for that section.
        
        Args:
            text: Complete resume text to parse
            
        Returns:
            ResumeSections dataclass with all parsed sections
        """
        # Extract each section
        skills = self.extract_section(text, 'skills')
        experience = self.extract_section(text, 'experience')
        education = self.extract_section(text, 'education')
        projects = self.extract_section(text, 'projects')
        
        return ResumeSections(
            skills=skills,
            experience=experience,
            education=education,
            projects=projects,
            raw_text=text
        )
    
    def extract_section(self, text: str, section_name: str) -> str:
        """Extract a specific section by name from resume text.
        
        This method searches for the section header using the configured patterns,
        then extracts all text from the header until the next section header or end of text.
        
        Args:
            text: Complete resume text
            section_name: Name of the section to extract (e.g., 'skills', 'experience')
            
        Returns:
            Extracted section content as a string, or empty string if section not found
        """
        if section_name not in self.section_patterns:
            return ""
        
        # Find the section header
        section_start = None
        matched_pattern = None
        
        for pattern in self.section_patterns[section_name]:
            match = pattern.search(text)
            if match:
                section_start = match.end()
                matched_pattern = pattern
                break
        
        # If section not found, return empty string
        if section_start is None:
            return ""
        
        # Find the end of this section (start of next section or end of text)
        # Look for any other section header after the current section
        section_end = len(text)
        
        # Collect all patterns from all sections
        all_patterns = []
        for patterns in self.section_patterns.values():
            all_patterns.extend(patterns)
        
        # Find the nearest section header after the current section start
        for pattern in all_patterns:
            # Search for next occurrence after the current section
            for match in pattern.finditer(text):
                if match.start() > section_start:
                    # Found a section header after current section
                    if match.start() < section_end:
                        section_end = match.start()
                    break
        
        # Extract and clean the section content
        section_content = text[section_start:section_end].strip()
        
        return section_content
