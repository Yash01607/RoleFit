from typing import Any, Dict, List, Optional
from app.models.db.base import BaseModelDB


class JobDescriptionDB(BaseModelDB):
    owner_id: str
    workspace_id: str

    job_title: str = None
    company: Optional[str] = None
    location: Optional[str] = None

    min_experience_years: Optional[int] = None
    max_experience_years: Optional[int] = None

    summary: Optional[str] = None
    skills: Optional[List[str]]
    responsibilities: Optional[List[str]] = None
    requirements: Optional[List[str]] = None

    additional_fields: Dict[str, Any] = None
