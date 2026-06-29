from typing import List

from pydantic import BaseModel


class Story(BaseModel):
    id: int
    title: str
    description: str
    tasks: List[str]
    acceptance_criteria: List[str]


class SprintResponse(BaseModel):
    epic: str
    stories: List[Story]
