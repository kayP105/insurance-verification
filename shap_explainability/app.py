import shap
import joblib
import pandas as pd
import plotly.express as px

# Load data and model
X = pd.read_csv(r"C:\Users\Karunya Paul\OneDrive\Desktop\insurance-verification-project\data\insurance_claims.csv")  # demo data
model = joblib.load(r"C:\Users\Karunya Paul\OneDrive\Desktop\insurance-verification-project\backend\eligibility_model.pkl")

explainer = shap.TreeExplainer(model)
shap_values = explainer.shap_values(X)

# Plot summary as HTML or in Dash
shap.summary_plot(shap_values, X, plot_type="bar")
