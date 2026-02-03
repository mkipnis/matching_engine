# Copyright (c) Mike Kipnis - DistributedATS

import os
import uuid
import logging

import dash
import dash_bootstrap_components as dbc
from dash import html, dcc, Input, Output, MATCH

from components.PriceDepth import PriceDepthGrid
from components.OrderEntry import OrderFormComponent
from components.Orders import TradeOrderHistory
from components.OrderCancelModify import OrderCancelModifyComponent
from liquibook_adapter.LiquiBookAdapter import LiquiBookAdapter

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
    ],
)

logger = logging.getLogger("LiquibookAdapter")

# ----------------------------
# Globals
# ----------------------------
liquibook_adapter_container = {}
sandbox_instrument = {"symbol": "SANDBOX", "market_price": 10095}

# ----------------------------
# LiquiBook Sandbox class
# ----------------------------
class LiquiBook_Sandbox:
    def __init__(self, prefix: str):
        self.prefix = prefix

        self.order_form_component = OrderFormComponent(prefix)
        self.order_cancel_modify = OrderCancelModifyComponent(prefix)
        self.trade_order_history = TradeOrderHistory(prefix)
        self.price_depth_grid = PriceDepthGrid(prefix)

    def layout(self):
        return dbc.Container(
            [
                dbc.Navbar(
                    dbc.NavbarBrand(
                        "Matching Engine - Liquibook",
                        href="#",
                        style={"margin-left": "20px", "fontSize": "20px"},
                    ),
                    color="Info",
                    dark=True,
                ),
                dbc.Row(
                    dbc.Col(
                        html.Hr(
                            style={
                                "borderTop": "2px solid #6c757d",
                                "margin": "0px 10px 20px",
                            }
                        ),
                        width=12,
                    )
                ),
                dbc.Row(
                    [
                        dbc.Col(self.price_depth_grid.layout()),
                        dbc.Col(
                            [
                                dbc.Row(self.order_form_component.layout()),
                                dbc.Row(self.order_cancel_modify.layout()),
                            ]
                        ),
                    ],
                    className="p-3",
                ),
                dbc.Row(self.trade_order_history.layout(), className="p-3"),
                html.Div(
                    [
                        "For support, contact: ",
                        html.A(
                            "mike.kipnis@gmail.com",
                            href="mailto:mike.kipnis@gmail.com",
                            style={
                                "textDecoration": "underline",
                                "color": "#AAAAAA",
                            },
                        ),
                    ],
                    style={
                        "fontSize": "12px",
                        "color": "#AAAAAA",
                        "marginTop": "8px",
                        "textAlign": "center",
                        "width": "100%",
                    },
                ),
                # 🔑 MATCH-based prefix store
                dcc.Store(
                    id={"type": "liquibook-prefix", "prefix": self.prefix},
                    data=self.prefix,
                ),
                dbc.Label(
                    id={"type": "liquibook-prefix-out", "prefix": self.prefix}
                )
            ],
            fluid=True,
            className="p-0",
        )

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

# ---------------------------
# Layout & Callback setup
# ---------------------------

# Generate prefix once per app load
prefix = str(uuid.uuid4())[:8]
logger.info(f"Generated prefix for this session: {prefix}")

# Create sandbox with this prefix
sandbox = LiquiBook_Sandbox(prefix)

# Register callbacks once
OrderFormComponent.register_callbacks(app, liquibook_adapter_container)
OrderCancelModifyComponent.register_callbacks(app, liquibook_adapter_container)
TradeOrderHistory.register_callbacks(app)
PriceDepthGrid.register_callbacks(app)

# Set layout once
app.layout = sandbox.layout

# ----------------------------
# Adapter helper
# ----------------------------
def recreate_adapter(prefix: str) -> LiquiBookAdapter:
    # Remove old adapter if exists
    if prefix in liquibook_adapter_container:
        logger.info(f"Recreating LiquibookAdapter for prefix={prefix}")
        del liquibook_adapter_container[prefix]

    # Create new adapter
    adapter = LiquiBookAdapter(prefix, sandbox_instrument)
    liquibook_adapter_container[prefix] = adapter
    return adapter

# =============================
# MATCH Callbacks
# =============================
@app.callback(
    Output(
        {"type": "liquibook-prefix-out", "prefix": MATCH},
        "children",
    ),
    Input(
        {"type": "liquibook-prefix", "prefix": MATCH},
        "data",
    ),
)
def setup_liquibook(prefix):
    adapter = recreate_adapter(prefix)
    adapter.update_order_book_data()
    logger.info(f"Liquibook initialized for prefix={prefix}")
    return prefix

# ----------------------------
# Main
# ----------------------------
if __name__ == "__main__":
    host = os.getenv("DASH_HOST", "127.0.0.1")
    port = int(os.getenv("DASH_PORT", "8050"))
    debug = os.getenv("DASH_DEBUG", "true").lower() == "true"

    app.run(host=host, port=port, debug=debug)
