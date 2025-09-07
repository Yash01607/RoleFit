from pydantic import BaseModel
from typing import Dict, List


class ParsedResume(BaseModel):
    sections: Dict[str, List[str]] | None = None
