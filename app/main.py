"""Τα HTTP endpoints του API."""
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.database import Base, engine, get_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Στην εκκίνηση δημιουργεί τους πίνακες αν δεν υπάρχουν.
    Base.metadata.create_all(engine)
    yield


app = FastAPI(
    title="Football API",
    description="Μικρό REST API για αγώνες, ομάδες και βαθμολογία ποδοσφαίρου.",
    version="0.1.0",
    lifespan=lifespan,
)


@app.get("/health")
def health():
    """Το χρησιμοποιούν Docker/hosting για να ελέγξουν ότι η εφαρμογή ζει."""
    return {"status": "ok"}


@app.get("/teams", response_model=list[schemas.TeamOut])
def list_teams(db: Session = Depends(get_db)):
    return db.scalars(select(models.Team).order_by(models.Team.name)).all()


@app.get("/teams/{team_id}", response_model=schemas.TeamOut)
def get_team(team_id: int, db: Session = Depends(get_db)):
    team = db.get(models.Team, team_id)
    if team is None:
        raise HTTPException(status_code=404, detail="Team not found")
    return team


@app.get("/matches", response_model=list[schemas.MatchOut])
def list_matches(
    season: str | None = Query(None, examples=["2024-25"]),
    team: str | None = Query(None, description="Ακριβές όνομα ομάδας"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    return crud.list_matches(db, season=season, team=team, limit=limit, offset=offset)


@app.post("/matches", response_model=schemas.MatchOut, status_code=201)
def create_match(data: schemas.MatchCreate, db: Session = Depends(get_db)):
    return crud.create_match(db, data)


@app.get("/standings", response_model=list[schemas.StandingRow])
def standings(season: str = Query(..., examples=["2024-25"]), db: Session = Depends(get_db)):
    return crud.compute_standings(db, season)
