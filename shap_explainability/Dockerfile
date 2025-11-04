FROM python:3.10
WORKDIR /app
COPY . /app
RUN pip install dash plotly shap joblib pandas dash_html_components dash_core_components
CMD ["python", "app.py"]
