FROM python:3.12-slim

WORKDIR /app

# Πρώτα τα requirements: αν δεν αλλάξουν, το Docker ξαναχρησιμοποιεί το cache
# και τα rebuilds είναι γρήγορα.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app
COPY sample_data ./sample_data
COPY D1.csv D1_2425.csv ./

# Η βάση SQLite ζει στο /app/data· χρησιμοποίησε volume ώστε να μη χάνονται δεδομένα.
RUN mkdir -p data
VOLUME ["/app/data"]

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
