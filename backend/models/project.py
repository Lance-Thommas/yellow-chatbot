
from pydantic import BaseModel

class Project(BaseModel):
    id: int
    name: str
    description: str # Create error handling for this later, let the LLM decide an appropriate name
    is_active: bool = True