from fastapi import HTTPException
from sqlalchemy.orm import Session

from .models import Experiment, Team
from .schemas import ExperimentCreate, TeamCreate


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


def get_teams(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Team).offset(skip).limit(limit).all()


def get_team(db: Session, team_id: int):
    return db.query(Team).filter(Team.id == team_id).first()


def create_team(db: Session, team: TeamCreate):
    db_team = Team(**team.dict())
    db.add(db_team)
    db.commit()
    db.refresh(db_team)
    return db_team
