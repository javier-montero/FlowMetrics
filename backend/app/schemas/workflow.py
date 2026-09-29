from pydantic import BaseModel, ConfigDict


class ReadSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class WorkflowDefinitionRead(ReadSchema):
    id: int
    name: str
    version: str


class ProcessDefinitionRead(ReadSchema):
    id: int
    name: str
    expected_duration_seconds: int | None = None