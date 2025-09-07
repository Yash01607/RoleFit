from typing import Dict, List
from app.models.db.base import BaseModelDB


class ParsedResumeDB(BaseModelDB):
    file_id: str
    owner_id: str
    workspace_id: str
    sections: Dict[str, List[str]] | None = None
