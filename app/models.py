from __future__ import annotations

from sqlalchemy import Column, ForeignKey, Table
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base

experiment_team_association = Table(
    "experiment_team",
    Base.metadata,
    Column("experiment_id", ForeignKey("experiment.id"), primary_key=True),
    Column("team_id", ForeignKey("team.id"), primary_key=True),
)


class Experiment(Base):
    __tablename__ = "experiment"

    id: Mapped[int] = mapped_column(primary_key=True)
    description: Mapped[str] = mapped_column(nullable=False, index=True)
    sample_ratio: Mapped[float] = mapped_column(nullable=False, index=True)

    teams: Mapped[list[Team]] = relationship(
        secondary=experiment_team_association, back_populates="experiments"
    )


class Team(Base):
    __tablename__ = "team"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(unique=True, nullable=False, index=True)
    parent_id: Mapped[int] = mapped_column(ForeignKey("team.id"), nullable=True)

    children = relationship("Team", back_populates="parent")
    parent = relationship("Team", back_populates="children", remote_side=[id])

    experiments: Mapped[list[Experiment]] = relationship(
        secondary=experiment_team_association, back_populates="teams"
    )

    def is_descendant_of(self, team: Team) -> bool:
        if self.parent_id == team.id:
            return True
        elif self.parent_id is None:
            return False
        else:
            return self.parent.is_descendant_of(team)
