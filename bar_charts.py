from dash import html, dcc, Input, Output, State, no_update, clientside_callback
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd

# ---------------- DATA ----------------
df_weather = pd.read_csv("predicted_crime_corrected.csv")
severity_order = ["Low", "Medium", "High", "Very High"]

# ---------------- LAYOUT ----------------
def create_bar_layout():
    cities = sorted(df_weather["City"].unique())
    years = sorted(df_weather["Month"].str.split("-").str[0].unique())
    disasters = sorted(df_weather["Disaster"].unique())

    return html.Div(
        id="print-area",   # 👈 important for printing
        children=[
            html.H2("Bar Charts: Weather Forecast by City and Year"),

            dcc.Dropdown(
                id="city-dropdown",
                options=[{"label": c, "value": c} for c in cities],
                value=[cities[0]] if cities else [],
                multi=True,
                style={"width": "50%"}
            ),

            dcc.Dropdown(
                id="year-dropdown",
                options=[{"label": y, "value": y} for y in years],
                value=years[0] if years else None,
                style={"width": "50%"}
            ),

            dcc.Checklist(
                id="disaster-checkbox",
                options=[{"label": d, "value": d} for d in disasters],
                value=disasters,
                style={"width": "50%"}
            ),

            dcc.Graph(id="bar-chart"),
            html.Div(id="bar-chart-writeup", style={"margin": "10px 0"}),

            dbc.Button(
                "Download Page as PDF",
                id="print-pdf-btn",
                color="danger"
            )
        ]
    )

# ---------------- CALLBACKS ----------------
def register_bar_callbacks(app):

    # ---- BAR CHART ----
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

        # 🔒 LIMIT TO MAX 2 CITIES
        cities = cities[:2]

        df_filtered = df_weather[
            (df_weather["City"].isin(cities)) &
            (df_weather["Month"].str.startswith(str(year))) &
            (df_weather["Disaster"].isin(disasters))
        ]

        if df_filtered.empty:
            return px.bar(title="No data available"), ""

        fig = px.bar(
            df_filtered,
            x="Month",
            y="Scale",
            color="Disaster",
            facet_row="City",
            barmode="group",
            title=f"Weather Forecast {year} (Max 2 Cities)",
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

    # ---- CLIENTSIDE PDF (PRINT) ----
    clientside_callback(
        """
        function(n_clicks) {
            if (n_clicks) {
                window.print();
            }
            return null;
        }
        """,
        Output("print-pdf-btn", "n_clicks"),
        Input("print-pdf-btn", "n_clicks")
    )
