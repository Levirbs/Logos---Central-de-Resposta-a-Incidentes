from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, StringConstraints

from app.models import Category, Criticality, Status

# strip_whitespace antes do min_length: "   " deve ser rejeitado como vazio.
Text120 = Annotated[str, StringConstraints(strip_whitespace=True, min_length=3, max_length=120)]
Text200 = Annotated[str, StringConstraints(strip_whitespace=True, min_length=3, max_length=200)]
Text2000 = Annotated[str, StringConstraints(strip_whitespace=True, min_length=3, max_length=2000)]


class IncidentCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: Text120
    description: Text2000
    category: Category
    criticality: Criticality
    status: Status = Status.OPEN
    location: Text200
    reporter: Text120


class StatusUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: Status
    version: Annotated[int, Field(ge=1)]


class IncidentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    code: str
    title: str
    description: str
    category: Category
    criticality: Criticality
    status: Status
    location: str
    reporter: str
    created_at: datetime
    updated_at: datetime
    version: int


class ConflictResponse(BaseModel):
    code: str = "VERSION_CONFLICT"
    message: str
    current: IncidentOut
