from typing import Any, Dict, List, Optional
from pydantic import BaseModel


class JobDescriptionCreate(BaseModel):
    job_title: str = None
    company: Optional[str] = None
    location: Optional[str] = None

    min_experience_years: Optional[int] = None
    max_experience_years: Optional[int] = None

    summary: Optional[str] = None
    skills: Optional[List[str]]
    responsibilities: Optional[List[str]] = None
    requirements: Optional[List[str]] = None

    additional_fields: Dict[str, Any] = {}
