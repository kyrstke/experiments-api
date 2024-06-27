from fastapi import HTTPException
from sqlalchemy.orm import Session

from .models import Experiment, Team
from .schemas import ExperimentCreate, TeamCreate, ExperimentUpdate, ExperimentBase


def get_experiment(db: Session, experiment_id: int):
    return db.query(Experiment).filter(Experiment.id == experiment_id).first()


def get_experiments(
    db: Session, skip: int = 0, limit: int = 100, team: str | None = None
):
    if team:
        return (
            db.query(Experiment)
            .filter(Experiment.teams.any(Team.name == team))
            .offset(skip)
            .limit(limit)
            .all()
            if team
            else db.query(Experiment).offset(skip).limit(limit).all()
        )

    return db.query(Experiment).offset(skip).limit(limit).all()


def create_experiment(db: Session, experiment: ExperimentCreate):
    teams = experiment.teams

    if not teams or len(teams) > 2:
        raise HTTPException(
            status_code=400, detail="Teams number must be either 1 or 2"
        )

    del experiment.teams

    db_experiment = Experiment(**experiment.dict())
    db.add(db_experiment)
    db.flush()

    for team_data in teams:
        team = db.query(Team).filter(Team.name == team_data.name).first()
        if not team:
            team = Team(**team_data.dict())
            db.add(team)
        db_experiment.teams.append(team)

    db.commit()
    db.refresh(db_experiment)

    return db_experiment


def update_experiment(db: Session, experiment: ExperimentBase, experiment_id: int):
    db_experiment = get_experiment(db, experiment_id=experiment_id)
    if db_experiment is None:
        raise HTTPException(status_code=404, detail="Experiment not found")

    db_experiment.description = experiment.description
    db_experiment.sample_ratio = experiment.sample_ratio

    db.commit()
    db.refresh(db_experiment)

    return db_experiment


def reassign_experiment_teams(db: Session, experiment: ExperimentUpdate, experiment_id: int):
    db_experiment = get_experiment(db, experiment_id=experiment_id)
    if db_experiment is None:
        raise HTTPException(status_code=404, detail="Experiment not found")

    # old_teams = [team.name for team in db_experiment.teams]
    # new_teams = [team.name for team in experiment.teams]
    #
    # print(f"Old teams: {old_teams}, New teams {new_teams}")

    if len(db_experiment.teams) != len(experiment.teams):
        raise HTTPException(
            status_code=400,
            detail=f"Provided number of teams ({len(experiment.teams)}) is not equal to the experiment's "
            f"current number of teams ({len(db_experiment.teams)}). The number of teams cannot change",
        )

    db_experiment.teams = []

    for team_data in experiment.teams:
        team = db.query(Team).filter(Team.name == team_data.name).first()
        if not team:
            team = Team(**team_data.dict())
            db.add(team)

        if team in db_experiment.teams:
            raise HTTPException(status_code=400, detail="Each team can be assigned to an experiment only once")

        db_experiment.teams.append(team)

    db.commit()
    db.refresh(db_experiment)

    return db_experiment


def get_teams(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Team).offset(skip).limit(limit).all()


def get_team(db: Session, team_name: str):
    return db.query(Team).filter(Team.name == team_name).first()


def create_team(db: Session, team: TeamCreate):
    db_team = db.query(Team).filter(Team.name == team.name).first()
    if db_team is not None:
        raise HTTPException(status_code=400, detail="A team with this name already exists")

    db_team = Team(**team.dict())
    db.add(db_team)
    db.commit()
    db.refresh(db_team)

    return db_team
