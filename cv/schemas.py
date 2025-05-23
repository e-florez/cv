from pydantic import BaseModel, EmailStr, HttpUrl, validator, PydanticValueError
from typing import Optional, List, Dict
from datetime import datetime
import re

# Custom error for date format
class InvalidDateFormatError(PydanticValueError):
    code = 'date.invalid_format'
    msg_template = 'Invalid date format for {field_name}: "{value}". Must be "MMM YYYY" (e.g., "Aug 2021").'

def validate_month_year_date(value: Optional[str], field_name: str) -> Optional[str]:
    if value is None: # Allow optional fields to be None
        return value
    # Regex to match "MMM YYYY" format, e.g., "Aug 2021", "Dec 2023"
    if not re.match(r"^(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec) \d{4}$", value):
        raise InvalidDateFormatError(field_name=field_name, value=value)
    # Additionally, try to parse with datetime to catch invalid dates like "Feb 3000" (if checking month validity)
    # or just to ensure it's a real month. strptime will validate month and year ranges.
    try:
        datetime.strptime(value, "%b %Y")
    except ValueError:
        # This might be redundant if regex is strict enough, but good for full validation
        raise InvalidDateFormatError(field_name=field_name, value=value)
    return value

class PersonalInfo(BaseModel):
    name: str
    email: EmailStr
    phone: Optional[str] = None
    linkedin: Optional[HttpUrl] = None
    github: Optional[HttpUrl] = None
    website: Optional[HttpUrl] = None

class ExperienceItem(BaseModel):
    title: str
    company: str
    location: Optional[str] = None
    start_date: str # Made non-optional as per original schema, validator handles format
    end_date: Optional[str] = None # Optional as 'current' can be true
    current: Optional[bool] = False
    description: Optional[str] = None
    achievements: Optional[List[str]] = None
    variants: Optional[List[str]] = None

    @validator('start_date')
    def check_start_date_format(cls, value):
        return validate_month_year_date(value, 'start_date')

    @validator('end_date')
    def check_end_date_format(cls, value):
        # This will also be called for None values if end_date is Optional,
        # validate_month_year_date handles None correctly.
        return validate_month_year_date(value, 'end_date')

class EducationItem(BaseModel):
    degree: str
    institution: str
    location: Optional[str] = None
    start_date: Optional[str] = None # Kept optional as per original schema
    end_date: Optional[str] = None
    description: Optional[str] = None
    variants: Optional[List[str]] = None

    @validator('start_date')
    def check_start_date_format(cls, value):
        return validate_month_year_date(value, 'start_date')

    @validator('end_date')
    def check_end_date_format(cls, value):
        return validate_month_year_date(value, 'end_date')

class TechnicalSkill(BaseModel):
    name: str
    level: Optional[str] = None
    keywords: Optional[List[str]] = None

class LanguageSkill(BaseModel):
    name: str
    level: Optional[str] = None

class Skills(BaseModel):
    technical: Optional[List[TechnicalSkill]] = None
    soft: Optional[List[str]] = None
    tools: Optional[List[str]] = None
    languages: Optional[List[LanguageSkill]] = None

class PublicationItem(BaseModel):
    title: str
    authors: str # Could be List[str] if more granularity is needed later
    journal: str
    year: str # Or int, but keeping as str for now as per YAML
    doi: Optional[str] = None
    variants: Optional[List[str]] = None

class ProjectItem(BaseModel):
    name: str
    description: str
    technologies: Optional[List[str]] = None
    link: Optional[HttpUrl] = None
    variants: Optional[List[str]] = None

class AwardItem(BaseModel):
    name: str
    event: Optional[str] = None
    year: Optional[str] = None
    description: Optional[str] = None
    variants: Optional[List[str]] = None

class VariantDetails(BaseModel):
    name: str
    description: Optional[str] = None
    sections: List[str]

class MetaData(BaseModel):
    variants: Dict[str, VariantDetails]

class CVData(BaseModel):
    personal_info: PersonalInfo
    profile: Optional[str] = None
    experience: Optional[List[ExperienceItem]] = None
    education: Optional[List[EducationItem]] = None
    skills: Optional[Skills] = None
    publications: Optional[List[PublicationItem]] = None
    projects: Optional[List[ProjectItem]] = None
    awards: Optional[List[AwardItem]] = None
    metadata: Optional[MetaData] = None
