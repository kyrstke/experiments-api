from pydantic import BaseModel


class TeamBase(BaseModel):
    name: str


class ExperimentBase(BaseModel):
    description: str
    sample_ratio: float


class TeamCreate(TeamBase):
    experiments: list[ExperimentBase]


class ExperimentCreate(ExperimentBase):
    teams: list[TeamBase]


class Team(TeamBase):
    id: int
    experiments: list[ExperimentBase] = []

    class Config:
        from_attributes = True


class Experiment(ExperimentBase):
    id: int
    teams: list[TeamBase] = []

    class Config:
        from_attributes = True
