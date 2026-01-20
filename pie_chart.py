from dash import html, dcc, Input, Output, State, no_update
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.io as pio
import pandas as pd

df_pie = pd.read_csv("above_threshold_counts.csv")


def create_pie_layout():
    years = sorted(df_pie["Year"].unique())
    cities = sorted(df_pie["City"].unique())
    disasters = sorted(df_pie["Disaster"].unique())

    return html.Div([
        html.H2("Pie Chart: Weather Events Above Threshold"),

        dcc.Dropdown(
            id="city-dropdown-pie",
            options=[{"label": city, "value": city} for city in cities],
            value=cities[0] if len(cities) > 0 else None,
            style={"width": "50%"}
        ),

        dcc.Dropdown(
            id="year-dropdown-pie",
            options=[{"label": year, "value": year} for year in years],
            value=years[0] if len(years) > 0 else None,
            style={"width": "50%"}
        ),

        dcc.Checklist(
            id="disaster-checkbox-pie",
            options=[{"label": disaster, "value": disaster} for disaster in disasters],
            value=list(disasters),
            style={"width": "50%"}
        ),

        dcc.Graph(id="pie-chart"),

        dbc.Button("Download PDF", id="btn-pdf-pie", color="danger", style={"margin-top": "10px"}),

        dcc.Download(id="download-pdf-pie")
    ])


def register_pie_callbacks(app):

    @app.callback(
        Output("pie-chart", "figure"),
        Input("city-dropdown-pie", "value"),
        Input("year-dropdown-pie", "value"),
        Input("disaster-checkbox-pie", "value")
    )
    def update_pie_chart(city, year, disasters):

        if not city or not year or not disasters:
            return px.pie(title="No data selected")

        df_filtered = df_pie[
            (df_pie["City"] == city) &
            (df_pie["Year"] == year) &
            (df_pie["Disaster"].isin(disasters))
        ]

        if df_filtered.empty:
            return px.pie(title="No data available for selection")

        fig = px.pie(
            df_filtered,
            values="Count",
            names="Disaster",
            title=f"Weather Conditions Above Threshold for {city} in {year}"
        )
        fig.update_traces(textposition="inside", textinfo="percent+label")

        return fig


    # ---- DOWNLOAD PDF (FIXED) ----
    @app.callback(
        Output("download-pdf-pie", "data"),
        Input("btn-pdf-pie", "n_clicks"),
        State("pie-chart", "figure"),
        prevent_initial_call=True
    )
    def download_pdf_pie(n, fig):
        if not n or fig is None:
            return no_update
        pdf_bytes = pio.to_image(fig, format="pdf", width=900, height=700)
        return dcc.send_bytes(pdf_bytes, "pie_chart.pdf")
