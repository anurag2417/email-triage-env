from pydantic import BaseModel

class Observation(BaseModel):
    id: int
    sender: str
    subject: str
    body: str

class Action(BaseModel):
    label: str
    priority: str
    reply: str = ""

class StepResponse(BaseModel):
    observation: Observation | None
    reward: float
    done: bool
    info: dict