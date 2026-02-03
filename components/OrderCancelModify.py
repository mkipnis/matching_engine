# Copyright (c) Mike Kipnis - DistributedATS

import dash
from dash import dcc, Output, Input, State, callback_context, html, MATCH
import dash_bootstrap_components as dbc
from liquibook_adapter.LiquiBookAdapter import LiquiBookAdapter


class OrderCancelModifyComponent:

    def __init__(self, prefix: str):
        self.prefix = prefix

    def layout(self):
        return html.Div(
            [
                html.Hr(
                    style={
                        "borderTop": "2px solid #6c757d",
                        "margin": "10px 0 10px"
                    }
                ),
                dbc.Card(
                    dbc.CardBody(
                        dbc.Row(
                            [
                                # Selected order store
                                dcc.Store(
                                    id={
                                        "type": "selected-order",
                                        "prefix": self.prefix,
                                    }
                                ),

                                # Order Id
                                dbc.Col(
                                    dbc.Label("Order Id:", className="text-end w-100"),
                                    width="auto",
                                    className="d-flex align-items-center"
                                ),
                                dbc.Col(
                                    dbc.Label(
                                        id={
                                            "type": "order-id-label",
                                            "prefix": self.prefix,
                                        },
                                        className="text-end w-100"
                                    ),
                                    width="auto",
                                    className="d-flex align-items-center"
                                ),

                                dbc.Col(width=True),  # spacer

                                # Price
                                dbc.Col(
                                    dbc.Label("Price", className="text-end w-100"),
                                    width="auto",
                                    className="d-flex align-items-center"
                                ),
                                dbc.Col(
                                    dbc.Input(
                                        type="number",
                                        id={
                                            "type": "new-price-input",
                                            "prefix": self.prefix,
                                        },
                                        step=100,
                                        placeholder="Enter new price"
                                    ),
                                    width=2
                                ),

                                # Delta Qty
                                dbc.Col(
                                    dbc.Label("Delta Qty", className="text-end w-100"),
                                    width="auto",
                                    className="d-flex align-items-center"
                                ),
                                dbc.Col(
                                    dbc.Input(
                                        type="number",
                                        id={
                                            "type": "delta-quantity-input",
                                            "prefix": self.prefix,
                                        },
                                        step=100,
                                        placeholder="Enter quantity"
                                    ),
                                    width=2
                                ),

                                # Buttons
                                dbc.Col(
                                    [
                                        dbc.Button(
                                            "Modify",
                                            id={
                                                "type": "modify-order-button",
                                                "prefix": self.prefix,
                                            },
                                            color="success",
                                            className="me-2"
                                        ),
                                        dbc.Button(
                                            "Cancel",
                                            id={
                                                "type": "cancel-order-button",
                                                "prefix": self.prefix,
                                            },
                                            color="danger",
                                            className="me-2"
                                        ),
                                    ],
                                    width="auto",
                                    className="d-flex align-items-center"
                                ),
                            ],
                            className="g-2 flex-nowrap"
                        ),
                    ),
                    style={"borderRadius": "10px", "margin": "10px 0"},
                ),
            ],
            id={
                "type": "modify-cancel-panel",
                "prefix": self.prefix,
            },
            style={"display": "none"},
        )

    @staticmethod
    def register_callbacks(app, adapter_container):

        # ----------------------------------
        # Show / hide modify panel
        # ----------------------------------
        @app.callback(
            Output({"type": "order-id-label", "prefix": MATCH}, "children"),
            Output({"type": "new-price-input", "prefix": MATCH}, "value"),
            Output({"type": "delta-quantity-input", "prefix": MATCH}, "value"),
            Output({"type": "modify-cancel-panel", "prefix": MATCH}, "style"),
            Input({"type": "selected-order", "prefix": MATCH}, "data"),
        )
        def handle_selected(selected_order):
            if selected_order and selected_order.get("state_str") == "Accepted":
                return (
                    selected_order["order_id_"],
                    selected_order["price"],
                    0,
                    {"display": "block"},
                )

            return None, None, None, {"display": "none"}

        # ----------------------------------
        # Modify / Cancel order
        # ----------------------------------
        @app.callback(
            Output(
                {"type": "liquibook-order-cancel-modify", "prefix": MATCH},
                "data"
            ),
            Input({"type": "modify-order-button", "prefix": MATCH}, "n_clicks"),
            Input({"type": "cancel-order-button", "prefix": MATCH}, "n_clicks"),
            State({"type": "new-price-input", "prefix": MATCH}, "value"),
            State({"type": "delta-quantity-input", "prefix": MATCH}, "value"),
            State({"type": "selected-order", "prefix": MATCH}, "data"),
            prevent_initial_call=True
        )
        def handle_order(modify_clicks, cancel_clicks, new_price, delta_quantity, selected_order):
            if not selected_order:
                return dash.no_update

            triggered = callback_context.triggered_id
            prefix = triggered["prefix"]
            adapter = adapter_container[prefix]

            if triggered["type"] == "cancel-order-button":
                return adapter.cancel_order(selected_order)

            if triggered["type"] == "modify-order-button":
                return adapter.modify_order(
                    selected_order,
                    delta_quantity,
                    new_price
                )

            return dash.no_update

