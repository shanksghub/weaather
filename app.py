import dash
from dash import html, dcc, Input, Output, State
import dash_bootstrap_components as dbc

from bar_charts import create_bar_layout, register_bar_callbacks
from pie_chart import create_pie_layout, register_pie_callbacks
from surface_plots import create_surface_layout, register_surface_callbacks
from treemap_app import create_treemap_layout, register_treemap_callbacks
from rr import create_map_layout, register_map_callbacks

# ---------------------- MOCK DB ----------------------
users_db = {}

# ---------------------- APP INIT ----------------------
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.LUX], suppress_callback_exceptions=True)

app.layout = html.Div([
    dcc.Store(id="current-user", data={"logged_in": False, "email": ""}),
    dcc.Location(id="url"),
    html.Div(id="page-content")
])

# ---------------------- UI COMPONENTS ----------------------

def signup_login_page():
    return html.Div([
        html.H2("Signup / Login"),
        dbc.Input(id="email", placeholder="Email", type="text", style={"margin": "8px"}),
        dbc.Input(id="password", placeholder="Password", type="password", style={"margin": "8px"}),
        dbc.Button("Signup", id="signup-btn", color="success", style={"margin": "8px"}),
        dbc.Button("Login", id="login-btn", color="primary", style={"margin": "8px"}),
        html.Div(id="auth-message", style={"margin": "10px", "color": "red"})
    ])


def navbar():
    return dbc.NavbarSimple(
        children=[
            dbc.NavItem(dbc.NavLink("Home", href="/home")),
            dbc.NavItem(dbc.NavLink("Bar Charts", href="/bar-charts")),
            dbc.NavItem(dbc.NavLink("Treemaps", href="/treemaps")),
            dbc.NavItem(dbc.NavLink("Pie Chart", href="/pie-chart")),
            dbc.NavItem(dbc.NavLink("3D Surface Plots", href="/3d-surface")),
            dbc.NavItem(dbc.NavLink("Map", href="/rr-map")),
            dbc.NavItem(dbc.NavLink("Logout", href="/logout"))
        ],
        brand="Weather Dashboard",
        color="dark",
        dark=True,
        className="mb-4"
    )


def home_page():
    return html.Div([
        navbar(),
        html.H2("Welcome to Weather Dashboard"),
        html.P("Select a tab to visualize weather data.")
    ])


def bar_charts_page():
    return html.Div([
        navbar(),
        create_bar_layout()
    ])


def treemaps_page():
    return html.Div([
        navbar(),
        create_treemap_layout()
    ])


def pie_chart_page():
    return html.Div([
        navbar(),
        create_pie_layout()
    ])


def surface_plots_page():
    return html.Div([
        navbar(),
        create_surface_layout()
    ])


def rr_page():
    return html.Div([
        navbar(),
        create_map_layout()
    ])

# ---------------------- ROUTING ----------------------

@app.callback(
    Output("page-content", "children"),
    Input("url", "pathname"),
    Input("current-user", "data")
)
def render_page(path, user):
    if not user["logged_in"]:
        return signup_login_page()

    if path in ["/", "/home"]:
        return home_page()
    if path == "/bar-charts":
        return bar_charts_page()
    if path == "/treemaps":
        return treemaps_page()
    if path == "/pie-chart":
        return pie_chart_page()
    if path == "/3d-surface":
        return surface_plots_page()
    if path == "/rr-map":
        return rr_page()
    if path == "/logout":
        return signup_login_page()

    return home_page()

# ---------------------- AUTH ----------------------

@app.callback(
    Output("current-user", "data"),
    Output("auth-message", "children"),
    Input("signup-btn", "n_clicks"),
    Input("login-btn", "n_clicks"),
    State("email", "value"),
    State("password", "value"),
    State("current-user", "data"),
    prevent_initial_call=True
)
def auth(signup, login, email, password, current):
    ctx = dash.callback_context
    button = ctx.triggered[0]["prop_id"].split(".")[0]

    if not email or not password:
        return current, "Enter email & password"

    if button == "signup-btn":
        if email in users_db:
            return current, "User already exists"
        users_db[email] = password
        return {"logged_in": True, "email": email}, "Signup successful!"

    if button == "login-btn":
        if email not in users_db or users_db[email] != password:
            return current, "Invalid login"
        return {"logged_in": True, "email": email}, "Login successful!"

    return current, ""

# ---------------------- REGISTER ALL CALLBACKS ----------------------

register_bar_callbacks(app)
register_pie_callbacks(app)
register_surface_callbacks(app)
register_treemap_callbacks(app)
register_map_callbacks(app)

# ---------------------- RUN ----------------------

if __name__ == "__main__":
    app.run(debug=True, port=9091)
