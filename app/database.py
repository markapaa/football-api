"""Σύνδεση με τη βάση δεδομένων (SQLAlchemy).

Το DATABASE_URL διαβάζεται από environment variable, ώστε το ίδιο code να
τρέχει τοπικά (SQLite αρχείο), στα tests (SQLite στη μνήμη) ή αργότερα με
Postgres, χωρίς αλλαγές στον κώδικα.
"""
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./data/football.db")

if DATABASE_URL.startswith("sqlite"):
    os.makedirs("data", exist_ok=True)
    connect_args = {"check_same_thread": False}
else:
    connect_args = {}

engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(bind=engine, autoflush=False)


class Base(DeclarativeBase):
    pass


def get_db():
    """Dependency: ανοίγει session για κάθε request και το κλείνει στο τέλος."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
