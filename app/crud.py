import logging

from sqlalchemy import or_
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import aliased, Session

from .exceptions import (
    ExperimentNotFoundError,
    TeamAlreadyExistsError,
    TeamCircularReferenceError,
    TeamDoubleAssignmentError,
    TeamNotFoundError,
    TeamsNumberChangeError,
    TeamsNumberError,
)
from .models import Experiment, Team
from .schemas import (
    ExperimentCreate,
    ExperimentReassignTeams,
    ExperimentUpdate,
    TeamBase,
    TeamCreate,
    TeamUpdate,
)


def _add_teams_to_experiment(
    db: Session, experiment: Experiment, teams: list[TeamBase]
):
    try:
        db_teams = []
        for team in teams:
            db_team = get_team_by_name(db, team.name)
            if not db_team:
                db_team = Team(**team.dict())
                db.add(db_team)
                db.flush()
            db_teams.append(db_team)

        for db_team in db_teams:
            if any(
                other_db_team.is_descendant_of(db_team) for other_db_team in db_teams
            ):
                raise TeamCircularReferenceError()

            if db_team in experiment.teams:
                raise TeamDoubleAssignmentError()

            experiment.teams.append(db_team)

    except SQLAlchemyError as e:
        logging.error(f"An error occurred while adding teams to an experiment: {e}")
        db.rollback()
        raise


def get_experiment(db: Session, experiment_id: int) -> Experiment | None:
    return db.query(Experiment).filter(Experiment.id == experiment_id).first()


def get_experiments(db: Session, team: str | None = None, include_descendants: bool = False):
    if team:
        if include_descendants:
            team_alias = aliased(Team)
            descendants = db.query(team_alias).\
                with_entities(team_alias.id).\
                filter(team_alias.name == team).\
                cte(name='descendants', recursive=True)

            aliased_descendants = aliased(descendants, name='d')
            recursive_query = db.query(Team.id).filter(Team.parent_id == aliased_descendants.c.id)
            descendants = descendants.union_all(recursive_query)

            return (
                db.query(Experiment)
                .filter(or_(Experiment.teams.any(Team.id.in_(descendants)), Experiment.teams.any(Team.name == team)))
                .all()
            )
        else:
            return db.query(Experiment).filter(Experiment.teams.any(Team.name == team)).all()

    return db.query(Experiment).all()


def create_experiment(db: Session, experiment: ExperimentCreate):
    teams = experiment.teams

    if not teams or len(teams) > 2:
        raise TeamsNumberError()

    del experiment.teams

    try:
        db_experiment = Experiment(**experiment.dict())
        db.add(db_experiment)
        db.flush()

        _add_teams_to_experiment(db, db_experiment, teams)

        db.commit()
        db.refresh(db_experiment)

    except SQLAlchemyError as e:
        logging.error(f"An error occurred while creating an experiment: {e}")
        db.rollback()
        raise

    else:
        return db_experiment


def update_experiment(db: Session, experiment: ExperimentUpdate, experiment_id: int):
    try:
        db_experiment = get_experiment(db, experiment_id=experiment_id)
        if db_experiment is None:
            raise ExperimentNotFoundError()

        db_experiment.description = experiment.description
        db_experiment.sample_ratio = experiment.sample_ratio

        db.commit()
        db.refresh(db_experiment)

    except SQLAlchemyError as e:
        logging.error(f"An error occurred while updating an experiment: {e}")
        db.rollback()
        raise

    else:
        return db_experiment


def reassign_experiment_teams(
    db: Session, experiment: ExperimentReassignTeams, experiment_id: int
):
    try:
        db_experiment = get_experiment(db, experiment_id=experiment_id)
        if db_experiment is None:
            raise ExperimentNotFoundError()

        if len(db_experiment.teams) != len(experiment.teams):
            raise TeamsNumberChangeError(len(experiment.teams), len(db_experiment.teams))

        db_experiment.teams = []

        _add_teams_to_experiment(db, db_experiment, experiment.teams)

        db.commit()
        db.refresh(db_experiment)

    except SQLAlchemyError as e:
        logging.error(f"An error occurred while reassigning teams to an experiment: {e}")
        db.rollback()
        raise

    else:
        return db_experiment


def delete_experiment(db: Session, experiment_id: int):
    try:
        db_experiment = get_experiment(db, experiment_id=experiment_id)
        if db_experiment is None:
            raise ExperimentNotFoundError()

        db.delete(db_experiment)
        db.commit()

    except SQLAlchemyError as e:
        logging.error(f"An error occurred while deleting an experiment: {e}")
        db.rollback()
        raise

    else:
        return None


def get_teams(db: Session):
    return db.query(Team).all()


def get_team_by_id(db: Session, team_id: int):
    return db.query(Team).filter(Team.id == team_id).first()


def get_team_by_name(db: Session, team_name: str):
    return db.query(Team).filter(Team.name == team_name).first()


def create_team(db: Session, team: TeamCreate):
    try:
        db_team = get_team_by_name(db, team_name=team.name)
        if db_team is not None:
            raise TeamAlreadyExistsError()

        db_team = Team(**team.dict())
        db.add(db_team)
        db.commit()
        db.refresh(db_team)

    except SQLAlchemyError as e:
        logging.error(f"An error occurred while creating a team: {e}")
        db.rollback()
        raise

    else:
        return db_team


def update_team(db: Session, team: TeamUpdate, team_name: str):
    try:
        db_team = get_team_by_name(db, team_name=team_name)
        if db_team is None:
            raise TeamNotFoundError()

        if db_team.parent is not None and db_team.parent.is_descendant_of(db_team):
            logging.error(
                "Attempted to set a team's descendant as its parent. Aborting team update."
            )
            raise TeamCircularReferenceError()

        db_team.name = team.name
        db_team.parent_id = team.parent_id

        db.commit()
        db.refresh(db_team)

    except SQLAlchemyError as e:
        logging.error(f"An error occurred while updating a team: {e}")
        db.rollback()
        raise

    else:
        return db_team


def delete_team(db: Session, team_name: str):
    try:
        db_team = get_team_by_name(db, team_name=team_name)
        if db_team is None:
            raise TeamNotFoundError()

        db.delete(db_team)
        db.commit()

    except SQLAlchemyError as e:
        logging.error(f"An error occurred while deleting a team: {e}")
        db.rollback()
        raise

    else:
        return None
