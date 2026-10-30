
FROM python:3.13

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY account/ ./account/
COPY backend/ ./backend/
COPY dashboard/ ./dashboard/
COPY static/ ./static/
COPY pydomus/manage.py ./manage.py
COPY pydomus/pydomus/ ./pydomus/

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
