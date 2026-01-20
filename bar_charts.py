from dash import html, dcc, Input, Output, State, no_update
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd

# ---- PDF (Render-safe) ----
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from io import BytesIO

# ---------------- DATA ----------------
df_weather = pd.read_csv("predicted_crime_corrected.csv")
severity_order = ["Low", "Medium", "High", "Very High"]

# ---------------- LAYOUT ----------------
def create_bar_layout():
    cities = sorted(df_weather["City"].unique())
    years = sorted(df_weather["Month"].str.split("-").str[0].unique())
    disasters = sorted(df_weather["Disaster"].unique())

    return html.Div([
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

        dbc.Button("Download PDF", id="btn-pdf-bar", color="danger"),
        dcc.Download(id="download-pdf-bar")
    ])

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

        # 🔒 LIMIT TO 2 CITIES
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

    # ---- PDF DOWNLOAD (REPORTLAB) ----
    @app.callback(
        Output("download-pdf-bar", "data"),
        Input("btn-pdf-bar", "n_clicks"),
        State("city-dropdown", "value"),
        State("year-dropdown", "value"),
        State("disaster-checkbox", "value"),
        prevent_initial_call=True
    )
    def download_pdf_bar(n, cities, year, disasters):
        if not n:
            return no_update

        cities = cities[:2]

        df_filtered = df_weather[
            (df_weather["City"].isin(cities)) &
            (df_weather["Month"].str.startswith(str(year))) &
            (df_weather["Disaster"].isin(disasters))
        ]

        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer)
        styles = getSampleStyleSheet()
        content = []

        content.append(Paragraph(f"<b>Weather Report – {year}</b>", styles["Title"]))
        content.append(Spacer(1, 12))

        for _, row in df_filtered.iterrows():
            content.append(
                Paragraph(
                    f"{row['City']} | {row['Month']} | {row['Disaster']} | "
                    f"{row['Value']} {row['Unit']} | Severity: {row['Severity']}",
                    styles["Normal"]
                )
            )
            content.append(Spacer(1, 6))

        doc.build(content)
        buffer.seek(0)

        return dcc.send_bytes(buffer.read(), "weather_report.pdf")
