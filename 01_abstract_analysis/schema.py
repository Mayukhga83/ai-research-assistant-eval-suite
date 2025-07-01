from pydantic import BaseModel, Field
from typing import List, Optional


class AbstractRecord(BaseModel):
    paper_id: str
    title: str
    abstract: str
    field: Optional[str] = None


class StructuredSummary(BaseModel):
    task: str = ""
    method: str = ""
    dataset: str = ""
    metric: str = ""
    result: str = ""
    limitation: str = ""
    keywords: List[str] = Field(default_factory=list)
