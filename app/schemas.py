from pydantic import BaseModel


class TeamBase(BaseModel):
    name: str


class ExperimentBase(BaseModel):
    description: str
    sample_ratio: float


class TeamCreate(TeamBase):
    parent_id: int | None = None


class ExperimentCreate(ExperimentBase):
    teams: list[TeamBase]


class TeamUpdate(TeamBase):
    parent_id: int | None = None


class ExperimentUpdate(ExperimentBase):
    pass


class ExperimentReassignTeams(BaseModel):
    teams: list[TeamBase]


class TeamChild(TeamBase):
    id: int


class Team(TeamBase):
    id: int
    parent_id: int | None = None
    children: list[TeamChild] = []
    experiments: list[ExperimentBase] = []

    class Config:
        from_attributes = True


class Experiment(ExperimentBase):
    id: int
    teams: list[TeamBase] = []

    class Config:
        from_attributes = True
