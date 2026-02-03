# Copyright (c) Mike Kipnis
import os
import time
import uuid

import liquibook

import dash
import dash_bootstrap_components as dbc
from dash import html
from dash import html, dcc, Input, Output

from components import Orders
from components.PriceDepth import PriceDepthGrid
from components.OrderEntry import OrderFormComponent
from components.Orders import TradeOrderHistory
from components.OrderCancelModify import OrderCancelModifyComponent
from liquibook_adapter.LiquiBookAdapter import LiquiBookAdapter

import logging

# ----------------------------
# Logging configuration
# ----------------------------
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("liquibook_adapter.log", "a"),
    ]
)

logger = logging.getLogger("LiquiBookAdapter")

liquibook_adapter_container = {}
sandbox_instrument = {'symbol': 'SANDBOX', 'market_price': 10095}

# ----------------------------
# LiquiBook Sandbox class
# ----------------------------
class LiquiBook_Sandbox:
    def __init__(self, prefix: str, app: dash.Dash):
        self.prefix = prefix
        self.app = app

        self.order_form_component = OrderFormComponent(self.prefix)
        self.order_cancel_modify = OrderCancelModifyComponent(self.prefix)
        self.trade_order_history = TradeOrderHistory(self.prefix)
        self.price_depth_grid = PriceDepthGrid(self.prefix)

    def layout(self):

        return dbc.Container([
            dbc.Navbar(
                dbc.NavbarBrand(
                    "Matching Engine - Liquibook",
                    href="#",
                    style={"margin-left": "20px", "fontSize": "20px"}
                ),
                color="Info",
                dark=True
            ),
            dbc.Row(
                dbc.Col(
                    html.Hr(style={"borderTop": "2px solid #6c757d", "margin": "0px 10px 20px"}),
                    width=12
                )
            ),
            dbc.Row([
                dbc.Col(self.price_depth_grid.layout()),
                dbc.Col([
                    dbc.Row([self.order_form_component.layout()]),
                    dbc.Row([self.order_cancel_modify.layout()])
                ])
            ], className="p-3"),
            dbc.Row([self.trade_order_history.layout()], className="p-3"),
            html.Div([
                "For support, contact: ",
                html.A(
                    "mike.kipnis@gmail.com",
                    href="mailto:mike.kipnis@gmail.com",
                    style={"textDecoration": "underline", "color": "#AAAAAA"},
                ),
            ], style={
                "fontSize": "12px",
                "color": "#AAAAAA",
                "marginTop": "8px",
                "textAlign": "center",
                "width": "100%",
            }),
            dcc.Store(id="liquibook-prefix", data=self.prefix),
            dbc.Label(id="liquibook-prefix-out"),
        ], fluid=True, className="p-0")

# =============================
# Dash App Initialization
# =============================
app = dash.Dash(
    __name__,
    suppress_callback_exceptions=False,
    title="Matching Engine - Liquibook",
    external_stylesheets=[dbc.themes.SUPERHERO],
)
server = app.server  # Gunicorn expects this


def register_all_callbacks_for_prefix(prefix):
    OrderFormComponent.register_callbacks(app, prefix, liquibook_adapter_container)
    OrderCancelModifyComponent.register_callbacks(app, prefix, liquibook_adapter_container)
    TradeOrderHistory.register_callbacks(app, prefix)
    PriceDepthGrid.register_callbacks(app, prefix)

# ---------------------------
# Layout factory
# ----------------------------
def serve_layout():

    prefix = str(uuid.uuid4())[:8]
    logger.info(f"New reload prefix: {prefix}")
    register_all_callbacks_for_prefix(prefix)
    sandbox = LiquiBook_Sandbox(prefix, app)
    return sandbox.layout()


app.layout = serve_layout

# ----------------------------
# Adapter helper
# ----------------------------
def get_adapter(prefix: str):
    if prefix not in liquibook_adapter_container:
        logger.info(f"Creating LiquiBookAdapter for {prefix}")
        adapter = LiquiBookAdapter(prefix, sandbox_instrument)
        liquibook_adapter_container[prefix] = adapter

    return liquibook_adapter_container[prefix]

# =============================
# Callbacks
# =============================
@app.callback(
    Output("liquibook-prefix-out", "children"),
    Input(f"liquibook-prefix", "data"),  # dummy input to trigger on load
)
def setup_liquibook(liquibook_prefix):
    liquibook_adapter = get_adapter(liquibook_prefix)
    liquibook_adapter.update_order_book_data()
    print(f"Callback is good {liquibook_prefix}")
    return f"{liquibook_prefix}"

# ----------------------------
# Main
# ----------------------------
if __name__ == '__main__':
    host = os.getenv("DASH_HOST", "127.0.0.1")
    port = int(os.getenv("DASH_PORT", "8050"))
    debug = os.getenv("DASH_DEBUG", "true").lower() == "true"

    app.run(host=host, port=port, debug=debug)
