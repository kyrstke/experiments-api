from fastapi import HTTPException


class TeamNotFoundError(HTTPException):
    def __init__(self):
        super().__init__(status_code=404, detail="Team not found")


class TeamAlreadyExistsError(HTTPException):
    def __init__(self):
        super().__init__(status_code=400, detail="A team with this name already exists")


class TeamsNumberChangeError(HTTPException):
    def __init__(self, provided_teams_length: int, current_teams_length: int):
        detail = (
            f"Provided number of teams ({provided_teams_length}) is not equal to the experiment's "
            f"current number of teams ({current_teams_length}). The number of teams cannot change"
        )
        super().__init__(status_code=400, detail=detail)


class TeamsDescendantError(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=400,
            detail="Teams working on an experiment cannot be descendants of each other",
        )


class TeamDoubleAssignmentError(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=400,
            detail="Each team can be assigned to an experiment only once",
        )


class TeamsNumberError(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=400, detail="An experiment must be assigned either 1 or 2 teams"
        )


class TeamCircularReferenceError(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=400, detail="Cannot set a team's descendant as its parent"
        )


class ExperimentNotFoundError(HTTPException):
    def __init__(self):
        super().__init__(status_code=404, detail="Experiment not found")
