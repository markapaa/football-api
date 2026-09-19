import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app


@pytest.fixture()
def client():
    """Κάθε test παίρνει καθαρή βάση SQLite στη μνήμη, οπότε τα tests
    δεν αγγίζουν τα πραγματικά δεδομένα και δεν επηρεάζουν το ένα το άλλο."""
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    TestingSession = sessionmaker(bind=engine, autoflush=False)

    def override_get_db():
        db = TestingSession()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()


def add_match(client, home, away, hg, ag, date="2024-08-10", season="2024-25"):
    return client.post(
        "/matches",
        json={
            "season": season,
            "date": date,
            "home_team": home,
            "away_team": away,
            "home_goals": hg,
            "away_goals": ag,
        },
    )


def test_health(client):
    assert client.get("/health").json() == {"status": "ok"}


def test_create_and_list_matches(client):
    r = add_match(client, "A", "B", 2, 0)
    assert r.status_code == 201
    assert r.json()["home_team"]["name"] == "A"

    matches = client.get("/matches", params={"season": "2024-25"}).json()
    assert len(matches) == 1
    assert matches[0]["away_goals"] == 0


def test_teams_are_created_once(client):
    add_match(client, "A", "B", 1, 0)
    add_match(client, "B", "A", 1, 1, date="2024-08-17")
    teams = client.get("/teams").json()
    assert [t["name"] for t in teams] == ["A", "B"]


def test_get_team_404(client):
    assert client.get("/teams/999").status_code == 404


def test_same_team_rejected(client):
    assert add_match(client, "A", "a", 1, 1).status_code == 422


def test_negative_goals_rejected(client):
    assert add_match(client, "A", "B", -1, 0).status_code == 422


def test_filter_matches_by_team(client):
    add_match(client, "A", "B", 1, 0)
    add_match(client, "C", "D", 2, 2)
    result = client.get("/matches", params={"team": "C"}).json()
    assert len(result) == 1
    assert result[0]["home_team"]["name"] == "C"


def test_standings(client):
    add_match(client, "A", "B", 2, 0)
    add_match(client, "B", "C", 1, 1, date="2024-08-17")
    add_match(client, "C", "A", 0, 3, date="2024-08-24")

    table = client.get("/standings", params={"season": "2024-25"}).json()
    assert [row["team"] for row in table] == ["A", "B", "C"]

    a, b, c = table
    assert (a["points"], a["goal_difference"], a["won"]) == (6, 5, 2)
    assert (b["points"], b["goal_difference"], b["drawn"]) == (1, -2, 1)
    assert (c["points"], c["goal_difference"]) == (1, -3)


def test_standings_requires_season(client):
    assert client.get("/standings").status_code == 422
