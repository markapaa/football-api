"""Schemas (Pydantic): ορίζουν τι δέχεται και τι επιστρέφει το API.

Το FastAPI τα χρησιμοποιεί για αυτόματο validation των εισόδων και για να
φτιάξει την τεκμηρίωση στο /docs.
"""
import datetime as dt

from pydantic import BaseModel, ConfigDict, Field, model_validator


class TeamOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str


class MatchCreate(BaseModel):
    season: str = Field(pattern=r"^\d{4}-\d{2}$", examples=["2024-25"])
    date: dt.date
    home_team: str = Field(min_length=1, max_length=100)
    away_team: str = Field(min_length=1, max_length=100)
    home_goals: int = Field(ge=0, le=99)
    away_goals: int = Field(ge=0, le=99)

    @model_validator(mode="after")
    def teams_must_differ(self):
        if self.home_team.strip().lower() == self.away_team.strip().lower():
            raise ValueError("home_team and away_team must be different")
        return self


class MatchOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    season: str
    date: dt.date
    home_team: TeamOut
    away_team: TeamOut
    home_goals: int
    away_goals: int


class StandingRow(BaseModel):
    position: int
    team: str
    played: int
    won: int
    drawn: int
    lost: int
    goals_for: int
    goals_against: int
    goal_difference: int
    points: int
