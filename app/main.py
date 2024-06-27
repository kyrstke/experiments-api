from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

from . import crud, schemas
from .database import SessionLocal


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


app = FastAPI()


@app.get("/experiments/", response_model=list[schemas.Experiment])
def read_experiments(
    skip: int = 0,
    limit: int = 100,
    team: str | None = None,
    db: Session = Depends(get_db),
):
    experiments = crud.get_experiments(db, skip=skip, limit=limit, team=team)
    return experiments


@app.get("/experiments/{experiment_id}", response_model=schemas.Experiment)
def read_experiment(experiment_id: int, db: Session = Depends(get_db)):
    db_experiment = crud.get_experiment(db, experiment_id=experiment_id)
    if db_experiment is None:
        raise HTTPException(status_code=404, detail="Experiment not found")
    return db_experiment


@app.post("/experiments/", response_model=schemas.Experiment)
def create_experiment(
    experiment: schemas.ExperimentCreate, db: Session = Depends(get_db)
):
    return crud.create_experiment(db=db, experiment=experiment)


@app.put("/experiments/{experiment_id}/", response_model=schemas.Experiment)
def update_experiment(
    experiment_id: int,
    experiment: schemas.ExperimentBase,
    db: Session = Depends(get_db),
):
    return crud.update_experiment(
        db=db, experiment=experiment, experiment_id=experiment_id
    )


@app.patch("/experiments/{experiment_id}/reassign_teams/", response_model=schemas.Experiment)
def reassign_experiment_teams(
    experiment_id: int,
    experiment: schemas.ExperimentUpdate,
    db: Session = Depends(get_db),
):
    return crud.reassign_experiment_teams(
        db=db, experiment=experiment, experiment_id=experiment_id
    )


@app.get("/teams/", response_model=list[schemas.Team])
def read_teams(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    teams = crud.get_teams(db, skip=skip, limit=limit)
    return teams


@app.get("/teams/{team_name}", response_model=schemas.Team)
def read_team(team_name: str, db: Session = Depends(get_db)):
    db_team = crud.get_team(db, team_name=team_name)
    if db_team is None:
        raise HTTPException(status_code=404, detail="Team not found")
    return db_team


@app.post("/teams/", response_model=schemas.Team)
def create_team(team: schemas.TeamCreate, db: Session = Depends(get_db)):
    return crud.create_team(db=db, team=team)
