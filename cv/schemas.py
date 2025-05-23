"""Pydantic models for CV data validation and structure.

This module defines the Pydantic models that correspond to the structure of the 
`cv_data.yaml` file. These models are used by `validators.py` to parse and 
validate the CV data, ensuring it conforms to the expected schema. This includes 
validating data types, formats (like email, URL, and custom date formats), and 
the presence of required fields.
"""
import re
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, HttpUrl, PydanticValueError, validator


class InvalidDateFormatError(PydanticValueError):
    """Custom Pydantic error for invalid date formats.

    This error is raised by `validate_month_year_date` when a date string
    does not conform to the "MMM YYYY" format.
    """
    code = 'date.invalid_format'
    msg_template = 'Invalid date format for {field_name}: "{value}". Must be "MMM YYYY" (e.g., "Aug 2021").'

def validate_month_year_date(value: Optional[str], field_name: str) -> Optional[str]:
    """Validate that a date string is in 'MMM YYYY' format.

    Parameters
    ----------
    value : Optional[str]
        The date string to validate. Can be None.
    field_name : str
        The name of the field being validated (for error messages).

    Returns
    -------
    Optional[str]
        The validated date string, or None if the input was None.

    Raises
    ------
    InvalidDateFormatError
        If the date string does not conform to the "MMM YYYY" format
        or represents an invalid date (e.g., if datetime.strptime fails).
    """
    if value is None:  # Allow optional fields to be None
        return value
    # Regex to match "MMM YYYY" format, e.g., "Aug 2021", "Dec 2023"
    if not re.match(r"^(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec) \d{4}$", value):
        raise InvalidDateFormatError(field_name=field_name, value=value)
    # Additionally, try to parse with datetime to catch invalid dates
    try:
        datetime.strptime(value, "%b %Y")
    except ValueError:
        raise InvalidDateFormatError(field_name=field_name, value=value)
    return value

class PersonalInfo(BaseModel):
    """Stores personal contact information.

    Attributes
    ----------
    name : str
        The full name.
    email : EmailStr
        The primary email address.
    phone : Optional[str], default=None
        The phone number.
    linkedin : Optional[HttpUrl], default=None
        URL to the LinkedIn profile.
    github : Optional[HttpUrl], default=None
        URL to the GitHub profile.
    website : Optional[HttpUrl], default=None
        URL to a personal or professional website.
    """
    name: str
    email: EmailStr
    phone: Optional[str] = None
    linkedin: Optional[HttpUrl] = None
    github: Optional[HttpUrl] = None
    website: Optional[HttpUrl] = None

class ExperienceItem(BaseModel):
    """Represents a single experience entry (e.g., a job).

    Attributes
    ----------
    title : str
        The job title or role.
    company : str
        The name of the company or organization.
    location : Optional[str], default=None
        The location of the work (e.g., "City, Country").
    start_date : str
        The start date of the experience, in "MMM YYYY" format.
    end_date : Optional[str], default=None
        The end date of the experience, in "MMM YYYY" format.
        Can be None if the experience is current.
    current : Optional[bool], default=False
        Indicates if this is a current position.
    description : Optional[str], default=None
        A brief description of the role and responsibilities.
    achievements : Optional[list[str]], default=None
        A list of key achievements or accomplishments.
    variants : Optional[list[str]], default=None
        A list of variant tags this item belongs to.
    """
    title: str
    company: str
    location: Optional[str] = None
    start_date: str
    end_date: Optional[str] = None
    current: Optional[bool] = False
    description: Optional[str] = None
    achievements: Optional[list[str]] = None
    variants: Optional[list[str]] = None

    @validator('start_date')
    def check_start_date_format(cls, value: str) -> str:
        """Validate the start_date format."""
        return validate_month_year_date(value, 'start_date')

    @validator('end_date')
    def check_end_date_format(cls, value: Optional[str]) -> Optional[str]:
        """Validate the end_date format."""
        return validate_month_year_date(value, 'end_date')

class EducationItem(BaseModel):
    """Represents a single education entry (e.g., a degree).

    Attributes
    ----------
    degree : str
        The name of the degree or qualification.
    institution : str
        The name of the educational institution.
    location : Optional[str], default=None
        The location of the institution (e.g., "City, Country").
    start_date : Optional[str], default=None
        The start date of the education, in "MMM YYYY" format.
    end_date : Optional[str], default=None
        The end date or graduation date, in "MMM YYYY" format.
    description : Optional[str], default=None
        Additional details, such as dissertation title or honors.
    variants : Optional[list[str]], default=None
        A list of variant tags this item belongs to.
    """
    degree: str
    institution: str
    location: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    description: Optional[str] = None
    variants: Optional[list[str]] = None

    @validator('start_date')
    def check_start_date_format(cls, value: Optional[str]) -> Optional[str]:
        """Validate the start_date format."""
        return validate_month_year_date(value, 'start_date')

    @validator('end_date')
    def check_end_date_format(cls, value: Optional[str]) -> Optional[str]:
        """Validate the end_date format."""
        return validate_month_year_date(value, 'end_date')

