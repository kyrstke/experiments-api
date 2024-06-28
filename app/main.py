from fastapi import Depends, FastAPI
from sqlalchemy.orm import Session

from . import crud, schemas
from .database import get_db
from .exceptions import TeamNotFoundError, ExperimentNotFoundError

app = FastAPI()


@app.get("/experiments/", response_model=list[schemas.Experiment])
def read_experiments(
    team: str | None = None,
    include_descendants: bool = False,
    db: Session = Depends(get_db),
):
    """
    Get a list of all experiments. Optionally, provide the following query parameters:

    - **team**: the name of the team to filter by
    - **include_descendants**: whether to include the descendants of the team or not
    """
    experiments = crud.get_experiments(db, team=team, include_descendants=include_descendants)
    return experiments


@app.get("/experiments/{experiment_id}", response_model=schemas.Experiment)
def read_experiment(experiment_id: int, db: Session = Depends(get_db)):
    """
    Get an experiment by its ID
    """
    db_experiment = crud.get_experiment(db, experiment_id=experiment_id)
    if db_experiment is None:
        raise ExperimentNotFoundError()
    return db_experiment


@app.post("/experiments/", status_code=201, response_model=schemas.Experiment)
def create_experiment(
    experiment: schemas.ExperimentCreate, db: Session = Depends(get_db)
):
    """
    Create an experiment with all the information:

    - **description**: a description of the experiment
    - **sample_ratio**: the ratio of the sample
    - **teams**: a list of teams assigned to the experiment (their names)

    There are several constraints related to the teams:
    - the number of teams must be between 1 and 2
    - the teams must not be descendants of each other
    - each team can be assigned to an experiment only once
    """
    return crud.create_experiment(db=db, experiment=experiment)


@app.put("/experiments/{experiment_id}/", response_model=schemas.Experiment)
def update_experiment(
    experiment_id: int,
    experiment: schemas.ExperimentUpdate,
    db: Session = Depends(get_db),
):
    """
    Update an experiment by passing its ID. You can update the following fields:

    - **description**: a description of the experiment
    - **sample_ratio**: the ratio of the sample
    """
    return crud.update_experiment(
        db=db, experiment=experiment, experiment_id=experiment_id
    )


@app.patch(
    "/experiments/{experiment_id}/reassign_teams/", response_model=schemas.Experiment
)
def reassign_experiment_teams(
    experiment_id: int,
    experiment: schemas.ExperimentReassignTeams,
    db: Session = Depends(get_db),
):
    """
    Reassign the teams of an experiment by passing its ID. You can update the following fields:

    - **teams**: a list of teams assigned to the experiment (their names)

    There are several constraints related to the teams, the same as during the creation of an experiment:
    - the number of teams must be between 1 and 2
    - the teams must not be descendants of each other
    - each team can be assigned to an experiment only once
    """
    return crud.reassign_experiment_teams(
        db=db, experiment=experiment, experiment_id=experiment_id
    )


@app.delete("/experiments/{experiment_id}/", status_code=204)
def delete_experiment(experiment_id: int, db: Session = Depends(get_db)):
    """
    Delete an experiment by passing its ID.
    """
    return crud.delete_experiment(db=db, experiment_id=experiment_id)


@app.get("/teams/", response_model=list[schemas.Team])
def read_teams(db: Session = Depends(get_db)):
    """
    Get a list of all teams.
    """
    teams = crud.get_teams(db)
    return teams


@app.get("/teams/{team_name}", response_model=schemas.Team)
def read_team(team_name: str, db: Session = Depends(get_db)):
    """
    Get a team by its name.
    """
    db_team = crud.get_team_by_name(db, team_name=team_name)
    if db_team is None:
        raise TeamNotFoundError()
    return db_team


@app.post("/teams/", status_code=201, response_model=schemas.Team)
def create_team(team: schemas.TeamCreate, db: Session = Depends(get_db)):
    """
    Create a team with the following information:

    - **name**: the name of the team
    - **parent_id**: the ID of the parent team (if any)
    """
    return crud.create_team(db=db, team=team)


@app.put("/teams/{team_name}/", response_model=schemas.Team)
def update_team(
    team_name: str, team: schemas.TeamUpdate, db: Session = Depends(get_db)
):
    """
    Update a team by passing its name. You can update the following fields:

    - **name**: the name of the team
    - **parent_id**: the ID of the parent team (if any)
    """
    return crud.update_team(db=db, team=team, team_name=team_name)


@app.delete("/teams/{team_name}/", status_code=204)
def delete_team(team_name: str, db: Session = Depends(get_db)):
    """
    Delete a team by passing its name.
    """
    return crud.delete_team(db=db, team_name=team_name)