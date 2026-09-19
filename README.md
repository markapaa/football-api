# Football API

Μικρό REST API με FastAPI, SQLAlchemy (SQLite), pytest, Docker και GitHub Actions.
Επιστρέφει αγώνες και ομάδες ποδοσφαίρου και υπολογίζει τη βαθμολογία μιας σεζόν.

## Endpoints

| Method | Path | Περιγραφή |
|---|---|---|
| GET | `/health` | Έλεγχος ότι η εφαρμογή ζει |
| GET | `/teams` | Λίστα ομάδων |
| GET | `/teams/{id}` | Μία ομάδα (404 αν δεν υπάρχει) |
| GET | `/matches?season=&team=&limit=&offset=` | Αγώνες με φίλτρα και σελιδοποίηση |
| POST | `/matches` | Προσθήκη αγώνα |
| GET | `/standings?season=2024-25` | Βαθμολογία (3 βαθμοί νίκη, 1 ισοπαλία) |

Η διαδραστική τεκμηρίωση (Swagger UI) παράγεται αυτόματα στο `/docs`.

## Τοπική εκτέλεση

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt

python -m app.importer sample_data/sample_matches.csv --season 2024-25
uvicorn app.main:app --reload
```

Άνοιξε http://127.0.0.1:8000/docs

## Tests

```bash
pytest -v
```

## Docker

```bash
docker build -t football-api .
docker run -d --name football-api -p 8000:8000 -v football-data:/app/data football-api

# φόρτωση δεδομένων μέσα στο container
docker exec football-api python -m app.importer sample_data/sample_matches.csv --season 2024-25
```

## Πραγματικά δεδομένα

Το `sample_data/sample_matches.csv` έχει φανταστικές ομάδες. Για πραγματικά
δεδομένα κατέβασε CSV από το https://www.football-data.co.uk (π.χ. Bundesliga)
και φόρτωσέ το με τον ίδιο importer, δίνοντας τη σεζόν στο `--season`.

## Δομή

```
app/
  main.py       endpoints
  schemas.py    validation εισόδου/εξόδου (Pydantic)
  models.py     πίνακες βάσης (SQLAlchemy)
  crud.py       λογική δεδομένων και υπολογισμός βαθμολογίας
  database.py   σύνδεση με τη βάση
  importer.py   εισαγωγή CSV
tests/          pytest
```
