"""Εισαγωγή αγώνων από CSV στη βάση.

Δέχεται το format των αρχείων του football-data.co.uk (στήλες Date, HomeTeam,
AwayTeam, FTHG, FTAG), οπότε μπορείς να φορτώσεις πραγματικά δεδομένα
Bundesliga / Europa League με μία εντολή:

    python -m app.importer D1.csv --season 2025-26

Οι αγώνες που υπάρχουν ήδη στη βάση παραλείπονται.
"""
import argparse
import csv
import datetime as dt

from app import crud, schemas
from app.database import Base, SessionLocal, engine


def parse_date(text: str) -> dt.date:
    for fmt in ("%d/%m/%Y", "%d/%m/%y", "%Y-%m-%d"):
        try:
            return dt.datetime.strptime(text.strip(), fmt).date()
        except ValueError:
            continue
    raise ValueError(f"Unrecognised date: {text!r}")


def import_csv(path: str, season: str) -> tuple[int, int]:
    """Επιστρέφει (νέοι αγώνες, αγώνες που υπήρχαν ήδη)."""
    Base.metadata.create_all(engine)
    added = skipped = 0
    with SessionLocal() as db, open(path, newline="", encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            if not row.get("HomeTeam") or not row.get("FTHG"):
                continue  # γραμμές χωρίς αποτέλεσμα (π.χ. αγώνες που δεν έχουν παιχτεί)
            match = schemas.MatchCreate(
                season=season,
                date=parse_date(row["Date"]),
                home_team=row["HomeTeam"],
                away_team=row["AwayTeam"],
                home_goals=int(row["FTHG"]),
                away_goals=int(row["FTAG"]),
            )
            if crud.match_exists(db, match):
                skipped += 1
                continue
            crud.create_match(db, match)
            added += 1
    return added, skipped


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Import matches from a CSV file")
    parser.add_argument("csv_path")
    parser.add_argument("--season", required=True, help='π.χ. "2024-25"')
    args = parser.parse_args()
    added, skipped = import_csv(args.csv_path, args.season)
    print(f"Imported {added} new matches, skipped {skipped} that already existed")