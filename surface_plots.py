from dash import html, dcc, Input, Output
import plotly.express as px
import pandas as pd

df_weather = pd.read_csv("predicted_crime_corrected.csv")

severity_colors = {
    "Low": "green",
    "Medium": "violet",
    "High": "orange",
    "Very High": "blue"
}

severity_order = ["Low", "Medium", "High", "Very High"]

def create_surface_layout():
    return html.Div([
        html.H2("3D Surface Plots: Weather Data"),
        dcc.Dropdown(
            id="surface-city-dropdown",
            options=[{"label": city, "value": city} for city in df_weather["City"].unique()],
            value=[df_weather["City"].unique()[0]],
            multi=True,
            style={"width": "50%"}
        ),
        dcc.Dropdown(
            id="surface-weather-dropdown",
            options=[{"label": weather, "value": weather} for weather in df_weather["Disaster"].unique()],
            value=df_weather["Disaster"].unique()[0],
            style={"width": "50%"}
        ),
        dcc.Graph(id="surface-plot"),
        html.H3("3D Subplots: Weather Scaling by City"),
        dcc.Dropdown(
            id="subplot-city-dropdown",
            options=[{"label": city, "value": city} for city in df_weather["City"].unique()],
            value=df_weather["City"].unique()[0],
            style={"width": "50%"}
        ),
        dcc.Graph(id="subplot-3d")
    ])

def register_surface_callbacks(app):

    @app.callback(
        Output("surface-plot", "figure"),
        Input("surface-city-dropdown", "value"),
        Input("surface-weather-dropdown", "value")
    )
    def update_surface_plot(cities, weather):
        df_filtered = df_weather[
            (df_weather["City"].isin(cities)) &
            (df_weather["Disaster"] == weather)
        ]

        fig = px.scatter_3d(
            df_filtered,
            x="Month",
            y="City",
            z="Value",
            color="Severity",
            category_orders={"Severity": severity_order},
            color_discrete_map=severity_colors,
            title=f"3D Surface: {weather} by City"
        )
        return fig

    @app.callback(
        Output("subplot-3d", "figure"),
        Input("subplot-city-dropdown", "value")
    )
    def update_subplot_3d(city):
        df_filtered = df_weather[df_weather["City"] == city]

        fig = px.scatter_3d(
            df_filtered,
            x="Month",
            y="Disaster",
            z="Scale",
            color="Severity",
            category_orders={"Severity": severity_order},
            color_discrete_map=severity_colors,
            title=f"3D Subplot: Weather Scaling for {city}"
        )
        return fig