class TechnicalSkill(BaseModel):
    """Represents a single technical skill.

    Attributes
    ----------
    name : str
        The name of the skill (e.g., "Python", "SQL").
    level : Optional[str], default=None
        The proficiency level (e.g., "Expert", "Advanced").
    keywords : Optional[list[str]], default=None
        Associated keywords or sub-skills (e.g., ["pandas", "numpy"] for Python).
    """
    name: str
    level: Optional[str] = None
    keywords: Optional[list[str]] = None

class LanguageSkill(BaseModel):
    """Represents proficiency in a spoken or written language.

    Attributes
    ----------
    name : str
        The name of the language (e.g., "English", "Spanish").
    level : Optional[str], default=None
        The proficiency level (e.g., "Fluent", "Native").
    """
    name: str
    level: Optional[str] = None

class Skills(BaseModel):
    """Container for different categories of skills.

    Attributes
    ----------
    technical : Optional[list[TechnicalSkill]], default=None
        A list of technical skills.
    soft : Optional[list[str]], default=None
        A list of soft skills.
    tools : Optional[list[str]], default=None
        A list of tools or software proficiency.
    languages : Optional[list[LanguageSkill]], default=None
        A list of language proficiencies.
    """
    technical: Optional[list[TechnicalSkill]] = None
    soft: Optional[list[str]] = None
    tools: Optional[list[str]] = None
    languages: Optional[list[LanguageSkill]] = None

class PublicationItem(BaseModel):
    """Represents a single publication entry.

    Attributes
    ----------
    title : str
        The title of the publication.
    authors : str
        The list of authors, typically as a string (e.g., "Doe, J., et al.").
    journal : str
        The name of the journal or conference.
    year : str
        The year of publication.
    doi : Optional[str], default=None
        The Digital Object Identifier (DOI) for the publication.
    variants : Optional[list[str]], default=None
        A list of variant tags this item belongs to.
    """
    title: str
    authors: str
    journal: str
    year: str
    doi: Optional[str] = None
    variants: Optional[list[str]] = None

class ProjectItem(BaseModel):
    """Represents a single project entry.

    Attributes
    ----------
    name : str
        The name of the project.
    description : str
        A brief description of the project.
    technologies : Optional[list[str]], default=None
        A list of technologies used in the project.
    link : Optional[HttpUrl], default=None
        A URL link to the project (e.g., GitHub repository).
    variants : Optional[list[str]], default=None
        A list of variant tags this item belongs to.
    """
    name: str
    description: str
    technologies: Optional[list[str]] = None
    link: Optional[HttpUrl] = None
    variants: Optional[list[str]] = None

class AwardItem(BaseModel):
    """Represents a single award or honor.

    Attributes
    ----------
    name : str
        The name of the award.
    event : Optional[str], default=None
        The event or organization that gave the award.
    year : Optional[str], default=None
        The year the award was received.
    description : Optional[str], default=None
        A brief description of the award.
    variants : Optional[list[str]], default=None
        A list of variant tags this item belongs to.
    """
    name: str
    event: Optional[str] = None
    year: Optional[str] = None
    description: Optional[str] = None
    variants: Optional[list[str]] = None

class VariantDetails(BaseModel):
    """Defines the properties of a single CV variant.

    Attributes
    ----------
    name : str
        The display name of the variant (e.g., "Data Science CV").
    description : Optional[str], default=None
        A brief description of this CV variant.
    sections : list[str]
        A list of top-level section keys (e.g., "experience", "education")
        to be included in this variant.
    """
    name: str
    description: Optional[str] = None
    sections: list[str]

class MetaData(BaseModel):
    """Stores metadata about the CV, including variant definitions.

    Attributes
    ----------
    variants : dict[str, VariantDetails]
        A dictionary where keys are variant tags (e.g., "ds", "academic")
        and values are `VariantDetails` objects defining each variant.
    """
    variants: dict[str, VariantDetails]

class CVData(BaseModel):
    """The root model for the entire CV data structure.

    This model aggregates all other data models and represents the complete
    content of the `cv_data.yaml` file.

    Attributes
    ----------
    personal_info : PersonalInfo
        The personal information section.
    profile : Optional[str], default=None
        A professional profile or summary statement.
    experience : Optional[list[ExperienceItem]], default=None
        A list of work experience entries.
    education : Optional[list[EducationItem]], default=None
        A list of education entries.
    skills : Optional[Skills], default=None
        The skills section, categorized.
    publications : Optional[list[PublicationItem]], default=None
        A list of publications.
    projects : Optional[list[ProjectItem]], default=None
        A list of projects.
    awards : Optional[list[AwardItem]], default=None
        A list of awards and honors.
    metadata : Optional[MetaData], default=None
        Metadata for the CV, including variant definitions.
    """
    personal_info: PersonalInfo
    profile: Optional[str] = None
    experience: Optional[list[ExperienceItem]] = None
    education: Optional[list[EducationItem]] = None
    skills: Optional[Skills] = None
    publications: Optional[list[PublicationItem]] = None
    projects: Optional[list[ProjectItem]] = None
    awards: Optional[list[AwardItem]] = None
    metadata: Optional[MetaData] = None
