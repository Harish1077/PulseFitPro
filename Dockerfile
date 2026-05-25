FROM python:3.11

WORKDIR /app

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

EXPOSE 5000

RUN chmod +x wait-for-db.sh
CMD ["./wait-for-db.sh", "db", "python", "app.py"]