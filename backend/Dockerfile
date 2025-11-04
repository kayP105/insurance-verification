FROM python:3.10
WORKDIR /app
COPY . /app
RUN pip install --upgrade pip
RUN pip install fastapi uvicorn sqlalchemy pandas joblib shap plotly spacy rapidfuzz durable_rules pytesseract lightgbm pdf2image python-multipart
RUN python -m spacy download en_core_web_sm
RUN apt-get update && apt-get install -y poppler-utils

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
