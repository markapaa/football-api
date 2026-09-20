"""Λογική πρόσβασης στα δεδομένα, χωριστά από τα HTTP endpoints."""
from sqlalchemy import or_, select
from sqlalchemy.orm import Session, joinedload

from app import models, schemas


def get_or_create_team(db: Session, name: str) -> models.Team:
    name = name.strip()
    team = db.scalar(select(models.Team).where(models.Team.name == name))
    if team is None:
        team = models.Team(name=name)
        db.add(team)
        db.flush()  # παίρνει id χωρίς να κάνει commit
    return team


def create_match(db: Session, data: schemas.MatchCreate) -> models.Match:
    home = get_or_create_team(db, data.home_team)
    away = get_or_create_team(db, data.away_team)
    match = models.Match(
        season=data.season,
        date=data.date,
        home_team_id=home.id,
        away_team_id=away.id,
        home_goals=data.home_goals,
        away_goals=data.away_goals,
    )
    db.add(match)
    db.commit()
    db.refresh(match)
    return match


def list_seasons(db: Session) -> list[str]:
    stmt = select(models.Match.season).distinct().order_by(models.Match.season.desc())
    return list(db.scalars(stmt))


def list_matches(
    db: Session,
    season: str | None = None,
    team: str | None = None,
    limit: int = 50,
    offset: int = 0,
) -> list[models.Match]:
    stmt = (
        select(models.Match)
        .options(joinedload(models.Match.home_team), joinedload(models.Match.away_team))
        .order_by(models.Match.date, models.Match.id)
        .limit(limit)
        .offset(offset)
    )
    if season:
        stmt = stmt.where(models.Match.season == season)
    if team:
        stmt = stmt.where(
            or_(
                models.Match.home_team.has(models.Team.name == team),
                models.Match.away_team.has(models.Team.name == team),
            )
        )
    return list(db.scalars(stmt))


def compute_standings(db: Session, season: str) -> list[schemas.StandingRow]:
    """Βαθμολογία: 3 βαθμοί νίκη, 1 ισοπαλία. Διαβάζει τους αγώνες της σεζόν
    και τους αθροίζει ανά ομάδα. Ταξινόμηση: βαθμοί, διαφορά τερμάτων, γκολ υπέρ."""
    matches = list_matches(db, season=season, limit=100_000)
    table: dict[str, dict[str, int]] = {}

    def row(name: str) -> dict[str, int]:
        return table.setdefault(
            name, dict(played=0, won=0, drawn=0, lost=0, gf=0, ga=0, points=0)
        )

    for m in matches:
        for team, scored, conceded in (
            (m.home_team.name, m.home_goals, m.away_goals),
            (m.away_team.name, m.away_goals, m.home_goals),
        ):
            r = row(team)
            r["played"] += 1
            r["gf"] += scored
            r["ga"] += conceded
            if scored > conceded:
                r["won"] += 1
                r["points"] += 3
            elif scored == conceded:
                r["drawn"] += 1
                r["points"] += 1
            else:
                r["lost"] += 1

    ordered = sorted(
        table.items(),
        key=lambda kv: (-kv[1]["points"], -(kv[1]["gf"] - kv[1]["ga"]), -kv[1]["gf"], kv[0]),
    )
    return [
        schemas.StandingRow(
            position=i,
            team=name,
            played=r["played"],
            won=r["won"],
            drawn=r["drawn"],
            lost=r["lost"],
            goals_for=r["gf"],
            goals_against=r["ga"],
            goal_difference=r["gf"] - r["ga"],
            points=r["points"],
        )
        for i, (name, r) in enumerate(ordered, start=1)
    ]
