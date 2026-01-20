import dash
from dash import html, dcc, Input, Output, State
import plotly.graph_objects as go
import pandas as pd

# Define color mapping for severity
severity_colors = {
    "Low": "green",
    "Medium": "violet",
    "High": "orange",
    "Very High": "blue"
}

# Available years
available_years = ["2026", "2027", "2028", "2029", "2030"]


def create_treemap_layout():
    return html.Div([
        html.H2("Treemaps: Weather Data Hierarchy"),

        dcc.Store(id="selected-year"),
        dcc.Store(id="selected-month"),
        dcc.Store(id="selected-city"),

        dcc.Graph(id="year-treemap", style={"height": "400px"}),
        dcc.Graph(id="month-treemap", style={"height": "400px", "display": "none"}),
        dcc.Graph(id="city-treemap", style={"height": "400px", "display": "none"}),
        dcc.Graph(id="disaster-treemap", style={"height": "400px", "display": "none"})
    ])


def create_year_treemap():
    fig = go.Figure(go.Treemap(
        labels=available_years,
        parents=[""] * len(available_years),
        values=[1] * len(available_years),
        hoverinfo="none"   # 👈 NO HOVER
    ))
    fig.update_layout(title="Select Year", margin=dict(t=40, l=0, r=0, b=0))
    return fig


def create_month_treemap(year):
    months = [f"{year}-{i:02d}" for i in range(1, 13)]
    fig = go.Figure(go.Treemap(
        labels=[year] + months,
        parents=[""] + [year] * 12,
        values=[1] * 13,
        hoverinfo="none"   # 👈 NO HOVER
    ))
    fig.update_layout(title=f"Select Month in {year}", margin=dict(t=40, l=0, r=0, b=0))
    return fig


def create_city_treemap(year, month):
    df = pd.read_csv(f"{year}.csv")
    df = df[df["Month"] == month]
    cities = df["City"].unique().tolist()

    fig = go.Figure(go.Treemap(
        labels=[month] + cities,
        parents=[""] + [month] * len(cities),
        values=[1] * (len(cities) + 1),
        hoverinfo="none"   # 👈 NO HOVER
    ))
    fig.update_layout(title=f"Select City in {month}", margin=dict(t=40, l=0, r=0, b=0))
    return fig


def create_disaster_treemap(year, month, city):
    df = pd.read_csv(f"{year}.csv")
    df = df[(df["Month"] == month) & (df["City"] == city)]

    labels = [city] + df["Disaster"].tolist()
    parents = [""] + [city] * len(df)
    values = [1] * (len(df) + 1)

    colors = ["lightgrey"] + [severity_colors.get(s, "grey") for s in df["Severity"].tolist()]

    customdata = [["", "", "", ""]] + df[["Value", "Unit", "Severity", "Scale"]].values.tolist()

    fig = go.Figure(go.Treemap(
        labels=labels,
        parents=parents,
        values=values,
        marker=dict(colors=colors),
        customdata=customdata,
        hovertemplate=(
            "<b>%{label}</b><br>"
            "Value: %{customdata[0]} %{customdata[1]}<br>"
            "Severity: %{customdata[2]}<br>"
            "Scale: %{customdata[3]}"
            "<extra></extra>"
        )
    ))

    fig.update_layout(title=f"Disasters in {city} ({month})", margin=dict(t=40, l=0, r=0, b=0))
    return fig


def register_treemap_callbacks(app):

    @app.callback(
        Output("selected-year", "data"),
        Output("selected-month", "data"),
        Output("selected-city", "data"),

        Output("year-treemap", "figure"),
        Output("month-treemap", "figure"),
        Output("city-treemap", "figure"),
        Output("disaster-treemap", "figure"),

        Output("year-treemap", "style"),
        Output("month-treemap", "style"),
        Output("city-treemap", "style"),
        Output("disaster-treemap", "style"),

        Input("year-treemap", "clickData"),
        Input("month-treemap", "clickData"),
        Input("city-treemap", "clickData"),
        Input("disaster-treemap", "clickData"),

        State("selected-year", "data"),
        State("selected-month", "data"),
        State("selected-city", "data"),
    )
    def navigation(year_click, month_click, city_click, disaster_click, year, month, city):

        ctx = dash.callback_context
        if not ctx.triggered:
            return None, None, None, create_year_treemap(), go.Figure(), go.Figure(), go.Figure(), \
                   {"display": "block"}, {"display": "none"}, {"display": "none"}, {"display": "none"}

        trigger = ctx.triggered[0]["prop_id"].split(".")[0]

        # --- Year Click ---
        if trigger == "year-treemap" and year_click:
            label = year_click["points"][0]["label"]
            return label, None, None, create_year_treemap(), create_month_treemap(label), go.Figure(), go.Figure(), \
                   {"display": "none"}, {"display": "block"}, {"display": "none"}, {"display": "none"}

        # --- Month Click ---
        if trigger == "month-treemap" and month_click:
            label = month_click["points"][0]["label"]
            if label in available_years:
                return None, None, None, create_year_treemap(), go.Figure(), go.Figure(), go.Figure(), \
                       {"display": "block"}, {"display": "none"}, {"display": "none"}, {"display": "none"}

            return year, label, None, create_year_treemap(), create_month_treemap(year), create_city_treemap(year, label), go.Figure(), \
                   {"display": "none"}, {"display": "none"}, {"display": "block"}, {"display": "none"}

        # --- City Click ---
        if trigger == "city-treemap" and city_click:
            label = city_click["points"][0]["label"]

            if label == month:
                return year, None, None, create_year_treemap(), create_month_treemap(year), go.Figure(), go.Figure(), \
                       {"display": "none"}, {"display": "block"}, {"display": "none"}, {"display": "none"}

            return year, month, label, create_year_treemap(), create_month_treemap(year), create_city_treemap(year, month), create_disaster_treemap(year, month, label), \
                   {"display": "none"}, {"display": "none"}, {"display": "none"}, {"display": "block"}

        # --- Disaster Click (Back to City) ---
        if trigger == "disaster-treemap" and disaster_click:
            label = disaster_click["points"][0]["label"]

            if label == city:
                return year, month, None, create_year_treemap(), create_month_treemap(year), create_city_treemap(year, month), go.Figure(), \
                       {"display": "none"}, {"display": "none"}, {"display": "block"}, {"display": "none"}

        raise dash.exceptions.PreventUpdate
