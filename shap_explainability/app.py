import dash
import dash_core_components as dcc
import dash_html_components as html
import shap
import joblib
import pandas as pd
import plotly.figure_factory as ff

X = pd.read_csv(r"C:\Users\Karunya Paul\OneDrive\Desktop\insurance-verification-project\data\insurance_claims.csv")
model = joblib.load(r"C:\Users\Karunya Paul\OneDrive\Desktop\insurance-verification-project\backend\eligibility_model.pkl")
explainer = shap.TreeExplainer(model)
shap_values = explainer.shap_values(X)

fig = shap.summary_plot(shap_values, X, plot_type="bar", show=False)

app = dash.Dash(__name__)
app.layout = html.Div([
    html.H1("Eligibility Model Explainability - SHAP"),
    dcc.Graph(figure=fig)
])

if __name__ == "__main__":
    app.run_server(debug=True)
