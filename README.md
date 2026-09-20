# Football API

REST API και μικρή ιστοσελίδα για αποτελέσματα ποδοσφαίρου, με **πραγματικά δεδομένα Bundesliga** (σεζόν 2024-25 και 2025-26).
Φτιάχτηκε με FastAPI, SQLAlchemy (SQLite), pytest, Docker και GitHub Actions.

![Αρχική σελίδα](docs/screenshot.png)

## Τι κάνει

- Αποθηκεύει ομάδες και αγώνες σε βάση δεδομένων (SQLite).
- Υπολογίζει τη βαθμολογία κάθε σεζόν (3 βαθμοί νίκη, 1 ισοπαλία· ταξινόμηση με βαθμούς, διαφορά τερμάτων, γκολ υπέρ).
- Υπολογίζει στατιστικά, π.χ. τις πιο δυνατές επιθέσεις της σεζόν (`/stats/top-attacks`).
- Απορρίπτει λανθασμένα δεδομένα (αρνητικά γκολ, ίδια ομάδα εντός και εκτός) και διπλοεγγραφές του ίδιου αγώνα.
- Φορτώνει αγώνες από CSV με εντολή. Ο importer μπορεί να τρέξει πολλές φορές χωρίς να δημιουργεί διπλά δεδομένα.
- Σερβίρει μια ιστοσελίδα (HTML + JavaScript) με βαθμολογία, αγώνες ανά ομάδα και γράφημα θέσης ανά αγωνιστική. Η σελίδα παίρνει τα δεδομένα από το ίδιο το API.

## Endpoints

| Method | Path | Περιγραφή |
|---|---|---|
| GET | `/` | Η ιστοσελίδα |
| GET | `/health` | Έλεγχος ότι η εφαρμογή ζει |
| GET | `/seasons` | Οι σεζόν που υπάρχουν στη βάση (πρώτη η νεότερη) |
| GET | `/teams` | Λίστα ομάδων |
| GET | `/teams/{id}` | Μία ομάδα (404 αν δεν υπάρχει) |
| GET | `/matches?season=&team=&limit=&offset=` | Αγώνες με φίλτρα και σελιδοποίηση (limit έως 200) |
| POST | `/matches` | Προσθήκη αγώνα (422 για μη έγκυρα δεδομένα, 409 αν υπάρχει ήδη) |
| GET | `/standings?season=2025-26` | Βαθμολογία σεζόν (το `season` είναι υποχρεωτικό) |
| GET | `/stats/top-attacks?season=2025-26&limit=5` | Οι ομάδες με τα περισσότερα γκολ υπέρ, με μέσο όρο ανά αγώνα |

Η διαδραστική τεκμηρίωση (Swagger UI) φτιάχνεται αυτόματα στο `/docs`.

## Τοπική εκτέλεση

Χρειάζεται Python 3.12 ή νεότερη.

```bash
python -m venv .venv
.venv\Scripts\activate             # Windows
# source .venv/bin/activate        # Mac / Linux

pip install -r requirements-dev.txt

# φόρτωση πραγματικών δεδομένων (δες την ενότητα παρακάτω)
python -m app.importer D1_2425.csv --season 2024-25
python -m app.importer D1.csv --season 2025-26

uvicorn app.main:app --reload
```

Άνοιξε http://127.0.0.1:8000 (η σελίδα) ή http://127.0.0.1:8000/docs (το API).

## Δεδομένα

Τα αποτελέσματα προέρχονται από το [football-data.co.uk](https://www.football-data.co.uk) (Bundesliga, αρχεία CSV). Ο importer διαβάζει τις στήλες `Date`, `HomeTeam`, `AwayTeam`, `FTHG`, `FTAG`.

- `D1.csv`: Bundesliga 2025-26
- `D1_2425.csv`: Bundesliga 2024-25

Για άλλη σεζόν ή λίγκα κατεβάζεις το αντίστοιχο CSV και δίνεις το όνομα της σεζόν στο `--season`. Αν φορτώσεις το ίδιο αρχείο δεύτερη φορά, οι αγώνες που υπάρχουν ήδη παραλείπονται και η εντολή γράφει πόσοι προστέθηκαν και πόσοι παραλείφθηκαν.

Το `sample_data/sample_matches.csv` έχει φανταστικές ομάδες και είναι μόνο για γρήγορη δοκιμή.

## Tests

```bash
pytest -v
```

Τα tests τρέχουν σε βάση στη μνήμη, οπότε δεν αγγίζουν τα πραγματικά δεδομένα. Καλύπτουν τη δημιουργία και λίστα αγώνων, τα φίλτρα, τη βαθμολογία, τα στατιστικά, τους κανόνες εγκυρότητας και την απόρριψη διπλών αγώνων. Το GitHub Actions τα τρέχει σε κάθε push και χτίζει και το Docker image.

## Docker

```bash
docker build -t football-api .
docker run -d --name football-api -p 8000:8000 -v football-data:/app/data football-api

# φόρτωση δεδομένων μέσα στο container
docker cp D1.csv football-api:/app/D1.csv
docker exec football-api python -m app.importer D1.csv --season 2025-26
```

Το volume `football-data` κρατά τη βάση ακόμα κι αν το container σβηστεί.

## Δομή

```
app/
  main.py       endpoints
  schemas.py    validation εισόδου/εξόδου (Pydantic)
  models.py     πίνακες βάσης (SQLAlchemy)
  crud.py       λογική δεδομένων, βαθμολογία, στατιστικά
  database.py   σύνδεση με τη βάση
  importer.py   εισαγωγή CSV (χωρίς διπλοεγγραφές)
  static/       η ιστοσελίδα (index.html)
docs/           στιγμιότυπο οθόνης
tests/          pytest
sample_data/    δοκιμαστικά δεδομένα
Dockerfile
.github/workflows/ci.yml
```

## Τεχνολογίες

Python · FastAPI · Pydantic · SQLAlchemy 2.0 · SQLite · pytest · Docker · GitHub Actions · HTML/CSS/JavaScript