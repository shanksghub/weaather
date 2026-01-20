# rr.py
from dash import html, dcc, Input, Output, State, no_update
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import pandas as pd
import os

# ---------------------- DATA ----------------------
city_coords = {
    "New York City": {"lat": 40.71, "lon": -74.01},
    "San Francisco Bay Area": {"lat": 37.77, "lon": -122.42},
    "Los Angeles": {"lat": 34.05, "lon": -118.24},
    "Chicago": {"lat": 41.88, "lon": -87.63},
    "Houston": {"lat": 29.76, "lon": -95.36},
    "London": {"lat": 51.50, "lon": -0.12},
    "Vancouver": {"lat": 49.28, "lon": -123.12},
    "Toronto": {"lat": 43.65, "lon": -79.38},
    "Tijuana": {"lat": 32.51, "lon": -117.03},
    "Toulouse": {"lat": 43.60, "lon": 1.44},
    "Paris": {"lat": 48.85, "lon": 2.35},
    "Amsterdam": {"lat": 52.37, "lon": 4.90},
    "Bern": {"lat": 46.95, "lon": 7.44},
    "Zurich": {"lat": 47.37, "lon": 8.54},
    "Istanbul": {"lat": 41.01, "lon": 28.97},
    "Tel Aviv": {"lat": 32.09, "lon": 34.78},
    "Stockholm": {"lat": 59.33, "lon": 18.07},
    "Dubai": {"lat": 25.20, "lon": 55.27},
    "Bangalore": {"lat": 12.97, "lon": 77.59},
    "Mumbai": {"lat": 19.07, "lon": 72.88},
    "Chennai": {"lat": 13.08, "lon": 80.27},
    "Gurugram": {"lat": 28.46, "lon": 77.03},
    "Delhi": {"lat": 28.61, "lon": 77.21},
    "Ahmedabad": {"lat": 23.03, "lon": 72.58},
    "Manila": {"lat": 14.60, "lon": 120.98},
    "Singapore": {"lat": 1.35, "lon": 103.82},
    "Tokyo": {"lat": 35.68, "lon": 139.69},
    "Osaka": {"lat": 34.69, "lon": 135.50},
    "Fukuoka": {"lat": 33.59, "lon": 130.40},
    "Shanghai": {"lat": 31.23, "lon": 121.47},
    "Hong Kong": {"lat": 22.32, "lon": 114.17}
}

month_names = {1:"Jan",2:"Feb",3:"Mar",4:"Apr",5:"May",6:"Jun",
               7:"Jul",8:"Aug",9:"Sep",10:"Oct",11:"Nov",12:"Dec"}

# ---------------------- LOAD DATA ----------------------
def load_disaster_data():
    all_dfs = []
    for year in range(2026, 2031):
        path = f"{year}.csv"
        if os.path.exists(path):
            df = pd.read_csv(path)
            df["Year"] = year
            df["Month_num"] = df["Month"].str.split("-").str[1].astype(int)
            all_dfs.append(df)
    if all_dfs:
        return pd.concat(all_dfs, ignore_index=True)
    return pd.DataFrame()

df = load_disaster_data()

# ---------------------- LAYOUT ----------------------
def create_map_layout():
    return html.Div([
        html.H2("Global Disaster Map (2026–2030)", style={"fontSize": 26}),
        dcc.Dropdown(
            id="year-dropdown-map",
            options=[{"label": y, "value": y} for y in sorted(df["Year"].unique())],
            value=sorted(df["Year"].unique())[0] if not df.empty else None,
            style={"width": "30%", "fontSize": 18}
        ),
        dcc.Dropdown(
            id="city-dropdown-map",
            options=[{"label": "All Cities", "value": "All"}] +
                    [{"label": c, "value": c} for c in sorted(city_coords.keys())],
            value="All",
            style={"width": "40%", "fontSize": 18}
        ),
        dcc.Graph(
            id="city-map",
            config={"scrollZoom": True, "displayModeBar": True},
            style={"height": "80vh"}
        ),
        html.Button("Play", id="playpause-btn", n_clicks=0,
                    style={"marginTop":"15px","padding":"12px 28px",
                           "fontSize":"20px","backgroundColor":"#0066FF",
                           "color":"white","borderRadius":"10px","border":"none"}),
        dcc.Slider(
            id="month-slider",
            min=1, max=12, value=1, step=1,
            marks={i: month_names[i] for i in range(1,13)},
            tooltip={"placement":"bottom","always_visible":True}
        ),
        dcc.Interval(id="auto-interval", interval=1000, n_intervals=0, disabled=True),
        dcc.Interval(id="blink-interval", interval=500, n_intervals=0)
    ])

# ---------------------- CALLBACKS ----------------------
def register_map_callbacks(app):

    @app.callback(
        Output("auto-interval", "disabled"),
        Input("playpause-btn", "n_clicks"),
        State("auto-interval", "disabled")
    )
    def toggle_play(n, disabled):
        return not disabled if n else disabled

    @app.callback(
        Output("playpause-btn", "children"),
        Input("auto-interval", "disabled")
    )
    def update_btn(disabled):
        return "Play" if disabled else "Pause"

    @app.callback(
        Output("month-slider", "value"),
        Input("auto-interval", "n_intervals"),
        State("month-slider", "value")
    )
    def advance_month(n, current):
        return 1 if current == 12 else current + 1

    @app.callback(
        Output("city-map", "figure"),
        Input("year-dropdown-map", "value"),
        Input("city-dropdown-map", "value"),
        Input("month-slider", "value"),
        Input("blink-interval", "n_intervals"),
        State("city-map", "relayoutData")
    )
    def update_map(year, city, month, blink, relayout):
        opacity = 1 if blink % 2 == 0 else 0.2
        year_df = df[df["Year"] == year]

        if city == "All":
            month_df = year_df[year_df["Month_num"] == month]
            cities = month_df["City"].unique()
        else:
            month_df = year_df[(year_df["City"] == city) & (year_df["Month_num"] == month)]
            cities = [city]

        fig = go.Figure()

        for c in cities:
            if c not in city_coords:
                continue
            cdata = month_df[month_df["City"] == c]
            coords = city_coords[c]

            hover_blocks = []
            for _, r in cdata.iterrows():
                hover_blocks.append(
                    f"<b>Disaster:</b> {r['Disaster']}<br>"
                    f"<b>Severity:</b> {r['Severity']}<br>"
                    f"<b>Scale:</b> {r['Scale']}<br>"
                    f"<b>Value:</b> {r['Value']} {r['Unit']}<br>"
                    "------------------------"
                )

            fig.add_trace(go.Scattermapbox(
                lat=[coords["lat"]],
                lon=[coords["lon"]],
                mode="markers+text",
                marker=dict(size=18, color="red", opacity=opacity),
                text=[c],
                textposition="top center",
                textfont=dict(color="orange", size=14),
                hovertext="<br>".join(hover_blocks),
                hoverinfo="text"
            ))

        # ---- Retain zoom/pan or zoom to city ----
        if city != "All" and city in city_coords:
            map_center = city_coords[city]
            map_zoom = 5
        elif relayout and "mapbox.center" in relayout:
            map_center = relayout["mapbox.center"]
            map_zoom = relayout.get("mapbox.zoom", 1)
        else:
            map_center = dict(lat=0, lon=0)
            map_zoom = 1

        fig.update_layout(
            mapbox_style="carto-darkmatter",
            mapbox=dict(center=map_center, zoom=map_zoom),
            margin=dict(l=0, r=0, t=0, b=0),
            showlegend=False
        )

        return fig

