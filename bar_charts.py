from dash import html, dcc, Input, Output, State, no_update
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.io as pio
import pandas as pd

df_weather = pd.read_csv("predicted_crime_corrected.csv")

severity_order = ["Low", "Medium", "High", "Very High"]


def create_bar_layout():
    cities = df_weather["City"].unique()
    years = sorted(df_weather["Month"].str.split("-").str[0].unique())
    disasters = df_weather["Disaster"].unique()

    return html.Div([
        html.H2("Bar Charts: Weather Forecast by City and Year"),

        dcc.Dropdown(
            id="city-dropdown",
            options=[{"label": city, "value": city} for city in cities],
            value=[cities[0]] if len(cities) > 0 else [],
            multi=True,
            style={"width": "50%"}
        ),

        dcc.Dropdown(
            id="year-dropdown",
            options=[{"label": year, "value": year} for year in years],
            value=years[0] if len(years) > 0 else None,
            style={"width": "50%"}
        ),

        dcc.Checklist(
            id="disaster-checkbox",
            options=[{"label": disaster, "value": disaster} for disaster in disasters],
            value=list(disasters),
            style={"width": "50%"}
        ),

        dcc.Graph(id="bar-chart"),
        html.Div(id="bar-chart-writeup", style={"margin": "10px 0"}),

        dbc.Button("Download PDF", id="btn-pdf-bar", color="danger", style={"margin-right": "10px"}),
        dbc.Button("Download PNG", id="btn-png-bar", color="success"),

        dcc.Download(id="download-pdf-bar"),
        dcc.Download(id="download-png-bar")
    ])


def register_bar_callbacks(app):

    @app.callback(
        Output("bar-chart", "figure"),
        Output("bar-chart-writeup", "children"),
        Input("city-dropdown", "value"),
        Input("year-dropdown", "value"),
        Input("disaster-checkbox", "value")
    )
    def update_bar_chart(cities, year, disasters):

        if not cities or not year or not disasters:
            return px.bar(title="No data selected"), ""

        df_filtered = df_weather[
            (df_weather["City"].isin(cities)) &
            (df_weather["Month"].str.startswith(str(year))) &
            (df_weather["Disaster"].isin(disasters))
        ]

        if df_filtered.empty:
            return px.bar(title="No data available for selection"), ""

        fig = px.bar(
            df_filtered,
            x="Month",
            y="Scale",
            color="Disaster",
            facet_row="City",
            barmode="group",
            title=f"Weather Forecast for {year}",
            category_orders={"Severity": severity_order}
        )

        max_row = df_filtered.loc[df_filtered["Value"].idxmax()]
        min_row = df_filtered.loc[df_filtered["Value"].idxmin()]

        writeup = (
            f"Highest: {max_row['Disaster']} in {max_row['City']} "
            f"({max_row['Value']} {max_row['Unit']}) | "
            f"Lowest: {min_row['Disaster']} in {min_row['City']} "
            f"({min_row['Value']} {min_row['Unit']})"
        )

        return fig, writeup


    # ---- DOWNLOAD PDF (FIXED) ----
    @app.callback(
        Output("download-pdf-bar", "data"),
        Input("btn-pdf-bar", "n_clicks"),
        State("bar-chart", "figure"),
        prevent_initial_call=True
    )
    def download_pdf_bar(n, fig):
        if not n or fig is None:
            return no_update
        pdf_bytes = pio.to_image(fig, format="pdf", width=900, height=700)
        return dcc.send_bytes(pdf_bytes, "bar_chart.pdf")


    # ---- DOWNLOAD PNG (FIXED) ----
    @app.callback(
        Output("download-png-bar", "data"),
        Input("btn-png-bar", "n_clicks"),
        State("bar-chart", "figure"),
        prevent_initial_call=True
    )
    def download_png_bar(n, fig):
        if not n or fig is None:
            return no_update
        img_bytes = pio.to_image(fig, format="png", width=900, height=700)
        return dcc.send_bytes(img_bytes, "bar_chart.png")
